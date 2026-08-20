#!/usr/bin/env python3
r"""validate_ideoligion.py — check a religion against the LIVE def dump.

WHY THIS EXISTS. Every way an ideoligion can be wrong fails SILENTLY. A meme that
is not installed, two memes sharing an `exclusionTag`, a precept whose
`conflictingMemes` names a meme you took, a `deityPresets` block on a structure
with `deityCount 0` — none of these produce a red error. The faction simply
generates something else and the design is gone, discovered (if ever) 25 minutes
into a cold load.

This runs offline in under a second and is the gate before any of that.

    python3 src/RimMandrake/Utils/validate_ideoligion.py --md design/Jawa/worldbuilding/faction_religions_spec.md
    python3 src/RimMandrake/Utils/validate_ideoligion.py --xml src/Jawa/.../FactionDefs.xml
    python3 src/RimMandrake/Utils/validate_ideoligion.py --spec my_religion.json

Exit 0 = no ERRORs. WARNs and INFO never change the exit code.

THE JSON SPEC FORMAT (also what --md and --xml are parsed into):

    {"religions": [{
       "name": "the Unmoving Noon",
       "memes":   ["Structure_TheistEmbodied", "Loyalist", "HumanPrimacy"],
       "candidateMemes": ["MaleSupremacy", "FemaleSupremacy"],
       "precepts":["Slavery_Acceptable", "Execution_Required"],
       "styles":  ["Techist"],
       "deities": 1,
       "fixedIdeo": true, "requiredPreceptsOnly": true,
       "target": "faction",         // or "player" — changes two checks
       // raw FactionDef lists, only for the game's own two ConfigErrors.
       // null/absent = the tag is not on the def at all.
       "allowedMemes": null, "disallowedMemes": null, "requiredMemes": null
    }]}

🔴 HELD vs CANDIDATE. `memes` is what the religion **holds simultaneously**
(`forcedMemes` + `requiredMemes`). `candidateMemes` is a **menu of alternatives**
the generator draws a remainder from (`allowedMemes` + `structureMemeWeights`
children) — its entries are NOT expected to coexist. Coexistence checks
(`meme/exclusion`, `structure/multiple`, `precept/conflicting-meme`) therefore
run over the held set only; candidates still get every existence check, because a
typo in `allowedMemes` is a real bug. Merging the two was a measured false
positive on Ludeon's own Empire (fixed 2026-08-14).

⚠️ `precepts` is a DESIGN artefact. No FactionDef or IdeoPresetDef field lists an
ideo's precepts (FactionDef has `disallowedPrecepts`, a blacklist, and nothing
else). The list is still checked — it is what a review judges and what an in-game
ideo-editor session is transcribed into — but --xml can never populate it, and
`route/preceptsUnauthorable` fires if you hand a faction one.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from game_paths import LOCALLOW, MODS_CONFIG  # noqa: E402

DUMP = Path(LOCALLOW) / "DefDump" / "defs"
LUDEON = ("ludeon.rimworld",)

# The engine's own cap on total meme impact. Left None until it is MEASURED out
# of Assembly-CSharp (symbols: MaxMemeImpact, MemeCountRangeAbsolute). Pass
# --impact-budget N to enforce a number you have verified; otherwise the total is
# reported as INFO and nothing is failed on a guess.
DEFAULT_IMPACT_BUDGET = None


# --------------------------------------------------------------------------- #
# the dump
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict[str, dict]:
    p = DUMP / f"{name}.json"
    if not p.is_file():
        sys.exit(f"missing {p} — run a def dump from the live game first")
    return {d["defName"]: d for d in json.loads(p.read_text(encoding="utf-8"))["defs"]}


class Dump:
    def __init__(self) -> None:
        self.memes = _load("MemeDef")
        self.precepts = _load("PreceptDef")
        self.issues = _load("IssueDef")
        self.styles = _load("StyleCategoryDef")
        self.rituals = _load("RitualPatternDef")
        try:
            man = json.loads((DUMP.parent / "manifest.json").read_text(encoding="utf-8"))
            self.stamp = f'{man.get("capturedUtc", "?")}, game {man.get("gameVersion", "?")}'
        except Exception:
            self.stamp = "unknown capture"
        self.active = _active_mods()

    @staticmethod
    def f(d: dict, key, default=None):
        return (d.get("fields") or {}).get(key, default)

    def pkg(self, d: dict) -> str:
        return (d.get("packageId") or "").lower()

    def is_modded(self, d: dict) -> bool:
        return not self.pkg(d).startswith(LUDEON)

    def kind(self, name: str) -> str:
        if name in self.memes:
            return "meme"
        if name in self.precepts:
            return "precept"
        if name in self.styles:
            return "style"
        return "?"


# Overridden by --mods-config. 🔴 Without it a run during a minimal-list window
# reports every modded meme as `def/inactive-mod` and the whole religion INVALID —
# a fact about the LIVE list, not about the file being checked.
MODS_CONFIG_OVERRIDE: Path | None = None


def _active_mods() -> set[str]:
    try:
        root = ET.parse(MODS_CONFIG_OVERRIDE or MODS_CONFIG).getroot()
    except Exception:
        return set()
    out = set()
    for li in root.iter("li"):
        if li.text:
            out.add(li.text.strip().lower().removesuffix("_steam"))
    return out


# --------------------------------------------------------------------------- #
# findings
# --------------------------------------------------------------------------- #
class Report:
    def __init__(self, name: str) -> None:
        self.name = name
        self.rows: list[tuple[str, str, str]] = []

    def add(self, level, code, msg):
        self.rows.append((level, code, msg))

    E = "ERROR"
    W = "WARN"
    I = "INFO"

    @property
    def errors(self) -> int:
        return sum(1 for lv, _, _ in self.rows if lv == self.E)

    def print(self) -> None:
        icon = {"ERROR": "🔴", "WARN": "⚠️ ", "INFO": "  "}
        verdict = "INVALID" if self.errors else "VALID"
        print(f"\n=== {self.name} — {verdict}")
        for lv, code, msg in self.rows:
            print(f"  {icon[lv]} {lv:<5} {code:<28} {msg}")
        if not self.rows:
            print("  (nothing to report)")


# --------------------------------------------------------------------------- #
# the checks
# --------------------------------------------------------------------------- #
def check(rel: dict, D: Dump, budget) -> Report:
    r = Report(rel.get("name") or "(unnamed)")
    memes = list(dict.fromkeys(rel.get("memes") or []))
    # a MENU the generator draws from — alternatives, never simultaneous
    cands = [n for n in dict.fromkeys(rel.get("candidateMemes") or []) if n not in memes]
    precepts = list(dict.fromkeys(rel.get("precepts") or []))
    styles = list(dict.fromkeys(rel.get("styles") or []))
    deities = int(rel.get("deities") or 0)
    target = (rel.get("target") or "faction").lower()

    # -- vocabulary -------------------------------------------------------- #
    for n in memes:
        if n not in D.memes:
            r.add(r.E, "def/unknown-meme", f"{n} is not an installed MemeDef")
    for n in cands:
        if n not in D.memes:
            r.add(r.E, "def/unknown-meme",
                  f"{n} is not an installed MemeDef (candidate — allowedMemes/"
                  "structureMemeWeights)")
    for n in precepts:
        if n not in D.precepts:
            r.add(r.E, "def/unknown-precept", f"{n} is not an installed PreceptDef")
    for n in styles:
        if n not in D.styles:
            r.add(r.E, "def/unknown-style", f"{n} is not an installed StyleCategoryDef")

    known_memes = [n for n in memes if n in D.memes]
    known_cands = [n for n in cands if n in D.memes]
    known_precepts = [n for n in precepts if n in D.precepts]
    meme_set = set(known_memes)

    # -- MayRequire / active mods ------------------------------------------ #
    for n in known_memes + known_cands + known_precepts + [s for s in styles if s in D.styles]:
        d = D.memes.get(n) or D.precepts.get(n) or D.styles[n]
        if not D.is_modded(d):
            continue
        pkg = D.pkg(d)
        if D.active and pkg.removesuffix("_steam") not in D.active:
            r.add(r.E, "def/inactive-mod",
                  f"{n} comes from {pkg}, which is NOT in ModsConfig activeMods")
        else:
            r.add(r.I, "def/needs-mayrequire",
                  f'{n} → MayRequire="{d.get("packageId")}"  ({d.get("modName")})')

    # -- structure --------------------------------------------------------- #
    # exactly-one applies to the HELD set. Candidate structures are a weighted
    # pick of one, so several of them is normal, not a collision.
    structs = [n for n in known_memes if D.f(D.memes[n], "category") == "Structure"]
    cstructs = [n for n in known_cands if D.f(D.memes[n], "category") == "Structure"]
    if not structs:
        if cands:
            r.add(r.I, "structure/generated",
                  "no structure meme is held; the generator picks one from "
                  + (f"{cstructs} (weighted)" if cstructs else "the whole structure pool"))
        else:
            r.add(r.E, "structure/none",
                  "no structure meme — every ideoligion has exactly one")
    elif len(structs) > 1:
        r.add(r.E, "structure/multiple", f"{len(structs)} structure memes: {structs}")
    elif cstructs:
        r.add(r.W, "structure/candidate-shadowed",
              f"{structs[0]} is held, so the candidate structure(s) {cstructs} can "
              "never be drawn — one of the two lists is wrong")

    # -- deities ----------------------------------------------------------- #
    # off the held structure, or an unambiguous single candidate one
    deity_struct = structs[0] if len(structs) == 1 else (
        cstructs[0] if not structs and len(cstructs) == 1 else None)
    if deity_struct:
        dc = D.f(D.memes[deity_struct], "deityCount") or {}
        lo, hi = int(dc.get("min", 0)), int(dc.get("max", 0))
        if lo < 0:
            lo = hi = 0
        if deities and hi == 0:
            # NOT an error: Ludeon's own HoraxCult puts one deityPreset on
            # Structure_Archist (deityCount 0). deityCount governs how many
            # deities the GENERATOR invents; deityPresets supplies them
            # explicitly. Unproven whether the preset then displays — that is on
            # the live-load checklist (references/validation.md).
            r.add(r.W, "deity/structure-generates-none",
                  f"{deities} deity(s) named on {deity_struct}, which has deityCount 0. "
                  "Legal — HoraxCult ships exactly this — but the structure invents "
                  "no gods of its own, so the religion has only what you name.")
        elif deities and not (lo <= deities <= hi):
            r.add(r.W, "deity/count",
                  f"{deities} deity(s) named; {deity_struct} generates {lo}..{hi}")
        elif lo > 0 and not deities:
            r.add(r.W, "deity/missing",
                  f"{deity_struct} requires {lo}..{hi} deities and none are named — "
                  "the generator will invent them")
        elif hi > 0:
            r.add(r.I, "deity/ok", f"{deity_struct} deityCount {lo}..{hi}, {deities} named")

    # -- meme exclusion tags ----------------------------------------------- #
    # HELD memes only. Two candidates sharing a tag are alternatives, which is
    # what a menu is for — Ludeon's Empire offers Male- and FemaleSupremacy.
    tagged: dict[str, list[str]] = defaultdict(list)
    for n in known_memes:
        for t in D.f(D.memes[n], "exclusionTags") or []:
            tagged[t].append(n)
    for t, ns in sorted(tagged.items()):
        if len(ns) > 1:
            r.add(r.E, "meme/exclusion",
                  f"{' + '.join(ns)} all carry exclusionTag '{t}' — they cannot coexist")
    # a candidate that collides with a HELD meme can never be drawn — the menu is
    # wrong as a set, but nothing is broken at generation, so WARN
    for n in known_cands:
        dead = sorted({f"{h} ('{t}')" for t in D.f(D.memes[n], "exclusionTags") or []
                       for h in tagged.get(t, [])})
        if dead:
            r.add(r.W, "meme/candidate-excluded",
                  f"candidate {n} shares an exclusionTag with held {', '.join(dead)} — "
                  "it can never be drawn")

    # -- meme impact -------------------------------------------------------- #
    # summed over the held set; candidates are alternatives, so their impacts do
    # not add up to anything the engine ever sees at once
    total = sum(int(D.f(D.memes[n], "impact") or 0) for n in known_memes)
    per = ", ".join(f"{n}:{D.f(D.memes[n], 'impact')}" for n in known_memes)
    if cands:
        per += f"; + {len(cands)} candidate(s) the generator may add"
    if budget is not None and total > budget:
        r.add(r.E, "meme/impact-budget", f"total impact {total} > budget {budget} ({per})")
    else:
        r.add(r.I, "meme/impact", f"total impact {total} over {len(known_memes)} memes ({per})")

    # -- the two ConfigErrors FactionDef raises for itself ------------------ #
    # verified as game behaviour; strings live in Assembly-CSharp 1.6.4871
    allowed = rel.get("allowedMemes")
    if allowed is not None:
        if rel.get("disallowedMemes") is not None:
            r.add(r.E, "faction/both-meme-lists",
                  "both disallowedMemes (black list) and allowedMemes (white list) are "
                  "defined — the game rejects this as a ConfigError")
        outside = [n for n in (rel.get("requiredMemes") or []) if n not in allowed]
        if outside:
            r.add(r.E, "faction/required-not-allowed",
                  f"requiredMemes {outside} are not in allowedMemes — the game raises "
                  '"has a required meme which is not allowed:" per entry')

    # -- meme requireOne: which precepts the memes DRAG IN ------------------ #
    for n in known_memes:
        for group in D.f(D.memes[n], "requireOne") or []:
            if not group:
                continue
            if known_precepts and not (set(group) & set(known_precepts)):
                r.add(r.W, "meme/requireOne",
                      f"{n} requires one of {group}; the spec names none of them — "
                      "the generator picks, not you")

    # -- precepts ----------------------------------------------------------- #
    by_issue: dict[str, list[str]] = defaultdict(list)
    ptags: dict[str, list[str]] = defaultdict(list)
    for n in known_precepts:
        p = D.precepts[n]
        conflict = set(D.f(p, "conflictingMemes") or []) & meme_set
        if conflict:
            r.add(r.E, "precept/conflicting-meme",
                  f"{n} lists {sorted(conflict)} in conflictingMemes — hard exclusion")
        req = D.f(p, "requiredMemes") or []
        if req and not (set(req) & meme_set):
            r.add(r.E, "precept/required-meme",
                  f"{n} requires one of {req}; none is in the meme set")
        if D.f(p, "visible") is False:
            r.add(r.E, "precept/invisible",
                  f"{n} has visible:false — engine-internal, never hand-author it")
        if target == "faction" and D.f(p, "enabledForNPCFactions") is False:
            r.add(r.E, "precept/npc-disabled",
                  f"{n} has enabledForNPCFactions:false — it cannot appear on a faction ideo")
        iss = D.f(p, "issue")
        if iss:
            by_issue[iss].append(n)
            if iss not in D.issues:
                r.add(r.W, "precept/orphan-issue", f"{n} names issue {iss}, which is not installed")
        for t in D.f(p, "exclusionTags") or []:
            ptags[t].append(n)

    for iss, ns in sorted(by_issue.items()):
        if len(ns) > 1:
            dup = any(D.f(D.precepts[n], "allowDuplicates") for n in ns)
            r.add(r.W if dup else r.E, "precept/issue-duplicate",
                  f"issue {iss} carries {len(ns)} precepts: {ns} — one position per issue")
    for t, ns in sorted(ptags.items()):
        if len(ns) > 1:
            r.add(r.E, "precept/exclusion", f"{ns} share exclusionTag '{t}'")

    counted = [n for n in known_precepts
               if D.f(D.precepts[n], "countsTowardsPreceptLimit") is not False]
    if known_precepts:
        r.add(r.I, "precept/count",
              f"{len(known_precepts)} precepts, {len(counted)} count towards the limit")

    # -- authoring route ----------------------------------------------------- #
    if target == "faction" and known_precepts:
        r.add(r.W, "route/precepts-unauthorable",
              f"{len(known_precepts)} precepts listed, but no FactionDef field can set them "
              "(disallowedPrecepts is a blacklist). This is a design/review artefact only.")
    if rel.get("fixedIdeo") and not known_memes:
        r.add(r.E, "route/fixed-no-memes",
              "fixedIdeo true with no memes — the generator fills it randomly anyway")
    if rel.get("requiredPreceptsOnly") and not rel.get("fixedIdeo"):
        r.add(r.W, "route/preceptsonly-without-fixed",
              "requiredPreceptsOnly without fixedIdeo constrains a religion you did not author")

    # -- interest metrics (counted, never scored here) ----------------------- #
    if known_precepts:
        with_comps = [n for n in known_precepts if D.f(D.precepts[n], "comps")]
        high = [n for n in known_precepts if D.f(D.precepts[n], "impact") == "High"]
        social = [n for n in known_precepts
                  if any(c.get("$type", "").startswith(("PreceptComp_KnowsMemoryThought",
                                                        "PreceptComp_SituationalThought",
                                                        "PreceptComp_GoodwillSituation",
                                                        "PreceptComp_UnwillingToDo"))
                         for c in (D.f(D.precepts[n], "comps") or []))]
        r.add(r.I, "interest/live-precepts",
              f"{len(with_comps)}/{len(known_precepts)} precepts carry comps (fire thoughts); "
              f"{len(high)} High impact; {len(social)} produce player-visible mood or refusal")
        inert = [n for n in known_precepts if n not in with_comps]
        if inert:
            r.add(r.W, "interest/inert",
                  f"{len(inert)} precept(s) with NO comps — a tooltip, not a mechanic: {inert}")
    return r


def distinctiveness(rels: list[dict], D: Dump) -> list[str]:
    """The name-blind test, made countable: pairwise Jaccard on memes+precepts."""
    out = []
    for i in range(len(rels)):
        for j in range(i + 1, len(rels)):
            a = set(rels[i].get("memes") or []) | set(rels[i].get("precepts") or [])
            b = set(rels[j].get("memes") or []) | set(rels[j].get("precepts") or [])
            if not a or not b:
                continue
            jac = len(a & b) / len(a | b)
            if jac >= 0.34:
                out.append(f"  ⚠️  {jac:.0%} shared  {rels[i].get('name')}  ~  "
                           f"{rels[j].get('name')}   ({sorted(a & b)})")
    return out


# --------------------------------------------------------------------------- #
# input parsers
# --------------------------------------------------------------------------- #
BACKTICK = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")
SECTION = re.compile(r"^##\s+(\d+)\s*[·.]\s*(.+?)\s*$", re.M)


def from_markdown(path: Path, D: Dump) -> list[dict]:
    """Best-effort extractor for the project's faction_religions_spec.md shape.

    Reads ONLY structured rows — the `| **memes** |`, `| **structure** |`,
    `| **styles** |` rows and the three-column tables under a `**Precepts` line.
    Prose mentions are deliberately ignored; a backticked defName in a paragraph
    is a citation, not a claim that the religion holds it.
    """
    text = path.read_text(encoding="utf-8")
    cuts = [(m.start(), m.group(1), m.group(2)) for m in SECTION.finditer(text)]
    rels = []
    for k, (start, num, title) in enumerate(cuts):
        end = cuts[k + 1][0] if k + 1 < len(cuts) else len(text)
        body = text[start:end]
        rel = {"name": f"{num} · {re.sub(r'[*_]', '', title)}", "target": "faction",
               "memes": [], "precepts": [], "styles": [], "deities": 0}
        in_precepts = False
        for line in body.splitlines():
            low = line.lower()
            if "**precepts" in low:
                in_precepts = True
            elif line.startswith("##") or low.startswith("**what the player"):
                in_precepts = False
            if line.startswith("|"):
                cells = [c.strip() for c in line.strip("|").split("|")]
                head = cells[0].lower().replace("*", "").strip()
                if head in ("structure", "memes") and len(cells) > 1:
                    rel["memes"] += BACKTICK.findall(cells[1])
                elif head == "styles" and len(cells) > 1:
                    rel["styles"] += BACKTICK.findall(cells[1])
                elif head == "fixedideo" and len(cells) > 1:
                    rel["fixedIdeo"] = "✅" in cells[1]
                    rel["requiredPreceptsOnly"] = "requiredPreceptsOnly` ✅" in cells[1]
                elif in_precepts and len(cells) >= 3:
                    rel["precepts"] += [n for n in BACKTICK.findall(cells[1])
                                        if n in D.precepts]
            rel["deities"] += line.count("<name>")
        rel["memes"] = [n for n in dict.fromkeys(rel["memes"]) if n in D.memes or "_" in n]
        rels.append(rel)
    return rels


# 🔴 forced/required are HELD SIMULTANEOUSLY; allowed is a MENU of alternatives.
# They must not share a bucket — merging them false-fired meme/exclusion on
# Ludeon's own Empire (MaleSupremacy + FemaleSupremacy), measured 2026-08-14.
IDEO_LIST_FIELDS = {"forcedMemes": "memes", "requiredMemes": "memes",
                    "allowedMemes": "candidateMemes", "styles": "styles"}


def from_xml(path: Path) -> list[dict]:
    rels = []
    for f in ([path] if path.is_file() else sorted(path.rglob("*.xml"))):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as e:
            print(f"  🔴 ERROR xml/parse  {f}: {e}")
            continue
        # A religion may arrive as a FactionDef, or as the <value> of a
        # PatchOperationAdd that grafts an ideo block onto someone else's
        # FactionDef — which is how every religion this project does not own
        # has to ship. Both shapes carry identical children, so treat them
        # alike. Without this the whole patch file reads as "no religions
        # found", which is a silent pass, not a failure.
        targets = list(root.iter("FactionDef"))
        for val in root.iter("value"):
            if val.find("ideoName") is not None or val.find("forcedMemes") is not None:
                targets.append(val)
        for fd in targets:
            rel = {"name": (fd.findtext("ideoName") or fd.findtext("defName")
                            or f.name) + f"  [{f.name}]",
                   "target": "faction", "memes": [], "candidateMemes": [],
                   "precepts": [], "styles": [],
                   "deities": len(fd.findall("./deityPresets/li")),
                   "fixedIdeo": (fd.findtext("fixedIdeo") or "").lower() == "true",
                   "requiredPreceptsOnly":
                       (fd.findtext("requiredPreceptsOnly") or "").lower() == "true"}
            hit = False
            for tag, bucket in IDEO_LIST_FIELDS.items():
                for li in fd.findall(f"./{tag}/li"):
                    if li.text:
                        rel[bucket].append(li.text.strip())
                        hit = True
            # a weighted pick of exactly ONE structure — a menu, not a held set
            for w in fd.findall("./structureMemeWeights/*"):
                rel["candidateMemes"].append(w.tag)
                hit = True
            rel["candidateMemes"] = [n for n in dict.fromkeys(rel["candidateMemes"])
                                     if n not in rel["memes"]]
            # raw lists for the game's own two ConfigErrors. None = tag absent,
            # which is NOT the same as an empty list and is what the game tests.
            for tag in ("allowedMemes", "disallowedMemes", "requiredMemes"):
                node = fd.find(tag)
                rel[tag] = None if node is None else [li.text.strip()
                                                      for li in node.findall("li") if li.text]
                hit = hit or node is not None
            if hit or rel["fixedIdeo"] or rel["deities"]:
                rels.append(rel)
    return rels


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--spec", type=Path, help="JSON spec file")
    src.add_argument("--md", type=Path, help="markdown design doc (faction_religions_spec shape)")
    src.add_argument("--xml", type=Path, help="FactionDef .xml file or a directory of them")
    ap.add_argument("--impact-budget", type=int, default=DEFAULT_IMPACT_BUDGET,
                    help="fail when total meme impact exceeds N (only pass a MEASURED cap)")
    ap.add_argument("--only", help="check just the religion whose name contains this")
    ap.add_argument("--mods-config", type=Path, default=None,
                    help="read activeMods from THIS ModsConfig.xml instead of the live "
                         "one. Use it whenever the live list is not the campaign list — "
                         "e.g. infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml "
                         "while a minimal list is swapped in.")
    a = ap.parse_args()

    if a.mods_config:
        if not a.mods_config.is_file():
            sys.exit(f"--mods-config: no such file {a.mods_config}")
        global MODS_CONFIG_OVERRIDE
        MODS_CONFIG_OVERRIDE = a.mods_config

    D = Dump()
    if a.spec:
        rels = json.loads(a.spec.read_text(encoding="utf-8"))["religions"]
    elif a.md:
        rels = from_markdown(a.md, D)
    else:
        rels = from_xml(a.xml)

    if a.only:
        rels = [r for r in rels if a.only.lower() in (r.get("name") or "").lower()]
    def _has_content(r):
        return bool(r.get("memes") or r.get("candidateMemes") or r.get("precepts"))

    skipped = [r["name"] for r in rels if not _has_content(r)]
    rels = [r for r in rels if _has_content(r)]
    if not rels:
        print("no religions found in the input")
        return 1

    print(f"validate_ideoligion — {len(rels)} religion(s) against the live dump ({D.stamp})")
    if skipped:
        print(f"  skipped {len(skipped)} empty section(s): {skipped}")
    print(f"  {len(D.memes)} memes · {len(D.precepts)} precepts · {len(D.styles)} styles"
          f" · {len(D.active) or '?'} active mods")

    reports = [check(r, D, a.impact_budget) for r in rels]
    for rep in reports:
        rep.print()

    dis = distinctiveness(rels, D)
    if dis:
        print("\n=== name-blind test — pairs sharing a third or more of their vocabulary")
        print("\n".join(dis))

    bad = [rep.name for rep in reports if rep.errors]
    print(f"\n{len(reports) - len(bad)}/{len(reports)} VALID.", end=" ")
    print(f"INVALID: {bad}" if bad else "No errors.")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
