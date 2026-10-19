"""
Module: sport and data recommendations
Purpose: Turn local tracking signals and user preferences into conservative,
    explainable wellness suggestions without pretending to provide medical care.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Standard library only; recommendations are general and educational.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from .analytics import calculate_dashboard
from .config import AppSettings
from .i18n import normalize_language, tr
from .models import HealthEntry, UserProfile
from .workouts import WorkoutSession, training_signals

# Session load this week ÷ the previous three weeks' weekly mean that counts as a sharp jump.
LOAD_JUMP_RATIO = 1.5


@dataclass(frozen=True, slots=True)
class RecommendationItem:
    """Describe one explainable recommendation card.

    Args:
        category: Stable category such as ``movement`` or ``data``.
        title: Short recommendation title.
        action: Concrete, conservative next step.
        reason: Evidence-based explanation.
        priority: ``high``, ``medium``, or ``low``.

    Example:
        >>> RecommendationItem('data', 'Track', 'Log today', 'More data helps', 'high').priority
        'high'
    """

    category: str
    title: str
    action: str
    reason: str
    priority: str


@dataclass(frozen=True, slots=True)
class RecommendationPlan:
    """Store the complete recommendation result for GUI, CLI, and reports.

    Attributes:
        data_confidence_pct: Confidence based on record count and coverage.
        summary: One-line interpretation.
        weekly_plan: Safe, preference-aware activity rhythm.
        items: Explainable recommendation cards.
        disclaimer: Safety and scope boundary.

    Example:
        >>> RecommendationPlan(0, 'Start', (), (), 'General only').data_confidence_pct
        0
    """

    data_confidence_pct: int
    summary: str
    weekly_plan: tuple[str, ...]
    items: tuple[RecommendationItem, ...]
    disclaimer: str


_COPY = {
    "en": {
        "disclaimer": (
            "General educational wellness suggestions only—not medical advice. "
            "Stop if you feel pain, dizziness, chest discomfort, or unusual symptoms, "
            "and seek qualified professional guidance."
        ),
        "empty": "Add a few daily records before NovaFit compares patterns.",
        "emerging": "Your pattern is emerging; prioritize consistent tracking over intensity.",
        "stable": "Your tracking base is strong enough for cautious pattern-based suggestions.",
        "track_title": "Build a reliable baseline",
        "track_action": "Log steps, water, mood, and optional notes on at least 7 different days.",
        "track_reason": "A small archive can describe individual days but cannot support stable trend claims.",
        "coverage_title": "Close the missing-day gaps",
        "coverage_action": "Use a 30-second evening check-in on untracked days.",
        "coverage_reason": "Calendar gaps can look like performance drops even when they are only missing data.",
        "walk_title": "Use short movement blocks",
        "walk_action": "Consider one or two comfortable 10-minute walks or movement breaks today.",
        "walk_reason": "Recent average steps are below half of the configured goal; gradual additions are easier to sustain.",
        "progress_title": "Progress gradually",
        "progress_action": "Keep the next session comfortable and increase duration or intensity slowly.",
        "progress_reason": "A recent drop or limited history makes conservative progression more appropriate than a hard jump.",
        "water_title": "Strengthen hydration tracking",
        "water_action": "Place water where you work and record intake at two fixed moments in the day.",
        "water_reason": "Average recorded water is below the configured hydration target.",
        "recovery_title": "Protect recovery",
        "recovery_action": "Keep at least one low-intensity or rest day and protect sleep and regular meals.",
        "recovery_reason": "Sustainable routines need recovery; NovaFit does not treat every day as a maximum-effort day.",
        "mood_title": "Add context to the numbers",
        "mood_action": "Record a short mood label or note after activity on several days.",
        "mood_reason": "Context helps distinguish a productive routine from one that feels draining.",
        "load_title": "Ease into the next sessions",
        "load_action": "Keep the next two or three sessions shorter or easier, and plan one rest day.",
        "load_reason": (
            "Your session load over the last 7 days is {pct}% above your average week of the three before; "
            "sharp jumps are harder to recover from than gradual ones."
        ),
        "resume_title": "Restart with something short",
        "resume_action": "Log one comfortable 15–20 minute session this week to restart the rhythm.",
        "resume_reason": "No training session was logged in the last 14 days.",
        "start_title": "Start your training log",
        "start_action": "Log your walks, rides or workouts in the Training tab or with --add-workout.",
        "start_reason": "Sessions add duration and effort to the daily numbers, so the coach can read your week.",
        "variety_title": "Add some variety",
        "variety_action": "Consider one short mobility or strength session next to your usual {kind}.",
        "variety_reason": "Every session of the last four weeks was {kind}; mixing types spreads the load.",
    },
    "es": {
        "disclaimer": (
            "Sugerencias generales de bienestar con fines educativos; no son consejo médico. "
            "Detente ante dolor, mareo, molestias en el pecho o síntomas inusuales y busca orientación profesional cualificada."
        ),
        "empty": "Añade algunos registros diarios antes de comparar patrones.",
        "emerging": "Tu patrón está apareciendo; prioriza registrar con constancia antes que aumentar la intensidad.",
        "stable": "Tu base de datos permite sugerencias prudentes basadas en patrones.",
        "track_title": "Construye una base confiable",
        "track_action": "Registra pasos, agua, ánimo y notas opcionales durante al menos 7 días distintos.",
        "track_reason": "Un archivo pequeño describe días aislados, pero no sostiene tendencias estables.",
        "coverage_title": "Reduce los huecos de registro",
        "coverage_action": "Haz un check-in nocturno de 30 segundos en los días sin datos.",
        "coverage_reason": "Los huecos pueden parecer caídas de rendimiento aunque solo sean datos faltantes.",
        "walk_title": "Usa bloques cortos de movimiento",
        "walk_action": "Considera una o dos caminatas cómodas de 10 minutos o pausas activas hoy.",
        "walk_reason": "El promedio reciente está por debajo de la mitad del objetivo; aumentar gradualmente suele ser más sostenible.",
        "progress_title": "Progresa gradualmente",
        "progress_action": "Mantén la próxima sesión cómoda y aumenta duración o intensidad poco a poco.",
        "progress_reason": "Una bajada reciente o poco historial favorece una progresión conservadora.",
        "water_title": "Mejora el seguimiento de hidratación",
        "water_action": "Deja agua cerca del lugar de trabajo y registra la ingesta en dos momentos fijos.",
        "water_reason": "El promedio registrado está por debajo del objetivo configurado.",
        "recovery_title": "Protege la recuperación",
        "recovery_action": "Conserva al menos un día suave o de descanso y protege sueño y comidas regulares.",
        "recovery_reason": "Una rutina sostenible necesita recuperación; no todos los días deben ser de máximo esfuerzo.",
        "mood_title": "Añade contexto a los números",
        "mood_action": "Registra ánimo o una nota breve después de la actividad durante varios días.",
        "mood_reason": "El contexto ayuda a distinguir una rutina productiva de una que se siente agotadora.",
        "load_title": "Suaviza las próximas sesiones",
        "load_action": "Haz las próximas dos o tres sesiones más cortas o suaves y planifica un día de descanso.",
        "load_reason": (
            "Tu carga de los últimos 7 días está un {pct}% por encima de tu semana media de las tres anteriores; "
            "los saltos bruscos cuestan más de recuperar que los graduales."
        ),
        "resume_title": "Vuelve con algo corto",
        "resume_action": "Registra esta semana una sesión cómoda de 15–20 minutos para retomar el ritmo.",
        "resume_reason": "No hay sesiones de entrenamiento registradas en los últimos 14 días.",
        "start_title": "Empieza tu registro de entrenamientos",
        "start_action": "Anota caminatas, salidas en bici o rutinas en la pestaña Entrenos o con --add-workout.",
        "start_reason": "Las sesiones añaden duración y esfuerzo a los números diarios para que el coach lea tu semana.",
        "variety_title": "Añade algo de variedad",
        "variety_action": "Considera una sesión corta de movilidad o fuerza junto a tus sesiones de {kind}.",
        "variety_reason": "Todas las sesiones de las últimas cuatro semanas fueron de {kind}; mezclar tipos reparte la carga.",
    },
    "he": {
        "disclaimer": (
            "המלצות כלליות לצורכי למידה בלבד ואינן ייעוץ רפואי. "
            "יש לעצור במקרה של כאב, סחרחורת, אי־נוחות בחזה או תסמינים חריגים ולפנות לייעוץ מוסמך."
        ),
        "empty": "יש להוסיף מספר רישומים יומיים לפני השוואת דפוסים.",
        "emerging": "הדפוס מתחיל להתבהר; עדיף להתמקד ברישום עקבי לפני העלאת עצימות.",
        "stable": "בסיס הנתונים מספיק להצעות זהירות המבוססות על דפוסים.",
        "track_title": "בניית בסיס אמין",
        "track_action": "יש לרשום צעדים, מים, מצב רוח והערות אופציונליות לפחות ב־7 ימים שונים.",
        "track_reason": "ארכיון קטן מתאר ימים בודדים אך אינו מספיק לטענות יציבות על מגמות.",
        "coverage_title": "צמצום פערי הרישום",
        "coverage_action": "אפשר לבצע בדיקת ערב של 30 שניות בימים ללא נתונים.",
        "coverage_reason": "פערים בלוח השנה עלולים להיראות כירידה בביצועים אף שהם רק נתונים חסרים.",
        "walk_title": "שימוש במקטעי תנועה קצרים",
        "walk_action": "אפשר לשקול הליכה נוחה אחת או שתיים של 10 דקות או הפסקות תנועה היום.",
        "walk_reason": "ממוצע הצעדים האחרון נמוך מחצי היעד; תוספת הדרגתית קלה יותר להתמדה.",
        "progress_title": "התקדמות הדרגתית",
        "progress_action": "כדאי לשמור על אימון נוח ולהגדיל זמן או עצימות בהדרגה.",
        "progress_reason": "ירידה אחרונה או היסטוריה מוגבלת מצדיקות התקדמות שמרנית.",
        "water_title": "חיזוק מעקב השתייה",
        "water_action": "אפשר להציב מים ליד אזור העבודה ולרשום שתייה בשני זמנים קבועים ביום.",
        "water_reason": "ממוצע המים הרשום נמוך מהיעד שהוגדר.",
        "recovery_title": "הגנה על התאוששות",
        "recovery_action": "יש לשמור לפחות יום אחד בעצימות נמוכה או מנוחה ולהגן על שינה וארוחות סדירות.",
        "recovery_reason": "שגרה בת־קיימא כוללת התאוששות; לא כל יום צריך להיות מאמץ מרבי.",
        "mood_title": "הוספת הקשר למספרים",
        "mood_action": "כדאי לרשום מצב רוח או הערה קצרה לאחר פעילות במספר ימים.",
        "mood_reason": "הקשר עוזר להבחין בין שגרה מועילה לשגרה מתישה.",
        "load_title": "הקלה באימונים הבאים",
        "load_action": "כדאי לקצר או להקל את שניים או שלושה האימונים הבאים ולתכנן יום מנוחה.",
        "load_reason": (
            "העומס ב־7 הימים האחרונים גבוה ב־{pct}% מהשבוע הממוצע בשלושת השבועות שלפניהם; "
            "קפיצות חדות קשות יותר להתאוששות מעלייה הדרגתית."
        ),
        "resume_title": "חזרה עם משהו קצר",
        "resume_action": "אפשר לרשום השבוע אימון נוח של 15–20 דקות כדי לחזור לקצב.",
        "resume_reason": "לא נרשם אף אימון ב־14 הימים האחרונים.",
        "start_title": "התחלת יומן האימונים",
        "start_action": "אפשר לרשום הליכות, רכיבות או אימונים בלשונית האימונים.",
        "start_reason": "האימונים מוסיפים משך ומאמץ למספרים היומיים, כך שהמאמן יכול לקרוא את השבוע.",
        "variety_title": "הוספת גיוון",
        "variety_action": "אפשר לשקול אימון קצר של גמישות או כוח לצד {kind} הרגיל.",
        "variety_reason": "כל האימונים בארבעת השבועות האחרונים היו {kind}; גיוון מפזר את העומס.",
    },
}


def build_recommendation_plan(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
    profile: UserProfile,
    language: str | None = None,
    *,
    sessions: Iterable[WorkoutSession] | None = None,
    today: date | None = None,
) -> RecommendationPlan:
    """Build a conservative, explainable recommendation plan.

    Args:
        entries: Active profile's health records.
        settings: Current goals and preferences.
        profile: Activity-level and sport-focus preferences.
        language: Optional output-language override.
        sessions: Optional training sessions; ``None`` keeps the daily-record-only plan.
        today: Reference day for the rolling training windows (tests pin it).

    Returns:
        Recommendation plan for GUI, CLI, and reports.

    Raises:
        ValueError: If settings or language are invalid.

    Example:
        >>> plan = build_recommendation_plan([], AppSettings(), UserProfile.build('Demo'))
        >>> plan.data_confidence_pct
        0
    """
    settings.validate()
    code = normalize_language(language or profile.language)
    copy = _COPY[code]
    rows = list(entries)
    stats = calculate_dashboard(rows, settings)
    confidence = min(
        100, round(min(1.0, stats.entry_count / 14) * 70 + min(1.0, stats.tracking_coverage_pct / 100) * 30)
    )
    if stats.entry_count == 0:
        summary = copy["empty"]
    elif confidence < 65:
        summary = copy["emerging"]
    else:
        summary = copy["stable"]

    items: list[RecommendationItem] = []
    if stats.entry_count < 7:
        items.append(
            RecommendationItem(
                "data", copy["track_title"], copy["track_action"], copy["track_reason"], "high"
            )
        )
    elif stats.tracking_coverage_pct < 75:
        items.append(
            RecommendationItem(
                "data", copy["coverage_title"], copy["coverage_action"], copy["coverage_reason"], "high"
            )
        )

    if stats.entry_count and stats.average_steps < settings.step_goal * 0.5:
        items.append(
            RecommendationItem(
                "movement", copy["walk_title"], copy["walk_action"], copy["walk_reason"], "high"
            )
        )
    else:
        items.append(
            RecommendationItem(
                "movement", copy["progress_title"], copy["progress_action"], copy["progress_reason"], "medium"
            )
        )

    training_items = _training_items(sessions, code, today)
    items.extend(item for item in training_items if item.priority != "low")

    if stats.entry_count and stats.average_water_l < settings.water_goal_l:
        items.append(
            RecommendationItem(
                "hydration", copy["water_title"], copy["water_action"], copy["water_reason"], "medium"
            )
        )

    items.append(
        RecommendationItem(
            "recovery", copy["recovery_title"], copy["recovery_action"], copy["recovery_reason"], "medium"
        )
    )
    mood_days = sum(1 for entry in rows if entry.mood)
    if stats.entry_count >= 4 and mood_days / max(1, stats.entry_count) < 0.5:
        items.append(
            RecommendationItem("context", copy["mood_title"], copy["mood_action"], copy["mood_reason"], "low")
        )
    items.extend(item for item in training_items if item.priority == "low")

    weekly = _weekly_rhythm(profile, code)
    return RecommendationPlan(confidence, summary, weekly, tuple(items[:5]), copy["disclaimer"])


def format_recommendation_plan(
    plan: RecommendationPlan,
    profile: UserProfile,
    language: str | None = None,
) -> str:
    """Format a recommendation plan for terminal output.

    Args:
        plan: Recommendation result.
        profile: Active profile.
        language: Optional report-language override.

    Returns:
        Readable terminal report.

    Example:
        >>> 'DATA CONFIDENCE' in format_recommendation_plan(RecommendationPlan(0, 'Start', (), (), 'General'), UserProfile.build('Demo'))
        True
    """
    code = normalize_language(language or profile.language)
    lines = [
        tr(code, "recommendation_report_title", name=profile.display_name),
        "=" * 58,
        f"{tr(code, 'data_confidence').upper()}: {plan.data_confidence_pct}%",
        plan.summary,
        "",
        tr(code, "recommendations_heading").upper(),
    ]
    for index, item in enumerate(plan.items, start=1):
        priority = tr(code, f"priority_{item.priority}").upper()
        lines.extend(
            (
                f"{index}. {item.title} [{priority}]",
                f"   {tr(code, 'action')}: {item.action}",
                f"   {tr(code, 'why')}: {item.reason}",
            )
        )
    lines.extend(("", tr(code, "suggested_weekly_rhythm").upper()))
    lines.extend(f"- {item}" for item in plan.weekly_plan)
    lines.extend(("", plan.disclaimer))
    return "\n".join(lines)


def _training_items(
    sessions: Iterable[WorkoutSession] | None, language: str, today: date | None
) -> list[RecommendationItem]:
    """Return training-log cards; empty when no session list was supplied."""
    if sessions is None:
        return []
    copy = _COPY[language]
    signals = training_signals(list(sessions), today=today)
    items: list[RecommendationItem] = []
    if signals.total_sessions == 0:
        items.append(
            RecommendationItem("training", copy["start_title"], copy["start_action"], copy["start_reason"], "low")
        )
        return items
    if signals.load_ratio is not None and signals.load_ratio >= LOAD_JUMP_RATIO:
        pct = round((signals.load_ratio - 1) * 100)
        items.append(
            RecommendationItem(
                "training", copy["load_title"], copy["load_action"], copy["load_reason"].format(pct=pct), "high"
            )
        )
    elif signals.sessions_14d == 0:
        items.append(
            RecommendationItem(
                "training", copy["resume_title"], copy["resume_action"], copy["resume_reason"], "medium"
            )
        )
    if signals.single_kind:
        kind = tr(language, f"workout_kind_{signals.single_kind}").lower()
        items.append(
            RecommendationItem(
                "training",
                copy["variety_title"],
                copy["variety_action"].format(kind=kind),
                copy["variety_reason"].format(kind=kind),
                "low",
            )
        )
    return items


def _weekly_rhythm(profile: UserProfile, language: str) -> tuple[str, ...]:
    plans = {
        "en": {
            "beginner": (
                "3 comfortable movement days of 10–20 minutes",
                "2 short mobility or stretch breaks",
                "2 recovery or optional easy days",
            ),
            "balanced": (
                "3–4 moderate movement days of 20–30 minutes",
                "2 strength or mobility sessions at a comfortable level",
                "At least 1 deliberate recovery day",
            ),
            "active": (
                "4–5 varied activity days without making every day maximal",
                "2 strength or mobility blocks",
                "At least 1 easy recovery day",
            ),
        },
        "es": {
            "beginner": (
                "3 días de movimiento cómodo de 10–20 minutos",
                "2 pausas cortas de movilidad o estiramiento",
                "2 días de recuperación o actividad suave opcional",
            ),
            "balanced": (
                "3–4 días de movimiento moderado de 20–30 minutos",
                "2 sesiones cómodas de fuerza o movilidad",
                "Al menos 1 día deliberado de recuperación",
            ),
            "active": (
                "4–5 días variados sin convertir todos en esfuerzo máximo",
                "2 bloques de fuerza o movilidad",
                "Al menos 1 día suave de recuperación",
            ),
        },
        "he": {
            "beginner": (
                "3 ימי תנועה נוחה של 10–20 דקות",
                "2 הפסקות קצרות של ניידות או מתיחות",
                "2 ימי התאוששות או פעילות קלה אופציונלית",
            ),
            "balanced": (
                "3–4 ימי תנועה מתונה של 20–30 דקות",
                "2 אימוני כוח או ניידות ברמה נוחה",
                "לפחות יום התאוששות מתוכנן אחד",
            ),
            "active": (
                "4–5 ימי פעילות מגוונים בלי להפוך כל יום למאמץ מרבי",
                "2 מקטעי כוח או ניידות",
                "לפחות יום התאוששות קל אחד",
            ),
        },
    }
    selected = plans[language][profile.activity_level]
    focus_name = tr(language, f"sport_{profile.sport_focus}")
    focus = {
        "en": f"Preferred focus: {focus_name}. Adapt the rhythm to your environment and current comfort.",
        "es": f"Enfoque preferido: {focus_name}. Adapta el ritmo a tu entorno y comodidad actual.",
        "he": f"הפעילות המועדפת: {focus_name}. מומלץ להתאים את הקצב לסביבה ולהרגשה הנוכחית.",
    }[language]
    return (*selected, focus)
