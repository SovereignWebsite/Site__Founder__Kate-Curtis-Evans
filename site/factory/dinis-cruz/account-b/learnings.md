# Learnings

- **GitHub verification is not identity.** Commits from any Claude Code session signed with Claude's built-in signer show as verified for the shared "claude" login. Only a key published for the agent, or a named person's login, says who made a commit (24 Nov).
- **The handover**: organisation base permission "No permission", the owner invited as a member and accepting at github.com/orgs/<org>/invitation, then the owner's Claude attaching the repository with push access. The "only the owner can connect" notice did not block pushing (20 Nov; docs/handover.md).
- **Two editors on one branch** work if each fetches and rebases before pushing, and nobody regenerates the other's pages unasked: rebuild only what your change touches.
- **Protected paths stay protected.** When the permission check refuses an edit to policy/ or .github/, write the change as a proposal and ask; never route around it with the shell.
- **Test a rule before writing it down for someone else**: the own-key step was tested against signers.mjs on a scratch copy first, and the pipeline was tested on this site's own history before adopting it, which caught the refusal.
- **GitHub Pages "artifact" errors** are transient; re-run the deploy, once, and wait for it.
- **Secrets in tool output**: `sgit vault info` printed a vault passphrase on 20 Nov; that vault was deleted and remade with output suppressed. Suppress output of any command that may print a secret.
- **Consent before featuring**: a public commit history is not consent to be used as proof in marketing (23 Nov).
