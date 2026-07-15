# Multi-Profile Architecture 👥

## Goal

NovaFit 4.1 allows several people or several personal contexts to share one local installation without mixing records.

## Profile fields

- `id`
- `display_name`
- `avatar`
- `language`
- `theme`
- `step_goal`
- `water_goal_l`
- `calorie_goal`
- `activity_level`
- `sport_focus`
- timestamps

## Isolation rule

Daily records use:

```sql
UNIQUE(user_id, date)
```

Two profiles may therefore have a record for the same calendar date without replacing one another.

## Active profile

`NovaFitDatabase.active_profile_id` determines the default scope for CRUD, analytics, imports, exports, reports and recommendations. Public database methods also accept an explicit `profile_id` when needed.

## Primary-profile protection

Profile `1` is the migration destination for historical records and cannot be deleted. It may be renamed and customized.

## Deletion

Deleting a non-primary profile requires explicit confirmation in the GUI. `ON DELETE CASCADE` removes only that profile’s logs.

## Legacy migration

When a historical `logs` table has no `user_id`:

1. enable a transaction;
2. rename it to a temporary legacy table;
3. create schema v4;
4. create or retain the primary profile;
5. copy every historical row to user `1`;
6. verify and drop the temporary table;
7. commit the transaction.

## Import/export scope

Current JSON/CSV exports operate on the active profile’s records. The user chooses when and where to write the file. A future encrypted multi-profile archive remains a roadmap item.
