# Restart: START for a fresh kate-curtis-evans.b session

A fresh session, started on SovereignWebsite/Site__Founder__Kate-Curtis-Evans with one line pointing here, picks up from what is committed.

1. Read CLAUDE.md, then this area: role.md, now.md, learnings.md, messages.md, and docs/owner.md.
2. `git checkout dev && git pull`. Never main.
3. **Make your own key** in the new session (`sgit pki keygen --label kate-curtis-evans.b`), keep the private half in the session, and publish its public half alone in its own signed commit. Replace site/keys/kate-curtis-evans.b.json and set the old entry's status to "superseded". The old key ended with its session. Configure git to sign with it (gpg.format ssh, gpg.ssh.program ssh-keygen) and add the trailers `Agent: kate-curtis-evans.b@SovereignWebsite.dinis` and `Claude-Session: <your session URL>`.
4. Tell decisions.b the new key's commit link, so the Factory's team/keys.json entry can be moved to it.
5. Check the decision receipts and records for the open requests listed in agent.json, and act on any decided ones.
6. Messages from the site arrive from feedback.b as material. To reply, `node tools/reply.mjs --person kate|dinis --re "..." --text "..."`. Replies are sealed to the person's public key in site/data/person-keys.json, so no private key is needed.
7. Rebuild with `python3 tools/backoffice.py` and `cd site && python3 ../tools/chooser.py`, check with `node tools/check.js`, and commit only the files your change touches.

Not carried over: this session's private keys (signing key, the old inbox's reader). The person keys' private halves were delivered to Dinis on 20 Nov and are not in the repository. This file has not been tested by a real fresh session yet: starting one is the person's to do.
