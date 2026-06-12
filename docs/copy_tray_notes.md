# Copy Tray: What Was Built and How It Feels

## What Was Built

Copy Tray is a nine-slot persistent clipboard integrated across QUILL's menu
bar, keyboard layer, dialog system, and system tray icon. Every slot holds text
that survives application restarts.

### Core model (`quill/core/copy_tray.py`)

A pure Python model with no wx dependency. `CopyTray` owns nine `TraySlot`
instances. Each slot has `text`, `label`, and `copied_at`. The model reads and
writes `copy_tray.json` in the QUILL data directory using `write_json_atomic`
(temp file + `os.replace`). A corrupt file causes a silent fresh start; it
never raises to the UI.

### UI mixin (`quill/ui/main_frame_copy_tray.py`)

`CopyTrayMixin` is mixed into `MainFrame`. Methods:

- `copy_to_tray_slot(n)` — copies the editor selection to slot n; announces
  slot number and text preview.
- `paste_from_tray_slot(n)` — inserts slot n text at cursor (or replaces
  selection); announces slot number and label.
- `open_copy_tray()` — opens the management dialog; pastes if the user chooses
  Paste and returns to the editor.
- `clear_all_tray_slots()` — Yes/No confirmation (default No); clears all nine
  slots on Yes.

### Dialog (`quill/ui/copy_tray_dialog.py`)

A resizable wx.Dialog with a ListBox and five action buttons. Each list row
shows slot number, optional label, and a 60-character preview. The list
receives focus on open. Buttons: Paste (Enter), Copy Selection Here, Set
Label..., Clear Slot, Close (Escape). Double-click pastes. Button states
update on every selection change: Paste and Clear Slot are disabled on empty
slots; Copy Selection Here is disabled when no editor text is selected.

### Keyboard bindings (`quill/core/keymap.py`)

| Key | Action |
| --- | --- |
| `Ctrl+Shift+1` through `Ctrl+Shift+9` | Paste from slot 1-9 |
| `Ctrl+Shift+Grave, Shift+1` through `Ctrl+Shift+Grave, Shift+9` | Copy selection to slot 1-9 |
| `Ctrl+Shift+Grave, X` | Open Copy Tray dialog |

The paste bindings use the number row with `Ctrl+Shift`. These keys were
confirmed free across the entire QUILL keymap. QUILL-key bare digits 1-6 are
heading shortcuts; adding Shift produces a distinct chord with no conflict.

All 20 commands (`edit.open_copy_tray`, `edit.clear_all_tray_slots`,
`edit.copy_to_tray_1..9`, `edit.paste_from_tray_1..9`) are registered in
the keymap and appear in the Command Palette. All are reassignable in the
Keymap Editor.

### Menu integration (`quill/ui/main_frame_menu.py`)

`Edit > Copy Tray` submenu with:
- Copy to Slot 1-9
- Paste from Slot 1-9
- Open Copy Tray...
- Clear All Tray Slots

The 18 per-slot items use dedicated `wx.NewIdRef()` IDs (`_id_copy_tray_slots`
and `_id_paste_tray_slots` arrays). Management commands are recirculated from
the power tools manifest via `_append_power_tools_copy_tray_items`.

### Power tools manifest (`quill/ui/main_frame_power_tools_menu.py`)

New `"copy_tray"` group with `edit.open_copy_tray` and
`edit.clear_all_tray_slots`. New recirculation helper
`_append_power_tools_copy_tray_items`. The 18 individual slot commands are also
registered in the manifest for Command Palette discoverability.

### System tray integration (`quill/ui/main_frame.py`)

The `_on_tray_right_click` method now builds a **Copy Tray** submenu listing
every occupied slot with its label (if any) and a 50-character text preview.
Clicking a slot calls `_tray_paste_slot(n)`, which restores the main window if
it is hidden, then pastes the slot content. If all slots are empty, the submenu
shows "(all slots empty)" as a disabled item. "Open Copy Tray..." is always
present at the bottom of the submenu.

### Documentation

- `docs/features/copy_tray.md` — complete feature reference with keyboard
  tables, dialog walkthrough, accessibility notes, and workflow tips.
- `docs/QUILL-PRD.md` — section 5.77 added with motivation, operations table,
  keyboard defaults, storage spec, accessibility guarantees, and implementation
  map.
- `docs/userguide.md` — "Copy Tray" section added in Writing and Editing,
  before "Copy With Source", with full keyboard tables and a tips block.

---

## The User Experience

### First encounter

You open QUILL to write a long document while researching from several other
sources. You read a quote you want to use, select it, and press
`Ctrl+Shift+Grave, Shift+1`. QUILL says "Copied to slot 1". You read another
fragment. `Ctrl+Shift+Grave, Shift+2`. "Copied to slot 2". A third. Slot 3.

You switch to your draft. Where you want the first quote, press `Ctrl+Shift+1`.
QUILL says "Pasted from slot 1" and the text is there. The system clipboard was
never disturbed. The other two quotes are still in their slots.

You close QUILL. Come back tomorrow. Slots 1, 2, and 3 still hold their
contents.

### Using labels

After a few days you decide to give slot 1 a permanent home: your email
signature. You open `Ctrl+Shift+Grave, X`, navigate to slot 1, press Set
Label..., type "signature", press Enter. Now when you paste, QUILL says "Pasted
from slot 1 (signature)". The slot is identifiable without looking at a screen.

### From the system tray

QUILL is minimized to the system tray while you read in another browser. You
right-click the QUILL icon. The menu shows:

```
Show Quill
Copy Tray  >
  1.  signature — Hi, I wanted to follow up...
  2.  Hello world...
  3.  import sys, os, pathlib...
  ...
  Open Copy Tray...
Sticky Notes...
Exit Quill
```

You click slot 3. QUILL restores its window and pastes the import block at
your cursor. You minimize again.

### Screen reader workflow

Press `Ctrl+Shift+5`. QUILL says "Slot 5 is empty." You know immediately
without opening a dialog or reading the screen. Select some text, press
`Ctrl+Shift+Grave, Shift+5`. "Copied to slot 5." Move elsewhere. Press
`Ctrl+Shift+5`. "Pasted from slot 5." Everything happened through voice, at
typing speed, with standard modifier+number chords.

---

## Future Directions: Double-Tap and Beyond

The user asked whether pressing a key twice quickly could trigger an alternative
action. For Copy Tray, the natural double-tap behaviour would be:

- **Single `Ctrl+Shift+N`** — paste from slot N immediately.
- **Double `Ctrl+Shift+N`** (two presses within ~300ms) — peek: QUILL speaks
  what is in slot N *without pasting* ("Slot 3: Hello world..."). This lets
  a screen-reader user verify a slot's content before committing to paste.

Implementing double-tap detection requires a timer in the QUILL-key prefix
state machine, a 300ms debounce, and a clear screen-reader announcement
pattern. It is architecturally clean and would make the Copy Tray even more
efficient for screen-reader-only workflows. This is noted here as a planned
enhancement, not yet implemented.

Other places in QUILL where double-tap patterns could add value:

- **Double QUILL key** (two presses of `Ctrl+Shift+Grave`) = open Copy Tray
  dialog, similar to how Windows `Win+V` opens clipboard history.
- **Double `F3`** = repeat the last Find All and jump to the next cluster of
  matches.
- **Double `Ctrl+Z`** = undo back to the last explicit save point.
- **Double `Ctrl+G`** = return to the previous location (ping-pong navigation).
- **Double `Escape`** = collapse all side panels and return focus to the editor.

These should be evaluated selectively — double-tap timing is sensitive and can
interfere with rapid typists. The patterns with the clearest benefit and the
lowest collision risk are: Copy Tray peek and QUILL-key-double-press for the
tray dialog.
