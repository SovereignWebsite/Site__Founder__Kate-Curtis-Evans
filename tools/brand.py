#!/usr/bin/env python3
"""Audio Genius brand on every design (Kate's choice, 20 November 2026): the brand
colours as accents (links, buttons, highlights) and the logo in each design's
Audio Genius section, linking to audio-genius.com. Safe to run again.
Run from site/:  cd site && python3 ../tools/brand.py

Brand colours, from the logo Kate supplied: navy #05102f, purple #6b3fc0 to #c5aaf1.
On light backgrounds the accent is #6b3fc0 (white text on it); on dark backgrounds
it is #c5aaf1 (navy text on it). Both pass WCAG AA contrast."""
import re

LIGHT = '--accent:#6b3fc0;--accent-ink:#fff'
DARK = '--accent:#c5aaf1;--accent-ink:#05102f'
LOGO_CSS = ('.ag-logo{margin:.6rem 0 1rem}'
            '.ag-logo a{display:inline-block;background:#fff;border-radius:10px;padding:.35rem .6rem;line-height:0;border:1px solid #d9d6ec}'
            '.ag-logo img{display:block;width:12.5rem;max-width:100%;height:auto}')


def style(page, dark_only=False, rule=False, print_black=False):
    extra = ';--rule:var(--accent)' if rule else ''
    if dark_only:
        css = f':root:root{{{DARK}{extra}}}'
    else:
        css = (f':root:root{{{LIGHT}{extra}}}'
               f'@media (prefers-color-scheme:dark){{:root:root{{{DARK}{extra}}}}}')
    if print_black:
        css += '@media print{:root:root{--accent:#000}}'
    return f'<style id="brand">{css}{LOGO_CSS}</style>'


def logo(up):
    return (f'<p class="ag-logo"><a href="https://audio-genius.com/">'
            f'<img src="{up}img/audio-genius-logo.webp" width="600" height="240" '
            f'alt="Audio Genius: visit audio-genius.com" loading="lazy" decoding="async"></a></p>')


# page: (where the logo goes after, style options)
PAGES = {
    'index.html': ('<h2>Audio Genius</h2>', {}),
    'designs/1.html': ('What is Audio Genius?</h2></div></li>\n<li class="turn "><span class="tc" aria-hidden="true">00:02:36</span><span class="who">A.</span><div class="say">', {'rule': True}),
    'designs/2.html': ('<h3 id="s2">Audio Genius</h3>', {'dark_only': True}),
    'designs/4.html': ('<h2 id="sec-h">Audio Genius, drawn in section</h2>', {}),
    'designs/5.html': ('<h2>Audio Genius</h2>', {'print_black': True}),
    'designs/newsroom.html': ('<h2>The product</h2>', {}),
    'designs/profile.html': ('<h2 id="ag-h">Audio Genius</h2>', {}),
    'designs/index.html': (None, {}),
}

for f, (after, opts) in PAGES.items():
    up = '../' if f.startswith('designs/') else ''
    s = open(f).read()
    s = re.sub(r'<style id="brand">.*?</style>\n?', '', s, flags=re.S)
    s = re.sub(r'<p class="ag-logo">.*?</p>', '', s, flags=re.S)
    s = s.replace('</head>', style(f, **opts) + '\n</head>', 1)
    if after:
        assert s.count(after) == 1, (f, after)
        s = s.replace(after, after + logo(up), 1)
    open(f, 'w').write(s)
    print('brand on', f)
