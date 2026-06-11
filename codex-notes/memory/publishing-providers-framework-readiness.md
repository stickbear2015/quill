# Publishing Providers Framework Readiness

Status: stable implementation checkpoint with current `origin/main` merged, focused validation green, and next work identified.

## 2026-06-10 final state update

- current branch is `features/publishing-providers-framework`
- current branch history now includes merge of the latest observed `origin/main` work as of 2026-06-10:
  - `54cef8c` Node.js runtime / QDC tutorial / installer component work
  - `106ef2c` editor menu consolidation / notebook store groundwork
  - `d394863` notebook workspace UI layer
- branch-owned publishing and merge-sensitive verification slice last passed at:
  - `87 passed in 9.85s`
- Codex support documents have been centralized under `codex-notes/`
- branch is in a good reviewable state, but direct merge to `main` is still not the recommended next step

## Current recommendation

- okay for visibility / draft PR discussion
- not ideal yet for final merge to `main`

Why:

- publishing foundation, connection management, and browse/open flows are in place
- approved content-representation behavior is implemented
- but the explicit `Update Remote Content...` lifecycle step is still the next intended product slice
- branch also carries process/support documentation that may deserve scoping before any final `main` merge

## 2026-06-10 audit update

- `fork/main` has been resynced to `origin/main`
- `features/publishing-providers-framework` has been merged with current `main`
- the branch is no longer planning-only; it already contains publishing foundation, connection management, and browse/open implementation work
- publishing now enters through `File > Publish`, not a top-level `Publishing` menu
- browse/open now supports the approved representation choice:
  - default `Readable Markdown`
  - per-open override `Raw HTML`
  - automatic fallback to `Raw HTML` when conversion would be misleading or lossy
- publishing-open metadata now records the chosen Quill authoring surface explicitly so later update work can stay honest about Markdown-authored versus HTML-authored remote tabs

## Git state

- Repo: `C:\code\git-src\quill`
- Branch: `features/publishing-providers-framework`
- local historical notes below may mention older merge points; latest meaningful branch state is the merged-and-documented state above
- latest documentation-only cleanup commits after the merge include:
  - `249ba49` `docs(codex): record merge readiness assessment`
  - `08f3677` `docs(codex): centralize notes and planning artifacts`
  - `1b65db4` `docs(codex): record clean push checkpoint`

## Source of truth

- Planning spec: `codex-notes/plans/publishing-providers-framework.md`
- Tracking issue: `#140`
- Issue URL: `http://github.com/community-access/quill`
- Product source of truth: `docs/QUILL-PRD.md`

## Pre-coding guardrails

- Follow `CONTRIBUTING.md` and `docs/QUILL-PRD.md`.
- Keep the implementation simple, accessible, and powerful by reusing existing Quill patterns.
- Preserve the approved `File > Publish` menu direction from the current plan.
- Support both posts and pages.
- Keep network actions explicit, review-first, and never silent.
- Keep publishing behind feature gating until the implementation is ready.
- Do not add memory or process notes under the existing product docs tree unless explicitly requested.

## Existing patterns the implementation should reuse

- Feature definitions and command gating in `quill/core/features.py` and `quill/core/feature_command_map.py`
- Command registration via `quill/core/commands.py`
- Menu wiring in `quill/ui/main_frame_menu.py`
- Top-level menu definitions and menu customization in `quill/ui/main_frame.py` and `quill/core/menu_customization.py`
- Dialog patterns from `quill/ui/assistant_tools.py`
- Dialog governance from `dialogs.md` and `quill/tools/dialog_inventory.py`
- Notification storage in `quill/core/notifications.py`
- Verified TLS and no-silent-network expectations in `quill/core/net.py` and `quill/tools/network_egress_audit.py`
- About-surface contributor pattern in `quill/ui/main_frame.py`
