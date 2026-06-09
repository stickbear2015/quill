# Research Alchemist

The **Research Alchemist** is a showcase Quillin for QUILL that synthesizes scattered notes from multiple files into a structured, attributed list inside your current document. It demonstrates how a Quillin can use the `fs.read` capability -- declared in the manifest and disclosed to the user at install time -- to read files from a designated folder and pull their content into the editor.

## The problem it solves

Writers and researchers accumulate notes in many places: a quote copied from a source into a text file, a fragment of an idea in a Markdown note, a key fact stored with its citation. These fragments live in separate files because they came from separate sources. When it is time to write, the first step is always the same: open each file, find the relevant lines, copy them to a scratch document, note where each one came from.

That consolidation step is tedious, error-prone, and invisible to screen reader users who have to navigate each file individually. Research Alchemist automates it entirely. Point it at a folder of notes, run one command, and every bullet point or key fact is collected and inserted into your document with its source file and line number attached -- ready to read, sort, or delete.

## How it works

The Quillin scans a folder named `quill_research` in your home directory. It reads every `.txt` and `.md` file in that folder and extracts every line that starts with a bullet (`-` or `*`) or a key-value pattern (`Key:`). Each extracted line is tagged with its source filename and line number so you can trace it back later. The compiled list is inserted at the cursor as a formatted section, and the screen reader announces how many items were found across how many files.

The result in your document looks like this:

```
--- Research Siphon Results ---
• [chapter1_notes.md:4] - The human ear can distinguish about 1,400 pitches.
• [chapter1_notes.md:7] - Key: First deaf school in US founded 1817.
• [source_interviews.txt:12] * "The interface never told me where I was." -- participant 3
• [source_interviews.txt:18] * "I had to count keypresses just to navigate." -- participant 7
```

## Setup

1. Create a folder named `quill_research` in your home directory.
   - Windows: `C:\Users\YourName\quill_research`
   - macOS: `~/quill_research`
2. Add `.txt` or `.md` files to the folder. One file per source or topic is a natural organization, but any structure works as long as the notes are in the same directory.
3. Format your notes so extractable lines start with `-`, `*`, or `Key:`. Lines that do not start with these are skipped, so you can include headings and prose in the same file without having them appear in the siphon output.

## How to use it

1. Open QUILL and position the cursor where you want the siphoned notes inserted.
2. Open the **Tools** menu and choose **Siphon Knowledge**.
3. The Quillin scans the `quill_research` folder. When done, the screen reader announces *"Siphoned N items from M files."*
4. The formatted list is inserted at the cursor. Read through it, delete lines you do not need, and begin writing.

If the `quill_research` folder does not exist, the screen reader announces *"Research directory not found. Please create ~/quill_research"* and nothing is inserted. If the folder exists but contains no matching lines, it announces *"No research notes found in the directory."*

## Quillin capabilities used

| Capability | Purpose |
| --- | --- |
| `fs.read` | Read `.txt` and `.md` files from the `quill_research` folder |
| `editor.write` | Insert the compiled note list at the cursor |
| `ui.announce` | Speak the item count and any error conditions |
| `ui.command` | Register the "Siphon Knowledge" menu command |

The `fs.read` capability is a **consent-gated capability**: when you install this Quillin, QUILL discloses that it will read files from your filesystem and asks you to confirm. No file access happens silently. The Quillin reads only from the designated folder; it does not traverse your whole filesystem.

## Files

- `manifest.json` - the `quill.extension/1` manifest declaring `fs.read` and the Tools menu placement.
- `extension.py` - the `siphon_knowledge` handler that scans the folder and builds the output.
- `README.md` - this file.

## Extending the alchemist

The showcase version uses a fixed folder path and a simple line-start heuristic. A production version could:

- Use the `storage` capability to let you configure the folder path through the Quillin itself, persisting the preference between sessions
- Use the `ui.choices` capability to show a list of discovered files and let you choose which ones to include before inserting
- Support nested subdirectories (one folder per project or source)
- Let you define custom extraction patterns beyond `-`, `*`, and `Key:`
- Use `ui.status` to show progress as large folders are scanned
- Use `net` to fetch notes from a remote service (such as a synced note app's API) in addition to local files

The pattern -- read a collection of files, extract structured content, insert an attributed list, announce the summary -- applies to many research and writing workflows beyond simple note siphoning.
