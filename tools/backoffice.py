#!/usr/bin/env python3
"""Build the back office (site/admin/) from files in the repository. No dependencies.

    python3 tools/backoffice.py        (run from the repository root)

Writes:
  site/admin/index.html        the back office: board summary, guide, policy, how the site was made
  site/admin/board.html        the Issues-FS kanban board, from issues/{open,blocked,done}/*.md
  site/admin/guide/*.html      the guide for Kate's Claude, from site/admin/guide/*.md
  site/admin/policy.html       from site/admin/policy.md
  site/admin/made.html         the agents, the design rounds and every commit (from git log)

Issues follow Issues-FS lite (https://issues-fs.sgit.ai/): one Markdown file per issue, YAML
front matter (created, priority, source, estimated_effort, blocked_on), the title as the # heading.
The folder is the status: open, blocked, done. Move a file with git mv to change its column.
"""
import html, os, re, subprocess, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
ADMIN = os.path.join(SITE, 'admin')
U = 'https://kate-curtis-evans.founder.sovereignweb.site'
REPO = 'https://github.com/SovereignWebsite/Site__Founder__Kate-Curtis-Evans'
COLUMNS = [('open', 'Open'), ('blocked', 'Blocked'), ('done', 'Done')]
PRIORITY = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}

CSS = '''
:root{--bg:#f6f5f1;--paper:#fff;--fg:#1c1b19;--muted:#57544d;--line:#e2ded4;--accent:#9a3b1f;--chip:#efebe2;
--open:#2f6fb0;--blocked:#9a5f00;--done:#2f7a42;--sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
--mono:ui-monospace,Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141412;--paper:#1d1c1a;--fg:#ecebe6;--muted:#b3ada2;--line:#2f2d29;--accent:#e58a63;--chip:#2a2825;--open:#6ea8e6;--blocked:#f0b866;--done:#6cc283}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 var(--sans);overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:.18em;overflow-wrap:anywhere}
a:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:3px}
.skip{position:absolute;left:-999px}.skip:focus{left:1rem;top:1rem;background:var(--paper);padding:.4rem .7rem}
header.bo{border-bottom:1px solid var(--line);background:var(--paper)}
header.bo div{max-width:68rem;margin:0 auto;padding:.7rem 1rem;display:flex;flex-wrap:wrap;gap:.3rem 1rem;align-items:center}
header.bo .t{font-weight:700;margin-right:auto}
header.bo nav a{display:inline-block;min-height:28px;line-height:28px;padding:0 .5rem;border-radius:6px;color:var(--fg);text-decoration:none}
header.bo nav a:hover,header.bo nav a[aria-current="page"]{background:var(--chip)}
main{max-width:68rem;margin:0 auto;padding:1.6rem 1rem 3rem}
h1{font-size:clamp(1.6rem,4vw,2.1rem);line-height:1.2;margin:0 0 .4rem}
h2{font-size:1.2rem;margin:2rem 0 .6rem}h3{font-size:1rem;margin:1.4rem 0 .4rem}
p,li{max-width:46rem}.lede{color:var(--muted);margin:0 0 1.4rem}
code{font:.9em var(--mono);background:var(--chip);padding:.05rem .3rem;border-radius:4px;overflow-wrap:anywhere}
pre{background:var(--chip);padding:.8rem 1rem;border-radius:8px;overflow-x:auto;font:.88em/1.5 var(--mono)}pre code{background:none;padding:0}
blockquote{margin:1rem 0;padding:.6rem 1rem;border-left:3px solid var(--accent);background:var(--paper)}
table{border-collapse:collapse;width:100%;font-size:.95rem;margin:.6rem 0}th,td{text-align:left;padding:.45rem .5rem;border-bottom:1px solid var(--line);vertical-align:top}
.wrapx{overflow-x:auto}
.tiles{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));margin:1rem 0}
.tile{display:block;background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:1rem 1.1rem;color:var(--fg);text-decoration:none}
.tile:hover,.tile:focus-visible{border-color:var(--accent)}
.tile b{display:block;font-size:1.05rem;margin-bottom:.2rem}.tile span{color:var(--muted);font-size:.95rem}
.counts{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.5rem}
.pill{display:inline-block;font-size:.85rem;font-weight:650;padding:0 .55rem;border-radius:999px;background:var(--chip);color:var(--fg);border:1px solid var(--line)}
.board{display:grid;gap:1rem;grid-template-columns:repeat(3,minmax(0,1fr));align-items:start}
@media (max-width:52rem){.board{grid-template-columns:1fr}}
.col{background:var(--chip);border-radius:12px;padding:.7rem}
.col h2{margin:.1rem .2rem .7rem;font-size:.95rem;letter-spacing:.06em;text-transform:uppercase;display:flex;justify-content:space-between}
.col.open h2{color:var(--open)}.col.blocked h2{color:var(--blocked)}.col.done h2{color:var(--done)}
.card{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:.7rem .8rem;margin:0 0 .6rem}
.card h3{margin:0 0 .3rem;font-size:1rem}.card p{margin:.3rem 0;font-size:.93rem}
.meta{display:flex;flex-wrap:wrap;gap:.3rem;margin:.2rem 0 .3rem}
.pr-urgent,.pr-high{border-color:var(--accent);color:var(--accent)}
.wait{font-size:.9rem;color:var(--blocked)}.file{font:.8rem var(--mono);color:var(--muted)}
footer{border-top:1px solid var(--line);margin-top:2.5rem;padding-top:1rem;color:var(--muted);font-size:.9rem}
footer a{display:inline-block;min-height:24px;line-height:24px}
li a,td a,nav a,.file a{display:inline-block;min-height:24px;line-height:24px}
'''


def page(title, desc, body, cur, depth=1):
    up = '../' * depth
    nav = [('index.html', 'Back office'), ('board.html', 'Board'), ('guide/index.html', 'Guide'),
           ('policy.html', 'Policy'), ('made.html', 'How it was made')]
    base = '' if depth == 1 else '../'
    links = ''.join(f'<a href="{base}{h}"{" aria-current=\"page\"" if h == cur else ""}>{n}</a>' for h, n in nav)
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}, Kate Curtis-Evans</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="noindex">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="bo"><div><span class="t">Kate Curtis-Evans · back office</span>
<nav aria-label="Back office">{links}<a href="{up}">Live site</a></nav></div></header>
<main id="main">
{body}
<footer>The back office of <a href="{up}">kate-curtis-evans.founder.sovereignweb.site</a>. Built from the repository by tools/backoffice.py. <a href="{REPO}">Repository</a> · <a href="{REPO}/actions">Publishing runs</a> · No cookies, no tracking.</footer>
</main>
</body>
</html>
'''


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', lambda m: '<code>' + m.group(1) + '</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*([^*\s][^*]*)\*(?!\w)', r'<em>\1</em>', t)

    def link(m):
        text, href = m.group(1), m.group(2)
        if href.endswith('.md') and not href.startswith('http'):
            href = href[:-3] + '.html'
        return f'<a href="{href}">{text}</a>'
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, t)
    t = re.sub(r'(?<!["=>])(https?://[^\s<)]+[^\s<).,])', r'<a href="\1">\1</a>', t)
    return t


def md(src):
    """A small Markdown subset: headings, paragraphs, lists, tables, code blocks, quotes."""
    out, lines, i = [], src.split('\n'), 0
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1; continue
        if l.startswith('```') or l.startswith('    ') and not l.strip().startswith(('-', '|')):
            if l.startswith('```'):
                i += 1; buf = []
                while i < len(lines) and not lines[i].startswith('```'):
                    buf.append(lines[i]); i += 1
                i += 1
            else:
                buf = []
                while i < len(lines) and (lines[i].startswith('    ') or not lines[i].strip()):
                    buf.append(lines[i][4:]); i += 1
            out.append('<pre><code>' + html.escape('\n'.join(buf).strip('\n')) + '</code></pre>'); continue
        m = re.match(r'(#{1,3}) (.*)', l)
        if m:
            n = len(m.group(1)); out.append(f'<h{n}>{inline(m.group(2))}</h{n}>'); i += 1; continue
        if l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip('|').split('|')]); i += 1
            body = [r for r in rows if not all(re.fullmatch(r':?-+:?', c) for c in r)]
            h = ''.join(f'<th>{inline(c)}</th>' for c in body[0])
            b = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body[1:])
            out.append(f'<div class="wrapx"><table><tr>{h}</tr>{b}</table></div>'); continue
        if l.startswith('> '):
            buf = []
            while i < len(lines) and lines[i].startswith('>'):
                buf.append(lines[i][1:].strip()); i += 1
            out.append('<blockquote><p>' + inline(' '.join(buf)) + '</p></blockquote>'); continue
        m = re.match(r'(\s*)([-*]|\d+\.) (.*)', l)
        if m:
            tag = 'ol' if m.group(2)[0].isdigit() else 'ul'; items = []
            while i < len(lines) and re.match(r'\s*([-*]|\d+\.) ', lines[i]):
                item = re.sub(r'^\s*([-*]|\d+\.) ', '', lines[i]); i += 1
                while i < len(lines) and lines[i].strip() and lines[i].startswith('   ') and not re.match(r'\s*([-*]|\d+\.) ', lines[i]) and not lines[i].startswith('        '):
                    item += ' ' + lines[i].strip(); i += 1
                sub = []
                while i < len(lines) and (lines[i].startswith('        ') or not lines[i].strip()) and i + 1 < len(lines) and (lines[i].startswith('        ') or lines[i + 1].startswith('        ')):
                    sub.append(lines[i][8:]); i += 1
                items.append('<li>' + inline(item) + ('<pre><code>' + html.escape('\n'.join(sub).strip('\n')) + '</code></pre>' if ''.join(sub).strip() else '') + '</li>')
                while i < len(lines) and not lines[i].strip() and i + 1 < len(lines) and re.match(r'\s*([-*]|\d+\.) ', lines[i + 1]):
                    i += 1
            out.append(f'<{tag}>' + ''.join(items) + f'</{tag}>'); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r'(#{1,3} |\||> |\s*([-*]|\d+\.) |```)', lines[i]):
            buf.append(lines[i].strip()); i += 1
        out.append('<p>' + inline(' '.join(buf)) + '</p>')
    return '\n'.join(out)


def read_issue(path):
    s = open(path, encoding='utf-8').read()
    meta, body = {}, s
    m = re.match(r'---\n(.*?)\n---\n?(.*)', s, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1); meta[k.strip()] = v.strip().strip('"')
        body = m.group(2)
    t = re.search(r'^# (.+)$', body, re.M)
    title = t.group(1).strip() if t else os.path.basename(path)
    text = re.sub(r'^# .+$', '', body, count=1, flags=re.M).strip()
    first = text.split('\n\n')[0] if text else ''
    return {'file': os.path.relpath(path, ROOT), 'title': title, 'summary': first, **meta}


def issues():
    cols = {}
    for c, _ in COLUMNS:
        items = [read_issue(p) for p in sorted(glob.glob(os.path.join(ROOT, 'issues', c, '*.md')))]
        items.sort(key=lambda x: (PRIORITY.get(x.get('priority', 'normal'), 2), x['file']))
        cols[c] = items
    return cols


def board(cols):
    out = []
    for c, name in COLUMNS:
        cards = []
        for it in cols[c]:
            pr = it.get('priority', 'normal')
            meta = f'<span class="pill pr-{html.escape(pr)}">{html.escape(pr)}</span>'
            if it.get('estimated_effort'):
                meta += f'<span class="pill">{html.escape(it["estimated_effort"])}</span>'
            wait = f'<p class="wait">Waiting on: {inline(it["blocked_on"])}</p>' if it.get('blocked_on') else ''
            cards.append(f'<article class="card"><h3>{inline(it["title"])}</h3><div class="meta">{meta}</div>'
                         f'<p>{inline(it["summary"])}</p>{wait}<p class="file"><a href="{REPO}/blob/dev/{it["file"]}">{html.escape(it["file"])}</a></p></article>')
        out.append(f'<section class="col {c}" aria-labelledby="col-{c}"><h2 id="col-{c}">{name} <span>{len(cols[c])}</span></h2>{"".join(cards) or "<p>Nothing here.</p>"}</section>')
    return '<div class="board">' + ''.join(out) + '</div>'


def made():
    log = subprocess.run(['git', 'log', '--format=%h|%ad|%an|%s', '--date=format:%d %b %H:%M'],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip().splitlines()
    rows = ''.join(f'<tr><td><a href="{REPO}/commit/{h}"><code>{h}</code></a></td><td>{html.escape(t)}</td><td>{html.escape(a)}</td><td>{html.escape(s)}</td></tr>'
                   for h, t, a, s in (l.split('|', 3) for l in log))
    R = 'https://design.agents.sovereignweb.site/reviews-kate-curtis-evans-2026-11-20-'
    rounds = [('1', 'round-1', 'Live audit, five designs proposed', '1, then 2'), ('2', 'round-2', 'Synthetic users on the home page: 4.0', '2'),
              ('3', 'round-3', 'Hand checks: keyboard, zoom, reflow', '2'), ('4', 'round-4', 'Choose-a-design bar, The Newsroom', '2'),
              ('5', 'round-5-sign-off', 'Signed off with notes; synthetic users 3.8', '4'), ('6', 'round-6', '"Wow, not bland": redesign brief', '3'),
              ('7', 'round-7', 'Synthetic users 4.0: would show a friend', '3'), ('8', 'round-8-sign-off', 'Signed off with notes', '4')]
    rr = ''.join(f'<tr><td><a href="{R}{s}.html">Round {n}</a></td><td>{d}</td><td>{r}</td></tr>' for n, s, d, r in rounds)
    agents = [('Kate Curtis-Evans', 'Owns the site; her own Claude (site@SovereignWebsite.kate) now makes changes with her'),
              ('kate-curtis-evans.b', 'Built the site from the material, pushed every change, wrote the handover and this back office'),
              ('sites.b', 'Took the request from Dinis Cruz and gathered the material'),
              ('factory.b', 'Made the repository, the address and the publishing pipeline'),
              ('conductor.b', "Registered each agent's signing key"),
              ('design.b', 'Ran eight design rounds: audits, five designs, synthetic users'),
              ('hub.b', 'Added the site to the showroom'), ('accountant.b', 'Set the image budget (no images were generated)')]
    ar = ''.join(f'<tr><td>{html.escape(a)}</td><td>{html.escape(d)}</td></tr>' for a, d in agents)
    return (f'<h1>How this site was made</h1><p class="lede">Built on 20 November 2026 by a team of AI agents working for Dinis Cruz, from Kate\'s own LinkedIn profile and posts, then handed to Kate.</p>'
            f'<h2>Who worked on it</h2><div class="wrapx"><table><tr><th>Who</th><th>What</th></tr>{ar}</table></div>'
            f'<h2>The design rounds</h2><p>Each round audited the live site and, in some rounds, ran synthetic users: five imagined visitors who each rate it out of 5. Full records: <a href="https://design.agents.sovereignweb.site/back-office.html">the design team\'s back office</a>.</p>'
            f'<div class="wrapx"><table><tr><th>Round</th><th>What happened</th><th>Rating</th></tr>{rr}</table></div>'
            f'<h2>Every commit</h2><p>Newest first, times UTC.</p><div class="wrapx"><table><tr><th>Commit</th><th>When</th><th>Who</th><th>Change</th></tr>{rows}</table></div>')


def main():
    cols = issues()
    n = {c: len(v) for c, v in cols.items()}
    # board
    open(os.path.join(ADMIN, 'board.html'), 'w').write(page('Board', 'What is open, blocked and done on Kate Curtis-Evans\'s site.',
        '<h1>Board</h1><p class="lede">Every task is a file in the repository\'s <a href="' + REPO + '/tree/dev/issues">issues/</a> folder, in the Issues-FS format: the folder is the column. To move a card, move its file (<code>git mv issues/open/NNN-name.md issues/done/</code>), then run <code>python3 tools/backoffice.py</code> and publish.</p>' + board(cols), 'board.html'))
    # guide pages
    gdir = os.path.join(ADMIN, 'guide')
    for f in sorted(glob.glob(os.path.join(gdir, '*.md'))):
        src = open(f, encoding='utf-8').read()
        t = re.search(r'^# (.+)$', src, re.M); title = t.group(1) if t else 'Guide'
        name = os.path.basename(f)[:-3] + '.html'
        open(os.path.join(gdir, name), 'w').write(page(title, 'Guide for Kate\'s Claude: ' + title, md(src) +
            f'<p class="file">Markdown for AI agents: <a href="{os.path.basename(f)}">{os.path.basename(f)}</a></p>', 'guide/index.html' if name == 'index.html' else '', depth=2))
    # policy
    psrc = open(os.path.join(ADMIN, 'policy.md'), encoding='utf-8').read()
    open(os.path.join(ADMIN, 'policy.html'), 'w').write(page('Policy', 'The behaviour policy for agents working on Kate Curtis-Evans\'s site.',
        md(psrc) + f'<p class="file">Machine-readable: <a href="{REPO}/blob/dev/policy/abp.json">policy/abp.json</a> · enforced rules: <a href="{REPO}/blob/dev/.claude/settings.json">.claude/settings.json</a> · Markdown: <a href="policy.md">policy.md</a></p>', 'policy.html'))
    # made
    open(os.path.join(ADMIN, 'made.html'), 'w').write(page('How it was made', 'How Kate Curtis-Evans\'s site was made: the agents, the design rounds and every commit.', made(), 'made.html'))
    # hub
    top = ''.join(f'<li><a href="{REPO}/blob/dev/{it["file"]}">{inline(it["title"])}</a></li>' for it in cols['open'][:4])
    hub = f'''<h1>Back office</h1>
<p class="lede">Everything about running this site, for Kate and for her Claude. The live site is at <a href="../">kate-curtis-evans.founder.sovereignweb.site</a>.</p>
<div class="tiles">
<a class="tile" href="board.html"><b>Board</b><span>What is open, blocked and done.</span><span class="counts"><span class="pill">Open {n["open"]}</span><span class="pill">Blocked {n["blocked"]}</span><span class="pill">Done {n["done"]}</span></span></a>
<a class="tile" href="guide/index.html"><b>Guide for your Claude</b><span>Ten pages: how the site works, changing facts in every design, photos, checks, publishing, limits, interviewing Kate.</span></a>
<a class="tile" href="guide/09-interview.html"><b>Interview Kate</b><span>A prompt for Kate's Claude to draw out her story and facts, one question at a time.</span></a>
<a class="tile" href="policy.html"><b>Policy</b><span>What Kate's Claude may and may not change or reach, and what is enforced.</span></a>
<a class="tile" href="made.html"><b>How it was made</b><span>The agents, eight design rounds and every commit.</span></a>
<a class="tile" href="../start/"><b>Start here</b><span>How Kate took over the site: GitHub, Claude, the first change.</span></a>
</div>
<h2>Next up</h2>
<ol>{top}</ol>
<h2>For Kate's Claude</h2>
<p>Begin every session with <a href="guide/01-start.html">Start of every session</a>. To be interviewed, Kate pastes:</p>
<blockquote><p>Read {U}/admin/guide/09-interview.md and interview me for my website. Start with the open questions in docs/questions-for-kate.md. Ask one question at a time, use my own words, and after each answer show me the change you would make and wait for my yes.</p></blockquote>'''
    open(os.path.join(ADMIN, 'index.html'), 'w').write(page('Back office', 'The back office of Kate Curtis-Evans\'s site: board, guide, policy and how it was made.', hub, 'index.html'))
    print('back office built:', n)


if __name__ == '__main__':
    main()
