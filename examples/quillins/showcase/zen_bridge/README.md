# Zen Focus Bridge

The **Zen Focus Bridge** is a showcase Quillin for QUILL that helps writers transition into a focused writing state by bridging the editor and the broader computing environment. It demonstrates how a Quillin can use the `net` capability -- disclosed to the user at install time -- to connect QUILL to external services and tools, turning the editor into a control surface for your whole writing environment.

## The problem it solves

Getting into a focused writing state takes more than opening a text editor. The environment around you -- notifications arriving, background apps demanding attention, ambient distractions -- competes for the same attention you are trying to direct at the page. Writers use different strategies to manage this: switching on Do Not Disturb, launching focus music, blocking social media, dimming the display, setting a Pomodoro timer. The problem is that setting up focus mode requires manual steps across multiple apps, and each step is an interruption of its own.

Zen Focus Bridge collapses this setup into a single command. One keypress or menu action announces the transition, marks your document with a session boundary, and can trigger any number of external environment changes. When you are done, a second command marks the end of the session and restores normal operation. The entire ceremony is keyboard-accessible and confirmed by the screen reader.

## What it does

**Activate Zen Sanctuary.** Opens the focus session. The screen reader announces *"Zen Sanctuary activated. Notifications silenced, focus music playing."* A visible marker is inserted at the cursor position so you know exactly when the focused session began:

```
[--- ZEN MODE ACTIVE ---]
```

This marker serves as a session boundary in your document. When reviewing a writing session later, you can see exactly where focused work started.

**Exit Zen Sanctuary.** Closes the focus session. The screen reader announces *"Leaving the Zen Sanctuary. Welcome back to the noise."* A closing marker is inserted:

```
[--- ZEN MODE EXITED ---]
```

Both commands appear in the **View** menu and can be bound to hotkeys in your QUILL configuration.

## What a production version can do

The showcase simulates the environment transition (announcement + marker). A production version wired to real services could do any of the following using the `net` capability:

- **Smart lighting:** Call a Philips Hue, LIFX, or Home Assistant API to set a focus-mode light color or brightness.
- **Do Not Disturb:** Call a webhook or local API exposed by your OS or a notification manager app to silence incoming alerts.
- **Focus music:** Trigger a Spotify, Apple Music, or VLC local API to start a designated focus playlist.
- **Pomodoro timers:** Call a time-tracking service or start a local timer app via a webhook.
- **Communication status:** Update your Slack, Teams, or Discord status to "In a writing session" via those apps' APIs.
- **Custom automation:** Post to a local Zapier webhook, an n8n workflow, or any HTTP endpoint that triggers your preferred focus setup.

Each network call goes through QUILL's per-action consent gate: the first time the Quillin tries to reach an external service, QUILL asks you to confirm. You can see exactly what is being contacted and approve or deny it. Nothing reaches the network silently.

## How to use it

1. Open QUILL and begin or open the document for your writing session.
2. Open the **View** menu and choose **Activate Zen Sanctuary** to begin the session.
3. The screen reader confirms activation. A session-start marker appears in the document.
4. Write. The marker in the document records when the focused work began.
5. When the session is complete, open the **View** menu and choose **Exit Zen Sanctuary**.
6. The screen reader confirms deactivation. A session-end marker appears in the document.

## Quillin capabilities used

| Capability | Purpose |
| --- | --- |
| `ui.command` | Register the Activate and Exit commands in the View menu |
| `editor.write` | Insert the session boundary markers at the cursor |
| `ui.announce` | Speak the activation and deactivation confirmations |
| `net` | (Production) Connect to external services via HTTP to trigger environmental changes |

The `net` capability is a **consent-gated capability**: QUILL discloses that this Quillin can make outbound network requests and asks for your confirmation before any request is made. In the showcase version, no actual network calls are made; the capability is declared to show the design pattern.

## Files

- `manifest.json` - the `quill.extension/1` manifest declaring both commands under View, with the `net` capability.
- `extension.py` - the `activate_zen` and `deactivate_zen` handlers.
- `README.md` - this file.

## Extending the bridge

The focus session pattern is simple enough to adapt for any "mode transition" in a writing workflow:

- **Draft mode / Edit mode:** Insert markers that distinguish generative writing passes from revision passes.
- **Reading mode:** Trigger an OS accessibility setting or font size change that makes the document easier to review.
- **Session logging:** Use the `storage` capability to record session start and end times, then insert a summary (total session time, word count change) when the session ends.
- **Team coordination:** Use `net` to post a status update to a shared channel so collaborators know you are in a writing block and should not expect quick responses.

The broader point this Quillin demonstrates: a Quillin does not have to operate only on the document. It can use the document as a control surface and the `net` capability as a bridge to the outside world, turning QUILL into a command center for your writing environment.
