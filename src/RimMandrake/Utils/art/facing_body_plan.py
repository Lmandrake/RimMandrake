#!/usr/bin/env python3
"""facing_body_plan.py — which BODY PLAN is a creature, from its race's BodyDef (never from its defName).

The facing-scale lint (facing_scale_lint.py) needs a body plan because a quadruped's front view, a snake's, a fish's
and a bird's legitimately differ in height against their side view by different amounts (vanilla's measured scatter
differs per plan; see Transient/facing_lint_calibration_2026-10-16/PROGRESS.md).

THE HEURISTIC (documented, deterministic). The DefDump capture carries, for every PawnKindDef, `race` -> ThingDef
`race.body` -> BodyDef, whose part tree is the creature's anatomy. Count part defs by TOKEN (case-sensitive substrings
of the part defName, so mod prefixes such as BS_/AA_/SW_ do not matter):

    insect   (any of Insect|Elytra|Pronotum|Thorax|Abdomen|Carapace|Chitin, or >= 6 legs) AND at least one leg or wing
             (arthropods: beetles, crabs, spiders, wasps; a legless larva is a serpent)
    flyer    any Wing part (not insect), OR a 2-legged / armless / footed body with no arms (bird)
    fish     Fish|Fin|Gills token, no legs
    blob     no legs, no wings, and Tentacle|Slug|Snail|Jelly|Protoplasm|Nucleus tokens (or no Head)
    serpent  no legs, no wings, no fins, has a head (snakes, worms, larvae)
    biped    2 legs and arms (apes, monkeys, upright kangaroo-likes)
    lowslung 4+ legs ending in CLAWS rather than paws/hooves/feet (Front/RearClaw parts: lizards, crocodilians), or a
             Shell/Plastron (tortoises, turtles) — the reptile body, whose splayed legs read as feet from any camera
    quadruped  every other 3..5-legged body

An east-silhouette aspect ratio was tried for lowslung and rejected: elephants, cows and wolves reach 2.0-2.3 while
vanilla's alligator, monitor and iguana sit at 2.9-4.0 together with badgers, so no single threshold separates them.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

PLANS = ("quadruped", "lowslung", "biped", "flyer", "fish", "serpent", "insect", "blob")


def _walk(n, acc):
    if isinstance(n, dict):
        acc.append(n.get("def", ""))
        for c in n.get("parts") or []:
            _walk(c, acc)


_CACHE = {}


def dump_tables() -> dict:
    """{'body': {bodyDefName: Counter(part defs)}, 'race_body': {thingDef: bodyDef}, 'kind_race': {kind: thingDef}}"""
    if _CACHE:
        return _CACHE
    from game_paths import DEF_DUMP
    d = Path(DEF_DUMP) / "defs"
    body = {}
    for e in json.loads((d / "BodyDef.json").read_text())["defs"]:
        acc = []
        _walk(e["fields"].get("corePart"), acc)
        body[e["defName"]] = Counter(acc)
    race_body, flesh = {}, {}
    for e in json.loads((d / "ThingDef.json").read_text())["defs"]:
        r = (e.get("fields") or {}).get("race")
        if isinstance(r, dict) and isinstance(r.get("body"), str):
            race_body[e["defName"]] = r["body"]
            flesh[e["defName"]] = str(r.get("fleshType"))
    kind_race = {}
    for e in json.loads((d / "PawnKindDef.json").read_text())["defs"]:
        f = e.get("fields") or {}
        if isinstance(f.get("race"), str):
            kind_race[e["defName"]] = f["race"]
    _CACHE.update(body=body, race_body=race_body, flesh=flesh, kind_race=kind_race)
    return _CACHE


def features(parts: Counter) -> dict:
    n = lambda pat: sum(c for p, c in parts.items() if re.search(pat, p))      # noqa: E731
    return {"legs": n(r"Leg"), "arms": n(r"Arm$|Hand$"), "wings": n(r"Wing"), "fins": n(r"Fin|Flipper|Gills|Fish"),
            "insect": n(r"Insect|Elytra|Pronotum|Thorax|Abdomen|Carapace|Chitin"),
            "blobby": n(r"Tentacle|Slug|Snail|Jelly|Protoplasm|Nucleus"),
            "head": n(r"Head|Skull"), "shell": n(r"Shell|Plastron"), "foot": n(r"Foot$"),
            "claws": n(r"Claw"), "pads": n(r"Paw$|Hoof$|Foot$")}


def plan_from_features(ft: dict) -> str:
    if (ft["insect"] and not ft["blobby"] or ft["legs"] >= 6) and (ft["legs"] or ft["wings"]):
        return "insect"                                 # a LEGLESS, wingless 'insect' body is a larva: serpent below
    if ft["wings"]:
        return "flyer"
    if not ft["legs"]:
        if ft["fins"]:
            return "fish"
        if ft["blobby"] or not ft["head"]:
            return "blob"
        return "serpent"
    if ft["legs"] == 2 and not ft["arms"]:
        return "flyer"                                  # two legs, no arms, no wings parts: a bird body
    if ft["legs"] == 2 and ft["arms"]:
        return "biped"
    if ft["shell"] or (ft["legs"] >= 4 and ft["claws"] and not ft["pads"]):
        return "lowslung"
    return "quadruped"


def _xml_part_names(node, acc):
    d = node.findtext("def")
    if d:
        acc.append(d.strip())
    for li in node.findall("parts/li"):
        _xml_part_names(li, acc)


def xml_tables() -> dict:
    """The same three maps read from the repo's own Defs XML (src/**/Defs) — for kinds newer than the DefDump capture.
    ThingDef race.body is inherited through ParentName."""
    if "x" in _CACHE:
        return _CACHE["x"]
    import xml.etree.ElementTree as ET
    repo = HERE.parents[3]
    kind_race, thing, body = {}, {}, {}
    for p in (repo / "src").glob("**/Defs/**/*.xml"):
        try:
            root = ET.parse(p).getroot()
        except (ET.ParseError, OSError):
            continue
        for e in root:
            dn = (e.findtext("defName") or "").strip()
            if e.tag == "PawnKindDef" and dn and e.findtext("race"):
                kind_race[dn] = e.findtext("race").strip()
            elif e.tag == "ThingDef":
                thing[dn or e.get("Name") or ""] = e
                if e.get("Name"):
                    thing[e.get("Name")] = e
            elif e.tag == "BodyDef" and dn and e.find("corePart") is not None:
                acc = []
                _xml_part_names(e.find("corePart"), acc)
                body[dn] = Counter(acc)
    _CACHE["x"] = {"kind_race": kind_race, "thing": thing, "body": body}
    return _CACHE["x"]


def _xml_race_body(thing: dict, name: str) -> str | None:
    seen = set()
    e = thing.get(name)
    while e is not None and id(e) not in seen:
        seen.add(id(e))
        b = e.findtext("race/body")
        if b:
            return b.strip()
        e = thing.get(e.get("ParentName") or "")
    return None


def body_parts(body: str) -> Counter | None:
    return dump_tables()["body"].get(body) or xml_tables()["body"].get(body)


def body_of_kind(kind: str) -> tuple[str | None, str]:
    """(bodyDef name or None, how): the DefDump first (post-patch, every active mod), the repo XML for newer kinds."""
    t, x = dump_tables(), xml_tables()
    race = t["kind_race"].get(kind)
    if race and t["race_body"].get(race):
        return t["race_body"][race], "dump"
    race = race or x["kind_race"].get(kind)
    if not race:
        return None, "kind in neither DefDump nor repo XML"
    b = t["race_body"].get(race) or _xml_race_body(x["thing"], race)
    return (b, "repo-xml") if b else (None, f"race {race} has no body")


def plan_of_kind(kind: str) -> tuple[str, str]:
    """(plan, evidence) — plan 'UNCLASSIFIED' when the body cannot be found."""
    b, how = body_of_kind(kind)
    if b is None:
        return "UNCLASSIFIED", how
    parts = body_parts(b)
    if parts is None:
        return "UNCLASSIFIED", f"BodyDef {b} in neither DefDump nor repo XML"
    return plan_from_features(features(parts)), f"body={b} ({how})"
