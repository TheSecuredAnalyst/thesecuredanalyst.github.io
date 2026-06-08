-- Migrates the live table (old draft schema) to match form/index.html + dashboard/index.html
BEGIN;

-- Rename columns to the names the form/dashboard actually use
ALTER TABLE team_assessments RENAME COLUMN other_departments  TO other_dept;
ALTER TABLE team_assessments RENAME COLUMN role_description   TO role_desc;
ALTER TABLE team_assessments RENAME COLUMN analytics_level    TO analytics_understanding;
ALTER TABLE team_assessments RENAME COLUMN availability       TO available_days;
ALTER TABLE team_assessments RENAME COLUMN schedule_note      TO sched_note;
ALTER TABLE team_assessments RENAME COLUMN vision_opportunity TO opportunity;
ALTER TABLE team_assessments RENAME COLUMN should_be_doing    TO should_do;
ALTER TABLE team_assessments RENAME COLUMN anything_else      TO other_comments;

-- Drop the leftovers: admired_page is a duplicate of admire_page (which we added
-- earlier), and skills (jsonb) is replaced by the 22 granular skill_* columns below
ALTER TABLE team_assessments DROP COLUMN IF EXISTS admired_page;
ALTER TABLE team_assessments DROP COLUMN IF EXISTS skills;

-- Add the granular per-skill rating columns the form's slide 3 collects
ALTER TABLE team_assessments
  ADD COLUMN IF NOT EXISTS skill_camera int2,
  ADD COLUMN IF NOT EXISTS skill_vedit  int2,
  ADD COLUMN IF NOT EXISTS skill_reel   int2,
  ADD COLUMN IF NOT EXISTS skill_colour int2,
  ADD COLUMN IF NOT EXISTS skill_subs   int2,
  ADD COLUMN IF NOT EXISTS skill_live   int2,
  ADD COLUMN IF NOT EXISTS skill_photo  int2,
  ADD COLUMN IF NOT EXISTS skill_pedit  int2,
  ADD COLUMN IF NOT EXISTS skill_design int2,
  ADD COLUMN IF NOT EXISTS skill_typo   int2,
  ADD COLUMN IF NOT EXISTS skill_brand  int2,
  ADD COLUMN IF NOT EXISTS skill_ig     int2,
  ADD COLUMN IF NOT EXISTS skill_tt     int2,
  ADD COLUMN IF NOT EXISTS skill_fb     int2,
  ADD COLUMN IF NOT EXISTS skill_yt     int2,
  ADD COLUMN IF NOT EXISTS skill_copy   int2,
  ADD COLUMN IF NOT EXISTS skill_sched  int2,
  ADD COLUMN IF NOT EXISTS skill_stats  int2,
  ADD COLUMN IF NOT EXISTS skill_dead   int2,
  ADD COLUMN IF NOT EXISTS skill_team   int2,
  ADD COLUMN IF NOT EXISTS skill_init   int2,
  ADD COLUMN IF NOT EXISTS skill_fback  int2;

COMMIT;

NOTIFY pgrst, 'reload schema';
