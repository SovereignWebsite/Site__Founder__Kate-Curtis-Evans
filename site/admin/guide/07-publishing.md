# Publishing and undoing

## Publishing

    git add <the files you changed>
    git commit -m "<what changed, in plain words>"
    git push origin dev

Then watch the Pages run in the repository's Actions tab (about a minute) and open the live page to confirm. Tell Kate the commit and that it is live. If the live page still shows the old version, wait a minute and reload: pages are cached for up to ten minutes.

## If the Pages run fails

Open the failed run in Actions. A message about artifacts or "Fetching artifact metadata failed" is a GitHub hiccup: re-run the job. Anything else, stop and tell Kate.

## Undoing a mistake

Never rewrite history. To undo a commit that is already pushed:

    git revert <commit>
    git push origin dev

That adds a new commit that reverses the old one, and the site goes back.

## Never

Push to main, force-push, delete a branch, or reset dev to an older commit.
