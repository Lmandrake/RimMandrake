#!/usr/bin/env python3
"""Flyer census 2026-10-08 (FLYER_STABLE_BODY_GATE_1).

Every creature ThingDef of ours (src/**, race ThingDefs, ParentName resolved within our files) that flies or
should fly: MaxFlightTime > 0 (own, inherited or patch-added), OR its description / canon entry says it flies.
Also donor flyers we re-skin through an *ArtOverride mod (their static art is ours, their flip-book is not).

Read-only. Writes Transient/flyer_census_2026-10-08.csv. Prints a sanity probe first.
    python3 Transient/flyer_census_2026-10-08.py [--no-art]
"""
from __future__ import annotations
import csv, json, os, re, subprocess, sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
CANON = REPO / "design/RimStarWars/canon_references"
DONOR = Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3497316713")
ARTPIPE = Path("/mnt/d/Luke/dev/_artpipe")
OUT = REPO / "Transient/flyer_census_2026-10-08.csv"

FLY = re.compile(r"\b(fl(?:y|ies|ying|ight|ights|ew|own|yer|yers|ier|iers)|winged|wings?|glid(?:e|es|ing|er|ers)|"
                 r"airborne|soar\w*|aloft|hover\w*|flutter\w*|aerial|swoop\w*|on the wing)\b", re.I)
NEG = re.compile(r"\b(wingless|flightless|cannot fly|can't fly|unable to fly|never flies|does not fly|"
                 r"vestigial wings?|no wings|lost (?:its|the) wings)\b", re.I)
STRONG = re.compile(r"\b(fl(?:y|ies|ying|ew|own|yer|yers|ier|iers)|in flight|airborne|soar\w*|aloft|glid\w+|"
                    r"swoop\w*|on the wing|hover\w*)\b", re.I)


def xml_files(root: Path):
    for p in root.rglob("*.xml"):
        s = str(p)
        if "/Defs/" in s or "/Patches/" in s or "/Defs" in s:
            yield p


def parse(p):
    try:
        return ET.parse(p).getroot()
    except Exception:
        return None


def txt(e, path):
    x = e.find(path)
    return (x.text or "").strip() if x is not None and x.text else ""


# ---------------------------------------------------------------- collect our defs
thingdefs: dict[str, dict] = {}          # by defName (or Name for abstracts, key "@Name")
pawnkinds: list[dict] = []
biome_roster = defaultdict(set)          # creature -> biomes
patch_flight = defaultdict(list)         # defName -> evidence of patch-added MaxFlightTime/flying frames
patch_targets = defaultdict(set)         # defName -> mods that patch it (for donor overrides)

XP_DEF = re.compile(r'(ThingDef|PawnKindDef|BiomeDef)\[(?:@Name|defName)\s*=\s*"([^"]+)"\]')

for p in xml_files(SRC):
    r = parse(p)
    if r is None:
        continue
    mod = str(p.relative_to(SRC)).split("/")
    mod = "/".join(mod[:2])
    if r.tag == "Defs":
        for e in r:
            if e.tag == "ThingDef":
                key = txt(e, "defName") or ("@" + e.get("Name", "")) if not txt(e, "defName") else txt(e, "defName")
                d = dict(defName=txt(e, "defName"), name=e.get("Name"), parent=e.get("ParentName"),
                         abstract=e.get("Abstract", "").lower() == "true", label=txt(e, "label"),
                         desc=txt(e, "description"), race=e.find("race") is not None,
                         mft=txt(e, "statBases/MaxFlightTime"), mod=mod, file=str(p.relative_to(REPO)),
                         intel=txt(e, "race/intelligence"), body=txt(e, "race/body"),
                         canFlyIntoMap=txt(e, "race/canFlyIntoMap"))
                if d["defName"]:
                    thingdefs[d["defName"]] = d
                if d["name"]:
                    thingdefs.setdefault("@" + d["name"], d)
            elif e.tag == "PawnKindDef":
                pk = dict(defName=txt(e, "defName"), race=txt(e, "race"), parent=e.get("ParentName"),
                          prefix=txt(e, "flyingAnimationFramePathPrefix"),
                          prefixF=txt(e, "flyingAnimationFramePathPrefixFemale"),
                          frames=txt(e, "flyingAnimationFrameCount"), mod=mod,
                          tex=[(x.text or "").strip() for x in e.iter("texPath")])
                pawnkinds.append(pk)
            elif e.tag == "BiomeDef":
                wa = e.find("wildAnimals")
                if wa is not None:
                    for c in wa:
                        nm = c.find("animal").text.strip() if c.tag == "li" and c.find("animal") is not None else c.tag
                        biome_roster[nm].add(txt(e, "defName"))
    elif r.tag == "Patch":
        for op in r.iter():
            xp = op.find("xpath")
            if xp is None or not xp.text:
                continue
            xpt = xp.text
            val = op.find("value")
            for kind, name in XP_DEF.findall(xpt):
                patch_targets[name].add(mod)
                if kind == "BiomeDef" and "wildAnimals" in xpt and val is not None:
                    for c in val.iter():
                        if c is val or c.tag in ("wildAnimals", "li", "animal", "commonality"):
                            if c.tag == "animal" and c.text:
                                biome_roster[c.text.strip()].add(name)
                            continue
                        if c.tag not in ("li",):
                            biome_roster[c.tag].add(name)
                if val is not None:
                    blob = ET.tostring(val, encoding="unicode")
                    if kind in ("ThingDef", "PawnKindDef") and ("MaxFlightTime" in blob or "MaxFlightTime" in xpt):
                        patch_flight[name].append(f"MaxFlightTime patch in {p.relative_to(REPO)}")
                    if "flyingAnimationFramePathPrefix" in blob or "flyingAnimationFramePathPrefix" in xpt:
                        m = re.search(r"<flyingAnimationFramePathPrefix>([^<]+)<", blob)
                        patch_flight[name].append("frames:" + (m.group(1) if m else "?"))


def resolve(d, field, seen=None):
    seen = seen or set()
    v = d.get(field)
    if v:
        return v
    par = d.get("parent")
    if not par or par in seen:
        return v
    seen.add(par)
    pd = thingdefs.get("@" + par)
    return resolve(pd, field, seen) if pd else v


def inherited_race(d, seen=None):
    seen = seen or set()
    if d.get("race"):
        return True
    par = d.get("parent")
    if par and par not in seen:
        seen.add(par)
        pd = thingdefs.get("@" + par)
        if pd:
            return inherited_race(pd, seen)
        return par.lower().startswith(("animal", "basepawn", "insect", "bird", "base")) and "Animal" in par or par in (
            "AnimalThingBase", "BasePawn", "AnimalThingBaseNoLeather")
    return False


# ---------------------------------------------------------------- canon index
canon = {}
for d in CANON.iterdir():
    if d.is_dir() and not d.name.startswith("_"):
        t = ""
        for f in d.glob("*.md"):
            try:
                t += open(f, errors="ignore").read() + "\n"
            except Exception:
                pass
        canon[d.name] = t


def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())


def canon_slug(defname, label):
    stem = re.sub(r"^(RM|RSW|RUT)_", "", defname)
    for k in (norm(stem), norm(label)):
        if k in canon:
            return k
    return ""


def fly_signal(text):
    if not text:
        return "", ""
    hits = [m.group(0) for m in FLY.finditer(text)]
    if not hits:
        return "", ""
    neg = NEG.search(text)
    strong = STRONG.search(text)
    m = (strong or FLY.search(text))
    s = max(0, m.start() - 60)
    snip = text[s:m.end() + 60].replace("\n", " ")
    level = "strong" if strong else "winged"
    if neg and not strong:
        level = "negated"
    return level, snip


def canon_fly(text):
    """Only the canon facts/brief section; ignore the must-show checklist noise from other words."""
    return fly_signal(text[:6000])


# ---------------------------------------------------------------- texture existence
tex_index = set()
for p in SRC.rglob("*.png"):
    s = str(p)
    i = s.find("/Textures/")
    if i >= 0:
        tex_index.add(s[i + 10:-4])
donor_tex = set()
if DONOR.exists():
    for p in (DONOR / "Textures").rglob("*.png"):
        s = str(p)
        donor_tex.add(s[s.find("/Textures/") + 10:-4])
donor_flyers = {}
if DONOR.exists():
    for f in (DONOR / "1.6/Defs").rglob("*.xml"):
        r = parse(f)
        if r is None:
            continue
        for e in r:
            if e.tag == "PawnKindDef" and txt(e, "flyingAnimationFramePathPrefix"):
                donor_flyers[txt(e, "race") or txt(e, "defName")] = dict(
                    prefix=txt(e, "flyingAnimationFramePathPrefix"), frames=txt(e, "flyingAnimationFrameCount"),
                    pk=txt(e, "defName"))


def frame_source(prefix):
    if not prefix:
        return "none"
    k = prefix + "1_east"
    if k in tex_index:
        return "ours"
    if k in donor_tex:
        return "donor"
    return "MISSING"


# ---------------------------------------------------------------- pending artpipe jobs
pending_jobs = []
for st in ("pending", "active"):
    d = ARTPIPE / st
    if d.exists():
        for f in d.glob("*.json"):
            try:
                j = json.load(open(f))
            except Exception:
                continue
            pending_jobs.append((st, f.stem, str(j.get("target_def", "")), str(j.get("prompt", ""))[:400]))


def pending_for(defname, label):
    stem = norm(re.sub(r"^(RM|RSW|RUT)_", "", defname))
    out = []
    for st, jid, td, _ in pending_jobs:
        toks = [norm(t) for t in jid.split("_")]
        if td == defname or (stem and stem in toks):
            out.append(f"{st}:{jid}")
    return out


# ---------------------------------------------------------------- build rows
rows = []
for name, d in thingdefs.items():
    if name.startswith("@") or d["abstract"] or not inherited_race(d):
        continue
    dn = d["defName"]
    desc = resolve(d, "desc") or ""
    mft = resolve(d, "mft") or ""
    label = d["label"] or dn
    slug = canon_slug(dn, label)
    dlev, dsnip = fly_signal(desc)
    clev, csnip = canon_fly(canon.get(slug, "")) if slug else ("", "")
    pks = [pk for pk in pawnkinds if pk["race"] == dn]
    prefix = next((pk["prefix"] for pk in pks if pk["prefix"]), "")
    frames = next((pk["frames"] for pk in pks if pk["frames"]), "")
    pf = [x for x in patch_flight.get(dn, []) + sum((patch_flight.get(pk["defName"], []) for pk in pks), [])]
    if not prefix:
        for x in pf:
            if x.startswith("frames:"):
                prefix = x[7:]
    try:
        mftv = float(mft) if mft else 0.0
    except ValueError:
        mftv = -1
    patched_mft = any("MaxFlightTime" in x for x in pf)
    reasons = []
    if mftv > 0:
        reasons.append("MaxFlightTime")
    if patched_mft:
        reasons.append("patch-MaxFlightTime")
    if dlev in ("strong", "winged"):
        reasons.append("desc-" + dlev)
    if clev in ("strong", "winged"):
        reasons.append("canon-" + clev)
    if not reasons:
        continue
    rows.append(dict(defName=dn, label=label, mod=d["mod"], kind="ours",
                     biomes=";".join(sorted(biome_roster.get(dn, set()))),
                     max_flight_time=mft or ("patched" if patched_mft else ""),
                     frame_prefix=prefix, frame_count=frames, frame_source=frame_source(prefix),
                     canon_entry=slug, reasons="+".join(reasons), desc_snippet=dsnip, canon_snippet=csnip,
                     intelligence=resolve(d, "intel") or "", body=resolve(d, "body") or "",
                     pending_jobs=";".join(pending_for(dn, label)), file=d["file"]))

# donor flyers whose look we override (ArtOverride mods / ports patching the donor def)
ours_dn = {r["defName"] for r in rows}
for race, info in donor_flyers.items():
    if race in ours_dn:
        continue
    mods = sorted(patch_targets.get(race, set()) | patch_targets.get(info["pk"], set()))
    port = [r for r in rows if norm(re.sub(r"^(RM|RSW|RUT)_", "", r["defName"])) == norm(race)]
    slug = norm(race) if norm(race) in canon else ""
    rows.append(dict(defName=race, label=race, mod=";".join(mods) or "(donor only)", kind="donor" + ("+ported" if port else ""),
                     biomes=";".join(sorted(biome_roster.get(race, set()))), max_flight_time="donor",
                     frame_prefix=info["prefix"], frame_count=info["frames"], frame_source=frame_source(info["prefix"]),
                     canon_entry=slug, reasons="donor-flipbook", desc_snippet="", canon_snippet="",
                     intelligence="", body="", pending_jobs=";".join(pending_for(race, race)), file=""))

# ---------------------------------------------------------------- adjudication (read every desc/canon-only hit by hand)
ADJ = {  # defName -> (flies verdict, why). Only rows WITHOUT MaxFlightTime need one; reviewed 2026-10-08.
    "RM_BloodropMoth": ("should-fly", "desc: 'a pale, near-silent flier'; no MaxFlightTime"),
    "RSW_FacetMoth": ("should-fly", "desc: moth that 'flits about in dark caverns'; no MaxFlightTime"),
    "RSW_Baseopsis": ("maybe", "giant earwig, 'wings fold like paper' -- earwigs rarely fly; owner call"),
    "RSW_Gorg": ("no", "canon mentions a bio-engineered winged 'chubafly' variant, not the gorg"),
}
NO = {"RM_Gharrek": "fluttering gill-fans, a crawler", "RM_Ysvaltha": "blades folded 'like wings'",
      "RM_SparkleechGrub": "grub, 'grow into something that flies'", "RM_TheUnfinished": "'a wing that never had anywhere to go'",
      "RM_Barkwarden": "'It cannot fly'", "RM_Liliana": "'It cannot fly'", "RM_Siidda": "carried aloft passively as dust",
      "RM_DancingSkresh": "'aloft' in water: a swimmer", "RSW_Gelagrub": "canon: eyes spot aerial attacks",
      "RSW_Glowtail": "lures flying insects", "RSW_Grank": "senses airborne vibrations", "RSW_Jimvu": "'in flight' = fleeing; canon: no wings",
      "RSW_KraytDragon": "one legendary winged individual", "RSW_Laa": "wing-like fins (fish)", "RSW_Lothcat": "episode title",
      "RSW_MegaphoridLarva": "larva of a fly", "RSW_Nuna": "canon: could not fly", "RSW_Ronto": "wing-like ear flaps",
      "RSW_Segnosaurus": "claws 'glide through paper'", "RSW_WompRat": "shot at while flying skyhoppers"}
for k, v in NO.items():
    ADJ[k] = ("no", v)
for r in rows:
    if r["kind"] != "ours":
        r["flies"] = "flies (donor def)"
        continue
    if r["max_flight_time"] and r["max_flight_time"] not in ("0", ""):
        r["flies"] = "flies"
        r["adjudication"] = ""
    else:
        v = ADJ.get(r["defName"], ("UNADJUDICATED", ""))
        r["flies"], r["adjudication"] = v
rows[:] = [r for r in rows if r["flies"] != "no" and r["kind"] != "donor+ported"]

# frame provenance: sha of <prefix>1_east.png vs art-ledger variants of kind donor
import hashlib
sha_kinds = defaultdict(set)
for f in (REPO / "infrastructure/state/art/events").glob("*.jsonl"):
    for l in open(f):
        e = json.loads(l)
        if e.get("type") == "variant":
            sha_kinds[e["sha"]].add(e.get("kind", ""))
tex_file = {}
for p in SRC.rglob("*.png"):
    s = str(p); i = s.find("/Textures/")
    if i >= 0:
        tex_file.setdefault(s[i + 10:-4], p)
for r in rows:
    pre = r["frame_prefix"]
    if not pre:
        r["frame_provenance"] = "no flip-book"
    elif r["frame_source"] != "ours" and pre.startswith("Things/Pawn/Animal/"):
        r["frame_provenance"] = "vanilla Core frames (borrowed)"
    elif r["frame_source"] == "ours":
        f = tex_file.get(pre + "1_east")
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()
        k = sha_kinds.get(h, set())
        r["frame_provenance"] = "donor-copy (cartoon)" if "donor" in k else ("generated/ours" if k else "ours, not in ledger")
    else:
        r["frame_provenance"] = "donor bundle (cartoon)" if pre.startswith("swanimals/") else "MISSING"

# ---------------------------------------------------------------- art ledger status
def art_status(dn):
    try:
        out = subprocess.run([sys.executable, str(SRC / "RimMandrake/Utils/art/art.py"), "status", dn],
                             capture_output=True, text=True, timeout=120, cwd=REPO).stdout
    except Exception as ex:
        return dict(art_live="UNMEASURED", art_protected="", last_ruling="", flight_tex_ledger="")
    live = re.findall(r"LIVE (\S+)\s+(\S+)\s+\S+\s*(PROTECTED)?", out)
    body_live = [l for l in live if "Flying" not in l[1]]
    fly_live = [l for l in live if "Flying" in l[1]]
    prot = sum(1 for l in body_live if l[2])
    rul = re.findall(r"^\s+(\d{4}-\d\d-\d\d)\s+(\S+)\s+trust=(\S+)\s+(\S+)\s*(.*)$", out, re.M)
    rul.sort()
    last = f"{rul[-1][0]} {rul[-1][1]} ({rul[-1][3][:40]}): {rul[-1][4][:90]}" if rul else ""
    mods = sorted({l[0] for l in body_live})
    return dict(art_live=f"{len(body_live)} files in {','.join(mods)}" if body_live else "none-in-ledger",
                art_protected=str(prot), last_ruling=last,
                flight_tex_ledger=f"{len(fly_live)} live" if fly_live else "0")


if "--no-art" not in sys.argv:
    with ThreadPoolExecutor(6) as ex:
        for r, s in zip(rows, ex.map(lambda r: art_status(r["defName"]), rows)):
            r.update(s)

# ---------------------------------------------------------------- sanity probe + output
PROBE = ["firehawk", "firewasp", "screecher", "hawkbat", "mynock"]
print("SANITY PROBE (stem -> rows matched):")
for k in PROBE:
    hit = [r["defName"] for r in rows if k in norm(r["defName"]) or k in norm(r["label"])]
    print(f"  {k:10s} {len(hit)}  {hit[:4]}")
print(f"race ThingDefs scanned: {sum(1 for k, d in thingdefs.items() if not k.startswith('@') and not d['abstract'] and inherited_race(d))}"
      f"  | pawnkinds {len(pawnkinds)} | biome-roster creatures {len(biome_roster)} | canon entries {len(canon)}"
      f" | donor flyers {len(donor_flyers)} | pending/active jobs {len(pending_jobs)}")
cols = ["defName", "label", "kind", "flies", "adjudication", "mod", "biomes", "reasons", "max_flight_time", "frame_prefix",
        "frame_count", "frame_source", "frame_provenance", "canon_entry", "art_live", "art_protected", "last_ruling", "flight_tex_ledger",
        "pending_jobs", "intelligence", "body", "desc_snippet", "canon_snippet", "file"]
rows.sort(key=lambda r: (r["kind"], r["mod"], r["defName"]))
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
from collections import Counter
print("rows", len(rows), Counter(r["kind"] for r in rows))
print("reasons", Counter(r["reasons"] for r in rows).most_common(12))
print("frame_provenance", Counter(r["frame_provenance"] for r in rows))
print("flies", Counter(r["flies"] for r in rows))
print("wrote", OUT)
