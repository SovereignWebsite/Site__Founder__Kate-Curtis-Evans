# Checks before publishing

Run these after every change, before you ask Kate for her yes:

1. **Page checks**:

        node tools/check.js

   It opens every page at 320, 390 and 1366 px, in light and dark, and prints a CHECK line for any page that scrolls sideways, has a phone top bar over 210 px, a link under 24 px, or loads something from another site. "done" with no CHECK lines means all clear.

2. **Look at it**: take a phone and a desktop screenshot of the pages you changed (Playwright is available) and look at them. Check text is readable over photos.

3. **Words and figures**: search the site for the old and new wording (grep -rn) and confirm every design says the same thing. No em dashes: `grep -rn $'\u2014' site/` must find nothing.

4. **Show Kate**: the diff (git diff), the screenshots, and the list of files changed. Wait for her yes.
