# Ghostwriter's Mirror

The **Ghostwriter's Mirror** is a showcase Quillin for QUILL that transforms the tone and voice of selected text. It demonstrates how a Quillin can read a selection, apply a word-level transformation using a pure Python mapping, and replace the selection in a single undoable step -- all without touching anything outside that selection.

## The problem it solves

Tone is one of the hardest things to revise. When you need to make a casual draft sound professional, or want to hear how your text reads in a completely different register, the changes are rarely structural -- they live in individual word choices, phrasing habits, and the cumulative weight of small substitutions that are easy to miss on a manual pass.

The usual workflow is: read through the selection, mentally flag words that break the target register, fix them one by one, re-read to check. That process is slow, and every re-read introduces a chance to miss something. Ghostwriter's Mirror does the scan and substitution in one operation, then lets you listen to the result and undo it instantly if the output is not right.

The Quillin is deliberately non-destructive: it replaces only the current selection, your surrounding document is never touched, and a single Undo (Ctrl+Z) restores the original.

## Personas

**Legal Formalist.** Replaces informal words with formal equivalents suited to professional documents, legal writing, or business correspondence.

| Original | Transformed |
| --- | --- |
| hello | Greetings |
| thanks | We express our gratitude |
| bad | suboptimal |
| fix | rectify |
| idea | proposition |
| help | assistance |

**Victorian Poet.** Replaces everyday words with dramatically romanticized equivalents suited to evocative, creative, or literary writing.

| Original | Transformed |
| --- | --- |
| hello | Hail, traveler |
| thanks | My heart overflows with thanks |
| bad | woeful |
| fix | mend |
| idea | whisper of inspiration |
| help | succor |

Words not in the mapping pass through unchanged, so the transformation is always incremental -- partial replacement of known words, not a rewrite of unknown ones.

## How to use it

1. In QUILL, select a sentence or paragraph you want to transform. The selection can be as small as a phrase or as large as several paragraphs.
2. Open the **Format** menu.
3. Choose **Mirror as: Legal Formalist** for a formal, professional tone, or **Mirror as: Victorian Poet** for a dramatic, literary tone.
4. The selected text is replaced instantly. The screen reader announces *"Text mirrored as Legal Formalist."* (or the Poet variant).
5. Listen to the result. If it is not what you wanted, press Ctrl+Z to undo and restore the original.

If you activate either command with no text selected, the screen reader announces *"Please select some text to mirror."* and the document is unchanged.

## Quillin capabilities used

| Capability | Purpose |
| --- | --- |
| `editor.read` | Read the current selection |
| `editor.write` | Replace the selection with the transformed text |
| `ui.announce` | Speak the confirmation or the no-selection warning |
| `ui.command` | Register both mirror commands in the Format menu |

No filesystem, network, clipboard, or storage access. The entire transformation is a pure in-memory dictionary lookup over the selected text.

## Files

- `manifest.json` - the `quill.extension/1` manifest with both commands under Format.
- `extension.py` - the `apply_mirror` function and both handler registrations.
- `README.md` - this file.

## Extending the mirror

The showcase mapping is intentionally small -- a handful of words to demonstrate the pattern clearly. A production version could:

- Use larger curated vocabulary lists (hundreds or thousands of entries per persona)
- Add more personas: Academic, Journalist, Children's Author, Technical Manual
- Preserve case: if the original word was capitalized, capitalize the replacement
- Use the `storage` capability to let users add their own mapping entries and persist them between sessions
- Use the `ui.choices` capability to show a dialog listing available personas instead of separate menu items, so adding new personas does not require new menu entries
- Use the `net` capability to send the selection to a language model API for more nuanced transformation, with per-action consent

The transformation pattern -- read selection, map word by word, replace selection, announce -- is reusable for any word-substitution problem: acronym expansion, jargon translation, controlled vocabulary enforcement.
