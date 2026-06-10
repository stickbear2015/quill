# Publishing Providers Framework Readiness

Status: active implementation and audit follow-up after merge with current `main`.

## 2026-06-10 audit update

- `fork/main` has been resynced to `origin/main`
- `features/publishing-providers-framework` has been merged with current `main`
- the branch is no longer planning-only; it already contains publishing foundation, connection management, and browse/open implementation work
- publishing now enters through `File > Publish`, not a top-level `Publishing` menu
- current browse/open behavior still opens remote content as raw HTML in a normal Quill tab
- the approved next refinement remains the explicit representation choice:
  - default `Readable Markdown`
  - per-open override `Raw HTML`
  - automatic fallback to `Raw HTML` when conversion would be misleading or lossy

## Git state

- Repo: `C:\code\git-src\quill`
- Branch: `features/publishing-providers-framework`
- local `main`, `origin/main`, and `fork/main` match at `c43ff0f`
- latest merge commit on the feature branch: `23b8adf`

## Source of truth

- Planning spec: `codex-plans/publishing-providers-framework.md`
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
