#!/usr/bin/env python3
"""Builds Transient/sheet_conflicts_review_2026-10-09.{html,map.json,decisions.json} (+ _img/).
Source list: Transient/sheet_conflicts_for_owner_2026-10-09.md (66 A/B lines). Deletes and changes nothing else."""
import glob, json, re, shutil, subprocess, sys
from pathlib import Path
R = Path("/home/mandrake/rm/bench"); T = R / "Transient"
sys.path.insert(0, str(R / "src/RimMandrake/Utils/art"))
import artledger as L
import enact
STEM = "sheet_conflicts_review_2026-10-09"
IMG = T / (STEM + "_img"); IMG.mkdir(exist_ok=True)
CANON = R / "design/RimStarWars/canon_references"
STORE = Path("/mnt/d/Luke/dev/_artstore")
DRY = Path(sys.argv[1]) if len(sys.argv) > 1 else None

REC = {"del": "A", "amb": "B", "stale": "A", "noslot": "A", "kept": "A", "note": "A", "failed": "A", "purgedpick": "B", "tier": "A"}
def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())

# ── data
sheets = {}      # biome -> [ (decisions path, doc, snap) ]
for f in sorted(glob.glob(str(T / "biome_ffar/*_sheet_*.decisions.json"))):
    doc = json.load(open(f)); sp = Path(doc["snapshot"]);
    sp = sp if sp.is_absolute() else R / sp
    sheets.setdefault(doc["biome"], []).append((Path(f), doc, json.load(open(sp)), sp))
dry = json.load(open(DRY)) if DRY else {}
jobs = {j["id"]: j for j in enact.load_jobs()}
idx = L.Index()

def full_sha(p12):
    g = glob.glob(str(STORE / p12[:2] / (p12 + "*")))
    return Path(g[0]).stem if g else None

def put(sha):
    if not sha: return None
    p = IMG / f"{sha[:16]}.png"
    if not p.exists():
        try: p.write_bytes(L.store_get(sha))
        except Exception: return None
    return p.name

# canon index
canon_by_def, canon_by_norm = {}, {}
for d in CANON.iterdir():
    dm = d / "description.md"
    if not dm.exists(): continue
    head = dm.read_text()[:1500]
    for m in re.finditer(r"`([A-Za-z0-9_]+)`", head.split("\n\n")[2] if head.count("\n\n") > 2 else head):
        canon_by_def.setdefault(m.group(1), d.name)
    canon_by_norm[norm(d.name)] = d.name
def canon_for(row, extra=None):
    for k in ([extra] if extra else []) + [row]:
        if k in canon_by_def: return canon_by_def[k]
    if extra and extra in (d.name for d in CANON.iterdir()): return extra
    base = re.sub(r"^(?:[A-Z]{2,3}_)(?:Plant_)?", "", row); base = re.sub(r"^Plant_", "", base)
    for cand in (norm(base), norm(re.sub(r"_?(Wild|Juv)$", "", base))):
        if cand in canon_by_norm: return canon_by_norm[cand]
    return None
def must(name):
    out, f = [], False
    for ln in (CANON / name / "description.md").read_text().splitlines():
        if ln.startswith("## Must show"): f = True; continue
        if ln.startswith("## "): f = False
        if f and ln.strip().startswith("- "): out.append(ln.strip()[2:].replace("[ ] ", "").replace("[x] ", ""))
    return out
def cimgs(name):
    res = []
    for p in sorted((CANON / name).iterdir()):
        if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and "donor_current" not in p.name:
            d = IMG / f"canon_{name}_{p.name}"
            if not d.exists(): shutil.copy(p, d)
            res.append(d.name)
    return res[:4]

def kind_of(text):
    if "marked an old picture for deletion" in text: return "del"
    if "doesn't say which of its several" in text: return "amb"
    if "made before the sheet was rebuilt" in text: return "stale"
    if "donor-mod art" in text: return "noslot"
    if "protected the current picture but also picked" in text: return "kept"
    if text.startswith("Your note"): return "note"
    if "redraw job failed" in text: return "failed"
    if "picked a picture you had also deleted" in text: return "purgedpick"
    if "two rows disagree" in text: return "tier"
    raise ValueError(text)

# ── old snapshots (for stale re-picks)
def old_snapshot(sp, doc):
    rel = str(sp.relative_to(R))
    revs = subprocess.run(["git", "-C", str(R), "log", "--format=%H", "--", rel], capture_output=True, text=True).stdout.split()
    last = None
    for rv in revs:
        try: s = json.loads(subprocess.run(["git", "-C", str(R), "show", f"{rv}:{rel}"], capture_output=True, text=True).stdout)
        except ValueError: continue
        if s.get("snapshotId") == doc.get("snapshotId"): return s, rv[:9]
        last = (s, rv[:9])
    return last if last else (None, None)

# ── parse the md
entries, biome = [], None
for ln in (T / "sheet_conflicts_for_owner_2026-10-09.md").read_text().splitlines():
    if ln.startswith("## "): biome = ln[3:].strip()
    m = re.match(r"- \*\*(.+?)\*\*: (.*)", ln)
    if m:
        body = m.group(2); mm = re.search(r"\s+A\) (.*?)\s+B\) (.*)$", body)
        entries.append({"biome": biome, "name": m.group(1), "text": body[:mm.start()].strip(), "optA": mm.group(1).strip(),
                        "optB": mm.group(2).strip(), "kind": kind_of(body)})
assert len(entries) == 66, len(entries)

def dry_for(dpath):
    v = dry.get(str(dpath)) or {}
    return (v.get("conflicts") or []), (v.get("todo") or [])

KINDPAT = {"del": r"^(\S+): ✕ (\w+) not purged — (.*)", "amb": r"^(\S+): pick (\w) is a by-name", "stale": r"^(\S+): letter\(s\) ([A-Z, ]+) were clicked",
           "noslot": r"^(\S+): pick (\w) (\S+) has no slot", "kept": r"^(\S+): (\S+) holds (\w+), owner-kept on (.*?);? pick (\w) not installed",
           "note": r"^(\S+): note not enacted", "failed": r"^(\S+): job (\S+) failed after", "purgedpick": r"^(\S+): pick (\w) (\w+) (\w+) was purged"}

def find_rows(e):
    """-> list of (dpath, doc, snap, sp, row, [regex matches]) for this entry"""
    out = []
    for dpath, doc, snap, sp in sheets.get(e["biome"], []):
        c, t = dry_for(dpath)
        pool = c + t
        for line in pool:
            m = re.match(KINDPAT.get(e["kind"], r"$^"), line) if e["kind"] in KINDPAT else None
            if not m: continue
            if e["kind"] == "note" and "OWNER" in line: continue
            if norm(m.group(1)).endswith(norm(e["name"])):
                out.append((dpath, doc, snap, sp, m.group(1), m, line))
    return out

def purged_lookup(snapcols, sha):
    for l, c in snapcols.items():
        for f, s in c.items():
            if s == sha: return l, f
    return None, None

def strip(snap, row, letter):
    cols = (snap["rows"][row]["columns"] or {}).get(letter) or {}
    return [(f, put(s), s) for f, s in sorted(cols.items()) if s]

def ingame(snap, row):
    r = snap["rows"].get(row) or {}
    for l, lab in (r.get("labels") or {}).items():
        if str(lab).startswith("IN GAME"): return l, strip(snap, row, l), lab
    return None, [], ""

def shortpath(p):
    p = re.sub(r"^src/", "", p); parts = p.split("/")
    return parts[0] + " / " + parts[-1] if len(parts) > 2 else p

items, maps = [], {}
unmatched = []
for e in entries:
    rows = find_rows(e)
    # fall back (no dry line): derive from the decisions directly
    if not rows:
        for dpath, doc, snap, sp in sheets.get(e["biome"], []):
            for row in doc["decisions"]:
                if norm(row).endswith(norm(e["name"])) and row in snap["rows"]:
                    rows.append((dpath, doc, snap, sp, row, None, None))
    if not rows:
        unmatched.append(e["name"]); continue
    dpath, doc, snap, sp, row = rows[0][:5]
    # entries of the same kind for >1 sheet (e.g. Vozzik): pick the sheet by biome (already filtered)
    v = doc["decisions"].get(row, {}); srow = snap["rows"].get(row, {})
    labels = srow.get("labels") or {}
    lines = [r[6] for r in rows if r[6] and r[4] == row]
    ms = [r[5] for r in rows if r[5] and r[4] == row]
    canon_name = canon_for(row)
    if not canon_name:
        for j in jobs.values():
            if j.get("target_def") == row and j.get("target_canon"): canon_name = canon_for(row, j["target_canon"])
    it = {"id": f"{e['biome']}/{e['name']}/{e['kind']}", "group": e["biome"], "label": e["name"], "kind": e["kind"], "row": row,
          "sentence": e["text"], "optA": e["optA"], "optB": e["optB"], "prefill": REC[e["kind"]], "thumb": None, "effect": e["text"],
          "A": [], "B": [], "notes": [], "other": [], "canon": [], "must": [], "canonName": canon_name}
    mp = {"decisionsFile": str(dpath.relative_to(R)), "sheetId": doc.get("sheetId"), "row": row, "kind": e["kind"],
          "conflictLines": lines, "A": {"means": e["optA"]}, "B": {"means": e["optB"]}}
    k = e["kind"]
    if k == "del":
        shas12 = sorted({m.group(2) for m in ms}) if ms else [s[:12] for s in v.get("purge", [])]
        shas = []
        for p12 in shas12:
            fs = next((s for s in v.get("purge", []) if s.startswith(p12)), None) or full_sha(p12)
            if fs: shas.append(fs)
        mp["A"]["shas"] = mp["B"]["shas"] = shas; mp["A"]["action"] = "drop the delete: keep these pictures"
        mp["B"]["action"] = "install a replacement for these, then delete them"
        for s in shas:
            l, f = purged_lookup(srow.get("columns") or {}, s)
            live = idx.live_anywhere(s); kept = idx.protected(s)
            why = ("live in game: " + shortpath(live[0])) if live else ("owner-kept on " + (Path(kept[0].get("via") or "").name or "a ruling") if kept else "")
            it["A"].append({"img": put(s), "cap": f"{f or ''} {('· col ' + l) if l else ''} · {why}"})
        # B: his replacement pick, else the row's candidates
        pick = (v.get("picks") or {}).get("_byname") or v.get("decision")
        pl = [pick] if pick in (srow.get("columns") or {}) and not set((srow["columns"][pick]).values()) & set(shas) else []
        if pl:
            for f, im, s in strip(snap, row, pl[0]): it["B"].append({"img": im, "cap": f"your pick, column {pl[0]} · {f}"})
            it["notes"].append(f"B would install your pick (column {pl[0]}: {labels.get(pl[0], '')}) and then delete the old picture(s).")
        else:
            it["notes"].append("You picked no replacement on this row, so B means: a replacement must be chosen first. Candidates are shown at right; say which in the notes box.")
            for l, c in (srow.get("columns") or {}).items():
                s0 = next((s for f, s in sorted(c.items()) if s and s not in shas), None)
                if s0 and not str(labels.get(l, "")).startswith("IN GAME"): it["B"].append({"img": put(s0), "cap": f"candidate column {l}: {labels.get(l, '')}"})
    elif k == "amb":
        letter = ms[0].group(2) if ms else (v.get("picks") or {}).get("_byname")
        mp["A"]["letter"] = mp["B"]["letter"] = letter; mp["A"]["action"] = f"column {letter} replaces the row's main picture"
        mp["B"]["action"] = "owner will say which graphic; read the notes box"
        for f, im, s in strip(snap, row, letter): it["A"].append({"img": im, "cap": f"your pick, column {letter} ({labels.get(letter, '')}) · {f}"})
        gof = srow.get("graphic_of") or {}
        gs = sorted({g for g in gof.values() if g != "_byname"})
        it["notes"].append(f"This row has {len(gs)} separate in-game pictures (graphics); your pick does not say which it replaces: " + ", ".join(g.rsplit("/", 1)[-1] for g in gs) + ". Choose B and name the graphic in the notes box.")
        for g in gs:
            for l, gg in gof.items():
                if gg == g and str(labels.get(l, "")).startswith("IN GAME"):
                    s0 = next((s for f, s in sorted((srow["columns"][l]).items()) if s), None)
                    if s0: it["B"].append({"img": put(s0), "cap": g.rsplit("/", 1)[-1] + " (live now)"})
        mp["graphics"] = gs
    elif k == "stale":
        letters = [x.strip() for x in ms[0].group(2).split(",")] if ms else []
        mp["A"]["letters"] = letters; mp["A"]["action"] = "owner re-picks on the current sheet (say which column in the notes)"
        mp["B"]["action"] = "leave the current art"
        old, rev = old_snapshot(sp, doc)
        orow = (old or {}).get("rows", {}).get(row) or {}
        for lt in letters:
            for f, s in sorted(((orow.get("columns") or {}).get(lt) or {}).items()):
                if s: it["A"].append({"img": put(s), "cap": f"your OLD pick: letter {lt} on the earlier sheet ({orow.get('labels', {}).get(lt, '')}) · {f}"})
        mp["oldSnapshotRev"] = rev
        it["notes"].append("Pick A, then type the letter of the CURRENT column you want in the notes box (current columns are listed below the pictures). Pick B to leave things as they are.")
        for l, c in (srow.get("columns") or {}).items():
            s0 = next((s for f, s in sorted(c.items()) if s), None)
            if s0: it["other"].append({"img": put(s0), "cap": f"column {l}: {labels.get(l, '')}"})
        gl, gstrip, gl_lab = ingame(snap, row)
        for f, im, s in gstrip: it["B"].append({"img": im, "cap": f"current art ({gl_lab}) · {f}"})
        if not it["A"]: it["notes"].append("The old picture could not be recovered from the earlier snapshot.")
    elif k == "noslot":
        letters = sorted({m.group(2) for m in ms}) or []
        targets = sorted({m.group(3) for m in ms})
        mp["A"]["letters"] = letters; mp["A"]["action"] = "create our own override texture slot so the pick ships"; mp["B"]["action"] = "drop the pick"
        for lt in letters:
            for f, im, s in strip(snap, row, lt): it["A"].append({"img": im, "cap": f"your pick, column {lt} ({labels.get(lt, '')}) · {f}"})
        it["notes"].append("This pick would land on donor-mod texture(s): " + ", ".join(sorted({t.rsplit('/', 1)[0].rsplit('/', 1)[-1] for t in targets})) + ", which we cannot overwrite. A makes our own override.")
        gl, gstrip, gl_lab = ingame(snap, row)
        for f, im, s in gstrip: it["B"].append({"img": im, "cap": f"stays as is ({gl_lab}) · {f}"})
        if not gstrip: it["notes"].append("There is no current in-game picture to fall back to on this row.")
    elif k == "kept":
        letter = ms[0].group(5) if ms else None
        mp["A"]["letter"] = mp["B"]["letter"] = letter; mp["A"]["action"] = "keep the protected current picture"; mp["B"]["action"] = f"install the new pick (column {letter}); release the keep"
        kept_by = sorted({m.group(4) for m in ms})
        for m in ms:
            fs = full_sha(m.group(3))
            if fs: it["A"].append({"img": put(fs), "cap": f"current, protected: {m.group(2).rsplit('/', 1)[-1]}"})
        for f, im, s in strip(snap, row, letter): it["B"].append({"img": im, "cap": f"your new pick, column {letter} ({labels.get(letter, '')}) · {f}"})
        it["notes"].append("The current picture is protected by: " + "; ".join(kept_by) + ". You also picked a different one on this sheet.")
        mp["keptBy"] = kept_by
    elif k == "note":
        note = v.get("note") or ""
        mp["A"]["action"] = "queue a redraw following the note"; mp["B"]["action"] = "mark the note handled / ignore it"
        it["notes"].append("Your note: “" + note + "”")
        dec = v.get("decision")
        shown = False
        if dec in (srow.get("columns") or {}):
            for f, im, s in strip(snap, row, dec): it["A"].append({"img": im, "cap": f"the picture you were looking at (column {dec}: {labels.get(dec, '')}) · {f}"}); shown = True
        if not shown:
            gl, gstrip, gl_lab = ingame(snap, row)
            for f, im, s in gstrip: it["A"].append({"img": im, "cap": f"current art ({gl_lab}) · {f}"})
        it["B"] = []
    elif k == "failed":
        jid = ms[0].group(2) if ms else None
        jb = jobs.get(jid) or {}
        mp["A"]["jobs"] = sorted({m.group(2) for m in ms}); mp["A"]["action"] = "rewrite the prompt and re-file the failed job(s)"; mp["B"]["action"] = "drop the redraw"
        note = v.get("note") or jb.get("owner_note") or ""
        it["notes"].append("Failed job(s): " + ", ".join(sorted({m.group(2) for m in ms})) + (". Your note it carried: “" + note + "”" if note else "."))
        ref = jb.get("reference")
        if ref and Path(ref).exists():
            sh = Path(ref).stem; it["A"].append({"img": put(sh), "cap": "the reference picture the redraw was told to follow"})
        gl, gstrip, gl_lab = ingame(snap, row)
        for f, im, s in gstrip: it["B"].append({"img": im, "cap": f"art if you drop the redraw ({gl_lab}) · {f}"})
        if jb.get("target_canon"): canon_name = canon_name or canon_for(row, jb["target_canon"])
    elif k == "purgedpick":
        pick = (v.get("picks") or {}).get("_byname"); sh = (v.get("purge") or [None])[0]
        mp["A"]["letter"] = pick; mp["A"]["action"] = "owner picks a different column"; mp["B"]["action"] = "queue a redraw"
        for f, im, s in strip(snap, row, pick): it["A"].append({"img": im, "cap": f"the picture you picked (column {pick}) · {f}"})
        l, f = purged_lookup(srow.get("columns") or {}, sh)
        it["notes"].append(f"You picked column {pick} AND marked a picture deleted (✕){(' in column ' + l + ' · ' + f) if l else ''}; the deleted picture is {'the same one' if l == pick else 'in another column'}. Pick A and name another column in the notes, or B for a fresh redraw.")
        for ll, c in (srow.get("columns") or {}).items():
            if ll == pick: continue
            s0 = next((s for f2, s in sorted(c.items()) if s), None)
            if s0: it["other"].append({"img": put(s0), "cap": f"other column {ll}: {labels.get(ll, '')}"})
    elif k == "tier":
        mp["A"]["action"] = "Star Wars level only: RSW_GreatDevourer is the one def; remove/hide the plain RM_ row"
        mp["B"]["action"] = "plain mod level: RM_GreatDevourer is the one def; RSW_ row dropped"
        mp["rows"] = ["RM_GreatDevourer", "RSW_GreatDevourer"]
        for rr in ("RM_GreatDevourer", "RSW_GreatDevourer"):
            vv = doc["decisions"].get(rr, {})
            it["notes"].append(f"{rr} says: “{(vv.get('note') or '')[:400]}”")
        gl, gstrip, gl_lab = ingame(snap, "RM_GreatDevourer" if "RM_GreatDevourer" in snap["rows"] else row)
        for f, im, s in gstrip: it["A"].append({"img": im, "cap": f"current art ({gl_lab}) · {f}"})
        if not gstrip:
            for l, c in (srow.get("columns") or {}).items():
                s0 = next((s for f2, s in sorted(c.items()) if s), None)
                if s0 and put(s0): it["other"].append({"img": put(s0), "cap": f"column {l}: {labels.get(l, '')}"})
    if canon_name:
        it["canon"] = cimgs(canon_name); it["must"] = must(canon_name)
    it["other"] = [o for o in it["other"] if o["img"]]
    for k2 in ("A", "B"):
        for o in it[k2]:
            if not o["img"]: o["cap"] += " \u2014 this picture was purged and is no longer in the art store"
    items.append(it); maps[it["id"]] = mp

print("items", len(items), "unmatched", unmatched)
assert not unmatched, unmatched

# ── page
tpl = Path(glob.glob(str(Path.home() / ".claude/skills/review-sheets/assets/sheet_template.html"))[0]).read_text()
cfg = {"sheetId": STEM, "title": "66 blocking art decisions", "subtitle": "pick A, B or other for each row; type in the notes box when it asks",
 "briefHtml": "<p>Each row is a spot where I could not carry out one of your earlier sheet rulings without your choice. <b>A</b> and <b>B</b> are the two ways forward, spelled out on the row, with the pictures involved shown large. <b>other</b> means neither; say what you want in the notes box. Nothing is changed by this page. Your choices are only recorded, and I enact them afterwards.</p><p><b>The pre-selected letter is only my suggestion (the safe, least-destructive way forward).</b> A row you do not touch counts as undecided and nothing is done for it.</p><p>Rows are grouped by biome. Where a creature has a canon entry its reference images and <i>Must show</i> list are under the pictures; a row without one says so.</p>",
 "criterion": "Not ranked: grouped by biome. The pre-selected letter is my least-destructive suggestion, not a decision.",
 "invented": [], "posture": {"mode": "whitelist", "explain": "A blank row means no decision yet. Nothing is done for a blank row."},
 "options": [{"key": "A", "label": "A", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
             {"key": "B", "label": "B", "hotkey": "2", "color": "#6aa6e8", "counts": "in"},
             {"key": "other", "label": "other", "hotkey": "3", "color": "#e8b64c", "counts": "out"}],
 "groupLabel": "biome", "media": False, "decisionsFile": STEM + ".decisions.json", "decisionsPath": "", "sheetPath": ""}
a = tpl.index('<script id="CONFIG"'); b = tpl.index("</script>", a)
tpl = tpl[:a] + '<script id="CONFIG" type="application/json">\n' + json.dumps(cfg, ensure_ascii=False) + "\n" + tpl[b:]
a = tpl.index('<script id="ITEMS"'); b = tpl.index("</script>", a)
tpl = tpl[:a] + '<script id="ITEMS" type="application/json">\n' + json.dumps(items, ensure_ascii=False).replace("</", "<\\/") + "\n" + tpl[b:]
render = r"""<script id="RENDER">
window.IMGDIR = '""" + STEM + r"""_img/';
window.itemBody = it => {
  const im = (o, w) => o.img ? `<figure style="margin:0;width:${w}px"><div class="thumb" style="width:${w}px;height:${w}px" data-zoom="${esc(window.IMGDIR + o.img)}" data-cap="${esc(o.cap)}"><img src="${esc(window.IMGDIR + o.img)}" alt="" style="width:100%;height:100%;object-fit:contain;image-rendering:pixelated;background:#222"></div><figcaption class="effect" style="font-size:11px">${esc(o.cap)}</figcaption></figure>` : `<div class="effect">(picture missing: ${esc(o.cap)})</div>`;
  const side = (L, txt, arr) => `<div style="flex:1 1 440px;min-width:300px;border:1px solid #2a2f37;border-radius:6px;padding:8px"><div><b style="color:var(--accent);font-size:15px">${L}</b> ${esc(txt)}</div><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px">${arr.length ? arr.map(o => im(o, arr.length > 3 ? 150 : 200)).join('') : '<div class="effect">no picture — this option shows nothing new</div>'}</div></div>`;
  const canon = it.canon.length ? `<div class="effect" style="margin-top:8px"><b>Canon references</b> (${esc(it.canonName)})</div><div style="display:flex;gap:6px;flex-wrap:wrap">${it.canon.map(c => im({img: c, cap: 'canon'}, 130)).join('')}</div><div class="effect"><b>Must show:</b><ul style="margin:2px 0 0 18px;padding:0">${it.must.map(m => `<li>${esc(m)}</li>`).join('')}</ul></div>` : `<div class="effect" style="margin-top:8px"><i>No canon entry for this subject.</i></div>`;
  return `<div style="font-size:14px;margin:2px 0 6px"><b>${esc(it.sentence)}</b></div>
   <div class="effect"><code>${esc(it.row)}</code></div>
   ${it.notes.map(n => `<div class="effect" style="margin:3px 0">${esc(n)}</div>`).join('')}
   <div style="display:flex;gap:12px;flex-wrap:wrap;margin:8px 0">${side('A', it.optA, it.A)}${side('B', it.optB, it.B)}</div>
   ${it.other.length ? `<div class="effect"><b>Current columns</b> (type the letter in the notes if you want one):</div><div style="display:flex;gap:6px;flex-wrap:wrap">${it.other.map(o => im(o, 110)).join('')}</div>` : ''}
   ${canon}`;
};
</script>
"""
a = tpl.index("<script>\n\"use strict\";")
tpl = tpl[:a] + render + tpl[a:]
import nonart_sheet as NA
tpl = NA.declare(tpl)
(T / (STEM + ".html")).write_text(tpl)
(T / (STEM + ".map.json")).write_text(json.dumps({"sheetId": STEM, "decisionsFile": "Transient/" + STEM + ".decisions.json",
    "note": "Enact ONLY rows whose decisions-file record has decidedAt (a human click); the page pre-selects a suggestion (prefill) that is NOT a decision. Each item id is a key in the decisions file. A/B/other -> maps[id][A|B]; 'other' means read the note.", "maps": maps}, indent=1, ensure_ascii=False) + "\n")
dp = T / (STEM + ".decisions.json")
if not dp.exists() or not json.loads(dp.read_text()).get("savedBy"):
    dp.write_text(json.dumps({"posture": "whitelist", "criterion": cfg["criterion"], "sheetId": STEM,
        "reviewStatus": {"state": "prefill", "by": None, "at": None, "evidence": "generated; no human has picked"}, "decisions": {}}, indent=2) + "\n")
missing = [(i["id"], c["cap"]) for i in items for k in ("A", "B", "other") for c in i[k] if not c["img"]]
print("pictures missing:", missing)
print("rows w/o any picture:", [i["id"] for i in items if not (i["A"] or i["B"] or i["other"])])
print("canon rows:", sum(bool(i["canon"]) for i in items))
