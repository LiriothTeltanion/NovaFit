<div align="center">

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/novafit-ultimate-gui.png" />
  <img src="./assets/novafit-ultimate-banner-animated.svg" width="100%" alt="Banner animado de NovaFit Ultimate 4.2" />
</picture>

# NovaFit Ultimate 4.2 💙

### Inteligencia de bienestar local · perfiles múltiples · EN/ES/HE · 12 temas · recomendaciones explicables · analítica avanzada

[![Calidad de NovaFit](https://github.com/LiriothTeltanion/NovaFit/actions/workflows/quality.yml/badge.svg?branch=main)](https://github.com/LiriothTeltanion/NovaFit/actions/workflows/quality.yml)
[![Showcase en vivo](https://img.shields.io/badge/Showcase-GitHub%20Pages-2DD4BF?style=for-the-badge&logo=github)](https://liriothteltanion.github.io/NovaFit/)

[English](README.md) · [Español](README_ES.md) · [עברית](README_HE.md)

</div>

---

## 🌌 Visión

NovaFit es la aplicación local de escritorio y terminal de Kevin “Lirioth” Cusnir para registrar pasos, agua, calorías opcionales, estado de ánimo y notas privadas. La edición **4.2.0** la convierte en un **Wellness Intelligence Studio** más pulido, honesto y mantenible:

- perfiles de usuario aislados;
- textos completos en inglés, español y hebreo;
- composición RTL real en paneles, formularios, tarjetas y tablas;
- doce temas visuales;
- cuatro espacios analíticos;
- Motivation Center;
- Sport & Data Coach;
- iconos antialias con estados activo y atenuado;
- animaciones persistentes que se pausan al ocultarse y respetan movimiento reducido;
- gráficos responsivos sin cruces en ventanas compactas o amplias;
- SQLite con migración del modelo histórico;
- JSON, CSV, PNG, informes HTML offline y backup ZIP completo verificado;
- CLI ampliada;
- apertura, reparación y validación completa con un clic en Windows;
- datos de proyecto y assets generados para sincronizar README y perfil GitHub;
- releases automáticos desde tags con archivos auditados y checksums SHA-256;
- showcase público instalable en GitHub Pages con datos de proyecto verificados;
- auditoría que preserva la base del usuario;
- empaquetado de release que excluye datos privados.

> NovaFit describe patrones y ayuda a organizar una rutina. No diagnostica, prescribe ni reemplaza consejo médico o deportivo profesional.

---

## 🌐 Showcase en vivo y límites del PWA

Abre **[liriothteltanion.github.io/NovaFit](https://liriothteltanion.github.io/NovaFit/)** para ver la experiencia pública e instalable.

El PWA es un showcase estático: presenta el producto, sus imágenes, métricas
verificadas y enlaces de descarga. No es la aplicación Tkinter en el navegador y
no puede leer perfiles, SQLite, OneDrive, exports ni backups locales.

La experiencia completa se obtiene mediante el ejecutable de
[GitHub Releases](https://github.com/LiriothTeltanion/NovaFit/releases/latest)
o desde código fuente con `run_novafit.bat`. Pages se despliega únicamente tras
un Quality verde de `main`; CI audita el artifact exacto para evitar datos
privados, rutas locales y enlaces rotos. Consulta
[PAGES_AND_RELEASES.md](docs/PAGES_AND_RELEASES.md).

---

## ✅ Corrección del error de `VERIFY_ALL.bat`

El log reportado mostraba que las pruebas, el smoke workflow y el perfil habían terminado correctamente. El fallo final ocurría porque el auditor veía `NovaFit/data/novafit.db`, creado por el uso real de la aplicación, y lo trataba como si fuera un archivo incluido en un ZIP público.

Ahora existen dos modos:

| Modo | Resultado |
|---|---|
| **Workspace** | Conserva `novafit.db`, lo informa y continúa la auditoría |
| **Distribución estricta** | Trabaja sobre una copia limpia y rechaza bases, logs, secretos o configuración local |

<img src="./assets/distribution-safety-animated.svg" width="100%" alt="Diagrama animado de verificación segura" />

Este comportamiento queda protegido por pruebas automatizadas.

---

## 🖥️ GUI definitiva

<img src="./assets/novafit-ultimate-gui.png" width="100%" alt="Centro de mando real de NovaFit Ultimate" />

La GUI incluye:

- cabecera animada grande;
- navegación lateral persistente;
- selector de usuario;
- selector de idioma;
- selector de doce temas;
- iconos temáticos;
- escala de interfaz configurable;
- reduced motion;
- Command Center;
- Motivation Center;
- Coach deportivo y de datos;
- formulario validado;
- biblioteca de registros;
- estudio de perfiles;
- herramientas de backup, clima, informes y preferencias.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/novafit-ultimate-gui.png" />
  <img src="./assets/novafit-ultimate-tour.gif" width="100%" alt="Tour animado de NovaFit Ultimate" />
</picture>

---

## 👥 Perfiles y aislamiento

<img src="./assets/multi-profile-i18n-animated.svg" width="100%" alt="Arquitectura animada de perfiles e idiomas" />

Cada perfil mantiene de forma independiente:

- nombre y avatar;
- idioma;
- tema;
- objetivos;
- nivel de actividad;
- foco deportivo;
- registros por fecha.

La clave de unicidad es:

```text
UNIQUE(user_id, date)
```

<img src="./assets/multi-profile-language-center.png" width="100%" alt="Administrador real de perfiles de NovaFit" />

---

## 🌍 Tres idiomas y hebreo RTL

| Idioma | Código | Dirección |
|---|---:|---:|
| English | `en` | LTR |
| Español | `es` | LTR |
| עברית | `he` | RTL |

<img src="./assets/spanish-sport-data-coach.png" width="100%" alt="Coach deportivo y de datos en español" />

<img src="./assets/hebrew-rtl-command-center.png" width="100%" alt="Centro de mando en hebreo RTL" />

Al activar un perfil hebreo, la navegación se mueve a la derecha y los controles principales se reflejan.

---

## 🎨 Doce temas

Midnight Neon · Aurora Borealis · Negev Sunrise · Ocean Depth · Forest Focus · Rose Quartz · Cloud Day · Solar Paper · High Contrast · Royal Sapphire · Cyber Lime · Sunset Arcade.

<img src="./assets/theme-spectrum.png" width="100%" alt="Los doce temas de NovaFit" />

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/theme-spectrum.png" />
  <img src="./assets/theme-spectrum-tour.gif" width="100%" alt="Tour animado de los doce temas" />
</picture>

---

## 📊 Cuatro espacios analíticos

### Wellness Command Center

<img src="./assets/analytics-command-center.png" width="100%" alt="Wellness Command Center" />

### Trend Lab

<img src="./assets/analytics-trend-lab.png" width="100%" alt="Trend Lab" />

### Consistency Map

<img src="./assets/analytics-consistency-map.png" width="100%" alt="Consistency Map" />

### Training Atlas

<img src="./assets/training-atlas-animated.svg" width="100%" alt="Training Atlas animado" />

<img src="./assets/analytics-training-atlas.png" width="100%" alt="Training Atlas exportado" />

Los rangos disponibles van de 7 a 365 días.

---

## 🧠 Coach deportivo y de datos

<img src="./assets/sport-data-engine-animated.svg" width="100%" alt="Motor de recomendaciones explicable" />

<img src="./assets/sport-data-coach-real.png" width="100%" alt="Interfaz real del Coach deportivo y de datos" />

Las sugerencias pueden orientar:

- progresión gradual de movimiento;
- constancia de hidratación;
- protección de recuperación;
- calidad de seguimiento;
- ritmo semanal;
- caminata, movilidad, fuerza, carrera, ciclismo o foco mixto.

Cada recomendación muestra acción, razón, prioridad y confianza. El sistema evita recomendaciones médicas, planes extremos, zonas cardíacas, rehabilitación o dietas.

---

## ✨ Motivation Center

<img src="./assets/motivation-center-ultimate.png" width="100%" alt="Motivation Center de NovaFit Ultimate" />

Incluye motivación diaria, rachas, logros, propósito privado, próximo paso, objetivo semanal y pausa visual. Su score mide regularidad de registro y cumplimiento de objetivos configurados; no representa salud clínica.

---

## ⌨️ CLI ampliada

```bash
python -m novafit.cli --help
python -m novafit.cli --menu
python -m novafit.cli --profiles
python -m novafit.cli --user "Kevin / Lirioth" --dashboard
python -m novafit.cli --user "Lucía" --recommendations --language es
```

Crear perfil:

```bash
python -m novafit.cli \
  --create-user "Lucía" \
  --language es \
  --theme arcade \
  --avatar sun \
  --activity-level beginner \
  --sport-focus walking
```

Exportar Training Atlas:

```bash
python -m novafit.cli \
  --chart data/training-atlas.png \
  --chart-view training_atlas \
  --chart-days 90 \
  --chart-theme sapphire
```

---

## 🪟 Windows con un clic

1. Conserva el repositorio en su ubicación actual de OneDrive o extráelo donde prefieras.

2. Haz doble clic en:

```text
run_novafit.bat
```

El lanzador crea o repara `.venv` cuando hace falta y abre NovaFit. Para comprobar absolutamente todo antes de publicar, haz doble clic en:

```text
VERIFY_ALL.bat
```

La verificación instala dependencias binarias, valida Tkinter/Matplotlib/Pillow/tzdata, descubre todas las pruebas actuales, revisa documentación y assets, ejecuta Ruff/Pyright y completa un smoke workflow aislado.

---

## 🏗️ Arquitectura

<img src="./assets/technology-constellation-animated.svg" width="100%" alt="Constelación tecnológica de NovaFit" />

```text
Tkinter GUI ─┐
             ├─ Application services ─ Profiles / Analytics / Coach / Motivation
argparse CLI ┘                         │
                                      ├─ SQLite v4
                                      ├─ Matplotlib PNG
                                      ├─ JSON / CSV
                                      └─ HTML offline
```

Módulos destacados:

- `gui.py` — shell de escritorio;
- `cli.py` — automatización y menú;
- `database.py` — perfiles, migraciones y CRUD;
- `i18n.py` — EN/ES/HE y RTL;
- `themes.py` — 12 temas;
- `recommendations.py` — sugerencias conservadoras;
- `charts.py` — cuatro laboratorios visuales;
- `icon_factory.py` — iconos Pillow;
- `reporting.py` — informes offline.

---

## 🧪 Calidad comprobada

El badge superior refleja el estado del commit remoto actual en `main`. La versión, cantidad de pruebas descubiertas, temas y tamaño de assets se generan automáticamente en [PROJECT_FACTS.md](docs/PROJECT_FACTS.md), evitando cifras antiguas escritas a mano.

También se verificó:

- compilación Python;
- smoke SQLite/CLI/JSON/PNG/HTML;
- lanzamiento real de Tkinter bajo Xvfb;
- generación de screenshots reales;
- assets SVG válidos;
- perfiles aislados;
- hebreo RTL;
- release staging sin bases ni logs.
- artifact exacto de Pages sin rutas privadas ni enlaces locales rotos.

Superar la suite implementada no significa 100% de cobertura de líneas; es un contrato reproducible validado en Windows y Ubuntu.

---

## 🔒 Privacidad

- Los datos permanecen en SQLite local.
- Los perfiles no mezclan fechas ni métricas.
- Los informes escapan notas HTML.
- Las consultas SQL están parametrizadas.
- El clima no recibe datos personales de bienestar.
- El release no incluye `.db`, logs ni config local.
- Las recomendaciones son generales y explicables.

---

## 📚 Documentación

- [GUI Ultimate](docs/ULTIMATE_GUI.md)
- [Perfiles](docs/MULTI_PROFILE.md)
- [Idiomas y RTL](docs/I18N_RTL.md)
- [Recomendaciones](docs/SPORT_DATA_RECOMMENDATIONS.md)
- [Seguridad de distribución](docs/DISTRIBUTION_SAFETY.md)
- [Analítica](docs/ANALYTICS.md)
- [Modelo de datos](docs/DATA_MODEL.md)
- [Testing](docs/TESTING.md)
- [Windows](docs/WINDOWS_GUIDE.md)
- [Seguridad](docs/SECURITY.md)
- [Changelog](docs/CHANGELOG.md)
- [Datos verificados del proyecto](docs/PROJECT_FACTS.md)
- [Pages, PWA y releases](docs/PAGES_AND_RELEASES.md)

---

## 👨‍💻 Autor

**Kevin “Lirioth” Cusnir** · Beersheba, Israel · Asia/Jerusalem  
[GitHub](https://github.com/LiriothTeltanion) · [LinkedIn](https://www.linkedin.com/in/kevin-cusnir-883173b4/)

## 📄 Licencia

MIT. Consulta [LICENSE](LICENSE).

<div align="center">

**Construye con constancia. Lee los datos con honestidad. Protege la recuperación.** 💙

**NovaFit Ultimate 4.2 · Wellness Intelligence Studio · 2026-07-16**

</div>
