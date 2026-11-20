# Changing what the site says

## Where a fact lives

Most facts appear in **every design** plus the machine-readable copies. When Kate changes a fact, change it in all of these, then search to be sure:

- site/index.html, site/designs/1.html, site/designs/2.html, site/designs/newsroom.html, site/designs/5.html
- site/designs/4.html and site/designs/profile.html (earlier designs; keep them consistent too)
- site/index.md (the master copy of the facts) and site/llms.txt (the one-paragraph summary)
- the share tags at the top of each page (og:description, twitter:description) if the summary changes
- site/admin/index.html only describes how the site was made; do not put Kate's facts there

Search for the old wording across the site before and after, for example:

    grep -rn "34,000" site/

and report to Kate every file you changed.

## The rules for words

- **Only what Kate has said or approved.** If she tells you something new, use her words. Never fill a gap with a guess, and never draft "her" answers from the LinkedIn material.
- **Date every figure**, with where it came from: "as Kate stated in her LinkedIn post, November 2026", or "as Kate told the site on [date]".
- **Plain British English, no em dashes** (use commas, colons or full stops).
- **No new names** of other people (clients, testers, family) without their consent.
- Keep claims modest and checkable; she should be able to talk about anything on the site.

## Common changes

- **A new figure** (users, minutes, visits): update every design and site/index.md, with the new date. Remove the old date note.
- **A new section** (for example a testimonial): add it to every design in a way that suits that design, or ask Kate whether it belongs in only one.
- **Contact details**: only LinkedIn and audio-genius.com are on the site. Add an email or phone only if Kate asks, and then everywhere she wants it.
