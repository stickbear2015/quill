# zfix4 — SHELL-3 live verification & remaining Tier 2 / intake-issue status

This document does two things:

1. **Verification steps** for SHELL-3 (installer-registered "Send to Quill"
   context-menu verbs) — the one manual pass needed to flip SHELL-3 from
   *In progress* to *Done*.
2. **Issue status** — exactly what is left to complete for the file-manager
   intake issues (#113, #114, #115, #116) and the open Tier 2 roadmap items.

---

## Part 1 — SHELL-3 verification steps

### What already shipped (commit `1d3bfc4`, on `main`)

- `build_shell_verb_registry_lines()` in
  `scripts/build_windows_distribution.py` generates the Inno `[Registry]`
  verb keys directly from `quill.core.shell_verbs.default_shell_verbs()`.
- A new opt-in `[Tasks]` checkbox, `shellverbs`, gates every verb key; all
  keys carry `uninsdeletekey` for clean uninstall.
- The committed `installer/quill.iss` is regenerated to include the verbs.
- Six contract tests in
  `tests/unit/scripts/test_build_windows_distribution.py` assert per-verb /
  per-extension coverage, opt-in + uninstall-clean flags, the launch command
  shape, and end-to-end presence in the generated `.iss`.

These are all green (ruff + strict mypy + pytest). **What remains is purely a
live Windows install/uninstall pass — it cannot be done in a non-live
environment and is the only thing standing between SHELL-3 and Done.**

### Prerequisite: install the Inno Setup 6 compiler (ISCC)

The build box does **not** currently have ISCC. Install it once:

```powershell
winget install --id JRSoftware.InnoSetup --source winget
```

Confirm it resolves (either of these should print a path):

```powershell
Get-Command ISCC.exe -ErrorAction SilentlyContinue
@("C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
  "C:\Program Files\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ }
```

### Step 1 — Build the portable bundle + installer

From the repo root, with the venv active:

```powershell
# Build the portable tree, regenerate installer/quill.iss, and compile the
# installer in one pass. --bundle-python makes the result self-contained.
python -m scripts.build_windows_distribution --bundle-python --compile-installer
```

Expected: `windows-distribution\installer\Quill-Setup-<version>.exe` (and/or
`...\Output\Quill-Setup-<version>.exe`) is produced. If `--compile-installer`
is not wired as a flag in your build, compile manually:

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" `
  windows-distribution\installer\quill.iss
```

### Step 2 — Install with the "Send to Quill" verbs enabled

1. Run `Quill-Setup-<version>.exe`.
2. On the **Select Additional Tasks** page, **check**
   *"Add 'Send to Quill' actions (OCR, Open, Read aloud) to the file
   right-click menu"* (it is unchecked by default, by design).
3. Finish the install.

Accessibility check while you are here: the task checkbox label must be read
clearly by your screen reader, and the wizard must not auto-close before the
final status is announced (it is configured `CloseApplications=force`,
`RestartApplications=no`).

### Step 3 — Verify the verbs appear and run (the core test)

The classic registry verbs surface under **"Show more options"** on
Windows 11, and directly in the **Shift+F10** keyboard context menu.

1. In **File Explorer**, navigate to a test **`.png`** (or `.jpg`, `.tif`).
2. Give it focus and press **Shift+F10** (keyboard context menu).
   - On Win11 you may need to arrow to **"Show more options"** first.
3. Confirm these items are present and screen-reader friendly:
   - **OCR with Quill**
   - **OCR with Quill (structured Markdown)** — only meaningful when AI is on
   - **Read aloud in Quill**
   (For a `.txt`/`.md`/`.html` file you should instead see **Open in Quill**
   and **Read aloud in Quill**.)
4. Activate **OCR with Quill**.
5. Confirm: a running QUILL instance is reused (or one launches), focus lands
   on the **OCR review dialog**, and an announcement states what happened.
6. Repeat once for a **`.pdf`** to confirm document handling.

> If a verb does **not** appear, the most likely causes are: the `shellverbs`
> task was left unchecked at install, or another app owns an overriding
> per-extension association. Re-run the installer and confirm the task is
> ticked. The keys are written to **HKCU** (never HKLM), so no elevation is
> needed and no other user is affected.

### Step 4 — Confirm the registry keys exist (optional, precise)

```powershell
# Should list a "Quill.ocr" subkey with a (default) value of "OCR with Quill"
reg query "HKCU\Software\Classes\SystemFileAssociations\.png\shell\Quill.ocr" /ve
reg query "HKCU\Software\Classes\SystemFileAssociations\.png\shell\Quill.ocr\command" /ve
```

The `\command` default value should be:
`"<install>\run-quill.cmd" --action ocr "%1"`.

### Step 5 — Uninstall and confirm clean removal

1. Uninstall QUILL (Settings → Apps, or the Start-menu uninstaller).
2. When prompted about removing personal data, either choice is fine for this
   test (that prompt covers `%APPDATA%\Quill`, not the shell verbs).
3. Re-run the `reg query` commands from Step 4 — both must now return
   **"ERROR: The system was unable to find the specified registry key"**,
   proving `uninsdeletekey` cleaned up the verbs.
4. Re-check **Shift+F10** on the test `.png`: the Quill verbs must be gone.

### Step 6 — Flip SHELL-3 to Done

Once Steps 1–5 pass on real hardware:

- In `golden.md`: change the **SHELL-3** row Status from `In progress` to
  `Done`, move `SHELL-3` out of the two living *Work-in-progress* lists into
  the *Completed* Tier 2 list, and update the tracker totals
  (Tier 2 becomes `60 | 58 | 2 | AI-19, SHELL-2`; bump the 1.0 subtotal and
  grand total Done counts by 1).
- Add a dated activity-log entry recording the live verification pass.
- Regenerate the HTML: `pandoc -s golden.md -o golden.html`.
- Stage `golden.md` + `golden.html` only and commit.

---

## Part 2 — What's left, issue by issue

### Umbrella #113 — Open & OCR from the file manager

**Status: substantially delivered on Windows; keep open as the umbrella.**
The shared groundwork it asked for is done: the action-bearing entry point
(`quill --action <verb> "<path>"`), routing through the existing
single-instance IPC, the qualifying file-type sets, and the initial action
set (Open, OCR, Read aloud) all ship via SHELL-1. Close this only when its
three sub-issues are resolved.

### #114 — Windows Explorer context menu

**Status: classic/Show-more-options path is code-complete and tested; needs
the Part 1 live pass to call done. One sub-item is intentionally deferred.**

| Sub-item from #114 | Status |
| --- | --- |
| Classic registry verbs (`SystemFileAssociations\<ext>\shell\…`) per image ext + `.pdf` | **Done in code** (SHELL-1 runtime writer + SHELL-3 installer registration) |
| Verb invokes shared `--action` entry point over single-instance IPC | **Done** (SHELL-1) |
| Installer registration + clean uninstall | **Done in code** (SHELL-3); **needs live verify** (Part 1) |
| Reachable via Shift+F10; clear labels; focus + announcement after invoke | **Done in code**; confirmed by the Part 1 manual pass |
| **Modern Win11 menu via `IExplorerCommand` (packaged COM)** | **Deferred to QUILL 2.0** — the OS gates the primary menu behind compiled COM + package identity (sparse/MSIX). Out of scope for 1.0. |

**To finish #114 for 1.0:** run Part 1, then post a status comment noting the
modern-menu `IExplorerCommand` piece is tracked as a 2.0 follow-up, and close.

### #115 — macOS Finder integration

**Status: Blocked, correctly. Not a 1.0 item.**
Depends on the macOS port (#42), which is not done. The OCR engine work it
describes (Apple Vision backend) also lands with the macOS port. No action now.

### #116 — Structured OCR (AI-gated)

**Status: functionally delivered (SHELL-2), pending one live-AI verification;
the geometry/bounding-box enhancement is an optional follow-up.**

| Sub-item from #116 | Status |
| --- | --- |
| Gate behind AI + explicit `ocr_structured` opt-in setting | **Done** (SHELL-1/SHELL-2) |
| Dedicated `transform`-style op returning structured Markdown | **Done** — assistant `structure` operation |
| Feed structured result into the OCR review dialog | **Done** — `_apply_ocr_structuring` in the OCR worker |
| Plain-text behavior unchanged when AI off | **Done** — degrades safely with a status note |
| **Capture layout geometry (bounding boxes) for tables/columns** | **Not started** — optional quality enhancement; `OcrLine` has no boxes yet. Nice-to-have, can be a 2.0 follow-up. |

**To finish #116 for 1.0:** one live-key end-to-end run + structuring-quality
tuning on real multi-column / table OCR output (this is the SHELL-2 remainder),
then close noting the geometry enhancement is a future improvement.

---

## Open Tier 2 roadmap items (the honest blockers)

After SHELL-1 (Done) and this SHELL-3 work, Tier 2 stands at **57 of 60**.
The three open items and what each genuinely needs:

| ID | What's left | Blocker class |
| --- | --- | --- |
| **SHELL-3** | The Part 1 live install → right-click → run → uninstall pass | Windows runtime + Inno Setup install cycle |
| **SHELL-2** | One live-AI run + prompt-quality tuning on real OCR; then flip to Done | Configured/available AI backend |
| **AI-19** | Real HTTPS device-login poster, `DeviceLoginDialog`, DPAPI token storage, AIBackend wiring, live sign-in (RFC 8628 state machine already built + tested) | Live provider OAuth device endpoint + Windows runtime |

**Closest to Done:** SHELL-3 and SHELL-2 — each needs a single live pass with
no further code. AI-19 still needs real code plus a live provider.

### Explicitly out of scope for 1.0 (do not work on)

- Win11 modern primary-menu `IExplorerCommand` sparse package (the deferred
  half of #114) — 2.0.
- OCR bounding-box geometry capture (the deferred half of #116) — 2.0.
- macOS Finder (#115) — blocked on the macOS port (#42).
