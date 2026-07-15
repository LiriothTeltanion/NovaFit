# Ultimate CLI Reference ⌨️

## Global context flags

```text
--db PATH
--user ID_OR_NAME
--language {en,es,he}
--theme THEME_ID
--log-level LEVEL
--debug
```

## Primary actions

Only one primary action may be selected per command:

```text
--gui
--menu
--add DATE
--list [N]
--dashboard
--motivation
--recommendations
--profiles
--create-user NAME
--delete-user ID
--delete DATE
--seed N
--sample
--export-json PATH
--import-json PATH
--export-csv PATH
--import-csv PATH
--weather CITY
--chart PNG
--report-html HTML
--settings
```

## Record fields

```text
--steps INTEGER
--water FLOAT
--calories INTEGER
--mood TEXT
--note TEXT
```

## Profile fields

```text
--avatar {nova,runner,walker,cyclist,strength,focus,sun,moon}
--activity-level {beginner,balanced,active}
--sport-focus {walking,strength,mobility,running,cycling,mixed}
```

## Chart fields

```text
--chart-view {command_center,trend_lab,consistency_map,training_atlas,...aliases}
--chart-days 7..365
--chart-theme THEME_ID
```

## Examples

```bash
python -m novafit.cli --profiles
python -m novafit.cli --user 2 --dashboard
python -m novafit.cli --user 2 --recommendations --language es
python -m novafit.cli --chart atlas.png --chart-view training_atlas --chart-theme lime
```

Use `NO_COLOR=1` to disable ANSI color while preserving readable output.
