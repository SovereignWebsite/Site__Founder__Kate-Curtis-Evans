"""Dashboard charts for the admin area: inline SVG from real repository data, no scripts.

Used by tools/backoffice.py. Every number comes from the repository (git history, issues/, the files
in site/) or from the design team's recorded rounds (listed in ROUNDS, with their source pages).
Hover a mark for its value (SVG <title>); every chart has a table view underneath.
"""
import html, os, re, subprocess, glob, collections

E = html.escape

# Design rounds, from https://design.agents.sovereignweb.site/back-office.html (round pages linked in made.html).
# rating: the rating recorded at the end of the round. users: mean synthetic-user score, where a round ran them.
ROUNDS = [(1, 2, None), (2, 2, 4.0), (3, 2, None), (4, 2, None), (5, 4, 3.8), (6, 3, None), (7, 3, 4.0), (8, 4, None)]

CSS = '''
.dash{--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--grid:#e6e3db;--axis:#8f8b82;--good:#2f7a42;--warn:#9a5f00;--info:#2a78d6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .dash{--s1:#3987e5;--s2:#d95926;--s3:#199e70;--grid:#2f2d29;--axis:#8a857b;--good:#6cc283;--warn:#f0b866;--info:#6ea8e6}}
.kpis{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fit,minmax(10.5rem,1fr));margin:1rem 0 1.4rem}
.kpi{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:.8rem 1rem}
.kpi b{display:block;font-size:1.9rem;line-height:1.1;font-variant-numeric:tabular-nums}
.kpi span{display:block;color:var(--muted);font-size:.9rem;margin-top:.2rem}
.panels{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,30rem),1fr))}
.panel{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:1rem 1.1rem}
.panel h2{margin:0 0 .2rem;font-size:1.02rem}.panel .sub{margin:0 0 .6rem;color:var(--muted);font-size:.9rem}
.panel svg{display:block;width:100%;height:auto;overflow:visible}
.panel svg text{font:12px var(--sans);fill:var(--muted)}.panel svg .v{fill:var(--fg);font-weight:600}
.legend{display:flex;gap:1rem;flex-wrap:wrap;font-size:.88rem;color:var(--muted);margin:.2rem 0 .4rem}
.legend i{display:inline-block;width:.8rem;height:.8rem;border-radius:3px;margin-right:.35rem;vertical-align:-.1rem}
.panel details{margin-top:.5rem;font-size:.9rem}.panel summary{cursor:pointer;color:var(--muted);min-height:24px;line-height:24px}
.panel table{font-size:.88rem}.note{font-size:.85rem;color:var(--muted)}
.status{display:flex;height:22px;border-radius:6px;overflow:hidden;gap:2px;margin:.4rem 0}
.status div{min-width:2px}
.mark:hover{opacity:.8}
'''


def git(*a, root):
    return subprocess.run(['git', *a], cwd=root, capture_output=True, text=True).stdout


def history(root):
    out = git('log', '--format=@@%h|%aI|%an', '--numstat', root=root)
    commits = []
    for block in out.split('@@')[1:]:
        lines = block.strip().split('\n')
        h, when, who = lines[0].split('|', 2)
        files = [l.split('\t')[2] for l in lines[1:] if l.count('\t') == 2]
        commits.append({'h': h, 'when': when, 'who': who, 'files': files})
    shallow = git('rev-parse', '--is-shallow-repository', root=root).strip() == 'true'
    return commits, shallow


def who_group(name):
    n = name.lower()
    if n.startswith('claude') or 'kate' == n:
        return 'kate'
    if n.endswith('.b') or '.b@' in n:
        return 'agents'
    return 'setup'


def legend(items):
    return '<div class="legend">' + ''.join(f'<span><i style="background:var({c})"></i>{E(n)}</span>' for n, c in items) + '</div>'


def table(head, rows):
    h = ''.join(f'<th>{E(x)}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{E(str(c))}</td>' for c in r) + '</tr>' for r in rows)
    return f'<details><summary>Show as a table</summary><div class="wrapx"><table><tr>{h}</tr>{b}</table></div></details>'


def commits_by_hour(commits):
    buckets = collections.OrderedDict()
    for c in reversed(commits):
        q = int(c['when'][14:16]) // 15 * 15
        key = f"{c['when'][:13]}:{q:02d}"  # YYYY-MM-DDTHH:MM, 15-minute buckets
        g = who_group(c['who'])
        buckets.setdefault(key, collections.Counter())[g] += 1
    keys = list(buckets)
    W, H, pad, top = 640, 220, 34, 14
    mx = max([sum(v.values()) for v in buckets.values()] or [1])
    bw = (W - pad - 8) / max(len(keys), 1)
    series = [('agents', '--s1', 'Agents'), ('kate', '--s2', "Kate's Claude"), ('setup', '--s3', 'Factory set-up')]
    svg = []
    for t in range(0, mx + 1, max(1, (mx + 3) // 4)):
        y = H - 24 - (H - 24 - top) * t / mx
        svg.append(f'<line x1="{pad}" x2="{W}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--grid)"/><text x="{pad-6}" y="{y+4:.1f}" text-anchor="end">{t}</text>')
    for i, k in enumerate(keys):
        x = pad + 4 + i * bw
        y0 = H - 24
        for s, col, name in series:
            n = buckets[k][s]
            if not n:
                continue
            h = (H - 24 - top) * n / mx
            svg.append(f'<rect class="mark" x="{x+1:.1f}" y="{y0-h+1:.1f}" width="{max(bw-4,2):.1f}" height="{max(h-2,1):.1f}" rx="3" fill="var({col})"><title>{E(k[11:16])} UTC, {E(name)}: {n} commit{"s" if n != 1 else ""}</title></rect>')
            y0 -= h
        if k.endswith(':00') or len(keys) <= 8:
            svg.append(f'<text x="{x+bw/2:.1f}" y="{H-8}" text-anchor="middle">{E(k[11:16])}</text>')
    rows = [(k[:10] + ' ' + k[11:16], buckets[k]['agents'], buckets[k]['kate'], buckets[k]['setup']) for k in keys]
    present = [(n, c) for s, c, n in series if any(buckets[k][s] for k in keys)]
    return (f'<h2>Commits over time</h2><p class="sub">Every change to the site in 15-minute steps (UTC), and who made it.</p>{legend(present)}'
            f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Commits in 15-minute steps, stacked by who made them">{"".join(svg)}</svg>'
            + table(['From (UTC)', 'Agents', "Kate's Claude", 'Set-up'], rows))


def hbars(title, sub, items, unit, col='--s1', fmt=str):
    W, row = 640, 30
    H = row * len(items) + 8
    mx = max([v for _, v in items] or [1])
    label_w = 210
    svg = []
    for i, (name, v) in enumerate(items):
        y = i * row + 4
        w = (W - label_w - 70) * v / mx
        svg.append(f'<text x="{label_w-8}" y="{y+17}" text-anchor="end">{E(name if len(name) < 32 else "..." + name[-29:])}</text>'
                   f'<rect class="mark" x="{label_w}" y="{y+4}" width="{max(w,2):.1f}" height="{row-12}" rx="4" fill="var({col})"><title>{E(name)}: {E(fmt(v))} {E(unit)}</title></rect>'
                   f'<text class="v" x="{label_w+w+6:.1f}" y="{y+17}">{E(fmt(v))}</text>')
    return (f'<h2>{E(title)}</h2><p class="sub">{E(sub)}</p><svg viewBox="0 0 {W} {H}" role="img" aria-label="{E(title)}">{"".join(svg)}</svg>'
            + table(['Name', unit], [(n, fmt(v)) for n, v in items]))


def rounds_chart():
    W, H, pad, top = 640, 220, 34, 16
    n = len(ROUNDS)
    xs = lambda i: pad + 20 + (W - pad - 40) * i / (n - 1)
    ys = lambda v: H - 28 - (H - 28 - top) * v / 5
    svg = []
    for t in range(0, 6):
        svg.append(f'<line x1="{pad}" x2="{W}" y1="{ys(t):.1f}" y2="{ys(t):.1f}" stroke="var(--grid)"/><text x="{pad-6}" y="{ys(t)+4:.1f}" text-anchor="end">{t}</text>')
    pts = ' '.join(f'{xs(i):.1f},{ys(r):.1f}' for i, (_, r, _) in enumerate(ROUNDS))
    svg.append(f'<polyline points="{pts}" fill="none" stroke="var(--s1)" stroke-width="2" stroke-linejoin="round"/>')
    for i, (rd, r, u) in enumerate(ROUNDS):
        svg.append(f'<circle class="mark" cx="{xs(i):.1f}" cy="{ys(r):.1f}" r="5" fill="var(--s1)" stroke="var(--paper)" stroke-width="2"><title>Round {rd}: rating {r} of 5</title></circle>')
        if u is not None:
            svg.append(f'<rect class="mark" x="{xs(i)-5:.1f}" y="{ys(u)-5:.1f}" width="10" height="10" rx="2" fill="var(--s2)" stroke="var(--paper)" stroke-width="2" transform="rotate(45 {xs(i):.1f} {ys(u):.1f})"><title>Round {rd}: synthetic users {u} of 5</title></rect>')
        svg.append(f'<text x="{xs(i):.1f}" y="{H-10}" text-anchor="middle">R{rd}</text>')
    svg.append(f'<text class="v" x="{xs(n-1)-8:.1f}" y="{ys(4)-10:.1f}" text-anchor="end">Signed off at 4</text>')
    return ('<h2>Design rounds</h2><p class="sub">The design team\'s rating at the end of each round, and the mean score from its synthetic users (five imagined visitors) where it ran them. Out of 5.</p>'
            + legend([('Design rating', '--s1'), ('Synthetic users', '--s2')])
            + f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Design rating and synthetic user score by round">{"".join(svg)}</svg>'
            + table(['Round', 'Rating', 'Synthetic users'], [(r, a, '' if u is None else u) for r, a, u in ROUNDS]))


def page_weights(site):
    pages = [('Home: The Workflow Board', 'index.html'), ('The Transcript', 'designs/1.html'), ('The Edit Window', 'designs/2.html'),
             ('The Newsroom', 'designs/newsroom.html'), ('The Brief', 'designs/5.html'), ('Start here', 'start/index.html'),
             ('Use with your AI', 'agents/index.html')]
    items = []
    for name, f in pages:
        p = os.path.join(site, f)
        if not os.path.exists(p):
            continue
        s = open(p, encoding='utf-8').read()
        size = len(s.encode())
        imgs = set(re.findall(r'src="([^"]+\.(?:webp|jpg|png|svg))"', s))
        for src in imgs:
            if 'img/designs/' in src:
                continue  # chooser thumbnails load only when the panel opens
            q = os.path.normpath(os.path.join(os.path.dirname(p), src))
            if os.path.exists(q):
                size += os.path.getsize(q)
        items.append((name, round(size / 1024)))
    return hbars('Page weight', 'What a visitor downloads to see each page: HTML plus images, in KB. The limit is 1,000 KB; under 200 is fast on a phone.', items, 'KB', '--s1', lambda v: f'{v:,}')


def busiest_files(commits):
    c = collections.Counter(f for x in commits for f in x['files'] if not f.startswith('site/img/'))
    items = c.most_common(8)
    return hbars('Most-changed files', 'How many commits touched each file. The design pages and the top bar changed most.', items, 'commits', '--s3')


def issue_status(cols, colours=(('open', 'Open', '--info'), ('blocked', 'Blocked', '--warn'), ('done', 'Done', '--good'))):
    total = sum(len(v) for v in cols.values()) or 1
    seg = ''.join(f'<div class="mark" style="flex:{len(cols[k])};background:var({c})" title="{E(n)}: {len(cols[k])}"></div>' for k, n, c in colours if cols[k])
    lab = ''.join(f'<span><i style="background:var({c})"></i>{E(n)} {len(cols[k])}</span>' for k, n, c in colours)
    pr = collections.Counter(it.get('priority', 'normal') for it in cols['open'] + cols['blocked'])
    prow = ', '.join(f'{pr[p]} {p}' for p in ('urgent', 'high', 'normal', 'low') if pr[p])
    return (f'<h2>Board</h2><p class="sub">{total} tasks in issues/. Still to do by priority: {E(prow or "none")}.</p>'
            f'<div class="status" role="img" aria-label="Tasks by status">{seg}</div><div class="legend">{lab}</div>'
            f'<p class="note"><a href="board.html" style="display:inline-block;min-height:24px;line-height:24px">Open the board</a></p>'
            + table(['Status', 'Tasks'], [(n, len(cols[k])) for k, n, _ in colours]))


def render(root, site, cols):
    commits, shallow = history(root)
    by = collections.Counter(who_group(c['who']) for c in commits)
    pages = len(glob.glob(os.path.join(site, '**', '*.html'), recursive=True))
    weight = sum(os.path.getsize(p) for p in glob.glob(os.path.join(site, '**', '*'), recursive=True) if os.path.isfile(p))
    first = commits[-1]['when'][:16].replace('T', ' ') if commits else ''
    kpis = [(str(len(commits)), 'commits' + (' (in this copy)' if shallow else '')), (str(by['kate']), "by Kate's Claude"),
            ('5', 'designs, one chooser'), ('4 / 5', 'design rating, signed off'), (str(len(cols['open'])), 'open tasks'),
            (str(pages), 'pages'), (f'{weight/1024/1024:.1f} MB', 'the whole site')]
    k = '<div class="kpis">' + ''.join(f'<div class="kpi"><b>{E(v)}</b><span>{E(t)}</span></div>' for v, t in kpis) + '</div>'
    note = ('<p class="note">This copy of the repository has shortened history, so the commit charts show only part of it. Run <code>git fetch --unshallow</code> and rebuild to see all of it.</p>' if shallow else '')
    panels = [commits_by_hour(commits), rounds_chart(), issue_status(cols), page_weights(site), busiest_files(commits)]
    return (k + note + '<div class="panels">' + ''.join(f'<section class="panel">{p}</section>' for p in panels) + '</div>'
            + f'<p class="note">From the repository history since {E(first)} UTC, the files in issues/ and site/, and the design team\'s recorded rounds. Rebuilt by <code>python3 tools/backoffice.py</code>.</p>')
