# Internationalization and Hebrew RTL 🌍

## Supported languages

| Code | Label | Direction |
|---|---|---|
| `en` | English | LTR |
| `es` | Español | LTR |
| `he` | עברית | RTL |

## Translation architecture

`novafit/i18n.py` owns stable language definitions and UI translation keys. `tr()` falls back to English only when a supported language omits a key; a completely missing key raises `KeyError` so programmer mistakes remain visible.

## Profile binding

Language is stored per profile. Activating a profile updates the shell, navigation, forms, recommendation language and layout direction.

## RTL behavior

Hebrew mode:

- places the sidebar on the right;
- places content on the left;
- mirrors top selector placement;
- uses right anchors and right text alignment where practical;
- localizes hero copy;
- retains native theme names because theme names are product identifiers.

## Scope

The shell, forms, preferences and recommendation engine are multilingual. Some Matplotlib labels and historical analytic copy remain English because chart-localization coverage is still being expanded. The README declares this limitation instead of presenting translation as complete.

## Testing

Automated tests cover language aliases, native labels, English fallback and `he → rtl`. Real Xvfb screenshots demonstrate the RTL shell.
