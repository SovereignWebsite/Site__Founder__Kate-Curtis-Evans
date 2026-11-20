# The behaviour policy

This site's agents follow an Agent Behaviour Policy, kept in the repository as policy/abp.json. Claude Code enforces the parts it can with deny rules in .claude/settings.json. Dinis Cruz asked for it on 20 November 2026: Kate's Claude can make changes, but is kept away from her wider Claude account and from the parts of the site she should not change.

## Kate's Claude (site@SovereignWebsite.kate)

**May change**, always with Kate's yes: site/**, issues/** (the board), docs/notes.md, docs/questions-for-kate.md, docs/sources.md, tools/**.

**Must not change**: site/CNAME and .github/** (the address and the publishing pipeline); .claude/**, policy/** and CLAUDE.md (its own rules); material/** (the record of the sources).

**Branch**: dev only. Never main, never a force-push, never deleting history or branches.

**Never**:

- use connectors or account tools outside this repository: email, calendar, drive, other repositories, other Claude sessions, scheduled tasks, environment settings, credentials or computer access;
- read, print or commit a key, token or password;
- invent a fact, figure, client or quote, or publish anything Kate has not said or approved;
- add cookies, tracking, analytics, third-party scripts, embeds or web fonts;
- publish a photo without its credit, or a photo of anyone other than Kate without their consent.

## What is enforced, and what is not

Claude Code blocks: edits to the protected paths; force-pushes, pushes to main and deleting branches; the account tools for other sessions, scheduled tasks, environments, credentials and computer access; and the Gmail, Google Drive and Google Calendar connectors. These rules apply in a Claude Code session on this repository alone. They do not apply in a project's threads, or in a session with several repositories.

Two things only Kate can do, in her Claude settings: turn off any connector she does not want this session to see, and keep this repository as the only one in the session. GitHub itself keeps main locked and dev free of deletions and force-pushes.

Changing a rule needs Kate and Dinis together.

## Two editors

By Dinis Cruz's word on 20 November 2026: "it's very important that we have two editors here". Kate edits through her own Claude; Dinis edits with his agents (kate-curtis-evans.b and the SovereignWebsite team). Both push to dev.

## Messages sent from the message page

Kate and Dinis can send requests from [the message page](message/index.html). Each message is sealed to the agent and signed with the sender's own key. Dinis asked that these requests be "quite limited to, for example, content and maybe even like tasks on the Kanban board, and not crazy stuff. Or maybe even add an image".

**Acted on only if** it is signed by Kate's or Dinis's published key (site/data/person-keys.json) and the signature checks.

**Allowed**:

- change words on the site (every design and site/index.md), keeping the site's rules: only what Kate or Dinis say, figures dated, no em dashes;
- add, move or close a task on the board;
- add or replace a photo sent with the message, with its credit and a description, hidden metadata removed;
- answer a question, by a reply on the message page.

**Refused**: anything touching the address, publishing, settings, policy or the source material; new scripts, trackers, embeds or cookies; deleting pages, designs or history; anything outside this repository (other repositories, accounts, email, payments); a photo of anyone other than Kate without their consent or without a credit; a request to change these rules.

**Unsigned or forged** messages are recorded as an id, a time and a length only: their words never reach the agent.

**Every change** is committed to dev with the message id in the commit, and the sender gets a reply, sealed to them, saying what changed or why not.
