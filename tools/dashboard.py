"""The admin dashboard: data and charts made at build time from the repository. No chart library, no API calls.

Used by tools/backoffice.py, which writes site/admin/index.html, site/admin/data.json and site/version.json.
Every number comes from the repository (git history, issues/, the files in site/, site/admin/data/checks.json
written by tools/check.js) or from the design team's recorded rounds (ROUNDS below, with their sources).
Charts are inline SVG: hover a mark for its value (SVG <title>); every chart has its data behind "Show data".
Public data only: author names and agent ids, never email addresses.
"""
import html, os, re, json, math, subprocess, glob, collections, datetime

E = html.escape
REPO = 'https://github.com/SovereignWebsite/Site__Founder__Kate-Curtis-Evans'

# Design rounds, from https://design.agents.sovereignweb.site/back-office.html: rating at the end of each round,
# and the synthetic users' scores (five imagined visitors) where the round ran them, as design.b reported them.
ROUNDS = [(1, 1, None), (2, 2, [4, 4, 4, 4, 4]), (3, 2, None), (4, 2, None), (5, 4, [4, 3, 4, 4, 4]),
          (6, 3, None), (7, 3, [4, 4, 4, 4, 4]), (8, 4, None)]
PERSONAS = ['Hurried phone visitor', 'Small business owner', 'Low-vision reader', 'Design critic', 'Co-founder candidate']
AUTHORS = {'claude': "Kate's Claude", 'kate-curtis-evans.b': 'kate-curtis-evans.b', 'agenticcells-site-factory[bot]': 'Factory (bot)',
           'sites.b@sovereignwebsite.dinis': 'sites.b'}
ROLES = {"Kate's Claude": 'Kate, through her own Claude: the owner, editing her site',
         'kate-curtis-evans.b': 'Built the site, the handover and this admin area',
         'Factory (bot)': 'Made the repository, the address and the publishing pipeline',
         'sites.b': 'Took the request from Dinis Cruz and committed the material'}
CREDITS = {'kate-at-desk': 'Photo by Matt Hinton Photography', 'share-card': 'Link preview, made from the Matt Hinton Photography photo',
           'designs/': 'Screenshot of a design, for the chooser', 'favicon': 'Tab icon'}
PROMPTS = [
    ('Words', 'Change my headline to "..." on every design.', 'Your Claude finds the headline in all five designs and the facts file, shows you the change, and publishes it when you say yes.'),
    ('Words', 'Ask me the open questions on the board, one at a time.', 'It works through issues/open, uses your own words, and moves each card to Done.'),
    ('Words', 'Add a short paragraph about why I started Audio Genius, in my words: "..."', 'It places your words in each design where they fit, and in site/index.md.'),
    ('Pictures', 'Replace the hero photo with this one, credited to "...".', 'It strips the photo\'s hidden location data, makes web sizes, credits it, and updates the share card.'),
    ('Pictures', 'Add this photo of me to the Transcript design as Exhibit C, credited to "...".', 'It adds one photo to one design, with its credit and a description for screen readers.'),
    ('Pages', 'Add a section to every design for quotes from Audio Genius users: "..." (I have their permission).', 'A new section in each design, styled to suit it; names only with consent.'),
    ('Pages', 'Add my email address, ..., next to LinkedIn everywhere.', 'Contact details appear only where you ask, on every design.'),
    ('Designs', 'Make the Newsroom design my home page.', 'It asks the design team first, then swaps the home page and updates the chooser.'),
    ('Designs', 'Show me all five designs side by side as screenshots.', 'It takes phone and desktop screenshots of each design for you to compare.'),
    ('Checks', 'Check my site for broken links, sideways scrolling and small buttons, and fix what you find.', 'It runs tools/check.js on every page in four views and fixes problems, with your yes.'),
    ('Checks', 'Show me what changed on my site this week.', 'A plain list of every change, who made it, and links to each one on GitHub.'),
    ('Checks', 'Make sure every design says the same figures, with their dates.', 'It searches every page for each figure and reports any that differ.'),
]

CSS = '''
body.dash{--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--grid:#e6e3db;--good:#2f7a42;--warn:#9a5f00;--bad:#c0392b;--info:#2a78d6;--heat0:#ebe8e1;--heat1:#c6dbf3;--heat2:#8fb8e8;--heat3:#4f8fd9;--heat4:#2a78d6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) body.dash{--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--grid:#2f2d29;--good:#6cc283;--warn:#f0b866;--bad:#ef7a6b;--info:#6ea8e6;--heat0:#24231f;--heat1:#1e3a5f;--heat2:#285b94;--heat3:#3478c8;--heat4:#5d9ff0}}
.app{display:grid;grid-template-columns:13rem minmax(0,1fr);gap:1.6rem;max-width:84rem;margin:0 auto;padding:1.2rem 1rem 3rem}
.side{position:sticky;top:1rem;align-self:start}
.side nav a{display:flex;align-items:center;min-height:34px;padding:0 .7rem;border-radius:8px;color:var(--fg);text-decoration:none;font-size:.95rem}
.side nav a:hover{background:var(--chip)}.side nav hr{border:0;border-top:1px solid var(--line);margin:.6rem 0}
.side .lab{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:.8rem .7rem .3rem}
.side .phone{display:none}
@media (max-width:56rem){.app{grid-template-columns:1fr;gap:1rem}.side{position:static}.side .desk{display:none}.side .phone{display:block}.side .phone summary{display:flex;align-items:center;min-height:40px;padding:0 .8rem;border:1px solid var(--line);border-radius:10px;background:var(--paper);cursor:pointer;font-weight:650}}
.app main{padding:0;max-width:none;margin:0}
.sec{scroll-margin-top:1rem;margin:0 0 2rem}.sec>h2{font-size:1.25rem;margin:0 0 .8rem;display:flex;flex-wrap:wrap;gap:.2rem .6rem;align-items:baseline}
.sec>h2 small{font-size:.85rem;color:var(--muted);font-weight:500}
.kpis{display:grid;gap:.7rem;grid-template-columns:repeat(4,minmax(0,1fr))}
@media (max-width:56rem){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
.kpi{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:.75rem .9rem;min-width:0}
.kpi b{display:block;font-size:1.65rem;line-height:1.15;font-variant-numeric:tabular-nums}
.kpi span{display:block;color:var(--muted);font-size:.86rem;margin-top:.15rem}
.chips{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.35rem}
.chip{display:inline-flex;align-items:center;gap:.25rem;font-size:.78rem;font-weight:650;padding:0 .5rem;border-radius:999px;border:1px solid currentColor;min-height:22px}
.chip.ok{color:var(--good)}.chip.no{color:var(--bad)}
.grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,26rem),1fr))}
.card{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:1rem 1.1rem;min-width:0}
.card.wide{grid-column:1/-1}
.card h3{margin:0 0 .15rem;font-size:1rem}.card .sub{margin:0 0 .6rem;color:var(--muted);font-size:.88rem}
.card svg{display:block;width:100%;height:auto;overflow:visible}
.card svg text{font:12px var(--sans);fill:var(--muted)}.card svg .v{fill:var(--fg);font-weight:600}.card svg .w{fill:#fff;font-weight:600}
.legend{display:flex;gap:.9rem;flex-wrap:wrap;font-size:.86rem;color:var(--muted);margin:.1rem 0 .5rem}
.legend i{display:inline-block;width:.75rem;height:.75rem;border-radius:3px;margin-right:.35rem;vertical-align:-.08rem}
.card details{margin-top:.5rem;font-size:.88rem}.card details>summary{cursor:pointer;color:var(--muted);min-height:24px;line-height:24px}
.card table{font-size:.86rem}.note{font-size:.84rem;color:var(--muted)}
.mark:hover{opacity:.78}
.statusbar{display:flex;height:22px;border-radius:6px;overflow:hidden;gap:2px;margin:.4rem 0}
.commits{list-style:none;margin:0;padding:0}.commits li{display:grid;grid-template-columns:5.2rem 1fr;gap:.6rem;padding:.4rem 0;border-bottom:1px solid var(--line);font-size:.9rem;max-width:none}
.commits code{font-size:.82rem}.commits .who{color:var(--muted);font-size:.82rem;display:block}
.gallery{display:grid;gap:.7rem;grid-template-columns:repeat(auto-fill,minmax(9.5rem,1fr))}
.gallery figure{margin:0;background:var(--chip);border-radius:10px;padding:.4rem;font-size:.78rem;color:var(--muted);min-width:0}
.gallery img{display:block;width:100%;height:92px;object-fit:cover;object-position:top;border-radius:6px;background:var(--line)}
.gallery figcaption{margin-top:.3rem;line-height:1.35}.gallery b{color:var(--fg);display:block;font-size:.8rem;overflow-wrap:anywhere}
.live{display:inline-block;font-size:.72rem;font-weight:700;color:var(--paper);background:var(--good);border-radius:999px;padding:0 .45rem;margin-left:.3rem}
.preview{border:1px solid var(--line);border-radius:12px;overflow:hidden;max-width:30rem;background:var(--paper)}
.preview img{display:block;width:100%;height:auto}.preview div{padding:.55rem .8rem}.preview b{display:block;font-size:.95rem}
.preview p{margin:.15rem 0;font-size:.84rem;color:var(--muted)}.preview .dom{font-size:.78rem;text-transform:lowercase}
.preview.wa{background:#e7fcd8;color:#111;border-color:#cde9b9}.preview.wa p{color:#444}
.prompts{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,22rem),1fr))}
.prompt{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:.8rem .9rem;display:flex;flex-direction:column;gap:.4rem}
.prompt .grp{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);font-weight:700}
.prompt q{font-weight:600;quotes:none}.prompt p{margin:0;font-size:.86rem;color:var(--muted)}
.prompt button{align-self:flex-start;min-height:30px;padding:0 .8rem;border-radius:999px;border:1px solid var(--line);background:var(--chip);color:var(--fg);font:600 .85rem var(--sans);cursor:pointer}
.prompt button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.ghost{opacity:.55;filter:grayscale(1)}
'''


def git(*a, root):
    return subprocess.run(['git', *a], cwd=root, capture_output=True, text=True).stdout


def author(name):
    return AUTHORS.get(name.lower(), name if '@' not in name else name.split('@')[0])


def collect(root, site, cols):
    out = git('log', '--format=@@%h|%aI|%an|%s', '--numstat', root=root)
    commits = []
    for block in out.split('@@')[1:]:
        lines = block.strip().split('\n')
        h, when, who, subj = lines[0].split('|', 3)
        add = rem = 0; files = []
        for l in lines[1:]:
            p = l.split('\t')
            if len(p) == 3:
                files.append(p[2])
                if p[0].isdigit(): add += int(p[0])
                if p[1].isdigit(): rem += int(p[1])
        commits.append({'commit': h, 'when': when, 'author': author(who), 'subject': subj, 'added': add, 'removed': rem, 'files': files})
    shallow = git('rev-parse', '--is-shallow-repository', root=root).strip() == 'true'
    tree = []
    for p in glob.glob(os.path.join(site, '**', '*'), recursive=True):
        if os.path.isfile(p):
            tree.append({'path': os.path.relpath(p, site), 'bytes': os.path.getsize(p)})
    images = []
    try:
        from PIL import Image
    except Exception:
        Image = None
    for t in tree:
        if re.search(r'\.(webp|jpg|jpeg|png|svg)$', t['path']):
            dims = ''
            if Image and not t['path'].endswith('.svg'):
                try:
                    with Image.open(os.path.join(site, t['path'])) as im:
                        dims = f'{im.width} x {im.height}'
                except Exception:
                    pass
            credit = next((v for k, v in CREDITS.items() if k in t['path']), '')
            images.append({**t, 'dims': dims, 'credit': credit})
    checks = []
    try:
        checks = json.load(open(os.path.join(site, 'admin', 'data', 'checks.json')))
    except Exception:
        pass
    datasets = []
    for rel in ['index.md', 'llms.txt', 'admin/data/checks.json', 'admin/data.json', 'version.json']:
        p = os.path.join(site, rel)
        if not os.path.exists(p):
            continue
        s = open(p, encoding='utf-8').read()
        if rel.endswith('.json'):
            try:
                d = json.loads(s); n = len(d) if isinstance(d, list) else len(d.keys())
            except Exception:
                n = 0
            unit = 'records' if rel.endswith('checks.json') else 'keys'
        else:
            n = len([l for l in s.splitlines() if l.strip().startswith(('- ', '* '))]); unit = 'facts (list items)'
        datasets.append({'path': rel, 'bytes': len(s.encode()), 'records': n, 'unit': unit, 'preview': s[:220]})
    datasets.append({'path': '../issues/', 'bytes': 0, 'records': sum(len(v) for v in cols.values()), 'unit': 'tasks', 'preview': ', '.join(f'{k} {len(v)}' for k, v in cols.items())})
    return {'commits': commits, 'shallow': shallow, 'tree': tree, 'images': images, 'checks': checks, 'datasets': datasets,
            'issues': {k: [{'file': i['file'], 'title': i['title'], 'priority': i.get('priority', 'normal')} for i in v] for k, v in cols.items()},
            'rounds': [{'round': r, 'rating': a, 'synthetic_users': u} for r, a, u in ROUNDS]}


# ---------- small helpers
def legend(items):
    return '<div class="legend">' + ''.join(f'<span><i style="background:var({c})"></i>{E(n)}</span>' for n, c in items) + '</div>'


def table(head, rows):
    h = ''.join(f'<th>{E(x)}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{E(str(c))}</td>' for c in r) + '</tr>' for r in rows)
    return f'<details><summary>Show data</summary><div class="wrapx"><table><tr>{h}</tr>{b}</table></div></details>'


def card(title, sub, body, wide=False):
    return f'<article class="card{" wide" if wide else ""}"><h3>{E(title)}</h3><p class="sub">{sub}</p>{body}</article>'


def kb(b):
    return f'{b/1024:,.0f} KB' if b < 1024 * 1024 else f'{b/1024/1024:.1f} MB'


SERIES = [("Kate's Claude", '--s2'), ('kate-curtis-evans.b', '--s1'), ('sites.b', '--s3'), ('Factory (bot)', '--s4')]


def scol(name):
    return dict(SERIES).get(name, '--s3')


# ---------- charts
def heatmap(commits):
    days = collections.Counter(c['when'][:10] for c in commits)
    end = datetime.date.fromisoformat(max(days)) if days else datetime.date.today()
    end = end + datetime.timedelta(days=6 - end.weekday())
    start = end - datetime.timedelta(days=7 * 12 - 1)
    mx = max(days.values() or [1]); cell = 22; gap = 4
    svg = []; d = start; i = 0
    while d <= end:
        w, dow = i // 7, d.weekday()
        n = days.get(d.isoformat(), 0)
        lvl = 0 if not n else min(4, 1 + int(3 * n / mx))
        svg.append(f'<rect class="mark" x="{34 + w*(cell+gap)}" y="{dow*(cell+gap)}" width="{cell}" height="{cell}" rx="3" fill="var(--heat{lvl})"><title>{d.strftime("%a %d %b %Y")}: {n} commit{"s" if n != 1 else ""}</title></rect>')
        if d.day <= 7 and dow == 0:
            svg.append(f'<text x="{34 + w*(cell+gap)}" y="{7*(cell+gap)+14}">{d.strftime("%b")}</text>')
        d += datetime.timedelta(days=1); i += 1
    for k, lab in [(0, 'Mon'), (2, 'Wed'), (4, 'Fri')]:
        svg.append(f'<text x="0" y="{k*(cell+gap)+15}">{lab}</text>')
    W = 34 + 12 * (cell + gap) + 10
    leg = '<div class="legend"><span>Less</span>' + ''.join(f'<span><i style="background:var(--heat{l})"></i></span>' for l in range(5)) + '<span>More</span></div>'
    return card('Commit calendar', 'Commits per day over the last twelve weeks.', f'<svg viewBox="0 0 {W} {7*(cell+gap)+18}" style="max-width:{W}px" role="img" aria-label="Commit calendar">{"".join(svg)}</svg>' + leg
                + table(['Day', 'Commits'], sorted(days.items())))


def over_time(commits):
    buckets = collections.OrderedDict()
    for c in reversed(commits):
        q = int(c['when'][14:16]) // 15 * 15
        buckets.setdefault(f"{c['when'][:13]}:{q:02d}", collections.Counter())[c['author']] += 1
    keys = list(buckets); W, H, pad, top = 640, 220, 30, 22
    mx = max([sum(v.values()) for v in buckets.values()] or [1]); bw = (W - pad - 8) / max(len(keys), 1)
    svg = []
    for t in range(0, mx + 1, max(1, (mx + 3) // 4)):
        y = H - 24 - (H - 24 - top) * t / mx
        svg.append(f'<line x1="{pad}" x2="{W}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--grid)"/><text x="{pad-6}" y="{y+4:.1f}" text-anchor="end">{t}</text>')
    first_kate = next((c for c in reversed(commits) if c['author'] == "Kate's Claude"), None)
    for i, k in enumerate(keys):
        x = pad + 4 + i * bw; y0 = H - 24
        for name, col in SERIES:
            n = buckets[k][name]
            if not n: continue
            h = (H - 24 - top) * n / mx
            svg.append(f'<rect class="mark" x="{x+1:.1f}" y="{y0-h+1:.1f}" width="{max(bw-4,2):.1f}" height="{max(h-2,1):.1f}" rx="3" fill="var({col})"><title>{E(k[11:16])} UTC, {E(name)}: {n}</title></rect>')
            y0 -= h
        if first_kate and k == f"{first_kate['when'][:13]}:{int(first_kate['when'][14:16])//15*15:02d}":
            svg.append(f'<line x1="{x+bw/2:.1f}" x2="{x+bw/2:.1f}" y1="{top-8}" y2="{H-24}" stroke="var(--fg)" stroke-dasharray="3 3"/><text class="v" x="{x+bw/2-4:.1f}" y="{top-11}" text-anchor="end">Kate\'s first commit</text>')
        if k.endswith(':00') or len(keys) <= 8:
            svg.append(f'<text x="{x+bw/2:.1f}" y="{H-8}" text-anchor="middle">{E(k[11:16])}</text>')
    present = [(n, c) for n, c in SERIES if any(buckets[k][n] for k in keys)]
    rows = [(k.replace('T', ' '), *[buckets[k][n] for n, _ in present]) for k in keys]
    return card('Commits over time', 'In 15-minute steps (UTC), by who made them. The dashed line marks the first change made by Kate\'s own Claude.',
                legend(present) + f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Commits over time by author">{"".join(svg)}</svg>' + table(['From (UTC)', *[n for n, _ in present]], rows))


def churn(commits):
    cs = list(reversed(commits)); W, H, pad = 640, 200, 48
    mx = max([max(c['added'], c['removed']) for c in cs] or [1]); mid = H / 2; bw = (W - pad) / max(len(cs), 1)
    svg = [f'<line x1="{pad}" x2="{W}" y1="{mid}" y2="{mid}" stroke="var(--grid)"/>',
           f'<text x="{pad-6}" y="{16}" text-anchor="end">+{mx:,}</text><text x="{pad-6}" y="{H-4}" text-anchor="end">-{mx:,}</text><text x="{pad-6}" y="{mid+4}" text-anchor="end">0</text>']
    for i, c in enumerate(cs):
        x = pad + i * bw
        ha = (mid - 8) * c['added'] / mx; hr = (mid - 8) * c['removed'] / mx
        t = f"{c['commit']} {c['author']}: +{c['added']:,} / -{c['removed']:,}, {c['subject'][:60]}"
        svg.append(f'<rect class="mark" x="{x+1:.1f}" y="{mid-ha-1:.1f}" width="{max(bw-2,1.5):.1f}" height="{max(ha,1):.1f}" rx="2" fill="var(--s3)"><title>{E(t)}</title></rect>')
        svg.append(f'<rect class="mark" x="{x+1:.1f}" y="{mid+1:.1f}" width="{max(bw-2,1.5):.1f}" height="{max(hr,1):.1f}" rx="2" fill="var(--s2)"><title>{E(t)}</title></rect>')
    tot_a = sum(c['added'] for c in cs); tot_r = sum(c['removed'] for c in cs)
    return card('Lines added and removed', f'Per commit, oldest on the left: {tot_a:,} lines added and {tot_r:,} removed in all.',
                legend([('Added', '--s3'), ('Removed', '--s2')]) + f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Lines added and removed per commit">{"".join(svg)}</svg>'
                + table(['Commit', 'Who', 'Added', 'Removed'], [(c['commit'], c['author'], c['added'], c['removed']) for c in cs]))


def recent(commits):
    li = ''.join(f'<li><a href="{REPO}/commit/{c["commit"]}"><code>{c["commit"]}</code></a><span>{E(c["subject"])}<span class="who">{E(c["author"])} · {E(c["when"][:16].replace("T", " "))} UTC</span></span></li>' for c in commits[:10])
    return card('Recent commits', 'The last ten changes, newest first. Each links to GitHub.', f'<ul class="commits">{li}</ul>')


def squarify(items, x, y, w, h):
    """Squarified treemap layout. items are (name, value, kind); returns (name, value, kind, x, y, w, h)."""
    out = []; items = [i for i in items if i[1] > 0]
    total = sum(i[1] for i in items)
    if not items or total <= 0: return out
    scale = w * h / total; vals = [(i, i[1] * scale) for i in items]

    def worst(row, side):
        s = sum(a for _, a in row)
        return max(max(side * side * a / (s * s), s * s / (side * side * a)) for _, a in row)
    while vals:
        side = min(w, h); row = [vals.pop(0)]
        while vals and worst(row + [vals[0]], side) <= worst(row, side):
            row.append(vals.pop(0))
        s = sum(a for _, a in row)
        if w >= h:
            cw = s / h; yy = y
            for it, a in row:
                hh = a / cw; out.append((*it, x, yy, cw, hh)); yy += hh
            x += cw; w -= cw
        else:
            ch = s / w; xx = x
            for it, a in row:
                ww = a / ch; out.append((*it, xx, y, ww, ch)); xx += ww
            y += ch; h -= ch
    return out


def treemap(tree):
    def kind(p):
        if re.search(r'\.(webp|jpg|jpeg|png|svg)$', p): return 'Images'
        if p.endswith('.html'): return 'Pages'
        if p.endswith(('.json', '.md', '.txt')): return 'Data and text'
        return 'Other'
    groups = collections.defaultdict(int)
    for t in tree:
        folder = t['path'].split('/')[0] if '/' in t['path'] else '(top)'
        if t['path'].startswith(('admin/guide/', 'img/designs/')): folder = '/'.join(t['path'].split('/')[:2])
        groups[(folder, kind(t['path']))] += t['bytes']
    items = sorted(((f'{f} · {k}', v, k) for (f, k), v in groups.items()), key=lambda x: -x[1])
    W, H = 640, 300
    rects = squarify(items, 0, 0, W, H)
    col = {'Images': '--s1', 'Pages': '--s2', 'Data and text': '--s3', 'Other': '--s4'}
    svg = []
    for name, v, k, x, y, w, h in rects:
        svg.append(f'<rect class="mark" x="{x+1:.1f}" y="{y+1:.1f}" width="{max(w-2,0):.1f}" height="{max(h-2,0):.1f}" rx="4" fill="var({col[k]})"><title>{E(name)}: {kb(v)}</title></rect>')
        if w > 74 and h > 34:
            label = name.split(' · ')[0]
            label = label if len(label) * 7 < w - 10 else label[:max(int((w - 10) / 7) - 1, 1)] + '.'
            svg.append(f'<text class="w" x="{x+7:.1f}" y="{y+17:.1f}">{E(label)}</text><text class="w" x="{x+7:.1f}" y="{y+31:.1f}" style="font-weight:400">{kb(v)}</text>')
    total = sum(t['bytes'] for t in tree)
    return card('What the site is made of', f'Every file in site/, grouped by folder and kind, sized by bytes: {kb(total)} in {len(tree)} files.',
                legend([(k, c) for k, c in col.items() if any(i[2] == k for i in items)]) + f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Treemap of the site by folder and size">{"".join(svg)}</svg>'
                + table(['Folder and kind', 'Size'], [(n, kb(v)) for n, v, _ in items]), wide=True)


def page_weight(site):
    pages = [('Home: The Workflow Board', 'index.html'), ('The Transcript', 'designs/1.html'), ('The Edit Window', 'designs/2.html'),
             ('The Newsroom', 'designs/newsroom.html'), ('The Brief', 'designs/5.html'), ('Start here', 'start/index.html'), ('Use with your AI', 'agents/index.html')]
    items = []
    for name, f in pages:
        p = os.path.join(site, f)
        if not os.path.exists(p): continue
        s = open(p, encoding='utf-8').read(); size = len(s.encode())
        for src in set(re.findall(r'src="([^"]+\.(?:webp|jpg|png|svg))"', s)):
            if 'img/designs/' in src: continue
            q = os.path.normpath(os.path.join(os.path.dirname(p), src))
            if os.path.exists(q): size += os.path.getsize(q)
        items.append((name, size / 1024))
    W, row, lw = 640, 30, 190; budget = 1000; H = row * len(items) + 26
    sc = (W - lw - 60) / budget; svg = []
    for i, (n, v) in enumerate(items):
        y = i * row + 4
        svg.append(f'<text x="{lw-8}" y="{y+17}" text-anchor="end">{E(n)}</text><rect class="mark" x="{lw}" y="{y+4}" width="{max(v*sc,2):.1f}" height="{row-12}" rx="4" fill="var(--s1)"><title>{E(n)}: {v:,.0f} KB</title></rect><text class="v" x="{lw+v*sc+6:.1f}" y="{y+17}">{v:,.0f} KB</text>')
    bx = lw + budget * sc
    svg.append(f'<line x1="{bx:.1f}" x2="{bx:.1f}" y1="0" y2="{H-20}" stroke="var(--bad)" stroke-dasharray="4 3"/><text x="{bx:.1f}" y="{H-6}" text-anchor="end">1 MB budget</text>')
    return card('Page weight', 'What a visitor downloads to see each page (HTML and images), against the 1 MB budget.',
                f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Page weight per page">{"".join(svg)}</svg>' + table(['Page', 'KB'], [(n, f'{v:,.0f}') for n, v in items]))


def gallery(images):
    figs = []
    for im in sorted(images, key=lambda x: (x['path'].startswith('img/designs/'), x['path'])):
        figs.append(f'<figure><img src="../{E(im["path"])}" alt="" loading="lazy" decoding="async"><figcaption><b>{E(im["path"])}</b>{E(kb(im["bytes"]))}{" · " + E(im["dims"]) if im["dims"] else ""}<br>{E(im["credit"])}</figcaption></figure>')
    return card('Images', f'All {len(images)} images on the site, with size, dimensions and credit.', f'<div class="gallery">{"".join(figs)}</div>', wide=True)


def designs():
    D = [('The Workflow Board', 'board', '../', True), ('The Transcript', 'transcript', '../designs/1.html', False), ('The Edit Window', 'edit', '../designs/2.html', False),
         ('The Newsroom', 'newsroom', '../designs/newsroom.html', False), ('The Brief', 'brief', '../designs/5.html', False)]
    figs = ''.join(f'<figure><a href="{h}" aria-label="{E(n)}"><img src="../img/designs/{s}.webp" alt="" loading="lazy"></a><figcaption><b>{E(n)}{"<span class=live>Home</span>" if live else ""}</b></figcaption></figure>' for n, s, h, live in D)
    return card('The five designs', 'The same facts, five ways. Visitors switch with "Choose a design"; the home page is marked.', f'<div class="gallery">{figs}</div>')


def datasets(ds):
    rows = ''.join(f'<tr><td><code>{E(d["path"])}</code></td><td>{d["records"]} {E(d["unit"])}</td><td>{E(kb(d["bytes"])) if d["bytes"] else ""}</td></tr>' for d in ds)
    prev = ''.join(f'<details><summary>Preview {E(d["path"])}</summary><pre><code>{E(d["preview"])}</code></pre></details>' for d in ds if d['bytes'])
    return card('Data files', 'The machine-readable files on the site, for agents and for this dashboard.', f'<div class="wrapx"><table><tr><th>File</th><th>Records</th><th>Size</th></tr>{rows}</table></div>{prev}')


def quality(checks):
    if not checks:
        return card('Checks over time', 'Run <code>node tools/check.js</code> to record the first check.', '')
    W, H, pad, top = 640, 200, 34, 16
    series = [('problems', 'Pages with problems', '--s2'), ('broken_links', 'Broken links', '--s1'), ('small_targets', 'Small links', '--s3')]
    mx = max([max(c[k] for k, _, _ in series) for c in checks] + [3]); n = len(checks)
    xs = lambda i: pad + 14 + (W - pad - 28) * (i / (n - 1) if n > 1 else .5)
    ys = lambda v: H - 26 - (H - 26 - top) * v / mx
    svg = []
    for t in range(0, mx + 1, max(1, mx // 3)):
        svg.append(f'<line x1="{pad}" x2="{W}" y1="{ys(t):.1f}" y2="{ys(t):.1f}" stroke="var(--grid)"/><text x="{pad-6}" y="{ys(t)+4:.1f}" text-anchor="end">{t}</text>')
    for j, (k, name, col) in enumerate(series):
        if n > 1:
            svg.append(f'<polyline points="{" ".join(f"{xs(i):.1f},{ys(c[k]):.1f}" for i, c in enumerate(checks))}" fill="none" stroke="var({col})" stroke-width="2"/>')
        for i, c in enumerate(checks):
            svg.append(f'<circle class="mark" cx="{xs(i)+(j-1)*6:.1f}" cy="{ys(c[k]):.1f}" r="4.5" fill="var({col})" stroke="var(--paper)" stroke-width="2"><title>{E(c["commit"])} {E(c["when"])}: {name} {c[k]}</title></circle>')
    for i, c in enumerate(checks):
        if n <= 8 or i in (0, n - 1):
            svg.append(f'<text x="{xs(i):.1f}" y="{H-8}" text-anchor="middle">{E(c["commit"])}</text>')
    last = checks[-1]
    return card('Checks over time', f'Each run of tools/check.js covers {last["views"]} page views: every page at 320, 390 and 1366 px, light and dark. Latest run, at {E(last["commit"])}: {last["problems"]} problems.',
                legend([(n2, c) for _, n2, c in series]) + f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Check results over time">{"".join(svg)}</svg>'
                + table(['When', 'Commit', 'Views', 'Problems', 'Broken links', 'Small links', 'Sideways scroll', 'Other-site requests'],
                        [(c['when'], c['commit'], c['views'], c['problems'], c['broken_links'], c['small_targets'], c['overflow'], c['external_requests']) for c in checks]))


def previews(site):
    s = open(os.path.join(site, 'index.html'), encoding='utf-8').read()
    g = lambda prop: (re.search(r'<meta (?:property|name)="' + re.escape(prop) + r'" content="([^"]*)"', s) or [None, ''])[1]
    t, d = html.unescape(g('og:title')), html.unescape(g('og:description'))
    wa = f'<div class="preview wa"><img src="../img/share-card.jpg" alt="The link preview picture: Kate at her desk with her name and line"><div><b>{E(t)}</b><p>{E(d)}</p><p class="dom">kate-curtis-evans.founder.sovereignweb.site</p></div></div>'
    li = f'<div class="preview"><img src="../img/share-card.jpg" alt=""><div><b>{E(t)}</b><p class="dom">kate-curtis-evans.founder.sovereignweb.site</p></div></div>'
    return card('Link preview', 'How the home page looks when shared, from its own share tags: WhatsApp style, then LinkedIn style.', f'<div style="display:grid;gap:.8rem">{wa}{li}</div>')


def rounds_card():
    W, H, pad, top = 640, 210, 30, 18; n = len(ROUNDS)
    xs = lambda i: pad + 20 + (W - pad - 40) * i / (n - 1); ys = lambda v: H - 28 - (H - 28 - top) * v / 5
    svg = []
    for t in range(6):
        svg.append(f'<line x1="{pad}" x2="{W}" y1="{ys(t):.1f}" y2="{ys(t):.1f}" stroke="var(--grid)"/><text x="{pad-6}" y="{ys(t)+4:.1f}" text-anchor="end">{t}</text>')
    svg.append(f'<polyline points="{" ".join(f"{xs(i):.1f},{ys(r):.1f}" for i, (_, r, _) in enumerate(ROUNDS))}" fill="none" stroke="var(--s1)" stroke-width="2"/>')
    for i, (rd, r, u) in enumerate(ROUNDS):
        svg.append(f'<circle class="mark" cx="{xs(i):.1f}" cy="{ys(r):.1f}" r="5" fill="var(--s1)" stroke="var(--paper)" stroke-width="2"><title>Round {rd}: rating {r} of 5</title></circle><text x="{xs(i):.1f}" y="{H-10}" text-anchor="middle">R{rd}</text>')
        if u:
            m = sum(u) / len(u)
            svg.append(f'<rect class="mark" x="{xs(i)-5:.1f}" y="{ys(m)-5:.1f}" width="10" height="10" rx="2" fill="var(--s2)" stroke="var(--paper)" stroke-width="2" transform="rotate(45 {xs(i):.1f} {ys(m):.1f})"><title>Round {rd}: synthetic users {m:.1f} of 5</title></rect>')
    svg.append(f'<text class="v" x="{xs(n-1)-8:.1f}" y="{ys(4)-10:.1f}" text-anchor="end">Signed off at 4</text>')
    return card('Design rounds', 'The design team\'s rating after each of its eight rounds, and the mean synthetic-user score where it ran them, out of 5. <a href="https://design.agents.sovereignweb.site/back-office.html">Full records</a>.',
                legend([('Design rating', '--s1'), ('Synthetic users (mean)', '--s2')]) + f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Design rating by round">{"".join(svg)}</svg>'
                + table(['Round', 'Rating', 'Synthetic users'], [(r, a, '' if not u else f'{sum(u)/len(u):.1f} ({", ".join(map(str, u))})') for r, a, u in ROUNDS]))


def personas_card():
    runs = [(r, u) for r, _, u in ROUNDS if u]
    W, lw, row = 640, 170, 22; H = len(PERSONAS) * (row * len(runs) + 10) + 4
    cols = ['--s1', '--s2', '--s3']; sc = (W - lw - 30) / 5; svg = []; y = 0
    for pi, p in enumerate(PERSONAS):
        svg.append(f'<text x="{lw-8}" y="{y + row*len(runs)/2 + 5:.1f}" text-anchor="end">{E(p)}</text>')
        for ri, (r, u) in enumerate(runs):
            v = u[pi]
            svg.append(f'<rect class="mark" x="{lw}" y="{y+2:.1f}" width="{v*sc:.1f}" height="{row-5}" rx="4" fill="var({cols[ri]})"><title>{E(p)}, round {r}: {v} of 5</title></rect><text class="v" x="{lw+v*sc+5:.1f}" y="{y+row-8:.1f}">{v}</text>')
            y += row
        y += 10
    return card('Synthetic users', 'Five imagined visitors rated the home page in three rounds, each score out of 5. The visitor names follow the order of the round 2 record.',
                legend([(f'Round {r}', cols[i]) for i, (r, _) in enumerate(runs)]) + f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Synthetic user scores per visitor">{"".join(svg)}</svg>'
                + table(['Visitor', *[f'Round {r}' for r, _ in runs]], [(p, *[u[i] for _, u in runs]) for i, p in enumerate(PERSONAS)]))


def agents_card(commits):
    c = collections.Counter(x['author'] for x in commits); items = c.most_common()
    W, row, lw = 640, 34, 190; H = row * len(items) + 6; mx = max(c.values() or [1]); svg = []
    for i, (n, v) in enumerate(items):
        y = i * row + 4; w = (W - lw - 40) * v / mx
        svg.append(f'<text x="{lw-8}" y="{y+19}" text-anchor="end">{E(n)}</text><rect class="mark" x="{lw}" y="{y+5}" width="{max(w,2):.1f}" height="{row-14}" rx="4" fill="var({scol(n)})"><title>{E(n)}: {v} commits</title></rect><text class="v" x="{lw+w+6:.1f}" y="{y+19}">{v}</text>')
    roles = ''.join(f'<tr><td>{E(n)}</td><td>{v}</td><td>{E(ROLES.get(n, ""))}</td></tr>' for n, v in items)
    roles += '<tr><td>design.b</td><td>0</td><td>Ran eight design rounds and the synthetic users (reviews, not commits here)</td></tr><tr><td>hub.b, conductor.b, accountant.b</td><td>0</td><td>Showroom, signing keys, image budget</td></tr>'
    return card('Who worked on the site', 'Commits per author (names and agent ids only, never email addresses), and what each did.',
                f'<svg viewBox="0 0 {W} {H}" style="max-width:{W}px" role="img" aria-label="Commits per author">{"".join(svg)}</svg><div class="wrapx"><table><tr><th>Who</th><th>Commits</th><th>Role</th></tr>{roles}</table></div>', wide=True)


def ask_claude():
    cards = ''.join(f'<div class="prompt"><span class="grp">{E(g)}</span><q id="p{i}">{E(t)}</q><p>{E(n)}</p><button type="button" data-copy="p{i}">Copy</button></div>' for i, (g, t, n) in enumerate(PROMPTS))
    return (f'<div class="prompts">{cards}</div><p class="note">Paste a prompt into Kate\'s Claude, in a session on this repository, and fill in the "...". It shows the change and waits for a yes before publishing. Full guide: <a href="guide/index.html">Guide for your Claude</a>; interview: <a href="guide/09-interview.html">Interviewing Kate</a>.</p>'
            '<script>document.querySelectorAll("[data-copy]").forEach(b=>b.addEventListener("click",()=>{const el=document.getElementById(b.dataset.copy),t=el.textContent;'
            '(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(()=>{b.textContent="Copied";setTimeout(()=>b.textContent="Copy",1500)},()=>{const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent="Selected: press Ctrl+C"})}))</script>')


def visitors_card():
    W, H = 640, 160
    pts = ' '.join(f'{20 + i*600/13:.1f},{H - 30 - 50*(0.5+0.5*math.sin(i/2)):.1f}' for i in range(14))
    svg = f'<polyline points="{pts}" fill="none" stroke="var(--muted)" stroke-width="2" stroke-dasharray="5 4"/><line x1="20" x2="{W}" y1="{H-30}" y2="{H-30}" stroke="var(--grid)"/><text x="20" y="{H-10}">Visitors per day (an outline only: there is no data yet)</text>'
    return card('Visitors', 'Visitor numbers will appear here once privacy-friendly stats are switched on (no cookies, no tracking of individuals). Nothing is collected today.',
                f'<div class="ghost"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Placeholder for future visitor numbers">{svg}</svg></div>', wide=True)


def render(root, site, cols):
    data = collect(root, site, cols)
    commits = data['commits']
    head = git('rev-parse', '--short', 'HEAD', root=root).strip()
    built = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    version = {'site': 'kate-curtis-evans.founder.sovereignweb.site', 'built_from_commit': head, 'built_at': built, 'repository': REPO, 'branch': 'dev'}
    with open(os.path.join(site, 'version.json'), 'w') as f:
        json.dump(version, f, indent=1); f.write('\n')
    public = {k: v for k, v in data.items() if k != 'tree'}
    public['files'] = len(data['tree']); public['bytes'] = sum(t['bytes'] for t in data['tree']); public['version'] = version
    with open(os.path.join(site, 'admin', 'data.json'), 'w') as f:
        json.dump(public, f, indent=1); f.write('\n')
    kate = [c for c in commits if c['author'] == "Kate's Claude"]
    first = kate[-1]['when'][:16].replace('T', ' ') + ' UTC' if kate else 'not yet'
    last = data['checks'][-1] if data['checks'] else None
    chip = lambda ok, t: f'<span class="chip {"ok" if ok else "no"}">{"&#10003;" if ok else "&#10007;"} {E(t)}</span>'
    checks_chips = (chip(last['problems'] == 0, 'Pages') + chip(last['broken_links'] == 0, 'Links') + chip(last['external_requests'] == 0, 'No other sites') + chip(last['overflow'] == 0, 'Phones')) if last else ''
    pages = len([t for t in data['tree'] if t['path'].endswith('.html')])
    tiles = [(head, f'built from this commit, {built.replace("T", " ")}', ''), (str(len(kate)), "Kate's commits", f'first {first}'),
             (str(len(commits)), 'commits' + (' (in this copy)' if data['shallow'] else ''), ''), ('4 / 5', 'design rating, signed off', ''),
             (str(pages), 'pages', '5 designs'), (str(len(data['images'])), 'images', ''), (kb(public['bytes']), 'the whole site', f'{public["files"]} files'),
             ('Checks', 'latest run' + (f' at {last["commit"]}' if last else ': not run yet'), checks_chips)]
    k = '<div class="kpis">' + ''.join(f'<div class="kpi"><b>{E(v)}</b><span>{E(t)}</span>{f"<div class=chips>{x}</div>" if "chip" in x else (f"<span>{E(x)}</span>" if x else "")}</div>' for v, t, x in tiles) + '</div>'
    note = '<p class="note">This copy of the repository has shortened history, so the activity charts show only part of it. Run <code>git fetch --unshallow</code> and rebuild.</p>' if data['shallow'] else ''
    n = {c: len(v) for c, v in cols.items()}
    seg = ''.join(f'<div class="mark" style="flex:{n[s]};background:var({c})" title="{t}: {n[s]}"></div>' for s, t, c in (('open', 'Open', '--info'), ('blocked', 'Blocked', '--warn'), ('done', 'Done', '--good')) if n[s])
    nxt = ''.join(f'<li><a href="{REPO}/blob/dev/{it["file"]}">{E(it["title"])}</a></li>' for it in cols['open'][:5])
    board = card('Board', f'{sum(n.values())} tasks in issues/. Next up:', f'<div class="statusbar">{seg}</div>' + legend([(f'Open {n["open"]}', '--info'), (f'Blocked {n["blocked"]}', '--warn'), (f'Done {n["done"]}', '--good')]) + f'<ol>{nxt}</ol><p class="note"><a href="board.html" style="display:inline-block;min-height:24px;line-height:24px">Open the board</a></p>')
    sec = lambda i, t, sub, body: f'<section class="sec" id="{i}"><h2>{E(t)} <small>{sub}</small></h2>{body}</section>'
    body = (sec('overview', 'Overview', 'the site at a glance', k + note + '<div class="grid" style="margin-top:1rem">' + board + over_time(commits) + '</div>')
            + sec('activity', 'Activity', 'every change, from git', '<div class="grid">' + heatmap(commits) + churn(commits) + recent(commits) + '</div>')
            + sec('content', 'Content', 'pages, images, designs, data', '<div class="grid">' + treemap(data['tree']) + page_weight(site) + designs() + datasets(data['datasets']) + gallery(data['images']) + '</div>')
            + sec('quality', 'Quality', 'checks and link previews', '<div class="grid">' + quality(data['checks']) + previews(site) + '</div>')
            + sec('design', 'Design', 'the design team\'s rounds', '<div class="grid">' + rounds_card() + personas_card() + '</div>')
            + sec('agents', 'Agents', 'who worked on it', '<div class="grid">' + agents_card(commits) + '</div>')
            + sec('ask', 'Ask Claude', 'prompts Kate can copy', ask_claude())
            + sec('visitors', 'Visitors', 'not switched on yet', '<div class="grid">' + visitors_card() + '</div>')
            + '<p class="note">Made at build time from the repository by <code>python3 tools/backoffice.py</code>: git history, issues/, the files in site/, tools/check.js results and the design team\'s recorded rounds. The data is in <a href="data.json">data.json</a> and <a href="../version.json">version.json</a>.</p>')
    links = ('<p class="lab">Dashboard</p>' + ''.join(f'<a href="#{i}">{t}</a>' for i, t in [('overview', 'Overview'), ('activity', 'Activity'), ('content', 'Content'), ('quality', 'Quality'), ('design', 'Design'), ('agents', 'Agents'), ('ask', 'Ask Claude'), ('visitors', 'Visitors')])
             + '<hr><p class="lab">Admin</p><a href="board.html">Board</a><a href="guide/index.html">Guide for your Claude</a><a href="policy.html">Policy</a><a href="made.html">How it was made</a><a href="../start/">Start here</a><a href="../">Live site</a>')
    side = (f'<aside class="side"><nav class="desk" aria-label="Dashboard">{links}</nav><details class="phone"><summary>Menu</summary><nav aria-label="Dashboard menu">{links}</nav></details></aside>')
    _unused = ('<aside class="side"><details open><summary>Menu</summary><nav aria-label="Dashboard">'
            '<p class="lab">Dashboard</p>' + ''.join(f'<a href="#{i}">{t}</a>' for i, t in [('overview', 'Overview'), ('activity', 'Activity'), ('content', 'Content'), ('quality', 'Quality'), ('design', 'Design'), ('agents', 'Agents'), ('ask', 'Ask Claude'), ('visitors', 'Visitors')])
            + '<hr><p class="lab">Admin</p><a href="board.html">Board</a><a href="guide/index.html">Guide for your Claude</a><a href="policy.html">Policy</a><a href="made.html">How it was made</a><a href="../start/">Start here</a><a href="../">Live site</a></nav></details></aside>')
    return f'<div class="app">{side}<div class="content"><h1>Admin</h1><p class="lede">The dashboard for Kate\'s site, for Kate and her Claude. Visitors do not need anything here.</p>{body}</div></div>'
