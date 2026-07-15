# NovaFit 4.1 Motivation Center ✨

## Product goal

The Motivation Center converts existing local records into a calm, useful next action. It is not a health diagnosis, therapist, coach replacement or prediction engine.

## Grounded inputs

The engine reads only values already available to NovaFit:

- number of records and coverage;
- average steps and hydration;
- configured step and hydration goals;
- tracking and combined-goal streaks;
- days reaching one or both goals;
- recent direction;
- earned milestone counts;
- optional locally saved purpose text.

No random percentage, medical claim or fabricated achievement is shown.

## Output model

`build_motivation_snapshot()` returns:

- **headline** — concise state summary;
- **message** — supportive explanation based on the records;
- **daily spark** — deterministic encouragement appropriate to the state;
- **micro-action** — the smallest useful next step;
- **weekly challenge** — a bounded challenge based on current coverage or goal consistency;
- **next milestone** — label, progress value and target;
- **achievements** — unlocked and locked evidence-backed badges;
- **celebration level** — quiet, steady or strong visual intensity.

## Private purpose board

Users can save:

- a personal why;
- this week's focus;
- a small reward note.

These values live in the same local configuration file as the selected theme and goals. They are not included in weather requests and are not transmitted to a backend because NovaFit has no health-data backend.

## Focus reset

The 60-second visual focus reset is an optional animation with a clear non-medical label. It is a pacing aid, not a breathing prescription. Reduced-motion mode produces a stable visual state.

## Empty and incomplete data

- No records: invite the user to create the first record.
- Missing recent dates: prioritize tracking continuity rather than claiming decline.
- Goal progress close to completion: suggest the smallest remaining action.
- Goal reached: acknowledge the evidence without implying medical benefit.

## Tests

The suite verifies:

- empty-data behavior;
- grounded milestones;
- achievement unlock conditions;
- deterministic spark selection;
- no medical-diagnosis language;
- CLI rendering.
