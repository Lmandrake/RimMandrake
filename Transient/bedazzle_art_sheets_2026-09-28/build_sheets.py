#!/usr/bin/env python3
"""Build the 2026-09-28 bedazzle art review sheets (Blue Desert / Cracked Lands /
Wasteland / Cauldron) from the artpipe done/ job specs + _artsrc renders.

Chrome is copied verbatim from Transient/contagion_cast_art_review/sheet.html
(the reviewed, check_sheet-passing sheet of the same program); only the CONFIG
and ITEMS JSON blocks are swapped per biome. Decision generator: running this
re-emits PREFILL scaffolds — it refuses if a decisions file was touched by the
sheet, unless --i-know-this-overwrites-the-owners-decisions is passed.
"""
import json, glob, os, re, shutil, sys, html

ROOT = "/mnt/d/Luke/dev/Rimworld"
OUT = os.path.join(ROOT, "Transient/bedazzle_art_sheets_2026-09-28")
CHROME_SRC = os.path.join(ROOT, "Transient/contagion_cast_art_review/sheet.html")

SHEETS = {
    "blue_desert": {
        "sitting": "BLUEDESERT_BEDAZZLE_SITTING_1",
        "title": "BLUE DESERT bedazzle cast — art review",
        "biome": "the Blue Desert",
    },
    "cracked_lands": {
        "sitting": "FLOODEDCANYON_BEDAZZLE_SITTING_1",
        "title": "CRACKED LANDS bedazzle cast — art review",
        "biome": "the Cracked Lands",
    },
    "wasteland": {
        "sitting": "WASTELAND_BEDAZZLE_SITTING_1",
        "title": "WASTELAND bedazzle cast — art review",
        "biome": "the Wasteland",
    },
    "cauldron": {
        "sitting": "CAULDRON_BEDAZZLE_SITTING_1",
        "title": "CAULDRON bedazzle cast — art review",
        "biome": "the Cauldron",
    },
}

# Subjects whose def already exists in the repo and whose art was wired into a
# mod Textures folder by this pass (shown on the row).
WIRED = {
    "RM_Tekk": "src/RimMandrake/Wasteland/Textures/Things/Item/Resource/RM_Tekk.png",
    "RM_Drazz": "src/RimMandrake/Wasteland/Textures/Things/Item/Resource/RM_Drazz.png",
    "RM_BrinePlate": "src/RimMandrake/Wasteland/Textures/Things/Item/Resource/RM_BrinePlate.png",
    "RUT_CrackWax": "src/RimUtinni/UtinniPatches/Textures/Things/Item/Resource/RUT_CrackWax/RUT_CrackWax.png",
}

FACINGS = ("south", "east", "north")


def load_jobs():
    by_sit = {c["sitting"]: [] for c in SHEETS.values()}
    for f in sorted(glob.glob(os.path.join(ROOT, "infrastructure/artpipe/done/*.json"))):
        if f.endswith(".manifest.json"):
            continue
        j = json.load(open(f))
        sit = j.get("rimflow_item_id")
        if sit in by_sit:
            by_sit[sit].append(j)
    return by_sit


def subject_of(job_id):
    for fc in FACINGS:
        if job_id.endswith("_" + fc):
            return job_id[: -(len(fc) + 1)], fc
    return job_id, None


def classify(prompt):
    p = prompt.lower()
    if "creature sprite" in p or "creature" in p.split(":")[0]:
        return "fauna"
    if "plant" in p.split(":")[0] or " tree" in p[:120] or "shrub" in p[:120] or "grass" in p[:120] or "fungus" in p[:120]:
        return "flora"
    return "items"


def effect_line(job):
    p = job.get("prompt", "")
    p = re.sub(r"^RimWorld game [^:]*:\s*", "", p)
    p = re.sub(r"\s+", " ", p).strip()
    return (p[:180] + "…") if len(p) > 180 else p


def build_sheet(key, cfgmeta, jobs, chrome):
    d = os.path.join(OUT, key)
    imgd = os.path.join(d, "img")
    os.makedirs(imgd, exist_ok=True)

    subjects = {}
    for j in jobs:
        subj, fc = subject_of(j["id"])
        s = subjects.setdefault(subj, {"jobs": {}, "spec": j})
        s["jobs"][fc] = j
        if fc in (None, "east"):
            s["spec"] = j

    items = []
    for subj in sorted(subjects):
        s = subjects[subj]
        spec = s["spec"]
        # copy renders locally
        thumbs = []
        if None in s["jobs"]:
            src = os.path.join(ROOT, f"infrastructure/artpipe/_artsrc/{subj}/{subj}.png")
            shutil.copy2(src, os.path.join(imgd, subj + ".png"))
            thumb = f"img/{subj}.png"
        else:
            for fc in FACINGS:
                if fc in s["jobs"]:
                    jid = f"{subj}_{fc}"
                    src = os.path.join(ROOT, f"infrastructure/artpipe/_artsrc/{jid}/{jid}.png")
                    shutil.copy2(src, os.path.join(imgd, jid + ".png"))
                    thumbs.append(f"img/{jid}.png")
            thumb = f"img/{subj}_east.png" if os.path.exists(os.path.join(imgd, subj + "_east.png")) else thumbs[0]
        kind = classify(spec.get("prompt", ""))
        short = cfgmeta["biome"].replace("the ", "")
        group = {"fauna": f"{short} fauna",
                 "flora": f"{short} flora",
                 "items": "Items & structures"}[kind]
        eff = effect_line(spec)
        if subj in WIRED:
            eff = f"[WIRED → {WIRED[subj]}] " + eff
        else:
            eff = "[awaits def build] " + eff
        it = {
            "id": subj,
            "label": subj.split("_", 1)[1] if "_" in subj else subj,
            "group": group,
            "effect": eff,
            "thumb": thumb,
            "prefill": "keep",
        }
        if thumbs:
            it["thumbs"] = thumbs
        items.append(it)
    items.sort(key=lambda x: (x["group"], x["id"]))

    n = len(items)
    wired_n = sum(1 for i in items if i["id"] in WIRED)
    cfg = {
        "sheetId": f"bedazzle_{key}_art_review_2026_09_28",
        "title": cfgmeta["title"],
        "subtitle": f"{n} subjects, all {len(jobs)} jobs done · 0 pending · {wired_n} wired into mod Textures",
        "briefHtml": (
            f"<p>The {html.escape(cfgmeta['biome'])} bedazzle cast (<code>{cfgmeta['sitting']}</code>) — "
            f"{n} subjects from {len(jobs)} artpipe jobs, every one finished (done/, none pending, active or failed). "
            "Faced creatures show south/east/north together; plants, items and structures show one render. "
            "A row tagged <b>[awaits def build]</b> has NO def in the repo yet — its art is staged here only and "
            "will be wired when the biome's RULED_CONTENT build lands; a row tagged <b>[WIRED → …]</b> was "
            "copied into that mod Textures path by this pass (repo copy only, not deployed). "
            "<b>Default is KEEP</b> — a subject ships as-is unless you overrule. <i>Improve</i> queues an "
            "iteration on this art; <i>Regenerate</i> discards it for a fresh prompt — a note on WHAT is wrong "
            "makes either far better.</p>"
        ),
        "criterion": "Prefill = artpipe validator/facts PASS, which ranks technical validity (alpha, canvas, facing presence) — it cannot rank whether the thing looks right for the biome. Your eye rules.",
        "invented": [
            "Section grouping (fauna/flora/items & structures) is my own bucketing from each job's prompt wording — it carries no ranking or ruling.",
        ],
        "posture": {
            "mode": "blacklist",
            "explain": "Default is KEEP. Only subjects marked improve/regenerate get new art jobs; everything else ships as rendered.",
        },
        "options": [
            {"key": "keep", "label": "Keep", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "improve", "label": "Improve", "hotkey": "2", "color": "#e0b34c", "counts": "out"},
            {"key": "regen", "label": "Regenerate", "hotkey": "3", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "section",
        "media": True,
        "decisionsFile": "decisions.json",
        "decisionsPath": "",
        "sheetPath": "",
    }

    page = chrome
    page = re.sub(
        r'(<script id="CONFIG" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(cfg, indent=1) + m.group(2),
        page, count=1, flags=re.S)
    page = re.sub(
        r'(<script id="ITEMS" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(items, indent=1) + m.group(2),
        page, count=1, flags=re.S)
    page = page.replace("<title>CONTAGION bedazzle cast — art review</title>",
                        f"<title>{cfgmeta['title']}</title>")
    with open(os.path.join(d, "sheet.html"), "w") as f:
        f.write(page)

    decf = os.path.join(d, "decisions.json")
    if os.path.exists(decf):
        old = json.load(open(decf))
        touched = bool(old.get("savedBy") or old.get("writeCount"))
        if touched and "--i-know-this-overwrites-the-owners-decisions" not in sys.argv:
            print(f"REFUSING to overwrite touched decisions file {decf}")
            return n, wired_n
    dec = {
        "posture": "blacklist",
        "decidedCount": 0,
        "decisions": {},
        "reviewStatus": {
            "state": "prefill",
            "by": None,
            "at": None,
            "evidence": f"Generated by build_sheets.py for {cfgmeta['sitting']}; every row prefilled keep; no human has ruled yet.",
        },
    }
    with open(decf, "w") as f:
        json.dump(dec, f, indent=1)
    return n, wired_n


def main():
    chrome = open(CHROME_SRC).read()
    by_sit = load_jobs()
    for key, meta in SHEETS.items():
        jobs = by_sit[meta["sitting"]]
        n, w = build_sheet(key, meta, jobs, chrome)
        print(f"{key}: {n} subjects from {len(jobs)} jobs, {w} wired")


if __name__ == "__main__":
    main()
