#!/usr/bin/env python3
"""Bones functional script (BONES_LEAN_PORT_BUILD_TREELESS_WORLD): the live half of the lean Bones port.

Offline clauses live in selftest_bones_port.py; this suite asks the RUNNING game (mandrake.rm.biomes loaded,
sihv.rombonesPort absent) four things, each through a static proof hook so the real engine paths answer:

  load      no load error names this mod's defs or classes;
  defs      RM_BonesProof.ProofDefs: RM_Bones is Woody stuff a Wall accepts, RM_BoneAmount and RM_BoneFloor exist,
            and no donor def (BoneItem, BoneChina, Bonecrete, BonePlastic, BoneWall, BoneAmount) is loaded;
  aliases   RM_DefAliasProof.ProofAliases (EnvironmentalHazards): every donor name in RM_BonesRetireAliases resolves
            to RM_Bones / RM_BoneFloor through BackCompatibility.BackCompatibleDefName (and the terrain short-hash
            path), which is what lets the 204 ancient BoneChina walls and doors load;
  butcher   RM_BonesProof.ProofButcher: the real Pawn.ButcherProducts on a muffalo yields RM_Bones and meat, an
            insect (megascarab) none, and none with butcherBones off (setting restored after).

    python3 src/RimMandrake/Bones/validation.py          static checks only (exit 0/1)
    modcheck run Bones                                     the live chains (needs the bridge and a map)

Informative false theories: none recorded yet. Add one here whenever a live session disproves a guess.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
from modcheck import Suite, ExpectationFailed  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
suite = Suite("Bones")
suite.toggles = ["butcherBones", "boneMultiplier"]
PROOF = "RimMandrake.Bones.RM_BonesProof"
ALIAS_PROOF = "RimMandrake.EnvironmentalHazards.RM_DefAliasProof"
DONOR_NAMES = ("BoneItem", "BoneChina", "Bonecrete", "BonePlastic",
               "BoneFloor", "BoneFloor_Blackened", "BoneFloor_Ashen", "BoneFloor_Tile", "BoneChinaFloor")
WANT = {n: ("RM_Bones" if i < 4 else "RM_BoneFloor") for i, n in enumerate(DONOR_NAMES)}
NEEDLES = ("RimMandrake.Bones", "RM_Bones", "RM_BoneAmount", "RM_BoneFloor", "RM_BonesRetireAliases")


def _text(r):
    return str((r or {}).get("result") or (r or {}).get("value") or r)


def _proof(t, typ, method):
    r = t.bridge_call("jawa/static_call", type=typ, method=method, args="")
    text = _text(r)
    if not (text.startswith("PASS") or text.startswith("FAIL")):
        raise ExpectationFailed("UNMEASURED: static_call %s.%s did not answer: %s" % (typ, method, text[:200]))
    return text


@suite.chain("load")
def load(t):
    with t.component("no_errors_naming_this_mod", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        if t._guard():
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("UNMEASURED: drain_log did not answer")
            msgs = [m.get("text", "") for m in (r.get("messages") or [])]
            hits = [m[:160] for m in msgs if any(n in m for n in NEEDLES)]
            if hits:
                raise ExpectationFailed("errors name this mod: %r" % hits[:4])


@suite.chain("defs")
def defs(t):
    with t.component("bone_is_woody_stuff_no_donor_defs", beyond_toggle=True):
        if t._guard():
            text = _proof(t, PROOF, "ProofDefs")
            if not text.startswith("PASS"):
                raise ExpectationFailed(text[:400])


@suite.chain("aliases")
def aliases(t):
    with t.component("donor_bone_defs_load_as_ours", beyond_toggle=True):
        if t._guard():
            text = _proof(t, ALIAS_PROOF, "ProofAliases")
            bad = []
            for n, want in WANT.items():
                if ("PASS %s->%s;" % (n, want)) not in text:
                    m = re.search(r"(PASS|FAIL) %s->[^;]*;" % re.escape(n), text)
                    bad.append(m.group(0) if m else "%s: no row" % n)
            if bad:
                raise ExpectationFailed("alias rows: %s" % bad)


@suite.chain("butcher")
def butcher(t):
    with t.component("butchering_yields_bones_gated", toggle="butcherBones"):
        if t._guard():
            text = _proof(t, PROOF, "ProofButcher")
            if not text.startswith("PASS"):
                raise ExpectationFailed(text[:400])


def static_checks():
    bad = []
    src = os.path.join(HERE, "Source")
    proj = open(os.path.join(src, "RM_Bones.csproj"), encoding="utf-8").read()
    for dp, dn, fn in os.walk(src):
        dn[:] = [d for d in dn if d not in ("obj", "bin")]
        for f in fn:
            if f.endswith(".cs"):
                rel = os.path.relpath(os.path.join(dp, f), src).replace("/", "\\")
                if ('Compile Include="%s"' % rel) not in proj:
                    bad.append("%s is not in the csproj (compiles into nothing)" % rel)
    mod = open(os.path.join(src, "RM_BonesMod.cs"), encoding="utf-8").read()
    for f in suite.toggles:
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s"' % (f, f), mod):
            bad.append("toggle %s is not Scribed" % f)
    keyed = open(os.path.join(HERE, "Languages", "English", "Keyed", "RM_Bones.xml"), encoding="utf-8").read()
    for k in sorted(set(re.findall(r'"(RM_Bones_[A-Za-z_]+)"', mod))):
        if "<%s>" % k not in keyed:
            bad.append("keyed string %s missing" % k)
    proof = open(os.path.join(src, "RM_BonesProof.cs"), encoding="utf-8").read()
    for m in ("ProofDefs", "ProofButcher"):
        if "public static string %s(string" % m not in proof:
            bad.append("proof hook %s missing" % m)
    if not os.path.isfile(os.path.join(HERE, "Assemblies", "RimMandrake.Bones.dll")):
        bad.append("no RimMandrake.Bones.dll")
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
