# NovaFit Analytics Reference 📊

## Purpose

This document defines every metric and visualization used by NovaFit Ultimate 4.1. The goal is reproducibility: another developer should be able to read the stored rows, follow the formulas and reach the same result.

NovaFit analytics are **descriptive product signals**, not medical measurements or recommendations.

## Input record

Each daily record may contain:

- ISO calendar date;
- non-negative step count;
- non-negative water liters;
- optional non-negative calorie reference;
- optional mood label;
- optional private note.

One date maps to one row. Saving the date again updates the row.

## Time ordering

Persistence returns rows newest-first for user interfaces. Analytics sort chronologically before calculating streaks, rolling windows or date series.

## Missing dates

A missing date is not automatically equivalent to a zero-valued record.

- streaks break when a calendar date is absent;
- calendar heatmaps leave the cell empty;
- daily chart series expose the missing date explicitly;
- rolling calculations wait for the complete declared window;
- coverage counts only dates actually stored.

This distinction prevents NovaFit from pretending to know what happened on a day that was never recorded.

## Goal metrics

Given configured goals:

```text
step_goal = 10,000
water_goal_l = 2.0
```

A date is:

- a **step-goal day** when `steps >= step_goal`;
- a **water-goal day** when `water_l >= water_goal_l`;
- a **combined-goal day** when both conditions are true.

Rates divide qualifying dates by stored dates, not by every calendar day in history.

## Coverage

The dashboard coverage metric uses the latest 30-calendar-day window ending at the latest stored date:

```text
coverage_pct = stored_dates_in_window / 30 × 100
```

The result is capped between 0 and 100.

## Tracking streaks

A tracking streak is a sequence of records whose dates differ by exactly one day.

### Current tracking streak

Start at the latest record and move backward while each previous date is one calendar day earlier.

### Longest tracking streak

Scan all sorted unique dates and keep the largest consecutive sequence.

### Longest combined-goal streak

Filter dates that met both primary goals and calculate the longest calendar-consecutive sequence.

## Recent movement trend

The recent trend compares two groups of seven **records**:

```text
latest_average = mean(latest 7 stored step values)
previous_average = mean(previous 7 stored step values)
change_pct = (latest_average - previous_average) / previous_average × 100
```

The metric is unavailable with fewer than 14 records or a zero previous average.

This is a record-window comparison, not a calendar-week comparison. The UI labels it as recent average movement rather than a medical change.

## Routine consistency score

The 0–100 score is a transparent portfolio/product metric:

```text
score =
    0.30 × recent_30_day_coverage
  + 0.25 × capped_average_step_goal_progress
  + 0.25 × capped_average_water_goal_progress
  + 0.20 × active_day_share_latest_7_calendar_days
```

Where:

```text
capped_average_step_goal_progress = min(average_steps / step_goal, 1) × 100
capped_average_water_goal_progress = min(average_water / water_goal, 1) × 100
active_day_share_latest_7_calendar_days = stored_dates_in_latest_7_days / 7 × 100
```

Why cap goal progress?

- one exceptional day should not erase several missing dates;
- the score represents routine consistency, not total athletic output;
- the score stays bounded and explainable.

What the score excludes:

- age;
- sex or gender;
- BMI;
- diagnoses;
- medication;
- heart rate;
- sleep;
- injury;
- clinical thresholds.

## Daily routine score in Trend Lab

Each tracked date receives:

```text
daily_score =
    min(steps / step_goal, 1) × 50
  + min(water_l / water_goal_l, 1) × 50
```

A missing date receives no recorded progress. The chart uses zero at that calendar position to make the gap visible.

## Rolling averages

For a seven-point rolling average:

- positions 1–6 remain empty;
- position 7 is the mean of points 1–7;
- each later position moves the complete seven-point window by one.

Leading partial windows are deliberately not drawn.

## Weekday profile

Records are grouped Monday through Sunday. For each weekday, NovaFit calculates:

- record count;
- average steps;
- average water;
- average non-empty calories.

The best weekday is the weekday with the highest average steps. It is a descriptive pattern, not a recommended training day.

## Mood distribution

Mood labels are trimmed, counted case-sensitively as entered and sorted by:

1. descending count;
2. label for deterministic ties.

Empty mood values are excluded.

## Calendar matrix

The matrix is Monday-first. Columns are ISO weeks and rows are weekdays.

Each tracked date gets a 0–1 intensity:

```text
step_progress = min(steps / step_goal, 1)
water_progress = min(water_l / water_goal_l, 1)
intensity = (step_progress + water_progress) / 2
```

Missing dates remain null and render with the empty-cell background.

## Command Center panels

### Movement signal

- raw daily step line;
- filled area for visual continuity;
- seven-point rolling average;
- configured goal threshold;
- goal-aware point colors;
- maximum-value annotation.

### Goal constellation

Three concentric rings show:

- step-goal rate;
- hydration-goal rate;
- combined-goal rate.

The center shows the documented routine consistency score.

### Hydration current

- daily bars;
- color distinction around the goal threshold;
- seven-point rolling average;
- configured goal line.

### Weekday rhythm

A polar display normalizes each weekday's average steps against the strongest weekday in the current record set.

### Mood check-ins

A horizontal frequency chart. It says what was recorded, not what the mood “means.”

### Consistency field

A compact calendar heatmap with missing dates left visibly empty.

## Trend Lab panels

- movement trajectory;
- hydration stability;
- optional calorie reference;
- daily routine score.

Calories remain optional and are presented as a user-configured reference—not a nutrition prescription.

## Consistency Map panels

- extended calendar matrix;
- weekday movement averages;
- weekday hydration averages;
- mood distribution;
- current and historical streak summary.

## Empty states

With no records, figures remain valid and present explicit empty-state text. This protects CLI and report generation in fresh installations.

## Testing

Analytics tests protect:

- missing date behavior;
- goal counts;
- current and longest streaks;
- combined-goal streaks;
- rolling windows;
- weekday completeness;
- mood sorting;
- calendar alignment;
- score bounds;
- grounded insight text;
- headless rendering in every view and theme.
