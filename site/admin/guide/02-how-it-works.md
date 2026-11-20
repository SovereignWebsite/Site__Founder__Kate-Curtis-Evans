# How the site works

The site is plain static files. There is no server code, no database and no build step: what is in site/ is what visitors get.

## The files

| Path | What it is |
|---|---|
| site/index.html | The home page, in the design called The Workflow Board |
| site/designs/1.html | The Transcript |
| site/designs/2.html | The Edit Window (dark first) |
| site/designs/newsroom.html | The Newsroom (dark first) |
| site/designs/5.html | The Brief (plain and printable) |
| site/designs/index.html | The page listing all designs |
| site/designs/4.html, site/designs/profile.html | Earlier designs (Foundations, The Profile), kept so old links work |
| site/designs/3.html | Forwards to the home page (the Board used to live here) |
| site/start/ | Start here: how Kate took over the site |
| site/agents/ | Use with your AI: prompts for visitors and for Kate, plus agents/*.md |
| site/admin/ | The admin area (for Kate and her Claude, not visitors): board, this guide, the policy, how the site was made |
| site/index.md | Every fact on the site, as Markdown: the master copy for AI agents |
| site/llms.txt | The entry point for AI agents visiting the site |
| site/img/ | Photos; site/img/designs/ holds the chooser thumbnails; site/img/share-card.jpg is the link preview |
| site/favicon.svg | The tab icon |
| site/CNAME | The site's address. Protected: do not touch |
| material/ | What the site was built from (LinkedIn profile, posts, images), with a README of sources. Read-only |
| docs/ | Handover, questions for Kate, the prompt for Kate's Claude, guidelines |
| tools/ | Scripts: chooser.py (top bar on every page), thumbs.js (chooser thumbnails), check.js (page checks) |
| policy/abp.json, .claude/settings.json | The behaviour policy and its enforced rules. Protected |
| .github/workflows/pages.yml | Publishes site/ on every push to dev. Protected |

## How it publishes

Every push to the **dev** branch runs the Pages workflow, which publishes site/ to https://kate-curtis-evans.founder.sovereignweb.site/ in about a minute. You can watch it in the repository's Actions tab. main is locked; nothing goes there.

## The five designs

The same facts are told five ways. Each design is a complete HTML page with its own styles; they share only the top bar, the photos and the footer links. So **a change to a fact must be made in every design** (see [Changing what the site says](03-changing-content.md)).
