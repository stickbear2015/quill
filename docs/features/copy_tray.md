# Copy Tray

## Overview

Copy Tray gives you nine independently addressable clipboard slots. Each slot
holds a piece of text that you copy there explicitly. Slots survive application
restarts — their contents are written to disk automatically so nothing is lost
when you close and reopen QUILL.

Unlike the system clipboard, which is shared with every other application and
holds only the most recently copied item, Copy Tray slots are exclusive to
QUILL and hold their contents until you explicitly replace or clear them. This
makes Copy Tray well suited for accumulating related fragments across a long
editing session: quotes from multiple sources, code snippets, address blocks,
standard disclaimers, or any text you paste repeatedly.

## Keyboard Access

### Paste from a slot

Hold `Ctrl+Shift` and press a number key. That is all.

| Key | Action |
| --- | --- |
| `Ctrl+Shift+1` | Paste from slot 1 at cursor |
| `Ctrl+Shift+2` | Paste from slot 2 at cursor |
| `Ctrl+Shift+3` | Paste from slot 3 at cursor |
| `Ctrl+Shift+4` | Paste from slot 4 at cursor |
| `Ctrl+Shift+5` | Paste from slot 5 at cursor |
| `Ctrl+Shift+6` | Paste from slot 6 at cursor |
| `Ctrl+Shift+7` | Paste from slot 7 at cursor |
| `Ctrl+Shift+8` | Paste from slot 8 at cursor |
| `Ctrl+Shift+9` | Paste from slot 9 at cursor |

If a selection is active when you paste, the pasted text replaces it.
If the slot is empty, QUILL announces "Slot N is empty".

### Copy to a slot

Hold the QUILL key (`Ctrl+Shift+Grave`), release, then press `Shift+digit`.
The QUILL-key bare digits 1-6 are heading shortcuts; adding Shift is a distinct
binding with no conflict.

| Key | Action |
| --- | --- |
| `Ctrl+Shift+Grave, Shift+1` | Copy selection to slot 1 |
| `Ctrl+Shift+Grave, Shift+2` | Copy selection to slot 2 |
| `Ctrl+Shift+Grave, Shift+3` | Copy selection to slot 3 |
| `Ctrl+Shift+Grave, Shift+4` | Copy selection to slot 4 |
| `Ctrl+Shift+Grave, Shift+5` | Copy selection to slot 5 |
| `Ctrl+Shift+Grave, Shift+6` | Copy selection to slot 6 |
| `Ctrl+Shift+Grave, Shift+7` | Copy selection to slot 7 |
| `Ctrl+Shift+Grave, Shift+8` | Copy selection to slot 8 |
| `Ctrl+Shift+Grave, Shift+9` | Copy selection to slot 9 |

You must have text selected. QUILL announces the slot number and a text
preview: "Copied to slot 2".

### Management

| Key | Action |
| --- | --- |
| `Ctrl+Shift+Grave, X` | Open Copy Tray dialog |

All bindings are reassignable in `App > Preferences > Keyboard` or the Command
Palette (`app.preferences`).

## Using the Edit Menu

All commands are available in `Edit > Copy Tray`. The submenu contains:

- `Copy to Slot 1` through `Copy to Slot 9` — copy the current selection
- `Paste from Slot 1` through `Paste from Slot 9` — paste at the cursor
- `Open Copy Tray...` — open the management dialog
- `Clear All Tray Slots` — clear all slots after confirmation

## Using the System Tray Icon

Right-click the QUILL icon in the system notification area (bottom-right
taskbar area). The context menu includes a **Copy Tray** submenu that lists
every occupied slot with its label (if any) and a text preview. Clicking a slot
pastes its content into the currently active QUILL document. This lets you
paste from the tray without bringing the main window to the front.

## Using the Dialog

Open the dialog with `Ctrl+Shift+Grave, X`, `Edit > Copy Tray > Open Copy
Tray`, or the Command Palette (`edit.open_copy_tray`). The dialog shows all
nine slots in a list. Each row displays:

- The slot number
- An optional label
- A preview of the stored text (empty slots show `(empty)`)

Navigate the list with the arrow keys. The following buttons appear below the
list:

- **Paste** (Enter or double-click) — paste the selected slot's text at the
  cursor position and close the dialog. Disabled when the selected slot is
  empty.
- **Copy Selection Here** — copy the current editor selection into the selected
  slot and refresh the list. Disabled when no text is selected in the editor.
- **Set Label...** — open a text-entry prompt to name the selected slot. Labels
  appear in all slot listings and in screen-reader announcements.
- **Clear Slot** — empty the selected slot. Disabled when already empty.
- **Close** (Escape) — close the dialog without pasting.

## Labelling Slots

Slot labels are optional but recommended for any slot you use regularly. A
label makes the slot identifiable in the dialog and in every spoken
announcement. Labelling slot 1 "signature" means you will hear "Pasted from
slot 1 (signature)" instead of "Pasted from slot 1".

To set a label:

1. Open the Copy Tray dialog.
2. Select the slot you want to label.
3. Press `Set Label...`.
4. Type the label and press Enter.

Labels are persisted alongside slot text and survive restarts.

## Accessibility Notes

- Every Copy Tray operation announces its result through QUILL's screen-reader
  interface. Copy, paste, clear, and label operations all produce spoken
  feedback.
- The slot list in the dialog receives initial focus when the dialog opens.
- Slot labels, when set, are included in every announcement.
- Empty slots are clearly identified as `(empty)` in all contexts.
- The `Clear All Tray Slots` confirmation dialog defaults to No to prevent
  accidental data loss.
- The `Ctrl+Shift+N` paste scheme is designed for screen reader users: one
  familiar chord activates slot N instantly, no menu navigation required.

## Tips

- **Research accumulator.** Assign each tray slot to a document section. Copy
  a relevant excerpt to each slot as you read through a source, then paste
  them in order when drafting.
- **Code boilerplate.** Keep import blocks, standard headers, and closing
  patterns in labelled slots for one-chord insertion.
- **Cross-document paste.** Copy a phrase to a tray slot, switch documents,
  paste from the tray — the system clipboard is untouched.
- **Persistent library.** Slots survive restarts. Build a set of standard
  fragments you reach for daily.
- **System tray access.** Paste into any QUILL document directly from the
  notification-area icon without bringing the window to the front.
