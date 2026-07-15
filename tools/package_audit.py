"""Audit NovaFit workspaces and clean release-staging directories.

The default mode is deliberately non-destructive: local databases and exports
inside ``data`` are reported but preserved. ``--strict-distribution`` is for a
copied staging directory and rejects anything that should not ship publicly.
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlsplit

NOVAFIT = Path(__file__).resolve().parents[1]

SKIP_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".nova-pack-backup",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "venv",
}
REQUIRED_PATHS = (
    ".github/workflows/quality.yml",
    ".github/workflows/release.yml",
    ".gitattributes",
    ".gitignore",
    "README.md",
    "VERIFY_ALL.bat",
    "export_backup.bat",
    "pyproject.toml",
    "requirements.txt",
    "run_novafit.bat",
    "novafit/__init__.py",
    "novafit/backup.py",
    "novafit/cli.py",
    "novafit/gui.py",
    "scripts/verify.py",
    "scripts/sync_docs.py",
    "docs/PROJECT_FACTS.md",
    "portfolio/project.json",
    "assets/manifest.json",
    "tests",
)
PRIVATE_NAMES = {
    "id_dsa",
    "id_ed25519",
    "id_rsa",
}
PRIVATE_SUFFIXES = {".db", ".key", ".log", ".p12", ".pem", ".pfx", ".sqlite", ".sqlite3"}
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_LINK_PATTERN = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class Finding:
    """One actionable repository audit result."""

    level: str
    message: str


@dataclass(slots=True)
class AuditReport:
    """Collect errors, warnings and informational audit results."""

    findings: list[Finding] = field(default_factory=list)
    checked_files: int = 0

    def add(self, level: str, message: str) -> None:
        """Append one normalized finding."""
        self.findings.append(Finding(level.upper(), message))

    @property
    def errors(self) -> list[Finding]:
        """Return findings that make the audit fail."""
        return [finding for finding in self.findings if finding.level == "ERROR"]

    @property
    def warnings(self) -> list[Finding]:
        """Return non-blocking findings."""
        return [finding for finding in self.findings if finding.level == "WARNING"]


def build_parser() -> argparse.ArgumentParser:
    """Create the audit command-line parser."""
    parser = argparse.ArgumentParser(
        prog="package_audit",
        description="Audit a NovaFit workspace or clean release-staging tree.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=NOVAFIT,
        help="Repository or staging directory to audit (defaults to this checkout).",
    )
    parser.add_argument(
        "--strict-distribution",
        action="store_true",
        help="Reject runtime/private files; use only on a copied release-staging tree.",
    )
    parser.add_argument("--quiet", action="store_true", help="Print only the final summary and errors.")
    return parser


def iter_repository_files(root: Path) -> list[Path]:
    """Return stable, relevant file paths without generated dependency trees."""
    files: list[Path] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRECTORIES for part in relative.parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix().casefold())


def is_runtime_file(path: Path, root: Path) -> bool:
    """Return whether a file is mutable local state that must not ship."""
    relative = path.relative_to(root)
    name = path.name.lower()
    if relative.parts and relative.parts[0].lower() == "data" and name != ".gitkeep":
        return True
    if path.suffix.lower() in PRIVATE_SUFFIXES:
        return True
    return name.endswith((".db-shm", ".db-wal", ".sqlite-shm", ".sqlite-wal"))


def is_private_file(path: Path) -> bool:
    """Return whether a filename strongly indicates a credential or secret."""
    name = path.name.lower()
    if name == ".env.example":
        return False
    if name == ".env" or name.startswith(".env."):
        return True
    return name in PRIVATE_NAMES or path.suffix.lower() in {".key", ".p12", ".pem", ".pfx"}


def audit_distribution_files(root: Path, *, strict_distribution: bool) -> AuditReport:
    """Check runtime, credential and backup files for the selected audit mode."""
    root = root.resolve()
    report = AuditReport()
    for path in iter_repository_files(root):
        report.checked_files += 1
        relative = path.relative_to(root).as_posix()
        if is_private_file(path):
            report.add("ERROR", f"Credential/private file must be removed: {relative}")
            continue
        is_runtime = is_runtime_file(path, root)
        if is_runtime and not strict_distribution:
            report.add("INFO", f"Workspace runtime file preserved (not distributable): {relative}")
        elif is_runtime:
            report.add("ERROR", f"Release packaging excludes NovaFit/data runtime files: {relative}")

    backup_root = root / ".nova-pack-backup"
    if backup_root.exists():
        level = "ERROR" if strict_distribution else "WARNING"
        report.add(level, "Legacy .nova-pack-backup exists; exclude it from every release archive.")
    return report


def audit_required_paths(root: Path, report: AuditReport) -> None:
    """Require the application, launch and verification entry points."""
    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            report.add("ERROR", f"Required project path is missing: {relative}")


def _local_link_target(raw_target: str) -> str | None:
    """Normalize a Markdown/HTML target, ignoring URLs and page anchors."""
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    elif " " in target:
        target = target.split(maxsplit=1)[0]
    if not target or target.startswith("#"):
        return None
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith("//"):
        return None
    return unquote(parsed.path)


def audit_markdown_links(root: Path, files: list[Path], report: AuditReport) -> None:
    """Reject broken local links in tracked-style Markdown documents."""
    for document in (path for path in files if path.suffix.lower() == ".md"):
        try:
            source = document.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            report.add("ERROR", f"Markdown is not UTF-8: {document.relative_to(root).as_posix()} ({exc})")
            continue
        targets = MARKDOWN_LINK_PATTERN.findall(source) + HTML_LINK_PATTERN.findall(source)
        for raw_target in targets:
            local_target = _local_link_target(raw_target)
            if not local_target:
                continue
            candidate = (document.parent / local_target).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                report.add(
                    "ERROR",
                    f"Local link escapes repository: {document.relative_to(root).as_posix()} -> {raw_target}",
                )
                continue
            if not candidate.exists():
                report.add(
                    "ERROR",
                    f"Broken local link: {document.relative_to(root).as_posix()} -> {raw_target}",
                )


def audit_svg_files(root: Path, files: list[Path], report: AuditReport) -> None:
    """Parse every SVG so malformed documentation artwork cannot be published."""
    for path in (item for item in files if item.suffix.lower() == ".svg"):
        try:
            ET.parse(path)
        except (ET.ParseError, OSError) as exc:
            report.add("ERROR", f"Invalid SVG {path.relative_to(root).as_posix()}: {exc}")


def audit_windows_launchers(root: Path, files: list[Path], report: AuditReport) -> None:
    """Check BAT encoding and CRLF portability declared by ``.gitattributes``."""
    for path in (item for item in files if item.suffix.lower() == ".bat"):
        content = path.read_bytes()
        relative = path.relative_to(root).as_posix()
        if b"\x00" in content:
            report.add("ERROR", f"Windows launcher contains NUL bytes: {relative}")
        bare_line_feeds = content.count(b"\n") - content.count(b"\r\n")
        if bare_line_feeds:
            report.add("ERROR", f"Windows launcher must use CRLF line endings: {relative}")


def audit_repository(root: Path, *, strict_distribution: bool) -> AuditReport:
    """Run all deterministic, standard-library package checks."""
    root = root.expanduser().resolve()
    report = audit_distribution_files(root, strict_distribution=strict_distribution)
    files = iter_repository_files(root)
    report.checked_files = len(files)
    audit_required_paths(root, report)
    audit_markdown_links(root, files, report)
    audit_svg_files(root, files, report)
    audit_windows_launchers(root, files, report)
    return report


def print_report(report: AuditReport, *, strict_distribution: bool, quiet: bool) -> None:
    """Print a compact, actionable audit report."""
    mode = "strict distribution" if strict_distribution else "workspace-safe"
    print(f"NovaFit package audit ({mode})")
    print("=" * 60)
    for finding in report.findings:
        if quiet and finding.level not in {"ERROR"}:
            continue
        marker = {"ERROR": "[ERROR]", "WARNING": "[WARNING]", "INFO": "[INFO]"}.get(
            finding.level,
            "[NOTE]",
        )
        print(f"{marker} {finding.message}")
    print(
        f"Checked {report.checked_files} files · "
        f"{len(report.errors)} errors · {len(report.warnings)} warnings"
    )


def main(argv: list[str] | None = None) -> int:
    """Run the requested audit and return a shell-friendly status."""
    args = build_parser().parse_args(argv)
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"Audit root does not exist or is not a directory: {root}", file=sys.stderr)
        return 2
    report = audit_repository(root, strict_distribution=args.strict_distribution)
    print_report(report, strict_distribution=args.strict_distribution, quiet=args.quiet)
    if report.errors:
        print("Package audit failed. Review the errors above. [ERROR]")
        return 1
    print("Package audit passed. User data was not modified. [OK]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
