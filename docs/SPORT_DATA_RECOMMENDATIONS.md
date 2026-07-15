# Sport & Data Recommendation Engine 🧠

## Product boundary

The engine provides general educational wellness suggestions. It does not diagnose illness, prescribe treatment, calculate medical risk, recommend extreme training, provide rehabilitation or replace a qualified professional.

## Inputs

- active profile goals;
- activity level;
- preferred sport focus;
- recorded steps;
- recorded water;
- record coverage;
- missing dates;
- recent direction;
- recorded mood frequencies.

## Outputs

`RecommendationPlan` contains:

- language;
- data-confidence percentage;
- confidence explanation;
- ordered recommendation items;
- suggested weekly rhythm;
- explicit disclaimer.

Each `RecommendationItem` contains title, action, reason, category and priority.

## Confidence

Confidence is derived from coverage and record count. Empty or sparse archives produce low confidence and emphasize data collection rather than behavior claims.

## Recommendation families

### Movement progression

Suggests a comfortable next step when recent movement is below the user’s configured target or history is limited. It never assigns speed, load, heart-rate zone or maximal intensity.

### Hydration tracking

Compares recorded average with the user-configured tracking target and recommends placing water or recording intake at fixed moments. It does not prescribe medical fluid intake.

### Recovery protection

Reminds active users to preserve low-intensity or rest time. It does not infer overtraining or injury.

### Data quality

When coverage is limited, recommends improving measurement consistency before interpreting patterns.

### Weekly rhythm

Uses `beginner`, `balanced` or `active` preference plus sport focus to present a flexible example rhythm. The user should adapt it to comfort, environment and qualified guidance.

## Localized output

Recommendation plans are available in English, Spanish and Hebrew through GUI and CLI.

## Stop conditions

The user-facing disclaimer instructs users to stop in the presence of pain, dizziness, chest discomfort or unusual symptoms and seek qualified guidance.
