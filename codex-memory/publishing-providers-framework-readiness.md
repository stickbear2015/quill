# Publishing Providers Framework Readiness

Status: ready for implementation planning handoff.

## Git state

- Repo: `C:\code\git-src\quill`
- Branch: `features/publishing-providers-framework`
- `main` matches `origin/main` at `6db2c8f`
- Latest planning commit on the feature branch: `9c5b6e2`

## Source of truth

- Planning spec: `codex-plans/publishing-providers-framework.md`
- Tracking issue: `#140`
- Issue URL: `http://github.com/community-access/quill`
- Product source of truth: `docs/QUILL-PRD.md`

## Pre-coding guardrails

- No product code has been approved yet beyond the planning stage.
- Follow `CONTRIBUTING.md` and `docs/QUILL-PRD.md`.
- Keep the implementation simple, accessible, and powerful by reusing existing Quill patterns.
- Preserve the top-level `Publishing` menu direction from the approved plan.
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
