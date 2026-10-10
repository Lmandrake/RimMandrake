"""selftest_modmanifest.py - modmanifest.compare() names every way the list the game will load can differ from
the list we meant (MOD_MANIFEST_BUILD_THREE_LISTS_ONE_TRUTH). Written failing-first.

Cases: identical; Core-only reset; omitted ids; extra ids; reorder; duplicate ids in the list; case-only
differences are NOT differences (RimWorld lowercases packageIds); duplicate installed roots; loaded-vs-intended.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modmanifest as M  # noqa: E402

CORE = ["ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey"]
FULL = ["brrainz.harmony"] + CORE + ["a.one", "b.two", "mandrake.rm.flowworks", "mandrake.rm.biomes"]


def cfg(ids, d):
    p = os.path.join(d, "ModsConfig_%d.xml" % abs(hash(tuple(ids))))
    with open(p, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="utf-8"?>\n<ModsConfigData>\n  <version>1.6</version>\n'
                 '  <activeMods>\n%s  </activeMods>\n  <knownExpansions />\n</ModsConfigData>\n'
                 % "".join("    <li>%s</li>\n" % i for i in ids))
    return p


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    good = []
    d = tempfile.mkdtemp()
    man = M.manifest_from_ids("TEST", FULL, source="selftest")

    r = M.compare(man["ids"], M.read_modsconfig(cfg(FULL, d)))
    good.append(case("identical list is clean", r["clean"] and not r["problems"], r["problems"]))

    r = M.compare(man["ids"], M.read_modsconfig(cfg(CORE, d)))
    good.append(case("Core-only list -> CORE_ONLY", "CORE_ONLY" in r["kinds"], r["kinds"]))

    r = M.compare(man["ids"], M.read_modsconfig(cfg([i for i in FULL if i != "b.two"], d)))
    good.append(case("omitted id named", r["missing"] == ["b.two"] and "MISSING" in r["kinds"], r["missing"]))

    r = M.compare(man["ids"], M.read_modsconfig(cfg(FULL + ["z.extra"], d)))
    good.append(case("extra id named", r["extra"] == ["z.extra"] and "EXTRA" in r["kinds"], r["extra"]))

    swapped = list(FULL)
    swapped[-1], swapped[-2] = swapped[-2], swapped[-1]
    r = M.compare(man["ids"], M.read_modsconfig(cfg(swapped, d)))
    good.append(case("reorder detected and located", "REORDERED" in r["kinds"] and r["reordered"], r["reordered"]))

    r = M.compare(man["ids"], M.read_modsconfig(cfg(FULL + ["a.one"], d)))
    good.append(case("duplicate id in list -> DUPLICATE_ID", "DUPLICATE_ID" in r["kinds"], r["kinds"]))

    r = M.compare(man["ids"], M.read_modsconfig(cfg([i.upper() if i == "a.one" else i for i in FULL], d)))
    good.append(case("case-only difference is not a difference", r["clean"], r["problems"]))

    r = M.compare(man["ids"], M.read_modsconfig(cfg(FULL, d)), loaded=[i for i in FULL if i != "a.one"])
    good.append(case("loaded set short of intended -> NOT_LOADED", "NOT_LOADED" in r["kinds"] and
                     r["not_loaded"] == ["a.one"], r["kinds"]))

    roots = {"a.one": ["/Mods/AOne", "/workshop/123"], "b.two": ["/Mods/BTwo"]}
    dups = M.duplicate_roots(roots, ["a.one", "b.two"])
    good.append(case("duplicate installed roots found", list(dups) == ["a.one"], dups))

    good.append(case("empty or unreadable ModsConfig raises, never reads as empty-and-fine",
                     _raises(lambda: M.read_modsconfig(os.path.join(d, "nope.xml")))))

    m2 = M.manifest_from_ids("TEST", FULL, source="selftest", modsconfig_path=cfg(FULL, d))
    good.append(case("manifest carries ordered ids and the ModsConfig sha256",
                     m2["ids"] == FULL and len(m2.get("modsconfig_sha256") or "") == 64))

    gap = M.shipping_gap(FULL, {"mandrake.rm.flowworks": "src/x", "mandrake.rm.newmod": "src/y",
                                "mandrake.rm.longshade": "src/z"}, folded_ids={"mandrake.rm.longshade"})
    good.append(case("shipping gap names our mod absent from the list, skips folded members",
                     gap["absent"] == ["mandrake.rm.newmod"] and "mandrake.rm.longshade" not in gap["absent"], gap))

    print("%d/%d" % (sum(good), len(good)))
    return 0 if all(good) else 1


def _raises(fn):
    try:
        fn()
    except M.ManifestError:
        return True
    return False


if __name__ == "__main__":
    sys.exit(main())
