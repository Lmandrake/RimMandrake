#!/usr/bin/env python3
"""L1 batch manifest generator.

Reads `rimflow next --acceptance --seat FOUNDRY`, takes every L1 criterion, and maps it to the
"DefType/DefName" strings jawa/get_defs should resolve (get_defs takes `defs` as a STRING, never a
list). Names come from the criterion text (confidence NAMED) and, failing that, from the item prose
(confidence PROSE). Each name is cross-checked offline against src/ XML parsed as elements.

Usage: python3 src/RimMandrake/Utils/l1_batch_manifest.py [--json out.json] [--report out.md]
Parse failures are reported UNMEASURED, never as zero.
"""
import json, re, subprocess, sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from l1_manifest_overrides import OVERRIDES  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
ITEMS = ROOT / "infrastructure/state/items"
CRIT = re.compile(r"^\s+(\w+)\s+(L1)\s+(.*)$")
ITEM = re.compile(r"^([A-Z][A-Z0-9_]+_\d+)\s+\[")
TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_]{4,}")
OUR = re.compile(r"^(RM|RSW|RUT)_")
LIVE_HINTS = [("tool list", r"tool list|appear in the live|tools? (appear|answer)"),
              ("log", r"Player\.log|log shows|log is clean"),
              ("settings", r"Mod Settings|LassoSpawn"),
              ("state-read", r"state-read|debug_action_yielders|spawn_pawn|projectile_damage|shader|flora_spawns|checks? pass|cherrypicker")]


PATCH_ADDED = {}  # defName -> [(tag, file)] for defs that only exist inside a PatchOperation <value> (XML patches)


def build_index():
    idx, failed, nfiles = {}, [], 0
    for p in ROOT.joinpath("src").rglob("*.xml"):
        nfiles += 1
        try:
            root = ET.parse(p).getroot()
        except Exception as e:  # UNMEASURED, not zero
            failed.append((str(p.relative_to(ROOT)), str(e)[:80]))
            continue
        if root.tag == "Patch":
            # Defs created by a patch (PatchOperationAdd of a whole def under <value>) never reach the Defs index above.
            for val in root.iter("value"):
                for el in val:
                    dn = el.find("defName")
                    if dn is not None and dn.text:
                        PATCH_ADDED.setdefault(dn.text.strip(), []).append((el.tag, str(p.relative_to(ROOT))))
            continue
        if root.tag != "Defs":
            continue
        for el in root:
            dn = el.find("defName")
            if dn is not None and dn.text:
                idx.setdefault(dn.text.strip(), []).append((el.tag, str(p.relative_to(ROOT))))
    return idx, failed, nfiles


def _short(tag):
    return tag.rsplit(".", 1)[-1]


def _defs_in_file(path, child=None):
    out = []
    for el in ET.parse(ROOT / path).getroot():
        dn = el.find("defName")
        if dn is not None and dn.text and (child is None or el.find(child) is not None):
            out.append(f"{el.tag}/{dn.text.strip()}")
    return out


def _patch_targets(path):
    rx = re.compile(r'/?Defs/([\w.]+)\[defName="([^"]+)"\]')
    seen, out = set(), []
    for el in ET.parse(ROOT / path).getroot().iter("xpath"):
        for t, n in rx.findall(el.text or ""):
            if (t, n) not in seen:
                seen.add((t, n))
                out.append(f"{t}/{n}")
    return out


def _wild_from_patches(biome):
    """Animals a patch adds to <biome>'s wildAnimals (the real cast of an RM_ twin lives in patches)."""
    rx = re.compile(r'BiomeDef\[defName="%s"\]' % re.escape(biome))
    names = set()
    for p in ROOT.joinpath("src").rglob("*.xml"):
        try:
            root = ET.parse(p).getroot()
        except Exception:
            continue
        if root.tag != "Patch":
            continue
        for op in root.iter():
            xp = op.find("xpath")
            val = op.find("value")
            if xp is None or val is None or not rx.search(xp.text or "") or "wildAnimals" not in (xp.text or ""):
                continue
            for e in val.iter():
                if e is not val and len(e) == 0 and (e.text or "").strip().replace(".", "", 1).isdigit():
                    names.add(e.tag)
    return names


def derive_sea(idx, aliases=None):
    """Four sea BiomeDefs -> BiomeDef + every catch + every living body; flags a catch with no living body."""
    defs, problems = [], []
    seas = ["RM_GreySea", "RM_TwilightSea", "RM_TheScald", "RM_TheChill"]
    found = {}
    for p in ROOT.joinpath("src").rglob("*.xml"):
        try:
            root = ET.parse(p).getroot()
        except Exception:
            continue
        if root.tag != "Defs":
            continue
        for e in root:
            if e.tag == "BiomeDef" and e.findtext("defName") in seas:
                found[e.findtext("defName")] = e
    for b in seas:
        e = found.get(b)
        if e is None:
            problems.append(f"{b}: BiomeDef not found in src/")
            continue
        defs.append(f"BiomeDef/{b}")
        catches = []
        ft = e.find("fishTypes")
        if ft is not None:
            for grp in ft:
                if len(grp):
                    catches += [c.tag for c in grp]
        inline = [c.tag for c in (e.find("wildAnimals") if e.find("wildAnimals") is not None else [])]
        patched = _wild_from_patches(b)
        wild = set(inline) | patched
        for c in catches:
            defs.append(f"ThingDef/{c}")
            body = (aliases or {}).get(c) or (c[:-5] if c.endswith("Catch") else c)
            if body not in wild:
                problems.append(f"{b}: catch {c} has no living body {body} in wildAnimals (inline {len(inline)}, patch-added {len(patched)})")
        for w in sorted(wild):
            if w in idx:
                defs.append(f"PawnKindDef/{w}" if any(t == "PawnKindDef" for t, _ in idx[w]) else f"{idx[w][0][0]}/{w}")
    return defs, problems


def resolve_override(spec, idx):
    """-> (verified[], external[], missing[], ambiguous[], extra_problems[])"""
    want, external, problems = [], [f for f in spec.get("external", [])], []
    want += spec.get("defs", [])
    for f in spec.get("files", []):
        want += _defs_in_file(f, spec.get("child"))
    for d in spec.get("dirs", []):
        for fp in sorted(ROOT.joinpath(d).rglob("*.xml")):
            try:
                want += _defs_in_file(str(fp.relative_to(ROOT)), spec.get("child"))
            except ET.ParseError:
                problems.append(f"parse failure {fp.relative_to(ROOT)} (UNMEASURED)")
    if spec.get("patch_targets"):
        want += _patch_targets(spec["patch_targets"])
    if spec.get("derive") == "sea":
        d, pr = derive_sea(idx, spec.get("body_aliases"))
        want += d
        problems += pr
    verified, missing, ambiguous, seen = [], [], [], set()
    for w in want:
        t, _, n = w.rpartition("/") if "/" in w else ("", "", w)
        key = (t, n)
        if key in seen:
            continue
        seen.add(key)
        rows = idx.get(n) or PATCH_ADDED.get(n)
        origin = "" if idx.get(n) else " (patch-added)"
        if not rows:
            # a patch target that is simply not ours (vanilla / DLC / donor): external, never "verified"
            if spec.get("patch_targets") and w in _patch_targets(spec["patch_targets"]):
                external.append(w)
            else:
                missing.append(w)
            continue
        types = sorted({tg for tg, _ in rows})
        if not t:
            if len(types) > 1:
                ambiguous.append(f"{n} {types}")
                continue
            verified.append(f"{types[0]}/{n}{origin}")
        elif any(tg == t or _short(tg) == _short(t) for tg in types):
            verified.append(f"{t}/{n}{origin}")
        else:
            missing.append(f"{w} (src/ has {n} only as {types})")
    return verified, sorted(set(external)), missing, ambiguous, problems


def acceptance():
    out = subprocess.run([sys.executable, str(ROOT / "src/RimMandrake/rimflow/cli.py"), "next",
                          "--acceptance", "--seat", "FOUNDRY"], capture_output=True, text=True, cwd=ROOT).stdout
    cur, rows, sec = None, [], None
    for line in out.splitlines():
        if line.startswith("## "):
            sec = line.split()[1]
            continue
        if sec != "L1":
            continue
        m = ITEM.match(line)
        if m:
            cur = m.group(1)
            continue
        m = CRIT.match(line)
        if m and cur:
            rows.append((cur, m.group(1), m.group(3).strip()))
    return rows


def main():
    idx, failed, nfiles = build_index()
    rows = acceptance()
    prose_cache, manifest = {}, []
    for item, cid, text in rows:
        if item not in prose_cache:
            f = ITEMS / f"{item}.md"
            prose_cache[item] = f.read_text(errors="replace") if f.exists() else None
        prose = prose_cache[item]
        spec = OVERRIDES.get((item, cid))
        if spec is not None:
            ver, ext, miss, amb, prob = resolve_override(spec, idx)
            if spec.get("no_defs"):
                status = "NO_DEFS_AUTHORED"
            elif miss or amb or prob:
                status = "OVERRIDE_DEFECT_OR_AMBIGUOUS"
            elif ext:
                status = "OVERRIDE_VERIFIED_PLUS_EXTERNAL"
            else:
                status = "OVERRIDE_VERIFIED"
            manifest.append(dict(item=item, criterion=cid, text=text, status=status, source="OVERRIDE",
                                 defs=ver, external=ext, missing=miss, ambiguous=amb, problems=prob,
                                 note=spec.get("note", ""), defect=spec.get("defect", ""), live_kind=[], multi_type=[]))
            continue
        named = sorted({t for t in TOKEN.findall(text) if t in idx})
        missing = sorted({t for t in TOKEN.findall(text) if OUR.match(t) and t not in idx})
        src, names = "NAMED", named
        if not named and prose:
            names = sorted({t for t in TOKEN.findall(prose) if t in idx and OUR.match(t)})[:40]
            src = "PROSE" if names else "NONE"
        elif not prose and not named:
            src = "NONE"
        defs = [f"{idx[n][0][0]}/{n}" for n in names]
        live = [h for h, rx in LIVE_HINTS if re.search(rx, text, re.I)]
        is_defs = bool(re.search(r"resolve|get_defs|defs?\b", text, re.I)) and not live
        if is_defs and defs and not missing:
            status = "OFFLINE_PRESENT" if src == "NAMED" else "OFFLINE_PRESENT_PROSE_DERIVED"
        elif is_defs and (missing or not defs):
            status = "DEFS_UNRESOLVED_OFFLINE" if missing else "DEFS_NO_NAMES_FOUND"
        else:
            status = "NEEDS_LIVE"
        manifest.append(dict(item=item, criterion=cid, text=text, status=status, source=src,
                             defs=defs, missing=missing, live_kind=live,
                             multi_type=[n for n in names if len({t for t, _ in idx[n]}) > 1]))
    # sanity probe
    probe = next((n for n in idx if n.startswith("RM_")), None)
    probe_ok = probe in idx and "RM_ZZZ_NOT_A_DEF" not in idx and len(idx) > 500
    args = sys.argv[1:]
    jp = args[args.index("--json") + 1] if "--json" in args else "Transient/l1_manifest.json"
    rp = args[args.index("--report") + 1] if "--report" in args else "Transient/l1_manifest_report.md"
    (ROOT / jp).write_text(json.dumps(manifest, indent=1))
    from collections import Counter
    c = Counter(m["status"] for m in manifest)
    L = ["# L1 manifest report", "",
         f"Criteria: {len(manifest)} across {len({m['item'] for m in manifest})} items. "
         f"Index: {len(idx)} defNames from {nfiles} XML files; {len(failed)} parse failures (UNMEASURED).",
         f"Sanity probe: {'PASS' if probe_ok else 'FAIL'} ({probe} present, fake name absent). "
         "get_defs call form: `defs` = single string \"DefType/DefName\" (one call per def).",
         "", "Offline-present means the def exists in src/ XML; the live get_defs read is still owed "
         "(deploy state unproven offline).", ""]
    for k, v in sorted(c.items()):
        L.append(f"- {k}: {v}")
    for st in ["OVERRIDE_VERIFIED", "OVERRIDE_VERIFIED_PLUS_EXTERNAL", "OVERRIDE_DEFECT_OR_AMBIGUOUS", "NO_DEFS_AUTHORED",
               "OFFLINE_PRESENT", "OFFLINE_PRESENT_PROSE_DERIVED", "DEFS_UNRESOLVED_OFFLINE", "DEFS_NO_NAMES_FOUND", "NEEDS_LIVE"]:
        L += ["", f"## {st}"]
        for m in manifest:
            if m["status"] != st:
                continue
            extra = f" defs={len(m['defs'])}" if m["defs"] else ""
            extra += f" MISSING={m['missing']}" if m["missing"] else ""
            extra += f" live={m['live_kind']}" if m["live_kind"] else ""
            L.append(f"- {m['item']} {m['criterion']}{extra} — {m['text'][:90]}")
            if m.get("source") == "OVERRIDE":
                for k in ("external", "missing", "ambiguous", "problems"):
                    if m.get(k):
                        L.append(f"  - {k.upper()}: {m[k]}")
                if m.get("note"):
                    L.append(f"  - note: {m['note']}")
    L += ["", "## BUILD DEFECTS AND CRITERION MISMATCHES (from overrides; real findings, not papered over)"]
    ds = [m for m in manifest if m.get("defect")]
    for m in ds:
        L.append(f"- {m['item']} {m['criterion']}: {m['defect']}")
    bad = [m for m in manifest if m["status"] in ("OVERRIDE_DEFECT_OR_AMBIGUOUS", "DEFS_UNRESOLVED_OFFLINE")]
    L.append(f"- Rows whose named def is absent from src/ after override resolution: {len(bad)}"
             + "".join(f"\n  - {m['item']} {m['criterion']}: {m.get('missing') or m.get('problems')}" for m in bad))
    if failed:
        L += ["", "## XML parse failures (UNMEASURED)"] + [f"- {a}: {b}" for a, b in failed[:40]]
    (ROOT / rp).write_text("\n".join(L) + "\n")
    print(dict(c), "probe", probe_ok, "parsefail", len(failed))


if __name__ == "__main__":
    main()
