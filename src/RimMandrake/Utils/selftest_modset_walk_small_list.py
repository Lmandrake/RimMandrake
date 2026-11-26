#!/usr/bin/env python3
"""selftest_modset_walk_small_list.py -- the small list of Gimme Some Slack's walk (owner 2026-11-24, 'go';
ledger RIMMANDRAKE_PROPOSE_FULL_LIST_WALK_NOT_PER_MOD_ARCHBIG_IS_THE_LINE; item
RIMMANDRAKE_STAGE_SLACK_WALK_SMALL_LIST_ARCHSMALL_NO_FULL_LIST).

His walk uses only the mods the mod really needs, all five expansions and the advanced-zoom mod. The list is written in
one named place, design/concepts/GimmeSomeSlack/version/small_list.json, and the modset_builder tier
`gimmesomeslack_walk` writes it. What must hold, offline, on a fake installed map that also holds Cherry Picker,
MandrakePatches and FlowWorks:
  - the tier resolves to exactly: the mod, every mod its About.xml requires, all five DLC, Harmony, the zoom mod and the
    bridge (harness); never Cherry Picker, MandrakePatches or FlowWorks; nothing missing or refused;
  - small_list.json names every modDependency of the mod's About.xml, every PatchOperationFindMod target in its Patches
    (a patch that matches nothing logs nothing), and the zoom mod; and the tier list holds each of them;
  - a tier without `no_cherry` still gets Cherry Picker (the test-tier policy is untouched).
"""
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import modset_builder as MB  # noqa: E402

TIER = "gimmesomeslack_walk"
GSS = "mandrake.rm.gimmesomeslack"
MOD_DIR = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack")
SMALL = os.path.join(REPO, "design", "concepts", "GimmeSomeSlack", "version", "small_list.json")
EXTRA = ("mandrake.rm.patches", "mandrake.rm.flowworks")
FAILS = []


def ok(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def rec(pid, deps=()):
    return {"packageId": pid, "name": pid, "deps": list(deps), "after": [], "before": [], "dir": "/x/" + pid}


def installed():
    ids = [MB.CORE, MB.HARMONY, MB.BRIDGE, MB.ZOOM, MB.CHARACTER_EDITOR, MB.CHERRY, GSS] + list(MB.DLC_IDS) + list(EXTRA)
    return {p: rec(p) for p in ids}


def about_deps():
    r = ET.parse(os.path.join(MOD_DIR, "About", "About.xml")).getroot()
    return sorted({(li.findtext("packageId") or "").strip().lower() for li in r.iter("li")
                   if li.find("packageId") is not None} - {""})


def findmod_targets():
    out = set()
    for f in glob.glob(os.path.join(MOD_DIR, "Patches", "**", "*.xml"), recursive=True):
        txt = open(f, encoding="utf-8", errors="replace").read()
        for block in re.findall(r'Class="PatchOperationFindMod".*?<mods>(.*?)</mods>', txt, re.S):
            out.update(m.strip() for m in re.findall(r"<li>(.*?)</li>", block))
    return sorted(out)


t = MB.TIERS.get(TIER)
ok(t is not None, "tier %s exists" % TIER)
pids, missing, refusals = (MB.resolve_tier(TIER, installed()) if t else ([], ["no tier"], []))
want = {MB.CORE, MB.HARMONY, MB.BRIDGE, MB.ZOOM, MB.CHARACTER_EDITOR, GSS} | set(MB.DLC_IDS)
ok(set(pids) == want, "tier resolves to exactly the mod, its needs, 5 DLC, zoom, Character Editor and bridge (extra %s, short %s)"
   % (sorted(set(pids) - want), sorted(want - set(pids))))
ok(MB.CHERRY not in pids, "no Cherry Picker on the walk list")
ok(not missing and not refusals, "nothing missing or refused (%s, %s)" % (missing, refusals))

small = json.load(open(SMALL, encoding="utf-8")) if os.path.exists(SMALL) else {}
ok(small.get("tier") == TIER, "small_list.json names tier %s" % TIER)
listed = {p.lower() for p in small.get("requires", []) + small.get("patch_targets", [])}
for d in about_deps():
    ok(d in listed, "small_list.json names About.xml dependency %s" % d)
    ok(d in pids, "tier holds About.xml dependency %s" % d)
for m in findmod_targets():
    ok(m.lower() in listed, "small_list.json names patch target %s" % m)
    ok(m.lower() in pids, "tier holds patch target %s" % m)
ok(small.get("zoom") == MB.ZOOM, "small_list.json names the zoom mod %s" % MB.ZOOM)
ok(small.get("character_editor") == MB.CHARACTER_EDITOR, "small_list.json names Character Editor %s" % MB.CHARACTER_EDITOR)
for d in MB.DLC_IDS:
    ok(d in listed, "small_list.json names expansion %s" % d)

p_other, _, _ = MB.resolve_tier("gimmesomeslack", installed())
ok(MB.CHERRY in p_other, "a tier without no_cherry still gets Cherry Picker")

print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
