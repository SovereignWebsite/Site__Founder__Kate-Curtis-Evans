# Handover to Kate

Your site is yours: its files, its history and its address. This page says what is here and how to carry on.

## What is here
- **The site:** https://kate-curtis-evans.founder.sovereignweb.site, plain static files in site/, published by GitHub Pages a minute or two after every push to dev. main is locked.
- **Designs:** the same facts in several designs, with a "Choose a design" bar at the top of every page. The home page (site/index.html) is The Workflow Board; the others are in site/designs/. Pick the one you like, or keep them all: the bar lets every visitor switch.
- **Material:** material/ holds what the site was built from (your LinkedIn profile and posts, and the images), with a README naming each source.
- **Your Claude:** docs/prompt-for-your-claude.md says how to connect your Claude to GitHub and gives a prompt to paste in.
- **Questions:** docs/questions-for-kate.md lists what the site would like to know from you (dates for the figures, who took your headshot, which images may be used, your founder story).

## How to carry on
The same steps, with direct links, are on the site at https://kate-curtis-evans.founder.sovereignweb.site/start/

1. Accept the GitHub invitation to the repository (from GitHub's email).
2. Connect your Claude to GitHub (Part 1 of docs/prompt-for-your-claude.md).
3. Paste the prompt (Part 2) and ask for what you want: answer the questions, add photos, change words, choose a design.
4. Your commits do not need to be signed.

## The rules the site keeps
Static files only; no cookies, tracking or third-party scripts; plain British English, no em dashes; never invent a fact, figure, client or quote; date every figure; credit every photo (the desk photo is by Matt Hinton Photography).

## Who made it
Built on 20 November 2026 by kate-curtis-evans.b, an agent working for Dinis Cruz, with design rounds by the design team. Every agent commit carries `Agent:` and `Claude-Session:` lines, so you can see who changed what.

## What made the handover work (20 November 2026)

The first owner handover in the SovereignWebsite organisation. Kate's own Claude pushed her first change, e1f1e9e, at 16:30 UTC, about 35 minutes after she accepted the invitation.

### The steps that worked, in order

1. **Repository invitation** (write access) from factory.b. Kate accepted it from GitHub's email, about 15:55 UTC.
2. **Organisation base permission set to "No permission"** by Dinis (Settings, Member privileges). Safe here because the agents' team ("Agents - CI") holds all 29 repositories itself. Without this, a new member could read every repository in the organisation.
3. **Kate invited as an organisation Member**, no teams, by Dinis. Her direct write role on her repository stayed.
4. **Kate joined via https://github.com/orgs/SovereignWebsite/invitation** ("Join SovereignWebsite"). The invitation email's link took her to the organisation's page without an accept button.
5. **In Claude** (claude.ai/code, in the browser): GitHub connected; she added the repository to her cloud environment's Repositories list and started a session on it.
6. **Her Claude asked for push access** (attached the repository with push) and it was granted, although Claude's GitHub settings still showed SovereignWebsite as "Needs reconnecting: only an owner of SovereignWebsite on GitHub can connect it". That notice did not block pushing.
7. **First change**: one line, the photo credit, shown to her, committed and pushed to dev, verified and live in about a minute.

### What tripped her up

- As an **outside collaborator**, Claude's GitHub settings said "GitHub refused Claude's check of your access to SovereignWebsite", even though the Claude GitHub App was installed on the organisation with All repositories. Joining as a member fixed the check.
- The **"Update Claude's repository access" page** on GitHub ("This action must be performed by an organization owner") was a dead end for her; the installation did not need changing.
- **"Switch GitHub account"** appeared as the only button; she did not need it.
- Her Claude first had a **read-only clone** (the repository is public), and said it could not save. Asking it to get permission to save, with the repository attached with push access, was the step that unlocked it.
- The terminal routes (`gh auth login`, `/web-setup`) were **not available to her**: everything had to work in the browser.
- She looked at /start/ and thought it was the site: the start page should say clearly at the top that the site itself is elsewhere.

### What to change in /start/ for every site

- Order the steps as above: repository invitation, then the **organisation invitation link** (direct link, not the email), then Claude, then "ask your Claude to get permission to save".
- Say plainly: ignore "Needs reconnecting" and "Switch GitHub account" if the repository check is green or the push works.
- Drop the terminal routes from the main path (keep them as a last resort).
- Put a "Your site is at ..." link at the very top.
- Owner-side checklist for whoever hands over: base permission "No permission" (check the agents' team first), invite the owner as Member, send the /start/ link.
