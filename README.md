# Library Promotion (Semi-Automated)

This repository semi-automates moving approved changes from one library folder
to another using a GitHub Actions workflow.

Default example is `mod` → `base`, but the folders are configurable per run.

---

## Repository Layout

```
.
├── base/          ← Example stable, versioned target library
│   ├── VERSION    ← Current base version (e.g. 1.0.0)
│   └── README.md
├── mod/           ← Example source library with approved changes
│   └── README.md
└── .github/
   └── workflows/mod-to-base.yml  ← Promotion workflow
```

## One-time Setup (Required)

Configure repository variable for promote allowlist:

1. Open GitHub repo → **Settings** → **Secrets and variables** → **Actions**.
2. Open **Variables** tab.
3. Add variable:

```text
Name  = PROMOTION_ALLOWED_ACTORS
Value = user1,user2,user3
```

Only these GitHub usernames can run `run_mode=promote`.

---

## Easy Runbook (Full library promotion)

1. Put approved changes in your source folder

- Example: `mod/`.
- Open PR, get review, and merge as usual.

2. Run GitHub Action

- Go to **Actions** → **Promote Library Changes** → **Run workflow**.
- Fill inputs:
  - `run_mode`: `dry-run` first, then `promote`
  - `promote_confirmation`: keep blank for `dry-run`; set `CONFIRM-PROMOTE` for `promote`
  - `source_dir`: folder to copy from (example: `mod`)
  - `target_dir`: folder to copy into (example: `base`)
  - `version_file`: version file to bump (example: `base/VERSION`)
  - `target_branch`: PR destination branch (example: `main`)
  - `version_bump`: `patch` / `minor` / `major`

3. Review plan output (Step 1: dry-run)

- Run once with `run_mode=dry-run`.
- Check **Summary** tab in workflow run for planned files and version bump.

4. Execute promotion (Step 2: promote)

- Run again with same inputs, but `run_mode=promote`.
- Set `promote_confirmation=CONFIRM-PROMOTE`.

5. Review auto-created PR

- Workflow does this automatically:
  - Copies files from `source_dir` to `target_dir` (keeps structure).
  - Skips `README.md` while copying (target README stays library-specific).
  - Bumps version in `version_file`.
  - Creates branch + PR for human review.

6. Approve and merge PR

- After merge, target library becomes the new approved version.

---

## Selective Runbook (Only specific files/folders)

Use this when you want to promote only part of the source library.

1. Go to **Actions** → **Promote Selected Library Changes** → **Run workflow**.
2. Fill the same fields as full promotion, plus:

- `include_paths`: newline-separated file/folder paths relative to `source_dir`.

3. Example `include_paths`:

```text
programs/
copybooks/customer.cpy
sql/ddl/
```

4. First run with `run_mode=dry-run` and verify planned files in workflow **Summary**.
5. Run again with `run_mode=promote` and `promote_confirmation=CONFIRM-PROMOTE`.
6. Workflow copies only those paths into `target_dir`, bumps version, and opens PR.
7. Review and merge the PR.

---

## Tagged Runbook (M02 style line-by-line promotion)

Use this when one source file contains multiple mod tags like `M01`, `M02`, `M03`, `M04`
and you want to promote only one mod tag.

Workflow: **Promote Tagged Mod Changes**

Inputs:

- `run_mode`: `dry-run` first, then `promote`
- `promote_confirmation`: blank for `dry-run`; `CONFIRM-PROMOTE` for `promote`
- `source_dir`: usually `mod`
- `target_dir`: usually `base`
- `version_file`: numeric version file like `base/VERSION` (example `009`)
- `target_branch`: usually `main`
- `selected_mod`: mod tag to promote only (example `M02`)

Behavior:

- Checks source files line by line.
- Keeps only lines tagged with selected mod (example `M02-a`, `M02-d`).
- Converts selected tags to next base version tags:
  - `M02-a` -> `010-a`
  - `M02-d` -> `010-d`
- Drops lines tagged with other mod IDs (`M01`, `M03`, `M04`, etc.).
- For selected `-d` lines, applies source-format comment style:
  - Fixed RPG (`.rpg`, `.sqlrpg`): `*` in column 7
  - Free RPG (`.rpgle`, `.sqlrpgle`): prefix `//`
  - CL/CLLE (`.cl`, `.clle`): wrap with `/* ... */`
  - DDS/files (`.dspf`, `.pf`, `.lf`, `.prtf`, `.dds`): `*` in column 7

Example for your case:

- Current base version = `009`
- Selected mod = `M02`
- New version becomes `010`
- Promoted tags become `010-a` and `010-d`

### Before/After quick samples

Fixed RPG (`.rpg` / `.sqlrpg`) - delete line:

```text
Before:      C                   EVAL      X = Y              M02-d
After:       C     *             EVAL      X = Y              010-d
```

Free RPG (`.rpgle` / `.sqlrpgle`) - delete line:

```text
Before:      eval x = y; // M02-d
After:       // eval x = y; // 010-d
```

CL/CLLE (`.cl` / `.clle`) - delete line:

```text
Before:      CHGVAR VAR(&FLAG) VALUE('Y')   M02-d
After:       /* CHGVAR VAR(&FLAG) VALUE('Y')   010-d */
```

DDS (`.dspf` / `.pf` / `.lf` / `.prtf` / `.dds`) - delete line:

```text
Before:      A          R CUSTREC                    M02-d
After:       A     *    R CUSTREC                    010-d
```

Add line sample (any format):

```text
Before:      ... M02-a
After:       ... 010-a
```

---

## Version Bump Rules

| Type    | Example           | Use when                      |
| ------- | ----------------- | ----------------------------- |
| `patch` | `1.0.0` → `1.0.1` | Small fixes                   |
| `minor` | `1.0.0` → `1.1.0` | Backward-compatible additions |
| `major` | `1.0.0` → `2.0.0` | Breaking changes              |

---

## Important Notes

- `version_file` must contain semantic version format: `MAJOR.MINOR.PATCH`.
- `source_dir` and `target_dir` must be different.
- In `promote` mode, `promote_confirmation` must be exactly `CONFIRM-PROMOTE`.
- In `promote` mode, actor must be listed in repository variable `PROMOTION_ALLOWED_ACTORS`.
- Tagged workflow expects numeric versions in `version_file` (example: `009`, `010`).
- This keeps the process semi-automated: copy + version bump + PR are automated,
  but final approval/merge stays manual.

---

## Hands-on Test Walkthrough (Do this now)

Use this once as UAT so your team can trust the automation.

### A) Create test files in source library

Add sample IBM i source files under `mod/` and push to your repo:

```text
mod/programs/TESTRPG.rpgle
mod/cl/TESTJOB.clle
mod/display/TESTSCRN.dspf
```

Commit and push these test files.

### B) Run Full Promotion workflow

1. Open GitHub repository.
2. Go to **Actions**.
3. Select **Promote Library Changes**.
4. Click **Run workflow**.
5. Use these values:

```text
source_dir    = mod
target_dir    = base
version_file  = base/VERSION
target_branch = main
version_bump  = patch
run_mode      = dry-run
promote_confirmation =
```

6. Click the green **Run workflow** button.
7. Open the run **Summary** and verify files/version shown in the plan.
8. Re-run with same values and set:

```text
run_mode      = promote
promote_confirmation = CONFIRM-PROMOTE
```

### C) Verify success

After run completes:

- A new PR is created automatically.
- PR shows copied files:
  - `base/programs/TESTRPG.rpgle`
  - `base/cl/TESTJOB.clle`
  - `base/display/TESTSCRN.dspf`
- `base/VERSION` is incremented by patch (example: `1.0.0` → `1.0.1`).

If this looks correct, approve and merge PR.

### D) Run Selective Promotion workflow

1. Go to **Actions** → **Promote Selected Library Changes**.
2. Click **Run workflow**.
3. Use values:

```text
source_dir    = mod
target_dir    = base
version_file  = base/VERSION
target_branch = main
version_bump  = patch
run_mode      = dry-run
promote_confirmation =
include_paths =
programs/
cl/TESTJOB.clle
```

4. Run workflow and review **Summary** planned files.
5. Re-run with `run_mode=promote` and `promote_confirmation=CONFIRM-PROMOTE`.

Expected: PR contains only selected paths under `base/` and version bump.

### E) Negative test (must fail)

Run selective workflow with:

```text
include_paths =
bad-folder/
```

Expected: workflow fails with clear error `include_paths entry not found under source_dir`.

This proves validation is working.

### F) Clean-up after UAT

- If this was only testing, close PRs without merge.
- Or merge and then remove test files in a follow-up PR.

---

## Promotion PR Go/No-Go Checklist (Template)

Copy this into your promotion PR description before approval:

```markdown
## Go/No-Go Checklist

### Request Summary

- Source directory:
- Target directory:
- Version file:
- Current version:
- New version:
- Workflow used: Full / Selective

### Technical Validation

- [ ] Workflow run completed successfully.
- [ ] PR branch and target branch are correct.
- [ ] Only expected files are changed in `base/` (or target directory).
- [ ] No unintended delete/overwrite found.
- [ ] `VERSION` bumped correctly (`patch` / `minor` / `major`).
- [ ] For selective run: `include_paths` matches approved scope.

### IBM i / AS400 Validation

- [ ] RPG/CLLE/DSPF source members copied correctly as source text.
- [ ] Member naming conventions are followed.
- [ ] Required compile/deploy activities are identified (if needed).
- [ ] No object-level assumptions in this PR (source promotion only).

### Approval

- [ ] Functional review complete.
- [ ] Technical review complete.
- [ ] Change-management approval complete.

## Decision

- [ ] GO (approve and merge)
- [ ] NO-GO (comments added and PR blocked)

## Sign-off

- Reviewer:
- Date:
- Notes:
```
