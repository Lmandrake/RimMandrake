#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_weapon_register.py — the owner's weapon-ART review sheet, rebuildable.

VERSION 1.0  (2026-09-05)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Python 3.8+ stdlib **plus Pillow**. Sibling of `gen_creature_register.py`, whose
structure, locks and data-honesty discipline this file deliberately copies.

WHAT IT MAKES
=============
    design/Jawa/worldbuilding/review/weapon_register.html            the sheet
    design/Jawa/worldbuilding/review/weapon_register.decisions.json  the owner's file
    design/Jawa/worldbuilding/review/weapon_register_rows.json       the data (derived)
    design/Jawa/worldbuilding/review/weapon_art/<defName>.scale.png  true in-hand scale
    design/Jawa/worldbuilding/review/weapon_art/<defName>.detail.png fixed zoom for art

Every one of those is DERIVED and regenerable. The one file that stops being so
is `weapon_register.decisions.json` the moment the owner touches it — see THE LOCK.

THE FOUR STAGES, AND WHY THEY ARE SEPARATE
==========================================
    data     defs.sqlite + Cherry Picker + pawnkind tag index  ->  rows json
    art      rows json                                         ->  two PNGs per row
    sheet    rows json + decisions json + the skill template    ->  the html
    prefill  rows json                                          ->  decisions json  🔒 LOCKED

⭐ Regenerating the SHEET must stay safe, because a renderer fix has to be
pickable-up mid-review; only the DECISION generator is locked. `--stage all`
runs data+art+sheet and NEVER prefill (review-sheets rule 7).

🔒 THE LOCK. `--stage prefill` refuses once the decisions file carries `savedBy` —
a key only serve_sheet.py writes, so this generator physically cannot forge it.
Override with `--i-know-this-overwrites-the-owners-decisions`.

WHERE EVERY NUMBER COMES FROM (data honesty)
============================================
🔑 EVERY WEAPON NUMBER HERE IS THE **DECLARED BASE**, at no stuff and normal
quality, with no wielder. That is a real limit and it is stated on the page:

  * a stuffable melee weapon's real damage is `power x
    MeleeWeapon_DamageMultiplier(stuff)` — a plasteel longsword hits harder than
    the number on its row;
  * quality multiplies melee damage and ranged accuracy;
  * the wielder's Shooting/Melee skill and the weapon's own hediffs are absent.

⛔ There is NO resolved-stat capture for weapons the way `animals.json` exists for
creatures, so nothing here can be joined to a running game. Rather than invent
one, this file computes what the ENGINE'S OWN StatWorkers compute from the same
inputs — the formulas were read out of the game's C#, not guessed:

  ranged DPS = damage x burstShotCount
               / (warmupTime + RangedWeapon_Cooldown
                  + (burstShotCount - 1) x ticksBetweenBurstShots / 60)

  melee DPS  = weightedAvg(tool.power) / weightedAvg(tool.cooldownTime),
               weight_i = power_i^2 x commonality x chanceFactor
               (RimWorld/StatWorker_MeleeAverageDPS.cs + VerbProperties.
                AdjustedMeleeSelectionWeight — note it is avg(dmg)/avg(cd),
                NOT avg(dmg/cd), and the two differ whenever cooldowns differ)

  armour pen: a tool or projectile declaring < 0 does NOT mean "none" — the
              engine derives `damage x 0.015` (VerbProperties.
              AdjustedArmorPenetration, ProjectileProperties.GetArmorPenetration).
              Reading -1 as zero would have printed 0% on most of the melee list.

CALIBRATION (`--calibrate`), and the one row that must NOT match the wiki
========================================================================
  Gun_AssaultRifle   dmg 11 · burst 3 · warmup 1s · cooldown 1.7s · 10 ticks
                     -> DPS 10.88, which is the RimWorld wiki's own figure.
                     range 30.9 · acc 60/70/65/55 · work 40000 · mass 3.5.
  MeleeWeapon_Gladius tools 9 blunt / 16 stab / 16 cut, all 2.0s — byte-identical
                     to the installed Core XML (Defs/Core/ThingDefs_Misc/Weapons/
                     MeleeMedieval.xml) — and the melee formula returns 7.52.
                     ⭐ The formula is independently proven on the SAME published
                     source that lists a 1.4-era gladius at power 15: feed it
                     9/15/15 and it returns 7.04, which is that source's printed
                     DPS to the digit. A formula that reproduces someone else's
                     number from their inputs is tested, not merely run.

  ⚠️ ONE DELIBERATE DIVERGENCE, and it is SOURCED. `Bullet_AssaultRifle.
  armorPenetrationBase` is **0.19** in this stack. Vanilla Core declares none at
  all, so the engine would derive 11 x 0.015 = 0.165 — the wiki's 16%. The value
  comes from **Yayo's Combat 3 (Continued)** (`Mlie.YayosCombat3`,
  `1.6/Patches/patch_weapon.xml`), which rewrites the projectile. Calibration
  asserts 0.19 and FAILS on 0.165, because a run that reads vanilla's number
  means that mod stopped applying — which would silently change every ranged AP
  figure on this sheet.

🔴 FRESHNESS IS THE MOD SET, NOT THE CLOCK — same gate as the creature register,
against the frozen `ModsConfig.FULL.LATEST.xml`, not live ModsConfig (another
window swaps live for a 13-mod minimal list to get a 22-second load).

⛔ CHERRY PICKER IS THE OTHER HALF, and `cherrypicker.py` is the one reader.
Cut weapons are BADGED, never hidden: the owner must be able to tell "this mod
ships nothing" from "I cut it all".
🔑 A SECOND, INDEPENDENT SIGNAL AGREES WITH IT, and it is worth knowing: every
one of the 177 cut weapons has an EMPTY `weaponTags` list in the dump, and no
weapon with tags is cut. So the dump is not uniformly pre-Cherry-Picker — the
list fields have already been stripped in it. The settings file stays the
authority; the empty-tags reading is reported as corroboration.

USAGE
    python3 src/RimMandrake/Utils/gen_weapon_register.py --stage all
    python3 src/RimMandrake/Utils/gen_weapon_register.py --calibrate
    python3 src/RimMandrake/Utils/gen_weapon_register.py --stage prefill
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sqlite3
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

import cherrypicker                                        # noqa: E402
import game_paths as GP                                    # noqa: E402
import rimworld_loadset as LS                              # noqa: E402
import animal_contact_sheet as ACS                         # noqa: E402
import thing_contact_sheet as TCS                          # noqa: E402

VERSION = "1.0"

# ── where things live ────────────────────────────────────────────────────────
REVIEW = os.path.join(REPO, "design", "Jawa", "worldbuilding", "review")
ART_DIR = os.path.join(REVIEW, "weapon_art")
ROWS_JSON = os.path.join(REVIEW, "weapon_register_rows.json")
SHEET_HTML = os.path.join(REVIEW, "weapon_register.html")
DECISIONS = os.path.join(REVIEW, "weapon_register.decisions.json")
TEMPLATE = os.path.expanduser(
    "~/.claude/skills/review-sheets/assets/sheet_template.html")
DB = os.path.join(GP.DUMP_ROOT, "defs.sqlite")
TEXCACHE = "/tmp/claude-1000/weapon_register_texindex.json"
HUMAN_ANCHOR = os.path.join(REVIEW, "assets", "human_anchor_south.png")
FULL_MODLIST = os.path.join(REPO, "infrastructure", "state", "modlists",
                            "ModsConfig.FULL.LATEST.xml")

# ── scale constants ──────────────────────────────────────────────────────────
# 🔑 A WEAPON'S TRUE IN-HAND SIZE IS `graphicData.drawSize`, FULL STOP. Read out
# of Verse/PawnRenderUtility.cs::DrawEquipmentAiming, which builds the mesh with
# `new Vector3(eq.Graphic.drawSize.x, 0f, eq.Graphic.drawSize.y)` and nothing
# else — no bodySize term, no fitted constant. So the picture and the game agree
# exactly, the same way the creature register's does.
PX_PER_CELL = 128         # ⚠️ 2x the creature register's 64. See CONFIG.invented:
                          # a 1-cell weapon at 64 px is too small to judge on a
                          # web page. The human anchor is scaled by the SAME
                          # factor, so the RATIO — the only thing the panel is
                          # for — stays true.
HUMAN_CELLS = 1.5         # a vanilla humanlike body graphic is drawn at 1.5 cells
DETAIL_BOX = 240          # px; the fixed-size art-inspection sprite
SCALE_CAP = 1500          # px; a bigger canvas is downscaled and SAYS so

# ── the shipping-art quality metric, and its two thresholds ──────────────────
# pxPerCell = the sprite's longest source edge / its longest DRAWN edge in px.
# Below 1.0 the engine upscales the art; below 0.5 it is stretched over 2x.
PPC_BAD = 0.5
PPC_SOFT = 0.8

# 🔴 WEAPONS ARE RESOLVED BARE-FIRST. animal_contact_sheet's ladder leads with
# `_south` because a pawn sprite has sides; an item texture almost never does,
# and leading with `_south` risks handing back a side variant of some other
# thing. Overridden per-run rather than edited into that module.
BARE_FIRST = ("", "_south", "_east", "_north", "_side")
BARE_FIRST_BUNDLE = ("", "_south", "_east", "_north", "_side", "_m")

# ── clustering. Six clusters, fixed by the owner's request. ──────────────────
CLUSTERS = ("ranged-ballistic", "ranged-energy", "explosive",
            "melee-blade", "melee-blunt", "natural / other")

# Capacity -> which melee cluster it argues for. Anything unlisted is decided by
# a substring rule and MARKED inferred, per review-sheets rule 2.
BLADE_CAPS = {"Cut", "Stab", "Poke", "Scratch"}
BLUNT_CAPS = {"Blunt", "Demolish", "Thump"}
# Natural-part vocabulary. A melee weapon that is a body part rather than a made
# object: it has no recipe, no cost and its label says what it is.
NATURAL_WORDS = ("tusk", "horn", "claw", "fang", "talon", "sting", "tooth",
                 "teeth", "spine", "quill", "mandible", "pincer", "beak",
                 "antler", "venom sac", "barb")

# Damage-type names that mean ENERGY when the damageDef carries no armour
# category to judge on (armorCategory Heat is the primary, data-driven signal).
ENERGY_WORDS = ("energy", "blaster", "laser", "ion", "plasma", "disruptor",
                "sonic", "beam", "turbolaser", "emp", "arc", "electr", "photon",
                "phaser", "pulse", "vaporize", "vapourise", "flame", "burn",
                "incend", "thermal", "fusion")

# 🔴 THE REGISTER HEURISTIC, and it is a NAME test, not an art judgement.
# The campaign is Star Wars: scavenged, ion, salvage-built and blaster-adjacent
# belong; a recognisably modern-Earth firearm is a problem however well drawn.
# This list is LEXICAL — it reads the label, it cannot see the sprite — so every
# row it fires on is marked CONTESTED and says so in the note.
EARTH_WORDS = (
    "assault rifle", "ak-47", "ak47", "ak-74", "m16", "m4 ", "m4a1", "ar-15",
    "glock", "uzi", "mp5", "mp40", "ump", "beretta", "colt", "magnum",
    "kalashnikov", "luger", "mauser", "thompson", "tommy gun", "browning",
    "remington", "winchester", "mosin", "garand", "sks", "fal", "g36", "scar",
    "famas", "aug ", "galil", "tavor", "desert eagle", "revolver",
    "pump shotgun", "combat shotgun", "sniper rifle", "bolt-action",
    "bolt action", "submachine gun", "machine pistol", "autopistol",
    "heavy smg", "lmg", "minigun", "rpg-", "grenade launcher", "kalash",
    "carbine", "musket", "flintlock", "blunderbuss", "derringer",
)

KNOWN_TURRET_TAG = "TurretGun"


# ═════════════════════════════════════════════════════════════════ util
def _num(v, default=None):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    if math.isnan(f) or math.isinf(f):
        return default
    return f


def _vec(v):
    if isinstance(v, dict):
        return (_num(v.get("x")), _num(v.get("y")))
    return (None, None)


def die(msg):
    print("REFUSED: " + msg, file=sys.stderr)
    sys.exit(3)


def _fmt(v, nd=1, suffix=""):
    """A number, or the literal string UNMEASURED. Never a plausible digit."""
    if v is None:
        return "UNMEASURED"
    if isinstance(v, float) and abs(v - round(v)) < 1e-9:
        return "%d%s" % (round(v), suffix)
    return ("%.*f%s" % (nd, v, suffix))


def _pct(v):
    return "UNMEASURED" if v is None else "%d%%" % round(v * 100)


# ═════════════════════════════════════════════════════════════ freshness
def _mods_of(path):
    root = ET.parse(path).getroot()
    am = root.find("activeMods")
    if am is None:
        die("%s has no <activeMods> — cannot fingerprint anything." % path)
    return {(e.text or "").strip().lower() for e in am}


MODINDEX_CACHE = "/tmp/claude-1000/weapon_register_modindex.json"


def _mod_index():
    """{packageId: folder} across every root, cached. discover_mods walks a lot of
    About.xml on a Windows mount, so it is paid once."""
    os.makedirs(os.path.dirname(MODINDEX_CACHE), exist_ok=True)
    if os.path.isfile(MODINDEX_CACHE):
        try:
            with open(MODINDEX_CACHE, encoding="utf-8") as fh:
                idx = json.load(fh)
            if all(os.path.isdir(v) for v in list(idx.values())[:20]):
                return idx
        except (OSError, ValueError):
            pass
    raw = LS.discover_mods([GP.WORKSHOP, GP.LOCAL_MODS, GP.GAME_DATA])
    idx = {k: v["folder"] for k, v in raw.items()}
    with open(MODINDEX_CACHE, "w", encoding="utf-8") as fh:
        json.dump(idx, fh)
    return idx


def _prove_absent_ship_no_weapons(absent):
    """A mod the dump never saw is only survivable if it PROVABLY ships no weapon.

    🔴 THE ASYMMETRY IS THE WHOLE POINT. A cut weapon can be badged on its row; a
    weapon that was never in the dump is simply not on the sheet, and an absence
    has no badge — the owner would review a list that quietly omits things. So
    the default is REFUSE.

    ⚠️ But refusing on a UI theme mod is a false alarm that stops the sheet
    existing, so the exception is EARNED ON DISK rather than assumed: walk the
    mod's own folder and look for the three tags a weapon def cannot avoid
    (<verbs>, <tools>, <weaponTags>). Nothing found -> it ships no weapon and is
    recorded as such in the sheet's provenance. Anything found, or a mod whose
    folder cannot be located at all -> refuse and name it.
    """
    idx = _mod_index()
    proven = []
    for pid in absent:
        folder = idx.get(pid)
        if not folder or not os.path.isdir(folder):
            die("the frozen FULL mod list has %r, which the dump never saw AND whose "
                "folder is not on disk, so it cannot even be checked for weapons. Its "
                "weapons would be missing from this sheet with nothing to say so, and "
                "an absence cannot be badged. Re-take the dump (refresh.py) first."
                % pid)
        hits = []
        for root, _dirs, files in os.walk(folder):
            for fn in files:
                if not fn.lower().endswith(".xml"):
                    continue
                fp = os.path.join(root, fn)
                try:
                    with open(fp, encoding="utf-8", errors="replace") as fh:
                        blob = fh.read()
                except OSError:
                    continue
                if "<verbs>" in blob or "<tools>" in blob or "<weaponTags>" in blob:
                    hits.append(os.path.relpath(fp, folder))
        if hits:
            die("the frozen FULL mod list has %r, which the dump never saw, and its "
                "folder DOES declare weapon-shaped defs (%s). Those weapons would be "
                "missing from this sheet with nothing to say so. Re-take the dump "
                "(refresh.py) first." % (pid, ", ".join(hits[:3])))
        proven.append(pid)
    return proven


def dump_fingerprint():
    """The dump's mod set vs the FROZEN full list. Direction is the judgement.

    dump ⊃ full — the dump knows a mod since dropped. Its weapons show up on the
                  sheet and are BADGED, exactly like a Cherry Picker cut.
    full ⊃ dump — a mod loads the dump never saw. Its weapons would be ABSENT
                  with nothing to say so, and an absence cannot be badged. Refuse.
    """
    if not os.path.isfile(DB):
        die("no def dump at %s — nothing to read." % DB)
    db = sqlite3.connect(DB)
    prov = dict(db.execute("select key, value from provenance"))
    sq = {r[0].strip().lower() for r in db.execute("select package_id from mods")}
    db.close()

    if not os.path.isfile(FULL_MODLIST):
        die("no frozen full mod list at %s — there is nothing authoritative to "
            "fingerprint the dump against." % FULL_MODLIST)
    full = _mods_of(FULL_MODLIST)
    extra, absent = sorted(sq - full), sorted(full - sq)
    proven = _prove_absent_ship_no_weapons(absent) if absent else []
    try:
        live = _mods_of(GP.MODS_CONFIG)
    except (OSError, ET.ParseError):
        live = set()
    return {
        "dumpMods": len(sq),
        "fullModlist": len(full),
        "liveActiveMods": len(live),
        "liveMatchesFull": live == full,
        "droppedSinceDump": extra,
        "absentFromDump": absent,
        "absentProvenWeaponless": proven,
        "dumpCaptured": prov.get("captured_utc") or prov.get("capturedUtc") or "?",
        "gameVersion": prov.get("game_version") or "?",
    }


# ═════════════════════════════════════════════════════════════ calibration
# Six readings that MUST match published vanilla, and one that must NOT.
CALIB_MATCH = {
    "ar_damage": 11.0, "ar_burst": 3.0, "ar_warmup": 1.0, "ar_cooldown": 1.7,
    "ar_range": 30.9, "ar_dps": 10.88, "ar_accLong": 0.55, "ar_work": 40000.0,
    "gl_blunt": 9.0, "gl_cut": 16.0, "gl_cooldown": 2.0, "gl_dps": 7.52,
    "gl_bluntAP": 0.135,
}
# ⚠️ The sourced surprise. Vanilla Core declares no armorPenetrationBase on
# Bullet_AssaultRifle, so the engine derives 11 x 0.015 = 0.165 (the wiki's 16%).
# This stack reads 0.19, which cannot arise from that derivation: a mod sets it.
CALIB_PATCHED = {"ar_ap": 0.19}
# The formula's own regression fixture: an independently published gladius at
# power 15 is listed at DPS 7.04. Feed the same inputs to melee_dps and it must
# return 7.04, or the weighting is wrong.
CALIB_FORMULA_TOOLS = [{"power": 9, "cooldownTime": 2, "chanceFactor": 1},
                       {"power": 15, "cooldownTime": 2, "chanceFactor": 1},
                       {"power": 15, "cooldownTime": 2, "chanceFactor": 1}]
CALIB_FORMULA_DPS = 7.04


def calibrate(db):
    bad = []
    got = {}

    ar = _def(db, "Gun_AssaultRifle")
    gl = _def(db, "MeleeWeapon_Gladius")
    if not ar or not gl:
        return ["Gun_AssaultRifle and/or MeleeWeapon_Gladius are not in the dump — "
                "nothing can be calibrated"]
    f = ar["fields"]
    stats = _stats(f)
    v = _primary_verb(f)
    proj = _def(db, (v or {}).get("defaultProjectile"))
    pj = ((proj or {}).get("fields") or {}).get("projectile") or {}
    got["ar_damage"] = _num(pj.get("damageAmountBase"))
    got["ar_ap"] = _num(pj.get("armorPenetrationBase"))
    got["ar_burst"] = _num((v or {}).get("burstShotCount"))
    got["ar_warmup"] = _num((v or {}).get("warmupTime"))
    got["ar_cooldown"] = stats.get("RangedWeapon_Cooldown")
    got["ar_range"] = _num((v or {}).get("range"))
    got["ar_accLong"] = stats.get("AccuracyLong")
    got["ar_work"] = stats.get("WorkToMake")
    got["ar_dps"] = ranged_dps(got["ar_damage"], got["ar_burst"], got["ar_warmup"],
                               got["ar_cooldown"], _num((v or {}).get("ticksBetweenBurstShots")))

    gf = gl["fields"]
    tools = {t.get("label"): t for t in (gf.get("tools") or [])}
    got["gl_blunt"] = _num((tools.get("handle") or {}).get("power"))
    got["gl_cut"] = _num((tools.get("edge") or {}).get("power"))
    got["gl_cooldown"] = _num((tools.get("handle") or {}).get("cooldownTime"))
    got["gl_dps"] = melee_dps(gf.get("tools") or [])
    got["gl_bluntAP"] = tool_ap(tools.get("handle") or {})

    for k, want in CALIB_MATCH.items():
        have = got.get(k)
        if have is None or abs(have - want) > max(0.011, abs(want) * 0.001):
            bad.append("%s: this stack says %s, published vanilla says %s — a MATCH was "
                       "expected" % (k, have, want))
    for k, want in CALIB_PATCHED.items():
        have = got.get(k)
        if have is None or abs(have - want) > 0.005:
            bad.append("%s: this stack says %s, but a mod in the 595 should make it %s "
                       "(Yayo's Combat 3, patch_weapon.xml; vanilla would DERIVE 0.165). "
                       "Either that patch stopped applying or the decode is wrong"
                       % (k, have, want))

    f_dps = melee_dps(CALIB_FORMULA_TOOLS)
    if f_dps is None or abs(f_dps - CALIB_FORMULA_DPS) > 0.011:
        bad.append("melee DPS formula regression: 9/15/15 @2.0s should return %.2f "
                   "(an independently published figure) and returned %r"
                   % (CALIB_FORMULA_DPS, f_dps))
    return bad


# ═════════════════════════════════════════════════════════ engine formulas
def ranged_dps(dmg, burst, warmup, cooldown, ticks_between):
    """damage x burst / (warmup + cooldown + (burst-1) x ticksBetween / 60).

    Reproduces the RimWorld wiki's own assault-rifle DPS (10.88) exactly. It is
    a SUSTAINED single-target figure: it ignores accuracy, armour, cover, the
    wielder's skill and — for an explosive — everything the blast hits.
    """
    if dmg is None or not burst or cooldown is None:
        return None
    warmup = warmup or 0.0
    gap = ((burst - 1) * (ticks_between or 0)) / 60.0
    cycle = warmup + cooldown + gap
    if cycle <= 0:
        return None
    return (dmg * burst) / cycle


def tool_ap(tool):
    """A tool's armour penetration, with the engine's derivation for a -1.

    VerbProperties.AdjustedArmorPenetration: `if (num < 0f) num = damage * 0.015f`.
    Reading the declared -1 as "no penetration" would print 0% on most of the
    melee list, which is the confident wrong number this file exists to avoid.
    """
    ap = _num(tool.get("armorPenetration"))
    p = _num(tool.get("power"))
    if ap is None or ap < 0:
        return None if p is None else p * 0.015
    return ap


def _tool_weight(tool):
    """StatWorker_MeleeAverageDPS's weighting: power^2 x chanceFactor.

    (commonality is a VerbProperties field and is 1 for every tool-derived verb;
    it is folded in as 1 rather than invented.)"""
    p = _num(tool.get("power")) or 0.0
    return (p * p) * (_num(tool.get("chanceFactor"), 1.0) or 0.0)


def melee_dps(tools):
    """weightedAvg(power) / weightedAvg(cooldown) — the engine's own shape.

    ⚠️ NOT the average of per-tool DPS. They agree only when every cooldown is
    equal, and disagree on every weapon with a fast jab and a slow swing.
    """
    tools = [t for t in (tools or []) if _num(t.get("power")) is not None]
    w = sum(_tool_weight(t) for t in tools)
    if not tools or w <= 0:
        return None
    dmg = sum(_tool_weight(t) * (_num(t.get("power")) or 0.0) for t in tools) / w
    cd = sum(_tool_weight(t) * (_num(t.get("cooldownTime"), 0.0) or 0.0)
             for t in tools) / w
    if cd <= 0:
        return None
    return dmg / cd


def melee_ap(tools):
    """Selection-weighted average armour penetration, engine weighting."""
    tools = [t for t in (tools or []) if tool_ap(t) is not None]
    w = sum(_tool_weight(t) for t in tools)
    if not tools or w <= 0:
        return None
    return sum(_tool_weight(t) * tool_ap(t) for t in tools) / w


def projectile_ap(pj, dmgdef):
    """ProjectileProperties.GetArmorPenetration, transcribed.

    Order matters and each branch is a real case in this stack:
      no armour category at all (EMP, Stun, Smoke) -> 0, genuinely;
      an explicit armorPenetrationBase           -> that;
      otherwise the damageDef's default;
      a negative anywhere                        -> damage x 0.015.
    """
    if not pj:
        return None
    if dmgdef is not None and not (dmgdef.get("armorCategory")):
        return 0.0
    ap = _num(pj.get("armorPenetrationBase"))
    dmg = _num(pj.get("damageAmountBase"))
    if not (dmg is not None and dmg != -1) and (ap is None or ap < 0):
        ap = _num((dmgdef or {}).get("defaultArmorPenetration"))
    if ap is None or ap < 0:
        return None if dmg is None else max(0.0, dmg) * 0.015
    return ap


# ═════════════════════════════════════════════════════════════ stage: data
def _def(db, name):
    if not name:
        return None
    r = db.execute("select json from defs where def_type='ThingDef' and def_name=?",
                   (name,)).fetchone()
    return json.loads(r[0]) if r else None


def _stats(f):
    return {s.get("stat"): _num(s.get("value")) for s in (f.get("statBases") or [])}


def _primary_verb(f):
    verbs = [v for v in (f.get("verbs") or []) if v.get("ai_IsWeapon")]
    if not verbs:
        verbs = list(f.get("verbs") or [])
    if not verbs:
        return None
    for v in verbs:
        if v.get("isPrimary"):
            return v
    return verbs[0]


def _damage_defs(db):
    out = {}
    for dn, j in db.execute("select def_name, json from defs where def_type='DamageDef'"):
        f = json.loads(j).get("fields") or {}
        out[dn] = {"label": f.get("label") or dn,
                   "armorCategory": f.get("armorCategory"),
                   "defaultArmorPenetration": _num(f.get("defaultArmorPenetration")),
                   "defaultDamage": _num(f.get("defaultDamage")),
                   "harmsHealth": f.get("harmsHealth")}
    return out


def _projectiles(db):
    out = {}
    for dn, j in db.execute("select def_name, json from defs where def_type='ThingDef'"):
        f = json.loads(j).get("fields") or {}
        if f.get("projectile"):
            out[dn] = f["projectile"]
    return out


def _pawnkind_tag_index(db):
    """{weaponTag: [pawnKind label]} — the answer to "who can carry this".

    🔑 This is the ONLY route from a weapon to the pawns that spawn holding it,
    and it is why an empty `weaponTags` list is a finding rather than a blank:
    a weapon no tag reaches is craft-only or quest-only, and no raider will ever
    arrive with one.
    """
    idx = {}
    n = 0
    for dn, j in db.execute("select def_name, json from defs where def_type='PawnKindDef'"):
        f = json.loads(j).get("fields") or {}
        tags = f.get("weaponTags") or []
        if not tags:
            continue
        n += 1
        label = f.get("label") or dn
        for t in tags:
            idx.setdefault(t, []).append(label)
    for v in idx.values():
        v.sort()
    return idx, n


def _research_label(db):
    out = {}
    for dn, j in db.execute(
            "select def_name, json from defs where def_type='ResearchProjectDef'"):
        f = json.loads(j).get("fields") or {}
        out[dn] = f.get("label") or dn
    return out


def _cluster_of(row):
    """Six buckets, decided from measured data, not from a name where possible.

    ranged: explosive first (a blast radius changes what the weapon IS), then
            ENERGY — driven by the damageDef's own `armorCategory == Heat`,
            which is how the engine itself separates a blaster bolt from a
            bullet — then ballistic.
    melee:  by the capacity of the STRONGEST tool. Natural body parts are pulled
            out first: no recipe, no cost, and a label that names a body part.
    """
    inferred = False
    if row["kind"] == "ranged":
        if row.get("explosionRadius"):
            return "explosive", False
        if (row.get("flyOverhead")):
            return "explosive", False
        dd = row.get("damageArmorCategory")
        dname = (row.get("damageDefName") or "") + " " + (row.get("damageLabel") or "")
        if dd == "Heat":
            return "ranged-energy", False
        if (row.get("verbClass") or "").lower().find("beam") >= 0:
            return "ranged-energy", False
        if any(w in dname.lower() for w in ENERGY_WORDS):
            return "ranged-energy", True
        if dd in ("Sharp", "Blunt"):
            return "ranged-ballistic", False
        if row.get("damageDefName") is None:
            # No projectile at all: a spray, a beam, a C#-driven verb. Its damage
            # is UNMEASURED, so the cluster is a guess and says so.
            return "ranged-energy", True
        return "ranged-ballistic", True

    if row.get("natural"):
        return "natural / other", row.get("naturalInferred", True)
    cap = row.get("topCapacity")
    if cap in BLADE_CAPS:
        return "melee-blade", False
    if cap in BLUNT_CAPS:
        return "melee-blunt", False
    if cap:
        low = cap.lower()
        if any(w in low for w in ("cut", "stab", "slash", "sword", "saber", "sabre",
                                 "pierce", "lacerate", "scalpel", "sear", "plasma")):
            return "melee-blade", True
        if any(w in low for w in ("blunt", "smash", "crush", "hammer", "thump",
                                 "demolish")):
            return "melee-blunt", True
    return "natural / other", True


def _role(row):
    """What the weapon is FOR, in <= 20 words, from the data — never the label.

    "A label is not a decision aid" (review-sheets rule 2). A weapon's role is
    its reach, its rate and what it beats: that is what decides whether the
    campaign needs another one.
    """
    bits = []
    if row["kind"] == "ranged":
        rng = row.get("range")
        band = ("point-blank" if (rng or 0) < 12 else
                "mid-range" if (rng or 0) < 26 else
                "long-range" if (rng or 0) < 40 else "very long range")
        if row.get("explosionRadius"):
            bits.append("%s explosive, %.1f-cell blast" % (band, row["explosionRadius"]))
        elif (row.get("burst") or 1) > 1:
            bits.append("%s, %d-round burst" % (band, int(row["burst"])))
        else:
            bits.append("%s single shot" % band)
        if row.get("dps") is not None:
            bits.append("DPS %.1f" % row["dps"])
        else:
            bits.append("DPS UNMEASURED")
        if row.get("oneUse"):
            bits.append("one use then gone")
        if row.get("isTurretGun"):
            bits.append("turret mount only")
    else:
        if row.get("dps") is not None:
            bits.append("melee, DPS %.1f" % row["dps"])
        else:
            bits.append("melee, DPS UNMEASURED")
        if row.get("topCapacity"):
            bits.append("mostly %s" % row["topCapacity"].lower())
        if row.get("stuffable"):
            bits.append("made of any %s" % "/".join(row.get("stuffCategories") or []))
        if row.get("natural"):
            bits.append("a body part, not a made object")
    if row.get("ap") is not None and row["ap"] >= 0.5:
        bits.append("cuts armour")
    return "; ".join(bits)[:160]


def build_rows():
    meta = dump_fingerprint()
    db = sqlite3.connect(DB)
    cuts = cherrypicker.load()
    meta["cutProvenance"] = cuts.provenance()

    bad = calibrate(db)
    if bad:
        db.close()
        die("CALIBRATION FAILED — refusing to emit numbers nobody checked:\n  "
            + "\n  ".join(bad))
    meta["calibration"] = ("PASSED — 13 assault-rifle/gladius readings match published "
                           "vanilla, the one modded divergence (assault-rifle AP 19% from "
                           "Yayo's Combat 3 vs vanilla's derived 16.5%) is exactly where expected, and the "
                           "melee-DPS formula reproduces an independently published 7.04")

    dmgdefs = _damage_defs(db)
    projs = _projectiles(db)
    kindidx, n_kinds = _pawnkind_tag_index(db)
    research = _research_label(db)
    meta["pawnKindsWithWeaponTags"] = n_kinds

    rows = []
    n_noname = 0
    for dn, pid, modname, j in db.execute(
            "select def_name, package_id, mod_name, json from defs where def_type='ThingDef'"):
        d = json.loads(j)
        isd = d.get("is") or {}
        if not isd.get("weapon"):
            continue
        if not dn:
            # 🪤 An abstract parent has no defName, declares no art, and cannot be
            # cut — offering one for review wastes the owner's time.
            n_noname += 1
            continue
        rows.append(_row(d, dn, pid, modname, isd, dmgdefs, projs, kindidx, research, cuts))
    db.close()
    meta["abstractRowsDropped"] = n_noname
    meta["builtUtc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return rows, meta


def _row(d, dn, pid, modname, isd, dmgdefs, projs, kindidx, research, cuts):
    f = d["fields"]
    stats = _stats(f)
    tools = f.get("tools") or []
    v = _primary_verb(f)
    ranged = bool(isd.get("rangedWeapon"))

    gd = f.get("graphicData") or {}
    ds = _vec(gd.get("drawSize"))
    tags = list(f.get("weaponTags") or [])
    classes = list(f.get("weaponClasses") or [])

    r = {
        "defName": dn, "label": f.get("label") or dn, "desc": f.get("description"),
        "mod": modname or pid, "packageId": pid,
        "kind": "ranged" if ranged else "melee",
        "cut": bool(cuts.cut("ThingDef", dn)),
        "texPath": gd.get("texPath"), "graphicClass": gd.get("graphicClass"),
        "drawSize": [ds[0], ds[1]],
        "techLevel": f.get("techLevel"),
        "weaponTags": tags, "weaponClasses": classes,
        "isTurretGun": KNOWN_TURRET_TAG in tags,
        "mass": stats.get("Mass"),
        "workToMake": stats.get("WorkToMake"),
        "stuffable": bool(f.get("stuffCategories")),
        "stuffCategories": list(f.get("stuffCategories") or []),
        "costStuffCount": _num(f.get("costStuffCount")),
        "costList": ["%s x%s" % (c.get("thingDef"), c.get("count"))
                     for c in (f.get("costList") or [])],
        "verbClass": (v or {}).get("verbClass"),
    }

    # ── who can carry it
    carriers = sorted({k for t in tags for k in kindidx.get(t, [])})
    r["carriers"] = carriers[:8]
    r["carrierCount"] = len(carriers)

    # ── recipe / research
    rm = f.get("recipeMaker") or {}
    prereqs = []
    if rm.get("researchPrerequisite"):
        prereqs.append(rm["researchPrerequisite"])
    prereqs += [p for p in (rm.get("researchPrerequisites") or []) if p]
    r["research"] = [research.get(p, p) for p in prereqs]
    r["craftable"] = bool(rm)
    skills = rm.get("skillRequirements") or []
    r["craftSkill"] = "; ".join("%s %s" % (s.get("skill"), s.get("minLevel"))
                                for s in skills) or None

    if ranged:
        _ranged_fields(r, f, v, stats, dmgdefs, projs)
    else:
        _melee_fields(r, f, tools, dmgdefs)

    grp, inferred = _cluster_of(r)
    r["group"] = grp
    r["clusterInferred"] = inferred
    r["role"] = _role(r)
    r["registerRisk"] = _register_risk(r)
    return r


def _ranged_fields(r, f, v, stats, dmgdefs, projs):
    v = v or {}
    pjname = v.get("defaultProjectile")
    pj = projs.get(pjname) if pjname else None
    dd = dmgdefs.get((pj or {}).get("damageDef")) if pj else None

    r["projectile"] = pjname
    r["damage"] = _num((pj or {}).get("damageAmountBase")) if pj else None
    if r["damage"] is not None and r["damage"] < 0:
        r["damage"] = (dd or {}).get("defaultDamage")
        if r["damage"] is not None and r["damage"] < 0:
            r["damage"] = None
    r["damageDefName"] = (pj or {}).get("damageDef")
    r["damageLabel"] = (dd or {}).get("label")
    r["damageArmorCategory"] = (dd or {}).get("armorCategory")
    r["ap"] = projectile_ap(pj, dd)
    r["apDerived"] = bool(pj and (_num(pj.get("armorPenetrationBase")) or -1) < 0)
    r["range"] = _num(v.get("range"))
    r["minRange"] = _num(v.get("minRange"))
    r["warmup"] = _num(v.get("warmupTime"))
    r["cooldown"] = stats.get("RangedWeapon_Cooldown")
    if r["cooldown"] is None:
        r["cooldown"] = _num(v.get("defaultCooldownTime"))
    r["burst"] = _num(v.get("burstShotCount"), 1.0)
    r["ticksBetween"] = _num(v.get("ticksBetweenBurstShots"))
    r["explosionRadius"] = _num((pj or {}).get("explosionRadius")) or None
    r["flyOverhead"] = bool((pj or {}).get("flyOverhead"))
    r["oneUse"] = "OneUse" in (v.get("verbClass") or "")
    r["accuracy"] = {k: stats.get("Accuracy" + k)
                     for k in ("Touch", "Short", "Medium", "Long")}
    r["dps"] = ranged_dps(r["damage"], r["burst"], r["warmup"], r["cooldown"],
                          r["ticksBetween"])
    # 🔴 THREE WAYS A RANGED DPS IS A CONFIDENT WRONG NUMBER, all measured on this
    # stack, all refused rather than printed:
    r["dpsNote"] = None
    harms = (dd or {}).get("harmsHealth")
    if pj is not None and harms is False:
        # A firefoam turret declares damageAmountBase 9999 of `Extinguish`, which
        # harms nothing. Straight arithmetic gave it 286,017 DPS and put it at the
        # top of the ballistic ladder.
        r["dps"] = None
        r["dpsNote"] = ("its damage type (%s) does not harm health — the %s figure the "
                        "def carries is a mechanic, not damage, so there is no DPS"
                        % (r.get("damageLabel") or r.get("damageDefName"),
                           _fmt(r.get("damage"))))
    elif not r["cooldown"]:
        # A turret gun often declares no RangedWeapon_Cooldown at all: the real
        # fire rate is `turretBurstCooldownTime` on the turret BUILDING
        # (Building_TurretGun.cs:478), which is not a weapon def and is out of
        # this sheet's scope. Dividing by the missing cooldown gave the mass
        # driver 14,193 DPS.
        r["dps"] = None
        r["dpsNote"] = ("the gun declares no cooldown — for a turret the real fire rate "
                        "is turretBurstCooldownTime on the turret BUILDING, which is not "
                        "a weapon def, so DPS is UNMEASURED rather than divided by zero")
    elif r["explosionRadius"]:
        r["dpsNote"] = ("single-target only — the blast is what this weapon is for "
                        "and no DPS number sees it")
    elif r["dps"] is None:
        r["dpsNote"] = ("no projectile on the primary verb (%s) — the damage lives in "
                        "C# and cannot be read off the def"
                        % (r.get("verbClass") or "unknown verb"))
    elif r.get("isTurretGun"):
        r["dpsNote"] = ("this is the GUN's own cooldown; a turret building carrying it "
                        "may override the rate with turretBurstCooldownTime")
    # the melee side of a gun (stock/barrel bash) — real, and worth one line
    r["meleeFallbackDps"] = melee_dps(f.get("tools") or [])


def _melee_fields(r, f, tools, dmgdefs):
    r["dps"] = melee_dps(tools)
    r["ap"] = melee_ap(tools)
    r["apDerived"] = any((_num(t.get("armorPenetration")) or -1) < 0 for t in tools)
    best = None
    for t in tools:
        p = _num(t.get("power"))
        if p is not None and (best is None or p > (_num(best.get("power")) or 0)):
            best = t
    r["damage"] = _num((best or {}).get("power"))
    r["cooldown"] = _num((best or {}).get("cooldownTime"))
    caps = (best or {}).get("capacities") or []
    r["topCapacity"] = caps[0] if caps else None
    r["toolLines"] = ["%s (%s) %s dmg · %ss · AP %s"
                      % (t.get("label") or "?",
                         ", ".join(t.get("capacities") or []) or "?",
                         _fmt(_num(t.get("power"))), _fmt(_num(t.get("cooldownTime"))),
                         _pct(tool_ap(t)))
                      for t in tools]
    r["damageLabel"] = (r["topCapacity"] or "").lower() or None
    r["damageDefName"] = None
    r["damageArmorCategory"] = ("Sharp" if r["topCapacity"] in ("Cut", "Stab", "Poke",
                                                               "Scratch")
                                else "Blunt" if r["topCapacity"] in BLUNT_CAPS else None)
    r["range"] = None
    r["burst"] = None
    r["accuracy"] = {}
    r["dpsNote"] = (None if r["dps"] is not None else
                    "no tools with a power value — this weapon's damage is not in the def")
    # natural-part test: no recipe, no cost, and the label names a body part.
    label = (r.get("label") or "").lower()
    named = any(w in label for w in NATURAL_WORDS)
    unmade = not r.get("craftable") and not r.get("costList") and not r.get("stuffable")
    r["natural"] = bool(named and unmade)
    r["naturalInferred"] = bool(named and not unmade)


def _register_risk(r):
    """LEXICAL Star-Wars-register test. It reads the LABEL. It cannot see art.

    Every row it fires on is contested and says why, because "recognisably from
    Earth" is the owner's call and a word list is at best a shortlist for it.
    """
    hay = (" %s " % (r.get("label") or "")).lower()
    for w in EARTH_WORDS:
        if w in hay:
            return w.strip()
    return None


# ═════════════════════════════════════════════════════════════ stage: art
def _texture_index(rebuild=False):
    """The loose-PNG index, cached — and SAMPLED, because a cached absolute path
    is a claim about a disk that keeps moving (Steam re-downloads a mod and the
    paths are simply gone, with nothing erroring)."""
    os.makedirs(os.path.dirname(TEXCACHE), exist_ok=True)
    if not rebuild and os.path.isfile(TEXCACHE):
        try:
            with open(TEXCACHE, encoding="utf-8") as fh:
                raw = json.load(fh)
            idx = ACS.TextureIndex()
            idx.update(raw["index"])
            import random
            keys = list(idx)
            probe = random.Random(1701).sample(keys, min(300, len(keys)))
            gone = sum(1 for k in probe if not os.path.isfile(idx[k]))
            if gone <= 1:
                return idx
            print("  texture cache is STALE (%d/%d sampled paths are gone). Rebuilding."
                  % (gone, len(probe)))
        except (OSError, ValueError, KeyError):
            pass
    mods, missing, ver = LS.build_load_set(
        GP.MODS_CONFIG, [GP.WORKSHOP, GP.LOCAL_MODS, GP.GAME_DATA])
    idx, nfiles, nroots = ACS.build_texture_index(mods)
    with open(TEXCACHE, "w", encoding="utf-8") as fh:
        json.dump({"index": dict(idx)}, fh)
    print("  texture index: %d loose PNGs in %d roots -> %d paths (%d mods, v%s)"
          % (nfiles, nroots, len(idx), len(mods), ver))
    return idx


def _resolve(r, idx, dirs, bundles):
    """thing_contact_sheet's resolver, run BARE-FIRST for items."""
    old_t, old_b = ACS.TEX_SUFFIXES, ACS.BUNDLE_SUFFIXES
    ACS.TEX_SUFFIXES, ACS.BUNDLE_SUFFIXES = BARE_FIRST, BARE_FIRST_BUNDLE
    try:
        gc = (r.get("graphicClass") or "").rsplit(".", 1)[-1]
        hit, rung = TCS.resolve_thing_texture(r.get("texPath"), gc, idx, dirs,
                                              bundles, own_pkg=r.get("packageId"))
    finally:
        ACS.TEX_SUFFIXES, ACS.BUNDLE_SUFFIXES = old_t, old_b
    return hit, rung


def render_cells(r):
    """What the game draws in a pawn's hands, in cells: max(drawSize)."""
    ds = r.get("drawSize") or [None, None]
    d = max(ds[0] or 0, ds[1] or 0)
    return float(d) if d else None


def generate_px(r):
    """The settled resolution rule (design/Jawa/worldbuilding/creature_size_model.md):
    clamp(ceil_pow2(max(drawSize) x 128), 256, 1024). Floor 256 is the owner's
    'prefer higher when uncertain' tiebreak."""
    cells = render_cells(r)
    if not cells:
        return None
    want = cells * 128.0
    px = 256
    while px < want and px < 1024:
        px *= 2
    return max(256, min(1024, px))


def render_art(rows):
    from PIL import Image, ImageDraw

    os.makedirs(ART_DIR, exist_ok=True)
    gi = os.path.join(ART_DIR, ".gitignore")
    if not os.path.isfile(gi):
        with open(gi, "w", encoding="utf-8") as fh:
            fh.write("# Derived art for weapon_register.html — regenerate with\n"
                     "# python3 src/RimMandrake/Utils/gen_weapon_register.py --stage art\n*\n")

    idx = _texture_index()
    dirs = TCS.build_dir_index(idx)
    bundles, _n = ACS.load_bundle_index()

    human = None
    try:
        human = Image.open(HUMAN_ANCHOR).convert("RGBA")
    except Exception:                                       # noqa: BLE001
        print("  ⚠ no human anchor at %s — the scale panel will draw a crude outline "
              "instead, and its absence is meant to be obvious" % HUMAN_ANCHOR)

    stats = {"placed": 0, "missing": 0, "blank": 0, "capped": 0}
    for r in rows:
        base = os.path.join(ART_DIR, re.sub(r"[^A-Za-z0-9_.-]", "_", r["defName"]))
        r["art"] = {"scale": None, "detail": None, "reason": None, "rung": None,
                    "srcPx": None, "pxPerCell": None, "shownPct": 100}
        if not r.get("texPath"):
            r["art"]["reason"] = "no_texPath"
            stats["missing"] += 1
            continue
        src, rung = _resolve(r, idx, dirs, bundles)
        if not src:
            r["art"]["reason"] = "not_found"
            stats["missing"] += 1
            continue
        r["art"]["rung"] = rung
        # 🔴 A BLANK-RATE METRIC CANNOT DETECT A WRONG PICTURE. Keeping the source
        # path is what makes the identity check possible: several defs that should
        # look different must resolve to DIFFERENT files, each under their own mod.
        r["art"]["src"] = src
        try:
            im = Image.open(src).convert("RGBA")
        except Exception as exc:                            # noqa: BLE001
            r["art"]["reason"] = "unreadable: %s" % exc
            stats["missing"] += 1
            continue
        bbox = im.getbbox()
        if not bbox:
            # A fully transparent PNG is NOT missing art; it is usually the wrong
            # variant, and calling it missing hides a resolver bug.
            r["art"]["reason"] = "blank_png"
            stats["blank"] += 1
            continue
        im = im.crop(bbox)
        r["art"]["srcPx"] = [im.width, im.height]

        det = _fit(im, DETAIL_BOX, DETAIL_BOX, Image)
        canvas = _checker(DETAIL_BOX, DETAIL_BOX, Image, ImageDraw)
        canvas.alpha_composite(det, ((DETAIL_BOX - det.width) // 2,
                                     (DETAIL_BOX - det.height) // 2))
        canvas.convert("RGB").save(base + ".detail.png", optimize=True)
        r["art"]["detail"] = "weapon_art/" + os.path.basename(base) + ".detail.png"

        cells = render_cells(r)
        if cells:
            draw_px = max(8.0, cells * PX_PER_CELL)
            r["art"]["pxPerCell"] = round(max(im.width, im.height)
                                          / (draw_px / (PX_PER_CELL / 64.0)), 3)
            panel = _scale_panel(im, cells, human, Image, ImageDraw)
            shown = 100
            if max(panel.size) > SCALE_CAP:
                k = SCALE_CAP / float(max(panel.size))
                panel = panel.resize((max(1, int(panel.width * k)),
                                      max(1, int(panel.height * k))), Image.LANCZOS)
                shown = int(round(k * 100))
                stats["capped"] += 1
            r["art"]["shownPct"] = shown
            panel.convert("RGB").save(base + ".scale.png", optimize=True)
            r["art"]["scale"] = "weapon_art/" + os.path.basename(base) + ".scale.png"
        stats["placed"] += 1
    return stats


def _fit(im, bw, bh, Image, max_upscale=4.0):
    k = min(bw / float(im.width), bh / float(im.height))
    k = min(k, max_upscale)
    w, h = max(1, int(im.width * k)), max(1, int(im.height * k))
    return im.resize((w, h), Image.NEAREST if k > 1 else Image.LANCZOS)


def _checker(w, h, Image, ImageDraw, sq=12):
    im = Image.new("RGBA", (w, h), (26, 29, 34, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, sq):
        for x in range(0, w, sq):
            if ((x // sq) + (y // sq)) % 2:
                d.rectangle([x, y, x + sq - 1, y + sq - 1], fill=(42, 47, 55, 255))
    return im


def _human_figure(hh, Image, ImageDraw, human):
    if human is not None:
        k = hh / float(human.height)
        return human.resize((max(1, int(human.width * k)), hh), Image.LANCZOS)
    fig = Image.new("RGBA", (max(6, int(hh * 0.45)), hh), (0, 0, 0, 0))
    ImageDraw.Draw(fig).rectangle([0, 0, fig.width - 1, hh - 1],
                                  outline=(255, 80, 80, 255))
    return fig


def _scale_panel(im, cells, human, Image, ImageDraw):
    """The weapon at true in-hand size beside a real colonist, on a 1-cell grid.

    The sprite is CONTAIN-fitted into a cells x cells box preserving its native
    aspect — never stretched, which turns a long thin rifle into a blob.
    """
    box = max(8, int(round(cells * PX_PER_CELL)))
    hh = int(round(HUMAN_CELLS * PX_PER_CELL))
    k = min(box / float(im.width), box / float(im.height))
    cw, ch = max(1, int(round(im.width * k))), max(1, int(round(im.height * k)))
    fig = _human_figure(hh, Image, ImageDraw, human)
    gap, pad = 18, 10
    tw = pad + fig.width + gap + cw + pad
    th = pad + max(hh, ch) + pad
    panel = Image.new("RGBA", (tw, th), (18, 21, 26, 255))
    d = ImageDraw.Draw(panel)
    for x in range(pad, tw, PX_PER_CELL):
        d.line([(x, 0), (x, th)], fill=(34, 39, 47, 255))
    for y in range(th - pad, -1, -PX_PER_CELL):
        d.line([(0, y), (tw, y)], fill=(34, 39, 47, 255))
    base_y = th - pad
    panel.alpha_composite(fig, (pad, base_y - fig.height))
    wep = im.resize((cw, ch), Image.LANCZOS if im.width > cw else Image.NEAREST)
    panel.alpha_composite(wep, (pad + fig.width + gap, base_y - ch))
    return panel


# ═══════════════════════════════════════════════════════ clustering + prefill
def cluster(rows):
    """Cluster order is fixed; inside a cluster, STRONGEST FIRST so the power
    ladder is visible in one scroll. A row with no DPS sorts last, not as zero —
    an unmeasured weapon is not a weak one."""
    order = {c: i for i, c in enumerate(CLUSTERS)}
    rows.sort(key=lambda r: (order.get(r["group"], 99),
                             0 if r.get("dps") is not None else 1,
                             -(r.get("dps") or 0.0),
                             -(r.get("damage") or 0.0),
                             r["defName"]))
    return rows


def prefill_of(r):
    """(decision, priority, contested, why) — ART at display size, plus a NAME test.

    ⭐ THE CRITERION, and its limit. What is measurable offline is how the
    shipping sprite holds up at the size the engine actually draws it:

        pxPerCell = longest source edge / (max(drawSize) x 64)

    Below 1.0 the game upscales the art; below 0.5 it is stretched over 2x and
    reads blurry on screen. That RANKS QUALITY.

    🔴 IT CANNOT RANK WORTH. Whether a weapon BELONGS on Ash'karr — scavenged,
    ion, salvage-built, blaster-adjacent — is a judgement about the picture and
    the fiction, and no number here sees either. The one gesture this function
    makes at it is LEXICAL: a label containing a modern-Earth firearm name is
    flagged CONTESTED with the word that fired, because that shortlist is worth
    the owner's eye. It is not a finding.
    """
    a = r.get("art") or {}
    ppc = a.get("pxPerCell")
    live = not r.get("cut")

    if r.get("cut"):
        return ("keep", "", False,
                "already cut from the game — its art cannot be seen, so there is nothing "
                "to spend on it. Flip to 'restore' in the note if you want it back")
    # 🪤 A DELIBERATELY INVISIBLE WEAPON IS NOT MISSING ART. Eight rows here point at
    # `Things/Empty`, `Misc/Blank`, `DummyWeapon` or an `_Invisible` pawn texture:
    # they are internal guns behind a creature's breath attack or a column effect,
    # and "regenerate" would be an instruction to draw something the mod
    # deliberately does not draw.
    tp = (r.get("texPath") or "").lower()
    if any(w in tp for w in ("empty", "blank", "invisible", "dummy", "transparent")):
        return ("keep", "", False,
                "its texPath IS a blank sprite (%s) — this weapon is meant to be "
                "invisible (an internal gun behind an effect), so there is no art to "
                "judge" % r.get("texPath"))
    if a.get("reason") == "no_texPath":
        return ("keep", "", True,
                "the def declares no graphicData at all. That is normal for a fake gun "
                "the game never draws, and a defect for anything a pawn holds — worth "
                "one look, not an art job")
    if a.get("reason") in ("not_found", "blank_png") or not a.get("detail"):
        return ("regen", "A" if live else "C", True,
                "no file matches the def's texPath on disk today (%s) — either the art "
                "was never shipped, or the MOD changed after the def dump was taken. "
                "Check the mod's own defs before drawing anything"
                % (a.get("reason") or "?"))
    if r.get("registerRisk"):
        return ("regen", "B", True,
                "the LABEL contains \u201c%s\u201d, which reads as modern Earth rather "
                "than Star Wars. This is a word test, not an art judgement — look at the "
                "sprite and overrule it freely" % r["registerRisk"])
    if ppc is not None and ppc < PPC_BAD:
        return ("rescale", "A" if live else "B", False,
                "art is stretched over 2x at its drawn size (%.2f px per cell) — soft on "
                "screen in a pawn's hands" % ppc)
    if ppc is not None and ppc < PPC_SOFT:
        return ("regen", "B" if live else "C", True,
                "art is upscaled at its drawn size (%.2f px per cell) — borderline, "
                "judge by eye" % ppc)
    if a.get("rung") and a["rung"].startswith("<dir:"):
        return ("keep", "", True,
                "this def's texPath names a FOLDER and the picture is one of several "
                "variants — the sprite you are judging may not be the one you get")
    return ("keep", "", False, "")


# ═════════════════════════════════════════════════════════════ stage: sheet
def _effect(r):
    """The consequence line — and the sheet's FILTER VOCABULARY.

    ⭐ The template's search box matches id + label + effect + group, so stable
    ALL-CAPS tokens here give every axis its own filter without touching a line
    of the skill's chrome: CUT · MISSING-ART · SOFT-ART · ORPHAN-TAGS ·
    REGISTER-RISK · TURRET-GUN · STUFFABLE · EXPLOSIVE · ONE-USE ·
    UNMEASURED · NATURAL-PART · UNCLASSIFIED-MELEE.
    """
    toks = []
    if r.get("cut"):
        toks.append("CUT")
    if not (r.get("art") or {}).get("detail"):
        toks.append("MISSING-ART")
    ppc = (r.get("art") or {}).get("pxPerCell")
    if ppc is not None and ppc < PPC_SOFT:
        toks.append("SOFT-ART")
    if not r.get("weaponTags") and not r.get("cut"):
        toks.append("ORPHAN-TAGS")
    if r.get("registerRisk"):
        toks.append("REGISTER-RISK")
    if r.get("isTurretGun"):
        toks.append("TURRET-GUN")
    if r.get("stuffable"):
        toks.append("STUFFABLE")
    if r.get("explosionRadius"):
        toks.append("EXPLOSIVE")
    if r.get("oneUse"):
        toks.append("ONE-USE")
    if r.get("dps") is None or r.get("damage") is None:
        toks.append("UNMEASURED")
    if r.get("clusterInferred"):
        toks.append("CLUSTER-INFERRED")
    if r["group"] == "natural / other":
        toks.append("NATURAL-PART" if r.get("natural") else "UNCLASSIFIED-MELEE")
    role = r.get("role") or ""
    return (role + ("  ·  " + " ".join(toks) if toks else "")).strip()


def _cost(r):
    bits = []
    if r.get("costStuffCount"):
        bits.append("%d of %s" % (r["costStuffCount"],
                                  "/".join(r.get("stuffCategories") or ["stuff"])))
    bits += r.get("costList") or []
    if not bits:
        return "not craftable — found, traded or spawned only" if not r.get("craftable") \
            else "UNMEASURED"
    out = " + ".join(bits)
    if r.get("workToMake"):
        out += "  ·  work %s" % _fmt(r["workToMake"])
    else:
        out += "  ·  work UNMEASURED"
    if r.get("craftSkill"):
        out += "  ·  needs %s" % r["craftSkill"]
    return out


def _accuracy(r):
    a = r.get("accuracy") or {}
    if not any(v is not None for v in a.values()):
        return None
    return "touch %s · short %s · medium %s · long %s" % (
        _pct(a.get("Touch")), _pct(a.get("Short")),
        _pct(a.get("Medium")), _pct(a.get("Long")))


def _carriers(r):
    if r.get("cut"):
        return "cut — nothing carries it"
    if not r.get("weaponTags"):
        return ("no weaponTags at all — NO pawn kind can roll this weapon; it reaches "
                "the game only by crafting, trade or a scripted spawn")
    if not r.get("carrierCount"):
        return ("tags %s, but no pawn kind in the stack asks for any of them — an "
                "orphaned tag" % ", ".join(r["weaponTags"][:4]))
    more = r["carrierCount"] - len(r["carriers"])
    return "%d pawn kind%s: %s%s" % (r["carrierCount"],
                                     "" if r["carrierCount"] == 1 else "s",
                                     ", ".join(r["carriers"]),
                                     " +%d more" % more if more > 0 else "")


def make_items(rows):
    items = []
    for r in rows:
        pre, prio, contested, why = prefill_of(r)
        a = r.get("art") or {}
        items.append({
            "id": r["defName"],
            "label": r["label"],
            "group": r["group"],
            "effect": _effect(r),
            "thumb": a.get("detail"),
            "prefill": pre,
            "prio": prio,
            "contested": contested,
            "inferred": bool(r.get("clusterInferred")),
            "cut": bool(r.get("cut")),
            "mod": r.get("mod"),
            "desc": r.get("desc"),
            "scale": a.get("scale"),
            "shownPct": a.get("shownPct"),
            "srcPx": a.get("srcPx"),
            "rung": a.get("rung"),
            "artReason": a.get("reason"),
            "pxPerCell": a.get("pxPerCell"),
            "role": r.get("role"),
            "kind": r.get("kind"),
            "damage": _fmt(r.get("damage")),
            "damageType": (r.get("damageLabel") or "UNMEASURED")
                          + (" (%s armour)" % r["damageArmorCategory"]
                             if r.get("damageArmorCategory") else ""),
            "ap": _pct(r.get("ap")) + (" (derived: damage x 0.015)"
                                       if r.get("apDerived") and r.get("ap") is not None
                                       else ""),
            "range": (_fmt(r.get("range"), 1) + " cells" if r.get("range") is not None
                      else ("melee" if r.get("kind") == "melee" else "UNMEASURED")),
            "warmupCooldown": "warmup %s s · cooldown %s s" % (
                _fmt(r.get("warmup"), 2), _fmt(r.get("cooldown"), 2)),
            "accuracy": _accuracy(r),
            "burst": (_fmt(r.get("burst")) + " shots"
                      + (" · %s ticks between" % _fmt(r.get("ticksBetween")))
                      if r.get("burst") and r["burst"] > 1 else
                      ("single shot" if r.get("kind") == "ranged" else None)),
            "dps": _fmt(r.get("dps"), 2),
            "dpsNote": r.get("dpsNote"),
            "meleeFallbackDps": (_fmt(r.get("meleeFallbackDps"), 2)
                                 if r.get("meleeFallbackDps") else None),
            "toolLines": r.get("toolLines") or [],
            "techLevel": r.get("techLevel") or "UNMEASURED",
            "cost": _cost(r),
            "stuffable": ("yes — %s (the row's damage is the UNSTUFFED base)"
                          % "/".join(r.get("stuffCategories") or [])
                          if r.get("stuffable") else "no"),
            "research": ", ".join(r.get("research") or []) or
                        ("none" if r.get("craftable") else "not craftable"),
            "tags": ", ".join(r.get("weaponTags") or []) or "(none)",
            "classes": ", ".join(r.get("weaponClasses") or []) or None,
            "carriers": _carriers(r),
            "regenPx": generate_px(r),
            "cells": render_cells(r),
            "registerRisk": r.get("registerRisk"),
            "why": why,
        })
    return items


def _native(p):
    try:
        import subprocess
        return subprocess.run(["wslpath", "-w", p], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                                       # noqa: BLE001
        return p


def _mask_comments(html):
    """Same-length copy with every HTML comment blanked, so offsets still line up.

    🪤 The template DOCUMENTS its own fill-in blocks inside a comment, and a
    tolerant regex will match the documentation instead of the real block, then
    eat everything up to the real closing tag. Nothing throws; the page is
    silently destroyed. check_sheet.py is what catches it.
    """
    return re.sub(r"<!--.*?-->", lambda m: " " * (m.end() - m.start()), html, flags=re.S)


def _replace_json(html, tag, obj):
    blob = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    blob = blob.replace("</", "<\\/")
    pat = re.compile(r'(<script\s+id="%s"\s+type="application/json"\s*>)(.*?)(</script>)'
                     % tag, re.S)
    m = pat.search(_mask_comments(html))
    if not m:
        die("the review-sheets template has no live %s block — it changed shape under "
            "us, or the only occurrence is inside a comment." % tag)
    return html[:m.start()] + m.group(1) + "\n" + blob + "\n" + m.group(3) + html[m.end():]


def _invented():
    return [
        "SCOPE. A \u201cweapon\u201d here is a ThingDef the running game reports as "
        "IsWeapon \u2014 category Item, and melee or ranged. That deliberately EXCLUDES "
        "130 other Item defs carrying weapon-ish verbs (psychic shock lances, orbital "
        "targeters, jump packs, shield belts): they are apparel and utility, not "
        "equipment a pawn wields. It deliberately INCLUDES the 62 defs tagged TurretGun, "
        "because a turret's gun IS a weapon def and its art is drawn on the map. Say the "
        "word and turret guns come out.",
        "TRUE IN-HAND SIZE = max(graphicData.drawSize) cells. This is not a model, it is "
        "the engine: Verse/PawnRenderUtility.cs::DrawEquipmentAiming builds the weapon's "
        "mesh with new Vector3(drawSize.x, 0, drawSize.y) and nothing else. There is no "
        "fitted constant anywhere in the scale panel.",
        "THE SCALE PANEL IS DRAWN AT 128 PX PER CELL, twice the creature register's 64. "
        "A one-cell weapon at 64 px is too small to judge on a web page. The human anchor "
        "is scaled by the SAME factor, so the ratio \u2014 the only thing the panel is "
        "for \u2014 is true. If you compare a weapon panel against a creature panel by "
        "eye, halve this one.",
        "THE HUMAN ANCHOR IS 1.5 CELLS TALL and is a real RimWorld colonist sprite. A "
        "vanilla humanlike body graphic is drawn at 1.5x1.5 world units; I did not find "
        "that stated in the defs, it is read across from the mechs and the 128 px body "
        "art. If it is wrong, every silhouette here is the wrong size and nothing else is.",
        "RANGED DPS = damage x burstShotCount / (warmupTime + RangedWeapon_Cooldown + "
        "(burst-1) x ticksBetweenBurstShots / 60). It reproduces the RimWorld wiki's own "
        "assault-rifle figure (10.88) to the digit. It is SUSTAINED SINGLE-TARGET damage "
        "and it ignores accuracy, armour, cover, range falloff, the wielder's Shooting "
        "skill, and \u2014 for anything explosive \u2014 everything the blast hits. Those "
        "rows say so on their own line.",
        "MELEE DPS = weightedAvg(tool power) / weightedAvg(tool cooldown), weighted by "
        "power\u00b2 x chanceFactor. That is RimWorld/StatWorker_MeleeAverageDPS.cs "
        "transcribed, not a convenience: it is avg(damage)/avg(cooldown), NOT the average "
        "of per-tool DPS, and the two disagree on every weapon with a fast jab and a slow "
        "swing. Proven by feeding it an independently published gladius (9/15/15 at 2.0s) "
        "and getting that source's printed 7.04 back.",
        "ARMOUR PENETRATION IS OFTEN DERIVED, NOT DECLARED. A tool or projectile that "
        "says -1 does not mean \u201cnone\u201d: the engine computes damage x 0.015 "
        "(VerbProperties.AdjustedArmorPenetration, ProjectileProperties."
        "GetArmorPenetration). Rows where that fired say \u201cderived\u201d. A damageDef "
        "with no armour category at all (EMP, Stun, Smoke) is a true 0%.",
        "EVERY NUMBER IS THE UNSTUFFED, NORMAL-QUALITY, NO-WIELDER BASE. A plasteel "
        "longsword hits harder than its row; a legendary anything hits harder than its "
        "row; a pawn with Melee 15 hits harder than its row. There is no resolved-stat "
        "capture for weapons the way animals.json exists for creatures, so nothing here "
        "was read out of a running game \u2014 it is the def, put through the engine's "
        "own arithmetic.",
        "CLUSTERING. Explosive wins first (a blast radius changes what a weapon IS), then "
        "ENERGY \u2014 decided by the damageDef's own armorCategory == Heat, which is how "
        "the engine itself separates a blaster bolt from a bullet \u2014 then ballistic. "
        "Melee splits on the capacity of the STRONGEST tool. Rows whose cluster came from "
        "a word rather than a field carry a CLUSTER-INFERRED token and can be filtered.",
        "NATURAL / OTHER means a melee weapon that is a BODY PART: no recipe, no cost, no "
        "stuff, and a label naming a tusk, horn, claw, fang, talon, sting, quill or the "
        "like. It is a two-part test and either half alone would be wrong \u2014 an "
        "uncraftable spacer sword is not a body part, and a mod's \u201cclaw blade\u201d "
        "may well be forged.",
        "REGISTER-RISK IS A WORD LIST, NOT AN ART JUDGEMENT. A label containing "
        "\u201cassault rifle\u201d, \u201cAK-47\u201d, \u201crevolver\u201d and 50-odd "
        "other modern-Earth firearm names is flagged contested and pre-filled REGENERATE. "
        "It cannot see the sprite, so it will flag a perfectly Star-Wars-looking gun with "
        "an unlucky name and miss a photorealistic M4 called a \u201cDL-44\u201d. It is a "
        "shortlist for your eye, and overruling it costs nothing.",
        "ORDER INSIDE A CLUSTER IS STRONGEST FIRST, by DPS then by damage, so the power "
        "ladder reads in one scroll. A row with no DPS sorts LAST, never as zero \u2014 "
        "an unmeasured weapon is not a weak one.",
        "REGENERATION RESOLUTION = clamp(ceil_pow2(max(drawSize) x 128), 256, 1024), the "
        "settled rule in design/Jawa/worldbuilding/creature_size_model.md, floor 256 "
        "because the owner prefers higher when uncertain.",
        "PRIORITY IS ONLY MEANINGFUL FOR REGENERATION. A/B/C is pre-filled on rows marked "
        "Regenerate or Regen + rescale and left blank on Keep, because there is no order "
        "to work you are not doing.",
    ]


def _brief(meta, items, groups, counts):
    top = [(c, groups.get(c, 0)) for c in CLUSTERS]
    return (
        "<p><b>What this is.</b> Every weapon the campaign's full mod stack loads "
        "\u2014 guns, energy weapons, launchers, turret guns, blades, clubs and natural "
        "parts \u2014 with its art shown twice: once at <b>the size the game draws it in "
        "a pawn's hands</b> (max drawSize \u00d7 128 px, a real colonist beside it, grid "
        "= 1 cell) and once zoomed to a fixed box so the art itself can be judged. "
        "<b>The scale panel matches the engine exactly</b>: "
        "<code>PawnRenderUtility.DrawEquipmentAiming</code> draws the weapon mesh at "
        "<code>drawSize</code> and nothing else. Decide whether each sprite is "
        "<b>kept</b>, <b>regenerated</b>, <b>regenerated and rescaled</b>, or whether the "
        "<b>weapon</b> goes.</p>"
        "<p><b>The campaign it is for.</b> Ash'karr \u2014 a desert world, a Jawa "
        "scavenger clan, <b>Star Wars register</b>. Scavenged, ion, salvage-built and "
        "blaster-adjacent belong. A recognisably modern-Earth assault rifle is a problem "
        "<i>however well drawn</i>. <b>The pre-fill ranks how the art holds up at display "
        "size. It CANNOT rank worth</b> \u2014 whether a weapon belongs in this fiction is "
        "your call, and the only gesture the machine makes at it is a <b>word test</b> on "
        "the label (<code>REGISTER-RISK</code>, %d rows). <b>The rows you overrule are the "
        "point of this sheet.</b></p>"
        "<p><b>Where the numbers come from.</b> The sqlite def dump at <code>%s</code> "
        "(<b>%d mods</b>, game <code>%s</code>, captured <code>%s</code>), checked against "
        "the frozen full list of <b>%d</b>%s.%s There is <b>no resolved-stat capture for "
        "weapons</b>, so every figure is the <b>declared base at no stuff, normal quality "
        "and no wielder</b>, put through the engine's own arithmetic (formulas read out of "
        "the game's C#, listed under \u201cinvented / assumed\u201d). Calibration: "
        "<b>%s</b>. Anything the defs do not carry is written <b>UNMEASURED</b>, never a "
        "plausible digit \u2014 <b>%d</b> rows carry at least one.</p>"
        "<p><b>What the art metric actually found, said plainly.</b> Only <b>%d</b> of "
        "<b>%d</b> resolved sprites are soft at their drawn size (under 0.8 px per cell) "
        "and <b>%d</b> are badly stretched. <b>The art in this stack is mostly fine at "
        "one cell</b>, so a criterion built on resolution has very little to say here "
        "\u2014 which is exactly why the <b>note</b> and the <b>register</b> question "
        "carry this review, not the pre-fill. If almost every row comes back "
        "\u201ckeep\u201d, that is the metric agreeing with itself, not the sheet "
        "succeeding.</p>"
        "<p><b>What has already been cut.</b> %s \u2014 <b>%d</b> of these weapons are on "
        "that list and are <b>badged CUT, not hidden</b>, because you must be able to tell "
        "\u201cthis mod ships nothing\u201d from \u201cI cut it all\u201d. A second, "
        "independent reading agrees with it exactly: every cut weapon has an <b>empty "
        "weaponTags</b> list in the dump and no tagged weapon is cut. A further <b>%d</b> "
        "LIVE weapons also carry no tags \u2014 those are <code>ORPHAN-TAGS</code>: real, "
        "loadable, and <b>no pawn kind can ever roll them</b>.</p>"
        "<p><b>Clusters (strongest first inside each):</b> %s. <b>%d</b> rows have no art "
        "this machine could resolve offline \u2014 that says MISSING on the row and never "
        "a placeholder guess.</p>"
        "<p><b>Filters.</b> The dropdowns cover state, cluster, and the contested / "
        "overruled / noted marks. The <b>search box</b> is the rest \u2014 every row "
        "carries stable tokens: <code>CUT</code> \u00b7 <code>MISSING-ART</code> \u00b7 "
        "<code>SOFT-ART</code> \u00b7 <code>ORPHAN-TAGS</code> \u00b7 "
        "<code>REGISTER-RISK</code> \u00b7 <code>TURRET-GUN</code> \u00b7 "
        "<code>STUFFABLE</code> \u00b7 <code>EXPLOSIVE</code> \u00b7 <code>ONE-USE</code> "
        "\u00b7 <code>UNMEASURED</code> \u00b7 <code>CLUSTER-INFERRED</code> \u00b7 <code>NATURAL-PART</code> \u00b7 <code>UNCLASSIFIED-MELEE</code>. A mod name "
        "works too.</p>"
        "<p><b>Keyboard:</b> <kbd>1</kbd> keep \u00b7 <kbd>2</kbd> regenerate \u00b7 "
        "<kbd>3</kbd> regen+rescale \u00b7 <kbd>4</kbd> cut weapon \u00b7 <kbd>n</kbd> "
        "note \u00b7 <kbd>z</kbd> zoom \u00b7 <kbd>g</kbd> next undecided. The "
        "<b>note</b> is the most valuable control on the row \u2014 the owner uses it for "
        "renames and description rewrites, and it is where \u201cthis is an M16 with the "
        "serial filed off\u201d belongs.</p>"
        % (counts["register"], os.path.basename(DB), meta["dumpMods"],
           meta.get("gameVersion"), meta["dumpCaptured"], meta["fullModlist"],
           (" \u2014 the dump additionally knows <code>%s</code>, dropped since; those "
            "weapons are on the sheet and badged"
            % ", ".join(meta["droppedSinceDump"][:4]))
           if meta["droppedSinceDump"] else " \u2014 the same set",
           (" <b>%d</b> mod(s) in the frozen list are missing from the dump "
            "(<code>%s</code>); each was walked on disk and PROVEN to declare no "
            "&lt;verbs&gt;, &lt;tools&gt; or &lt;weaponTags&gt;, so nothing is silently "
            "absent from this sheet."
            % (len(meta.get("absentProvenWeaponless") or []),
               ", ".join(meta.get("absentProvenWeaponless") or [])))
           if meta.get("absentProvenWeaponless") else "",
           meta["calibration"], counts["unmeasured"],
           counts["softArt"], counts["resolved"], counts["hardStretch"],
           meta["cutProvenance"],
           counts["cut"], counts["orphan"],
           ", ".join("%s (%d)" % (g, n) for g, n in top if n), counts["missing"]))


RENDER_JS = r"""
<script id="RENDER">
/* The default row is a thumbnail plus one line. A weapon row is a dossier: two
   pictures doing different jobs, the combat block, the build block, and a PRIORITY
   control the template does not ship. Everything below is ADDITIVE — the chrome,
   persistence, filters, undo and keyboard are the skill's, untouched. */
(function () {
  var css = document.createElement('style');
  css.textContent = [
    '.wp-scale{margin:6px 0 4px;max-height:250px;max-width:100%;overflow:auto;',
    '  border:1px solid #232a33;border-radius:6px;background:#12151a}',
    '.wp-scale img{display:block;image-rendering:pixelated}',
    '.wp-cap{color:#6d7987;font-size:10.5px;margin:1px 0 4px}',
    '.wp-desc{color:#9aa6b4;font-size:11.5px;margin:3px 0;max-width:78ch}',
    '.wp-facts{display:grid;grid-template-columns:104px minmax(0,1fr);gap:1px 8px;',
    '  font-size:11.5px;color:#c3cad6;margin-top:4px}',
    '.wp-facts>div{min-width:0;overflow-wrap:anywhere}',
    '.wp-facts b{color:#7f8b99;font-weight:600}',
    '.wp-um{color:#e8b64c}',
    '.row .ctrl{width:264px}',
    '.row .opts button{font-size:11px;padding:5px 2px}',
    '.wp-badge{font-size:10px;border-radius:3px;padding:1px 6px;border:1px solid;margin-right:4px}',
    '.wp-cut{color:#ffb3b3;border-color:#7a2b2b;background:#2a0f0f;font-weight:700}',
    '.wp-orph{color:#e8b64c;border-color:#5a4320;background:#1a1408}',
    '.wp-reg{color:#ffc9a3;border-color:#7a4a2b;background:#2a1608;font-weight:700}',
    '.wp-src{color:#5f6b7a;font-size:10.5px;margin:3px 0 0}',
    '.wp-miss{color:#ffb3b3;border-color:#7a2b2b;background:#2a0f0f}',
    '.wp-prio{display:flex;gap:4px;align-items:center;margin-top:4px}',
    '.wp-prio span{color:#5f6b7a;font-size:10.5px}',
    '.wp-prio button{cursor:pointer;background:#161a20;border:1px solid #2a2f37;',
    '  border-radius:4px;padding:2px 8px;font-size:11px;color:#98a2b3}',
    '.wp-prio button.on{background:#243447;border-color:#3d6a92;color:#dff0ff;font-weight:700}'
  ].join('');
  document.head.appendChild(css);

  function um(s) {
    s = esc(s == null ? '' : String(s));
    return s.replace(/UNMEASURED/g, '<span class="wp-um">UNMEASURED</span>');
  }

  window.itemBody = function (it) {
    var b = [];
    if (it.cut) b.push('<span class="wp-badge wp-cut">CUT — the game does not have this</span>');
    if (!it.thumb) b.push('<span class="wp-badge wp-miss">ART MISSING: ' + esc(it.artReason || '?') + '</span>');
    if (it.registerRisk) b.push('<span class="wp-badge wp-reg">REGISTER RISK — label says “' + esc(it.registerRisk) + '”</span>');
    if (!it.cut && (it.tags === '(none)')) b.push('<span class="wp-badge wp-orph">ORPHAN — no weaponTags, no pawn kind can roll it</span>');
    /* kind and mod are CATEGORIES, not flags: every row has exactly one of each, so
       they must not share the badge row with the sparse marks or they teach the eye
       to skip that position. They get their own muted line. The template already
       renders the ◆ contested / ⚠ inferred marks beside the label — repeating them
       here would be the same wallpaper in a second place. */

    var pic = '';
    if (it.scale) {
      pic = '<div class="wp-scale"><img src="' + esc(it.scale) + '" loading="lazy" decoding="async" alt=""></div>'
          + '<div class="wp-cap">true in-hand scale · colonist ≈1.5 cells · grid = 1 cell · drawn at '
          + (it.cells != null ? it.cells : '?') + ' cell(s), shown at 2× (128 px/cell)'
          + (it.shownPct && it.shownPct < 100 ? ' · panel shrunk to ' + it.shownPct + '%' : '')
          + (it.srcPx ? ' · source sprite ' + it.srcPx[0] + '×' + it.srcPx[1] + 'px' : '')
          + (it.pxPerCell != null ? ' · ' + it.pxPerCell + ' px per drawn cell' : '')
          + (it.rung ? ' · resolved ' + esc(it.rung) : '') + '</div>';
    }

    function row(k, v) { return (v === null || v === undefined || v === '') ? '' : '<b>' + k + '</b><div>' + um(v) + '</div>'; }
    var facts = '<div class="wp-facts">'
      + row('what it is for', it.role)
      + row('damage', it.damage + ' — ' + it.damageType)
      + row('armour pen', it.ap)
      + row('range', it.range)
      + row('timing', it.warmupCooldown)
      + row('accuracy', it.accuracy)
      + row('burst', it.burst)
      + row('DPS', it.dps + (it.dpsNote ? '  ⚠ ' + it.dpsNote : ''))
      + row('melee bash', it.meleeFallbackDps ? it.meleeFallbackDps + ' DPS with the stock/barrel' : '')
      + row('attacks', (it.toolLines || []).join('  ·  '))
      + row('tech level', it.techLevel)
      + row('to make', it.cost)
      + row('stuffable', it.stuffable)
      + row('research', it.research)
      + row('weapon tags', it.tags + (it.classes ? '   classes: ' + it.classes : ''))
      + row('who carries', it.carriers)
      + row('regen at', it.regenPx ? it.regenPx + '×' + it.regenPx + ' px (clamp(ceil_pow2(' + it.cells + '×128), 256, 1024))' : 'UNMEASURED — no drawSize')
      + row('pre-fill', it.why)
      + '</div>';

    var d = (typeof DEC !== 'undefined' && DEC[it.id]) || {};
    var prio = d.prio || '';
    var pb = ['A', 'B', 'C'].map(function (p) {
      return '<button data-prio="' + p + '" class="' + (prio === p ? 'on' : '') + '">' + p + '</button>';
    }).join('');
    var pctl = '<div class="wp-prio"><span>regen priority</span>' + pb
             + '<button data-prio="" class="' + (prio ? '' : 'on') + '">—</button></div>';

    return '<div class="marks">' + b.join('') + '</div>'
         + '<div class="wp-src">' + esc(it.kind || '') + ' · ' + esc(it.mod || '')
         + (it.inferred ? ' · cluster inferred from a word, not a field' : '') + '</div>'
         + (it.desc ? '<div class="wp-desc">' + esc(it.desc) + '</div>' : '')
         + pic + '<div class="effect">' + esc(it.effect || '') + '</div>' + facts + pctl;
  };

  /* The priority axis writes into the SAME per-row record the sidecar merges, so it
     rides the existing save path — no second file, no second protocol. */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('[data-prio]');
    if (!btn) return;
    var row = btn.closest('.row'); if (!row) return;
    var id = row.dataset.id;
    if (typeof DEC === 'undefined') return;
    var rec = DEC[id] || (DEC[id] = { decision: '', note: '', prio: '' });
    rec.prio = btn.dataset.prio;
    queue(id); patchRow(id);
  }, true);
})();
</script>
"""


def _inject_render(html):
    return html.replace("<script>\n\"use strict\";", RENDER_JS + "\n<script>\n\"use strict\";", 1)


def _counts(items, rows):
    return {
        "cut": sum(1 for it in items if it["cut"]),
        "missing": sum(1 for it in items if not it["thumb"]),
        "register": sum(1 for it in items if it.get("registerRisk")),
        "orphan": sum(1 for r in rows if not r.get("weaponTags") and not r.get("cut")),
        "unmeasured": sum(1 for it in items if "UNMEASURED" in json.dumps(it)),
        "contested": sum(1 for it in items if it["contested"]),
        "softArt": sum(1 for it in items
                       if it.get("pxPerCell") is not None and it["pxPerCell"] < PPC_SOFT),
        "hardStretch": sum(1 for it in items
                           if it.get("pxPerCell") is not None and it["pxPerCell"] < PPC_BAD),
        "resolved": sum(1 for it in items if it.get("pxPerCell") is not None),
    }


def write_sheet(rows, meta):
    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    items = make_items(rows)
    groups = {}
    for it in items:
        groups[it["group"]] = groups.get(it["group"], 0) + 1
    counts = _counts(items, rows)

    cfg = {
        "sheetId": "weapon_register",
        "title": "Weapon art register — every weapon in the stack",
        "subtitle": "%d weapons · %d clusters · %d CUT · %d art missing · %d register-risk"
                    % (len(items), len([g for g in groups if groups[g]]),
                       counts["cut"], counts["missing"], counts["register"]),
        "briefHtml": _brief(meta, items, groups, counts),
        "criterion":
            "Ranked by px-per-cell \u2014 how well the SHIPPING ART holds up at the size "
            "the game draws it in a pawn's hands (source sprite edge \u00f7 drawSize\u00d764). "
            "That ranks QUALITY. It cannot rank WORTH: whether a weapon belongs in a Star "
            "Wars desert-scavenger campaign is invisible to it, and the only gesture made "
            "at that is a word test on the label. Inside each cluster rows are ordered by "
            "DPS so the power ladder is visible \u2014 that is an ordering, not a verdict.",
        "invented": _invented(),
        "posture": {
            "mode": "blacklist",
            "explain": "Default is KEEP THE ART. An undecided row destroys nothing and "
                       "queues no work. Only an explicit \u201cCut weapon\u201d removes a "
                       "weapon; only \u201cRegenerate\u201d or \u201cRegen + rescale\u201d "
                       "queues art work. Freezing this sheet with rows undecided costs "
                       "nothing.",
        },
        "options": [
            {"key": "keep", "label": "Keep art", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "regen", "label": "Regenerate", "hotkey": "2", "color": "#6aa6e8", "counts": "in"},
            {"key": "rescale", "label": "Regen + rescale", "hotkey": "3", "color": "#e8b64c", "counts": "in"},
            {"key": "cut", "label": "Cut weapon", "hotkey": "4", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "weapon class",
        "media": True,
        "decisionsFile": os.path.basename(DECISIONS),
        "decisionsPath": _native(DECISIONS),
        "sheetPath": _native(SHEET_HTML),
    }

    out = _replace_json(tpl, "CONFIG", cfg)
    out = _replace_json(out, "ITEMS", items)
    out = _inject_render(out)
    with open(SHEET_HTML, "w", encoding="utf-8") as fh:
        fh.write(out)
    return items, groups, counts


# ═════════════════════════════════════════════════════════ stage: prefill 🔒
def write_prefill(rows, meta, override=False):
    existing = {}
    if os.path.isfile(DECISIONS):
        try:
            with open(DECISIONS, encoding="utf-8") as fh:
                existing = json.load(fh)
        except (OSError, ValueError):
            existing = {}
    if existing.get("savedBy") and not override:
        die("this decisions file has ALREADY been written by the sheet (savedBy=%r, "
            "writeCount=%r). Regenerating the pre-fill would record the generator's "
            "guesses under the owner's name.\n  If you truly mean it: "
            "--i-know-this-overwrites-the-owners-decisions"
            % (existing.get("savedBy"), existing.get("writeCount")))
    if existing.get("frozen") and not override:
        die("this decisions file is FROZEN (%s). It is the source of truth."
            % existing.get("frozenOn"))

    dec = {}
    for r in rows:
        pre, prio, _c, _why = prefill_of(r)
        dec[r["defName"]] = {"decision": pre, "prefill": pre, "prio": prio, "note": ""}

    doc = dict(existing)
    doc.update({
        "sheetId": "weapon_register",
        "posture": "blacklist",
        "postureMeaning":
            "Default is KEEP THE ART. An undecided row destroys nothing and queues no "
            "work. Only 'cut' removes a weapon; 'regen'/'rescale' queue art work. 'prio' "
            "(A/B/C) is the regeneration ORDER and is meaningful only on a regen/rescale "
            "row. 'note' is free text and outranks everything else.",
        "options": ["keep", "regen", "rescale", "cut"],
        "criterion":
            "px-per-cell — how the shipping art holds up at drawSize x 64, plus a LEXICAL "
            "modern-Earth-name test. Ranks QUALITY and flags a shortlist; it cannot rank "
            "WORTH. Whether a weapon belongs in the Star Wars register is the owner's "
            "call and lives in the notes.",
        "generatedBy": "gen_weapon_register.py " + VERSION,
        "generatedUtc": meta["builtUtc"],
        "provenance": {k: meta.get(k) for k in
                       ("dumpMods", "dumpCaptured", "gameVersion", "fullModlist",
                        "liveActiveMods", "cutProvenance", "calibration")},
        "decisions": dec,
    })
    with open(DECISIONS, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    return len(dec)


# ═════════════════════════════════════════════════════════════════════ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", default="all",
                    choices=("all", "data", "art", "sheet", "prefill"),
                    help="all = data+art+sheet. prefill is NEVER in all; it is locked.")
    ap.add_argument("--calibrate", action="store_true",
                    help="run the assault-rifle/gladius check and exit")
    ap.add_argument("--rebuild-texture-index", action="store_true")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions", action="store_true",
                    dest="override")
    a = ap.parse_args(argv)

    if a.calibrate:
        db = sqlite3.connect(DB)
        bad = calibrate(db)
        db.close()
        if bad:
            print("CALIBRATION FAILED:\n  " + "\n  ".join(bad))
            return 3
        print("CALIBRATION PASSED — 13 published-vanilla readings match, the one modded "
              "divergence is exactly where expected, and the melee-DPS formula reproduces "
              "an independently published 7.04")
        return 0

    os.makedirs(REVIEW, exist_ok=True)
    t0 = time.perf_counter()

    if a.stage in ("all", "data"):
        rows, meta = build_rows()
        rows = cluster(rows)
        with open(ROWS_JSON, "w", encoding="utf-8") as fh:
            json.dump({"meta": meta, "rows": rows}, fh, ensure_ascii=False)
        print("data:  %d weapons (%d abstract dropped) · %d clusters · %.1fs"
              % (len(rows), meta["abstractRowsDropped"],
                 len({r["group"] for r in rows}), time.perf_counter() - t0))
    else:
        with open(ROWS_JSON, encoding="utf-8") as fh:
            blob = json.load(fh)
        rows, meta = blob["rows"], blob["meta"]

    if a.stage in ("all", "art"):
        if a.rebuild_texture_index and os.path.isfile(TEXCACHE):
            os.remove(TEXCACHE)
        st = render_art(rows)
        with open(ROWS_JSON, "w", encoding="utf-8") as fh:
            json.dump({"meta": meta, "rows": rows}, fh, ensure_ascii=False)
        print("art:   %d placed · %d no texture · %d blank png · %d capped"
              % (st["placed"], st["missing"], st["blank"], st["capped"]))

    if a.stage == "prefill":
        n = write_prefill(rows, meta, override=a.override)
        print("prefill: %d rows written to %s" % (n, DECISIONS))
        return 0

    if a.stage in ("all", "sheet"):
        if not os.path.isfile(DECISIONS):
            n = write_prefill(rows, meta)
            print("prefill: %d rows (the decisions file did not exist yet)" % n)
        items, groups, counts = write_sheet(rows, meta)
        print("sheet: %d rows · %s" % (len(items), SHEET_HTML))
        for c in CLUSTERS:
            print("   %-18s %d" % (c, groups.get(c, 0)))
        print("   CUT %d · missing art %d · register-risk %d · orphan-tags %d · "
              "soft art %d · rows with an UNMEASURED %d · contested %d"
              % (counts["cut"], counts["missing"], counts["register"], counts["orphan"],
                 counts["softArt"], counts["unmeasured"], counts["contested"]))
    print("done in %.1fs" % (time.perf_counter() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
