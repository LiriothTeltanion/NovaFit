"use strict";

const COPY = {
  en: {
    meta: {
      title: "NovaFit 4.2 · Local-first wellness intelligence",
      description: "NovaFit is a local-first Windows wellness intelligence studio with private profiles, multilingual analytics, Hebrew RTL, and verified backups."
    },
    a11y: {
      skip: "Skip to main content",
      primaryNav: "Primary navigation",
      home: "NovaFit home",
      openMenu: "Open navigation menu",
      closeMenu: "Close navigation menu",
      language: "Language",
      highlights: "Product highlights",
      heroDemo: "Public NovaFit interface simulation",
      previewLanguage: "Interface language preview",
      timeWindow: "Sample time window",
      demoChart: "Illustrative movement trend chart",
      themeGallery: "NovaFit theme gallery",
      privacyDiagram: "Privacy boundaries diagram",
      architectureDiagram: "NovaFit architecture flow"
    },
    nav: { experience: "Experience", demo: "Public demo", themes: "Themes", privacy: "Privacy", architecture: "Architecture", install: "Install site" },
    hero: {
      eyebrow: "NOVA HEALTH INTELLIGENCE · 4.2",
      title: "Your signals. Your system. Your device.",
      lede: "Turn daily observations into an understandable routine—with multilingual analytics, purposeful motion, and private profiles that remain local.",
      download: "Download latest release",
      explore: "Explore the public demo",
      trustLocal: "Local SQLite profiles",
      trustLanguages: "EN · ES · HE + RTL",
      trustBackup: "Verified ZIP backups",
      publicSample: "PUBLIC SAMPLE",
      disclaimer: "Illustrative public values only. No personal records are loaded on this website."
    },
    facts: {
      title: "Verified project facts", version: "current version", tests: "automated tests", themes: "visual themes", assets: "public assets",
      localFirst: "Local-first", loading: "Checking local project facts…", verified: "Verified from the deployed project manifest", fallback: "Offline fallback facts · no remote tracking"
    },
    experience: {
      eyebrow: "THE DESKTOP EXPERIENCE",
      title: "One command center. Three languages. Your rhythm.",
      body: "NovaFit makes patterns readable without turning observations into diagnoses. Switch from English to Hebrew and the entire workspace becomes truly right-to-left.",
      realCapture: "REAL APP CAPTURE",
      captionEn: "English command center with profile controls, goal signals, hydration current, weekday rhythm, and a readable signal summary.",
      captionHe: "Hebrew command center with true right-to-left navigation, controls, summaries, tables, and analytics layout.",
      altEn: "NovaFit command center in English",
      altHe: "NovaFit command center in Hebrew with right-to-left layout"
    },
    features: {
      analyticsKicker: "FOUR ANALYTICS STUDIOS", analyticsTitle: "From a day to a pattern", analyticsBody: "Command Center, Trend Lab, Consistency Map, and Training Atlas turn stored observations into transparent, exportable views.",
      profilesKicker: "ISOLATED PROFILES", profilesTitle: "Clear boundaries by design", profilesBody: "Each profile keeps its own records and preferences in SQLite, with explicit switching and complete backup coverage.",
      motionKicker: "PURPOSEFUL MOTION", motionTitle: "Alive, never distracting", motionBody: "Efficient animations pause when hidden and respect your device’s reduced-motion preference."
    },
    demo: {
      consistency: "ROUTINE CONSISTENCY", days: "TRACKED DAYS", coverage: "COVERAGE", languages: "LANGUAGES",
      eyebrow: "TRY THE STORY", title: "Explore a safe, public simulation", body: "Change the time window to see how the narrative responds. These fixed example values are bundled with the site and are never saved.",
      sampleTitle: "PUBLIC ROUTINE SAMPLE", sampleSubtitle: "Illustrative observations · not medical advice", routineScore: "ROUTINE SCORE", trackedDays: "TRACKED DAYS", goalDays: "BOTH-GOAL DAYS", signal: "RECENT SIGNAL",
      publicEntries: "public sample entries", exampleGoal: "illustrative target days", comparedWindow: "than the prior window", movementSignal: "Movement signal", publicUnits: "relative sample units", earlier: "Earlier", recent: "Recent",
      summaryKicker: "EXPLAINABLE SUMMARY", noUpload: "Nothing from this demo is uploaded or stored.",
      noisier: "VARIABLE", steadier: "STEADIER", established: "ESTABLISHED",
      summaryTitle7: "A short window can change quickly.", summaryCopy7: "The seven-day sample is useful for noticing, but too short for strong conclusions. NovaFit keeps the language cautious.",
      summaryTitle30: "The routine is becoming more consistent.", summaryCopy30: "The recent sample has fewer gaps than the previous window. NovaFit would suggest one realistic action—not a diagnosis.",
      summaryTitle90: "A longer view reveals the rhythm.", summaryCopy90: "The ninety-day sample makes recurring days and recovery gaps easier to see while keeping the interpretation transparent.",
      announcement: "Public {range}-day sample selected. Routine score {score} out of 100."
    },
    themes: {
      eyebrow: "A SYSTEM THAT FEELS YOURS", title: "Twelve visual worlds. One readable language.", body: "Every chart, icon, focus state, and status color adapts as one system. Choose a theme to preview a real exported analytics view.",
      realExport: "REAL PUBLIC-DEMO EXPORT", previewAlt: "{name} NovaFit analytics theme"
    },
    privacy: {
      eyebrow: "PRIVATE BY DESIGN", title: "Your records do not need an audience.", body: "The desktop app stores profiles in local SQLite databases. This showcase is a separate static website: it has no account, no health-record form, no analytics tracker, and no route into your NovaFit database.",
      readSecurity: "Read the security model", core: "YOUR LOCAL RECORDS", profileBoundary: "Profile boundary", backupBoundary: "Verified backup boundary", publicBoundary: "Static showcase stays outside",
      localTitle: "Local by default", localBody: "Your daily records stay on the Windows device unless you deliberately export or back them up.",
      siteTitle: "A showcase, not a portal", siteBody: "The Pages site uses only fixed public examples and a device-local language preference.",
      backupTitle: "Backups you can verify", backupBody: "Complete ZIP archives cover every profile and include integrity evidence and SHA-256 verification."
    },
    architecture: {
      eyebrow: "CLEAR ARCHITECTURE", title: "Desktop product and public story—connected by releases, not private data.", body: "The application owns records and exports. GitHub Actions tests the public code, publishes a release, and refreshes this static showcase using verified project facts.",
      desktop: "Windows desktop", desktopBody: "Tkinter interface and local Python logic", storage: "Profile storage", storageBody: "Isolated SQLite records and preferences", backup: "Verified export", backupBody: "ZIP, CSV, JSON, PNG, and offline HTML",
      publicLane: "PUBLIC AUTOMATION LANE", quality: "Quality matrix", release: "GitHub Release", noRecords: "No personal record crosses into this lane."
    },
    backup: {
      eyebrow: "PORTABLE WITH INTENTION", title: "One archive. Every profile. Evidence included.", body: "NovaFit checks database integrity, packages the complete local profile set, and records cryptographic checksums so restoration is understandable—not mysterious.",
      inspect: "Inspect", inspectBody: "Validate each SQLite database", package: "Package", packageBody: "Collect profiles and configuration", verify: "Verify", verifyBody: "Write SHA-256 integrity evidence"
    },
    release: {
      eyebrow: "NOVA / FIT 4.2", title: "Ready to make your routine visible?", body: "Download the latest audited Windows release or explore the complete open-source project. NovaFit remains a personal tracking tool, not medical advice.",
      download: "Download for Windows", source: "View source on GitHub", note: "Open source · Local-first · English, Spanish, and Hebrew"
    },
    footer: { tagline: "PERSONAL SIGNALS, CLEARLY HELD", disclaimer: "Personal tracking only. No medical claims.", releases: "Releases", top: "Back to top ↑" },
    errors: { image: "Preview unavailable. The product description remains accessible." },
    toast: { installed: "NovaFit showcase installed for offline access.", installReady: "The NovaFit showcase can now be installed.", update: "A refreshed offline version will be ready next time you open the site." }
  },
  es: {
    meta: {
      title: "NovaFit 4.2 · Inteligencia de bienestar local-first",
      description: "NovaFit es un estudio de bienestar para Windows, local-first, con perfiles privados, analíticas multilingües, hebreo RTL y copias verificadas."
    },
    a11y: {
      skip: "Saltar al contenido principal", primaryNav: "Navegación principal", home: "Inicio de NovaFit", openMenu: "Abrir menú de navegación", closeMenu: "Cerrar menú de navegación", language: "Idioma", highlights: "Aspectos destacados del producto", heroDemo: "Simulación pública de la interfaz NovaFit", previewLanguage: "Vista previa del idioma de la interfaz", timeWindow: "Ventana temporal de la muestra", demoChart: "Gráfico ilustrativo de tendencia de movimiento", themeGallery: "Galería de temas NovaFit", privacyDiagram: "Diagrama de límites de privacidad", architectureDiagram: "Flujo de arquitectura de NovaFit"
    },
    nav: { experience: "Experiencia", demo: "Demo pública", themes: "Temas", privacy: "Privacidad", architecture: "Arquitectura", install: "Instalar sitio" },
    hero: {
      eyebrow: "INTELIGENCIA DE BIENESTAR NOVA · 4.2", title: "Tus señales. Tu sistema. Tu dispositivo.", lede: "Convierte observaciones diarias en una rutina comprensible, con analíticas multilingües, movimiento útil y perfiles privados que permanecen locales.", download: "Descargar última versión", explore: "Explorar la demo pública", trustLocal: "Perfiles SQLite locales", trustLanguages: "EN · ES · HE + RTL", trustBackup: "Copias ZIP verificadas", publicSample: "MUESTRA PÚBLICA", disclaimer: "Solo valores públicos ilustrativos. Este sitio no carga registros personales."
    },
    facts: { title: "Datos verificados del proyecto", version: "versión actual", tests: "pruebas automatizadas", themes: "temas visuales", assets: "recursos públicos", localFirst: "Local-first", loading: "Comprobando los datos locales del proyecto…", verified: "Verificado desde el manifiesto publicado del proyecto", fallback: "Datos alternativos sin conexión · sin seguimiento remoto" },
    experience: {
      eyebrow: "LA EXPERIENCIA DE ESCRITORIO", title: "Un centro de mando. Tres idiomas. Tu ritmo.", body: "NovaFit hace legibles los patrones sin convertir observaciones en diagnósticos. Al cambiar de inglés a hebreo, todo el espacio se transforma correctamente a derecha-a-izquierda.", realCapture: "CAPTURA REAL DE LA APP", captionEn: "Centro de mando en inglés con controles de perfil, señales de objetivos, hidratación, ritmo semanal y un resumen comprensible.", captionHe: "Centro de mando en hebreo con navegación, controles, resúmenes, tablas y analíticas realmente de derecha a izquierda.", altEn: "Centro de mando de NovaFit en inglés", altHe: "Centro de mando de NovaFit en hebreo con diseño de derecha a izquierda"
    },
    features: {
      analyticsKicker: "CUATRO ESTUDIOS ANALÍTICOS", analyticsTitle: "De un día a un patrón", analyticsBody: "Command Center, Trend Lab, Consistency Map y Training Atlas convierten observaciones guardadas en vistas transparentes y exportables.", profilesKicker: "PERFILES AISLADOS", profilesTitle: "Límites claros por diseño", profilesBody: "Cada perfil mantiene sus propios registros y preferencias en SQLite, con cambio explícito y cobertura completa de respaldo.", motionKicker: "MOVIMIENTO CON PROPÓSITO", motionTitle: "Vivo, nunca molesto", motionBody: "Las animaciones eficientes se pausan al ocultarse y respetan la preferencia de movimiento reducido del dispositivo."
    },
    demo: {
      consistency: "CONSISTENCIA DE RUTINA", days: "DÍAS REGISTRADOS", coverage: "COBERTURA", languages: "IDIOMAS", eyebrow: "PRUEBA LA HISTORIA", title: "Explora una simulación pública y segura", body: "Cambia la ventana temporal para ver cómo responde la narrativa. Estos valores fijos vienen incluidos en el sitio y nunca se guardan.", sampleTitle: "MUESTRA PÚBLICA DE RUTINA", sampleSubtitle: "Observaciones ilustrativas · no es consejo médico", routineScore: "PUNTUACIÓN DE RUTINA", trackedDays: "DÍAS REGISTRADOS", goalDays: "DÍAS CON AMBOS OBJETIVOS", signal: "SEÑAL RECIENTE", publicEntries: "entradas públicas de muestra", exampleGoal: "días objetivo ilustrativos", comparedWindow: "frente a la ventana anterior", movementSignal: "Señal de movimiento", publicUnits: "unidades relativas de muestra", earlier: "Anterior", recent: "Reciente", summaryKicker: "RESUMEN EXPLICABLE", noUpload: "Nada de esta demo se sube ni se almacena.", noisier: "VARIABLE", steadier: "MÁS ESTABLE", established: "CONSOLIDADO", summaryTitle7: "Una ventana corta puede cambiar rápido.", summaryCopy7: "La muestra de siete días sirve para observar, pero es demasiado breve para conclusiones fuertes. NovaFit mantiene un lenguaje prudente.", summaryTitle30: "La rutina se está volviendo más consistente.", summaryCopy30: "La muestra reciente tiene menos huecos que la ventana anterior. NovaFit sugeriría una acción realista, no un diagnóstico.", summaryTitle90: "Una vista más larga revela el ritmo.", summaryCopy90: "La muestra de noventa días permite ver mejor los días recurrentes y los intervalos de recuperación, con una interpretación transparente.", announcement: "Muestra pública de {range} días seleccionada. Puntuación de rutina: {score} de 100."
    },
    themes: { eyebrow: "UN SISTEMA QUE SE SIENTE TUYO", title: "Doce mundos visuales. Un lenguaje legible.", body: "Cada gráfico, icono, estado de enfoque y color se adapta como un solo sistema. Elige un tema para ver una exportación analítica real.", realExport: "EXPORTACIÓN REAL DE DEMO PÚBLICA", previewAlt: "Tema analítico {name} de NovaFit" },
    privacy: {
      eyebrow: "PRIVADO POR DISEÑO", title: "Tus registros no necesitan público.", body: "La app de escritorio guarda los perfiles en bases SQLite locales. Esta presentación es un sitio estático separado: no tiene cuenta, formulario de salud, rastreador analítico ni acceso a tu base de NovaFit.", readSecurity: "Leer el modelo de seguridad", core: "TUS REGISTROS LOCALES", profileBoundary: "Límite del perfil", backupBoundary: "Límite de copia verificada", publicBoundary: "La presentación estática queda fuera", localTitle: "Local por defecto", localBody: "Tus registros diarios permanecen en el dispositivo Windows salvo que decidas exportarlos o respaldarlos.", siteTitle: "Una presentación, no un portal", siteBody: "El sitio Pages solo usa ejemplos públicos fijos y una preferencia de idioma local del dispositivo.", backupTitle: "Copias que puedes verificar", backupBody: "Los archivos ZIP completos cubren cada perfil e incluyen evidencia de integridad y verificación SHA-256."
    },
    architecture: {
      eyebrow: "ARQUITECTURA CLARA", title: "Producto de escritorio e historia pública: conectados por versiones, no por datos privados.", body: "La aplicación controla los registros y exportaciones. GitHub Actions prueba el código público, publica una versión y actualiza esta presentación estática con datos verificados del proyecto.", desktop: "Escritorio Windows", desktopBody: "Interfaz Tkinter y lógica Python local", storage: "Almacenamiento de perfiles", storageBody: "Registros y preferencias SQLite aislados", backup: "Exportación verificada", backupBody: "ZIP, CSV, JSON, PNG y HTML sin conexión", publicLane: "VÍA DE AUTOMATIZACIÓN PÚBLICA", quality: "Matriz de calidad", release: "Versión de GitHub", noRecords: "Ningún registro personal entra en esta vía."
    },
    backup: { eyebrow: "PORTÁTIL CON INTENCIÓN", title: "Un archivo. Todos los perfiles. Evidencia incluida.", body: "NovaFit comprueba la integridad de la base, reúne todos los perfiles locales y registra sumas criptográficas para que restaurar sea comprensible, no misterioso.", inspect: "Inspeccionar", inspectBody: "Validar cada base SQLite", package: "Empaquetar", packageBody: "Reunir perfiles y configuración", verify: "Verificar", verifyBody: "Escribir evidencia de integridad SHA-256" },
    release: { eyebrow: "NOVA / FIT 4.2", title: "¿Listo para hacer visible tu rutina?", body: "Descarga la última versión auditada para Windows o explora el proyecto completo de código abierto. NovaFit es una herramienta de registro personal, no consejo médico.", download: "Descargar para Windows", source: "Ver código en GitHub", note: "Código abierto · Local-first · Inglés, español y hebreo" },
    footer: { tagline: "SEÑALES PERSONALES, BIEN RESGUARDADAS", disclaimer: "Solo registro personal. Sin afirmaciones médicas.", releases: "Versiones", top: "Volver arriba ↑" },
    errors: { image: "La vista previa no está disponible. La descripción del producto sigue accesible." },
    toast: { installed: "Presentación de NovaFit instalada para acceso sin conexión.", installReady: "Ya puedes instalar la presentación de NovaFit.", update: "Habrá una versión sin conexión actualizada la próxima vez que abras el sitio." }
  },
  he: {
    meta: {
      title: "NovaFit 4.2 · תובנות רווחה מקומיות",
      description: "NovaFit הוא סטודיו מקומי ל-Windows עם פרופילים פרטיים, ניתוחים רב-לשוניים, ממשק עברי מלא וגיבויים מאומתים."
    },
    a11y: {
      skip: "דילוג לתוכן הראשי", primaryNav: "ניווט ראשי", home: "דף הבית של NovaFit", openMenu: "פתיחת תפריט הניווט", closeMenu: "סגירת תפריט הניווט", language: "שפה", highlights: "עיקרי המוצר", heroDemo: "הדמיה ציבורית של ממשק NovaFit", previewLanguage: "תצוגה מקדימה של שפת הממשק", timeWindow: "טווח הזמן של הדוגמה", demoChart: "תרשים המחשה של מגמת תנועה", themeGallery: "גלריית ערכות הנושא של NovaFit", privacyDiagram: "תרשים גבולות פרטיות", architectureDiagram: "תרשים הארכיטקטורה של NovaFit"
    },
    nav: { experience: "החוויה", demo: "הדגמה ציבורית", themes: "ערכות נושא", privacy: "פרטיות", architecture: "ארכיטקטורה", install: "התקנת האתר" },
    hero: {
      eyebrow: "תובנות הרווחה של NOVA · 4.2", title: "האותות שלך. המערכת שלך. המכשיר שלך.", lede: "הפכו תצפיות יומיות לשגרה מובנת בעזרת ניתוחים רב-לשוניים, תנועה מכוונת ופרופילים פרטיים שנשארים מקומיים.", download: "הורדת הגרסה האחרונה", explore: "להדגמה הציבורית", trustLocal: "פרופילי SQLite מקומיים", trustLanguages: "EN · ES · HE + RTL", trustBackup: "גיבויי ZIP מאומתים", publicSample: "דוגמה ציבורית", disclaimer: "ערכי המחשה ציבוריים בלבד. האתר אינו טוען רשומות אישיות."
    },
    facts: { title: "נתוני פרויקט מאומתים", version: "גרסה נוכחית", tests: "בדיקות אוטומטיות", themes: "ערכות נושא", assets: "נכסים ציבוריים", localFirst: "מקומי תחילה", loading: "בודק את נתוני הפרויקט המקומיים…", verified: "אומת ממניפסט הפרויקט שפורסם", fallback: "נתוני גיבוי לא מקוונים · ללא מעקב מרחוק" },
    experience: {
      eyebrow: "חוויית שולחן העבודה", title: "מרכז בקרה אחד. שלוש שפות. הקצב שלך.", body: "NovaFit מציג דפוסים באופן ברור בלי להפוך תצפיות לאבחנות. במעבר מאנגלית לעברית, סביבת העבודה כולה עוברת באמת למבנה מימין לשמאל.", realCapture: "צילום אמיתי מהיישום", captionEn: "מרכז הבקרה באנגלית עם בקרות פרופיל, אותות יעדים, מגמת שתייה, קצב שבועי וסיכום ברור.", captionHe: "מרכז הבקרה בעברית עם ניווט, בקרות, סיכומים, טבלאות וניתוחים מלאים מימין לשמאל.", altEn: "מרכז הבקרה של NovaFit באנגלית", altHe: "מרכז הבקרה של NovaFit בעברית ובמבנה מימין לשמאל"
    },
    features: {
      analyticsKicker: "ארבע סביבות ניתוח", analyticsTitle: "מיום אחד לדפוס", analyticsBody: "מרכז הבקרה, מעבדת המגמות, מפת העקביות ואטלס האימונים הופכים תצפיות שמורות לתצוגות שקופות וניתנות לייצוא.", profilesKicker: "פרופילים מבודדים", profilesTitle: "גבולות ברורים כחלק מהעיצוב", profilesBody: "כל פרופיל שומר רשומות והעדפות משלו ב-SQLite, עם מעבר מפורש וכיסוי גיבוי מלא.", motionKicker: "תנועה עם מטרה", motionTitle: "חי, אך לא מסיח", motionBody: "הנפשות יעילות נעצרות כשהעמוד מוסתר ומכבדות את העדפת המכשיר להפחתת תנועה."
    },
    demo: {
      consistency: "עקביות השגרה", days: "ימים שנרשמו", coverage: "כיסוי", languages: "שפות", eyebrow: "נסו את הסיפור", title: "חקרו הדמיה ציבורית ובטוחה", body: "שנו את טווח הזמן כדי לראות כיצד הסיפור מגיב. הערכים הקבועים כלולים באתר ואינם נשמרים לעולם.", sampleTitle: "דוגמת שגרה ציבורית", sampleSubtitle: "תצפיות להמחשה · לא ייעוץ רפואי", routineScore: "ציון שגרה", trackedDays: "ימים שנרשמו", goalDays: "ימים עם שני יעדים", signal: "אות אחרון", publicEntries: "רשומות דוגמה ציבוריות", exampleGoal: "ימי יעד להמחשה", comparedWindow: "לעומת הטווח הקודם", movementSignal: "אות תנועה", publicUnits: "יחידות דוגמה יחסיות", earlier: "מוקדם יותר", recent: "לאחרונה", summaryKicker: "סיכום מוסבר", noUpload: "דבר מההדגמה אינו מועלה או נשמר.", noisier: "משתנה", steadier: "יציב יותר", established: "מבוסס", summaryTitle7: "טווח קצר עשוי להשתנות במהירות.", summaryCopy7: "דוגמה של שבעה ימים עוזרת להבחין, אך קצרה מדי למסקנות חזקות. NovaFit שומר על שפה זהירה.", summaryTitle30: "השגרה נעשית עקבית יותר.", summaryCopy30: "בדוגמה האחרונה יש פחות פערים לעומת הטווח הקודם. NovaFit היה מציע פעולה מציאותית אחת — לא אבחנה.", summaryTitle90: "מבט ארוך יותר חושף את הקצב.", summaryCopy90: "דוגמה של תשעים יום מקלה לזהות ימים חוזרים ופערי התאוששות, תוך שמירה על פרשנות שקופה.", announcement: "נבחרה דוגמה ציבורית של {range} ימים. ציון השגרה הוא {score} מתוך 100."
    },
    themes: { eyebrow: "מערכת שמרגישה שלך", title: "שנים-עשר עולמות חזותיים. שפה ברורה אחת.", body: "כל תרשים, סמל, מצב מיקוד וצבע סטטוס מסתגלים כמערכת אחת. בחרו ערכת נושא כדי לראות ייצוא אמיתי של הניתוחים.", realExport: "ייצוא אמיתי של דוגמה ציבורית", previewAlt: "ערכת הניתוחים {name} של NovaFit" },
    privacy: {
      eyebrow: "פרטי כחלק מהעיצוב", title: "הרשומות שלך אינן זקוקות לקהל.", body: "יישום שולחן העבודה שומר פרופילים במסדי SQLite מקומיים. אתר התצוגה הזה נפרד וסטטי: אין בו חשבון, טופס לרשומות בריאות, מעקב אנליטי או דרך גישה למסד NovaFit שלך.", readSecurity: "למודל האבטחה", core: "הרשומות המקומיות שלך", profileBoundary: "גבול הפרופיל", backupBoundary: "גבול הגיבוי המאומת", publicBoundary: "אתר התצוגה נשאר בחוץ", localTitle: "מקומי כברירת מחדל", localBody: "הרשומות היומיות נשארות במכשיר Windows, אלא אם בחרת לייצא או לגבות אותן.", siteTitle: "אתר תצוגה, לא פורטל", siteBody: "אתר Pages משתמש רק בדוגמאות ציבוריות קבועות ובהעדפת שפה מקומית במכשיר.", backupTitle: "גיבויים שאפשר לאמת", backupBody: "ארכיוני ZIP מלאים מכסים כל פרופיל וכוללים ראיות תקינות ואימות SHA-256."
    },
    architecture: {
      eyebrow: "ארכיטקטורה ברורה", title: "מוצר שולחני וסיפור ציבורי — מחוברים דרך גרסאות, לא דרך מידע פרטי.", body: "היישום מנהל את הרשומות והייצוא. GitHub Actions בודק את הקוד הציבורי, מפרסם גרסה ומרענן את האתר הסטטי באמצעות נתוני פרויקט מאומתים.", desktop: "שולחן עבודה Windows", desktopBody: "ממשק Tkinter ולוגיקת Python מקומית", storage: "אחסון פרופילים", storageBody: "רשומות והעדפות SQLite מבודדות", backup: "ייצוא מאומת", backupBody: "ZIP, CSV, JSON, PNG ו-HTML לא מקוון", publicLane: "מסלול האוטומציה הציבורי", quality: "מטריצת איכות", release: "גרסת GitHub", noRecords: "אף רשומה אישית אינה עוברת למסלול הזה."
    },
    backup: { eyebrow: "ניידות מכוונת", title: "ארכיון אחד. כל הפרופילים. הראיות בפנים.", body: "NovaFit בודק את תקינות מסדי הנתונים, אורז את כל הפרופילים המקומיים ומתעד סכומי ביקורת קריפטוגרפיים כדי שהשחזור יהיה מובן, לא מסתורי.", inspect: "בדיקה", inspectBody: "אימות כל מסד SQLite", package: "אריזה", packageBody: "איסוף פרופילים והגדרות", verify: "אימות", verifyBody: "כתיבת ראיות תקינות SHA-256" },
    release: { eyebrow: "NOVA / FIT 4.2", title: "רוצה לראות את השגרה שלך בבירור?", body: "הורידו את גרסת Windows האחרונה שעברה ביקורת, או עיינו בפרויקט הקוד הפתוח. NovaFit הוא כלי למעקב אישי ואינו ייעוץ רפואי.", download: "הורדה ל-Windows", source: "הקוד ב-GitHub", note: "קוד פתוח · מקומי תחילה · אנגלית, ספרדית ועברית" },
    footer: { tagline: "האותות האישיים, מוחזקים בבירור", disclaimer: "מעקב אישי בלבד. ללא טענות רפואיות.", releases: "גרסאות", top: "חזרה למעלה ↑" },
    errors: { image: "התצוגה המקדימה אינה זמינה. תיאור המוצר עדיין נגיש." },
    toast: { installed: "אתר NovaFit הותקן לשימוש לא מקוון.", installReady: "כעת אפשר להתקין את אתר NovaFit.", update: "גרסה לא מקוונת מעודכנת תהיה מוכנה בפעם הבאה שהאתר ייפתח." }
  }
};

const FALLBACK_FACTS = Object.freeze({ version: "4.2.0", tests: 124, themes: 12, assets: 58 });

const SAMPLE_WINDOWS = Object.freeze({
  7: {
    score: 43, days: 6, goals: 1, trend: "−4.2%", signalKey: "demo.noisier", titleKey: "demo.summaryTitle7", copyKey: "demo.summaryCopy7",
    values: [54, 71, 43, 65, 38, 76, 62]
  },
  30: {
    score: 57, days: 24, goals: 3, trend: "+9.1%", signalKey: "demo.steadier", titleKey: "demo.summaryTitle30", copyKey: "demo.summaryCopy30",
    values: [31, 46, 38, 52, 49, 58, 42, 61, 55, 66, 63, 58, 70, 48, 65, 74, 69, 78, 71, 82, 77, 84, 80, 88]
  },
  90: {
    score: 65, days: 84, goals: 6, trend: "+14.8%", signalKey: "demo.established", titleKey: "demo.summaryTitle90", copyKey: "demo.summaryCopy90",
    values: [42, 47, 50, 45, 54, 58, 52, 60, 64, 57, 62, 68, 65, 71, 69, 74, 70, 77, 73, 79, 76, 81, 78, 84, 80, 86, 83, 88]
  }
});

const THEMES = Object.freeze([
  { slug: "aurora", name: "Aurora Borealis", colors: ["#05252a", "#31d5c3", "#b56bf3"], rgb: "53, 212, 197" },
  { slug: "midnight", name: "Midnight Neon", colors: ["#020c10", "#31d5c3", "#9d67e9"], rgb: "53, 212, 197" },
  { slug: "ocean", name: "Ocean Depth", colors: ["#031324", "#2ab3e8", "#4a7dff"], rgb: "42, 179, 232" },
  { slug: "sapphire", name: "Royal Sapphire", colors: ["#08133f", "#4d8bff", "#bd66f2"], rgb: "77, 139, 255" },
  { slug: "forest", name: "Forest Focus", colors: ["#03180e", "#43db8b", "#42c7b8"], rgb: "67, 219, 139" },
  { slug: "lime", name: "Cyber Lime", colors: ["#07170a", "#8fdd24", "#3ed8a3"], rgb: "143, 221, 36" },
  { slug: "rose", name: "Rose Quartz", colors: ["#24101d", "#ef6eb3", "#bf70e9"], rgb: "239, 110, 179" },
  { slug: "arcade", name: "Sunset Arcade", colors: ["#251026", "#ff7049", "#cd5ee6"], rgb: "255, 112, 73" },
  { slug: "desert", name: "Negev Sunrise", colors: ["#25120a", "#ef8a32", "#a2d62e"], rgb: "239, 138, 50" },
  { slug: "solar", name: "Solar Paper", colors: ["#fff3d8", "#ed7d18", "#168f51"], rgb: "237, 125, 24" },
  { slug: "cloud", name: "Cloud Day", colors: ["#e7f2f6", "#25a9d8", "#a14ee4"], rgb: "37, 169, 216" },
  { slug: "contrast", name: "High Contrast", colors: ["#000000", "#ffe000", "#4ce3ff"], rgb: "255, 224, 0" }
]);

const state = { language: "en", range: 30, preview: "en", theme: "aurora", deferredInstall: null };

function getCopy(key, language = state.language) {
  return key.split(".").reduce((value, part) => value && value[part], COPY[language]) ?? key;
}

function formatCopy(key, replacements = {}) {
  return Object.entries(replacements).reduce((value, [name, replacement]) => value.replaceAll(`{${name}}`, String(replacement)), getCopy(key));
}

function safePreference() {
  try {
    const stored = localStorage.getItem("novafit-site-language");
    return Object.hasOwn(COPY, stored) ? stored : null;
  } catch {
    return null;
  }
}

function rememberLanguage(language) {
  try {
    localStorage.setItem("novafit-site-language", language);
  } catch {
    // The site remains fully usable when device-local storage is unavailable.
  }
}

function applyLanguage(language, { persist = true } = {}) {
  if (!Object.hasOwn(COPY, language)) return;
  state.language = language;
  const root = document.documentElement;
  root.lang = language;
  root.dir = language === "he" ? "rtl" : "ltr";
  document.title = getCopy("meta.title");
  document.querySelector('meta[name="description"]')?.setAttribute("content", getCopy("meta.description"));

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const value = getCopy(node.dataset.i18n);
    if (value !== node.dataset.i18n) node.textContent = value;
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((node) => {
    const value = getCopy(node.dataset.i18nAria);
    if (value !== node.dataset.i18nAria) node.setAttribute("aria-label", value);
  });
  document.querySelectorAll("[data-lang]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.lang === language)));

  const navToggle = document.querySelector(".nav-toggle");
  if (navToggle) navToggle.setAttribute("aria-label", getCopy(navToggle.getAttribute("aria-expanded") === "true" ? "a11y.closeMenu" : "a11y.openMenu"));
  updatePreview(state.preview);
  updateDemo(state.range, false);
  updateTheme(state.theme, false);
  if (persist) rememberLanguage(language);
}

function renderBars(container, values, delayStep = 16) {
  if (!container) return;
  const fragment = document.createDocumentFragment();
  values.forEach((value, index) => {
    const bar = document.createElement("i");
    bar.style.height = `${Math.max(8, Math.min(96, value))}%`;
    bar.style.animationDelay = `${index * delayStep}ms`;
    bar.setAttribute("aria-hidden", "true");
    if (value < 50) bar.dataset.tone = "low";
    if (value > 77) bar.dataset.tone = "high";
    fragment.append(bar);
  });
  container.replaceChildren(fragment);
}

function updateDemo(range, announce = true) {
  const sample = SAMPLE_WINDOWS[range];
  if (!sample) return;
  state.range = Number(range);
  document.querySelectorAll("[data-range]").forEach((button) => button.setAttribute("aria-pressed", String(Number(button.dataset.range) === state.range)));
  document.querySelector("#demo-score")?.replaceChildren(document.createTextNode(String(sample.score)), Object.assign(document.createElement("span"), { textContent: "/100" }));
  const fields = { "#demo-days": sample.days, "#demo-goals": sample.goals, "#demo-trend": sample.trend };
  Object.entries(fields).forEach(([selector, value]) => { const node = document.querySelector(selector); if (node) node.textContent = String(value); });
  const signal = document.querySelector("#demo-signal");
  if (signal) { signal.dataset.i18n = sample.signalKey; signal.textContent = getCopy(sample.signalKey); }
  const title = document.querySelector("#summary-title");
  const copy = document.querySelector("#summary-copy");
  if (title) { title.dataset.i18n = sample.titleKey; title.textContent = getCopy(sample.titleKey); }
  if (copy) { copy.dataset.i18n = sample.copyKey; copy.textContent = getCopy(sample.copyKey); }
  renderBars(document.querySelector("#demo-bars"), sample.values, Math.min(22, 300 / sample.values.length));
  if (announce) {
    const announcement = document.querySelector("#demo-announcement");
    if (announcement) announcement.textContent = formatCopy("demo.announcement", { range: state.range, score: sample.score });
  }
}

function resetImageFallback(image) {
  if (!image) return;
  image.hidden = false;
  const fallback = image.parentElement?.querySelector(".image-fallback");
  if (fallback) fallback.hidden = true;
}

function updatePreview(preview) {
  if (!new Set(["en", "he"]).has(preview)) return;
  state.preview = preview;
  const image = document.querySelector("#product-preview");
  if (image) {
    const src = preview === "he" ? image.dataset.heSrc : image.dataset.enSrc;
    if (image.getAttribute("src") !== src) {
      resetImageFallback(image);
      image.setAttribute("src", src);
    }
    image.alt = getCopy(preview === "he" ? "experience.altHe" : "experience.altEn");
  }
  const caption = document.querySelector("#preview-caption");
  if (caption) { caption.dataset.i18n = preview === "he" ? "experience.captionHe" : "experience.captionEn"; caption.textContent = getCopy(caption.dataset.i18n); }
  document.querySelectorAll("[data-preview]").forEach((button) => {
    const selected = button.dataset.preview === preview;
    button.setAttribute("aria-selected", String(selected));
    button.tabIndex = selected ? 0 : -1;
  });
  const panel = document.querySelector("#preview-panel");
  if (panel) panel.setAttribute("aria-labelledby", preview === "he" ? "preview-he-tab" : "preview-en-tab");
}

function createThemeSelector() {
  const selector = document.querySelector("#theme-selector");
  if (!selector) return;
  const fragment = document.createDocumentFragment();
  THEMES.forEach((theme) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "theme-option";
    button.dataset.theme = theme.slug;
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", String(theme.slug === state.theme));
    button.tabIndex = theme.slug === state.theme ? 0 : -1;
    const swatches = document.createElement("span");
    swatches.className = "theme-swatches";
    swatches.setAttribute("aria-hidden", "true");
    theme.colors.forEach((color) => {
      const swatch = document.createElement("i");
      swatch.style.setProperty("--swatch", color);
      swatches.append(swatch);
    });
    const label = document.createElement("span");
    label.textContent = theme.name;
    button.append(swatches, label);
    button.addEventListener("click", () => updateTheme(theme.slug));
    fragment.append(button);
  });
  selector.replaceChildren(fragment);
}

function updateTheme(slug, focus = true) {
  const theme = THEMES.find((candidate) => candidate.slug === slug);
  if (!theme) return;
  state.theme = theme.slug;
  document.documentElement.style.setProperty("--accent", theme.colors[1]);
  document.documentElement.style.setProperty("--accent-rgb", theme.rgb);
  const image = document.querySelector("#theme-image");
  if (image) {
    resetImageFallback(image);
    image.src = `assets/theme-gallery/command-center-${theme.slug}.png`;
    image.alt = formatCopy("themes.previewAlt", { name: theme.name });
  }
  const name = document.querySelector("#theme-name");
  if (name) name.textContent = theme.name;
  document.querySelectorAll("#theme-selector [data-theme]").forEach((button) => {
    const selected = button.dataset.theme === theme.slug;
    button.setAttribute("aria-selected", String(selected));
    button.tabIndex = selected ? 0 : -1;
    if (selected && focus) button.focus({ preventScroll: true });
  });
}

function bindTabKeyboard(containerSelector, itemSelector, select) {
  const container = document.querySelector(containerSelector);
  if (!container) return;
  container.addEventListener("keydown", (event) => {
    const items = [...container.querySelectorAll(itemSelector)];
    const index = items.indexOf(document.activeElement);
    if (index < 0) return;
    const rtl = document.documentElement.dir === "rtl";
    let next = index;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") next = (index + (rtl && event.key === "ArrowRight" ? -1 : 1) + items.length) % items.length;
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = (index + (rtl && event.key === "ArrowLeft" ? 1 : -1) + items.length) % items.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = items.length - 1;
    else return;
    event.preventDefault();
    select(items[next]);
  });
}

function validFactNumber(value, minimum, maximum) {
  return Number.isInteger(value) && value >= minimum && value <= maximum;
}

function factsFromManifest(data) {
  if (!data || data.schema !== "nova-portfolio-project-v1" || data.slug !== "novafit") throw new Error("Unexpected project manifest");
  const version = typeof data.version === "string" && /^\d+\.\d+\.\d+$/.test(data.version) ? data.version : FALLBACK_FACTS.version;
  const tests = validFactNumber(data.quality?.automated_tests_discovered, 1, 10000) ? data.quality.automated_tests_discovered : FALLBACK_FACTS.tests;
  const themes = validFactNumber(data.theme_count, 1, 100) ? data.theme_count : FALLBACK_FACTS.themes;
  const assets = validFactNumber(data.assets?.count, 1, 10000) ? data.assets.count : FALLBACK_FACTS.assets;
  return { version, tests, themes, assets };
}

function renderFacts(facts, statusKey) {
  const fields = { "#fact-version": facts.version, "#fact-tests": facts.tests, "#fact-themes": facts.themes, "#fact-assets": facts.assets };
  Object.entries(fields).forEach(([selector, value]) => { const node = document.querySelector(selector); if (node) node.textContent = String(value); });
  const status = document.querySelector("#facts-state");
  if (status) { status.dataset.i18n = statusKey; status.textContent = getCopy(statusKey); }
}

async function loadFacts() {
  renderFacts(FALLBACK_FACTS, "facts.loading");
  try {
    const response = await fetch("project.json", { cache: "no-cache", headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`Manifest response ${response.status}`);
    renderFacts(factsFromManifest(await response.json()), "facts.verified");
  } catch {
    renderFacts(FALLBACK_FACTS, "facts.fallback");
  }
}

function showToast(message) {
  const toast = document.querySelector("#site-toast");
  if (!toast) return;
  toast.textContent = message;
  toast.hidden = false;
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => { toast.hidden = true; }, 6000);
}

function setupNavigation() {
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector("#nav-links");
  if (!toggle || !links) return;
  const setOpen = (open) => {
    links.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", getCopy(open ? "a11y.closeMenu" : "a11y.openMenu"));
  };
  toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
  links.addEventListener("click", (event) => { if (event.target.closest("a")) setOpen(false); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") { setOpen(false); toggle.focus(); } });
  document.addEventListener("click", (event) => { if (!event.target.closest(".nav-shell")) setOpen(false); });
}

function setupObservers() {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const reveals = document.querySelectorAll(".reveal");
  if (reducedMotion || !("IntersectionObserver" in window)) reveals.forEach((node) => node.classList.add("is-visible"));
  else {
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => { if (entry.isIntersecting) { entry.target.classList.add("is-visible"); observer.unobserve(entry.target); } });
    }, { rootMargin: "0px 0px -8%", threshold: 0.08 });
    reveals.forEach((node) => revealObserver.observe(node));
  }

  if ("IntersectionObserver" in window) {
    const links = new Map([...document.querySelectorAll(".nav-links a[href^='#']")].map((link) => [link.hash.slice(1), link]));
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || !links.has(entry.target.id)) return;
        links.forEach((link, id) => id === entry.target.id ? link.setAttribute("aria-current", "true") : link.removeAttribute("aria-current"));
      });
    }, { rootMargin: "-35% 0px -55%", threshold: 0 });
    links.forEach((_link, id) => { const section = document.getElementById(id); if (section) sectionObserver.observe(section); });
  }
}

function setupImages() {
  document.querySelectorAll(".image-frame img").forEach((image) => {
    image.addEventListener("error", () => {
      image.hidden = true;
      const fallback = image.parentElement?.querySelector(".image-fallback");
      if (fallback) fallback.hidden = false;
    });
    image.addEventListener("load", () => resetImageFallback(image));
  });
}

function setupInstall() {
  const button = document.querySelector("#install-app");
  if (!button) return;
  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    state.deferredInstall = event;
    button.hidden = false;
    showToast(getCopy("toast.installReady"));
  });
  button.addEventListener("click", async () => {
    if (!state.deferredInstall) return;
    state.deferredInstall.prompt();
    await state.deferredInstall.userChoice;
    state.deferredInstall = null;
    button.hidden = true;
  });
  window.addEventListener("appinstalled", () => showToast(getCopy("toast.installed")));
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator) || location.protocol === "file:") return;
  window.addEventListener("load", async () => {
    try {
      const registration = await navigator.serviceWorker.register("sw.js", { scope: "./" });
      if (registration.waiting) showToast(getCopy("toast.update"));
      registration.addEventListener("updatefound", () => {
        const worker = registration.installing;
        worker?.addEventListener("statechange", () => { if (worker.state === "installed" && navigator.serviceWorker.controller) showToast(getCopy("toast.update")); });
      });
    } catch {
      // Offline installation is an enhancement; the showcase remains usable online.
    }
  });
}

function initialise() {
  createThemeSelector();
  setupNavigation();
  setupImages();
  setupInstall();
  setupObservers();
  registerServiceWorker();

  document.querySelectorAll("[data-lang]").forEach((button) => button.addEventListener("click", () => applyLanguage(button.dataset.lang)));
  document.querySelectorAll("[data-range]").forEach((button) => button.addEventListener("click", () => updateDemo(Number(button.dataset.range))));
  document.querySelectorAll("[data-preview]").forEach((button) => button.addEventListener("click", () => updatePreview(button.dataset.preview)));
  bindTabKeyboard(".stage-tabs", "[data-preview]", (button) => { updatePreview(button.dataset.preview); button.focus(); });
  bindTabKeyboard("#theme-selector", "[data-theme]", (button) => updateTheme(button.dataset.theme));

  renderBars(document.querySelector("#hero-bars"), [42, 61, 53, 72, 66, 82, 58, 75, 69, 87, 79, 92, 73, 84, 88, 76, 94, 83], 34);
  document.querySelector("#year").textContent = String(new Date().getFullYear());
  applyLanguage(safePreference() || (navigator.language?.toLowerCase().startsWith("he") ? "he" : navigator.language?.toLowerCase().startsWith("es") ? "es" : "en"), { persist: false });
  loadFacts();
}

initialise();
