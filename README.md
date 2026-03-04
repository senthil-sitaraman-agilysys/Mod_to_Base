# Mod → Base Promotion

This repository semi-automates moving approved changes from the **mod** library
to the **base** library using a GitHub Actions workflow.

---

## Repository Layout

```
.
├── base/          ← Stable, versioned base library
│   ├── VERSION    ← Current base version (e.g. 1.0.0)
│   └── README.md
├── mod/           ← Pending modifications awaiting approval
│   └── README.md
└── .github/
    └── workflows/
        └── mod-to-base.yml  ← Promotion workflow
```

---

## How to Promote Mod Changes to Base

### Step-by-step guide

1. **Add your changes to `mod/`**
   Commit and push any new or updated files to the `mod/` directory.
   Open a Pull Request and get it reviewed and merged as usual.

2. **Trigger the promotion workflow**
   - Go to **Actions** → **Promote Mod Changes to Base** → **Run workflow**.
   - Choose a **Version Bump Type**:

     | Type | Example | When to use |
     |------|---------|-------------|
     | `patch` | `1.0.0` → `1.0.1` | Bug fixes, small tweaks |
     | `minor` | `1.0.0` → `1.1.0` | New backward-compatible features |
     | `major` | `1.0.0` → `2.0.0` | Breaking changes |

   - Click **Run workflow**.

3. **Review the generated Pull Request**
   The workflow automatically:
   - Copies all files from `mod/` into `base/` (preserving folder structure).
   - Bumps the version in `base/VERSION`.
   - Opens a new Pull Request titled **"chore: promote mod → base (vX.Y.Z)"**.

4. **Approve and merge**
   Review the file diff in the PR, approve it, and merge.
   The base library is now updated to the new version.

---

## Version Numbering

Versions follow [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).
The current base version is stored in [`base/VERSION`](./base/VERSION).
