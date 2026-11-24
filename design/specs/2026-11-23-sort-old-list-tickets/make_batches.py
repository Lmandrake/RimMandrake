#!/usr/bin/env python3
"""make_batches.py: measure the old tickets that wait in Shape, and split them into reader batches (run once, 2026-11-23).

    python3 design/specs/2026-11-23-sort-old-list-tickets/make_batches.py measure       the counts; writes nothing
    python3 design/specs/2026-11-23-sort-old-list-tickets/make_batches.py make          write batches.json (refuses to
                                                                                        overwrite it without --again)

The set is the one that the Maturation Pipeline page counts, by the page's own functions: an open item that is not mod
work (maturation_nonmod.classify), at stage shape (list_pipeline.stage_of), with no outcome check and no route, filed
before list_dispatch.json `shape_from`, and not named. A younger item enters Shape by itself after its grace.
"""
import collections
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (os.path.join(REPO, "src", "RimMandrake", "rimflow"), os.path.join(REPO, "src", "RimMandrake", "Utils"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

MOST = 34               # tickets in a batch. Danger: a reader's context grows past what one run can hold to the end.
MOST_CHARS = 150000     # packet characters in a batch, the same danger (about 40k tokens)

# subject word for the batch name -> pattern over the id and the title; the first that matches wins
SUBJECTS = [
    ("STEVEDESKTOP", r"\bSTEVE|\bFLEET\b"),
    ("OPS_ALARMS", r"^OPS_|\bALARM|DEADMAN|TIMER|LIVE_RESTORE|HANDOFF|LOGIN|QUOTA|ACCOUNT"),
    ("HARNESS_AND_PROOFS", r"^HARNESS|PROOF|SELFTEST|VALIDATION|MODCHECK|TESTQ|QUICKTEST|REGRESSION|NORTHSTAR|NIGHTLY"),
    ("BRIDGE_AND_GAMES", r"BRIDGE|COMPANION|ARCHBIG|ARCHSMALL|LOAD_ROUND|MODLIST|SAVEGAME|\bSAVE\b"),
    ("PIPELINE_TOOLS", r"PIPELINE|RIMFLOW|DISPATCH|DETACHED|JUDGE|LEDGER|CONDUCTOR|HELPER|PUBLISH|CLONE|\bGIT\b|TICKET"
                       r"|RELENTLESS|FOUNDRY|LANE|BRIEF|AGENT|CLAUDE|RULING|LESSON|SKILL|\bDOC|OWNER_QUEUE|RUNNER|AUDIT"),
    ("ART_AND_SPRITES", r"\bART\b|SPRITE|TEXTURE|RESKIN|REDRAW|ICON|REGEN|GRAPHIC|CANON|\bIMAGE|MASK"),
    ("PEOPLE_AND_FACTIONS", r"JAWA|UTINNI|XENO|FACTION|IDEO|RITUAL|PAWN|CREW|CLAN|TRIBE|TUSKEN|NINE\b|QUEST|RAID|TRADE"
                            r"|BAZAAR|LLM|NEMESIS|APPAREL|BACKSTOR|NAMES?\b"),
    ("SHIPS_DROIDS_AND_GUNS", r"SHIP|GRAV|DROID|MECH|SANDCRAWLER|VEHICLE|CRAWLER|REACTOR|POWER|TURRET|WEAPON|ARMOU?R|GUN"
                           r"|FORGE|WRECK|JUNK|SCRAP|SALVAG|VAULT|DUNGEON"),
    ("CREATURES", r"CREATURE|ANIMAL|BEAST|DRAGON|FLY|FLIGHT|BIRD|EGG|HERD|PREDATOR|WORM|TITAN|LEVIATHAN|FISH|LURKER"
                  r"|ROSTER|EATER|NEST|BROOD|HATCH|VERMIN|DIANOGA|RACE"),
    ("PLANTS_AND_FOOD", r"PLANT|TREE|FLORA|CROP|FOOD|CUISINE|MEAL|FUNG|MUSH|BREW|DRINK|SPICE|FRUIT|ALGA|VINE|MOSS"),
    ("WATER_AND_WEATHER", r"WATER|SEA\b|SEAS|LAKE|RIVER|PIT\b|PITS|WEATHER|SUN\b|SHADE|HEAT|STORM|WIND|CLIMATE|GEYSER"
                          r"|STEAM|FLOOD|OIL|TAR\b|LIQUID|WAVE|TIDE|ICE|SNOW|COLD"),
    ("BIOMES_AND_MAPS", r"BIOME|WORLD|MAP\b|MAPGEN|TERRAIN|LANDMARK|TILE|MINERAL|STONE|ORE|CAVE|SCAR|CATHEDRAL|LONGSHADE"
                        r"|GREENTIDE|SCALD|SUMP|ROT\b|WEBWORK|CHILL|TWILIGHT|WEEPING|CRACKED|ABYSS|WASTE|PYRE|DUNE"),
    ("MIXED_SUBJECTS", r"."),
]
WORDS = ("ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN")


def measured():
    """-> (ids oldest first, {"open_total", "shape", "old", "young", "checked"}, now)."""
    import list_dispatch as LD
    import list_pipeline as LP
    import list_shape as LS
    import maturation_nonmod as N
    import maturation_now as MN
    now = time.time()
    croot = os.path.join(REPO, "design", "concepts")
    mods = [f for f in sorted(os.listdir(croot)) if not f.startswith("_") and os.path.isdir(os.path.join(croot, f))
            and (os.path.exists(os.path.join(croot, f, "version", "VERSION.json"))
                 or MN.read_json(os.path.join(croot, f, "stage.json"))[0] is not None)]
    lf = MN.live_facts(mods)
    stores = N.read_stores(lf, mods)
    if stores["items"] is None:
        raise SystemExit("UNMEASURED: the ledger could not be read (%s)" % stores["causes"])
    sec = N.section(stores, now, spend=MN.read_spend, stage=LP.stage_of)
    frm = LS._epoch(LD.load_cfg()["shape_from"])
    c = collections.Counter(open_total=sec["open_total"])
    old = []
    for i, k in sec["stage_of"].items():
        if k != "shape":
            continue
        c["shape"] += 1
        f = LS.facts(stores["items"][i])
        if not LS.needs_shape_run(f) or f["named"]:
            c["checked_or_named"] += 1
        elif f["filed"] is not None and f["filed"] >= frm:
            c["young"] += 1
        else:
            c["old"] += 1
            old.append((f["filed"] or 0, i))
    return [i for _f, i in sorted(old)], dict(c), now


def subject(iid, title):
    t = "%s %s" % (iid, title or "")
    for name, rx in SUBJECTS[:-1]:
        if re.search(rx, iid.replace("_", " ") + " | " + iid, re.I):
            return name
    for name, rx in SUBJECTS:
        if re.search(rx, t, re.I):
            return name
    return "MIXED_SUBJECTS"


def make():
    import sort_batch_accept as S
    ids, counts, now = measured()
    world, byid = S.ledger()
    groups = collections.defaultdict(list)
    for i in ids:
        groups[subject(i, world.items[i].title)].append(i)
    out, rows = {}, []
    for name, _rx in SUBJECTS:
        g = sorted(groups.get(name, []))
        parts, cur, size = [], [], 0
        for i in g:
            n = len(S.ticket_text(i, world, byid, {}, {}))
            if cur and (len(cur) >= MOST or size + n > MOST_CHARS):
                parts.append(cur)
                cur, size = [], 0
            cur.append(i)
            size += n
        if cur:
            if parts and len(cur) < 6 and len(parts[-1]) + len(cur) <= MOST + 5:
                parts[-1] += cur
            else:
                parts.append(cur)
        for k, p in enumerate(parts):
            b = "RIMMANDRAKE_SORT_OLD_%s" % name + (
                "_PART_%s_OF_%s" % (WORDS[k], WORDS[len(parts) - 1]) if len(parts) > 1 else "_TICKETS_IN_ONE_PART")
            out[b] = {"subject": name, "tickets": p,
                      "owner_words": sorted(i for i in p if S.owner_mark(i, world, byid))}
    d = {"made": time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(now)), "counts": counts, "batches": out}
    return d


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "measure":
        ids, counts, now = measured()
        print(json.dumps(counts))
        return 0
    if cmd == "make":
        path = os.path.join(HERE, "batches.json")
        if os.path.exists(path) and "--again" not in sys.argv:
            print("REFUSED: %s exists and its batches are filed; --again overwrites it" % path)
            return 1
        d = make()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
            f.write("\n")
        for b, v in d["batches"].items():
            print("%-62s %3d tickets, %3d with owner words" % (b, len(v["tickets"]), len(v["owner_words"])))
        print(json.dumps(d["counts"]), len(d["batches"]), "batches")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
