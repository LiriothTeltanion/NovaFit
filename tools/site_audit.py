"""Audit the exact static artifact published as the NovaFit Pages showcase."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = ROOT / "site"
DEFAULT_BASE_PATH = "/NovaFit/"
CANONICAL_URL = "https://liriothteltanion.github.io/NovaFit/"
REQUIRED_FILES = ("index.html", "404.html", "manifest.webmanifest", "project.json", "sw.js")
FORBIDDEN_PARTS = {
    ".git",
    ".nova-pack-backup",
    ".venv",
    "__pycache__",
    "backups",
    "data",
}
FORBIDDEN_NAMES = {".env", "config.json", "id_dsa", "id_ed25519", "id_rsa", "novafit.log"}
FORBIDDEN_SUFFIXES = {
    ".db",
    ".exe",
    ".key",
    ".log",
    ".msi",
    ".p12",
    ".pem",
    ".pfx",
    ".sqlite",
    ".sqlite3",
    ".zip",
}
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".svg", ".txt", ".webmanifest", ".xml"}
CSS_URL_PATTERN = re.compile(r"url\(\s*([\"']?)([^\"')]+)\1\s*\)", re.IGNORECASE)
CORE_SHELL_PATTERN = re.compile(r"\bconst\s+CORE_SHELL\s*=\s*\[(.*?)\]\s*;", re.DOTALL)
JS_STRING_PATTERN = re.compile(r"[\"']([^\"']+)[\"']")
PRIVATE_PATH_PATTERN = re.compile(
    r"(?i)(?:[a-z]:[\\/](?:users|documents and settings)[\\/]|/users/[^/]+/|/home/[^/]+/|onedrive[\\/])"
)
SECRET_PATTERN = re.compile(
    r"(?i)(?:github_pat_[a-z0-9_]{20,}|ghp_[a-z0-9]{20,}|-----BEGIN (?:RSA |EC )?PRIVATE KEY-----)"
)


@dataclass(frozen=True, slots=True)
class Finding:
    """One site audit result."""

    level: str
    message: str


@dataclass(slots=True)
class SiteReport:
    """Collect deterministic site validation results."""

    findings: list[Finding] = field(default_factory=list)
    files: int = 0
    total_bytes: int = 0

    def add(self, level: str, message: str) -> None:
        self.findings.append(Finding(level.upper(), message))

    @property
    def errors(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.level == "ERROR"]

    @property
    def warnings(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.level == "WARNING"]


class SiteHTMLParser(HTMLParser):
    """Collect local-link candidates and required metadata from HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.canonical: str | None = None
        self.description: str | None = None
        self.has_viewport = False
        self.has_manifest = False
        self.html_language: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): value or "" for name, value in attrs}
        if tag.lower() == "html":
            self.html_language = values.get("lang")
        if tag.lower() == "meta":
            name = values.get("name", "").lower()
            if name == "description":
                self.description = values.get("content", "").strip()
            elif name == "viewport":
                self.has_viewport = bool(values.get("content", "").strip())
        if tag.lower() == "link":
            relationships = set(values.get("rel", "").lower().split())
            if "canonical" in relationships:
                self.canonical = values.get("href", "").strip()
            if "manifest" in relationships:
                self.has_manifest = True
        for attribute in ("href", "src", "poster", "action"):
            if values.get(attribute):
                self.links.append(values[attribute])
        if values.get("srcset"):
            self.links.extend(part.strip().split()[0] for part in values["srcset"].split(",") if part.strip())
        if values.get("style"):
            self.links.extend(match[1] for match in CSS_URL_PATTERN.findall(values["style"]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="site_audit",
        description="Validate the exact static NovaFit Pages artifact without network access.",
    )
    parser.add_argument("--site-root", type=Path, default=DEFAULT_SITE, help="Static site or staged artifact.")
    parser.add_argument(
        "--asset-root",
        type=Path,
        default=None,
        help="Optional external assets directory when auditing source site/ before staging.",
    )
    parser.add_argument("--base-path", default=DEFAULT_BASE_PATH, help="GitHub Pages project base path.")
    parser.add_argument("--quiet", action="store_true", help="Print only errors and the summary.")
    return parser


def normalize_base_path(value: str) -> str:
    """Return a slash-delimited GitHub Pages project path."""
    base = "/" + value.strip("/") + "/"
    if base == "//":
        return "/"
    return base


def iter_files(root: Path) -> list[Path]:
    """Return stable artifact files without following symbolic links."""
    return sorted(
        (path for path in root.rglob("*") if path.is_file() or path.is_symlink()),
        key=lambda path: path.relative_to(root).as_posix().casefold(),
    )


def _is_forbidden_file(relative: Path) -> bool:
    lowered_parts = {part.lower() for part in relative.parts}
    name = relative.name.lower()
    if lowered_parts & FORBIDDEN_PARTS:
        return True
    if name in FORBIDDEN_NAMES or relative.suffix.lower() in FORBIDDEN_SUFFIXES:
        return True
    return name.endswith((".db-shm", ".db-wal", ".sqlite-shm", ".sqlite-wal"))


def audit_files(root: Path, report: SiteReport) -> list[Path]:
    """Reject unsafe artifact entries and private local path leakage."""
    files = iter_files(root)
    report.files = len(files)
    for path in files:
        relative = path.relative_to(root)
        display = relative.as_posix()
        if path.is_symlink():
            report.add("ERROR", f"Pages artifacts cannot contain symbolic links: {display}")
            continue
        report.total_bytes += path.stat().st_size
        if _is_forbidden_file(relative):
            report.add("ERROR", f"Private/runtime or binary release file is forbidden in Pages: {display}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            report.add("ERROR", f"Public text asset is not UTF-8: {display}")
            continue
        if PRIVATE_PATH_PATTERN.search(source):
            report.add("ERROR", f"Private absolute computer path leaked into Pages: {display}")
        if SECRET_PATTERN.search(source):
            report.add("ERROR", f"Credential-like value leaked into Pages: {display}")
    return files


def _candidate_for_target(
    target: str,
    *,
    document: Path,
    root: Path,
    asset_root: Path | None,
    base_path: str,
) -> tuple[Path | None, str | None]:
    """Resolve one local site target and return an error when it is unsafe."""
    cleaned = target.strip()
    if not cleaned or cleaned.startswith("#"):
        return None, None
    parsed = urlsplit(cleaned)
    scheme = parsed.scheme.lower()
    if scheme in {"mailto", "tel", "data", "blob"}:
        return None, None
    if scheme == "javascript":
        return None, "javascript: links are forbidden; bind behavior from a local script instead"
    if scheme in {"http", "https"}:
        if parsed.netloc.lower() != "liriothteltanion.github.io":
            return None, None
        path_value = parsed.path
    elif scheme or parsed.netloc:
        return None, f"unsupported link scheme: {cleaned}"
    else:
        path_value = parsed.path
    if not path_value:
        return None, None

    if path_value.startswith("/"):
        if base_path != "/" and not path_value.startswith(base_path):
            return None, f"root-relative link escapes the Pages base {base_path}: {cleaned}"
        relative_text = path_value[len(base_path) :] if base_path != "/" else path_value.lstrip("/")
        candidate = (root / unquote(relative_text)).resolve()
    else:
        candidate = (document.parent / unquote(path_value)).resolve()

    try:
        relative = candidate.relative_to(root)
    except ValueError:
        return None, f"local link escapes the staged site: {cleaned}"

    if candidate.is_dir():
        candidate = candidate / "index.html"
    if candidate.exists():
        return candidate, None
    if asset_root is not None and relative.parts and relative.parts[0].lower() == "assets":
        external = (asset_root / Path(*relative.parts[1:])).resolve()
        try:
            external.relative_to(asset_root.resolve())
        except ValueError:
            return None, f"asset link escapes the public asset root: {cleaned}"
        if external.exists() and external.is_file():
            return external, None
    return None, f"broken local site link: {cleaned}"


def audit_html_links(
    root: Path,
    files: list[Path],
    report: SiteReport,
    *,
    asset_root: Path | None,
    base_path: str,
) -> None:
    """Validate HTML/CSS links and index metadata without fetching the web."""
    for path in (item for item in files if item.suffix.lower() == ".html"):
        relative = path.relative_to(root).as_posix()
        parser = SiteHTMLParser()
        try:
            parser.feed(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            report.add("ERROR", f"Unable to parse HTML {relative}: {exc}")
            continue
        for target in parser.links:
            _, error = _candidate_for_target(
                target,
                document=path,
                root=root,
                asset_root=asset_root,
                base_path=base_path,
            )
            if error:
                report.add("ERROR", f"{relative}: {error}")
        if path.name.lower() == "index.html" and path.parent == root:
            if not parser.html_language:
                report.add("ERROR", "index.html must declare an HTML language.")
            if not parser.description:
                report.add("ERROR", "index.html must include a non-empty meta description.")
            if not parser.has_viewport:
                report.add("ERROR", "index.html must include responsive viewport metadata.")
            if not parser.has_manifest:
                report.add("ERROR", "index.html must link manifest.webmanifest.")
            if parser.canonical != CANONICAL_URL:
                report.add("ERROR", f"index.html canonical URL must be {CANONICAL_URL}")

    for path in (item for item in files if item.suffix.lower() == ".css"):
        source = path.read_text(encoding="utf-8")
        for _, target in CSS_URL_PATTERN.findall(source):
            _, error = _candidate_for_target(
                target,
                document=path,
                root=root,
                asset_root=asset_root,
                base_path=base_path,
            )
            if error:
                report.add("ERROR", f"{path.relative_to(root).as_posix()}: {error}")


def audit_manifest(root: Path, report: SiteReport, *, asset_root: Path | None, base_path: str) -> None:
    """Validate the installable showcase manifest and its local icons."""
    path = root / "manifest.webmanifest"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        report.add("ERROR", f"manifest.webmanifest is invalid: {exc}")
        return
    for key in ("name", "short_name", "start_url", "scope", "display", "icons"):
        if not manifest.get(key):
            report.add("ERROR", f"manifest.webmanifest is missing {key!r}.")

    def audit_manifest_resources(resources: object, *, label: str) -> None:
        if resources is None:
            return
        if not isinstance(resources, list):
            report.add("ERROR", f"manifest {label} must be a list.")
            return
        for index, resource in enumerate(resources):
            if not isinstance(resource, dict) or not resource.get("src"):
                report.add("ERROR", f"manifest {label} {index} is missing src.")
                continue
            candidate, error = _candidate_for_target(
                str(resource["src"]),
                document=path,
                root=root,
                asset_root=asset_root,
                base_path=base_path,
            )
            if error:
                report.add("ERROR", f"manifest {label} {index}: {error}")
            elif candidate is None:
                report.add("ERROR", f"manifest {label} {index} must use a local public resource.")

    audit_manifest_resources(manifest.get("icons"), label="icon")
    audit_manifest_resources(manifest.get("screenshots"), label="screenshot")

    shortcuts = manifest.get("shortcuts")
    if shortcuts is not None and not isinstance(shortcuts, list):
        report.add("ERROR", "manifest shortcuts must be a list.")
    elif isinstance(shortcuts, list):
        for index, shortcut in enumerate(shortcuts):
            if not isinstance(shortcut, dict) or not shortcut.get("url"):
                report.add("ERROR", f"manifest shortcut {index} is missing url.")
                continue
            _, error = _candidate_for_target(
                str(shortcut["url"]),
                document=path,
                root=root,
                asset_root=asset_root,
                base_path=base_path,
            )
            if error:
                report.add("ERROR", f"manifest shortcut {index}: {error}")
            audit_manifest_resources(shortcut.get("icons"), label=f"shortcut {index} icon")

    for key in ("start_url", "scope"):
        value = str(manifest.get(key, ""))
        candidate, error = _candidate_for_target(
            value,
            document=path,
            root=root,
            asset_root=asset_root,
            base_path=base_path,
        )
        if error:
            report.add("ERROR", f"manifest {key}: {error}")
        elif candidate is None:
            report.add("ERROR", f"manifest {key} must stay inside the local Pages scope.")


def audit_project_manifest(root: Path, report: SiteReport) -> None:
    """Validate the generated public facts consumed by the showcase."""
    path = root / "project.json"
    try:
        project = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        report.add("ERROR", f"project.json is invalid: {exc}")
        return
    if project.get("schema") != "nova-portfolio-project-v1":
        report.add("ERROR", "project.json has an unsupported schema.")
    for key in ("slug", "name", "version", "status", "repository"):
        if not project.get(key):
            report.add("ERROR", f"project.json is missing {key!r}.")
    privacy = project.get("privacy")
    if not isinstance(privacy, dict):
        report.add("ERROR", "project.json is missing its privacy contract.")
    else:
        if privacy.get("local_first") is not True:
            report.add("ERROR", "project.json must preserve NovaFit's local-first boundary.")
        if privacy.get("tracked_runtime_data") is not False:
            report.add("ERROR", "project.json must state that runtime data is not tracked.")
    website = project.get("website")
    if not isinstance(website, dict) or website.get("live") != CANONICAL_URL:
        report.add("ERROR", f"project.json website.live must be {CANONICAL_URL}")


def audit_service_worker(root: Path, report: SiteReport, *, base_path: str) -> None:
    """Ensure the offline shell cannot fail because a precached local file is missing."""
    path = root / "sw.js"
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report.add("ERROR", f"sw.js is invalid: {exc}")
        return
    if len(source.encode("utf-8")) < 200:
        report.add("ERROR", "sw.js is too small to provide a meaningful offline showcase shell.")
    match = CORE_SHELL_PATTERN.search(source)
    if match is None:
        report.add("ERROR", "sw.js must declare a static CORE_SHELL precache list.")
        return
    shell_targets = JS_STRING_PATTERN.findall(match.group(1))
    if not shell_targets:
        report.add("ERROR", "sw.js CORE_SHELL precache list cannot be empty.")
        return
    for target in shell_targets:
        candidate, error = _candidate_for_target(
            target,
            document=path,
            root=root,
            asset_root=None,
            base_path=base_path,
        )
        if error:
            report.add("ERROR", f"sw.js CORE_SHELL: {error}")
        elif candidate is None:
            report.add("ERROR", f"sw.js CORE_SHELL must use a local public resource: {target}")


def audit_site(
    site_root: Path,
    *,
    asset_root: Path | None = None,
    base_path: str = DEFAULT_BASE_PATH,
) -> SiteReport:
    """Run the complete static Pages privacy, metadata and link audit."""
    root = site_root.expanduser().resolve()
    external_assets = asset_root.expanduser().resolve() if asset_root else None
    report = SiteReport()
    if not root.is_dir():
        report.add("ERROR", f"Site root does not exist: {root}")
        return report
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            report.add("ERROR", f"Required Pages file is missing: {relative}")
    files = audit_files(root, report)
    audit_html_links(root, files, report, asset_root=external_assets, base_path=normalize_base_path(base_path))
    if (root / "manifest.webmanifest").is_file():
        audit_manifest(
            root,
            report,
            asset_root=external_assets,
            base_path=normalize_base_path(base_path),
        )
    if (root / "project.json").is_file():
        audit_project_manifest(root, report)
    if (root / "sw.js").is_file():
        audit_service_worker(root, report, base_path=normalize_base_path(base_path))
    return report


def print_report(report: SiteReport, *, quiet: bool) -> None:
    print("NovaFit Pages artifact audit")
    print("=" * 60)
    for finding in report.findings:
        if quiet and finding.level != "ERROR":
            continue
        print(f"[{finding.level}] {finding.message}")
    print(
        f"Checked {report.files} files · {report.total_bytes / (1024 * 1024):.2f} MiB · "
        f"{len(report.errors)} errors · {len(report.warnings)} warnings"
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = audit_site(args.site_root, asset_root=args.asset_root, base_path=args.base_path)
    print_report(report, quiet=args.quiet)
    if report.errors:
        print("Pages artifact audit failed. [ERROR]")
        return 1
    print("Pages artifact is public-only, internally linked and ready to deploy. [OK]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
