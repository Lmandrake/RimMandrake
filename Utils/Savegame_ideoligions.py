#!/usr/bin/env python3
"""
Savegame_ideoligions.py  —  RimWorld 1.6 (.rws) ideoligion (religion) reader
============================================================================

PURPOSE
-------
Third companion to Savegame_mapview.py (map) and Savegame_detailed_items.py
(items). This one reads every IDEOLIGION ("religion") defined inside a save and
pulls out its full human-interesting flavor: name / adjective / member-name,
leader titles, the free-text description, its memes, deities, roles, rituals,
relics, sacred buildings/weapons, issue positions (precepts), culture and
style — plus which pawns follow it.

Ideoligions in a save are FULLY expanded (not just a def reference): a fluid
ideo carries all of its precepts inline, so the save is a self-contained,
authoritative source for the campaign's religions. This makes it a legible,
safe-to-READ node (same as scenario / pawn story text). See
../rimworld_file_lore.md §2c.

WHERE THEY LIVE  (verified against 03_Gravtasm__starting_save.rws, 1.6.4633)
--------------------------------------------------------------------------
  <game> … <ideoManager> <ideos> <li> … </li> </ideos> </ideoManager>
Each <li> is one ideoligion. Direct children seen:
  <foundation Class="IdeoFoundation_Deity">  ->  <def>, <place>, <deities>
  <name> <adjective> <memberName>            proper nouns for the faith
  <leaderTitleMale> <leaderTitleFemale>
  <description> <descriptionTemplate>        the narrative blurb
  <culture>                                  culture defName (e.g. Kriminul)
  <iconDef> <colorDef> <primaryFactionColor> visual identity
  <memes>            list of meme defNames (the ideo's structural pillars)
  <precepts>         list of <li Class="Precept_*"> (rituals, roles, relics,
                     buildings, weapons, virtues, gravship-launch, and
                     Class-less <li> = issue positions like slavery/execution)
  <thingStyleCategories> <usedSymbols> <usedSymbolPacks> <style>
  <id>                                       the ideo's load id (referenced by
                                             pawns as "Ideo_<id>")

PRECEPT CLASSES SEEN (per ideo)
-------------------------------
  Precept_Ritual, Precept_RitualSeat, Precept_RoleSingle, Precept_RoleMulti,
  Precept_Building, Precept_Relic, Precept_Weapon, Precept_GravshipLaunch,
  IdeologyVirtues.Precept_Virtue, and Class-less <li> = an "issue position"
  (e.g. body modification / slavery / execution stance). Named precepts carry a
  human <name> (e.g. role "Archic Boss", ritual "Fidelist Oblation",
  building "Fidelist Altar", relic "Deepspeaker").

PAWN MEMBERSHIP
---------------
Pawns reference their ideo by load id via an <ideo> node whose text is
"Ideo_<id>". We tally those to report each religion's follower count.

OUTPUT
------
  <stem>_ideoligions.json   full machine-readable dump of every ideo
  <stem>_ideoligions.md     readable report: one section per religion
  (console)                 short roster summary

USAGE
-----
  python3 Savegame_ideoligions.py <path-to.rws> [--out DIR] [--max-desc N]

Pure standard library (ElementTree) — no third-party dependencies.
"""

import sys
import os
import json
import argparse
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict


def text_of(el, tag):
    if el is None:
        return None
    c = el.find(tag)
    if c is None:
        return None
    t = (c.text or "").strip()
    return t if t else None


def list_text(el, tag):
    """Return the stripped text of every <li> under el/<tag>."""
    parent = el.find(tag) if el is not None else None
    if parent is None:
        return []
    out = []
    for li in parent.findall("li"):
        t = (li.text or "").strip()
        if t:
            out.append(t)
    return out


def parse_deities(foundation):
    out = []
    d = foundation.find("deities") if foundation is not None else None
    if d is None:
        return out
    for li in d.findall("li"):
        out.append({
            "name": text_of(li, "name"),
            "type": text_of(li, "type"),
            "gender": text_of(li, "gender"),
            "title": text_of(li, "title"),
        })
    return out


# precept classes that carry a meaningful proper <name>
NAMED_PRECEPT_GROUPS = [
    ("roles", ("Precept_RoleSingle", "Precept_RoleMulti", "Precept_Role")),
    ("rituals", ("Precept_Ritual",)),
    ("ritual_seats", ("Precept_RitualSeat",)),
    ("buildings", ("Precept_Building",)),
    ("relics", ("Precept_Relic",)),
    ("weapons", ("Precept_Weapon",)),
    ("gravship_launch", ("Precept_GravshipLaunch",)),
]
VIRTUE_SUFFIX = "Precept_Virtue"  # e.g. IdeologyVirtues.Precept_Virtue


def parse_precepts(ideo):
    """Group precepts into named-flavor buckets + issue positions."""
    grouped = defaultdict(list)
    issue_positions = []   # Class-less <li>: def + human name
    virtues = []
    class_counts = Counter()

    prec = ideo.find("precepts")
    if prec is None:
        return {}, [], [], class_counts

    for li in prec.findall("li"):
        cls = li.get("Class")
        class_counts[cls or "IssuePosition"] += 1
        name = text_of(li, "name")
        defn = text_of(li, "def")

        if cls is None:
            # issue position (stance): slavery, execution, body mod, etc.
            issue_positions.append({"def": defn, "name": name})
            continue
        if cls.endswith(VIRTUE_SUFFIX):
            virtues.append({"def": defn, "name": name})
            continue

        placed = False
        for bucket, classes in NAMED_PRECEPT_GROUPS:
            if cls in classes:
                rec = {"name": name, "def": defn, "class": cls}
                # roles: capture leader-ness + supreme gender restriction
                if "Role" in cls:
                    rec["usesDefiniteArticle"] = text_of(li, "usesDefiniteArticle")
                    rec["restrictToSupremeGender"] = text_of(
                        li, "restrictToSupremeGender")
                # rituals: capture the expected-desc blurb (flavor!)
                if cls == "Precept_Ritual":
                    rec["expectedDesc"] = text_of(li, "ritualExpectedDesc")
                    rec["pattern"] = text_of(li, "sourcePattern")
                grouped[bucket].append(rec)
                placed = True
                break
        if not placed:
            grouped["other"].append({"name": name, "def": defn, "class": cls})

    return grouped, issue_positions, virtues, class_counts


def main():
    ap = argparse.ArgumentParser(
        description="RimWorld .rws ideoligion (religion) reader")
    ap.add_argument("save", help="path to .rws savegame")
    ap.add_argument("--out", default=None, help="output directory")
    ap.add_argument("--max-desc", type=int, default=1200,
                    help="truncate each description in the MD report to N chars "
                         "(JSON keeps full text)")
    args = ap.parse_args()

    if not os.path.isfile(args.save):
        sys.exit("No such file: %s" % args.save)

    stem = os.path.splitext(os.path.basename(args.save))[0]
    out_dir = args.out or os.path.dirname(os.path.abspath(args.save))
    os.makedirs(out_dir, exist_ok=True)

    print("Parsing %s ..." % args.save)
    tree = ET.parse(args.save)
    root = tree.getroot()

    ideos_parent = root.find(".//ideoManager/ideos")
    if ideos_parent is None:
        sys.exit("No <ideoManager><ideos> block found — is Ideology active in "
                 "this save?")

    # --- follower tally: pawns reference their faith as <ideo>Ideo_<id></ideo>
    follower_counts = Counter()
    for el in root.iter("ideo"):
        t = (el.text or "").strip()
        if t.startswith("Ideo_"):
            follower_counts[t[len("Ideo_"):]] += 1

    religions = []
    for io in ideos_parent.findall("li"):
        idv = text_of(io, "id")
        foundation = io.find("foundation")
        grouped, issues, virtues, class_counts = parse_precepts(io)
        rec = {
            "id": idv,
            "name": text_of(io, "name"),
            "adjective": text_of(io, "adjective"),
            "memberName": text_of(io, "memberName"),
            "leaderTitleMale": text_of(io, "leaderTitleMale"),
            "leaderTitleFemale": text_of(io, "leaderTitleFemale"),
            "culture": text_of(io, "culture"),
            "iconDef": text_of(io, "iconDef"),
            "colorDef": text_of(io, "colorDef"),
            "foundationClass": foundation.get("Class") if foundation is not None
            else None,
            "foundationDef": text_of(foundation, "def"),
            "sacredPlace": text_of(foundation, "place"),
            "description": text_of(io, "description"),
            "memes": list_text(io, "memes"),
            "deities": parse_deities(foundation),
            "precepts": grouped,
            "issuePositions": issues,
            "virtues": virtues,
            "preceptClassCounts": dict(class_counts),
            "followers": follower_counts.get(idv, 0),
        }
        religions.append(rec)

    # sort by follower count desc, then name
    religions.sort(key=lambda r: (-r["followers"], r.get("name") or ""))

    # ---- JSON ----
    report = {
        "save": os.path.basename(args.save),
        "totals": {
            "ideoligions": len(religions),
            "total_pawn_ideo_refs": sum(follower_counts.values()),
        },
        "religions": religions,
    }
    json_path = os.path.join(out_dir, "%s_ideoligions.json" % stem)
    with open(json_path, "w") as fh:
        json.dump(report, fh, indent=2)

    # ---- Markdown ----
    md = []
    md.append("# Ideoligion (religion) report — `%s`\n"
              % os.path.basename(args.save))
    md.append("Generated by `Utils/Savegame_ideoligions.py`.\n")
    md.append("## Summary\n")
    md.append("- **Ideoligions defined:** %d" % len(religions))
    md.append("- **Sorted by follower count** (pawns whose `<ideo>` points at "
              "each faith).\n")
    md.append("| Religion | Members called | Culture | Memes | Followers |")
    md.append("|---|---|---|---|---|")
    for r in religions:
        md.append("| **%s** | %s | %s | %s | %d |" % (
            r["name"] or "—", r["memberName"] or "—", r["culture"] or "—",
            ", ".join(r["memes"]) if r["memes"] else "—", r["followers"]))
    md.append("")

    for r in religions:
        md.append("---\n")
        md.append("## %s" % (r["name"] or "(unnamed)"))
        idline = []
        if r["adjective"]:
            idline.append("adjective *%s*" % r["adjective"])
        if r["memberName"]:
            idline.append("a member is a *%s*" % r["memberName"])
        if r["followers"]:
            idline.append("**%d follower(s)**" % r["followers"])
        if idline:
            md.append("*" + "; ".join(idline) + ".*\n")

        # identity block
        md.append("- **Leader title:** %s / %s" % (
            r["leaderTitleMale"] or "—", r["leaderTitleFemale"] or "—"))
        md.append("- **Culture:** %s  ·  **Foundation:** %s (`%s`)" % (
            r["culture"] or "—", r["foundationDef"] or "—",
            r["foundationClass"] or "—"))
        if r["sacredPlace"]:
            md.append("- **Sacred place:** %s" % r["sacredPlace"])
        if r["memes"]:
            md.append("- **Memes:** %s" % ", ".join("`%s`" % m
                                                    for m in r["memes"]))
        if r["iconDef"] or r["colorDef"]:
            md.append("- **Symbol:** icon `%s`, color `%s`" % (
                r["iconDef"] or "—", r["colorDef"] or "—"))

        # deities
        if r["deities"]:
            md.append("\n**Deities**\n")
            for d in r["deities"]:
                bits = [d.get("name") or "?"]
                if d.get("type"):
                    bits.append("— %s" % d["type"])
                if d.get("gender"):
                    bits.append("(%s)" % d["gender"])
                md.append("- " + " ".join(bits))

        # description
        if r["description"]:
            desc = r["description"]
            if len(desc) > args.max_desc:
                desc = desc[:args.max_desc] + " …[truncated]"
            md.append("\n**Description**\n")
            md.append("> " + desc.replace("\n", "\n> "))

        # roles
        roles = r["precepts"].get("roles", [])
        if roles:
            md.append("\n**Roles**\n")
            for rl in roles:
                sup = ""
                if rl.get("restrictToSupremeGender") == "True":
                    sup = " (supreme-gender only)"
                md.append("- **%s** — `%s`%s" % (
                    rl.get("name") or "?", rl.get("def") or "?", sup))

        # rituals (with flavor blurb)
        rituals = r["precepts"].get("rituals", [])
        if rituals:
            md.append("\n**Rituals** (%d)\n" % len(rituals))
            for rt in rituals:
                line = "- **%s** — `%s`" % (rt.get("name") or "?",
                                            rt.get("def") or "?")
                md.append(line)
                if rt.get("expectedDesc"):
                    ed = rt["expectedDesc"]
                    if len(ed) > 220:
                        ed = ed[:220] + " …"
                    md.append("  > " + ed.replace("\n", " "))

        # sacred buildings / relics / weapons / seats
        for bucket, label in (("buildings", "Sacred buildings"),
                              ("relics", "Relics"),
                              ("weapons", "Sacred/venerated weapon precepts"),
                              ("ritual_seats", "Ritual seats"),
                              ("gravship_launch", "Gravship-launch rites")):
            items = r["precepts"].get(bucket, [])
            if items:
                names = [it.get("name") or it.get("def") for it in items]
                md.append("\n**%s:** %s" % (label, ", ".join(
                    "%s" % n for n in names if n)))

        # virtues
        if r["virtues"]:
            vv = [v.get("def") or v.get("name") for v in r["virtues"]]
            md.append("\n**Virtues:** %s" % ", ".join("`%s`" % v
                                                      for v in vv if v))

        # issue positions
        if r["issuePositions"]:
            md.append("\n**Issue positions** (%d)\n"
                      % len(r["issuePositions"]))
            for ip in r["issuePositions"]:
                md.append("- %s → `%s`" % (
                    ip.get("name") or "?", ip.get("def") or "?"))
        md.append("")

    md_path = os.path.join(out_dir, "%s_ideoligions.md" % stem)
    with open(md_path, "w") as fh:
        fh.write("\n".join(md))

    # ---- console ----
    print("\nIdeoligions: %d" % len(religions))
    print("%-32s %-10s %-14s %s" % ("RELIGION", "FOLLOWERS", "CULTURE",
                                     "MEMES"))
    for r in religions:
        print("%-32s %-10d %-14s %s" % (
            (r["name"] or "—")[:32], r["followers"],
            (r["culture"] or "—")[:14],
            ", ".join(r["memes"])))
    print("\nReport MD:   %s" % md_path)
    print("Report JSON: %s" % json_path)


if __name__ == "__main__":
    main()
