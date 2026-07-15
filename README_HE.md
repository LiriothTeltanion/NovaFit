<div align="center" dir="rtl">

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/hebrew-rtl-command-center.png" />
  <img src="./assets/novafit-ultimate-banner-animated.svg" width="100%" alt="NovaFit Ultimate 4.1" />
</picture>

# NovaFit Ultimate 4.1 💙

### מערכת מקומית לתיעוד, ניתוח ומוטיבציה · פרופילים מרובים · אנגלית/ספרדית/עברית · 12 ערכות נושא

[![איכות NovaFit](https://github.com/LiriothTeltanion/NovaFit/actions/workflows/quality.yml/badge.svg?branch=main)](https://github.com/LiriothTeltanion/NovaFit/actions/workflows/quality.yml)

[English](README.md) · [Español](README_ES.md) · [עברית](README_HE.md)

</div>

---

<div dir="rtl">

## 🌌 מהי NovaFit?

NovaFit היא אפליקציית שולחן עבודה ושורת פקודה מקומית. היא שומרת צעדים, מים, קלוריות אופציונליות, מצב רוח והערות פרטיות ב־SQLite במכשיר שלך.

גרסה **4.1.0** כוללת:

- פרופילי משתמשים מבודדים;
- טקסט מלא באנגלית, ספרדית ועברית;
- מבנה RTL אמיתי בפאנלים, טפסים, כרטיסים וטבלאות;
- 12 ערכות נושא;
- ארבע תצוגות ניתוח;
- מרכז מוטיבציה והתאוששות;
- מאמן פעילות ונתונים;
- אייקונים חדים עם מצב פעיל ומצב מעומעם;
- אנימציות יעילות שנעצרות כשהמסך מוסתר ותומכות בהפחתת תנועה;
- תרשימים רספונסיביים ללא חפיפות;
- ייצוא JSON/CSV וגיבוי ZIP מלא עם בדיקת שלמות;
- דוחות HTML ללא שרת;
- CLI מורחב;
- הפעלה, תיקון ואימות מלאים בלחיצה אחת ב־Windows;
- בדיקה ששומרת על מסד הנתונים האישי.

> NovaFit מספקת מידע כללי ותיאורי בלבד. היא אינה ייעוץ רפואי, אבחון, טיפול או תוכנית אימון מקצועית.

---

## ✅ תיקון שגיאת האימות

הבדיקות עברו, אך הבודק הישן נכשל מפני שמצא את `data/novafit.db` — מסד נתונים לגיטימי שנוצר בעת שימוש באפליקציה.

כעת קיימים שני מצבים:

- **Workspace:** שומר את מסד הנתונים וממשיך לבדוק את הקוד.
- **Distribution:** יוצר עותק נקי ללא DB, לוגים או הגדרות אישיות.

<img src="./assets/distribution-safety-animated.svg" width="100%" alt="בדיקת הפצה בטוחה" />

---

## 🖥️ ממשק שולחן העבודה

<img src="./assets/hebrew-rtl-command-center.png" width="100%" alt="מרכז הבקרה של NovaFit בעברית RTL" />

במצב עברית:

- סרגל הניווט מופיע מימין;
- בקרי המשתמש, השפה וערכת הנושא עוברים לצד המתאים;
- הטקסט המרכזי מוצג בעברית;
- כל פרופיל שומר שפה וערכת נושא משלו.

---

## 👥 פרופילים מקומיים

<img src="./assets/multi-profile-i18n-animated.svg" width="100%" alt="פרופילים ושפות" />

לכל פרופיל יש:

- שם ואווטאר;
- שפה;
- ערכת נושא;
- יעדי צעדים, מים וקלוריות;
- רמת פעילות;
- תחום פעילות מועדף;
- רשומות מבודדות לפי `user_id` ותאריך.

<img src="./assets/multi-profile-language-center.png" width="100%" alt="ניהול פרופילים" />

---

## 🎨 שתים־עשרה ערכות נושא

Midnight Neon · Aurora Borealis · Negev Sunrise · Ocean Depth · Forest Focus · Rose Quartz · Cloud Day · Solar Paper · High Contrast · Royal Sapphire · Cyber Lime · Sunset Arcade.

<img src="./assets/theme-spectrum.png" width="100%" alt="12 ערכות הנושא" />

---

## 📊 תצוגות ניתוח

1. Wellness Command Center
2. Trend Lab
3. Consistency Map
4. Training Atlas

<img src="./assets/analytics-training-atlas.png" width="100%" alt="Training Atlas" />

התרשימים מציגים דפוסים מתועדים, ימים חסרים, ממוצעים, רצפים ועמידה ביעדים. הם אינם מציגים אבחון רפואי.

---

## 🧠 מאמן פעילות ונתונים

<img src="./assets/sport-data-engine-animated.svg" width="100%" alt="מנוע המלצות" />

המאמן עשוי להציע:

- התקדמות הדרגתית;
- תיעוד מים עקבי;
- הגנה על התאוששות;
- שיפור איכות הנתונים;
- קצב שבועי בהתאם להעדפת הליכה, ניידות, כוח, ריצה, רכיבה או שילוב.

כל המלצה כוללת פעולה, סיבה, עדיפות ורמת ביטחון.

---

## ⌨️ CLI

```bash
python -m novafit.cli --help
python -m novafit.cli --profiles
python -m novafit.cli --user 3 --dashboard --language he
python -m novafit.cli --user 3 --recommendations --language he
```

יצירת פרופיל:

```bash
python -m novafit.cli \
  --create-user "נועה" \
  --language he \
  --theme sapphire \
  --avatar moon \
  --activity-level balanced \
  --sport-focus mobility
```

---

## 🪟 הפעלה בלחיצה אחת ב־Windows

1. אפשר להשאיר את הפרויקט במיקום הנוכחי ב־OneDrive.
2. לחץ פעמיים על `run_novafit.bat` כדי לתקן את הסביבה בעת הצורך ולפתוח את NovaFit.
3. לפני פרסום, לחץ פעמיים על `VERIFY_ALL.bat` כדי להריץ את כל בדיקות האיכות.

הבודק יוצר `.venv`, מתקין תלויות, בודק `Asia/Jerusalem`, מגלה את כל הבדיקות הנוכחיות, מאמת תיעוד ונכסים, מריץ Ruff/Pyright ומבצע smoke workflow מבודד.

---

## 🧪 תוצאה שנבדקה

התג בראש הדף מציג את מצב ה־commit הנוכחי ב־`main`. הגרסה, מספר הבדיקות שהתגלו, ערכות הנושא וגודל הנכסים נוצרים אוטומטית בקובץ [PROJECT_FACTS.md](docs/PROJECT_FACTS.md), ולכן אין במסמך מספר ישן שנכתב ידנית.

נבדקו גם SQLite, מיגרציה, JSON/CSV, תרשימי PNG, דוח HTML, פרופילים, עברית RTL, המלצות, CLI והתנהגות ההפצה.

---

## 🔒 פרטיות

- הנתונים נשארים במכשיר.
- פרופילים אינם מערבבים רשומות.
- קובצי release אינם כוללים DB או לוגים.
- מזג האוויר מקבל רק קואורדינטות עיר.
- ההמלצות כלליות ומוגבלות במכוון.

---

## 👨‍💻 יוצר

**Kevin “Lirioth” Cusnir** · באר שבע · Asia/Jerusalem  
[GitHub](https://github.com/LiriothTeltanion) · [LinkedIn](https://www.linkedin.com/in/kevin-cusnir-883173b4/)

## 📄 רישיון

MIT — ראו [LICENSE](LICENSE).

**NovaFit Ultimate 4.1 · Wellness Intelligence Studio · 2026-07-16**

</div>
