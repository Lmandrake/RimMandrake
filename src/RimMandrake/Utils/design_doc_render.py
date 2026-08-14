#!/usr/bin/env python3
"""Render one of this project's design/review markdown docs as an HTML page
the owner can read in a browser.

Derived artifact -- the markdown is always the source of truth. Regenerate the
two that exist today with no arguments:
    python3 src/RimMandrake/Utils/design_doc_render.py
Or render any other doc:
    python3 src/RimMandrake/Utils/design_doc_render.py SRC.md OUT.html \\
        --title "Name" --eyebrow "VISION - context" --standfirst "one sentence" \\
        --stat "11|religions specified|ok"

Deliberately dependency-free (no `markdown` module on this box). Handles only
the constructs these docs actually use: headings, key/value and data tables,
fenced code, blockquotes, ordered/unordered lists, and the author's own glyph
markers (RED/AMBER/WARN/STAR), which become callouts.
"""
import argparse
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

CRIT, WARN, STAR = "\U0001f534", "⚠️", "⭐"
AMBER = ("\U0001f7e0", "\U0001f7e1")  # orange / yellow circles, used for severity


# ---------------------------------------------------------------- inline ----
def inline(text):
    """Escape, then apply code spans, bold and italic. Code first so that
    `**` inside a defName is never eaten by the bold pass."""
    slots = []

    def stash(m):
        slots.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(slots) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text, flags=re.S)
    text = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"<em>\1</em>", text, flags=re.S)
    return re.sub(r"\x00(\d+)\x00", lambda m: slots[int(m.group(1))], text)


def callout_class(text):
    stripped = text.lstrip()
    if stripped.startswith(CRIT):
        return "crit"
    if stripped.startswith(WARN) or stripped.startswith(AMBER):
        return "warn"
    if stripped.startswith(STAR):
        return "star"
    return ""


# ----------------------------------------------------------------- blocks ---
def render_table(rows):
    """A `| | |` header means a key/value spec strip; anything else is data."""
    head, body = rows[0], rows[1:]
    keyvalue = all(not c.strip() for c in head)
    out = ['<div class="scroll"><table class="%s">' % ("kv" if keyvalue else "data")]
    if not keyvalue:
        out.append("<thead><tr>")
        out += [f"<th>{inline(c)}</th>" for c in head]
        out.append("</tr></thead>")
    out.append("<tbody>")
    for row in body:
        out.append("<tr>")
        for i, cell in enumerate(row):
            tag = "th" if keyvalue and i == 0 else "td"
            out.append(f"<{tag}>{inline(cell)}</{tag}>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def flush_para(buf, out):
    if not buf:
        return
    text = " ".join(buf).strip()
    buf.clear()
    if not text:
        return
    cls = callout_class(text)
    if cls:
        out.append(f'<p class="callout {cls}">{inline(text)}</p>')
    else:
        out.append(f"<p>{inline(text)}</p>")


def convert(lines):
    """Return (body_html, toc) where toc is a list of (anchor, kicker, label)."""
    out, toc, para = [], [], []
    i, open_section = 0, False
    n = len(lines)

    def close_section():
        nonlocal open_section
        flush_para(para, out)
        if open_section:
            out.append("</section>")
        open_section = False

    while i < n:
        line = lines[i].rstrip("\n")
        stripped = line.strip()

        # fenced code
        if stripped.startswith("```"):
            flush_para(para, out)
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip("\n"))
                i += 1
            i += 1
            out.append(
                '<div class="scroll"><pre><code>%s</code></pre></div>'
                % html.escape("\n".join(code))
            )
            continue

        # table
        if stripped.startswith("|"):
            flush_para(para, out)
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                filled = [c for c in cells if c]
                separator = filled and all(
                    re.fullmatch(r":?-{2,}:?", c) for c in filled
                )
                if not separator:
                    rows.append(cells)
                i += 1
            if rows:
                out.append(render_table(rows))
            continue

        # blockquote
        if stripped.startswith(">"):
            flush_para(para, out)
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(quote))}</blockquote>")
            continue

        # lists (ordered or bulleted), with hanging continuation lines
        m_ol = re.match(r"^(\d+)\.\s+(.*)", stripped)
        m_ul = re.match(r"^[-*]\s+(.*)", stripped)
        if m_ol or m_ul:
            flush_para(para, out)
            tag = "ol" if m_ol else "ul"
            items = []
            while i < n:
                cur = lines[i].rstrip("\n")
                s = cur.strip()
                mo = re.match(r"^(\d+)\.\s+(.*)", s)
                mu = re.match(r"^[-*]\s+(.*)", s)
                if mo or mu:
                    items.append((mo.group(2) if mo else mu.group(1)))
                elif s and cur.startswith((" ", "\t")) and items:
                    items[-1] += " " + s
                elif s and items and not s.startswith(("|", ">", "#", "```")):
                    items[-1] += " " + s
                else:
                    break
                i += 1
            body = "".join(
                f'<li class="{callout_class(it)}">{inline(it)}</li>' for it in items
            )
            out.append(f"<{tag}>{body}</{tag}>")
            continue

        # headings
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            if level == 1:
                i += 1
                continue  # the page header carries the title
            if level == 2:
                close_section()
                anchor = "s%d" % len(toc)
                m = re.match(r"^(\d+)\s*·\s*(.+?)\s+—\s+(.*)$", text)
                if m:
                    num, faction, religion = m.groups()
                    religion = religion.strip().strip("*")  # it is styled, not bolded
                    toc.append((anchor, num, faction))
                    out.append(f'<section class="entry" id="{anchor}">')
                    out.append(
                        '<header class="entry-head">'
                        f'<span class="num">{num}</span>'
                        f'<h2>{inline(faction)}</h2>'
                        f'<p class="religion">{inline(religion)}</p>'
                        "</header>"
                    )
                else:
                    plain = re.sub(r"^[\U0001f300-\U0001faff⭐⚠️\s]+", "", text)
                    # nav wants the name of the section, not its whole sentence
                    toc.append((anchor, "", re.split(r"\s+—\s+", plain)[0]))
                    out.append(f'<section class="note" id="{anchor}">')
                    cls = callout_class(text)
                    out.append(f'<h2 class="{cls}">{inline(plain)}</h2>')
                open_section = True
            else:
                flush_para(para, out)
                # a leading short id (D1, A2, C3) is a real handle in these docs
                m_id = re.match(r"^([A-Z]\d{1,2})\s+(.*)$", text)
                tag, rest = (m_id.group(1), m_id.group(2)) if m_id else ("", text)
                cls = callout_class(rest)
                chip = f'<span class="tag {cls}">{tag}</span>' if tag else ""
                out.append(f'<h3 class="{cls}">{chip}{inline(rest)}</h3>')
            i += 1
            continue

        if stripped.startswith("---"):
            flush_para(para, out)
            i += 1
            continue

        if not stripped:
            flush_para(para, out)
        else:
            para.append(stripped)
        i += 1

    close_section()
    return "".join(out), toc


# ------------------------------------------------------------------ page ----
CSS = """
:root{
  color-scheme:light dark;
  --ground:#EFEFE9; --surface:#FAFAF7; --sunk:#E5E6DF;
  --ink:#1B211F; --ink-soft:#5C6663; --ink-faint:#8A928F;
  --rule:#D6D8D0; --rule-soft:#E4E5DE;
  --accent:#1D6E62; --accent-ink:#145148; --accent-wash:#E0EDE9;
  --warn:#8A6111; --warn-wash:#F3EBDA;
  --crit:#A02E22; --crit-wash:#F6E4E1;
  --star:#1D6E62;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;
  --sans:ui-sans-serif,"Segoe UI",system-ui,-apple-system,"Helvetica Neue",sans-serif;
  --mono:ui-monospace,"Cascadia Mono",Consolas,"DejaVu Sans Mono",monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#111514; --surface:#171C1A; --sunk:#1E2523;
    --ink:#E6E9E4; --ink-soft:#9EA8A4; --ink-faint:#6F7A76;
    --rule:#2A3230; --rule-soft:#222927;
    --accent:#5FBCAB; --accent-ink:#8FD3C5; --accent-wash:#14302B;
    --warn:#D6A548; --warn-wash:#2B2415;
    --crit:#E4796A; --crit-wash:#311B18;
    --star:#5FBCAB;
  }
}
:root[data-theme="dark"]{
  --ground:#111514; --surface:#171C1A; --sunk:#1E2523;
  --ink:#E6E9E4; --ink-soft:#9EA8A4; --ink-faint:#6F7A76;
  --rule:#2A3230; --rule-soft:#222927;
  --accent:#5FBCAB; --accent-ink:#8FD3C5; --accent-wash:#14302B;
  --warn:#D6A548; --warn-wash:#2B2415;
  --crit:#E4796A; --crit-wash:#311B18;
  --star:#5FBCAB;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:var(--serif); font-size:17px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px 96px}

/* ---- masthead ---- */
.mast{padding:64px 0 28px;border-bottom:1px solid var(--rule)}
.eyebrow{
  font-family:var(--sans);font-size:11px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--ink-faint);margin:0 0 18px;display:flex;gap:10px;flex-wrap:wrap;align-items:center;
}
.eyebrow span{color:var(--accent)}
h1{
  font-family:var(--serif);font-weight:600;font-size:clamp(34px,5.4vw,58px);
  line-height:1.06;letter-spacing:-.015em;margin:0;text-wrap:balance;
}
h1 em{font-style:italic;color:var(--accent)}
.standfirst{
  margin:18px 0 0;max-width:62ch;font-size:19px;color:var(--ink-soft);
}
.stats{
  display:flex;flex-wrap:wrap;gap:0;margin:32px 0 0;
  border:1px solid var(--rule);border-radius:2px;background:var(--surface);
}
.stat{flex:1 1 160px;padding:14px 18px;border-right:1px solid var(--rule-soft)}
.stat:last-child{border-right:0}
.stat b{
  display:block;font-family:var(--sans);font-size:22px;font-weight:600;
  font-variant-numeric:tabular-nums;letter-spacing:-.01em;
}
.stat span{
  display:block;font-family:var(--sans);font-size:10.5px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--ink-faint);margin-top:3px;
}
.stat.ok b{color:var(--accent)} .stat.warn b{color:var(--warn)} .stat.crit b{color:var(--crit)}

/* ---- layout ---- */
.cols{display:grid;grid-template-columns:200px minmax(0,1fr);gap:56px;margin-top:44px}
@media (max-width:900px){.cols{grid-template-columns:1fr;gap:28px}}
nav{position:sticky;top:24px;align-self:start;font-family:var(--sans);font-size:13px}
@media (max-width:900px){nav{position:static}}
nav p{
  font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint);
  margin:0 0 12px;
}
nav ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:1px}
nav a{
  display:flex;gap:9px;padding:5px 8px;color:var(--ink-soft);text-decoration:none;
  border-radius:2px;border-left:2px solid transparent;line-height:1.35;
}
nav a:hover{background:var(--sunk);color:var(--ink);border-left-color:var(--accent)}
nav a:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
nav .k{
  color:var(--ink-faint);font-variant-numeric:tabular-nums;min-width:14px;
  font-size:11px;padding-top:2px;
}
main{min-width:0}

/* ---- sections ---- */
section{margin:0 0 4px;padding:34px 0;border-bottom:1px solid var(--rule-soft)}
section:last-child{border-bottom:0}
.entry-head{margin:0 0 20px}
.num{
  font-family:var(--sans);font-size:11px;font-weight:600;letter-spacing:.1em;
  color:var(--accent);display:block;margin-bottom:6px;
}
h2{
  font-size:clamp(25px,3.2vw,33px);font-weight:600;line-height:1.14;margin:0;
  letter-spacing:-.012em;text-wrap:balance;
}
h2.crit{color:var(--crit)} h2.warn{color:var(--warn)}
.religion{
  margin:4px 0 0;font-style:italic;font-size:20px;color:var(--accent-ink);
}
h3{
  font-size:20px;font-weight:600;line-height:1.25;margin:34px 0 12px;
  letter-spacing:-.005em;text-wrap:balance;display:flex;gap:10px;align-items:baseline;
  flex-wrap:wrap;max-width:66ch;
}
h3.crit{color:var(--crit)} h3.warn{color:var(--warn)}
.tag{
  font-family:var(--sans);font-size:11px;font-weight:700;letter-spacing:.08em;
  padding:2px 7px;border-radius:2px;background:var(--sunk);color:var(--ink-soft);
  position:relative;top:-2px;
}
.tag.crit{background:var(--crit-wash);color:var(--crit)}
.tag.warn{background:var(--warn-wash);color:var(--warn)}
.tag.star{background:var(--accent-wash);color:var(--accent-ink)}
p{margin:0 0 15px;max-width:68ch}
strong{font-weight:600}
code{
  font-family:var(--mono);font-size:.855em;background:var(--sunk);
  padding:1px 5px;border-radius:2px;color:var(--accent-ink);
  overflow-wrap:anywhere;
}
blockquote{
  margin:20px 0;padding:2px 0 2px 22px;border-left:2px solid var(--accent);
  color:var(--ink-soft);font-style:italic;max-width:64ch;
}
blockquote code,blockquote strong{font-style:normal}
ol,ul{max-width:66ch;margin:0 0 16px;padding-left:22px}
li{margin:0 0 7px}
ol{counter-reset:none}

/* ---- callouts: the author's own glyph markers ---- */
.callout{
  padding:12px 16px;border-radius:2px;border-left:2px solid var(--rule);
  background:var(--surface);max-width:68ch;
}
.callout.crit{border-left-color:var(--crit);background:var(--crit-wash)}
.callout.warn{border-left-color:var(--warn);background:var(--warn-wash)}
.callout.star{border-left-color:var(--star);background:var(--accent-wash)}
li.crit,li.warn,li.star{list-style:none;margin-left:-22px;padding-left:12px;border-left:2px solid var(--rule)}
li.crit{border-left-color:var(--crit)} li.warn{border-left-color:var(--warn)} li.star{border-left-color:var(--star)}

/* ---- tables ---- */
.scroll{overflow-x:auto;margin:0 0 20px}
table{border-collapse:collapse;width:100%;font-size:15px}
table.kv{max-width:none;font-family:var(--sans);font-size:14px}
table.kv th{
  width:130px;text-align:left;font-weight:600;color:var(--ink-faint);
  font-size:11px;letter-spacing:.1em;text-transform:uppercase;vertical-align:top;
  padding:9px 16px 9px 0;white-space:nowrap;
}
table.kv td{padding:9px 0;border-bottom:1px solid var(--rule-soft);vertical-align:top}
table.kv tr:last-child td,table.kv tr:last-child th{border-bottom:0}
table.data{font-family:var(--sans);font-size:13.5px;line-height:1.5}
table.data thead th{
  text-align:left;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--ink-faint);font-weight:600;padding:0 14px 8px 0;
  border-bottom:1px solid var(--rule);white-space:nowrap;
}
table.data td{
  padding:9px 14px 9px 0;border-bottom:1px solid var(--rule-soft);vertical-align:top;
}
table.data tbody tr:hover{background:var(--sunk)}
table.data td:first-child{color:var(--ink-soft);white-space:nowrap}
pre{
  margin:0;padding:16px 18px;background:var(--surface);border:1px solid var(--rule);
  border-radius:2px;overflow-x:auto;
}
pre code{background:none;padding:0;color:var(--ink);font-size:13px;line-height:1.6}
footer{
  margin-top:56px;padding-top:22px;border-top:1px solid var(--rule);
  font-family:var(--sans);font-size:12.5px;color:var(--ink-faint);max-width:70ch;
}
footer code{font-size:12px}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""

TEMPLATE = """<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{css}</style>
<div class="wrap">
<header class="mast">
  <p class="eyebrow">{eyebrow}</p>
  <h1>{heading}</h1>
  <p class="standfirst">{standfirst}</p>
  {stats}
</header>
<div class="cols">
  <nav aria-label="Contents"><p>Contents</p><ol>{toc}</ol></nav>
  <main>{body}</main>
</div>
<footer>Rendered from <code>{src}</code> — the markdown is the source of truth;
this page is regenerated by <code>src/RimMandrake/Utils/design_doc_render.py</code>.
Every defName in it was read from the live def dump, not from memory.</footer>
</div>
"""

# The two docs that exist today. Each entry is the argument set `main()` would
# otherwise take on the command line.
PRESETS = [
    dict(
        src="design/Jawa/worldbuilding/faction_religions_spec.md",
        out="design/Jawa/worldbuilding/review/faction_religions_spec.html",
        title="Eleven Religions",
        heading="Eleven religions, <em>buildable</em>",
        eyebrow="VISION · design/Jawa/worldbuilding <span>·</span> the encoding layer"
        " <span>·</span> 2026-08-14",
        standfirst="Every NPC faction on the desert world gets an ideoligion whether we"
        " author one or not. These are the eleven we author — decisions, not"
        " recommendations, and the file CREATE builds the <code>FactionDef</code>"
        " blocks from.",
        stats=[
            ("11", "religions specified", "ok"),
            ("11/11", "validator: VALID", "ok"),
            ("3", "strings the engine renders", "warn"),
            ("1", "unmeasured premise", "crit"),
            ("12", "Jawa slot — owner’s", ""),
        ],
    ),
]


def render(src, out, title, heading, eyebrow, standfirst, stats):
    src_path, out_path = ROOT / src, ROOT / out
    body, toc = convert(src_path.read_text(encoding="utf-8").splitlines())
    nav = "".join(
        f'<li><a href="#{a}"><span class="k">{k or "·"}</span>'
        f'<span>{html.escape(label)}</span></a></li>'
        for a, k, label in toc
    )
    strip = ""
    if stats:
        cells = "".join(
            f'<div class="stat {cls}"><b>{html.escape(value)}</b>'
            f"<span>{html.escape(label)}</span></div>"
            for value, label, cls in stats
        )
        strip = f'<div class="stats">{cells}</div>'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        TEMPLATE.format(
            css=CSS,
            title=html.escape(title),
            heading=heading,
            eyebrow=eyebrow,
            standfirst=standfirst,
            stats=strip,
            toc=nav,
            body=body,
            src=html.escape(src),
        ),
        encoding="utf-8",
    )
    print(f"{out_path}  {out_path.stat().st_size:,} bytes  {len(toc)} sections")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src", nargs="?", help="repo-relative markdown source")
    ap.add_argument("out", nargs="?", help="repo-relative html destination")
    ap.add_argument("--title", default="")
    ap.add_argument("--heading", default="")
    ap.add_argument("--eyebrow", default="")
    ap.add_argument("--standfirst", default="")
    ap.add_argument(
        "--stat",
        action="append",
        default=[],
        metavar="VALUE|LABEL|CLASS",
        help="masthead stat, class one of ok/warn/crit or empty. Repeatable.",
    )
    a = ap.parse_args()
    if not a.src:
        for preset in PRESETS:
            render(**preset)
        return
    render(
        src=a.src,
        out=a.out,
        title=a.title or Path(a.src).stem,
        heading=a.heading or a.title or Path(a.src).stem,
        eyebrow=a.eyebrow,
        standfirst=a.standfirst,
        stats=[tuple((s.split("|") + ["", ""])[:3]) for s in a.stat],
    )


if __name__ == "__main__":
    main()
