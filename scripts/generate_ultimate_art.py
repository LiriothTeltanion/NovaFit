"""
Module: ultimate art generator
Purpose: Generate repository-hosted animated SVG artwork and an icon-system
    preview for NovaFit Ultimate without external design services.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Pillow is used only for the PNG contact sheet; SVG motion has a reduced-motion fallback.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from novafit import __version__  # noqa: E402

DEFAULT_OUTPUT = ROOT / "assets"
DISPLAY_VERSION = ".".join(__version__.split(".")[:2])

SVG_STYLE = """
<style>
  .bg{fill:url(#bg)} .grid{stroke:#1f5261;stroke-width:1;opacity:.45}
  .title{font:700 45px 'Segoe UI',Arial;fill:#f2fbff;letter-spacing:1px}
  .subtitle{font:500 18px 'Segoe UI',Arial;fill:#9cc6d2}
  .label{font:700 16px 'Segoe UI',Arial;fill:#e8fbff}
  .small{font:500 13px 'Segoe UI',Arial;fill:#8db6c2}
  .card{fill:#0a2830;stroke:#2dd4bf;stroke-width:2}
  .card2{fill:#101d42;stroke:#60a5fa;stroke-width:2}
  .line{fill:none;stroke:#2dd4bf;stroke-width:3;stroke-linecap:round}
  .line2{fill:none;stroke:#c084fc;stroke-width:3;stroke-linecap:round}
  .pulse{animation:pulse 2.7s ease-in-out infinite;transform-origin:center}
  .float{animation:float 4.8s ease-in-out infinite;transform-origin:center}
  .spin{animation:spin 13s linear infinite;transform-origin:center}
  .dash{stroke-dasharray:12 14;animation:dash 5s linear infinite}
  .glow{filter:url(#glow)}
  .delay1{animation-delay:-.7s}.delay2{animation-delay:-1.4s}.delay3{animation-delay:-2.1s}
  @keyframes pulse{0%,100%{opacity:.58;transform:scale(.96)}50%{opacity:1;transform:scale(1.04)}}
  @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
  @keyframes spin{to{transform:rotate(360deg)}}
  @keyframes dash{to{stroke-dashoffset:-104}}
  @media (prefers-reduced-motion:reduce){.pulse,.float,.spin,.dash{animation:none!important}}
</style>
"""

DEFS = """
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#04171c"/><stop offset=".52" stop-color="#071f2d"/><stop offset="1" stop-color="#15133b"/></linearGradient>
  <linearGradient id="aurora" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#2dd4bf"/><stop offset=".5" stop-color="#60a5fa"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
"""


def parser() -> argparse.ArgumentParser:
    """Create the artwork-generator parser.

    Returns:
        Configured parser.

    Example:
        >>> parser().prog
        'generate_ultimate_art'
    """
    result = argparse.ArgumentParser(prog="generate_ultimate_art")
    result.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return result


def svg_document(width: int, height: int, body: str) -> str:
    """Wrap SVG content with shared definitions and animation styles.

    Args:
        width: ViewBox width.
        height: ViewBox height.
        body: SVG body markup.

    Returns:
        Complete UTF-8 SVG document.

    Example:
        >>> svg_document(10, 10, '<rect width="10" height="10"/>').startswith('<svg')
        True
    """
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">{DEFS}{SVG_STYLE}{body}</svg>\n'


def grid(width: int, height: int, step: int = 64) -> str:
    """Return a lightweight SVG grid.

    Args:
        width: Grid width.
        height: Grid height.
        step: Grid-cell size.

    Returns:
        SVG path markup.

    Example:
        >>> '<path' in grid(100, 100, 20)
        True
    """
    commands: list[str] = []
    for x in range(0, width + 1, step):
        commands.append(f"M{x} 0V{height}")
    for y in range(0, height + 1, step):
        commands.append(f"M0 {y}H{width}")
    return f'<path d="{" ".join(commands)}" class="grid"/>'


def write_svg(path: Path, body: str, width: int, height: int) -> Path:
    """Write one generated SVG asset.

    Args:
        path: Destination.
        body: SVG body markup.
        width: ViewBox width.
        height: ViewBox height.

    Returns:
        Written path.

    Example:
        >>> write_svg(Path('x.svg'), '<rect/>', 10, 10)  # doctest: +SKIP
        PosixPath('x.svg')
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg_document(width, height, body), encoding="utf-8", newline="\n")
    return path


def build_banner(output: Path) -> Path:
    """Generate the primary version-aware Ultimate hero artwork."""
    cards = [
        (90, 355, "COMPLETE EN · ES · HE", "Full panels + true Hebrew RTL", "card"),
        (435, 355, "PURPOSEFUL MOTION", "Pausable · reduced-motion aware", "card2"),
        (780, 355, "VERIFIED BACKUPS", "All profiles · SQLite · SHA-256", "card"),
        (1125, 355, "LIVING DOCUMENTATION", "Facts + assets + profile sync", "card2"),
    ]
    card_markup = "".join(
        f'<g class="float delay{i % 4}"><rect x="{x}" y="{y}" width="300" height="105" rx="22" class="{kind}"/>'
        f'<text x="{x + 24}" y="{y + 42}" class="label">{title}</text><text x="{x + 24}" y="{y + 72}" class="small">{subtitle}</text></g>'
        for i, (x, y, title, subtitle, kind) in enumerate(cards)
    )
    body = f"""<rect width="1600" height="520" class="bg"/>{grid(1600, 520, 64)}
    <circle cx="1370" cy="145" r="94" fill="#2dd4bf" opacity=".08" class="pulse"/>
    <circle cx="1370" cy="145" r="68" fill="none" stroke="#60a5fa" stroke-width="3" class="spin dash"/>
    <circle cx="1370" cy="145" r="44" fill="#c084fc" opacity=".28" class="pulse delay1"/>
    <path d="M55 285 C250 210 370 350 560 270 S850 205 1030 285 S1280 355 1545 248" class="line glow"/>
    <path d="M55 309 C255 248 390 370 590 300 S890 252 1080 318 S1320 382 1545 285" class="line2" opacity=".7"/>
    <text x="76" y="92" class="small" fill="#2dd4bf">NOVA HEALTH INTELLIGENCE / LOCAL-FIRST</text>
    <text x="76" y="160" class="title">NovaFit Ultimate {DISPLAY_VERSION}</text>
    <text x="76" y="198" class="subtitle">Wellness Intelligence Studio · Python · Tkinter · SQLite · Matplotlib · Pillow</text>
    <text x="76" y="238" class="subtitle">Private profiles · honest recency · responsive charts · verified backups · one-click Windows delivery</text>
    {card_markup}"""
    return write_svg(output / "novafit-ultimate-banner-animated.svg", body, 1600, 520)


def build_profiles(output: Path) -> Path:
    """Generate multi-user and language-direction artwork."""
    body = f"""<rect width="1400" height="500" class="bg"/>{grid(1400, 500, 70)}
    <text x="55" y="65" class="title">Profiles, languages and private data boundaries</text>
    <text x="55" y="99" class="subtitle">Each profile owns its records, goals, theme, activity focus and interface language.</text>
    <g class="float"><rect x="70" y="155" width="280" height="230" rx="28" class="card"/><circle cx="140" cy="225" r="38" fill="#2dd4bf"/><text x="200" y="216" class="label">Kevin / Lirioth</text><text x="200" y="246" class="small">English · Aurora · Mixed</text><text x="105" y="315" class="subtitle">Private records stay local</text></g>
    <g class="float delay1"><rect x="405" y="155" width="280" height="230" rx="28" class="card2"/><circle cx="475" cy="225" r="38" fill="#fb7185"/><text x="535" y="216" class="label">Lucía Demo</text><text x="535" y="246" class="small">Español · Arcade · Walking</text><text x="440" y="315" class="subtitle">Demo records isolated</text></g>
    <g class="float delay2"><rect x="740" y="155" width="280" height="230" rx="28" class="card"/><circle cx="810" cy="225" r="38" fill="#60a5fa"/><text x="970" y="216" class="label" text-anchor="end">נועה Demo</text><text x="970" y="246" class="small" text-anchor="end">עברית · Sapphire · Mobility</text><text x="970" y="315" class="subtitle" text-anchor="end">רשומות הדגמה מבודדות</text></g>
    <path d="M1040 240H1260" class="line dash"/><path d="M1245 226l25 14-25 14" fill="#2dd4bf"/><rect x="1080" y="300" width="260" height="95" rx="24" class="card2"/><text x="1210" y="339" class="label" text-anchor="middle">SQLite profile vault</text><text x="1210" y="368" class="small" text-anchor="middle">UNIQUE(user_id, date)</text>
    <text x="1120" y="175" class="label">LTR →</text><text x="1285" y="175" class="label" text-anchor="end">← RTL</text>"""
    return write_svg(output / "multi-profile-i18n-animated.svg", body, 1400, 500)


def build_recommendations(output: Path) -> Path:
    """Generate explainable recommendation-pipeline artwork."""
    nodes = [
        (80, "LOCAL RECORDS", "steps · water · mood"),
        (385, "DATA QUALITY", "coverage · gaps · recency"),
        (690, "CONSERVATIVE PLAN", "movement · hydration · recovery"),
        (995, "WEEKLY RHYTHM", "small actions · explicit reasons"),
    ]
    node_markup = "".join(
        f'<g class="float delay{i % 4}"><rect x="{x}" y="180" width="250" height="150" rx="25" class="{"card" if i % 2 == 0 else "card2"}"/><text x="{x + 125}" y="235" class="label" text-anchor="middle">{title}</text><text x="{x + 125}" y="270" class="small" text-anchor="middle">{subtitle}</text><circle cx="{x + 125}" cy="305" r="10" fill="{"#2dd4bf" if i % 2 == 0 else "#c084fc"}" class="pulse"/></g>'
        for i, (x, title, subtitle) in enumerate(nodes)
    )
    arrows = "".join(
        f'<path d="M{x} 255H{x + 55}" class="line dash"/><path d="M{x + 45} 243l20 12-20 12" fill="#2dd4bf"/>'
        for x in (330, 635, 940)
    )
    body = f"""<rect width="1400" height="500" class="bg"/>{grid(1400, 500, 70)}<text x="55" y="68" class="title">Sport &amp; Data Coach</text><text x="55" y="102" class="subtitle">Explainable general wellness guidance — never diagnosis, treatment or pressure.</text>{node_markup}{arrows}<rect x="120" y="385" width="1160" height="64" rx="22" fill="#081f2b" stroke="#fbbf24"/><text x="700" y="424" class="label" text-anchor="middle">Confidence changes with your real tracking coverage · every suggestion includes “why this” and a safety boundary</text>"""
    return write_svg(output / "sport-data-engine-animated.svg", body, 1400, 500)


def build_atlas(output: Path) -> Path:
    """Generate Training Atlas analytical artwork."""
    body = f"""<rect width="1400" height="500" class="bg"/>{grid(1400, 500, 70)}<text x="55" y="67" class="title">Training Atlas · fourth analytics workspace</text><text x="55" y="102" class="subtitle">Capability radar, movement trajectory, hydration signal, weekday rhythm and a conservative coach lens.</text>
    <g transform="translate(205 290)" class="spin"><polygon points="0,-105 100,-32 62,85 -62,85 -100,-32" fill="#2dd4bf" opacity=".12" stroke="#2dd4bf" stroke-width="2"/><polygon points="0,-78 75,-24 46,63 -46,63 -75,-24" fill="#c084fc" opacity=".24" stroke="#c084fc" stroke-width="3"/><circle r="8" fill="#f2fbff"/></g>
    <g transform="translate(390 175)"><rect width="460" height="235" rx="25" class="card"/><path d="M28 180L85 154L142 172L199 105L256 128L313 70L370 90L430 42" class="line glow"/><path d="M28 198L85 184L142 191L199 166L256 176L313 138L370 149L430 118" class="line2"/><text x="28" y="35" class="label">Movement trajectory + rolling average</text></g>
    <g transform="translate(890 175)"><rect width="440" height="235" rx="25" class="card2"/><g fill="#60a5fa">{"".join(f'<rect x="{30 + i * 48}" y="{190 - (i % 5) * 24}" width="26" height="{35 + (i % 5) * 24}" rx="7" opacity="{0.55 + i * 0.04}"/>' for i in range(8))}</g><path d="M28 140C100 95 165 160 230 105S355 60 410 92" class="line2"/><text x="28" y="35" class="label">Hydration + weekday rhythm</text><text x="28" y="218" class="small">Coach lens: progress gradually · protect recovery · improve data consistency</text></g>"""
    return write_svg(output / "training-atlas-animated.svg", body, 1400, 500)


def build_technology(output: Path) -> Path:
    """Generate the project technology constellation."""
    labels = [
        "Python 3.10+",
        "Tkinter / ttk",
        "SQLite v4",
        "Matplotlib",
        "Pillow icons",
        "SHA-256 ZIP",
        "JSON / CSV",
        "Docs manifest",
        "GitHub Actions",
    ]
    nodes = []
    import math

    for i, label in enumerate(labels):
        angle = math.radians(i * 360 / len(labels) - 90)
        x = 700 + math.cos(angle) * 455
        y = 270 + math.sin(angle) * 165
        nodes.append(
            f'<g class="float delay{i % 4}"><circle cx="{x:.0f}" cy="{y:.0f}" r="57" fill="#0b2834" stroke="{"#2dd4bf" if i % 2 == 0 else "#60a5fa"}" stroke-width="2"/><text x="{x:.0f}" y="{y + 5:.0f}" class="small" text-anchor="middle">{label}</text></g><path d="M700 270L{x:.0f} {y:.0f}" class="line" opacity=".28"/>'
        )
    body = f"""<rect width="1400" height="520" class="bg"/>{grid(1400, 520, 70)}<text x="55" y="62" class="title">Technology constellation</text><text x="55" y="96" class="subtitle">Purposeful dependencies around one local-first Python core.</text>{"".join(nodes)}<circle cx="700" cy="270" r="96" fill="url(#aurora)" opacity=".19" class="pulse"/><circle cx="700" cy="270" r="68" fill="#071f2d" stroke="#c084fc" stroke-width="3"/><text x="700" y="263" class="label" text-anchor="middle">NOVAFIT</text><text x="700" y="292" class="small" text-anchor="middle">ULTIMATE {DISPLAY_VERSION}</text>"""
    return write_svg(output / "technology-constellation-animated.svg", body, 1400, 520)


def build_distribution(output: Path) -> Path:
    """Generate the repaired verification and release-safety diagram."""
    body = f"""<rect width="1400" height="430" class="bg"/>{grid(1400, 430, 70)}<text x="55" y="64" class="title">Verification that respects your data</text><text x="55" y="98" class="subtitle">The checker audits code in place, while the release builder stages a clean copy without runtime databases.</text>
    <g class="float"><rect x="70" y="155" width="410" height="190" rx="28" class="card"/><text x="105" y="205" class="label">WORKSPACE MODE</text><text x="105" y="245" class="subtitle">data/novafit.db may exist</text><text x="105" y="278" class="small">✓ verify code and tests</text><text x="105" y="306" class="small">✓ preserve the user database</text></g>
    <path d="M500 250H875" class="line dash"/><path d="M855 235l28 15-28 15" fill="#2dd4bf"/><text x="687" y="224" class="small" text-anchor="middle">clean release staging</text>
    <g class="float delay1"><rect x="900" y="155" width="410" height="190" rx="28" class="card2"/><text x="935" y="205" class="label">DISTRIBUTION MODE</text><text x="935" y="245" class="subtitle">runtime DB/log/config excluded</text><text x="935" y="278" class="small">✓ strict safety audit</text><text x="935" y="306" class="small">✓ ZIP contains only public source/demo assets</text></g>
    <rect x="350" y="370" width="700" height="42" rx="18" fill="#122a32" stroke="#34d399"/><text x="700" y="397" class="label" text-anchor="middle">Verified quality gates preserve personal data and keep releases clean.</text>"""
    return write_svg(output / "distribution-safety-animated.svg", body, 1400, 430)


def build_icon_sheet(output: Path) -> Path:
    """Generate a PNG preview of the in-app Pillow icon system.

    Args:
        output: Destination asset folder.

    Returns:
        Written PNG path.

    Raises:
        ImportError: If Pillow is unavailable.

    Example:
        >>> build_icon_sheet(Path('assets'))  # doctest: +SKIP
        PosixPath('assets/icon-system.png')
    """
    from PIL import Image, ImageDraw, ImageFont
    from novafit.icon_factory import IconFactory

    names = [
        "app",
        "dashboard",
        "motivation",
        "recommendations",
        "add",
        "records",
        "profiles",
        "tools",
        "theme",
    ]
    palette = {
        "accent": "#2dd4bf",
        "accent_alt": "#c084fc",
        "panel_alt": "#0c3238",
        "border": "#266274",
        "muted": "#668892",
    }
    width, height = 1260, 330
    sheet = Image.new("RGBA", (width, height), "#04171c")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.text((36, 28), "NovaFit Ultimate · theme-aware Pillow icon system", fill="#f2fbff", font=font)
    for i, name in enumerate(names):
        x = 38 + i * 135
        y = 88
        state = ("active", "default", "muted")[i % 3]
        tile = IconFactory.render(name, palette, 96, state=state)
        sheet.alpha_composite(tile, (x + 4, y + 4))
        label_box = draw.textbbox((0, 0), name, font=font)
        label_w = label_box[2] - label_box[0]
        draw.text((x + 52 - label_w / 2, 215), name, fill="#b7dbe3", font=font)
        draw.text((x + 22, 242), state, fill="#668892", font=font)
    draw.text(
        (38, 286),
        "Antialiased icons are paired with readable labels and expose active, default and muted states.",
        fill="#8db6c2",
        font=font,
    )
    destination = output / "icon-system.png"
    sheet.convert("RGB").save(destination, optimize=True)
    return destination


def generate(output: Path) -> list[Path]:
    """Generate all Ultimate artwork.

    Args:
        output: Asset destination.

    Returns:
        Generated paths.

    Example:
        >>> len(generate(Path('assets'))) >= 7  # doctest: +SKIP
        True
    """
    output.mkdir(parents=True, exist_ok=True)
    return [
        build_banner(output),
        build_profiles(output),
        build_recommendations(output),
        build_atlas(output),
        build_technology(output),
        build_distribution(output),
        build_icon_sheet(output),
    ]


def main() -> int:
    """Generate and report Ultimate artwork.

    Returns:
        Zero after successful output.

    Example:
        >>> main()  # doctest: +SKIP
        0
    """
    args = parser().parse_args()
    for path in generate(args.output.resolve()):
        print(f"Generated {path} [OK]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
