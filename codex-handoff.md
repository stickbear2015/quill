# Codex Handoff

## 2026-06-10 17:13:23 -04:00 Latest Coding Update

- completed the planned remote-open representation slice for publishing content
- browse/open now defaults to `Readable Markdown`
- browse/open now offers per-open `Raw HTML`
- added conservative fallback to `Raw HTML` for content Quill should not flatten misleadingly
- publishing-open metadata now records the chosen authoring surface from prepared content instead of hard-coded HTML assumptions

## 2026-06-10 17:13:23 -04:00 Latest Verification

- maintained publishing slice rerun after implementation:
  - `tests/unit/ui/test_main_frame_characterization.py`
  - `tests/unit/ui/test_dialog_inventory.py`
  - `tests/unit/ui/test_main_frame_menu_contract.py`
  - `tests/performance/test_budgets.py`
  - `tests/unit/core/test_publishing.py`
  - `tests/unit/core/test_publishing_browse.py`
  - `tests/unit/core/test_publishing_framework.py`
  - `tests/unit/core/test_features.py`
  - `tests/unit/ui/test_publishing_connection_dialog_a11y.py`
  - `tests/unit/ui/test_main_frame.py`
  - `tests/unit/core/test_remote_sites.py`
  - `tests/unit/ui/test_remote_sites_dialog.py`
- result: 87 passed in 9.96s

## 2026-06-10 16:19:03 -04:00 Maintainer Note

- main-branch findings from the reverted full-suite audit are preserved separately in:
  - `main-branch-audit-note-2026-06-10.md`
- branch work remains scoped to publishing after that note capture

## 2026-06-10 16:15:07 -04:00 Scope Correction

- reverted the out-of-scope audit-only changes from the mistaken full-suite pass
- reset verification back to the branch-owned publishing slice only

## 2026-06-10 16:15:07 -04:00 Current Verification

- reran the maintained publishing-focused slice:
  - `tests/unit/ui/test_main_frame_characterization.py`
  - `tests/unit/ui/test_dialog_inventory.py`
  - `tests/unit/ui/test_main_frame_menu_contract.py`
  - `tests/performance/test_budgets.py`
  - `tests/unit/core/test_publishing.py`
  - `tests/unit/core/test_publishing_browse.py`
  - `tests/unit/core/test_publishing_framework.py`
  - `tests/unit/core/test_features.py`
  - `tests/unit/ui/test_publishing_connection_dialog_a11y.py`
  - `tests/unit/ui/test_main_frame.py`
  - `tests/unit/core/test_remote_sites.py`
  - `tests/unit/ui/test_remote_sites_dialog.py`
- result: 84 passed in 9.75s

## 2026-06-10 15:57:07 -04:00 Audit Update

- ran a full `pytest -q` audit after the merged-`main` integration work
- fixed the stale test cluster that was still assuming pre-merge `QUILL_DATA_DIR` behavior
- added shared home-scoped test data setup in `tests/conftest.py`
- updated persistence/config test files to honor current `main`'s dev-only home-constrained data-dir contract
- tightened two suite hot spots:
  - `tests/unit/core/test_net_tls.py` now prefilters files before AST parsing
  - `quill/core/thesaurus.py` now avoids double synonym cleaning during thesaurus parse

## 2026-06-10 15:57:07 -04:00 Audit Verification

- focused repair slices now pass:
  - stale persistence/config failures: 11 passed
  - IPC/keymap/menu persistence verification: 11 passed
  - TLS audit verification: 5 passed
  - thesaurus reset-cache timeout repro: 1 passed in isolation
- full suite is improved but still not fully green in one uninterrupted run
- current blocking point:
  - `tests/unit/core/test_reset_caches.py::test_thesaurus_preload_after_reset_is_idempotent`
- current read:
  - isolated behavior is green
  - remaining problem appears to be suite-run timeout/performance pressure, not a confirmed publishing regression

## 2026-06-10 15:57:07 -04:00 Recommended Next Slice

- if the suite is stabilized fully green, next planned code work should still be remote-open representation handling:
  - open publishing remotes as `Readable Markdown` by default
  - allow `Raw HTML` override when needed
  - keep representation metadata explicit for follow-on save/update flows

## Latest Merge Update

- resynced local `main` with `origin/main` after upstream advanced by 4 commits
- pushed refreshed `main` to `fork/main`
- merged updated `main` into `features/publishing-providers-framework`
- upstream changes included a substantial new Remote Sites feature touching:
  - `quill/ui/main_frame.py`
  - `quill/ui/main_frame_menu.py`
  - dialog inventory/public-surface fixtures
  - network-egress audit
  - module-size budgets
- reapplied the branch's earlier publishing-audit tighten-ups on top of that merge:
  - explicit raw-HTML publishing-open metadata in `main_frame.py`
  - test fixes for the current dev-only `QUILL_DATA_DIR` contract
  - publishing checklist/readiness/plan updates
- resolved merge conflicts in:
  - `quill/tools/module_size_budgets.json`
  - `tests/unit/ui/fixtures/dialog_inventory.json`
  - `tests/unit/ui/fixtures/main_frame_public_surface.json`
- regenerated dialog/public-surface snapshots from merged source
- merge commit created: `47d5ff7` (`Merge main into features/publishing-providers-framework`)

## Latest Verification

- focused integrated test slice passed after the merge and reapply work:
  - `tests/unit/ui/test_main_frame_characterization.py`
  - `tests/unit/ui/test_dialog_inventory.py`
  - `tests/unit/ui/test_main_frame_menu_contract.py`
  - `tests/performance/test_budgets.py`
  - `tests/unit/core/test_publishing.py`
  - `tests/unit/core/test_publishing_browse.py`
  - `tests/unit/core/test_publishing_framework.py`
  - `tests/unit/core/test_features.py`
  - `tests/unit/ui/test_publishing_connection_dialog_a11y.py`
  - `tests/unit/ui/test_main_frame.py`
  - `tests/unit/core/test_remote_sites.py`
  - `tests/unit/ui/test_remote_sites_dialog.py`
- result: 84 passed

## Latest Audit Update

- performed a branch audit after merging current `main`
- confirmed the publishing branch still aligns with the approved architecture in these areas:
  - feature gating
  - `File > Publish` menu placement
  - dialog governance
  - explicit network-egress review
  - provider-aware core seam for WordPress browse/open
- confirmed the main remaining behavior gap versus the plan is remote-open representation:
  - current implementation opens remote content as raw HTML
  - approved next step is still `Readable Markdown` by default with a per-open `Raw HTML` override and conservative fallback
- tightened the current code to record explicit publishing-open metadata for the interim raw-HTML behavior
- updated `dialogs.md` and local readiness/planning notes to match the real post-merge state
- updated older publishing/feature tests so they honor the current `main` dev-only `QUILL_DATA_DIR` contract from `quill/core/paths.py`
- verified the focused audit slice after those updates: 53 tests passed

## Current State

- Branch: `features/publishing-providers-framework`
- Stage: planning plus implementation/audit alignment
- Coding status: code exists; next work should follow the updated plan and merged-main constraints
- Branch baseline: merged with `main` again on 2026-06-10 after syncing `fork/main` to `origin/main`

## Latest Planning Decisions

- remote content opens as `Readable Markdown` by default
- the open flow provides a per-open override to `Raw HTML`
- Quill automatically falls back to `Raw HTML` when conversion would be too lossy or structurally untrustworthy
- convert only clearly text-first HTML to `Readable Markdown`
- fall back to `Raw HTML` for anything interactive, embedded, layout-heavy, or structurally rich

## Next Likely Planning Step

- refine the fallback boundary into a more exact decision list
- define what metadata must be stored to remember the chosen authoring surface
- check whether the new Remote Sites shell patterns from `main` suggest any publishing-shell simplifications worth adopting before the next publish/update slice
- keep the design provider-neutral and accessibility-first

## Resume Instruction

When returning later, tell Codex:

`Check codex-handoff.md and codex-review-log.md first, then continue planning.`

## File Policy

- these files are temporary local memory aids
- leave them in place if you want continuity across breaks
- update them as the work progresses
