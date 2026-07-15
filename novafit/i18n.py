"""
Module: internationalization
Purpose: Provide deterministic English, Spanish, and Hebrew UI copy with
    explicit RTL metadata and safe fallback behavior.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Standard library only; user-facing strings may be multilingual.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class LanguageDefinition:
    """Describe one supported interface language.

    Args:
        code: Stable locale identifier.
        label: Native display label.
        direction: ``ltr`` or ``rtl``.
        locale: Locale tag used by formatters.

    Example:
        >>> LANGUAGES["he"].direction
        'rtl'
    """

    code: str
    label: str
    direction: str
    locale: str


LANGUAGES: Mapping[str, LanguageDefinition] = {
    "en": LanguageDefinition("en", "English", "ltr", "en-IL"),
    "es": LanguageDefinition("es", "Español", "ltr", "es-ES"),
    "he": LanguageDefinition("he", "עברית", "rtl", "he-IL"),
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "NovaFit Ultimate",
        "app_subtitle": "Local wellness intelligence · profiles · recommendations · multilingual analytics",
        "nav_dashboard": "Command Center",
        "nav_motivation": "Motivation Center",
        "nav_recommendations": "Sport & Data Coach",
        "nav_add": "Add Daily Record",
        "nav_records": "Record Library",
        "nav_profiles": "User Profiles",
        "nav_tools": "Tools & Settings",
        "privacy_title": "PRIVATE BY DESIGN",
        "privacy_body": "SQLite stays on this device. Recommendations are general wellness guidance, not medical advice.",
        "theme": "Theme",
        "language": "Language",
        "user": "User",
        "cycle_theme": "Cycle theme",
        "refresh": "Refresh",
        "ready": "Ready — your records remain on this device.",
        "date": "Date",
        "steps": "Steps",
        "water": "Water (L)",
        "calories": "Calories",
        "mood": "Mood",
        "note": "Private note",
        "save_record": "Save record",
        "clear_form": "Clear form",
        "search": "Search",
        "show_all": "Show all",
        "edit": "Edit",
        "delete": "Delete",
        "create_profile": "Create profile",
        "update_profile": "Update profile",
        "delete_profile": "Delete profile",
        "profile_name": "Display name",
        "avatar": "Avatar",
        "activity_level": "Activity level",
        "sport_focus": "Preferred activity",
        "beginner": "Gentle start",
        "balanced": "Balanced",
        "active": "Active",
        "walking": "Walking",
        "strength": "Strength",
        "mobility": "Mobility",
        "running": "Running",
        "cycling": "Cycling",
        "mixed": "Mixed",
        "recommendation_title": "Sport & Data Recommendation Center",
        "recommendation_disclaimer": "General educational suggestions only. Stop if you feel pain, dizziness, or unusual discomfort and seek qualified guidance.",
        "data_quality": "Data quality",
        "next_action": "Next useful action",
        "weekly_plan": "Suggested weekly rhythm",
        "why_this": "Why this suggestion",
        "file": "File",
        "view": "View",
        "help": "Help",
        "export_json": "Export JSON",
        "export_csv": "Export CSV",
        "export_report": "Export visual report",
        "exit": "Exit",
        "about": "About NovaFit",
        "success_saved": "Record saved",
        "profile_switched": "Active profile changed",
        "settings_saved": "Preferences saved",
        "no_records": "No records yet",
        "today": "Today",
        "days": "days",
        "dark_mode": "Dark",
        "light_mode": "Light",
        "reduced_motion": "Reduce decorative motion",
        "add_sample": "Add starter data",
        "generate_demo": "Generate 30 demo days",
        "clear_data": "Clear active user's records",
        "weather": "Weather",
        "check_weather": "Check weather",
        "goals": "Goals",
        "step_goal": "Step goal",
        "water_goal": "Water goal",
        "calorie_reference": "Calorie reference",
        "chart_range": "Chart range",
        "chart_view": "Chart view",
        "save_preferences": "Save preferences",
    },
    "es": {
        "app_title": "NovaFit Ultimate",
        "app_subtitle": "Inteligencia de bienestar local · perfiles · recomendaciones · analítica multilingüe",
        "nav_dashboard": "Centro de mando",
        "nav_motivation": "Centro de motivación",
        "nav_recommendations": "Coach deportivo y de datos",
        "nav_add": "Añadir registro diario",
        "nav_records": "Biblioteca de registros",
        "nav_profiles": "Perfiles de usuario",
        "nav_tools": "Herramientas y ajustes",
        "privacy_title": "PRIVADO POR DISEÑO",
        "privacy_body": "SQLite permanece en este dispositivo. Las recomendaciones son orientación general, no consejo médico.",
        "theme": "Tema",
        "language": "Idioma",
        "user": "Usuario",
        "cycle_theme": "Cambiar tema",
        "refresh": "Actualizar",
        "ready": "Listo — tus registros permanecen en este dispositivo.",
        "date": "Fecha",
        "steps": "Pasos",
        "water": "Agua (L)",
        "calories": "Calorías",
        "mood": "Ánimo",
        "note": "Nota privada",
        "save_record": "Guardar registro",
        "clear_form": "Limpiar formulario",
        "search": "Buscar",
        "show_all": "Mostrar todo",
        "edit": "Editar",
        "delete": "Eliminar",
        "create_profile": "Crear perfil",
        "update_profile": "Actualizar perfil",
        "delete_profile": "Eliminar perfil",
        "profile_name": "Nombre visible",
        "avatar": "Avatar",
        "activity_level": "Nivel de actividad",
        "sport_focus": "Actividad preferida",
        "beginner": "Inicio suave",
        "balanced": "Equilibrado",
        "active": "Activo",
        "walking": "Caminar",
        "strength": "Fuerza",
        "mobility": "Movilidad",
        "running": "Correr",
        "cycling": "Ciclismo",
        "mixed": "Mixto",
        "recommendation_title": "Centro de recomendaciones deportivas y de datos",
        "recommendation_disclaimer": "Solo sugerencias educativas generales. Detente ante dolor, mareo o malestar inusual y consulta a un profesional cualificado.",
        "data_quality": "Calidad de datos",
        "next_action": "Siguiente acción útil",
        "weekly_plan": "Ritmo semanal sugerido",
        "why_this": "Por qué se sugiere",
        "file": "Archivo",
        "view": "Vista",
        "help": "Ayuda",
        "export_json": "Exportar JSON",
        "export_csv": "Exportar CSV",
        "export_report": "Exportar informe visual",
        "exit": "Salir",
        "about": "Acerca de NovaFit",
        "success_saved": "Registro guardado",
        "profile_switched": "Perfil activo cambiado",
        "settings_saved": "Preferencias guardadas",
        "no_records": "Aún no hay registros",
        "today": "Hoy",
        "days": "días",
        "dark_mode": "Oscuro",
        "light_mode": "Claro",
        "reduced_motion": "Reducir movimiento decorativo",
        "add_sample": "Añadir datos iniciales",
        "generate_demo": "Generar 30 días demo",
        "clear_data": "Borrar registros del usuario activo",
        "weather": "Clima",
        "check_weather": "Consultar clima",
        "goals": "Objetivos",
        "step_goal": "Objetivo de pasos",
        "water_goal": "Objetivo de agua",
        "calorie_reference": "Referencia de calorías",
        "chart_range": "Rango del gráfico",
        "chart_view": "Vista del gráfico",
        "save_preferences": "Guardar preferencias",
    },
    "he": {
        "app_title": "NovaFit Ultimate",
        "app_subtitle": "תובנות רווחה מקומיות · פרופילים · המלצות · ניתוח רב־לשוני",
        "nav_dashboard": "מרכז בקרה",
        "nav_motivation": "מרכז מוטיבציה",
        "nav_recommendations": "מאמן פעילות ונתונים",
        "nav_add": "הוספת רישום יומי",
        "nav_records": "ספריית רישומים",
        "nav_profiles": "פרופילי משתמשים",
        "nav_tools": "כלים והגדרות",
        "privacy_title": "פרטיות כברירת מחדל",
        "privacy_body": "SQLite נשאר במכשיר. ההמלצות הן מידע כללי ואינן ייעוץ רפואי.",
        "theme": "ערכת נושא",
        "language": "שפה",
        "user": "משתמש",
        "cycle_theme": "החלפת ערכת נושא",
        "refresh": "רענון",
        "ready": "מוכן — הנתונים נשארים במכשיר שלך.",
        "date": "תאריך",
        "steps": "צעדים",
        "water": "מים (ליטר)",
        "calories": "קלוריות",
        "mood": "מצב רוח",
        "note": "הערה פרטית",
        "save_record": "שמירת רישום",
        "clear_form": "ניקוי טופס",
        "search": "חיפוש",
        "show_all": "הצגת הכל",
        "edit": "עריכה",
        "delete": "מחיקה",
        "create_profile": "יצירת פרופיל",
        "update_profile": "עדכון פרופיל",
        "delete_profile": "מחיקת פרופיל",
        "profile_name": "שם תצוגה",
        "avatar": "אווטאר",
        "activity_level": "רמת פעילות",
        "sport_focus": "פעילות מועדפת",
        "beginner": "התחלה עדינה",
        "balanced": "מאוזן",
        "active": "פעיל",
        "walking": "הליכה",
        "strength": "כוח",
        "mobility": "ניידות",
        "running": "ריצה",
        "cycling": "רכיבה",
        "mixed": "משולב",
        "recommendation_title": "מרכז המלצות לפעילות ולנתונים",
        "recommendation_disclaimer": "הצעות כלליות לצורכי למידה בלבד. יש לעצור במקרה של כאב, סחרחורת או אי־נוחות חריגה ולפנות לייעוץ מוסמך.",
        "data_quality": "איכות נתונים",
        "next_action": "הפעולה השימושית הבאה",
        "weekly_plan": "קצב שבועי מוצע",
        "why_this": "למה זו ההמלצה",
        "file": "קובץ",
        "view": "תצוגה",
        "help": "עזרה",
        "export_json": "ייצוא JSON",
        "export_csv": "ייצוא CSV",
        "export_report": "ייצוא דוח חזותי",
        "exit": "יציאה",
        "about": "אודות NovaFit",
        "success_saved": "הרישום נשמר",
        "profile_switched": "הפרופיל הפעיל הוחלף",
        "settings_saved": "ההעדפות נשמרו",
        "no_records": "עדיין אין רישומים",
        "today": "היום",
        "days": "ימים",
        "dark_mode": "כהה",
        "light_mode": "בהיר",
        "reduced_motion": "הפחתת תנועה דקורטיבית",
        "add_sample": "הוספת נתוני התחלה",
        "generate_demo": "יצירת 30 ימי הדגמה",
        "clear_data": "מחיקת רישומי המשתמש הפעיל",
        "weather": "מזג אוויר",
        "check_weather": "בדיקת מזג אוויר",
        "goals": "יעדים",
        "step_goal": "יעד צעדים",
        "water_goal": "יעד מים",
        "calorie_reference": "ייחוס קלוריות",
        "chart_range": "טווח תרשים",
        "chart_view": "תצוגת תרשים",
        "save_preferences": "שמירת העדפות",
    },
}


def normalize_language(value: str) -> str:
    """Normalize a language code or native label.

    Args:
        value: Locale code or display label.

    Returns:
        Stable ``en``, ``es``, or ``he`` code.

    Raises:
        ValueError: If the language is unsupported.

    Example:
        >>> normalize_language("Español")
        'es'
    """
    normalized = value.strip().lower()
    aliases = {
        "english": "en",
        "inglés": "en",
        "ingles": "en",
        "spanish": "es",
        "español": "es",
        "espanol": "es",
        "hebrew": "he",
        "עברית": "he",
    }
    normalized = aliases.get(normalized, normalized.split("-")[0])
    if normalized not in LANGUAGES:
        raise ValueError(f"Unsupported language: {value}")
    return normalized


def language_labels() -> tuple[str, ...]:
    """Return native language labels in display order.

    Returns:
        Native labels for a GUI selector.

    Example:
        >>> language_labels()
        ('English', 'Español', 'עברית')
    """
    return tuple(item.label for item in LANGUAGES.values())


def language_label(value: str) -> str:
    """Return the native label for a language value.

    Args:
        value: Language code or display label.

    Returns:
        Native display label.

    Example:
        >>> language_label("he")
        'עברית'
    """
    return LANGUAGES[normalize_language(value)].label


def direction_for(value: str) -> str:
    """Return the layout direction for a language.

    Args:
        value: Language code or label.

    Returns:
        ``ltr`` or ``rtl``.

    Example:
        >>> direction_for("he")
        'rtl'
    """
    return LANGUAGES[normalize_language(value)].direction


def tr(language: str, key: str, **values: object) -> str:
    """Translate one key with English fallback and safe formatting.

    Args:
        language: Language code or label.
        key: Translation key.
        **values: Optional ``str.format`` values.

    Returns:
        Translated and formatted text.

    Raises:
        KeyError: If the key is missing from every language.

    Example:
        >>> tr("es", "nav_dashboard")
        'Centro de mando'
    """
    code = normalize_language(language)
    template = TRANSLATIONS.get(code, {}).get(key, TRANSLATIONS["en"].get(key))
    if template is None:
        raise KeyError(f"Missing translation key: {key}")
    return template.format(**values)
