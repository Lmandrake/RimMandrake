#!/usr/bin/env python3
"""apparel_tag_audit.py - which apparel tags the cherrypick emptied, and who that strips.

The armour half of `weapon_tag_audit.py`, and it exists because that tool has no
counterpart and the owner asked for a THOROUGH retag of "weapons and armor".

🔴 WHAT A PawnKindDef ACTUALLY ASKS FOR. `apparelTags` is a filter over the apparel
pool, exactly as `weaponTags` is over the weapon pool. Empty every tag a kind names and
the kind still spawns - it just spawns wearing whatever the generic pool and
`apparelMoney` hand it, which for a themed faction means its look quietly dissolves.

⚠️ AND THAT IS WHY THIS IS A DIFFERENT SEVERITY FROM THE WEAPON CASE, STATED PLAINLY
RATHER THAN LEFT FOR SOMEONE TO ASSUME. A kind whose weapon tags all go empty arrives
BARE-HANDED - a hard, visible, combat-relevant failure. A kind whose apparel tags all go
empty is not naked; `apparelRequired` still applies and the general pool still dresses
it. The symptom is a stormtrooper in a duster, not a stormtrooper in the nude. ⇒ Treat a
finding here as a LOOK defect, not an arming defect, and do not let it borrow the
urgency of the weapon audit.

🔴 READ THE TAGS FROM THE DEF DUMP, NOT FROM MOD XML - same ruling as the weapon audit
(owner, 2026-08-19). The dump is post-inheritance, post-PatchOperation and post-dedup; a
raw XML scan is none of those.
⚠️ Same proviso, same refusal: this REFUSES to report unless the dump's mod set matches
`ModsConfig.xml`, because a dump captured under a different list describes a different
game. `--anyway` downgrades that to a loud warning.

⚠️ THE BLIND SPOT THIS TOOL CANNOT SEE, and it is the same one BUILDABLE.md 4 records
for weapons: Cherry Picker NEUTERS rather than deletes. A cut apparel def stays in the
dump with its tags stripped, so a tag whose every carrier was cut is ABSENT from a
dump-built index rather than EMPTY in it. A counter over that index cannot return
anything but zero. ⇒ It can tell you a KIND has no surviving carrier for its tags. It
cannot tell you which cut did it. Attribute cuts from the mod's SOURCE XML.

    python3 src/RimMandrake/Utils/apparel_tag_audit.py
    python3 src/RimMandrake/Utils/apparel_tag_audit.py --verbose   # every kind
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from game_paths import DEF_DUMP, MODS_CONFIG          # noqa: E402
import xml.etree.ElementTree as ET                    # noqa: E402

DUMP = Path(DEF_DUMP)


def f(d, k, dflt=None):
    return (d.get("fields") or {}).get(k, dflt)


def load_dump():
    defs = DUMP / "defs"
    if not defs.is_dir():
        sys.exit("no def dump at %s - the game must write one before this can run" % defs)
    things = json.loads((defs / "ThingDef.json").read_text(encoding="utf-8"))["defs"]
    kinds = json.loads((defs / "PawnKindDef.json").read_text(encoding="utf-8"))["defs"]
    man = json.loads((DUMP / "manifest.json").read_text(encoding="utf-8"))
    return things, kinds, man


def check_modlist(man, anyway):
    try:
        # 🔴 `activeMods` ONLY. Iterating every <li> in the file also sweeps up
        # `knownExpansions`, which added 5 and made a MATCHING 578-mod dump report as
        # 583-vs-578 on the first run of this tool. The overcount is already recorded as
        # a known trap in this project; it caught the tool that was written to catch
        # other tools, which is the argument for the refusal existing at all.
        live = {li.text.strip().lower()
                for li in ET.parse(MODS_CONFIG).getroot().find("activeMods") if li.text}
    except Exception as e:                                   # noqa: BLE001
        print("!! cannot read ModsConfig.xml (%s) - cannot verify the dump matches" % e)
        return
    n = man.get("modCount")
    if n != len(live):
        msg = ("dump modCount %s != %d active mods in ModsConfig.xml.\n"
               "   The dump describes a DIFFERENT mod set, so every number below would "
               "be a measurement of a game you are not running.\n"
               "   Regenerate the dump under the list you intend to ship, or pass "
               "--anyway to see the numbers as PROVISIONAL." % (n, len(live)))
        if not anyway:
            sys.exit("REFUSING: " + msg)
        print("⚠️  PROVISIONAL: " + msg + "\n")
    else:
        print("dump matches the live list: %d mods, captured %s\n"
              % (n, man.get("capturedUtc", "?")))


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true",
                    help="list every kind that asks for apparel by tag, not only the failures")
    ap.add_argument("--anyway", action="store_true",
                    help="report even though the dump does not match the live mod list")
    a = ap.parse_args()

    things, kinds, man = load_dump()
    check_modlist(man, a.anyway)

    # tag -> carriers. `apparel` is a nested block on the ThingDef, not a top-level field.
    tags: dict[str, list[str]] = {}
    tagged = 0
    for t in things:
        ap_block = f(t, "apparel")
        if not isinstance(ap_block, dict):
            continue
        names = ap_block.get("tags") or []
        if names:
            tagged += 1
        for name in names:
            tags.setdefault(name, []).append(t["defName"])

    stripped = 0
    for t in things:
        ap_block = f(t, "apparel")
        if isinstance(ap_block, dict) and not (ap_block.get("tags") or []):
            stripped += 1

    print("apparel tags in the dump: %d, carried by %d apparel defs" % (len(tags), tagged))
    print("apparel defs carrying NO tag at all: %d  (many are meant to have none)\n" % stripped)

    asked, naked, thin = 0, [], []
    for k in kinds:
        want = f(k, "apparelTags") or []
        if not want:
            continue
        asked += 1
        alive = [w for w in want if tags.get(w)]
        if not alive:
            naked.append((k["defName"], want))
        elif len(alive) < len(want):
            thin.append((k["defName"], [w for w in want if w not in alive], alive))

    print("pawn kinds asking for apparel BY TAG: %d" % asked)
    print("🔴 kinds whose EVERY apparelTag has no surviving carrier: %d" % len(naked))
    for dn, want in sorted(naked):
        print("   %-34s %s" % (dn, want))
    print("\n⚠️  kinds that lost SOME tags but keep at least one: %d" % len(thin))
    if a.verbose:
        for dn, lost, alive in sorted(thin):
            print("   %-34s lost %s | keeps %s" % (dn, lost, alive))
    elif thin:
        print("   (--verbose to list them; each still dresses, just from a smaller pool)")

    print("\n🔑 A kind listed above is NOT naked. `apparelRequired` and the general pool "
          "still dress it.\n   The symptom is a faction losing its LOOK, not a pawn "
          "losing its clothes.")
    return 1 if naked else 0


if __name__ == "__main__":
    raise SystemExit(main())
