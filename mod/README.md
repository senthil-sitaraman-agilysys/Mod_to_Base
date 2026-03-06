# Mod Library

This is the **mod (modification) library**. It holds changes that are pending
approval before being promoted to the base library.

## Workflow

1. Add or update files in this `mod/` directory.
2. Open a Pull Request so that changes can be reviewed.
3. Once the PR is approved and merged, trigger the
   [Mod → Base promotion workflow](../.github/workflows/mod-to-base.yml)
   to apply the changes to the base library with an updated version number.
