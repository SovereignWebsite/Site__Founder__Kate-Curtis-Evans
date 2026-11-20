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
