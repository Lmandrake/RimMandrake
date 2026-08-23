#!/usr/bin/env python3
r"""weapon_tag_audit.py - which weapon tags the cherrypick emptied, and who that disarms.

WHY THIS EXISTS. A PawnKindDef asks for weapons by TAG, never by defName. Cut the last
weapon carrying a tag and the tag resolves to an empty set - and a pawn kind whose tags
have ALL gone empty spawns BARE-HANDED, with no red error and nothing in Player.log. The
kind is valid, the tag is valid, the set is just empty. This campaign cut the entire
vanilla firearm line in favour of blasters and disarmed 49 pawn kinds doing it, including
vanilla tribals, the Mechanitor, and two of our own.

🔴 READ THE TAGS FROM THE DEF DUMP, NOT FROM MOD XML. Owner's ruling 2026-08-19: a dump
regenerated under the full list is "much more accurate than scanning the XML defs,
provided that its version matches the current modlist." The dump is post-inheritance,
post-PatchOperation and post-dedup; a raw XML scan is none of those, so it cannot see a
tag a kind inherits from an abstract parent or is handed by another mod's patch.
⚠️ The proviso is the point: this tool REFUSES to report unless the dump's mod set
matches ModsConfig.xml, because a dump captured under a different list describes a
different game. --anyway downgrades that to a loud warning.

    python3 src/RimMandrake/Utils/weapon_tag_audit.py                 # report
    python3 src/RimMandrake/Utils/weapon_tag_audit.py --emit-patch <out.xml>
"""
from __future__ import annotations
import argparse, json, os, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from game_paths import DEF_DUMP, LOCALLOW, MODS_CONFIG   # noqa: E402
import dump_projection   # noqa: E402

DUMP = Path(DEF_DUMP)
REPO = Path(__file__).resolve().parents[3]
CUTS = REPO / "observed" / "inventory"

# The vanilla tag vocabulary a pawn kind is likely to ask for. A surviving weapon that
# carries none of these is invisible to every vanilla and most modded pawn kinds.
VANILLA_ROLE_TAGS = {
    "SimpleGun", "Autopistol", "Revolver", "PumpShotgun", "AssaultRifle", "SniperRifle",
    "Minigun", "IndustrialGunAdvanced", "ShortShots", "LongShots", "MakeshiftGun",
    "Flamethrower", "GunHeavy", "SpacerGun", "GunSingleUse",
    "NeolithicMeleeBasic", "NeolithicMeleeDecent", "NeolithicMeleeAdvanced",
    "NeolithicRangedBasic", "NeolithicRangedDecent", "NeolithicRangedAdvanced",
    "NeolithicRangedHeavy", "NeolithicRangedChief",
    "MedievalMeleeBasic", "MedievalMeleeDecent", "MedievalMeleeAdvanced",
}

# defName/label substrings -> role. Order matters: the first hit wins, so the more
# specific words come first. This is a heuristic and the report prints it, because a
# misfiled weapon is a raid holding the wrong thing rather than a silent failure.
ROLE_WORDS = [
    ("bowcaster", "rifle"), ("holdout", "pistol"), ("revolver", "pistol"),
    ("pistol", "pistol"), ("sidearm", "pistol"), ("smg", "smg"),
    ("submachine", "smg"), ("shotgun", "shotgun"), ("scattergun", "shotgun"),
    ("sniper", "sniper"), ("marksman", "sniper"), ("dmr", "sniper"),
    ("minigun", "heavy"), ("cannon", "heavy"), ("launcher", "heavy"),
    ("repeating", "heavy"), ("lmg", "heavy"), ("hmg", "heavy"),
    ("carbine", "rifle"), ("rifle", "rifle"), ("blaster", "rifle"),
    ("repeater", "rifle"), ("musket", "rifle"),
]

# role -> the vanilla tags a weapon of that role should answer to. Two tiers, split at
# the role's median market value, because a pawn kind asking for `IndustrialGunAdvanced`
# means "a good gun" and one asking for `SimpleGun` means "any gun".
ROLE_TAGS = {
    "pistol":  (["SimpleGun", "Autopistol", "Revolver", "ShortShots"],
                ["SimpleGun", "Revolver", "ShortShots", "IndustrialGunAdvanced"]),
    "smg":     (["SimpleGun", "ShortShots", "MakeshiftGun"],
                ["ShortShots", "IndustrialGunAdvanced", "AssaultRifle"]),
    "shotgun": (["SimpleGun", "PumpShotgun", "ShortShots"],
                ["PumpShotgun", "ShortShots", "IndustrialGunAdvanced"]),
    "rifle":   (["SimpleGun", "AssaultRifle"],
                ["AssaultRifle", "IndustrialGunAdvanced"]),
    "sniper":  (["SniperRifle", "LongShots"],
                ["SniperRifle", "LongShots", "IndustrialGunAdvanced"]),
    "heavy":   (["IndustrialGunAdvanced", "GunHeavy"],
                ["IndustrialGunAdvanced", "GunHeavy", "Minigun"]),
    # The pre-industrial ladders. Their empty rungs disarm tribal kinds, which is the
    # half of this the owner noticed first: the vanilla bows were cut but modded ones
    # survive, so the tier a kind asks for is what decides whether it is armed.
    "n_melee":  (["NeolithicMeleeBasic", "NeolithicMeleeDecent"],
                 ["NeolithicMeleeDecent", "NeolithicMeleeAdvanced", "MedievalMeleeDecent"]),
    "n_ranged": (["NeolithicRangedBasic", "NeolithicRangedDecent"],
                 ["NeolithicRangedDecent", "NeolithicRangedAdvanced",
                  "NeolithicRangedHeavy", "NeolithicRangedChief"]),
}


def f(d, k, dflt=None):
    return (d.get("fields") or {}).get(k, dflt)


def market_value(d):
    for sm in (f(d, "statBases") or []):
        if isinstance(sm, dict) and sm.get("stat") == "MarketValue":
            return sm.get("value")
    return None


NEO_MELEE = ("club", "spear", "axe", "knife", "dagger", "sword", "mace", "hammer",
             "blade", "staff", "cleaver", "machete", "shiv", "scythe", "claw", "fang")
NEO_RANGED = ("bow", "sling", "javelin", "throw", "dart", "blowgun", "boomerang")


def _family(tag):
    """The tag family a tag belongs to: its longest leading run of capitalised words.

    `WarcasketBasic` -> `Warcasket`, `NeolithicRangedFlame` -> `NeolithicRanged`,
    `VEE_HunterIndustrialWeapon` -> `VEE_Hunter`. Crude on purpose: it only has to be
    good enough to put siblings beside each other for a human to read, and a wrong
    grouping is visible in one glance where a wrong TAG is invisible for a whole load.
    """
    import re as _re
    if "_" in tag:
        head = tag.split("_")[0] + "_" + tag.split("_")[1] if tag.count("_") >= 1 else tag
        parts = _re.findall(r"[A-Z][a-z]*", tag.split("_", 1)[1] if "_" in tag else tag)
        if len(parts) > 1:
            return tag.split("_", 1)[0] + "_" + "".join(parts[:-1])
        return head
    parts = _re.findall(r"[A-Z][a-z]*", tag)
    return "".join(parts[:-1]) if len(parts) > 1 else tag


def role_of(d):
    """Which tag ladder does this weapon belong on?

    Pre-industrial weapons are classified first and separately, because the vanilla
    firearm words ("rifle", "cannon") appear in modded neolithic labels often enough
    that running the gun list first mislabels them."""
    s = (d["defName"] + " " + str(f(d, "label") or "")).lower()
    tl = f(d, "techLevel")
    if tl in ("Neolithic", "Medieval"):
        cls = set(f(d, "weaponClasses") or [])
        if "Melee" in cls or any(w in s for w in NEO_MELEE):
            return "n_melee"
        if "Ranged" in cls or any(w in s for w in NEO_RANGED):
            return "n_ranged"
        return None
    for word, role in ROLE_WORDS:
        if word in s:
            return role
    return None


def load_dump():
    """The four things this tool actually needs, as PROJECTIONS not as records.

    🔴 It used to `json.load` the whole of `defs/ThingDef.json` — 24,904 records,
    ~316 MB of text — to read six fields off the ~771 defs that are weapons.
    Measured cost of that: **3.5 s and 1.50 GB resident**. The same four answers
    off `defs.sqlite`, using the pre-extracted `def_tags` / `def_flags` side
    tables and a `json_extract` restricted to weapon-flagged rows: **0.8 s and
    18 MB**.

    ⚠️ The db is NOT automatically the faster source and this tool is the proof —
    a naive `json_extract` per field over every ThingDef measures 6.7 s, twice as
    slow as reading the file. `dump_projection` carries the numbers and the shape
    that wins. It also falls back to the JSON when no `defs.sqlite` exists, so
    this still runs on a machine without the `measuring-large-artifacts` skill.
    """
    defs = DUMP / "defs"
    if not defs.is_dir():
        sys.exit("no def dump at %s - the game must write one before this can run" % defs)
    thing_tags = dump_projection.weapon_tag_pairs(str(DUMP), "ThingDef")
    kind_tags = dump_projection.weapon_tag_pairs(str(DUMP), "PawnKindDef")
    weapons = dump_projection.weapon_defs(str(DUMP))
    man = json.loads((DUMP / "manifest.json").read_text(encoding="utf-8"))
    return thing_tags, kind_tags, weapons, man


def check_modlist(man, anyway):
    """🔴 The proviso on the owner's ruling. A dump from a different mod set is a
    measurement of a different game, and every count below would be quietly wrong."""
    try:
        live = {li.text.strip().lower() for li in ET.parse(MODS_CONFIG).getroot()
                .find("activeMods") if li.text}
    except Exception as e:
        print("!! cannot read ModsConfig.xml (%s) - cannot verify the dump matches" % e)
        live = None
    n = man.get("modCount")
    if live is None:
        return
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


def cut_set(category):
    p = CUTS / ("decisions_%s.json" % category)
    if not p.is_file():
        return set()
    return {c["defName"] for c in json.loads(p.read_text(encoding="utf-8"))["cut"]}


def audit(anyway=False):
    thing_tags, kind_tags, weapons, man = load_dump()
    check_modlist(man, anyway)
    cut = cut_set("weapons")

    tags = {}
    for defname, t in thing_tags:
        e = tags.setdefault(t, {"all": [], "kept": []})
        e["all"].append(defname)
        # 🔴 CORRECTED 2026-08-23, BUILD. This used to be `if defname not in cut`,
        # and it subtracted the kill list a SECOND time — reporting 6 kinds as
        # disarmed that the capture proves are armed, `Mech_Pikeman`,
        # `Drone_Sentry` and `Tribal_Archer_Fire` among them. It would have closed
        # RESTORE_VANILLA_GUN_TAGS_1 and MECH_AND_ARCHER_ARMED_1 as still-broken.
        #
        # 🔑 THE KILL LIST IS INTENT; THE CAPTURE IS REALITY, and the capture is
        # ALREADY post-cut — the block below says so itself: Cherry Picker strips
        # `weaponTags` at load rather than deleting the def, so a genuinely cut
        # weapon contributes NO tag here and can never reach this line. Anything
        # that does reach it is a weapon that survived the cut still carrying the
        # tag. `Gun_Needle` is on the kill list AND carries
        # `MechanoidGunLongRange` in the live capture, because it was deliberately
        # restored; the list had not caught up and the list was believed.
        #
        # ⇒ Presence in the capture with the tag attached IS survival. Do not
        # re-subtract a written intent from a measured fact.
        e["kept"].append(defname)

    empty = sorted(t for t, v in tags.items() if not v["kept"])

    # 🔴 CORRECTED 2026-08-21 (WEAPON_TAGS_MATCH_NOTHING_1). `empty` above is
    # STRUCTURALLY ALWAYS EMPTY, and the "emptied by the cut: 0" this used to print was a
    # guaranteed zero, not a measurement. Cherry Picker does not DELETE a cut weapon; it
    # NEUTERS it in place - the ThingDef is still in the dump, carrying `weaponTags: []`
    # and MarketValue 0. So a cut weapon contributes no tag to `tags` at all, and a tag
    # whose every carrier was cut never enters `tags` to be counted as emptied. The `cut`
    # filter can only ever fire on a tag that still has a live carrier, which by
    # definition is not empty.
    # ⇒ A DUMP ALONE CANNOT ATTRIBUTE AN EMPTY TAG TO THE CUT. The attribution needs the
    # mod's SOURCE XML, which still carries the tag the neutered def used to have.
    # Measured that way, 11 of the 14 dead tags behind the 15 disarmed kinds are OURS:
    # AMHP, PKM, MechanoidGunLongRange (Gun_Needle), SentryDroneGunShortRange
    # (Gun_Scattergun), NeolithicRangedFlame (Flamebow), WarcasketBasic, BS_CrossbowTag,
    # VEE_HunterIndustrialWeapon, VEE_HunterNeolithicWeapon, DP_CannonNoEquipTag and
    # DP_RocketNoEquipTag. Evidence:
    # infrastructure/state/observed/build/WEAPON_TAGS_MATCH_NOTHING_1_offline.txt
    # 🔑 Asked of the NAMED cut list only. A cut weapon that still carries a tag is
    # not neutered, so the question is about ~200 defNames, never about 24,904.
    cut_now = dump_projection.defs_by_name(str(DUMP), "ThingDef", sorted(cut),
                                           ("weaponTags",))
    neutered = [dn for dn in sorted(cut)
                if dn in cut_now and not (cut_now[dn].get("weaponTags") or [])]

    kind_wt = {}
    for defname, t in kind_tags:
        kind_wt.setdefault(defname, []).append(t)
    disarmed = []
    for defname, wt in kind_wt.items():
        if wt and all(not tags.get(t, {}).get("kept") for t in wt):
            disarmed.append((defname, wt))

    def eligible(d):
        if d["defName"] in cut:
            return False
        # 🔴 An INGESTIBLE is never a weapon this tool may tag, however swingable it is.
        # Measured 2026-08-21: two of five `Jawa_Tribal_Scavenger` generated holding a
        # bottle of `TarisianAle` as their PRIMARY weapon, because this function saw
        # `techLevel Neolithic` + `weaponClasses [Melee, MeleeBlunt]` and handed the
        # bottle `NeolithicMeleeBasic`/`Decent` - the scavenger's whole pool. RimWorld
        # will let a pawn club someone with a bottle; a pawn GENERATED holding one
        # instead of a weapon is the bug. `ingestible` is the separator, not `category`
        # and not a missing `verbs` - real melee weapons keep their attacks under
        # `tools`, so filtering on `verbs` throws out axes and clubs instead.
        if f(d, "ingestible"):
            return False
        cls = set(f(d, "weaponClasses") or [])
        wt = set(f(d, "weaponTags") or [])
        if "TurretGun" in wt or "ImprovisedMelee" in wt:
            return False
        tl = f(d, "techLevel")
        if tl in ("Industrial", "Spacer"):
            return "Ranged" in cls and not (wt & VANILLA_ROLE_TAGS)
        if tl in ("Neolithic", "Medieval"):
            # A pre-industrial weapon already on a full rung needs nothing; one whose
            # only rungs are EMPTY is exactly the case that disarms a tribal.
            rungs = wt & VANILLA_ROLE_TAGS
            return bool(cls) and (not rungs or all(not tags[t]["kept"] for t in rungs))
        return False

    # `weapons` is every def the ENGINE flags as a weapon. Measured 2026-08-22: no
    # ThingDef carries a non-empty `weaponClasses` without that flag, and every
    # branch of `eligible()` requires one — so this is the same set as scanning all
    # 24,904, arrived at without reading them. See `dump_projection.weapon_defs`.
    untagged = [d for d in weapons if eligible(d)]
    return tags, empty, sorted(disarmed), untagged, neutered


def plan(untagged):
    """Group the untagged survivors by role and split each role at its median value."""
    by_role = {}
    for d in untagged:
        r = role_of(d)
        if r in ROLE_TAGS:
            by_role.setdefault(r, []).append(d)
    out = {}
    for r, ds in by_role.items():
        vals = sorted(v for v in (market_value(x) for x in ds) if v)
        mid = vals[len(vals) // 2] if vals else 0
        low, high = ROLE_TAGS[r]
        for d in ds:
            v = market_value(d) or 0
            # A Unique is a quest reward. Tagging it into a common pool puts a
            # legendary weapon in an ordinary raid, so it only ever gets the top tier.
            uniq = "Unique" in d["defName"]
            out[d["defName"]] = (r, sorted(set(high if (v >= mid or uniq) else low)))
    return out


# Tags this campaign needs that no weapon carries. A pawn kind naming one of these is
# asking for a weapon that does not exist; putting the tag on the right survivor is
# cheaper than rewriting the kind, and it survives a regenerate of the kind.
EXTRA_TAGS = {
    # The Gamorrean enforcer named a tag no weapon carried. These two vibro-axes are the
    # weapon it was named for.
    "guy762_vaxe": ["Jawa_GamorreanAxe"],
    "guy762_vaxe_hutt": ["Jawa_GamorreanAxe"],
    # 🔑 The ion blaster is the ONE thing Jawas canonically MANUFACTURE, and the roster
    # builds the Trade Moot's grunt around it - but `zal.ionweaponry` tags its guns only
    # `Gun`/`SpacerGun`, which every blaster in the stack also carries. Without a tag of
    # their own there is no way to ask for "an ion weapon" and get one.
    "IW_Gun_IonPistol": ["Jawa_IonWeapon", "Jawa_IonWeaponLight"],
    "IW_Gun_IonPDW": ["Jawa_IonWeapon", "Jawa_IonWeaponLight"],
    "IW_Gun_IonSlugthrower": ["Jawa_IonWeapon", "Jawa_IonWeaponLight"],
    "IW_Gun_IonRifle": ["Jawa_IonWeapon"],
    "IW_Gun_IonDMR": ["Jawa_IonWeapon"],
    "IW_Gun_IonLMG": ["Jawa_IonWeapon", "Jawa_IonWeaponHeavy"],
    "IW_Gun_HeavyIonLance": ["Jawa_IonWeapon", "Jawa_IonWeaponHeavy"],
}


# 🔴 THE FILE THIS GENERATOR OWNS. Both safety guards below - refuse_shrink and
# preserved_block - are ABOUT THIS FILE, never about wherever --emit-patch is pointed.
#
# ⚠️ THEY USED TO READ THE OUTPUT PATH, AND THAT INVERTED THEM. Point --emit-patch at a
# scratch file to inspect the result before overwriting anything - the careful thing, the
# thing a reviewer does - and `existing_targets` returned empty, so refuse_shrink found
# nothing lost and stayed silent, while `preserved_block` found no markers and dropped the
# hand-authored block. Measured 2026-08-22: emitting to a scratch path produced 9
# operations against the 154 on disk and silently lost every hand-authored op, with no
# warning of any kind. CAUTION DISARMED THE GUARD.
# ⇒ Both now read CANON_PATCH no matter where the output goes.
CANON_PATCH = Path(__file__).resolve().parents[3] / "src" / "Jawa" / "Jawa_Patches" \
    / "Patches" / "WeaponTags_Renormalise.xml"

HAND_BEGIN = "<!-- BEGIN HAND-AUTHORED -->"
HAND_END = "<!-- END HAND-AUTHORED -->"


def preserved_block(path):
    """Return the hand-authored block of an existing emitted patch, or ''."""
    try:
        old = Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""
    i = old.find(HAND_BEGIN)
    j = old.find(HAND_END)
    if i < 0 or j < i:
        return ""
    return "\n" + old[i:j + len(HAND_END)] + "\n"


def existing_targets(path):
    """The defNames the emitted patch on disk already tags. Empty if there is none."""
    try:
        return set(re.findall(r'ThingDef\[defName="([^"]+)"\]/weaponTags</xpath>',
                              Path(path).read_text(encoding="utf-8")))
    except OSError:
        return set()


def refuse_shrink(mapping, path, allow):
    """🔴 THIS GENERATOR IS NOT IDEMPOTENT AND THE DUMP IS WHY.

    The def dump is captured with this patch ALREADY APPLIED, so every weapon the last
    run tagged comes back reading as already-tagged and drops out of `eligible`. Re-run
    it against that dump and it emits a handful of operations where the file holds
    hundreds - measured 2026-08-21: 9 against 154, a silent loss of 145.

    A count is not a roster, so this compares the actual defNames. If the new mapping
    would drop any target the file already carries, REFUSE and name them.

    To regenerate for real: capture a def dump with `Jawa_Patches` DISABLED, so the
    dump describes the game before this patch, then re-run. `--allow-shrink` overrides
    this check and is the wrong answer nine times in ten."""
    # ⛔ CANON_PATCH, not `path`. See the note at CANON_PATCH: reading the output path
    # means a scratch target has nothing to lose and the guard never fires.
    was = existing_targets(CANON_PATCH)
    lost = sorted(was - set(mapping))
    if not lost:
        return
    msg = ("REFUSING to write %s: it already tags %d defs and this run would tag %d, "
           "dropping %d of them.\n   first lost: %s\n   The dump was almost certainly "
           "captured WITH this patch applied, which makes every weapon it tagged look "
           "already-tagged. Capture a dump with Jawa_Patches disabled, or pass "
           "--allow-shrink if you truly mean to delete them."
           % (path, len(was), len(mapping), len(lost), ", ".join(lost[:8])))
    if not allow:
        sys.exit(msg)
    print("!!  " + msg + "\n")


def emit_patch(mapping, path, allow_shrink=False):
    for dn, tg in EXTRA_TAGS.items():
        role, have = mapping.get(dn, ("extra", []))
        mapping[dn] = (role, sorted(set(have) | set(tg)))
    refuse_shrink(mapping, path, allow_shrink)
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<Patch>", "", "<!--", """
    WeaponTags_Renormalise.xml            Jawa_Patches = generated, do not hand-edit
    ============================================================================
    Regenerate with weapon_tag_audit.py, passing it this file as the patch to emit:
        python3 src/RimMandrake/Utils/weapon_tag_audit.py  (see its docstring)

    🔴 WHY. A PawnKindDef asks for weapons by TAG. This campaign cut the whole vanilla
    firearm line in favour of blasters, and the blasters carry their own mods' tags
    (`Gun`, `SpacerGun`, `StarWarsRange`) but none of the vanilla ones. So every kind
    asking for `SimpleGun`, `Autopistol`, `AssaultRifle`, `ShortShots` or
    `IndustrialGunAdvanced` found an EMPTY set and spawned its pawns BARE-HANDED - 49
    kinds, silently, with nothing in the log.

    ⇒ This re-tags the SURVIVORS into the vanilla vocabulary instead of un-cutting the
    weapons. The cut stands; the ladders refill. Fixing it at the weapon end also fixes
    every future pawn kind, where patching 49 kinds would not.

    Tier split is each role's median market value. A `_Unique` always takes the top
    tier - it is a quest reward, and tagging one into a common pool puts a legendary
    weapon in an ordinary raid.

    🔴 NO INGESTIBLE IS TAGGED HERE. Measured 2026-08-21: two of five
    `Jawa_Tribal_Scavenger` generated holding a BOTTLE OF ALE as their primary weapon,
    because `TarisianAle` reads as techLevel Neolithic with weaponClasses
    [Melee, MeleeBlunt] and this file handed it the scavenger's only tag. `eligible`
    now drops anything carrying an `ingestible` block.

    🔴 DO NOT REGENERATE THIS FILE AGAINST A POST-PATCH DEF DUMP. The dump is captured
    with this patch ALREADY APPLIED, so every weapon it tagged reads as already-tagged
    and falls out of the eligible set: a regenerate on 2026-08-21 emitted 9 operations
    against the 154 on disk. weapon_tag_audit.py REFUSES that write now; capture a dump
    with Jawa_Patches disabled instead.
  """.rstrip(), "-->", ""]
    for dn, (role, tg) in sorted(mapping.items()):
        lines += [
            '  <Operation Class="PatchOperationConditional">',
            '    <xpath>/Defs/ThingDef[defName="%s"]/weaponTags</xpath>' % dn,
            '    <match Class="PatchOperationAdd">',
            '      <xpath>/Defs/ThingDef[defName="%s"]/weaponTags</xpath>' % dn,
            "      <value>%s</value>" % "".join("<li>%s</li>" % t for t in tg),
            "    </match>",
            '    <nomatch Class="PatchOperationAdd">',
            '      <xpath>/Defs/ThingDef[defName="%s"]</xpath>' % dn,
            "      <value><weaponTags>%s</weaponTags></value>"
            % "".join("<li>%s</li>" % t for t in tg),
            "    </nomatch>",
            "  </Operation>",
            "",
        ]
    # 🔑 A HAND-AUTHORED block may live at the end of the emitted file, between the
    # BEGIN/END markers below. It holds PawnKindDef ops this generator cannot derive
    # (a kind whose tag no weapon carries needs a CHOSEN tag, not a computed one).
    # Carry it across verbatim, or regenerating silently deletes work nobody will miss
    # until pawns spawn bare-handed again.
    # ⛔ CANON_PATCH, not `path` - same reason. The hand-authored ops belong to the file
    # this generator owns, and they must ride along into a scratch emit too, or the diff
    # a reviewer looks at is not the diff they would get.
    lines += [preserved_block(CANON_PATCH), "</Patch>", ""]
    # 🪤 An XML comment may not contain '--' ANYWHERE in its BODY - not in a rule line,
    # not in a CLI flag it quotes. One occurrence does not spoil the comment, it kills
    # the FILE: the parser aborts and every operation below is lost. Sanitise the body
    # only; doing it to the whole document eats the '<!--' delimiter itself.
    out = []
    inside = False
    for ln in lines:
        if ln.strip() == "<!--":
            inside = True
        elif ln.strip() == "-->":
            inside = False
        elif inside:
            ln = ln.replace("--", "=")
        out.append(ln)
    Path(path).write_text("\n".join(out), encoding="utf-8")
    return len(mapping)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--emit-patch", metavar="OUT")
    ap.add_argument("--siblings", action="store_true",
                    help="for every disarmed kind, show the SURVIVING tags in the same family - a dead tag dies out of a family, and the family is the decision")
    ap.add_argument("--list-unclassified", action="store_true",
                    help="name the surviving guns role_of could not classify - the remaining retag work, which the summary line otherwise hides")
    ap.add_argument("--anyway", action="store_true",
                    help="report even though the dump does not match the live mod list")
    a = ap.parse_args()

    tags, empty, disarmed, untagged, neutered = audit(a.anyway)
    print("weapon tags in the dump: %d" % len(tags))
    print("cut weapons still present but NEUTERED (weaponTags stripped): %d" % len(neutered))
    print("⚠️  a tag whose EVERY carrier was cut is INVISIBLE here - it is absent from")
    print("   the dump entirely, not present-and-empty. Attribute those from the mod's")
    print("   SOURCE XML, never from this dump. See the comment in audit().")
    if empty:
        print("tags with a carrier still in the dump but every carrier cut: %d" % len(empty))
        for t in empty:
            print("   %-32s lost all %d" % (t, len(tags[t]["all"])))
    print("\n🔴 pawn kinds with EVERY weapon tag empty: %d" % len(disarmed))
    for n, w in disarmed:
        print("   %-34s %s" % (n, w))
        if not a.siblings:
            continue
        # 🔑 THE SURVIVING SIBLINGS OF A DEAD TAG ARE THE WHOLE DECISION.
        # A dead tag almost never dies alone - it dies out of a FAMILY, and the family
        # is what tells you what the kind was meant to hold. `WarcasketBasic` has zero
        # carriers while `WarcasketAll`, `WarcasketVeteran`, `WarcasketHeavy`,
        # `WarcasketFlamer` and `WarcasketMelee` all have them, because the cherrypick
        # took exactly the three basic-tier guns. Printing the family turns "pick a tag
        # from 390" into "pick one of four, and mind the tier".
        # ⚠️ IT DOES NOT PICK FOR YOU, deliberately. A sibling is usually a TIER, so
        # taking the wrong one promotes the kind - `WarcasketAll` on a combatPower-300
        # footsoldier is an arms-race change dressed as a bug fix. Read the counts,
        # then choose.
        for want in w:
            fam = _family(want)
            sibs = sorted((t, len(v["kept"])) for t, v in tags.items()
                          if t != want and _family(t) == fam and v["kept"])
            if sibs:
                print("      %-28s family %-14s survivors: %s"
                      % ("↳ " + want, fam,
                         ", ".join("%s(%d)" % (t, n) for t, n in sibs[:6])))
            else:
                print("      %-28s family %-14s NO SURVIVING SIBLING - the whole family "
                      "is gone, so a vanilla ladder tag is the only route"
                      % ("↳ " + want, fam))
    print("\nsurviving Industrial/Spacer guns carrying NO vanilla role tag: %d" % len(untagged))
    m = plan(untagged)
    from collections import Counter
    print("   classified by role: %s" % dict(Counter(r for r, _ in m.values())))
    print("   unclassified (left alone): %d" % (len(untagged) - len(m)))
    if a.list_unclassified:
        # 🔑 THIS IS THE REMAINING RETAG WORK, NAMED. `role_of` matches a word list
        # against defName+label; a weapon whose name carries none of those words gets no
        # role and is skipped in silence. That silence is the point of this flag: the
        # summary line says "unclassified (left alone)" and a reader has no way to find
        # out WHICH, so the residue never shrinks.
        # ⚠️ Each one needs a human call - is it a pistol, a rifle, a heavy - or a new
        # word in ROLE_WORDS. Do NOT guess from the name alone; check range and damage.
        rest = sorted((d for d in untagged if d["defName"] not in m),
                      key=lambda d: d["defName"])
        print("\n   the unclassified, with what a classifier would need:")
        print("   %-40s %-9s %-8s %s" % ("defName", "techLevel", "value", "label"))
        for d in rest:
            print("   %-40s %-9s %-8s %s"
                  % (d["defName"], f(d, "techLevel"), market_value(d) or "?",
                     str(f(d, "label"))[:34]))
    if a.emit_patch:
        n = emit_patch(m, a.emit_patch)
        print("\nwrote %s - %d weapons re-tagged" % (a.emit_patch, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
