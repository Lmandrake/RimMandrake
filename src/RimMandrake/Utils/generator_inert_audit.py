#!/usr/bin/env python3
"""generator_inert_audit.py -- do the five C05 "world generator" mods do anything after world creation?

    python3 src/RimMandrake/Utils/generator_inert_audit.py offline [--save NAME.rws] [--json OUT]

Owner, C05, 2026-10-10 (design/RimMandrake/mod_audit/OWNER_RULINGS.md): "You must validate that they don't do
anything after world creation. Experiments required." Item GENERATOR_MODS_PROVE_INERT_AFTER_CREATION.

OFFLINE reads each mod's shipped 1.6 DLL (ECMA-335 metadata and IL, via dnfile) and lists its RUNTIME SURFACE:
  - every Harmony target, from [HarmonyPatch] attributes AND from manual Harmony.Patch calls (an IL walk pairs
    each `ldtoken <Type>` with the next `ldstr "<Method>"`), minus the ones that only run while a world is being
    created (CREATION_ONLY below);
  - every type deriving from a class the engine ticks, saves or draws during play (RUNTIME_BASES);
  - every [StaticConstructorOnStartup] / Mod constructor that calls anything beyond Harmony setup and settings.
A mod is INERT when that surface is empty. It then scans the canonical start save (canon.yml
planet.start_savegame) for the mod's packageId in <meta><modIds> and for any of its type names: a save that names
a mod cannot lose it. Positive control: Alien Worlds' packageId must be found in the save, or the scan is blind.
Exit 0 only when every verdict equals EXPECTED (an expectation that turns false is a finding, not a fix).

A2 (no game; gen 9, 2026-11-05): the same canonical save is the record of a load WITHOUT the INERT mods. Its
<meta><modIds> is the list of the RUNNING game that wrote it (R3 was saved live: CANONICAL_SAVE.md), so when it holds
both Alien Worlds ids and neither INERT mod, its surface layer decodes to all 21,872 tiles and it names no INERT
type, the canonical world has already loaded, run and saved without them (judge_a2). The four live attempts this
replaced could not be staged: the game lane only ever ADDS mods to a list.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import game_paths  # noqa: E402

EXPECT_TILES = 21872   # Ash'karr: coverage 1.0 at subdivisions 7 (world_remake_reinstate_list.md section 1)

# packageId -> (workshop folder, DLL path inside it, assembly namespace roots)
MODS = {
    "7f.alienworlds": ("3626210061", "1.6/Assemblies/AlienWorlds.dll", ["AlienWorlds"]),
    "7f.alienworlds.tidallylocked": ("3631364335", "1.6/Assemblies/AlienWorlds.TidallyLocked.dll",
                                     ["AlienWorlds.TidallyLocked"]),
    "oblitus.mylittleplanet": ("1117406550", "1.6/Assemblies/MyLittlePlanet.dll", ["WorldGenRules", "MyLittlePlanet"]),
    "boots.sensiblefactions": ("3531306011", "Assemblies/Boots_SensibleFactions.dll", ["Boots_SensibleFactions"]),
    "jaeger972.factionterritories": ("3626725895", "Assemblies/FactionTerritories.dll", ["FactionTerritories"]),
}
EXPECTED = {
    "7f.alienworlds": "ACTIVE",
    "7f.alienworlds.tidallylocked": "ACTIVE",
    "oblitus.mylittleplanet": "INERT",
    "boots.sensiblefactions": "INERT",
    "jaeger972.factionterritories": "ACTIVE",
}
# Harmony targets that only execute while a world is being created (never in a loaded game).
CREATION_ONLY = [
    re.compile(r"^RimWorld\.Page_CreateWorldParams\."),
    re.compile(r"^RimWorld\.Planet\.WorldGenerator\.GenerateWorld$"),
    re.compile(r"^RimWorld\.Planet\.WorldGenStep_\w+\."),
    re.compile(r"^RimWorld\.BiomeWorker_\w+\.(GetScore|PermaIceScore)$"),   # biome scoring runs at worldgen only
]
RUNTIME_BASES = {"GameComponent", "WorldComponent", "MapComponent", "WorldObject", "ThingComp", "HediffComp",
                 "MapMode_Region", "ChoiceLetter", "CaravanArrivalAction", "Thing", "ThingWithComps", "Building",
                 "Hediff", "IncidentWorker", "GenStep", "JobDriver", "WorkGiver", "WorldLayer", "MapMode"}
# calls a startup constructor may make and still be nothing but Harmony and settings plumbing
SETUP_CALLS = {"Harmony..ctor", "Harmony.PatchAll", "Harmony.Patch", "HarmonyMethod..ctor", "AccessTools.Method",
               "Type.GetTypeFromHandle", "Type.GetMethod", "Assembly.GetExecutingAssembly", "Mod..ctor",
               "Mod.GetSettings", "Object..ctor", "LongEventHandler.ExecuteWhenFinished", "Action..ctor"}


# ---------------------------------------------------------------- IL walk (ECMA-335 III.1.2) ----
_OP4 = {0x20, 0x22, 0x27, 0x28, 0x29, 0x6F, 0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x79, 0x7B, 0x7C, 0x7D, 0x7E,
        0x7F, 0x80, 0x81, 0x8C, 0x8D, 0x8F, 0xA3, 0xA4, 0xA5, 0xC2, 0xC6, 0xD0, 0xDD} | set(range(0x38, 0x45))
_OP1 = {0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x1F, 0xDE} | set(range(0x2B, 0x38))
_OP8 = {0x21, 0x23}
_FE4 = {0x06, 0x07, 0x15, 0x16, 0x1C}
_FE2 = {0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E}
_FE1 = {0x12, 0x19}


def _operand_size(op, code, i):
    """bytes of operand after one-byte opcode `op` (code[i] is the first operand byte)."""
    if op in _OP4:
        return 4
    if op in _OP1:
        return 1
    if op in _OP8:
        return 8
    if op == 0x45:   # switch: uint32 n, then n int32 targets
        return 4 + 4 * struct.unpack_from("<I", code, i)[0]
    return 0


def _operand_size_fe(op2):
    return 4 if op2 in _FE4 else 2 if op2 in _FE2 else 1 if op2 in _FE1 else 0


def il_instructions(code):
    """yield (opcode, token_or_None) for a method body's IL."""
    i = 0
    while i < len(code):
        op = code[i]
        i += 1
        if op == 0xFE:
            op2 = code[i]
            i += 1
            n = _operand_size_fe(op2)
            tok = struct.unpack_from("<I", code, i)[0] if n == 4 else None
            yield (0xFE00 | op2, tok)
            i += n
            continue
        n = _operand_size(op, code, i)
        tok = struct.unpack_from("<I", code, i)[0] if n == 4 else None
        yield (op, tok)
        i += n


def method_body(pe, rva):
    if not rva:
        return b""
    off = pe.get_offset_from_rva(rva)
    data = pe.__data__
    first = data[off]
    if first & 0x3 == 0x2:                       # tiny header
        return bytes(data[off + 1: off + 1 + (first >> 2)])
    size = struct.unpack_from("<I", data, off + 4)[0]
    hdr = (struct.unpack_from("<H", data, off)[0] >> 12) * 4
    return bytes(data[off + hdr: off + hdr + size])


# ---------------------------------------------------------------- metadata ----
class Asm:
    def __init__(self, path):
        import dnfile
        self.pe = dnfile.dnPE(path)
        self.md = self.pe.net.mdtables
        self.path = path

    def user_string(self, tok):
        heap = self.pe.net.user_strings
        raw = heap.get_data_at_offset(0, heap.sizeof()) if hasattr(heap, "get_data_at_offset") else heap.__data__
        i = tok & 0xFFFFFF
        b = raw[i]
        if b & 0x80 == 0:
            n, i = b, i + 1
        elif b & 0xC0 == 0x80:
            n, i = ((b & 0x3F) << 8) | raw[i + 1], i + 2
        else:
            n, i = ((b & 0x1F) << 24) | (raw[i + 1] << 16) | (raw[i + 2] << 8) | raw[i + 3], i + 4
        return bytes(raw[i:i + max(n - 1, 0)]).decode("utf-16le", "replace")

    def token_name(self, tok):
        table, row = tok >> 24, tok & 0xFFFFFF
        try:
            if table == 0x01:
                r = self.md.TypeRef[row - 1]
                return "%s.%s" % (r.TypeNamespace, r.TypeName) if r.TypeNamespace else str(r.TypeName)
            if table == 0x02:
                r = self.md.TypeDef[row - 1]
                return "%s.%s" % (r.TypeNamespace, r.TypeName) if r.TypeNamespace else str(r.TypeName)
            if table == 0x0A:
                r = self.md.MemberRef[row - 1]
                cls = r.Class.row
                return "%s.%s" % (getattr(cls, "TypeName", "?"), r.Name)
            if table == 0x06:
                r = self.md.MethodDef[row - 1]
                return "<own>.%s" % r.Name
            if table == 0x2B:   # MethodSpec (a generic method instance): name the method it instantiates
                m = self.md.MethodSpec[row - 1].Method
                return self.token_name((m.table.number << 24) | m.row_index)
        except (IndexError, AttributeError):
            pass
        return "?%08x" % tok

    def types(self):
        for t in self.md.TypeDef:
            ext = t.Extends.row if t.Extends else None
            base = getattr(ext, "TypeName", None) if ext is not None else None
            meths = [m.row for m in t.MethodList] if t.MethodList else []
            yield "%s.%s" % (t.TypeNamespace, t.TypeName), str(base), meths, t


def _ca_strings(blob):
    out, i = [], 2
    while i < len(blob) - 1:
        n = blob[i]
        if 0 < n < 0x80 and i + 1 + n <= len(blob):
            s = blob[i + 1:i + 1 + n]
            if all(32 <= c < 127 for c in s):
                out.append(s.decode())
                i += 1 + n
                continue
        i += 1
    return out


def attribute_targets(asm):
    """[HarmonyPatch(typeof(T), "M")] targets, merged per patch class (class + method attributes)."""
    per_owner = {}
    for ca in asm.md.CustomAttribute:
        try:
            an = ca.Type.row.Class.row.TypeName
        except AttributeError:
            continue
        if str(an) != "HarmonyPatch":
            continue
        par = ca.Parent.row
        owner = str(getattr(par, "TypeName", None) or getattr(par, "Name", "?"))
        raw = ca.Value if isinstance(ca.Value, (bytes, bytearray)) else getattr(ca.Value, "raw_data", b"")
        per_owner.setdefault(owner, []).extend(_ca_strings(bytes(raw)))
    targets = []
    for owner, strs in per_owner.items():
        typ = next((s.split(",")[0] for s in strs if "." in s.split(",")[0] and " " not in s.split(",")[0]), None)
        meth = next((s for s in strs if re.fullmatch(r"[A-Za-z_]\w*", s)), None)
        targets.append((owner, "%s.%s" % (typ, meth) if typ and meth else "UNRESOLVED(%s)" % ",".join(strs)))
    return targets


def manual_targets_and_ctors(asm):
    """IL walk: manual Harmony.Patch targets (ldtoken T ... ldstr M), each method's external calls."""
    manual, calls_by_method = [], {}
    for tname, _base, meths, _t in asm.types():
        for m in meths:
            code = method_body(asm.pe, m.Rva)
            last_type, calls, strs = None, [], []
            for op, tok in il_instructions(code):
                if op == 0xD0 and tok:
                    # a TypeDef token is the mod's own class (typeof(MyPatch) for HarmonyMethod): not a target
                    last_type = asm.token_name(tok) if tok >> 24 == 0x01 else None
                elif op == 0x72 and tok:
                    s = asm.user_string(tok)
                    strs.append(s)
                    if last_type and re.fullmatch(r"[A-Za-z_]\w*", s):
                        manual.append(("%s.%s" % (tname, m.Name), "%s.%s" % (last_type, s)))
                        last_type = None
                elif op in (0x28, 0x6F, 0x73) and tok:
                    calls.append(asm.token_name(tok))
            calls_by_method.setdefault("%s.%s" % (tname, m.Name), []).extend(calls)   # overloads share a key
    return manual, calls_by_method


def audit_mod(pkg):
    folder, rel, _ns = MODS[pkg]
    path = os.path.join(game_paths.WORKSHOP, folder, *rel.split("/"))
    about = os.path.join(game_paths.WORKSHOP, folder, "About", "About.xml")
    got = (ET.parse(about).getroot().findtext("packageId") or "").strip().lower()
    if got != pkg:
        raise SystemExit("REFUSED: %s holds %r, not %s; fix MODS" % (about, got, pkg))
    asm = Asm(path)
    manual_all, calls_by_method = manual_targets_and_ctors(asm)
    manual = [(o, t) for o, t in manual_all
              if "Harmony.Patch" in calls_by_method.get(o, []) or "AccessTools.Method" in calls_by_method.get(o, [])]
    targets = attribute_targets(asm) + manual
    runtime_targets = sorted({t for _o, t in targets if not any(p.search(t) for p in CREATION_ONLY)})
    creation_targets = sorted({t for _o, t in targets if any(p.search(t) for p in CREATION_ONLY)})
    runtime_types, startup_extra, dev_actions = [], [], []
    scos = set()
    for ca in asm.md.CustomAttribute:
        try:
            if str(ca.Type.row.Class.row.TypeName) == "StaticConstructorOnStartup":
                par = ca.Parent.row
                scos.add("%s.%s" % (par.TypeNamespace, par.TypeName))
        except AttributeError:
            continue
    for tname, base, meths, _t in asm.types():
        if base in RUNTIME_BASES:
            runtime_types.append("%s : %s" % (tname, base))
        for m in meths:
            key = "%s.%s" % (tname, m.Name)
            if (m.Name == ".cctor" and tname in scos) or (m.Name == ".ctor" and base == "Mod"):
                # an unresolved call ("?...") counts against inertness: what cannot be named cannot be cleared
                extra = sorted({c for c in calls_by_method.get(key, []) if c not in SETUP_CALLS
                                and not c.startswith("<own>.")})
                own = [c for c in calls_by_method.get(key, []) if c.startswith("<own>.")]
                if extra:
                    startup_extra.append("%s calls %s" % (key, ", ".join(extra)))
                if own:
                    startup_extra.append("%s calls own %s" % (key, ", ".join(sorted(set(own)))))
    for ca in asm.md.CustomAttribute:
        try:
            if str(ca.Type.row.Class.row.TypeName) == "DebugActionAttribute":
                dev_actions.append(str(getattr(ca.Parent.row, "Name", "?")))
        except AttributeError:
            continue
    surface = runtime_targets + runtime_types + startup_extra
    return {"packageId": pkg, "dll": path, "verdict": "INERT" if not surface else "ACTIVE",
            "creation_only_targets": creation_targets, "runtime_targets": runtime_targets,
            "runtime_types": runtime_types, "startup_extra": startup_extra,
            "dev_only_debug_actions": dev_actions,
            "type_names": [t for t, _b, _m, _t in asm.types() if not t.startswith(".") and "<" not in t]}


def canonical_save_name():
    with open(os.path.join(REPO, "infrastructure", "state", "canon.yml"), encoding="utf-8") as fh:
        m = re.search(r"^\s*start_savegame:\s*(\S+)", fh.read(), re.M)
    if not m:
        raise SystemExit("REFUSED: canon.yml has no planet.start_savegame")
    return m.group(1)


def scan_save(path, audits):
    """packageIds in <meta><modIds>, and which audited type names the save text contains."""
    with open(path, "rb") as fh:
        head = fh.read(4 << 20).decode("utf-8", "replace")
    m = re.search(r"<modIds>(.*?)</modIds>", head, re.S)
    if not m:
        raise SystemExit("REFUSED: no <modIds> in the first 4 MB of %s" % path)
    mod_ids = [x.strip().lower() for x in re.findall(r"<li>(.*?)</li>", m.group(1))]
    wname = re.search(r"<world>.*?<info>.*?<name>(.*?)</name>", head, re.S)
    needles = {}
    for a in audits:
        for t in a["type_names"]:
            if "." in t:
                needles[t] = a["packageId"]
    found = {}
    tail = b""
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(8 << 20)
            if not chunk:
                break
            buf = tail + chunk
            text = buf.decode("utf-8", "replace")
            for t, pkg in needles.items():
                if t in text:
                    found.setdefault(pkg, set()).add(t)
            tail = buf[-256:]
    return mod_ids, {k: sorted(v) for k, v in found.items()}, (wname.group(1) if wname else None)


def offline(args):
    save = args.save or canonical_save_name()
    spath = os.path.join(game_paths.SAVES, save)
    audits = [audit_mod(p) for p in MODS]
    mod_ids, named_types, world_name = scan_save(spath, audits)
    ok = True
    if "7f.alienworlds" not in mod_ids or len(mod_ids) < 20:
        print("BLIND: positive control failed (7f.alienworlds absent from %d modIds in %s)" % (len(mod_ids), save))
        ok = False
    print("save %s: %d modIds, planet %r" % (save, len(mod_ids), world_name))
    for a in audits:
        pkg = a["packageId"]
        a["save_lists_mod"] = pkg in mod_ids
        a["save_names_types"] = named_types.get(pkg, [])
        match = a["verdict"] == EXPECTED[pkg]
        if a["verdict"] == "INERT" and (a["save_lists_mod"] or a["save_names_types"]):
            match = False
        ok &= match
        print("%-30s %-6s expected %-6s %s | runtime targets %d, runtime types %d, startup extra %d, "
              "creation-only targets %d | save lists it: %s, names its types: %d"
              % (pkg, a["verdict"], EXPECTED[pkg], "ok" if match else "MISMATCH", len(a["runtime_targets"]),
                 len(a["runtime_types"]), len(a["startup_extra"]), len(a["creation_only_targets"]),
                 a["save_lists_mod"], len(a["save_names_types"])))
        for t in a["creation_only_targets"]:
            print("    creation-only  %s" % t)
        for t in (a["runtime_targets"] + a["startup_extra"])[:8]:
            print("    runtime        %s" % t)
        if a["dev_only_debug_actions"]:
            print("    dev-only debug actions (developer mode menu): %s" % ", ".join(a["dev_only_debug_actions"]))
    code, why = judge_a2(mod_ids, surface_tiles(spath), named_types)
    print("A2 %s: %s" % ("PASS" if code == PASS else "FAIL", why))
    ok &= code == PASS
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"save": save, "world": world_name, "mods": audits}, fh, indent=1, default=list)
    print("OFFLINE %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


PASS, FAIL = 0, 1
ALIEN_WORLDS = ("7f.alienworlds", "7f.alienworlds.tidallylocked")


def surface_tiles(path):
    """The canonical save's surface-layer tile count: the first <tileBiomeDeflate> (base64 of raw-DEFLATE ushorts, one
    BiomeDef shortHash per tile) decoded and halved, or None when there is none."""
    import base64
    import zlib
    with open(path, encoding="utf-8", errors="replace") as fh:
        m = re.search(r"<tileBiomeDeflate>(.*?)</tileBiomeDeflate>", fh.read(), re.S)
    if not m:
        return None
    return len(zlib.decompress(base64.b64decode(m.group(1).strip()), -15)) // 2


def judge_a2(mod_ids, tiles, inert_types):
    """A2: the canonical world has run WITHOUT the INERT mods. A RimWorld save's <meta><modIds> is the mod list of the
    RUNNING game that wrote it (ScribeMetaHeaderUtility), so a canonical save listing neither INERT mod, both Alien
    Worlds ids, the whole 21,872-tile planet and no type of an INERT mod is a world that loaded, ran and saved without
    them. -> (PASS|FAIL, why)."""
    inert = sorted(p for p, v in EXPECTED.items() if v == "INERT")
    if len(mod_ids) < 20:
        return FAIL, "BLIND: only %d modIds read" % len(mod_ids)
    lacking = [p for p in ALIEN_WORLDS if p not in mod_ids]
    if lacking:
        return FAIL, "the save's running list lacks %s: not the canonical load" % ", ".join(lacking)
    held = [p for p in inert if p in mod_ids]
    if held:
        return FAIL, "the game that wrote the save ran %s: no load without it is on record" % ", ".join(held)
    if tiles != EXPECT_TILES:
        return FAIL, "the save's surface layer holds %s tiles, not %d" % (tiles, EXPECT_TILES)
    named = sorted(t for p in inert for t in inert_types.get(p, []))
    if named:
        return FAIL, "the save names INERT types %s" % ", ".join(named[:5])
    return PASS, ("the canonical world (%d tiles) was written by a running game whose %d-mod list held both Alien "
                  "Worlds ids and neither %s; the save names none of their types" % (tiles, len(mod_ids), " nor ".join(inert)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    o = sub.add_parser("offline")
    o.add_argument("--save", help="save file name in the Saves folder (default: canon.yml planet.start_savegame)")
    o.add_argument("--json")
    args = ap.parse_args(argv)
    return offline(args)


if __name__ == "__main__":
    sys.exit(main())
