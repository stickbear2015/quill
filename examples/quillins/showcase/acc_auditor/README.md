# Accessibility Auditor

The **Accessibility Auditor** is a showcase Quillin for QUILL that helps writers catch common document accessibility problems before sharing their work. It is a demonstration of how Quillins can read document content, analyze it against a set of rules, and produce an actionable, screen-reader-friendly report without leaving the editor.

## The problem it solves

Writing accessible documents is deceptively easy to get wrong. Heading levels are easy to skip under deadline pressure, images often lose their descriptions when notes are rushed, and some punctuation habits that feel emphatic on the page create noisy, repetitive reading when spoken aloud. The people most likely to be affected by these issues are screen reader users receiving your document.

Traditional accessibility checkers require exporting your document, opening a separate tool, interpreting visual reports, and returning to the editor. That round-trip is friction. The Accessibility Auditor brings the check inside QUILL so you can audit and correct in one place, in one pass.

## What it checks

**Heading hierarchy.** QUILL documents frequently use Markdown-style headings (`#`, `##`, `###`). Skipping a level -- jumping from `#` to `###` without an intermediate `##` -- is one of the most common heading errors and one of the most disruptive for screen reader users navigating by heading. The auditor detects every such skip and reports the exact transition.

**Image markers without descriptions.** A common shorthand in drafts is to write `[Image]` as a placeholder. If those markers reach a final document without an `Alt:` description, any screen reader user encounters a meaningless label. The auditor flags every unresolved image marker.

**Redundant punctuation.** Strings like `!!!` or `???` are read character by character by many screen readers, producing a string of "exclamation mark, exclamation mark, exclamation mark" that interrupts flow and adds no information. The auditor catches these patterns and recommends simplifying them.

## How to use it

1. Open the document you want to review in QUILL.
2. Place the cursor where you want the report inserted -- typically the end of the document.
3. Open the **Tools** menu and choose **Audit Accessibility**.
4. If no issues are found, the screen reader announces: *"Accessibility Audit: No immediate issues found. Great work!"* -- nothing is inserted.
5. If issues are found, the screen reader announces the count (*"Audit complete. Found 3 accessibility issues."*) and a formatted report is inserted at the cursor:

```
--- Accessibility Audit Report ---
Issue 1: Heading Level Skip: Found ### after #
Issue 2: Found image marker without alternative text description.
Issue 3: Redundant punctuation detected (can be noisy for screen readers).
```

Each issue is numbered so you can navigate to it by ear, then go fix the underlying problem in the document.

## Quillin capabilities used

| Capability | Purpose |
| --- | --- |
| `editor.read` | Read the full document text to analyze |
| `editor.write` | Insert the formatted audit report at the cursor |
| `ui.announce` | Speak the result count immediately on completion |
| `ui.command` | Register the "Audit Accessibility" menu command |

This Quillin uses no filesystem access, no network access, and no clipboard access. Everything it needs is already in your open document.

## Files

- `manifest.json` - the `quill.extension/1` manifest declaring the command and its menu placement.
- `extension.py` - the Python handler that runs the three accessibility checks.
- `README.md` - this file.

## Extending the auditor

This showcase implements three simple rules and is intended as a starting point. A production version could add:

- Line numbers in the report for each issue, so you can jump directly to the problem location
- More heading rules (multiple H1s, no H1 at all)
- Link text checks ("click here" and "read more" are unhelpful to screen reader users)
- Table structure validation (missing header rows)
- Configurable rules stored via the `storage` capability so you can turn individual checks on or off

The pattern -- read document, analyze, insert report, announce summary -- transfers directly to any document quality rule you want to enforce.
