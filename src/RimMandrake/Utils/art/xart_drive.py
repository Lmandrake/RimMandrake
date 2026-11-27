#!/usr/bin/env python3
"""Judge, install and wire the commissioned extra looks and the owed creature facings.

Two items share this driver: EXTRA_LOOKS_WIRE_AS_THEY_TRICKLE_IN (each row of
design/RimMandrake/extra_art_commission/commission.csv: female -> femaleGraphicData, variant -> alternateGraphics,
young -> the baby and juvenile lifeStages' bodyGraphicData) and CREATURE_FACINGS_REDRAW_ONE_PICTURE_ZOO (a creature on
one picture gets east, north and south, wired Graphic_Multi).

    xart_drive.py looks [--all]                 each look: COMPLETE (every facing rendered) | PART | HELD | INSTALLED | WIRED
    xart_drive.py spec <subject>...|--complete  art_eval specs for complete looks / drawn facing sets -> <data>/specs/
    xart_drive.py judge <run-id> <subject>...   art_eval runner.py run --record over those specs (resumable by run id)
    xart_drive.py install <run-id> [subject...] art.py install of every facing of each ACCEPTed subject of that run
    xart_drive.py wire [subject...] [--dry-run] write the def edits of every installed, unwired subject
    xart_drive.py faces-file [--dry-run]        file the owed facings' north/south (east) jobs with fill_queue
    xart_drive.py refile [--from-run RUN...] [--failed] [--dry-run]
                                                the next version of each look the judge sent back (REGEN in RUN: every
                                                facing, the judge's fix appended) and of each failed facing rescue
                                                could not save (that facing alone); canvas = the reference's own
    xart_drive.py rescue [--dry-run]            a failed look facing whose render is an exact multiple of the reference
                                                canvas or overflows its footprint by a few percent: conform it to the
                                                reference (canvas, then the reference's subject box) and re-run
                                                validate_sprite; a pass is a candidate like a done render

Subjects: `<race>__<look>` for a look (RM_Aurrok__young, RSW_Kybuck__female_pack) and `<kind>__faces` for a facing set.
A slot is never wired before every facing of it is installed under src/ (the item's rule: no magenta). Held mods
(src/RimMandrake/rimflow/mod_owner_hold.json) are left out. Judging is the art_eval pipeline (skill
rimworld-art-evaluation); its delegated verdict file is cited in each install (`--why "delegated: art <file>"`).
State lives in the artpipe queue, the art ledger, the runner's decision logs and the defs; this driver keeps none.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from rmpaths import rm_path  # noqa: E402

COMMISSION = REPO / "design/RimMandrake/extra_art_commission/commission.csv"
HOLDS = REPO / "src/RimMandrake/rimflow/mod_owner_hold.json"
OWED = REPO / "src/RimMandrake/Utils/facing_art_owed.json"
ART_EVAL = REPO / "src/RimMandrake/Utils/art_eval"
DELEGATED = REPO / "infrastructure/state/delegated"
FACES_ITEM = "CREATURE_FACINGS_REDRAW_ONE_PICTURE_ZOO"
LOOKS_ITEM = "EXTRA_LOOKS_WIRE_AS_THEY_TRICKLE_IN"
VARIANT_CHANCE = "0.35"   # about a third of a herd in the variant's colours: breaks up a herd, the base look stays the norm


def data() -> Path:
    d = rm_path("xart")
    d.mkdir(parents=True, exist_ok=True)
    return d


def artpipe() -> Path:
    sys.path.insert(0, str(HERE.parent / "artpipe"))
    import state_dir
    return Path(state_dir.require())


def held() -> set:
    return {h["mod"] for h in json.loads(HOLDS.read_text())["holds"]}


# ---------------------------------------------------------------------------------------------------------- looks
def commission_rows() -> list[dict]:
    return list(csv.DictReader(COMMISSION.open()))


def subject_of(row: dict) -> str:
    return f"{row['race']}__{row['slot']}"


def look_jobs(row: dict, q: Path | None = None) -> list[tuple[str, str]]:
    """[(facing or '', job id)] of one commission row: per facing the newest version the queue holds (a refiled facing
    is `..._v2_<facing>`; `refile`), else the commissioned v1."""
    fac = [f for f in row["facings"].split(";") if f] or [""]
    base = row["job_id"][:-len("_v1")] if row["job_id"].endswith("_v1") else row["job_id"]
    out = []
    for f in fac:
        ids = [f"{base}_v{n}" + (f"_{f}" if f else "") for n in range(1, 10)]
        have = [i for i in ids if q is not None and job_state(q, i) != "none"]
        out.append((f, have[-1] if have else ids[0]))
    return out


def rescued_dir() -> Path:
    d = data() / "rescued"
    d.mkdir(exist_ok=True)
    return d


def job_state(q: Path, jid: str) -> str:
    for d in ("done", "failed", "active", "pending"):
        if (q / d / f"{jid}.json").is_file():
            return d
    return "none"


def render_file(q: Path, jid: str, shas: dict | None = None) -> Path | None:
    """The finished render of a job: its _artsrc PNG, else the art store's copy (the daemon prunes _artsrc after 14 days;
    the art ledger's artpipe backfill keeps every render by its job id)."""
    r = rescued_dir() / f"{jid}.png"       # a failed render fitted to its reference: never the raw that failed
    if r.is_file():
        return r
    p = q / "_artsrc" / jid / f"{jid}.png"
    if p.is_file() and job_state(q, jid) == "done":
        return p
    shas = job_shas() if shas is None else shas
    if jid in shas:
        import artledger as L
        sp = L.store_path(shas[jid])
        return sp if sp.is_file() else None
    return None


_SHAS: dict | None = None


def job_shas() -> dict:
    global _SHAS
    if _SHAS is None:
        import artledger as L
        _SHAS = {}
        for ev in L.read_events():
            j = ev.get("job") or (ev.get("extra") or {}).get("job")
            if j and ev.get("sha") and j not in _SHAS:
                _SHAS[j] = ev["sha"]
    return _SHAS


def tex_file(mod: str, tex: str, facing: str) -> Path:
    return REPO / "src" / mod / "Textures" / (f"{tex}_{facing}.png" if facing else f"{tex}.png")


def wired(tex: str) -> bool:
    return subprocess.run(["grep", "-rqF", f"<texPath>{tex}</texPath>", str(REPO / "src"), "--include=*.xml"],
                          timeout=120).returncode == 0   # hang guard: a grep of src/ takes about a second


def look_status(row: dict, q: Path, hold: set) -> str:
    mod = row["install_mod"]
    if mod.split("/")[1] in hold:
        return "HELD"
    jobs = look_jobs(row, q)
    if all(tex_file(mod, row["tex_path"], f).is_file() for f, _ in jobs):
        return "WIRED" if wired(row["tex_path"]) else "INSTALLED"
    st = [job_state(q, j) if job_state(q, j) != "failed" or not (rescued_dir() / f"{j}.png").is_file() else "done"
          for _, j in jobs]
    if all(s == "done" for s in st):
        return "COMPLETE"
    return "PART:" + ",".join(sorted(set(st)))


def cmd_looks(a) -> int:
    q, hold = artpipe(), held()
    import collections
    c = collections.Counter()
    for r in commission_rows():
        s = look_status(r, q, hold)
        c[(r["look"], s.split(":")[0])] += 1
        if a.all or s.startswith(("COMPLETE", "INSTALLED")):
            print(f"{subject_of(r):40s} {r['look']:8s} {s}")
    for k, v in sorted(c.items()):
        print("#", v, *k)
    return 0


# ---------------------------------------------------------------------------------------------------------- specs
def base_spec(race: str) -> dict:
    bd = data() / "base"
    bd.mkdir(exist_ok=True)
    p = bd / f"{race}.spec.json"
    if not p.is_file():
        r = subprocess.run([sys.executable, "fauna_spec.py", "build", race, "--out", str(bd)], cwd=ART_EVAL,
                           capture_output=True, text=True, timeout=600)   # hang guard: one build takes ~20 s
        if not p.is_file():
            hits = list(bd.glob(f"**/{race}.spec.json"))
            if not hits:
                raise SystemExit(f"{race}: fauna_spec made no spec: {(r.stdout + r.stderr)[-400:]}")
            p = hits[0]
    return json.loads(p.read_text())


def kind_index() -> dict:
    """defName -> (file, element) of every PawnKindDef under src/."""
    import xml.etree.ElementTree as ET
    out = {}
    for p in glob.glob(str(REPO / "src/**/Defs/**/*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root:
            if d.tag == "PawnKindDef" and d.findtext("defName"):
                out[d.findtext("defName")] = (Path(p), d)
    return out


def stage_draw(kind_el, stage: int) -> float | None:
    ls = kind_el.find("lifeStages")
    if ls is None or len(ls) <= stage:
        return None
    g = ls[stage].find("bodyGraphicData")
    ds = g.findtext("drawSize") if g is not None else None
    if not ds:
        return None
    return float(ds.strip("() ").split(",")[0])


NOTES = {
    "variant": ("This is the COLOUR VARIANT of the {label}: a second look drawn by the game for some of the herd, to "
                "break up a herd of identical animals. It must read as the same species as the adult in the siblings "
                "panel: same anatomy, pose, size and silhouette on the canvas, painted in a distinct colouring. Judge it "
                "as that variant, not against the adult's colours."),
    "female": ("This is the FEMALE look of the {label} (canon says the sexes look different). It must read as the same "
               "species as the male in the siblings panel, with the female's own features."),
    "female_pack": ("This is the FEMALE look of the {label} carrying its pack gear. It must read as the same species as the "
                    "male in the siblings panel, with the female's own features and the pack."),
    "young": ("This is the YOUNG look of the {label}: the baby and juvenile stages draw it, smaller in game than the adult "
              "in the siblings panel. A young animal's proportions are expected: larger head for its body, shorter legs, "
              "softer features, horns or crests small or budding. It must read as the same species as the adult."),
}


def adult_files(spec: dict) -> list[str]:
    return [spec["images"][f] for f in ("south", "east", "north", "single") if spec.get("images", {}).get(f)]


def look_spec(row: dict, q: Path, kinds: dict, out: Path) -> Path:
    sys.path.insert(0, str(ART_EVAL))
    sys.path.insert(0, str(HERE))
    import scale_panel as SP
    sp = base_spec(row["race"])
    subj = subject_of(row)
    imgs = {}
    for f, j in look_jobs(row, q):
        p = render_file(q, j)
        if p is None:
            raise SystemExit(f"{subj}: render of {j} not found (artpipe _artsrc, rescued or art store)")
        imgs[f or "single"] = str(p)
    sib = adult_files(sp)
    k = kinds.get(row["kind"])
    ds = None
    if k is not None:
        ds = stage_draw(k[1], 1) if row["slot"] == "young" else None   # the juvenile's size: the larger young stage
    size = dict(sp.get("size") or {})
    if ds:
        size["drawSize"] = [ds, ds]
    pan = out / "panels"
    pan.mkdir(parents=True, exist_ok=True)
    key = imgs.get("east") or imgs.get("single") or next(iter(imgs.values()))
    cp = pan / f"{subj}_scale.png"
    SP.render_panel(Path(key).read_bytes(), {"kind": "animal", "drawSize": tuple(size.get("drawSize") or (1.0, 1.0))},
                    cp, pan / f"{subj}_scale_full.png")
    imgs["scale"] = str(cp)
    if sib:
        imgs["siblings"] = sib
    sp.update(subject=subj, candidate="r1", images=imgs, size=size, owner_kept=False, kept_install=[],
              artpipe_job=look_jobs(row, q)[0][1].rsplit("_", 1)[0] if row["facings"] else row["job_id"],
              target_texpath=row["tex_path"], previous_prompt=None,
              provenance=(f"extra-art commission ({LOOKS_ITEM}; commission.csv row {row['race']} {row['slot']}): "
                          f"{row['evidence']}; artpipe jobs {', '.join(j for _, j in look_jobs(row, q))}"))
    sp.setdefault("owner_notes", [])
    sp["owner_notes"] = list(sp["owner_notes"]) + [NOTES[row["slot"]].format(label=sp.get("label") or row["label"])]
    sp.pop("images_flight_note", None)
    for k in ("flight_labels", "flight_frames_unmeasured"):     # stills only: a look has no flight frames of its own
        sp.pop(k, None)
    if sp.get("module") == "flyer":
        sp["module"] = "walker"
        sp["owner_notes"].append("The kind flies, but this look is judged from its standing stills only: flight frames "
                                 "are drawn per kind, not per look.")
    p = out / f"{subj}.spec.json"
    p.write_text(json.dumps(sp, indent=1))
    return p


def cmd_spec(a) -> int:
    q, hold = artpipe(), held()
    out = data() / "specs"
    out.mkdir(exist_ok=True)
    kinds = kind_index()
    rows = {subject_of(r): r for r in commission_rows()}
    want = [s for s, r in rows.items() if look_status(r, q, hold) == "COMPLETE"] if a.complete else a.subjects
    bad = 0
    for s in want:
        if s.endswith("__faces"):
            try:
                print(s, faces_spec(s[:-len("__faces")], q, out))
            except SystemExit as e:
                print(s, "NOT READY:", e); bad += 1
            continue
        try:
            print(s, look_spec(rows[s], q, kinds, out))
        except SystemExit as e:
            print(s, "NO SPEC:", e); bad += 1
    return 1 if bad else 0


# ---------------------------------------------------------------------------------------------------------- judge
def cmd_judge(a) -> int:
    specs = [str(data() / "specs" / f"{s}.spec.json") for s in a.subjects]
    miss = [s for s in specs if not Path(s).is_file()]
    if miss:
        print("no spec:", miss)
        return 2
    # hang guard: one subject takes 1-3 min (Opus, then GPT); a batch of a few subjects is far under the 3 h guard
    r = subprocess.run([sys.executable, "runner.py", "run", "--spec", *specs, "--run-id", a.run_id, "--record"],
                       cwd=ART_EVAL, timeout=3 * 3600)
    return r.returncode


def decisions(run_id: str) -> dict:
    """subject -> last decision record of a run."""
    p = REPO / "infrastructure/state/art_eval/runs" / run_id / "decisions.jsonl"
    out = {}
    if p.is_file():
        for line in p.read_text().splitlines():
            try:
                d = json.loads(line)
            except ValueError:
                continue
            out[d.get("subject")] = d
    return out


def verdict_file(subj: str) -> str | None:
    hits = sorted(glob.glob(str(DELEGATED / "*" / f"{subj}.json")) + glob.glob(str(DELEGATED / "*" / f"{subj}__*.json")))
    return str(Path(hits[-1]).relative_to(REPO)) if hits else None


# ---------------------------------------------------------------------------------------------------------- install
def install_png(mod: str, rel: str, png: Path, why: str, dry: bool, reason: str | None = None) -> tuple[int, str]:
    stage = REPO / "Transient" / "xart_stage" / Path(rel).name
    stage.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(png, stage)
    cmd = [sys.executable, "src/RimMandrake/Utils/art/art.py", "install", mod, rel, "--file", str(stage), "--why", why]
    if reason:          # a mechanical copy names its writer (art_guard: script:<repo path>), never a free --why alone
        cmd += ["--reason", reason]
    if dry:
        cmd.append("--dry-run")
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600)  # hang guard: an install is ~5 s
    stage.unlink(missing_ok=True)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1][:200] if (r.stdout + r.stderr).strip() else ""


def pack_sources(row: dict, rows: dict) -> dict:
    """{facing: adult Pack PNG} a young or female look must also carry as `<look texPath>Pack_<facing>`: the game draws a
    pack animal's load from the CURRENT stage's body (or female) texPath + "Pack" (PawnRenderNode_AnimalPack), so a
    young or female look on a pack animal with no Pack texture shows a missing texture under a load. Vanilla's young pack
    animals draw the adult's pack at their own drawSize; the same bytes give that parity. A commissioned female pack
    set (female_pack row) is the female's own and wins."""
    if row["slot"] not in ("young", "female") or f"{row['race']}__female_pack" in rows:
        return {}
    ref = REPO / row["reference"]
    stem = ref.name.rsplit("_", 1)[0] if ref.name.rsplit("_", 1)[-1][:-4] in ("east", "south", "north") else ref.stem
    out = {}
    for f in ("east", "south", "north"):
        p = ref.parent / f"{stem}Pack_{f}.png"
        if p.is_file():
            out[f] = p
    return out


def cmd_install(a) -> int:
    dec = decisions(a.run_id)
    specs = data() / "specs"
    rows = {subject_of(r): r for r in commission_rows()}
    bad = 0
    for subj, d in sorted(dec.items()):
        if a.subjects and subj not in a.subjects:
            continue
        if d.get("decision") != "ACCEPT":
            print(subj, "not ACCEPT:", d.get("decision"))
            continue
        vf = verdict_file(subj)
        if not vf:
            print(subj, "ACCEPT but no delegated verdict file; not installed")
            bad += 1
            continue
        sp = json.loads((specs / f"{subj}.spec.json").read_text())
        if subj.endswith("__faces"):
            mod, tex = sp["install_mod"], sp["target_texpath"]
            files = {f: sp["images"][f] for f in ("east", "south", "north") if f in sp["images"]}
            files = {f: p for f, p in files.items() if f not in sp.get("installed_facings", [])}
        else:
            r = rows[subj]
            mod, tex = r["install_mod"], r["tex_path"]
            files = {f: sp["images"][f or "single"] for f, _ in look_jobs(r)}
        for f, p in files.items():
            rel = f"{tex}_{f}.png" if f else f"{tex}.png"
            rc, line = install_png(mod, rel, Path(p), f"delegated: art {vf}", a.dry_run)
            print(subj, f or "single", "rc", rc, line)
            bad += rc != 0
        if not subj.endswith("__faces"):
            for f, p in pack_sources(rows[subj], rows).items():
                rc, line = install_png(mod, f"{tex}Pack_{f}.png", p, f"mechanical: the adult pack drawn on the {rows[subj]['slot']} "
                                       f"look of a pack animal (vanilla parity; xart_drive.pack_sources)", a.dry_run,
                                       reason="script:src/RimMandrake/Utils/art/xart_drive.py")
                print(subj, "pack", f, "rc", rc, line)
                bad += rc != 0
    return 1 if bad else 0


# ---------------------------------------------------------------------------------------------------------- wire
def _block(text: str, kind: str) -> tuple[int, int]:
    """(start, end) of the <PawnKindDef> element whose defName is `kind`, as text offsets. A race ThingDef often shares
    the defName, so only PawnKindDef elements are searched."""
    for m in re.finditer(r"<PawnKindDef\b", text):
        e = text.find("</PawnKindDef>", m.end())
        if e < 0:
            break
        if re.search(r"<defName>\s*%s\s*</defName>" % re.escape(kind), text[m.start():e]):
            return m.start(), e
    raise ValueError(f"{kind}: no PawnKindDef of that defName")


def _stages(block: str) -> list[tuple[int, int]]:
    """Offsets (inside block) of each top-level <li>...</li> of <lifeStages>."""
    m = re.search(r"<lifeStages>", block)
    end = block.find("</lifeStages>")
    if not m or end < 0:
        raise ValueError("no <lifeStages>")
    out, i, depth, start = [], m.end(), 0, None
    for t in re.finditer(r"<(/?)li\b[^>]*?(/?)>", block[m.end():end]):
        pos = m.end() + t.start()
        if t.group(2):
            continue
        if not t.group(1):
            if depth == 0:
                start = pos
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                out.append((start, m.end() + t.end()))
    return out


def _indent_of(text: str, pos: int) -> str:
    ls = text.rfind("\n", 0, pos) + 1
    return re.match(r"[ \t]*", text[ls:]).group(0)


def wire_variant(text: str, kind: str, tex: str) -> str:
    s, e = _block(text, kind)
    blk = text[s:e]
    if "<alternateGraphics>" in blk:
        if f"<texPath>{tex}</texPath>" in blk:
            return text
        i = blk.find("</alternateGraphics>")
        ind = _indent_of(blk, i)
        new = blk[:i] + f"  <li><texPath>{tex}</texPath></li>\n{ind}" + blk[i:]
    else:
        ind = _indent_of(text, s) + "  "
        tail = blk.rstrip()
        add = (f"\n{ind}<!-- {LOOKS_ITEM}: the commissioned colour variant (commission.csv) -->"
               f"\n{ind}<alternateGraphicChance>{VARIANT_CHANCE}</alternateGraphicChance>"
               f"\n{ind}<alternateGraphics>\n{ind}  <li><texPath>{tex}</texPath></li>\n{ind}</alternateGraphics>\n"
               + _indent_of(text, s))
        new = tail + add
    return text[:s] + new + text[e:]


def wire_young(text: str, kind: str, tex: str) -> str:
    s, e = _block(text, kind)
    blk = text[s:e]
    st = _stages(blk)
    if len(st) < 3:
        raise ValueError(f"{kind}: {len(st)} life stages; young wiring needs baby, juvenile, adult")
    for a, b in reversed(st[:-1]):        # baby and juvenile; the adult stays
        li = blk[a:b]
        g = re.search(r"<bodyGraphicData>.*?</bodyGraphicData>", li, re.S)
        if not g:
            raise ValueError(f"{kind}: a young stage has no bodyGraphicData")
        body = re.sub(r"<texPath>[^<]*</texPath>", f"<texPath>{tex}</texPath>", g.group(0), count=1)
        li = li[:g.start()] + body + li[g.end():]
        # a female adult picture on a young stage would hide the young look for every female
        li = re.sub(r"\s*<femaleGraphicData>.*?</femaleGraphicData>", "", li, flags=re.S)
        blk = blk[:a] + li + blk[b:]
    return text[:s] + blk + text[e:]


def wire_female(text: str, kind: str, tex: str) -> str:
    s, e = _block(text, kind)
    blk = text[s:e]
    a, b = _stages(blk)[-1]
    li = blk[a:b]
    if "<femaleGraphicData>" in li:
        li = re.sub(r"(<femaleGraphicData>.*?<texPath>)[^<]*(</texPath>)", r"\g<1>%s\g<2>" % tex, li, count=1, flags=re.S)
    else:
        g = re.search(r"<bodyGraphicData>.*?</bodyGraphicData>", li, re.S)
        if not g:
            raise ValueError(f"{kind}: the adult stage has no bodyGraphicData")
        fem = g.group(0).replace("bodyGraphicData>", "femaleGraphicData>")
        fem = re.sub(r"<texPath>[^<]*</texPath>", f"<texPath>{tex}</texPath>", fem, count=1)
        li = li[:g.end()] + "\n" + _indent_of(li, g.start()) + fem + li[g.end():]
    blk = blk[:a] + li + blk[b:]
    return text[:s] + blk + text[e:]


def wire_multi(text: str, kind: str, tex: str) -> str:
    """Every bodyGraphicData of the kind that draws `tex` as Graphic_Single becomes Graphic_Multi."""
    s, e = _block(text, kind)
    blk = text[s:e]

    def fix(m):
        g = m.group(0)
        if f"<texPath>{tex}</texPath>" not in g:
            return g
        return g.replace("Graphic_Single", "Graphic_Multi")
    blk = re.sub(r"<bodyGraphicData>.*?</bodyGraphicData>", fix, blk, flags=re.S)
    return text[:s] + blk + text[e:]


def cmd_wire(a) -> int:
    kinds = kind_index()
    rows = {subject_of(r): r for r in commission_rows()}
    hold = held()
    q = artpipe()
    todo = []
    for subj, r in rows.items():
        if a.subjects and subj not in a.subjects:
            continue
        if look_status(r, q, hold) == "INSTALLED":
            todo.append((subj, r))
    # female_pack rides on the female's texPath (the game reads <texPath>Pack): it is installed, never wired itself
    bad = 0
    for subj, r in todo:
        if r["slot"] == "female_pack":
            continue
        if r["slot"] == "female" and f"{r['race']}__female_pack" in rows:
            pk = rows[f"{r['race']}__female_pack"]
            if look_status(pk, q, hold) not in ("INSTALLED", "WIRED"):
                print(subj, "waits for its female pack set"); continue
        lack = [f for f in pack_sources(r, rows) if not tex_file(r["install_mod"], r["tex_path"] + "Pack", f).is_file()]
        if lack:
            print(subj, "NOT WIRED: a pack animal; its Pack facings are not installed", lack); bad += 1; continue
        f, _ = kinds[r["kind"]]
        text = f.read_text()
        fn = {"variant": wire_variant, "young": wire_young, "female": wire_female}[r["slot"]]
        try:
            new = fn(text, r["kind"], r["tex_path"])
        except ValueError as e:
            print(subj, "NOT WIRED:", e); bad += 1; continue
        if r["slot"] == "variant" and not r["facings"]:
            body = re.search(r"<graphicClass>(\w+)</graphicClass>", text[slice(*_block(text, r["kind"]))])
            if body and body.group(1) != "Graphic_Single":
                print(subj, "NOT WIRED: a one-picture variant on a", body.group(1), "body"); bad += 1; continue
        print(subj, "->", f.relative_to(REPO), "(dry run)" if a.dry_run else "")
        if not a.dry_run:
            f.write_text(new)
    return 1 if bad else 0


# ---------------------------------------------------------------------------------------------------------- faces
FACE_KINDS = {   # kind -> (the one picture's view, the facings to draw); a west-facing picture's mirror is the east
    "RM_Fessu": ("east", ["south", "north"]), "RM_Hesuun": ("east", ["south", "north"]),
    "RM_Krellik": ("east", ["south", "north"]), "RM_Oddu": ("east", ["south", "north"]),
    "RM_Oovanam": ("east", ["south", "north"]), "RM_Oovu": ("east", ["south", "north"]),
    "RM_Tarnn": ("east", ["south", "north"]), "RM_Zhiil": ("east", ["south", "north"]),
    "RSW_Moornak": ("west", ["south", "north"]), "RSW_Onnik": ("west", ["south", "north"]),
    "RSW_SandStalker": ("west", ["south", "north"]), "RM_Tarruq": ("south", ["east"]),
}
FACE_PROMPT = ("Draw the SAME individual animal as the attached reference image (its accepted {view} view): same anatomy, "
               "same proportions, same colours and markings, same size on the canvas, seen from the view this job asks "
               "for. A creature sprite for RimWorld: the {label}. {desc} Visible features it must show: {feat}. "
               "Realistic painterly vanilla RimWorld sprite style, soft painted edges in a deeper shade of the local "
               "colour. Exactly ONE creature, centred, the whole body visible with nothing cut off. Fully transparent "
               "background: no ground, no water, no shadow, no text, no border.")


def face_row(kind: str) -> dict:
    sys.path.insert(0, str(HERE.parent))
    import facing_art_census as F
    rows, _ = F.census()
    hit = [r for r in rows if r["kindDef"] == kind and r["class"]]
    if not hit:
        raise SystemExit(f"{kind}: the census owes it nothing")
    return hit[0]


def face_master(kind: str, out: Path) -> tuple[str, str, Path]:
    """(mod, texPath, east master PNG): the one picture, mirrored when it faces west; Tarruq's south."""
    r = face_row(kind)
    tex = r["texPath"]
    mod = r["file"].split("/Defs/")[0][len("src/"):]
    view, _ = FACE_KINDS[kind]
    if view == "south":
        return mod, tex, REPO / "src" / mod / "Textures" / f"{tex}_south.png"
    one = REPO / "src" / mod / "Textures" / f"{tex}.png"
    if view == "east":
        return mod, tex, one
    from PIL import Image
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{kind}_east_mirrored.png"
    Image.open(one).transpose(Image.FLIP_LEFT_RIGHT).save(p)
    return mod, tex, p


def face_version(kind: str, q: Path | None) -> int:
    """The newest owedface version the queue holds for the kind (1 when none)."""
    n = 1
    for v in range(2, 10):
        if q is not None and any(job_state(q, f"owedface_{kind}_v{v}_{f}") != "none" for f in FACE_KINDS[kind][1]):
            n = v
    return n


def face_jobs(kind: str, q: Path | None = None) -> list[tuple[str, str]]:
    n = face_version(kind, q)
    return [(f, f"owedface_{kind}_v{n}_{f}") for f in FACE_KINDS[kind][1]]


SAME_SCALE = (" SCALE: draw the animal at the SAME scale as the reference: the body as tall on the canvas as in the "
              "reference, feet (or lowest point) on the same row; a front or rear view is narrower than a side view, "
              "never smaller.")


def cmd_faces_file(a) -> int:
    import artledger as L
    out = data() / "faces"
    rows = []
    fixes = {}
    if a.regen_from:
        rj = REPO / "infrastructure/state/art_eval/runs" / a.regen_from / "regen_jobs.json"
        by = {g["target_def"]: g["prompt"] for g in (json.loads(rj.read_text()) if rj.is_file() else [])}
        for subj, d in decisions(a.regen_from).items():
            if d.get("decision") == "REGEN" and subj.endswith("__faces"):
                fixes[subj[:-len("__faces")]] = by.get(subj) or "; ".join(d.get("reasons") or [])[:600]
    q = artpipe()
    for kind, (view, fac) in FACE_KINDS.items():
        if a.regen_from and kind not in fixes or a.kinds and kind not in a.kinds:
            continue
        n = face_version(kind, q) + (1 if a.regen_from else 0)
        if not a.regen_from and n > 1:
            continue
        mod, tex, master = face_master(kind, out)
        sp = base_spec(kind)
        ref = str(L.store_path(L.store_put_file(master)))     # pinned: the daemon never reads a clone
        fix = (SAME_SCALE + " FIX from review: " + fixes[kind]) if kind in fixes else ""
        rows.append({
            "id": f"owedface_{kind}_v{n}", "rimflow_item_id": FACES_ITEM, "target_def": kind, "target_texpath": tex,
            "facings": fac, "priority": 40, "biome_neutral": True, "canvas_w": 256, "canvas_h": 256,
            "drawsize": (sp.get("size") or {}).get("drawSize", [1.0])[0],
            "install_to": f"src/{mod}/Textures/{tex}" + "_{facing}.png", "canon_reference": ref,
            "prompt": FACE_PROMPT.format(view="front" if view == "south" else "side", label=sp.get("label") or kind,
                                         desc=sp.get("description", ""), feat="; ".join(sp.get("departures") or [])) + fix,
        })
    p = out / "rows.json"
    p.write_text(json.dumps(rows, indent=1))
    cmd = [sys.executable, "fill_queue.py", "--input", str(p), "--no-derive-facings"] + (["--dry-run"] if a.dry_run else [])
    r = subprocess.run(cmd, cwd=HERE.parent / "artpipe", timeout=600)   # hang guard: filing 12 rows takes ~30 s
    return r.returncode


def _feet_row(p: Path) -> int | None:
    """The lowest row with an opaque pixel (alpha >= 16), as facing_scale_lint measures the feet."""
    from PIL import Image
    a = Image.open(p).convert("RGBA").getchannel("A").point(lambda v: 255 if v >= 16 else 0)
    b = a.getbbox()
    return b[3] - 1 if b else None


def _align_feet(p: Path, row: int, out: Path) -> Path:
    """A new facing moved up or down (never scaled) so its feet stand on `row`, the accepted view's feet row; the
    lint's feet band is +-3% of the canvas. Nothing is cut: a shift that would push opaque pixels off the canvas is not
    made, and the render goes to the judge as drawn."""
    from PIL import Image
    im = Image.open(p).convert("RGBA")
    b = im.getchannel("A").point(lambda v: 255 if v >= 16 else 0).getbbox()
    if not b:
        return p
    dy = row - (b[3] - 1)
    if dy == 0 or b[1] + dy < 0 or b[3] + dy > im.height:
        return p
    canvas = Image.new("RGBA", im.size, (0, 0, 0, 0))
    canvas.alpha_composite(im, (0, dy))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    return out


def faces_spec(kind: str, q: Path, out: Path) -> Path:
    sys.path.insert(0, str(HERE))
    import scale_panel as SP
    mod, tex, master = face_master(kind, data() / "faces")
    imgs = {}
    for f, j in face_jobs(kind, q):
        if job_state(q, j) != "done":
            raise SystemExit(f"{j}: {job_state(q, j)}")
        p = render_file(q, j)
        if p is None:
            raise SystemExit(f"{j}: render not found")
        imgs[f] = str(p)
    view = FACE_KINDS[kind][0]
    imgs.setdefault("east", str(master))
    anchor_files = [str(master)] if view != "south" else [
        str(REPO / "src" / mod / "Textures" / f"{tex}_{f}.png") for f in ("south", "north")]
    feet = [_feet_row(Path(p)) for p in anchor_files]
    feet = [x for x in feet if x is not None]
    if feet:
        for f, _ in face_jobs(kind, q):
            imgs[f] = str(_align_feet(Path(imgs[f]), round(sum(feet) / len(feet)), out / "aligned" / f"{kind}_{f}.png"))
    for f in ("south", "north"):
        if f not in imgs:
            imgs[f] = str(REPO / "src" / mod / "Textures" / f"{tex}_{f}.png")
    sp = base_spec(kind)
    subj = f"{kind}__faces"
    pan = out / "panels"
    pan.mkdir(parents=True, exist_ok=True)
    cp = pan / f"{subj}_scale.png"
    SP.render_panel(Path(imgs["east"]).read_bytes(), {"kind": "animal",
                    "drawSize": tuple((sp.get("size") or {}).get("drawSize") or (1.0, 1.0))}, cp, pan / f"{subj}_scale_full.png")
    imgs["scale"] = str(cp)
    drawn = [f for f, _ in face_jobs(kind, q)]
    sp.update(subject=subj, candidate="r1", images=imgs, owner_kept=False, kept_install=[], install_mod=mod,
              target_texpath=tex, artpipe_job=f"owedface_{kind}_v{face_version(kind, q)}",
              installed_facings=[f for f in ("east", "south", "north") if f not in drawn and
                                 (REPO / "src" / mod / "Textures" / f"{tex}_{f}.png").is_file()],
              provenance=(f"{FACES_ITEM}: the creature was drawn on one picture ({view} view); "
                          f"{'/'.join(drawn)} drawn from it (canon_reference), artpipe jobs owedface_{kind}_v{face_version(kind, q)}_*"))
    sp.setdefault("owner_notes", [])
    sp["owner_notes"] = list(sp["owner_notes"]) + [
        f"Only the {'/'.join(drawn)} facing(s) are new; judge them against the "
        f"{'accepted front view' if view == 'south' else 'accepted one picture, shown as the east view'}, which is not "
        "being redrawn. Each new facing must show the same individual from its own side."]
    p = out / f"{subj}.spec.json"
    p.write_text(json.dumps(sp, indent=1))
    return p


def cmd_faces_wire(a) -> int:
    """Install the east master of each ACCEPTed facing set, wire the kind Graphic_Multi, drop its owed line."""
    kinds = kind_index()
    owed = json.loads(OWED.read_text())
    bad = 0
    for kind in a.kinds:
        mod, tex, master = face_master(kind, data() / "faces")
        need = [REPO / "src" / mod / "Textures" / f"{tex}_{f}.png" for f in ("east", "south", "north")]
        if not all(p.is_file() for p in need):
            print(kind, "NOT WIRED: facings missing", [p.name for p in need if not p.is_file()]); bad += 1; continue
        f, _ = kinds[kind]
        text = f.read_text() if kind in kinds else None
        if text is None:
            print(kind, "no PawnKindDef"); bad += 1; continue
        new = wire_multi(text, kind, tex)
        if not a.dry_run:
            f.write_text(new)
            if tex in owed["texPaths"]:
                owed["texPaths"].remove(tex)
        print(kind, "->", f.relative_to(REPO), "changed" if new != text else "unchanged")
    if not a.dry_run:
        OWED.write_text(json.dumps(owed, indent=1) + "\n")
    return 1 if bad else 0


# ---------------------------------------------------------------------------------------------------------- rescue
def cmd_rescue(a) -> int:
    """A failed look facing whose render is good art on the wrong canvas or a few percent over its reference's footprint:
    fit it to the reference (same canvas; subject box scaled to fit inside the reference's box, bottom-centre anchored)
    and validate it again. Only a validator pass is kept, in <data>/xart/rescued/<job>.png."""
    from PIL import Image
    q = artpipe()
    vs = REPO / "skills/generating-rimworld-sprites/scripts/validate_sprite.py"
    outd = rescued_dir()
    hold = held()
    n_ok = n_bad = 0
    for r in commission_rows():
        if r["install_mod"].split("/")[1] in hold:
            continue
        for f, j in look_jobs(r, q):
            if job_state(q, j) != "failed" or (outd / f"{j}.png").is_file():
                continue
            job = json.loads((q / "failed" / f"{j}.json").read_text())
            raw = q / "_artsrc" / j / f"{j}.png"
            ref = job.get("reference")
            if not raw.is_file() or not ref or not Path(ref).is_file():
                print(j, "no render or no reference: refile"); n_bad += 1
                continue
            im, rf = Image.open(raw).convert("RGBA"), Image.open(ref).convert("RGBA")
            rb, ib = rf.getchannel("A").point(lambda v: 255 if v >= 32 else 0).getbbox(), \
                im.getchannel("A").point(lambda v: 255 if v >= 32 else 0).getbbox()
            if not rb or not ib:
                print(j, "empty alpha"); n_bad += 1
                continue
            sub = im.crop(ib)
            k = min((rb[2] - rb[0]) / sub.width, (rb[3] - rb[1]) / sub.height)
            sub = sub.resize((max(1, round(sub.width * k)), max(1, round(sub.height * k))), Image.LANCZOS)
            canvas = Image.new("RGBA", rf.size, (0, 0, 0, 0))
            cx = (rb[0] + rb[2]) // 2
            canvas.alpha_composite(sub, (max(0, cx - sub.width // 2), max(0, rb[3] - sub.height)))
            cand = data() / "rescue" / f"{j}.png"
            cand.parent.mkdir(exist_ok=True)
            canvas.save(cand)
            v = subprocess.run([sys.executable, str(vs), "--reference", str(ref), "--candidate", str(cand)], capture_output=True, text=True,
                               timeout=120)   # hang guard: one validation takes ~1 s
            ok = v.returncode == 0
            print(j, "rescued" if ok else "still rejected", f"scale {k:.3f}",
                  "" if ok else [l for l in v.stdout.splitlines() if l.startswith("REJECT")][:2])
            if ok and not a.dry_run:
                shutil.copyfile(cand, outd / f"{j}.png")
            n_ok += ok
            n_bad += not ok
    print(f"rescued {n_ok}, not rescued {n_bad}")
    return 0


# ---------------------------------------------------------------------------------------------------------- refile
def _job_json(q: Path, jid: str) -> dict | None:
    for d in ("done", "failed", "active", "pending"):
        p = q / d / f"{jid}.json"
        if p.is_file():
            return json.loads(p.read_text())
    return None


def refile_row(q: Path, jid: str, fix: str = "") -> dict:
    """The fill_queue row of the next version of one look facing: the same job (prompt, reference, paths), its canvas the
    reference's own (a reference rescaled since the commission otherwise fails the validator), and the judge's fix."""
    from PIL import Image
    j = _job_json(q, jid)
    if j is None:
        raise SystemExit(f"{jid}: no job file")
    m = re.match(r"^(.*)_v(\d+)(?:_(north|south|east|west))?$", jid)
    base, n, f = m.group(1), int(m.group(2)), m.group(3)
    row = {"id": f"{base}_v{n + 1}", "rimflow_item_id": LOOKS_ITEM, "prompt": j["prompt"] + (f" FIX from review: {fix}" if fix else ""),
           "facings": [f] if f else [], "target_def": j.get("target_def"), "target_texpath": j.get("target_texpath"),
           "install_to": j["install_to"], "priority": 45, "biome_neutral": True,
           "style_notes": j.get("style_notes") or "", "drawsize": j.get("drawsize") or 1.0}
    w = h = (j.get("canvas") or {}).get("width", 256)
    if j.get("reference") and Path(j["reference"]).is_file():
        row["reference"] = j["reference"]
        w, h = Image.open(j["reference"]).size
    row["canvas_w"], row["canvas_h"] = w, h
    return row


ADULT_REF = ("The attached image is the ADULT of this species, as accepted in the game. Draw the {what} of exactly this "
             "species: the same colours, markings, materials, surface and body plan, so a player sees at once that it "
             "is the same animal. ")
ONE_COAT = ("Paint ONE colouring and pattern and keep it identical in every view of this animal. ")


def regen_rows(q: Path, row: dict, fix: str) -> list[dict]:
    """The next version of a whole look the judge sent back, built against the cause the first renders showed: a young or
    female look drawn from text alone came out as another species (its east master now carries the adult's east as
    anatomy guidance; north/south derive from that east), and a variant's facings reskinned one by one drifted apart in
    colour (its east is a reskin of the adult's east; north/south derive from that one east, so one coat)."""
    import artledger as L
    jobs = look_jobs(row, q)
    if [f for f, _ in jobs] == [""]:
        return [refile_row(q, jobs[0][1], fix)]
    east = dict(jobs).get("east")
    rows = []
    r0 = refile_row(q, east, fix)
    base = r0["id"]
    tmpl = r0["install_to"].replace("_east.png", "_{facing}.png")
    if row["slot"] in ("variant", "female_pack"):
        r0["prompt"] = ONE_COAT + r0["prompt"]
        rows.append(dict(r0, facings=["east"], install_to=tmpl))
        rows.append({k: v for k, v in dict(r0, facings=[f for f, _ in jobs if f != "east"], install_to=tmpl,
                                         derive_from=f"{base}_east").items() if k != "reference"})
    else:
        sp = base_spec(row["race"])
        adult = (sp.get("images") or {}).get("east") or (sp.get("images") or {}).get("single")
        if adult:
            r0["canon_reference"] = str(L.store_path(L.store_put_file(Path(adult))))   # pinned: the daemon never reads a clone
            r0["prompt"] = ADULT_REF.format(what="young" if row["slot"] == "young" else "female") + r0["prompt"]
        rows.append(dict(r0, facings=[f for f, _ in jobs], install_to=tmpl))    # fill_queue derives north/south from east
    return rows


def cmd_refile(a) -> int:
    q, hold = artpipe(), held()
    rows = []
    fixes = {}
    for run in a.from_run or []:
        rj = REPO / "infrastructure/state/art_eval/runs" / run / "regen_jobs.json"
        for g in json.loads(rj.read_text()) if rj.is_file() else []:
            fixes[g["target_def"]] = g["prompt"]
        for subj, d in decisions(run).items():
            if d.get("decision") == "REGEN" and subj not in fixes:
                fixes[subj] = "; ".join(d.get("reasons") or [])[:600]
            elif d.get("decision") != "REGEN":
                fixes.pop(subj, None)
    for r in commission_rows():
        if r["install_mod"].split("/")[1] in hold:
            continue
        subj = subject_of(r)
        if subj in fixes and look_status(r, q, hold) == "COMPLETE":
            rows += regen_rows(q, r, fixes[subj])
            continue
        for f, j in look_jobs(r, q):
            if a.failed and job_state(q, j) == "failed" and not (rescued_dir() / f"{j}.png").is_file():
                rows.append(refile_row(q, j))
    p = data() / "refile_rows.json"
    p.write_text(json.dumps(rows, indent=1))
    print(len(rows), "rows ->", p)
    if not rows:
        return 0
    cmd = [sys.executable, "fill_queue.py", "--input", str(p)] + (["--dry-run"] if a.dry_run else [])
    return subprocess.run(cmd, cwd=HERE.parent / "artpipe", timeout=900).returncode   # hang guard: filing takes ~1 min

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("looks"); p.add_argument("--all", action="store_true"); p.set_defaults(fn=cmd_looks)
    p = sub.add_parser("spec"); p.add_argument("subjects", nargs="*"); p.add_argument("--complete", action="store_true")
    p.set_defaults(fn=cmd_spec)
    p = sub.add_parser("judge"); p.add_argument("run_id"); p.add_argument("subjects", nargs="+"); p.set_defaults(fn=cmd_judge)
    p = sub.add_parser("install"); p.add_argument("run_id"); p.add_argument("subjects", nargs="*")
    p.add_argument("--dry-run", action="store_true"); p.set_defaults(fn=cmd_install)
    p = sub.add_parser("wire"); p.add_argument("subjects", nargs="*"); p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_wire)
    p = sub.add_parser("faces-file"); p.add_argument("--dry-run", action="store_true")
    p.add_argument("--regen-from", help="file the next version of each set this art_eval run sent back (REGEN)")
    p.add_argument("--kinds", nargs="*"); p.set_defaults(fn=cmd_faces_file)
    p = sub.add_parser("faces-wire"); p.add_argument("kinds", nargs="+"); p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_faces_wire)
    p = sub.add_parser("rescue"); p.add_argument("--dry-run", action="store_true"); p.set_defaults(fn=cmd_rescue)
    p = sub.add_parser("refile"); p.add_argument("--from-run", nargs="*"); p.add_argument("--failed", action="store_true")
    p.add_argument("--dry-run", action="store_true"); p.set_defaults(fn=cmd_refile)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
