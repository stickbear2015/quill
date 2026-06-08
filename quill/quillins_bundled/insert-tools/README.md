# Insert Tools (bundled Quillin)

A first-party, **bundled** Quillin (Tier C) that ships enabled inside QUILL. It
is a pure **Layer 1** snippet pack: three commands that insert the current date,
time, or both at the caret.

## Commands

| Command | Home | Inserts |
| --- | --- | --- |
| Insert Date | Insert | `${date}` - today's date in your configured format. |
| Insert Time | Insert | `${time}` - the current time in your configured format. |
| Insert Date and Time | Insert | `${date} ${time}`. |

## Capabilities

**None.** Layer 1 snippet expansion needs no capabilities, so this Quillin can
never read or write files, reach the network, or touch the clipboard. It is the
smallest possible illustration of a safe, additive contribution.

## Relationship to the built-in Insert Date/Time

QUILL keeps its built-in **Insert Date/Time** command, which honours the
`datetime_insert_format` setting in full. This Quillin is **additive**: it shows
how the same outcome is expressed as a zero-capability snippet contribution, and
it lets authors copy the pattern for their own date/time formats.
