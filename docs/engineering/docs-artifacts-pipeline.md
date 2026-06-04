# Docs-artifact regeneration pipeline

This note documents how Quill keeps each `docs/**/*.md` source in sync with its
rendered `.html` and `.epub` artifacts, and how the GitHub Actions workflows that
enforce and automate that stay correct. It is the canonical reference for the
[Docs artifacts](../../.github/workflows/docs-artifacts.yml) workflow, the
docs-parity guard ([scripts/check_docs_artifacts.py](../../scripts/check_docs_artifacts.py)),
and the `workflow-lint` gate in [PR CI](../../.github/workflows/pr-ci.yml).

## What the pipeline guarantees

Every Markdown file under `docs/` ships alongside a matching HTML and EPUB build,
so readers who consume the published artifacts never see a stale rendering of a
source that has since changed. Two mechanisms cooperate:

- A **parity guard** that fails CI when an edited `docs/**/*.md` is missing an
  updated `.html` or `.epub` sibling in the same change.
- An **auto-regeneration workflow** that rebuilds artifacts for changed sources
  and, on a same-repo pull request, pushes them back to the PR branch so the
  author does not have to install Pandoc.

## The parity guard

[scripts/check_docs_artifacts.py](../../scripts/check_docs_artifacts.py) diffs a
base and head ref, and for every changed `docs/**/*.md` source that still exists,
requires that both its `.html` and `.epub` siblings also changed in that range.
It recurses into subdirectories (`docs/planning`, `docs/qa`, ...), not just the
top level. The guard runs as the "Verify docs artifacts are regenerated" step in
[Accessibility CI](../../.github/workflows/accessibility-ci.yml) and is a
required check.

## The auto-regeneration workflow

[Docs artifacts](../../.github/workflows/docs-artifacts.yml) triggers only when a
`docs/**.md` source changes. It has two design constraints that drove its
current shape, both learned from real failures.

### Constraint 1 — EPUB output is non-deterministic

Pandoc embeds a fresh UUID and build timestamp in every EPUB, so regenerating an
unchanged source produces different bytes each run. HTML output, by contrast, is
deterministic. A naive "regenerate everything and commit the diff" approach
therefore reports false staleness on every run and fails forever.

The workflow handles this by:

1. Scoping regeneration to only the Markdown that changed in the push/PR range
   (mirroring the parity guard), not the whole tree.
2. Always rebuilding the **deterministic HTML**, but generating an EPUB **only
   when it is missing** — never rewriting an existing one, so the random-UUID
   churn cannot manifest.
3. Basing the "is this stale?" decision on deterministic HTML drift plus
   genuinely untracked new files, never on EPUB byte differences.

### Constraint 2 — `main` is a protected branch

The workflow cannot push regenerated artifacts to `main`: branch protection
requires changes to arrive through a pull request, so a direct push is rejected
(`GH006: Protected branch update failed`). Attempting it was the original chronic
failure. The reconcile step now branches on context:

- **Same-repo pull request:** commit the regenerated artifacts and push them back
  to the PR's source branch, so the eventual merge into `main` is already in sync.
- **Push to `main`, or a fork PR:** do not attempt a push. Fail loudly with the
  exact diff and a "regenerate locally" message, so a human regenerates the
  artifacts and brings them in through a pull request.

### Regenerating locally

When the workflow or the parity guard reports a stale artifact, regenerate it
with the same Pandoc invocations CI uses:

```bash
pandoc <source>.md -f gfm -t html5 -s -o <source>.html
pandoc <source>.md -f gfm -t epub3      -o <source>.epub
```

Commit both artifacts with the source (through a pull request for `main`).

## Workflow linting (`workflow-lint`)

The `workflow-lint` job in [PR CI](../../.github/workflows/pr-ci.yml) runs
[actionlint](https://github.com/rhysd/actionlint) (pinned to a specific image)
over every workflow on each push and pull request. It statically validates YAML
structure, action input contracts, and shell-safety patterns.

This gate exists because a real script-injection vector slipped into the docs
workflow: an untrusted `${{ github.head_ref }}` was interpolated directly into an
inline `git push` script, where a crafted branch name could execute arbitrary
shell. The fix — and the rule the gate now enforces automatically — is to pass
workflow context through the step `env:` block and reference it as a shell
variable, never to expand untrusted `${{ github.* }}` values inline.

## Verifying the workflow logic

Because the reconcile logic is shell rather than Python, it is validated two ways:

1. **Static analysis** with actionlint, now wired into CI as `workflow-lint`.
2. **Behavioral simulation** against a throwaway git repository with a bare remote
   whose `pre-receive` hook rejects writes to `main` (simulating branch
   protection) and a mock `pandoc` that mirrors the measured behavior
   (deterministic HTML, random-bytes EPUB). The simulation exercises the
   in-sync, fail-loud, recursive-subdirectory, missing-EPUB, no-churn, and
   PR-push-back paths.

When changing the reconcile logic, re-run actionlint locally and re-run the
behavioral simulation before relying on CI.
