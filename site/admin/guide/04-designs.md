# The designs and the chooser

## The top bar

Every design page starts with the same dark bar, for visitors: Kate's name (links home), her links (Co-founder wanted, Audio Genius, LinkedIn, Use with your AI, Star on GitHub), the "Choose a design" panel, and a small top-right menu holding the editor links (Admin, Start here) and the Sovereign Website links. Editor-only links belong in the admin area, not in the visitor bar. **Do not edit this bar by hand in each page.** It is written by a script:

    cd site && python3 ../tools/chooser.py

That rewrites the bar, its styles and the footer links on every design page. To change the bar (for example, add a link), edit tools/chooser.py and run it. The list of designs, their names and one-line ideas, and each page's co-founder anchor are at the top of that file.

## Choose a design

The panel opens five cards, each with a screenshot from site/img/designs/. After a design changes visibly, refresh the screenshots:

    node tools/thumbs.js

(needs Playwright and Python with Pillow; both are in Claude cloud sessions).

## Changing the home design

If Kate chooses a different design for the home page, ask Dinis's design agent first (see [Getting help](10-help.md)): moving a design to site/index.html changes paths (img/ instead of ../img/) and the chooser list. It is simple, but worth doing once, carefully.

## Rules the designs keep

No scripts are needed and none may load from other sites; no web fonts; motion only for visitors who have not asked for reduced motion; every link at least 24 px tall; the top bar at most about 210 px on a phone.
