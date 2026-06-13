# Publishing Browse, Confirmation, and Remote Identity Planning

Date: 2026-06-12
Status: planning only
Scope: no code changes

## Purpose

This note captures a focused planning review of four related publishing concerns observed after the first publishing slices landed:

- drafts are not reliably visible in browse
- loading posts and pages together can time out on large servers
- publishing write actions need stronger confirmation and result feedback
- opened remote items need better title/tab identity in the editor

This note is intentionally framework-oriented. WordPress is the first researched provider, but the recommendations below are designed to remain usable across future publishing platforms.

## Research Inputs

Primary source review used current official WordPress developer documentation:

- [Posts REST API reference](https://developer.wordpress.org/rest-api/reference/posts/)
- [Pages REST API reference](https://developer.wordpress.org/rest-api/reference/pages/)
- [REST API pagination guide](https://developer.wordpress.org/rest-api/using-the-rest-api/pagination/)

Important documented behaviors:

- posts and pages list endpoints default to `status=publish`
- posts and pages support explicit `status` filtering
- collection endpoints are expected to be paginated
- `per_page` is capped and large collections should be assembled through multiple requests
- response headers include total-item and total-page counts for paginated responses

Inference from those sources:

- if Quill does not explicitly ask for non-published statuses, drafts may be absent even when the connection has permission to see them
- if Quill treats browse as a one-shot fetch across multiple content kinds, large sites will predictably hit timeout or performance pain

## Problem Breakdown

## 1. Draft Visibility

Current product symptom:

- a user can create a draft, then fail to see it in the browse surface

Most likely explanation:

- the current browse contract is too close to the default WordPress collection behavior, where listing defaults to published items unless status is requested explicitly

Provider-neutral planning takeaway:

- Quill cannot treat "browse content" as equivalent to "browse published content" unless the UI and framework deliberately scope it that way
- the framework needs an explicit concept of browse status scope

Planning recommendation:

- define browse around content state, not only content type
- at minimum, support a clear draft-including mode
- make status scope visible in the browse experience rather than hidden in provider defaults

Recommended product wording review:

- if the surface is meant to show drafts and published items, the title or filter language should say so plainly
- if the surface is intentionally publish-only, draft creation should not lead users to expect immediate visibility there

## 2. Timeouts on Large Sites

Current product symptom:

- requesting both posts and pages together can time out

Possible causes:

- two separate provider requests being treated as one blocking step
- too many items per request
- sites with large numbers of posts/pages
- slow hosting or plugin-heavy WordPress installations
- Quill waiting for all requested content kinds before surfacing anything useful

Provider-neutral planning takeaway:

- large content collections are a framework concern, not just a WordPress concern
- future providers may use:
  - page-based pagination
  - cursor-based pagination
  - continuation tokens
  - server-side search-only browsing

Planning recommendation:

- move from one-shot browse to staged browse
- normalize the framework around partial results
- let content kinds load independently where the provider model supports that

Recommended browse-scaling behavior:

1. let the user browse a narrower initial scope
   - posts only
   - pages only
   - both
2. request one content kind at a time internally even if the user chose both
3. show partial success if one kind loads and the other times out
4. surface retry language that names the failed slice
5. use provider pagination as a first-class part of the browse model
6. avoid assuming every provider can return “everything” cheaply

Product benefits:

- faster perceived response on large sites
- fewer all-or-nothing failures
- clearer error reporting
- better path to future providers

## 3. Confirmation and Result Feedback

Current product concern:

- publishing actions may not provide strong enough confirmation that the action actually happened

Why this matters:

- publishing is a trust-sensitive workflow
- users need explicit, unambiguous confirmation that a network write succeeded or failed, especially in an accessibility-first product where clear non-visual feedback is part of the core trust model
- “silent success” is product risk, not polish debt

Planning recommendation:

- standardize publishing confirmation into two stages:
  - pre-send confirmation
  - post-send result confirmation

Actions that should use the same confirmation model:

- create post draft
- create page draft
- update remote content
- future publish/promote actions
- future schedule actions

Minimum result payload to communicate after success:

- target site
- content kind
- resulting state
- content title
- remote URL when available

Failure guidance should communicate:

- what action failed
- whether anything partial may have happened
- what the user can do next

Accessibility and governance implications:

- use plain language
- do not rely on subtle status-bar-only feedback for trust-critical writes
- prefer existing standard confirmation patterns unless a richer governed dialog becomes clearly necessary

## 4. Remote Item Identity in the Editor

Current product concern:

- opened remote items still feel like anonymous unsaved documents in the editor shell

Why this matters:

- the title bar and tab name are part of navigation, orientation, and confidence
- if the user opens a remote page called “About” or “Quarterly Report,” the editor should help reflect that identity clearly

Planning options:

1. Tab-title override only
   - simplest UI improvement
   - least “file-like”
2. Synthesized temporary local file name
   - better parity with current editor title behavior
   - risk of implying a stronger local-file contract than really exists
3. Combined model
   - tab/title reflects remote title
   - remote/source metadata remains the authoritative linkage layer

Recommended direction:

- separate UI identity from storage identity
- let the shell display a remote-title-aware identity without pretending the item is a normal saved local file
- if a temp-backed representation is introduced later, it should exist to improve shell behavior, not to replace the remote metadata contract

## Provider-Neutral Framework Guidance

To keep the publishing architecture portable beyond WordPress, Quill should treat browse and write state using generic concepts:

- content kind
- content status
- pagination unit
- partial result state
- timeout state
- write intent
- write result
- remote identity

WordPress-specific implementation details can continue to live in the provider client, but the product and framework contract should not assume:

- WordPress names for statuses
- posts/pages as the only content kinds
- page-based pagination as the only paging model
- one endpoint per content kind

## Recommended Next Planning Sequence

1. Browse contract revision
   - define status visibility and default browse scope
   - define staged loading and partial-result rules
2. Confirmation contract revision
   - define a single publishing result-feedback model across all write actions
3. Remote identity design
   - define how opened remote items should appear in tabs/title bars without lying about local file state

## Recommended Next Coding Order After Planning

1. Browse scaling plus draft visibility
2. Confirmation/result feedback standardization
3. Remote item identity improvements

This order is recommended because browse correctness and trust feedback are more product-critical than title-bar polish.
