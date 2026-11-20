# What you must not touch

The full policy is in [policy.md](../policy.md) (and policy/abp.json). In short:

## In the repository

You may change site/**, docs/notes.md, docs/questions-for-kate.md, docs/sources.md and tools/**, always with Kate's yes.

You must not change:

- **site/CNAME and .github/**: the address and the publishing pipeline. A wrong change takes the site offline.
- **.claude/**, policy/** and CLAUDE.md**: the rules for this session. A session must not rewrite its own limits.
- **material/**: the record of what the site was built from.

Claude Code enforces most of these with deny rules in .claude/settings.json. If Kate wants one of them changed, she asks Dinis Cruz.

## In Kate's Claude account

This session works on this one repository. Do not use connectors or account tools for anything else: no email, calendar or drive; no other repositories; no reading or starting other Claude sessions; no scheduled tasks; no changes to environments, credentials or computer access. If Kate asks for something outside the site, tell her it is outside this session's job and suggest a separate conversation.
