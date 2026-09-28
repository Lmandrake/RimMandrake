#!/usr/bin/env python3
"""
biomes_compose_sweeps.py — the §4 collision sweeps for 'RimMandrake: Baroque
Biomes' (design/RimMandrake/biome_mod_unification_spec.md §4), re-run before
every load-prove of a compose wave (BAROQUE_BIOMES_COMPOSE_1).

    python3 src/RimMandrake/Utils/biomes_compose_sweeps.py            # the manifest's current compose_wave
    python3 src/RimMandrake/Utils/biomes_compose_sweeps.py --all      # every manifest entry (wave-2 preview)

Python on purpose: zsh does not word-split `for x in $NAMES`, so a shell loop
over mod names runs ONCE on the whole string and reports a confident zero
(CLAUDE.md). Every sweep prints a SANITY PROBE — something it must find if it
can see at all — beside its result; a sweep whose probe fails exits 2 and its
"clean" result means nothing.

Exit: 0 all clean · 1 a finding · 2 a probe failed (a sweep could not see).
"""
import argparse
import collections
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
TIER = os.path.join(SRC, "RimMandrake")
sys.path.insert(0, HERE)
import biomes_compose as BC                 # noqa: E402
import deploy_custom_mods as D              # noqa: E402

findings = 0
probe_fail = 0


def report(title, rows, probe_ok, probe_text):
    global findings, probe_fail
    print("\n== %s" % title)
    print("   probe: %s -> %s" % (probe_text, "OK" if probe_ok else "FAILED (sweep is blind)"))
    if not probe_ok:
        probe_fail += 1
    if rows:
        findings += 1
        print("   %d FINDING(S):" % len(rows))
        for r in rows:
            print("     " + r)
    else:
        print("   clean (0)")


def xml_files(root, sub=None):
    base = os.path.join(root, sub) if sub else root
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d not in D.EXCLUDE_DIRS]
        for fn in fns:
            if fn.lower().endswith(".xml"):
                yield os.path.join(dp, fn)


def parse(p):
    try:
        return ET.parse(p).getroot()
    except ET.ParseError:
        return None


def all_mod_roots():
    """every mod folder under every src tier (About/About.xml present), folded or not"""
    out = {}
    for tier in D.SRC_TIERS:
        d = os.path.join(SRC, tier)
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            p = os.path.join(d, n)
            if os.path.isfile(os.path.join(p, "About", "About.xml")):
                out["%s/%s" % (tier, n)] = p
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="sweep every manifest entry, not just the current compose wave")
    a = ap.parse_args()
    m = BC.load_manifest(SRC)
    entries = m["entries"] if a.all else BC.composed_entries(m)
    scope = {e["key"]: os.path.join(TIER, e["source"]) for e in entries}
    pids, names = {}, {}
    for k, d in scope.items():
        r = ET.parse(os.path.join(d, "About", "About.xml")).getroot()
        pids[k] = (r.findtext("packageId") or "").strip().lower()
        names[k] = (r.findtext("name") or "").strip()
    print("scope: %d entr%s (%s) — %s"
          % (len(scope), "y" if len(scope) == 1 else "ies",
             "all manifest entries" if a.all else "compose_wave %s" % m.get("compose_wave"),
             ", ".join(scope)))
    everyone = all_mod_roots()
    in_scope_dirs = {os.path.normpath(d) for d in scope.values()}
    outside = {k: d for k, d in everyone.items() if os.path.normpath(d) not in in_scope_dirs}

    # ---- 0. relative-path shadowing (the compose verb also refuses on this)
    owners = collections.defaultdict(list)
    for k, d in scope.items():
        for rel in D.tree(d):
            if rel.split(os.sep)[0] == "About" or os.sep not in rel:
                continue
            owners[rel.replace(os.sep, "/")].append(k)
    rows = ["%s <- %s" % (r, ks) for r, ks in sorted(owners.items()) if len(ks) > 1]
    report("0. relative-path shadowing across load roots (DirectXmlLoader TryAdd)",
           rows, len(owners) > 50, "%d content paths collected (need >50)" % len(owners))

    # ---- 1. defName + abstract Name, in-scope vs in-scope AND vs every other src mod
    def collect(dirs):
        dn, ab = collections.defaultdict(set), collections.defaultdict(set)
        biome = collections.defaultdict(set)
        for k, d in dirs.items():
            for p in xml_files(d, "Defs"):
                r = parse(p)
                if r is None:
                    continue
                for el in r:
                    if not isinstance(el.tag, str):
                        continue
                    if el.get("Name"):
                        ab[el.get("Name")].add(k)
                    n = (el.findtext("defName") or "").strip()
                    if n and (el.get("Abstract") or "").lower() != "true":
                        dn[(el.tag, n)].add(k)
                        if el.tag == "BiomeDef":
                            biome[k].add(n)
        return dn, ab, biome
    dn_in, ab_in, biome_in = collect(scope)
    dn_out, ab_out, _ = collect(outside)
    rows = []
    for key, ks in sorted(dn_in.items()):
        if len(ks) > 1:
            rows.append("defName %s/%s in %s" % (key[0], key[1], sorted(ks)))
        if key in dn_out:
            rows.append("defName %s/%s in %s AND outside: %s" % (key[0], key[1], sorted(ks), sorted(dn_out[key])))
    for n, ks in sorted(ab_in.items()):
        if len(ks) > 1:
            rows.append("abstract Name=%s in %s" % (n, sorted(ks)))
        if n in ab_out:
            rows.append("abstract Name=%s in %s AND outside: %s" % (n, sorted(ks), sorted(ab_out[n])))
    biomes = [e["key"] for e in entries if e.get("group") == "biome"]
    no_biome = [k for k in biomes if not biome_in.get(k)]
    report("1. defName + abstract Name= (in-scope, and in-scope vs %d other src mods)" % len(outside),
           rows, not no_biome and len(dn_in) > 100,
           "%d concrete defs, %d abstracts in scope; every biome entry ships a BiomeDef%s"
           % (len(dn_in), len(ab_in), "" if not no_biome else " — MISSING for %s" % no_biome))
    print("   BiomeDefs per entry: " + "; ".join("%s=%s" % (k, ",".join(sorted(v))) for k, v in sorted(biome_in.items())))

    # ---- 2. texPath values: the binding key. A shared VALUE is fine (two defs
    # may use one texture); a value that resolves to a file SHIPPED by more
    # than one in-scope entry is the collision (sweep 0 covers files, this
    # confirms it on the binding key and shows which of our files are bound).
    tex_files = collections.defaultdict(set)
    for k, d in scope.items():
        t = os.path.join(d, "Textures")
        for dp, _, fns in os.walk(t):
            for fn in fns:
                rel = os.path.relpath(os.path.join(dp, fn), t).replace(os.sep, "/")
                stem = re.sub(r"(_(north|south|east|west)m?|_m)?\.(png|psd|dds|jpg)$", "", rel, flags=re.I)
                tex_files[stem].add(k)
                tex_files[os.path.dirname(rel)].add(k)     # folder texPaths (Graphic_Random)
    vals = collections.defaultdict(set)
    for k, d in scope.items():
        for p in xml_files(d, "Defs"):
            r = parse(p)
            if r is None:
                continue
            for el in r.iter():
                if el.tag in ("texPath", "texture", "texPathFemale") and (el.text or "").strip():
                    vals[el.text.strip()].add(k)
    bound = {v: ks for v, ks in vals.items() if v in tex_files}
    rows = ["texPath %s used by %s, file shipped by %s" % (v, sorted(ks), sorted(tex_files[v]))
            for v, ks in sorted(bound.items()) if len(tex_files[v]) > 1]
    report("2. texPath binding key", rows, len(bound) > 0,
           "%d texPath values collected, %d bind to a texture an in-scope entry ships (need >0)"
           % (len(vals), len(bound)))

    # ---- 3. PatchOperationFindMod naming a folded mod's NAME, anywhere in src/
    findmod, rows = [], []
    for k, d in everyone.items():
        for p in xml_files(d):
            r = parse(p)
            if r is None:
                continue
            for el in r.iter():
                cls = el.get("Class") or ""
                if cls.endswith("PatchOperationFindMod"):
                    for li in el.findall("mods/li"):
                        v = (li.text or "").strip()
                        findmod.append(v)
                        hit = [kk for kk, nm in names.items() if nm.lower() == v.lower()]
                        if hit:
                            rows.append("%s names folded mod '%s' (%s)" % (os.path.relpath(p, SRC), v, hit[0]))
    report("3. PatchOperationFindMod naming a folded mod (goes dark after the merge)", rows,
           len(findmod) > 0, "%d FindMod <li> values read across %d src mods (need >0); e.g. %s"
           % (len(findmod), len(everyone), sorted(set(findmod))[:3]))

    # ---- 4. MayRequire / MayRequireAnyOf naming a folded packageId, anywhere in src/
    folded_ids = set(pids.values())
    seen_mr, rows = collections.Counter(), []
    rx = re.compile(r'MayRequire(?:AnyOf)?\s*=\s*"([^"]+)"', re.I)
    for k, d in everyone.items():
        for p in xml_files(d):
            try:
                txt = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for mm in rx.finditer(txt):
                for pid in (x.strip().lower() for x in mm.group(1).split(",")):
                    seen_mr[pid] += 1
                    if pid in folded_ids:
                        line = txt.count("\n", 0, mm.start()) + 1
                        rows.append("%s:%d MayRequire=%s" % (os.path.relpath(p, SRC), line, pid))
    report("4. MayRequire naming a folded packageId (dies when that id leaves the list)", rows,
           sum(seen_mr.values()) > 0,
           "%d MayRequire ids read; most common %s" % (sum(seen_mr.values()), seen_mr.most_common(2)))

    # ---- 5. C# reading its own mod identity / another folded mod's activity
    rx_self = re.compile(r"(Content\s*\.\s*(Name|PackageId|PackageIdPlayerFacing|RootDir|FolderName))"
                         r"|(\bmodContentPack\s*\.\s*(Name|PackageId|RootDir|FolderName))"
                         r"|packageIdPlayerFacing")
    rx_ids = re.compile(r'"(mandrake\.[a-z]+\.[a-z0-9_.]+)"', re.I)
    rows, cs_n, mod_classes = [], 0, collections.defaultdict(list)
    for k, d in everyone.items():
        src = os.path.join(d, "Source")
        for dp, dns, fns in os.walk(src):
            dns[:] = [x for x in dns if x not in ("obj", "bin")]
            for fn in fns:
                if not fn.endswith(".cs"):
                    continue
                p = os.path.join(dp, fn)
                txt = open(p, encoding="utf-8", errors="replace").read()
                cs_n += 1
                insc = os.path.normpath(d) in in_scope_dirs
                for i, line in enumerate(txt.splitlines(), 1):
                    s = line.strip()
                    if s.startswith("//"):
                        continue
                    if insc and rx_self.search(line):
                        rows.append("%s:%d self-identity read: %s" % (os.path.relpath(p, SRC), i, s[:110]))
                    for mm in rx_ids.finditer(line):
                        # a Harmony instance ID is only a label; it never tests identity
                        if re.search(r"new\s+Harmony\s*\(", line):
                            continue
                        if mm.group(1).lower() in folded_ids:
                            rows.append("%s:%d names folded id %s: %s" % (os.path.relpath(p, SRC), i, mm.group(1), s[:100]))
                if insc:
                    for mm in re.finditer(r"class\s+(\w+)\s*:\s*(Mod|ModSettings)\b", txt):
                        mod_classes[mm.group(1)].append(k)
    report("5. C# self-identity (Content.Name/PackageId/RootDir...) in scope; folded ids named anywhere",
           rows, cs_n > 50, "%d .cs files read across src mods (need >50)" % cs_n)

    # ---- 6. Keyed language keys, in-scope vs in-scope and vs every other src mod
    def keyed(dirs):
        out = collections.defaultdict(set)
        for k, d in dirs.items():
            lang = os.path.join(d, "Languages")
            for p in xml_files(lang) if os.path.isdir(lang) else []:
                if os.sep + "Keyed" + os.sep not in p:
                    continue
                r = parse(p)
                if r is None:
                    continue
                parts = os.path.relpath(p, lang).split(os.sep)
                for el in r:
                    if isinstance(el.tag, str):
                        out[(parts[0], el.tag)].add(k)
        return out
    kin, kout = keyed(scope), keyed(outside)
    rows = []
    for key, ks in sorted(kin.items()):
        if len(ks) > 1:
            rows.append("Keyed %s/%s in %s" % (key[0], key[1], sorted(ks)))
        if key in kout:
            rows.append("Keyed %s/%s in %s AND outside: %s" % (key[0], key[1], sorted(ks), sorted(kout[key])))
    report("6. Keyed language keys", rows, len(kin) + len(kout) > 0,
           "%d in-scope keys, %d outside (need >0 total)" % (len(kin), len(kout)))

    # ---- 7. Mod / ModSettings class names unique in scope (+ the shell's)
    shell = os.path.join(TIER, m["shell"]["source"], "Source")
    for dp, _, fns in os.walk(shell):
        for fn in fns:
            if fn.endswith(".cs"):
                t = open(os.path.join(dp, fn), encoding="utf-8").read()
                for mm in re.finditer(r"class\s+(\w+)\s*:\s*(Mod|ModSettings)\b", t):
                    mod_classes[mm.group(1)].append("(shell)")
    rows = ["class %s in %s" % (c, ks) for c, ks in sorted(mod_classes.items()) if len(ks) > 1]
    report("7. Mod/ModSettings class names", rows, "RM_BiomesMod" in mod_classes,
           "%d Mod/ModSettings classes read; shell's RM_BiomesMod among them" % len(mod_classes))
    print("   Mod subclasses in scope: %s" % ", ".join(sorted(mod_classes)))

    # ---- 8. a composed entry's Patches naming another composed entry's defNames
    # (their relative order then becomes load-bearing — spec §2 Patches note)
    owner_of = {}
    for (tag, n), ks in dn_in.items():
        for k in ks:
            owner_of[n] = k
    rows, xp_n = [], 0
    rx_dn = re.compile(r"defName\s*=\s*[\"']([^\"']+)[\"']")
    for k, d in scope.items():
        for p in xml_files(d, "Patches"):
            r = parse(p)
            if r is None:
                continue
            for el in r.iter("xpath"):
                xp_n += 1
                for mm in rx_dn.finditer(el.text or ""):
                    o = owner_of.get(mm.group(1))
                    if o and o != k:
                        rows.append("%s patches %s's %s (%s)" % (k, o, mm.group(1), os.path.relpath(p, SRC)))
    report("8. cross-entry patch targets (order becomes load-bearing)", rows, xp_n > 0,
           "%d xpaths read in scope (need >0)" % xp_n)

    print("\nSUMMARY: %d sweep(s) with findings, %d probe failure(s)" % (findings, probe_fail))
    return 2 if probe_fail else (1 if findings else 0)


if __name__ == "__main__":
    sys.exit(main())
