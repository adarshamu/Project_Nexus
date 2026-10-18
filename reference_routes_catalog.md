# NEXUS Complete Route & Entity Catalog
# Extracted directly from https://x5t7evxf2zu7m.kimi.page/ and its production bundle

## 1. Authentication & System Access Pages
- **`/login`** - Sign In with role selection (Developer, Admin, Super Admin), first-login state, unavailable state.
- **`/signup`** - Employee self-registration with batch code validation (e.g. `FS-2026-A`).
- **`/access-denied`** - Role-based authorization barrier with navigation recovery.
- **`/account-unavailable`** - Suspended / off-hours / deactivated employee account landing page.
- **`/change-password`** - Initial mandatory or scheduled password update.
- **`/forgot-password`** - Simulated self-service credential recovery.
- **`/reset-password`** - Token-based password reset simulation.

## 2. Developer Workspace
- **`/dashboard`** - Personalized engineering snapshot (strongest skill, focus skill, active course progress, batch cohort ranking).
- **`/skillquest`** - Interactive SkillQuest career progression (4-quadrant skill breakdown, learning velocity, practice recommendations).
- **`/skillquest/skills`** - Full technical skills inventory (React, TypeScript, Testing, Node.js, Accessibility, Docker).
- **`/skillquest/courses`** - 6 Core Masterclasses:
  1. *React State Patterns in Practice*
  2. *TypeScript Generics from First Principles*
  3. *API Debugging and Resilience*
  4. *Accessible Component Engineering*
  5. *Testing Confidence: Unit to Integration*
  6. *Prompt Evaluation for Product Teams*
- **`/skillquest/courses/:courseId`** - Interactive course module viewer with progress tracking and syllabus.
- **`/skillquest/leaderboard`** - Cohort ranking leaderboard for assigned batches (`FS-2026-A`, etc.).
- **`/human-api`** - Technical problem escalation hub and expert matching.
- **`/human-api/problem/:problemId`** - Specific technical problem diagnostic detail.
- **`/human-api/ai/:problemId`** - Grounded AI Expert guidance (Visual Expert archetype).
- **`/human-api/expert/:expertId`** - Senior engineer profile (Amara Osei, Ava Chen, Marcus Vance, etc.).
- **`/human-api/chat`** - Real-time peer huddle room simulation.
- **`/settings`** - Profile, technology interests, notification, and privacy telemetry controls.

## 3. Admin Workspace
- **`/admin`** - Admin Overview: Batch metrics (`FS-2026-A`), active employee rosters, import issues, cohort completion velocity.
- **`/admin/batches`** - Batch Management (`Full Stack Foundations A`, `Full Stack Foundations B`, `Applied AI Engineering`).
- **`/admin/batches/:batchId`** - Deep batch analytics, syllabus pacing, and focus areas.
- **`/admin/batches/:batchId/employees`** - Assigned cohort employee roster management.
- **`/admin/employees/new`** - Onboard new cohort engineer with batch assignment.
- **`/admin/employees/:employeeId`** - Individual employee growth and compliance history.
- **`/admin/courses`** - Curated cohort course catalog and prerequisite controls.
- **`/admin/recommendations`** - Automated learning intervention rules.
- **`/admin/leaderboard`** - Administrative performance and batch pacing leaderboard.
- **`/admin/insights`** - Cohort skill gap analytics and focus areas.
- **`/admin/import`** - CSV/JSON employee roster importer.
- **`/admin/import/:importId/review`** - Staged employee import data review.
- **`/admin/import/:importId/results`** - Batch import validation report.
- **`/admin/audit-log`** - Immutable administrative audit log.
- **`/admin/settings`** - Admin preferences and cohort notification thresholds.

## 4. Super Admin Workspace
- **`/super-admin`** - Organization-wide administrative cockpit.
- **`/super-admin/admins`** - System administrators list.
- **`/super-admin/admins/new`** - Provision new administrator.
- **`/super-admin/admins/:adminId`** - Admin access scope and batch assignments.
- **`/super-admin/batches`** - Global batch lifecycle management.
- **`/super-admin/assignments`** - Admin-to-batch assignment matrix.
- **`/super-admin/audit-log`** - Global security and access audit trail.
- **`/super-admin/settings`** - Organization security policies and retention settings.
