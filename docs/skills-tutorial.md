# Writing Skills for QUILL — A Tutorial

This guide teaches you to write, validate, and share `.sqp` (Skill Quill Pack) files.
A skill is a multi-step AI workflow written in plain Markdown. If you can write a
prompt, you can write a skill.

---

## 1. What is a skill?

A QUILL prompt is one instruction. A skill is a conversation — a series of instructions
where each step can see what the previous step produced.

You might use a skill when:

- You want to analyse your text first, then act on the analysis.
- You want to gather information in one step and draft with it in the next.
- You want to check a condition (is this a question or a statement?) and take a
  different path depending on the answer.
- You want to repeat the same sub-task at a higher quality by giving the model
  context it built in an earlier step.

---

## 2. Your first skill

Create a file called `my-first-skill.sqp` and open it in QUILL.

```markdown
---
schema: quill.skill/1
name: Explain Then Simplify
description: Explains the selected text in plain terms, then simplifies it further.
author: Your Name
version: 1.0.0
---

# Step 1: Explain

Explain the following text as if the reader has no prior knowledge. Use simple
vocabulary and short sentences. Aim for 50-80 words.

Text to explain:
{selection}

# Step 2: Simplify further

The explanation below is good, but we need it even simpler. Rewrite it so a
twelve-year-old would understand it immediately. Keep the core meaning.

Explanation to simplify:
{step1.output}

```output
format: text
label: Plain-language explanation
accept_into: clipboard
```
```

Save the file, then validate it:

```powershell
python -m quill.tools.sqp_validator my-first-skill.sqp
```

You should see:

```
my-first-skill.sqp: OK
```

---

## 3. Adding parameters

Parameters let users choose options before the skill runs. QUILL shows a small dialog
collecting the choices before step 1 begins.

Add a reading-level choice to the skill above:

```markdown
---
schema: quill.skill/1
name: Explain Then Simplify
description: Explains and simplifies selected text at a chosen reading level.
author: Your Name
version: 1.0.0
parameters:
  - name: level
    label: Target reading level
    type: choice
    choices: [Grade 4, Grade 6, Grade 8]
    default: Grade 6
---

# Step 1: Explain

Explain the following text so it is accessible at {parameters.level} reading level.
Use simple vocabulary and short sentences. Aim for 50-80 words.

Text to explain:
{selection}

# Step 2: Simplify further

Rewrite the explanation below to be even clearer. Target: {parameters.level}.
Keep the core meaning intact.

{step1.output}

```output
format: text
label: Plain-language explanation
accept_into: clipboard
```
```

Now the parameter `{parameters.level}` is available in both steps. The value
comes from the user's choice in the dialog.

**Parameter types.**

| Type | UI control | Example |
| --- | --- | --- |
| `text` | Single-line text field | A keyword or name |
| `multiline` | Multi-line text area | A block of context |
| `choice` | Drop-down list | Reading level, tone, language |
| `bool` | Checkbox | Include citations: yes/no |
| `number` | Numeric field | Word count target |

---

## 4. Using the input block

Long texts can clutter the prompt. The `input` block appends data after the
instruction text, keeping the step prose readable:

```markdown
# Step 1: Extract key claims

Read the following document and list the five most important claims it makes.
Number each claim. One sentence per claim.

```input
{document}
```
```

Without the `input` block you would write:

```markdown
# Step 1: Extract key claims

Read the following document and list the five most important claims it makes.
Number each claim. One sentence per claim.

Document:
{document}
```

Both are equivalent; the `input` block is just cleaner when the data is long.

---

## 5. Conditional branching

Use a `condition` block to route execution based on a step's output.

```markdown
# Step 1: Detect intent

Read the following text. Is it asking a question, or making a statement?
Answer with exactly one word: "question" or "statement".

```input
{selection}
```

```condition
if: "{step1.output}" contains "question"
then: step2
else: step3
```

# Step 2: Answer the question

Answer this question clearly and concisely:
{selection}

```output
format: text
label: Answer
accept_into: clipboard
```

# Step 3: Expand the statement

Expand the following statement into a full paragraph with supporting detail:
{selection}

```output
format: text
label: Expanded statement
accept_into: clipboard
```
```

**How it works.** After step 1 runs, QUILL checks the condition: if the output
contains "question", it jumps to step 2. Otherwise, it jumps to step 3. Whichever
step runs last is the one that produces the output.

**Supported operators.**

| Operator | Matches when |
| --- | --- |
| `contains` | Subject contains value (case-insensitive) |
| `equals` | Subject exactly matches value (case-insensitive) |
| `starts_with` | Subject starts with value |
| `ends_with` | Subject ends with value |
| `length_gt` | Subject length > number |
| `length_lt` | Subject length < number |
| `is_empty` | Subject is blank |

---

## 6. Controlling the output

The `output` block on the last step controls what happens to the result.

```markdown
```output
format: text
label: Rewritten paragraph
accept_into: selection
```
```

**`format`:** `text` (default), `list` (AI should return a bulleted or numbered
list), `json` (AI should return valid JSON).

**`accept_into`:** What happens when the user presses Accept in the result dialog.
- `selection` — replaces the current editor selection.
- `clipboard` — copies to clipboard.
- `none` — shows read-only (default).

The `label` appears in the result dialog header so the user knows what they are
reviewing.

---

## 7. A complete example — Accessible Rewrite

Here is the bundled "Accessible Rewrite" skill in full, with commentary.

```markdown
---
schema: quill.skill/1
name: Accessible Rewrite
description: Rewrites selected text for plain-language accessibility.
author: QUILL Project
version: 1.0.0
parameters:
  - name: reading_level
    label: Target reading level
    type: choice
    choices: [Grade 6, Grade 8, Grade 10, No target]
    default: Grade 8
---

# Step 1: Analyse accessibility issues

Review the following text for plain-language accessibility issues. List the
problems as a numbered list. Focus on: sentence length (over 25 words), passive
voice, unexplained jargon or acronyms, abstract nouns where concrete ones would
serve better, and complex nested clauses. Be concise — one clear problem per
line. If the text has no issues, say "No issues found."

```input
{selection}
```

# Step 2: Rewrite for accessibility

Rewrite the text below to fix the issues identified in Step 1. Requirements:
- Target reading level: {parameters.reading_level}
- Preserve all factual content
- Do not add new information

Original text:
{selection}

Issues to fix:
{step1.output}

```output
format: text
label: Rewritten text
accept_into: selection
```
```

**Step 1** analyses the text and produces a numbered list of issues.
**Step 2** uses `{step1.output}` (the issue list) as context alongside the
original text, so the model knows exactly what to fix. The output replaces the
selection when the user presses Accept.

---

## 8. Validating your skill

Always run the validator before sharing:

```powershell
python -m quill.tools.sqp_validator my-skill.sqp
```

For extra checks:

```powershell
python -m quill.tools.sqp_validator my-skill.sqp --strict
```

`--strict` also warns if `description` or `author` are missing.

**Common errors and how to fix them.**

| Error | Cause | Fix |
| --- | --- | --- |
| `schema must be 'quill.skill/1'` | Missing or wrong schema | Add `schema: quill.skill/1` to front matter |
| `front matter must include 'name'` | No `name:` field | Add `name: My Skill` |
| `must have at least one step` | No `# Heading` lines | Add at least one `# Step N:` heading |
| `{step3.output} references a step that hasn't run yet` | Forward reference | Steps can only reference outputs from earlier steps |
| `unknown parameter 'tone'` | Used `{parameters.tone}` but didn't declare it | Add `tone` to the `parameters` list in front matter |
| `output format 'xml' is invalid` | Bad `format:` value | Use `text`, `list`, or `json` |

---

## 9. Sharing skills

A `.sqp` file is a plain text file — share it the same way you share any document.

**Via the Skill Library.** When someone receives your `.sqp` file, they import it
through `Tools > AI Assistant > Skill Library > Import .sqp`.

**Via a Quillin.** If you maintain a Quillin, add your `.sqp` files to the Quillin
directory. QUILL discovers them automatically at Skill Library load time.

**As a standalone file.** A `.sqp` file is self-contained. The recipient can also
open it in QUILL's editor to read, understand, and customise every step.

---

## 10. Skill authoring tips

**Keep step instructions specific.** "List the five most important claims" is
better than "What are the claims?" The model follows precision.

**Name outputs explicitly.** Instead of "Summarise the following", write "Write a
one-sentence summary of the following text. Return only the summary sentence,
no preamble." This ensures `{step1.output}` contains exactly what you expect.

**Test with short text first.** Paste two or three sentences into the editor,
select them, and run the skill. Short inputs are faster and errors are easier to
trace.

**Use `input` blocks for long data.** If your selection might be a full document,
put `{document}` in an `input` block rather than inline in the prompt. The step
reads more cleanly.

**Put conditions after a clean-detection step.** If you are branching on whether
text is a question, a statement, a list, or something else, dedicate step 1 to
just that classification. Ask for a single-word answer. The more constrained the
output, the more reliably the condition evaluates.

**Use the output block's `accept_into` intentionally.** If the skill rewrites the
selection, use `accept_into: selection`. If it produces supplementary content
(meeting summary, outline), use `accept_into: clipboard` so the user can paste
where they choose. Use `none` for informational skills (grammar analysis,
readability score) where the result is read but not inserted.

---

## Reference card

**Front matter fields.**

| Field | Required | Default |
| --- | --- | --- |
| `schema: quill.skill/1` | yes | — |
| `name: ...` | yes | — |
| `description: ...` | recommended | `""` |
| `author: ...` | recommended | `""` |
| `version: ...` | no | `1.0.0` |
| `parameters: [...]` | no | `[]` |

**Variables.**

| Variable | Value |
| --- | --- |
| `{selection}` | Selected editor text (full document if nothing selected) |
| `{document}` | Full document text |
| `{title}` | Document title |
| `{clipboard}` | Clipboard text at skill-start time |
| `{stepN.output}` | Output from step N (must be a lower-numbered step) |
| `{parameters.name}` | Value of a declared parameter |

**Fenced block types.**

| Block | Where | Purpose |
| --- | --- | --- |
| `` `input` `` | Any step | Appends data to the prompt |
| `` `condition` `` | Any step | Branch to `then`/`else` step after this step runs |
| `` `output` `` | Last step | Controls format, label, accept_into |
| `` `use-prompt` `` | Any step | Delegates to a named Prompt Library prompt |

**Condition operators.** `contains`, `equals`, `starts_with`, `ends_with`,
`length_gt`, `length_lt`, `is_empty`.

**Output formats.** `text`, `list`, `json`.

**Output accept_into values.** `selection`, `clipboard`, `none`.
