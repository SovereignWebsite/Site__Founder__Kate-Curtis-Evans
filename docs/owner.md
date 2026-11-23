# What the owners can do on this site, themselves

kate-curtis-evans.b, 23 November 2026. Dinis asked (23 Nov 2026) that every site be left so he can carry on with it himself, with no agent waiting on him. This page lists what Kate (the owner) and Dinis (co-editor) can do here without any agent.

## Every day

- **Ask for a change from your phone.** Open https://kate-curtis-evans.founder.sovereignweb.site/admin/message/ with your private key (the QR code you were given), write the change, send. feedback.b reads the inbox hourly from 10:00 to 22:00 UK time, plus 01:00, 04:00 and 07:00; the site's agent acts within [the policy](../site/admin/policy.md) and replies on the same page.
- **Edit with your own Claude.** Open a Claude Code session on this repository and paste [the prompt](prompt-for-your-claude.md). The guide at /admin/guide/ tells Claude how the site is built and what it must not touch.
- **Edit in GitHub directly.** Every page is a plain file in site/. Edit it in the GitHub web editor on branch dev; it goes live in about a minute.
- **See what is happening.** The dashboard is at /admin/, the board at /admin/board.html, and every change at https://github.com/SovereignWebsite/Site__Founder__Kate-Curtis-Evans/commits/dev.

## The board

Tasks are files in issues/. The folder is the status: issues/open, issues/blocked, issues/done. To close a task, move its file to issues/done; to add one, copy any task file and change it. Open now: headshot credit (002), logo and poster (003), founder story interview (004), choose the home design (005), photo credit wording (006), more photos (007), user quotes (008).

## Decisions only the owners can make (nothing waits on them)

Each of these is ready for you to do yourself, or to say yes to from the message page. The site works as it is in the meantime.

1. **Pick the home design** (issue 005). Use "Choose a design" on any page, then send the one you want.
2. **Say whether Kate may be featured beyond her site.** That means the startup brochure (as proof that she edits her own site) and the showroom on sovereignweb.site. Until Kate says yes, nothing about her goes in the brochure. Record her words and the date in this file.
3. **Update the behaviour policy.** The proposed change is in [proposals/abp-lane-requests.md](proposals/abp-lane-requests.md): two editors, board tasks for Kate's Claude, and the message limits. policy/** is protected from agents, so an owner pastes it into policy/abp.json in the GitHub editor.
4. **Update CLAUDE.md** to say Kate owns the site and her Claude is site@SovereignWebsite.kate. This file is also protected from agents.
5. **Adopt the Factory's new publishing pipeline**, if wanted. Copy seed/site-template/.github/ from SovereignWebsite__Factory (dev) over .github/ here. .github/** is protected from agents. The current pipeline publishes fine.
6. **Delete the old inbox vault** (mptf9t93 on dev.send.sgraph.ai), which nothing points to since 21 Nov. Optional.

## Keys

Your private message key is yours alone: never post it. To stop using it in a browser, press "Forget this key" on the message page. If a key is lost or shared, ask for a new one and the old one is removed from site/data/person-keys.json.
