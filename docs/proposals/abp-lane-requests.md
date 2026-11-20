# Proposal: add two editors and the message limits to policy/abp.json

kate-curtis-evans.b, 20 November 2026. Waiting for Dinis: this session's permission check refuses edits to policy/** (the protected path), so this is written here for Dinis to apply or approve. The human-readable version is already on site/admin/policy.md.

Add to policy/abp.json:

```json
"editors": "Two editors (Dinis, 20 Nov 2026): Kate through her own Claude (site@SovereignWebsite.kate), and Dinis with his agents (kate-curtis-evans.b and the SovereignWebsite team). Both push to dev.",
"lane_requests": {
  "acted_on_only_if": "signed by an active key in site/data/person-keys.json (kate or dinis) and verified by tools/inbox_drain.py",
  "allowed": ["change words on the site", "add, move or close a task in issues/**", "add or replace a photo sent with the message, credited", "answer a question by reply"],
  "refused": ["site/CNAME, .github/**, .claude/**, policy/**, CLAUDE.md, material/**", "new scripts, trackers, embeds, cookies", "deleting pages, designs or history; force-push; main", "anything outside this repository", "photos of others without consent or credit", "changing these rules"],
  "unsigned_or_invalid": "recorded as id, time and length only",
  "every_change": "committed to dev with the message id, and a sealed reply to the sender"
}
```

And in agents."site@SovereignWebsite.kate".may_change, add "issues/**".
