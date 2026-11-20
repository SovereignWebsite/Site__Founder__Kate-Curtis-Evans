#!/usr/bin/env python3
"""Kate's own top bar on every page: her name (home), her links, "Choose a design" (five
picture cards, details/summary, no script) and a small top-right menu for the Sovereign
Website family. Removes the old family strip and adds the site links to the footer.
Run from site/:  cd site && python3 ../tools/chooser.py"""
import re

D = [  # file, name, idea, thumb
    ('index.html', 'The Workflow Board', 'Her work as a board, with one open job', 'board'),
    ('designs/1.html', 'The Transcript', 'Her story set out as a legal transcript', 'transcript'),
    ('designs/2.html', 'The Edit Window', 'A transcription editor, dark and cinematic', 'edit'),
    ('designs/newsroom.html', 'The Newsroom', 'A magazine cover: specialist to founder', 'newsroom'),
    ('designs/5.html', 'The Brief', 'Plain and printable on A4', 'brief'),
]
PAGES = [d[0] for d in D] + ['designs/index.html', 'designs/4.html', 'designs/profile.html']
COF = {'index.html': '#wanted', 'designs/1.html': '#cofounder', 'designs/2.html': '#s5',
       'designs/newsroom.html': '#cofounder', 'designs/5.html': '#cofounder'}
FAMILY = [('Sovereign Website', 'https://sovereignwebsite.ai/'), ('Principles', 'https://sovereignwebsite.org/'),
          ('Hosted', 'https://sovereignwebsite.site/'), ('Hub', 'https://hub.sovereignweb.site/'),
          ('Agents', 'https://agents.sovereignweb.site/'), ('Vault', 'https://vault.sovereignwebsite.site/'),
          ('AgentiCCells', 'https://agenticcells.ai/'), ('RiskMandate', 'https://riskmandate.ai/'),
          ('Newsroom', 'https://newsroom.sgit.ai/')]

CSS = '''<style>
.pick{font:14px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:#1c1b19;color:#f2eee6;border-bottom:1px solid #000;position:relative;z-index:20}
.pick .pick-row{max-width:72rem;margin:0 auto;padding:.45rem 1rem;display:flex;flex-wrap:wrap;align-items:center;gap:.35rem .4rem}
.pick a{color:#f2eee6;text-decoration:none}
.pick .pick-name{display:flex;align-items:center;gap:.6rem;line-height:1.15;margin-right:auto;padding:.15rem 0;min-height:24px}
.pick .pick-face{display:block;flex:none;width:40px;height:40px;border-radius:50%;object-fit:cover;border:2px solid #f2eee6;background:#3a3833}
.pick .pick-name .pick-nm{display:flex;flex-direction:column;font-size:inherit;color:inherit}
.pick .pick-name b{font-size:15px}.pick .pick-name span{font-size:12.5px;color:#d8d2c6}
.pick .pick-links{list-style:none;display:flex;flex-wrap:wrap;gap:0 .2rem;margin:0 .4rem 0 0;padding:0}
.pick .pick-links a{display:inline-block;min-height:28px;line-height:28px;padding:0 .55rem;border-radius:999px;white-space:nowrap}
.pick .pick-links a:hover,.pick .pick-links a:focus-visible{background:#3a3833;text-decoration:underline}
.pick .pick-links a.pick-gh{display:inline-flex;align-items:center;gap:.35rem;border:1px solid #6b665c}
.pick summary{display:inline-block;cursor:pointer;font-weight:650;min-height:28px;line-height:28px;padding:0 .7rem;border-radius:999px;background:#f2eee6;color:#1c1b19;list-style:none;white-space:nowrap}
.pick summary::-webkit-details-marker{display:none}
.pick .pick-design summary::after{content:" \\25BE"}
.pick .pick-design[open] summary::after{content:" \\25B4"}
.pick summary:focus-visible,.pick a:focus-visible{outline:2px solid #f2eee6;outline-offset:2px}
.pick .pick-design{order:3}
.pick .pick-design[open]{order:7;flex-basis:100%}
.pick .pick-cards{padding:1rem 0 .6rem}
.pick .pick-cards ul{min-width:0;list-style:none;margin:0 auto;padding:0;max-width:72rem;display:grid;gap:.8rem;grid-template-columns:repeat(auto-fill,minmax(11.5rem,1fr))}
.pick .pick-cards li{min-width:0}
.pick .pick-cards a{display:block;border-radius:10px;padding:.5rem;background:#2a2824;border:2px solid transparent;height:100%}
.pick .pick-cards a:hover,.pick .pick-cards a:focus-visible{border-color:#8a857b}
.pick .pick-cards a[aria-current="page"]{border-color:#f2eee6}
.pick .pick-cards img{display:block;width:100%;height:auto;aspect-ratio:16/10;object-fit:cover;object-position:top;border-radius:6px;background:#3a3833}
.pick .pick-cards strong{display:block;margin:.5rem .2rem 0;font-size:15px}
.pick .pick-cards span{display:block;margin:.1rem .2rem .2rem;color:#d8d2c6;font-size:13px}
.pick .pick-cards .now{color:#f2eee6;font-weight:650}
.pick .pick-all{max-width:72rem;margin:.8rem auto 0}.pick .pick-all a{text-decoration:underline;display:inline-block;min-height:24px;line-height:24px}
.pick .pick-fam{order:4;position:relative}
.pick .pick-fam summary{background:transparent;color:#f2eee6;border:1px solid #6b665c;padding:0 .6rem;font-size:18px;font-weight:700;min-width:32px;text-align:center}
.pick .pick-fam-menu{position:absolute;right:0;top:calc(100% + .4rem);background:#1c1b19;border:1px solid #6b665c;border-radius:10px;padding:.6rem .4rem;min-width:13rem;box-shadow:0 14px 30px rgba(0,0,0,.45);z-index:30}
.pick .pick-fam-menu p{margin:.3rem .6rem .3rem;font-size:12.5px;color:#d8d2c6}
.pick .pick-fam-menu ul{list-style:none;margin:0;padding:0}
.pick .pick-fam-menu a{display:block;padding:0 .6rem;min-height:30px;line-height:30px;border-radius:6px}
.pick .pick-fam-menu a:hover,.pick .pick-fam-menu a:focus-visible{background:#3a3833;text-decoration:underline}
.pick .pick-links{order:5;flex-basis:100%;margin:0 -.55rem}
@media (max-width:40rem){.pick .pick-cards ul{grid-template-columns:1fr 1fr}.pick .pick-face{width:26px;height:26px;border-width:1.5px}.pick .pick-name{gap:.3rem}.pick .pick-row{padding-left:.6rem;padding-right:.6rem;column-gap:.3rem}.pick .pick-design summary{padding:0 .55rem}}
@media (max-width:22rem){.pick .pick-links a{padding:0 .38rem;font-size:13.5px}.pick .pick-row{gap:.3rem}}
@media print{.pick{display:none}}
.site-links{margin:.6rem 0 0}.site-links a{display:inline-block;min-height:24px;line-height:24px;margin-right:.9rem}
</style>'''


def rel(target, cur):
    up = '../' if cur.startswith('designs/') else ''
    if target.endswith('/'):
        return up + target
    if cur.startswith('designs/'):
        return '../index.html' if target == 'index.html' else target[len('designs/'):]
    return target


def bar(cur):
    up = '../' if cur.startswith('designs/') else ''
    cards = ''.join(
        f'<li><a href="{rel(f, cur)}"{" aria-current=\"page\"" if f == cur else ""}>'
        f'<img src="{up}img/designs/{t}.webp" width="640" height="400" alt="" loading="lazy" decoding="async">'
        f'<strong>{n}</strong><span>{i}</span>'
        f'{"<span class=\"now\">You are here</span>" if f == cur else ""}</a></li>'
        for f, n, i, t in D)
    alla = f'<a href="{rel("designs/index.html", cur)}"{" aria-current=\"page\"" if cur == "designs/index.html" else ""}>All designs</a>'
    cof = COF.get(cur, rel('index.html', cur) + '#wanted')
    fam = ('<details class="pick-fam"><summary aria-label="Made with Sovereign Website: menu">&#8942;</summary>'
           f'<div class="pick-fam-menu"><p>For Kate</p><ul><li><a href="{up}admin/">Admin</a></li><li><a href="{up}admin/message/">Message the agent</a></li><li><a href="{up}start/">Start here</a></li></ul><p>Made with Sovereign Website</p><ul>'
           + ''.join(f'<li><a href="{u}">{n}</a></li>' for n, u in FAMILY) + '</ul></div></details>')
    return ('<nav class="pick" aria-label="Kate Curtis-Evans"><div class="pick-row">'
            f'<a class="pick-name" href="{rel("index.html", cur)}">'
            f'<img class="pick-face" src="{up}img/kate-headshot.webp" width="40" height="40" alt="">'
            '<span class="pick-nm"><b>Kate Curtis-Evans</b><span>Founder, Audio Genius</span></span></a>'
            '<ul class="pick-links">'
            f'<li><a href="{cof}">Co-founder wanted</a></li>'
            '<li><a href="https://audio-genius.com/">Audio Genius</a></li>'
            '<li><a href="https://www.linkedin.com/in/kate-curtis-evans/">LinkedIn</a></li>'
            f'<li><a href="{up}agents/">Use with your AI</a></li>'
            '<li><a class="pick-gh" href="https://github.com/SovereignWebsite/Site__Founder__Kate-Curtis-Evans">'
            '<svg aria-hidden="true" viewBox="0 0 16 16" width="16" height="16"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>'
            '<span>Star on GitHub</span></a></li></ul>'
            '<details class="pick-design"><summary>Choose a design</summary>'
            f'<div class="pick-cards"><ul>{cards}</ul><p class="pick-all">{alla}</p></div></details>'
            + fam + '</div></nav>')


for f in PAGES:
    s = open(f).read()
    s = re.sub(r'(?s)<style>\n\.pick\{.*?</style>\n?', '', s)
    s = s.replace('</head>', CSS + '\n</head>', 1)
    s, n = re.subn(r'(?s)<nav class="pick".*?</nav>', bar(f), s, count=1)
    assert n == 1, f
    s = re.sub(r'(?s)\n?<nav class="family".*?</nav>\n?', '\n', s)
    s = re.sub(r'(?s)<p class="site-links">.*?</p>', '', s)
    up = '../' if f.startswith('designs/') else ''
    links = (f'<p class="site-links"><a href="{up}agents/">Use with your AI</a>'
             f'<a href="{up}admin/">Admin</a></p>')
    k = s.rfind('</footer>')
    assert k > 0, f
    s = s[:k] + links + s[k:]
    open(f, 'w').write(s)
    print('bar on', f)
