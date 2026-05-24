# PCCX Launcher Release Guide

This guide is for public GitHub releases from `pccxai/pccx-launcher`.

## Release Tag

Use a date tag for the first public source release:

```text
v2026.5.24
```

Use a new `vYYYY.M.D` tag for later public release snapshots unless the
project adopts package-versioned tags.

## Preflight

Run these checks from a clean branch that is up to date with `main`:

```bash
bash scripts/smoke.sh
git diff --check
```

Confirm the public repository metadata before creating the release:

```bash
gh repo view pccxai/pccx-launcher --json nameWithOwner,visibility,isPrivate,defaultBranchRef
```

Expected visibility is `PUBLIC` and default branch is `main`.

## Cut The GitHub Release

After the release pull request is merged:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git tag v2026.5.24
git push origin v2026.5.24
gh release create v2026.5.24 \
  --repo pccxai/pccx-launcher \
  --title "PCCX Launcher v2026.5.24" \
  --notes-file docs/release-notes/v2026.5.24.md
```

Do not create tags from an unmerged feature branch.

## Release Boundary

The public release is a source release for checked launcher contracts,
readiness fixtures, and local preview scripts. It does not execute a model,
touch hardware, package binaries, call providers, upload data, or make
runtime-readiness claims.
