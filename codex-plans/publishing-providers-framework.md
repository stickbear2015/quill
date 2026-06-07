# Publishing Providers Framework Plan

Status: Proposed. Owner: product and engineering. Scope: planning only, no implementation approved yet.

Tracking:

- GitHub issue: `#140`
- Issue URL: [community-access/quill issue #140](http://github.com/community-access/quill)

This plan must be read together with [docs/QUILL-PRD.md](C:/code/git-src/quill/docs/QUILL-PRD.md), which remains the product source of truth. If this plan conflicts with the PRD, the PRD wins.

## Summary

Introduce a provider-based publishing framework that lets QUILL connect to external publishing platforms without turning WordPress into a one-off special case.

WordPress is the first planned provider because it is common, mature, and exposes a stable REST API. The framework should still be designed so later providers can plug into the same concepts, workflows, and UI surfaces.

This document is a planning artifact only. It describes the proposed architecture, rollout path, risks, and decision points before any code is accepted.

## Spec status

This document now serves two roles:

- a planning record of the repo audit and integration constraints
- a pre-implementation product and engineering spec for the first approved publishing slices

Anything in this document labeled as a recommendation is the current preferred direction unless a later review explicitly changes it.

## Goals

- Let users publish without leaving QUILL.
- Treat WordPress as the first provider, not the final architecture.
- Preserve QUILL's accessibility bar across setup, browsing, publishing, and error recovery.
- Reuse existing QUILL patterns where they already solve adjacent problems well.
- Keep the first approved slice small enough to review clearly.
- Follow the PRD requirements for explicit network consent, feature metadata and gating, and standard-control accessibility behavior.

## Planning-stage decisions locked by this spec

These decisions are now the recommended baseline for future implementation unless product review explicitly reopens them:

- publishing starts under `Tools -> Publishing`, not as a new top-level menu
- publishing does not graduate to a top-level menu later under the current product direction
- WordPress is the only named provider in the first user-visible slices
- publishing ships behind a dedicated gated feature id
- the first implementation adds no publishing status-bar cell
- the first implementation does not depend on Quillins or any third-party plugin runtime
- local-to-remote linkage starts in a Quill-local registry, not inside the source document
- the first publish path is explicit, review-first, and never silent
- the first content path should prefer HTML-oriented output, with any source transformation explained plainly to the user

These decisions can still be changed, but the burden should be on the change proposal to explain why the current spec is no longer the safest fit for Quill.

## Non-goals for the first approved slice

- Full multi-provider plugin loading.
- A generic third-party provider marketplace.
- Rich media upload workflows.
- Taxonomy, category, tag, SEO, or theme-specific editing.
- Real-time bidirectional sync.
- Bulk cross-site publishing.

## Why this fits QUILL

QUILL already owns most of the writing lifecycle:

- writing
- editing
- review
- accessibility auditing
- AI-assisted revision

Publishing is the next natural step. If users have to leave QUILL for the final handoff, the workflow breaks at the point where many users most want continuity and low friction.

## Existing repo patterns this plan should reuse

The current codebase already has patterns worth reusing instead of inventing parallel systems:

- Provider metadata modules in `quill/core`
- Dedicated connection dialogs in `quill/ui`
- Secure secret storage via Credential Manager or platform fallback
- Feature-flag gating through `FeatureManager`
- HTTPS and local-endpoint policy checks
- Cause-specific verification messages for network configuration flows

The AI connection system is the strongest direct precedent. The publishing design should borrow its shape where that shape still makes sense.

Additional structure observed in the current codebase that should shape the plan:

- `quill/ui/main_frame_menu.py` already owns a very large, centralized top-level menu build and event-binding surface.
- `quill/ui/assistant_tools.py` already provides a mature pattern for connection dialogs, hub dialogs, verification actions, model discovery, and review-first summary text.
- `dialogs.md` and the generated dialog inventory already act as the project’s explicit dialog-governance system.

## Repo-wide planning audit

This section records the current repo audit so the plan is based on the real application structure, not assumptions.

### Full-repo audit scope

This planning pass reviewed the repo as a full system, not only the obvious UI files. The audit covered:

- top-level governance and contributor docs
- product docs and user-facing guides
- `quill/core` feature, command, settings, storage, trust, notifications, and network patterns
- `quill/ui` shell integration points for menus, dialogs, status bar, and assistant-style connection flows
- `quill/tools` enforcement gates for dialog inventory and network egress review
- `quill/plugins` and related tests to verify current extensibility limits
- representative unit-test families that would fail if publishing were added carelessly
- project config in `pyproject.toml` to confirm typing, test, packaging, and dependency expectations

This means the plan below is intentionally written against the repo's real contracts, not against a hypothetical clean-slate architecture.

### Documentation and policy audit

Confirmed from `CONTRIBUTING.md`, `README.md`, `RELEASE.md`, `docs/QUILL-PRD.md`, `docs/userguide.md`, and `dialogs.md`:

- the repo already has explicit workflow, product, release, and UX rules
- `docs/QUILL-PRD.md` is the source of truth for behavior, trust, and discoverability requirements
- user-facing behavior is expected to be explicit, plain-language, and accessibility-first
- dialog additions are treated as governed product surfaces, not incidental implementation details
- release discipline matters because `main` is protected and changes are expected to be reviewable and sliceable

Planning implication:

- publishing must be treated as a product feature spanning architecture, UX, tests, and docs from the start
- each user-visible publishing slice should be planned with docs and dialog-governance work included, not postponed

### Architecture and layering

Confirmed from `CONTRIBUTING.md` and the current code:

- `quill/core` is the pure domain layer and should own publishing provider definitions, settings models, connection verification logic, and capability metadata.
- `quill/ui` owns menus, dialogs, status-bar interactions, command palette surfacing, and widget lifecycle.
- `quill/plugins` is intentionally minimal in the current product and should not be treated as a ready-made publishing extension mechanism for the first approved slices.
- `quill/tools` and `tests` already enforce behavior around dialogs, menu wiring, and feature surfaces.

### Menu structure

Confirmed from `quill/ui/main_frame_menu.py`:

- the menu shell is already centralized and very large
- top-level menus are already fixed and tested for order
- menu items are individually bound and the repo has tests that fail if a new menu id is appended without a corresponding menu binding

Planning implication:

- publishing should enter through the existing menu architecture, not a separate shell model
- any future publishing menu entry must be planned together with command ids and bind coverage

Additional planning implication from the menu source:

- `quill/ui/main_frame_menu.py` is already a large contract-heavy surface, so publishing should begin as a compact submenu rather than a top-level shell redesign
- any first implementation should avoid spreading publishing menu construction across multiple new mixins unless there is already an established pattern for that split

### Command system

Confirmed from `quill/core/commands.py` and `quill/core/feature_command_map.py`:

- commands are explicitly registered
- each command needs a stable command id
- each command is tied to a feature id, either explicitly or via the mapping helper
- command visibility can be filtered by the active feature manager

Planning implication:

- publishing must be planned as a command family, not merely as menu labels or dialog launches
- the plan must define command naming early enough that feature gating, palette surfacing, and help coverage can stay consistent

Additional planning implication from the command registry:

- publishing commands should be registered through the same explicit `CommandRegistry.register(...)` path as the rest of the app
- command titles should be plain-language first, because they will surface in menus and the command palette without a second translation layer

### Feature gating and profile integration

Confirmed from the PRD, `quill/core/features.py`, and `quill/core/feature_command_map.py`:

- Quill treats feature ids as a cross-cutting contract
- features gate commands, menus, settings, help, and status surfaces
- hidden and quiet behavior is already a first-class concept

Planning implication:

- publishing needs a dedicated feature id and must be designed as gated from the start
- planning should assume incomplete publishing flows remain hidden or quiet until their corresponding slices are ready

Additional planning implication from the shipped profile model:

- the safest first stance is to keep publishing hidden or quiet outside `Full Quill` and explicit overrides until the end-to-end workflow proves stable
- publishing must declare privacy/network impact metadata honestly, because feature descriptions already carry those semantics

### Dialog governance

Confirmed from `dialogs.md`, `quill/tools/dialog_inventory.py`, `tests/unit/ui/fixtures/dialog_inventory.json`, and `tests/unit/ui/test_dialog_inventory.py`:

- dialogs are a governed surface with explicit inventory and classification
- new dialogs are not informal additions; they require registry presence and sanctioned classification
- the repo already distinguishes `native`, `web`, and `hardened_custom` dialog surfaces

Planning implication:

- every planned publishing dialog must be named and treated as a governed dialog surface
- the first slice should minimize dialog count and nesting because every new surface adds governance and regression burden

Additional planning implication from the dialog governance tooling:

- any publishing dialog implementation will need both human checklist coverage in `dialogs.md` and machine registry coverage in `tests/unit/ui/fixtures/dialog_inventory.json`
- a plan that adds too many secondary or nested dialogs too early will create unnecessary maintenance pressure

### Existing connection-flow precedent

Confirmed from `quill/ui/assistant_tools.py` and `quill/core/assistant_ai.py`:

- the app already has a mature connection dialog pattern
- the current precedent includes provider choice, help text, secure secret handling, verification, discovery actions, and clear status messaging
- endpoint security and blank-key rules are already enforced in tested core logic

Planning implication:

- publishing should mirror this pattern rather than inventing a bespoke setup flow
- WordPress verification should follow the same cause-specific messaging philosophy

Additional planning implication:

- publishing connection UX should reuse the app's existing pattern of "configure, verify, then discover or act"
- secure-secret handling should follow the same split between ordinary settings and secure credential storage

### Notifications and status bar

Confirmed from `quill/core/notifications.py` and `quill/ui/main_frame_statusbar.py`:

- Quill already has a persistent notifications store
- the status bar is interactive and feature-aware
- status cells are deliberately tied to actions, not just passive text

Planning implication:

- publishing does not need a custom “toast” model
- user-facing publishing outcomes should be planned through existing notification/status patterns where appropriate
- the first slices should avoid adding a new status-bar cell unless publishing becomes persistent enough to justify one

Additional planning implication from the status-bar implementation:

- status-bar cells in Quill are interactive, keyboard-navigable, and feature-aware, so adding one is a heavier commitment than adding a message string
- the first publishing slices should use explicit dialog feedback plus the existing notification center rather than introducing a persistent publishing cell too early

### Help and user-facing docs

Confirmed from `README.md`, `docs/userguide.md`, `docs/QUILL-PRD.md`, and `dialogs.md`:

- the project already documents connection flows, trust/privacy expectations, and menu entry points in detail
- user-facing text expects plain-language, explicit wording
- dialog additions imply checklist and eventual userguide/help updates

Planning implication:

- publishing is not done when the core works; help/userguide/discoverability updates must be part of the rollout plan
- the plan should stage documentation work alongside feature slices instead of as an afterthought

Documentation hook-in sequence for publishing:

- update `dialogs.md` as soon as a publishing dialog exists
- update user-facing docs only when the feature is no longer hidden-only
- keep wording honest about provider support and plugin/runtime limitations

### Plugin and extensibility reality

Confirmed from `quill/plugins/__init__.py`, `quill/plugins/api.py`, and `tests/unit/core/test_plugins.py`:

- third-party plugin loading is locked off
- the plugin API is intentionally minimal right now
- the product term “Quillins” exists, but the runtime is not yet a general extension platform for this feature

Planning implication:

- this plan must not depend on Quillins for the first implementation
- future provider extensibility should be architected internally first, then exposed later when plugin runtime policy actually supports it

### Test and enforcement audit

Confirmed from the current test suite and tooling:

- menu structure and menu binding contracts are tested
- dialog inventory and dialog classification are tested
- feature mapping and profile behavior are tested
- plugin policy expectations are tested
- provider and connection logic already have unit-test precedents in adjacent systems
- network egress is structurally audited in `quill/tools/network_egress_audit.py`

Likely enforcement surfaces for publishing work:

- `tests/unit/ui/test_main_frame_menu_contract.py`
- `tests/unit/ui/test_dialog_inventory.py`
- `tests/unit/core/test_features.py`
- provider-oriented core tests modeled after existing assistant/provider tests
- a likely future `network_egress_audit` entry once real publishing requests are implemented

Planning implication:

- publishing must be planned against existing enforcement points before implementation starts
- every user-visible slice should declare which test contracts it is expected to touch

### Settings, storage, and trust-model audit

Confirmed from `quill/core/settings.py`, `quill/core/storage.py`, `quill/core/trust.py`, `quill/core/net.py`, and adjacent connection flows:

- Quill already distinguishes ordinary settings from sensitive secrets
- JSON persistence is atomic and path-guarded
- trusted-location and explicit-consent behavior are already part of the app's design vocabulary
- verified TLS is the baseline for outbound HTTPS requests

Planning implication:

- publishing settings must be split into normal configuration versus secure credentials
- remote publishing must follow the same explicit-consent and verified-transport stance as other networked features
- the publishing plan should assume no ad hoc file persistence shape that bypasses current storage patterns

### Packaging and dependency audit

Confirmed from `pyproject.toml`:

- `quill/core` is under stricter typing expectations than `quill/ui`
- tests, lint, and packaging assume incremental, reviewable additions
- optional dependencies are already grouped by capability, rather than bundled indiscriminately

Planning implication:

- the first publishing slice should prefer a core-heavy design that is easy to type-check and unit-test
- provider dependencies should be kept minimal for the first slice and should not force a broad packaging rethink

### Editor and document-lifecycle audit

Confirmed from the repo structure and product docs:

- Quill centers the local writing/editing workflow and treats external actions as extensions of that workflow
- documents, save paths, format handling, and status/reporting are already designed around local-first editing
- the current product model does not justify mutating arbitrary document formats for remote-link state in the first slice

Planning implication:

- the safest first hook is from the existing current-document workflow outward to publishing actions
- remote linkage should begin with a Quill-local registry unless a later approved design chooses document-embedded metadata

## PRD constraints this plan must satisfy

The PRD sets several non-optional requirements that apply directly to publishing work:

- No silent network calls. Any remote publishing action must be explicit, consented, show progress where appropriate, and report the outcome.
- Accessibility-first UI. Publishing surfaces should use the same stock-control, screen-reader-native approach Quill expects elsewhere in the product.
- Feature-registry integration. Publishing cannot be an orphan surface; it needs a feature id, metadata, privacy and network labels, and consistent gating across commands, menus, settings, help, and status surfaces.
- Local-first trust model. Remote publishing is optional, visible, and never the default path for ordinary editing.
- Plugin realism. The PRD’s plugin runtime is limited in v1.0, so this plan must not assume a broad third-party publishing plugin marketplace as a first implementation dependency.
- Menu and command discoverability. Any eventual publish actions should fit the command palette, menu model, and keybinding conventions rather than becoming a separate ad hoc workflow.

## Proposed architecture

### 1. Core provider model

Add a publishing domain in `quill/core` with:

- provider definitions
- connection settings
- secure credential handling
- endpoint verification
- provider capability metadata

The framework should not assume all providers behave like WordPress. The core abstractions should represent QUILL actions, not REST endpoints.

The implementation should also respect Quill’s layer boundaries from `CONTRIBUTING.md` and the PRD:

- `quill/core` owns provider logic, settings models, verification logic, and capability metadata
- `quill/ui` owns dialogs, menus, progress, and announcements
- publishing work should not add raw persistence or widget ownership into `core`

### 2. Provider contract

Each provider should eventually implement a shared contract covering:

- verify connection
- list or browse content
- fetch a single item
- create draft
- update draft or post
- publish now
- schedule publish

Nice-to-have later:

- delete or trash
- upload media
- sync status comparison

Recommended planning shape for the contract:

- one provider interface in `quill/core`
- one command-facing service layer that translates Quill actions into provider calls
- no UI classes in the contract itself

### 3. WordPress provider

The first provider should target the standard WordPress REST API and support:

- self-hosted WordPress
- WordPress.com sites exposing the standard API
- WP Engine-hosted sites
- other hosts exposing compatible WordPress REST endpoints

Authentication baseline:

- WordPress username
- WordPress Application Password

### 4. Settings and secrets

Connection settings should likely include:

- provider id
- site URL
- username
- content format preference
- optional site-specific defaults later

Secrets should be stored using the same secure pattern already used by AI connection flows, not plain settings JSON.

### 5. Feature gating

Publishing should ship behind its own feature flag until it is proven end to end.

Recommended initial flag shape:

- hidden or quiet in normal profiles
- visible in Full Quill or explicit feature override
- documented as experimental until the workflow is complete
- labeled with explicit privacy and network impact metadata per the PRD feature-registry model

Recommended feature metadata stance:

- maturity: `advanced` or equivalent early-stage label until draft publishing and update flows are both stable
- privacy label: explicitly network-sending
- visibility: hidden or quiet outside `Full Quill` until the first full user-visible slice is approved

## Proposed UX surfaces

### Current UI structure the plan should fit into

The current application already has these top-level menus in the shell:

- File
- Edit
- Insert
- View
- Search
- AI
- BITS Whisperer
- Navigate
- Format
- Tools
- Window
- Help

Because that structure already exists, publishing should be planned as an extension of the current shell rather than as a separate UI model.

## Phase 1 product spec

This section defines the desired behavior for the first coherent user-visible publishing phase. It is intentionally specific enough to guide later implementation and review.

### Phase 1 scope

Phase 1 should include:

- provider-aware publishing connection setup
- WordPress connection verification
- publish-current-document confirmation and draft creation
- explicit result reporting
- command and menu discoverability for the approved actions

Phase 1 should not include:

- top-level `Publishing` menu promotion
- persistent sync
- media upload
- category/tag/taxonomy editing
- multi-provider user choice beyond WordPress
- document-embedded remote metadata
- a publishing status-bar cell

### Phase 1 user story

The intended first user journey is:

1. The user discovers `Tools -> Publishing`.
2. The user opens `Publishing Connection...`.
3. The user selects WordPress, enters site URL, username, and application password, and verifies the connection.
4. The user returns to the current document and chooses `Create Draft...` or `Publish Current Document...`.
5. Quill presents a review-first confirmation dialog with title, destination summary, publish state, and network explanation.
6. Quill performs the explicit remote action.
7. Quill reports the outcome through the dialog result, status text, and notifications.

### Phase 1 command set

The recommended phase 1 command family is:

- `publishing.connection`
- `publishing.verify_connection`
- `publishing.create_draft`
- `publishing.publish_current`

The following commands should be planned but deferred from the first user-visible slice:

- `publishing.browse_content`
- `publishing.open_remote_item`
- `publishing.update_remote_item`
- `publishing.schedule_publish`

### Phase 1 menu contract

The recommended phase 1 menu contract is:

- `Tools -> Publishing -> Publishing Connection...`
- `Tools -> Publishing -> Verify Publishing Connection`
- separator
- `Tools -> Publishing -> Create Draft...`
- `Tools -> Publishing -> Publish Current Document...`

`Browse Published Content...` should remain planned for a later slice unless it is explicitly approved into the first user-visible rollout.

### Exact hook-in plan

This section describes the current planning view of exactly how publishing would hook into existing Quill surfaces when implementation is eventually approved.

#### 1. Feature registry hook-in

Planned hook:

- define a dedicated publishing feature id in `quill/core/features.py`
- add command-to-feature mappings in `quill/core/feature_command_map.py`
- ensure publishing surfaces follow the same hidden/quiet/on rules as other advanced features

What this avoids breaking:

- existing profile behavior
- command palette filtering
- help/menu/status consistency gates

#### 2. Command registry hook-in

Planned hook:

- register publishing commands through the existing command registry
- make menu items, palette entries, and later keybindings resolve through those commands

Recommended initial command family:

- `publishing.connection`
- `publishing.verify_connection`
- `publishing.create_draft`
- `publishing.publish_current`
- `publishing.browse_content`
- `publishing.open_remote_item`
- `publishing.update_remote_item`

What this avoids breaking:

- menu-only feature drift
- orphan dialogs not reachable from the palette
- inconsistent feature-id attribution

#### 3. Menu hook-in

Planned hook:

- append a new `Publishing` submenu under `Tools` in `quill/ui/main_frame_menu.py`
- bind each menu id through the existing `wx.EVT_MENU` pattern
- keep the first menu footprint deliberately small

Recommended initial submenu items:

- `Publishing Connection...`
- `Verify Publishing Connection`
- separator
- `Create Draft...`
- `Publish Current Document...`
- `Browse Published Content...`

Phase 1 refinement:

- for the first coherent user-visible rollout, `Browse Published Content...` is recommended as deferred unless review decides that draft creation without browse support would be too limiting

What this avoids breaking:

- top-level menu sprawl before the workflow is mature
- failure of menu binding contract tests
- discoverability gaps between menu and command palette

#### 4. Dialog hook-in

Planned hook:

- implement publishing dialogs as governed `wx.Dialog` surfaces or sanctioned stock/web surfaces, depending on the specific need
- add each publishing dialog to `dialogs.md`
- ensure each new dialog is accepted by the dialog inventory gate

Planned first dialog surfaces:

- `Publishing Connection Dialog`
- `Publish Current Document Dialog`
- later `Browse Published Content Dialog`

What this avoids breaking:

- dialog inventory gates
- keyboard and screen-reader regression expectations
- focus return and escape/default button contracts

#### 5. Notifications and status hook-in

Planned hook:

- use existing notifications for meaningful results such as connection verified, draft created, or publish failed
- consider status-bar integration only after publishing becomes persistent enough to justify a dedicated surface

Recommended first status behavior:

- no dedicated publishing status-bar cell in the first implementation slices
- rely on explicit dialog feedback, status text, and notifications

What this avoids breaking:

- unnecessary status-bar complexity
- premature persistent UI for a feature that may remain gated or quiet

#### 6. Help and documentation hook-in

Planned hook:

- update `dialogs.md` when dialogs are added
- update user-facing docs only when a slice becomes user-visible
- keep PRD-aligned wording around privacy, network consent, and supported scope

What this avoids breaking:

- stale dialog checklist coverage
- discoverability gaps
- mismatch between the actual shipping UI and the user guide

#### 6a. Governance and audit hook-in

Planned hook:

- keep publishing changes aligned with the existing contributor and release rules
- treat network egress review, dialog registration, and feature mapping as first-class acceptance criteria
- include docs updates in the same slice as newly user-visible publishing surfaces

What this avoids breaking:

- shipping a user-visible feature that bypasses current repo gates
- a plan that looks sound architecturally but fails the repo's actual governance model

#### 7. Extensibility hook-in

Planned hook:

- keep provider architecture internal-first in `quill/core`
- do not expose Quillin/plugin extension points for publishing in the initial approved work
- plan a later internal seam where provider registration could be generalized when plugin policy permits it

What this avoids breaking:

- the current locked-off third-party plugin policy
- false expectations that provider installation is available now

## Exact implementation-thinking summary

This section is intentionally concrete so later implementation, if approved, can proceed from a shared mental model rather than vague intent.

### How the feature would enter the app

The planned entry path is:

- feature registry enables publishing for the active profile
- command registry exposes publishing commands
- `Tools -> Publishing` surfaces the approved subset of those commands
- dialogs handle connection setup and explicit remote actions
- notifications and status text report outcomes

This means publishing would hook into the existing application shell the same way other advanced features do, instead of becoming a sidecar workflow or a one-off floating tool.

### How the current document would participate

The working assumption is:

- the active document remains the source object
- publish actions read from the active document state
- publish confirmation happens in a dialog before any remote call
- remote identity is stored outside the document in the first design, likely in a Quill-local registry keyed by file path or document identity

This minimizes risk to the existing editor and format handlers while still allowing later update flows.

### How WordPress-specific behavior would stay contained

The working assumption is:

- provider-neutral commands ask for publish, browse, update, or verify actions
- a service layer translates those actions into provider-specific API calls
- WordPress-specific fields or limitations stay inside provider/service code and provider-aware help text, not spread through global shell logic

This keeps the UI language mostly provider-neutral while still allowing the first provider to be WordPress.

### How this avoids breaking today’s app

The current planning model is deliberately conservative:

- no change to top-level menu order in the first slices
- no new status-bar cell in the first slices
- no plugin-runtime dependency
- no silent background sync
- no document-format mutation for remote ids in the first slice
- no bypass around the command registry, menu bindings, dialog inventory, feature gating, settings persistence, or network-egress review systems

That is the core reason this plan should integrate cleanly with the existing codebase if implementation is later approved.

### Recommended menu placement strategy

Based on the current menu layout, the best planning path is:

### Phase A: start inside `Tools`

Use a dedicated publishing submenu under `Tools` for the first implementation slices. That keeps the feature discoverable without prematurely promoting an incomplete workflow to a new top-level menu.

Recommended initial submenu label:

- `Tools -> Publishing`

Recommended first commands in that submenu:

- `Publishing Connection...`
- `Verify Publishing Connection`
- `Publish Current Document...`
- `Create Draft...`
- `Browse Published Content...`

Items that are not yet implemented should remain visible only when consistent with the project’s feature-gating rules; otherwise they should stay hidden behind the feature flag until ready.

Planning note from the menu contract audit:

- each new publishing menu id must have a matching `wx.EVT_MENU` binding
- the plan should treat that as part of the acceptance criteria for any implementation slice that adds menu items

### Phase B: evaluate a top-level `Publishing` menu later

Only after the workflow is complete enough to feel first-class should the project consider promoting publishing to its own top-level menu.

Promotion criteria should include:

- connection flow complete
- create/update/browse flows complete
- command palette coverage complete
- help and dialog inventory coverage complete
- accessibility verification complete

### Command palette integration

Every planned publishing action should also exist as a command-palette command from the start. The menu should not be the only discovery path.

Recommended initial command concepts:

- `publishing.connection`
- `publishing.verify_connection`
- `publishing.create_draft`
- `publishing.publish_current`
- `publishing.browse_content`

### Phase 1 UI surface

The smallest coherent user-facing setup is:

- a `Publishing` or `Publish` entry point
- a connection dialog for provider selection and WordPress setup
- a verify connection action

This is the minimum needed before post creation flows make sense.

The eventual UI should use Quill’s normal discoverability paths:

- menu entry
- command palette command
- feature-gated visibility
- clear disabled-state explanation when unavailable

Phase 1 recommendation:

- keep the visible first flow to connection plus publish-current actions
- do not expand into browse/update until the connection and draft-creation paths are stable and understandable

### Dialog strategy based on existing app patterns

The existing AI surfaces provide the closest UI precedent for publishing. The publishing plan should intentionally reuse that shape:

- a focused connection dialog for provider-specific credentials and verification
- an optional publishing hub dialog later if the workflow grows beyond one dialog
- plain-language summary text near the top of the dialog
- explicit action buttons for verification and discovery tasks
- `OK` or `Cancel` modal behavior with proper escape and default-action wiring

### Recommended first publishing dialogs

#### 1. Publishing Connection Dialog

Purpose:

- choose provider
- enter site URL
- enter username
- enter application password
- verify connection

Recommended controls:

- provider choice
- site URL text field
- username text field
- application password field with reveal toggle
- provider help text
- verify button
- optional future button for “Browse content”

This dialog should be the publishing equivalent of the existing AI connection dialog, not a brand-new interaction model.

Expected plain-language summary text:

- explain that Quill can connect to a publishing site only when the user configures it
- state that verification sends a deliberate network request to the configured site
- state that credentials are stored securely on the device

#### 2. Publish Current Document Dialog

Purpose:

- confirm what is being sent
- choose title
- choose draft or publish now
- choose initial format behavior if needed

Recommended controls:

- title text field
- status choice: draft or publish now
- content-format summary
- plain-language network summary
- confirmation buttons

This dialog should be review-first and explicit about remote action.

Expected plain-language summary text:

- say whether the action will create a draft or publish immediately
- name the target site clearly
- state that document content will be sent over the network if the user continues
- explain any format conversion in one sentence, not jargon

#### 3. Browse Published Content Dialog

Purpose:

- list remote content
- inspect summary metadata
- open selected item into QUILL
- choose update target when publishing changes later

Recommended controls:

- searchable list control
- metadata preview pane or read-only text area
- open button
- refresh button

This should likely come after connection and initial publish flows are proven.

### Dialog governance requirements

Because the repo already treats dialogs as a governed surface, publishing planning should explicitly require:

- a `dialogs.md` entry for every user-facing publishing dialog
- dialog inventory registration when code is eventually added
- dialog contract compliance: title announcement, tab order, enter/escape behavior, and focus return
- nested dialog planning kept minimal in the first slice

Recommended classification expectations:

- `Publishing Connection Dialog`: likely `hardened_custom`
- `Publish Current Document Dialog`: likely `hardened_custom`
- confirm-only or pick-one prompts inside the flow: prefer native dialogs where possible

### Phase 2 UI surface

After connection works:

- create draft
- publish current document
- schedule publish
- browse existing posts
- open a selected post into QUILL for editing

### Accessibility requirements

All publishing surfaces must meet the same QUILL bar as other dialogs:

- keyboard-only complete
- predictable focus
- plain-language verification and failure messages
- no dead-end dialogs
- clear success announcements
- no hidden network behavior
- use stock, screen-reader-friendly controls consistent with the PRD’s writing-surface and dialog philosophy

More specifically, based on the current dialog estate:

- prefer stock `wx.Dialog`, `wx.TextCtrl`, `wx.Choice`, `wx.ListBox`, and standard buttons
- avoid introducing bespoke publishing-specific custom controls in the first iteration
- keep verification and publish flows in short, linear dialogs rather than wizard sprawl

## UX contract for first implementation

This is the planning-level UX contract that future implementation should satisfy.

### Connection setup behavior

The connection dialog should:

- default to WordPress as the only visible provider in the first user-visible slice
- ask for site URL, username, and application password
- provide a visible verify action before save-and-exit is the only path forward
- use cause-specific feedback such as invalid URL, insecure endpoint, authentication failure, unreachable host, or successful verification

The connection flow should not:

- auto-verify silently on field blur or dialog open
- hide the fact that a real network call is happening
- use provider-specific jargon without plain-language explanation

### Publish confirmation behavior

The publish dialog should:

- name the target site
- show the proposed title
- let the user choose at least draft versus publish now, unless the slice is draft-only
- explain content-format behavior in plain language
- require explicit confirmation before any remote call starts

The publish flow should not:

- assume the current filename is always the final title without showing it
- publish immediately on menu command with no confirmation step
- perform background retries or deferred sync in the first slice

### Outcome reporting behavior

Success reporting should:

- confirm what happened in plain language
- identify the target site
- provide the remote result identity that matters most, such as URL or remote item id
- surface the outcome through dialog feedback, status text, and notifications

Failure reporting should:

- say what failed
- keep the message specific where possible
- avoid traceback language and raw protocol noise unless the detailed view is explicitly requested

## Planning-stage acceptance criteria

The plan should consider a future slice ready for implementation only if the slice can satisfy these criteria in concept before any code starts.

### Acceptance criteria for slice 1 foundation work

- the feature id, command ids, and initial provider/service boundaries are defined in advance
- the connection model separates ordinary settings from secure credentials
- the endpoint policy is explicitly HTTPS-first and consistent with existing network rules
- the slice does not require new menus or dialogs unless separately approved
- the test plan names the affected core test families and confirms no dialog/menu gates are expected to change

### Acceptance criteria for the first user-visible slice

- the menu location is fixed as `Tools -> Publishing`
- the command names and labels are fixed
- the dialog list is fixed and minimal
- the user journey is explicit and review-first
- the documentation update list is known in advance
- the regression surfaces are named in advance

### Regression checklist for future implementation review

Any implementation proposal should explicitly verify impact on:

- feature registry definitions and profile visibility behavior
- command registry and command-to-feature mappings
- menu ids and `wx.EVT_MENU` binding coverage
- dialog inventory and `dialogs.md`
- notification usage and status-text reporting
- settings persistence versus secure-secret storage boundaries
- network-egress review expectations
- user-facing docs once the feature becomes visible

## Recommended decisions resolved from earlier open questions

These replace the earlier broad ambiguity with a recommended spec stance.

### Menu placement

Recommendation:

- start under `Tools -> Publishing`
- do not create a top-level `Publishing` menu in the first implementation waves

Rationale:

- this matches current shell architecture
- it minimizes menu-order churn
- it keeps the feature discoverable without overselling early maturity

### Provider naming in the first UI

Recommendation:

- WordPress should be the only user-facing provider in the first visible slice, even if the core is provider-based

Rationale:

- it keeps the user promise honest
- it prevents a “provider framework” UI from implying support breadth that does not exist yet

### Title derivation

Recommendation:

- prompt every time, with the default suggested from the first heading and a fallback to filename

Rationale:

- it avoids surprising remote titles
- it still keeps the workflow fast

### Remote linkage storage

Recommendation:

- use a Quill-local registry in the first phase

Rationale:

- it avoids mutating the source document contract
- it reduces risk across multiple document formats

### First publish format behavior

Recommendation:

- prefer HTML-oriented output in the first WordPress slice
- if source text is Markdown or another format, explain the conversion in the confirmation step

Rationale:

- WordPress natively expects HTML in the standard REST flow
- this is the least ambiguous first behavior

### First user-visible dialog set

Recommendation:

- `Publishing Connection Dialog`
- `Publish Current Document Dialog`

Deferred by default:

- `Browse Published Content Dialog`

Rationale:

- this is the smallest coherent user journey
- it keeps the first visible surface area reviewable

### First visible remote action

Recommendation:

- the first visible remote action set should include both `Create Draft...` and `Publish Current Document...`
- the default selection inside the publish confirmation dialog should still be `Draft`

Rationale:

- this keeps the first visible workflow honest about the likely long-term shape of publishing
- it avoids a later UX reset where users must relearn the same dialog for publish-now
- it still preserves the safer path by defaulting to draft

Guardrail:

- publish-now should remain an explicit user choice in the dialog, never the menu command's silent default

### Browse in the first visible rollout

Recommendation:

- `Browse Published Content...` should stay deferred from the first visible rollout

Rationale:

- connection plus draft/publish-current is the smallest coherent workflow
- browse adds more dialog surface, more remote state complexity, and more inventory/test burden
- deferring browse keeps the first user-visible slice easier to review and stabilize

Revisit trigger:

- browse should be reconsidered after draft creation and publish-now are stable and their local-to-remote linkage model is proven

### Success result model

Recommendation:

- the first slice should preserve both the remote URL and the remote id when both are available

Rationale:

- the URL is the most useful immediate user-facing result
- the remote id is often the more stable internal linkage key
- storing both avoids an early redesign if one is needed later for update, browse, or sync flows

First-slice behavior:

- if only one of these values is returned reliably, Quill should store the available value and leave room in the local record for the other later

### Quill-local linkage record shape

Recommendation:

- the first slice should use a flat Quill-local linkage record shape

Recommended minimum fields:

- `provider_id`
- `site_url`
- `remote_id`
- `remote_url`

Deferred by default:

- `last_synced_at`
- content hash or revision markers
- remote title cache

Rationale:

- a flat local record is easy to inspect, easy to migrate later, and low-risk for the first slice
- it preserves the information most likely to matter for later update and browse flows without overdesigning sync early

### Success wording

Recommendation:

- use plain-language completion messages built around action + site + result
- messages should use the configured host only

Recommended first wording set:

- draft created: `Draft created on <host>.`
- draft created with link: `Draft created on <host>. Link available.`
- published now: `Published to <host>.`
- published now with link: `Published to <host>. Link available.`
- connection verified: `Publishing connection verified for <host>.`

Rationale:

- this matches Quill's preference for concise, useful announcements
- it avoids jargon like `POST succeeded` or `remote object created`
- it keeps success reporting understandable in speech output

### Publish-state label text

Recommendation:

- the publish-state choice should use action-oriented labels:
  - `Create draft`
  - `Publish now`

Rationale:

- these labels describe what will happen next, not just the resulting state
- they are clearer in speech output than bare state words like `Draft`
- they keep the dialog aligned with Quill’s preference for plain, explicit wording

## Proposed rollout plan

### Slice 0: planning and approval

- approve architecture direction
- approve naming
- approve feature-gating approach
- approve first implementation slice
- approve exact hook-in points for commands, menus, dialogs, notifications, and docs

### Slice 1: framework foundation

- publishing provider metadata
- connection settings model
- secure secret storage
- endpoint security validation
- WordPress verification flow
- unit tests for those pieces
- feature-registry and feature-gating integration

No publishing menu or dialog should be implemented in this slice unless specifically approved as part of the slice. This slice is primarily architecture and connection validation.

Planned tests and governance for this slice:

- core unit tests modeled after current assistant/provider tests
- no dialog inventory changes
- no menu contract changes

This slice does not need post editing yet. Its job is to prove that the framework shape is sound.

### Slice 2: WordPress draft publishing

- create draft from current QUILL document
- send title and body
- return resulting URL or post id
- announce success clearly
- add the first approved publishing menu entry points
- add the first approved publishing dialogs

Planned tests and governance for this slice:

- menu binding coverage remains green
- dialog inventory snapshot updated deliberately
- dialog checklist entries added
- user-facing text reviewed for plain-language and explicit-consent wording

### Slice 3: update and browse

- list existing posts
- fetch a post into QUILL
- update an existing draft or post
- extend menu coverage once the browse flow is real
- add dialog inventory coverage for browse and update surfaces

Planned tests and governance for this slice:

- browse dialog added to dialog registry and checklist
- command coverage expanded for remote-item actions
- feature gating verified across new browse/update commands

### Slice 4: schedule and sync polish

- schedule publish
- compare local versus remote state
- define the first honest sync model

## Document model questions

These need explicit decisions before implementation expands:

### 1. Source format

QUILL documents may be plain text, Markdown, or HTML-oriented content. WordPress expects HTML in the standard REST flow.

Decision needed:

- should the first WordPress slice publish HTML only
- or should Markdown be converted on publish

Recommended planning stance:

- first implementation should support a simple, explicit content-format choice
- default to HTML-oriented output for least ambiguity
- user-facing behavior must be explicit when a document is being transformed rather than round-tripped as-is

### 2. Title extraction

Decision needed:

- derive title from filename
- derive title from first heading
- prompt every time
- allow site-specific default behavior later

Recommended first behavior:

- prompt with a suggested default from the first heading, then fallback to filename

### 3. Remote identity

Once a local document is linked to a remote WordPress post, QUILL needs a way to remember that association.

Options:

- embedded document metadata
- sidecar metadata file
- QUILL-local registry keyed by file path

Recommended first planning direction:

- start with a QUILL-local registry because it is lowest-risk and avoids mutating document formats unexpectedly
- if later moved into document metadata, that should require a separate approval step because it changes the file-behavior contract

## Risks

### 1. Architecture risk

If WordPress is implemented directly in UI code, the framework will become WordPress-specific and harder to generalize later.

Mitigation:

- keep provider logic in `quill/core`
- keep UI surfaces provider-agnostic where practical

### 2. Accessibility risk

Publishing workflows can turn into complex multi-step dialogs with hidden state.

Mitigation:

- keep first slices narrow
- verify every dialog flow with the project’s existing dialog hardening expectations
- keep publishing UI within the same command/menu/help/status model rather than inventing a parallel surface

### 3. Security risk

This feature adds new network egress and new stored credentials.

Mitigation:

- reuse existing secure storage patterns
- enforce HTTPS for remote endpoints
- keep all requests explicit and user-driven
- add tests for endpoint policy and auth failure reporting
- include feature metadata that accurately labels privacy and network impact

### 4. Content fidelity risk

Markdown or rich structured content may not map perfectly to WordPress post content.

Mitigation:

- start with clearly defined supported formats
- avoid overpromising sync fidelity in the first release

### 5. Scope risk

Publishing can easily expand into CMS management.

Mitigation:

- explicitly keep first scope to connect, verify, create, update, browse, and schedule

### 6. Regression risk against existing shell contracts

Because Quill already has tests and conventions around menus, dialogs, commands, and feature surfaces, publishing can break the app structurally even before it breaks functionally.

Mitigation:

- plan every new publishing command id before implementation
- plan every menu id and matching event binding before implementation
- plan every publishing dialog as an inventory-governed surface
- avoid introducing a status-bar cell in the first slices
- stage docs and checklist updates as part of each user-visible slice

## Remaining decisions for review

The major planning decisions are now covered by this spec. Any remaining questions should be treated as normal implementation-detail review items rather than planning blockers.

## Recommended first approved implementation slice

If this plan is approved, the first code slice should be limited to:

- publishing provider metadata
- publishing connection settings
- secure application-password storage
- WordPress endpoint verification
- feature gating
- focused unit tests

And it should explicitly avoid:

- assuming the v1.1+ plugin marketplace/runtime is already available
- adding custom-drawn or unusual UI controls
- adding any silent or background remote publishing behavior

That slice is small enough to review clearly and large enough to validate the architecture before we build user-facing publishing actions on top of it.

## Recommended first user-visible slice after the foundation

If the foundation slice succeeds, the next recommended slice should be limited to:

- `Tools -> Publishing` submenu wiring
- `Publishing Connection Dialog`
- `Publish Current Document Dialog`
- WordPress draft creation from the current document
- explicit publish-now from the current document as a user-controlled choice
- plain-language success and failure reporting
- local preservation of remote URL and remote id when available
- targeted dialog, menu, feature, and core tests

And it should still avoid:

- browse/update/schedule flows unless separately approved
- top-level menu promotion
- status-bar cell addition
- multi-provider UI promises

## Full-repo planning conclusion

After the full repo audit, the current planning direction still looks usable inside Quill's existing architecture if it is implemented conservatively.

Why it looks viable:

- the repo already has a provider-and-connection precedent to borrow from
- the shell already has stable places to surface new commands and dialogs
- the feature/profile system can gate incomplete work safely
- the test suite already tells us where careless integration would break contracts
- the product docs strongly support explicit, user-driven network features when they are accessible and well-labeled

What makes it high-risk if done carelessly:

- menu and dialog surfaces are contract-heavy
- network features are governance-heavy
- plugin/extensibility assumptions would be premature
- status-bar and profile integration carry more blast radius than they first appear to

So the planning recommendation remains:

- design publishing as an internal core-plus-shell feature
- start with WordPress as the first provider, not the whole product model
- enter through `Tools -> Publishing`
- use explicit dialogs and existing notifications
- keep remote linkage outside the source document at first
- do not promote publishing to a top-level menu under the current direction
- keep publish-now as an explicit writer-controlled choice rather than a system-decided content action
- delay any status-bar cell or external plugin story until the base workflow is proven

## What this plan deliberately does not change

To reduce risk, the current planning direction does not assume changes to:

- the top-level menu order
- the command palette architecture
- the status-bar layout model
- the plugin runtime policy
- the current dialog classification system
- the existing AI or BITS provider systems beyond borrowing their connection-flow patterns

Those systems are integration points, not redesign targets, for this feature.

## Acceptance bar for the planning phase

This plan is ready to move into implementation only when:

- the architecture direction is approved
- the first slice is approved
- we create a branch before implementation starts
