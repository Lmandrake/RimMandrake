"""Known donor-original content bugs in the KotOR absorption pool, corrected
at generation time so the fix survives every regen instead of being hand-
edited into a file whose own header says "GENERATED, do not hand-edit".
Filed against KOTORWEAPONS_ABSORPTION_CONTENT_NITS_1 -- see that item for the
full nine-item list; only the low-risk pure-text/stray-field fixes below are
applied. Left OUT on purpose, not fixed here:
  - the StormtrooperNameMaker rule-keyword path venting ("...FuckThisShitty
    NameMakerSystem") -- renaming it means renaming the matching rules-file
    keyword elsewhere too, and RimWorld's grammar resolver fails silently on
    a mismatched reference; not confident enough to do blind.
  - the Bullets_Special.xml donor TODO comment -- informational only, the
    fix would be real DamageWorker C#, not a text nit.
  - lightsabernames.xml naming lightsabers after Final Fantasy characters --
    the filer flagged this as a design call for the owner, not a bug.

    from absorption_content_fixes import apply_content_fixes
    apply_content_fixes(el)   # el is one top-level def Element, already
                               # parsed from the donor source

Keyed by defName -> {field path: (expected_broken_text_or_None, new_text_or_None)}.
`field path` is an ElementTree find() path relative to the def element (a
bare tag, or "parent/tag" for a nested field). If `expected_broken_text` is
given, the fix only applies when the field's CURRENT text matches it exactly
-- so if the donor source ever changes underneath this (a pack update), the
fix silently stops applying (reported via `note`) instead of overwriting
content nobody has re-checked. `new_text=None` means remove the field
instead of rewriting it (used for the one stray, non-applicable stat).
"""


class _Missing(object):
    """Sentinel for `expected_broken_text` meaning "the donor def has no such
    field at all". The fix then CREATES the field (inserted after <label> when
    there is one, else appended) instead of rewriting it, and is skipped -- as
    every other fix is -- if the donor has since grown a field of its own that
    nobody has re-checked."""

    def __repr__(self):
        return "MISSING"


MISSING = _Missing()

FIXES = {
    # Verbatim copy-paste: CrystalPart_heart's description was the sibling
    # CrystalPart_mantle's description under a different label/defName.
    "guy762_SWForceLightsabers_CrystalPart_heart": {
        "description": (
            "The Mantle of the Force is an item assembled by Suvam Tan from pieces found in the ruins of Exar Kun's temples on the fourth moon orbiting Yavin. It appears to be the remains of an even older artifact of unknown origin. It is not known if it was used by Exar Kun, or just uncovered when his temples were destroyed. Nor is it known what the original properties of the item were, but given the current abilities, in its original state it must have been fearsome indeed.\\n\\nThe Mantle is a crystalline lattice, resembling a lightsaber crystal in many ways, but having the additional property of being able to radically alter the flow of energy that passes through it. Additionally, the Mantle seems to almost act as a focusing tool for Force-sensitive individuals, leading to the idea that the original artifact may once have been a powerful tool of the Sith, or perhaps something they took with them when the dark Jedi originally split from the Order.",
            "The Heart of the Guardian shares the Mantle of the Force's crystalline lattice, recovered from the same ruined temples on Yavin's fourth moon, but where the Mantle unmakes and redirects the energy that passes through it, the Heart holds steady -- it seems built to anchor a wielder rather than to focus one, and radiates a faint warmth even when cut from its housing.",
        ),
    },
    # Donor placeholder "." left in place of real flavor text, ahead of the
    # generator-appended UPGRADE SLOTS block (compare guy762_vblade_sanasiki
    # or guy762_brifle_jurgan in the same packs, which both have real prose
    # here -- this is the shape every other entry in these files follows).
    "guy762_MalgusArmor": {
        "description": (
            ".\\n\\nUPGRADE SLOTS:\\n- Armor Underlay (heavy)\\n- Armor Overlay (heavy)\\n- Armor Tech",
            "Salvaged from Darth Malgus' own war-plate, this powered battle armor still carries the weight and menace of the man who wore it into the Jedi Temple itself.\n\nUPGRADE SLOTS:\n- Armor Underlay (heavy)\n- Armor Overlay (heavy)\n- Armor Tech",
        ),
    },
    "guy762_MalgusMask": {
        "description": (
            ".",
            "A rebreather mask built into Darth Malgus' armor, filtering the air around a face few ever saw whole.",
        ),
    },
    "guy762_MalgusHood": {
        "description": (
            ".",
            "The hood that completed Darth Malgus' silhouette, concealing the scarring beneath.",
        ),
    },
    "guy762_VisasHood": {
        "description": (
            "https://steamcommunity.com/sharedfiles/filedetails/?id=3378970100",
            "A hood cut for a blind seer who reads a room by touch and instinct rather than sight.",
        ),
    },
    "guy762_VisasRobes": {
        "description": (
            ".\\n\\nUPGRADE SLOTS:\\n- Armor Underlay (robe)",
            "Plain robes worn by a wanderer who trusts her other senses more than her eyes.\n\nUPGRADE SLOTS:\n- Armor Underlay (robe)",
        ),
    },
    # Typo: "wanteed" -> "wanted".
    "guy762_brifle_jurgan": {
        "description": (
            "Jurgan Kalta wanteed to make a big noise in the galaxy. If it was the screams of his enemies, all the better. This weapon was his favorite because it shared his adaptability.\\n\\nUPGRADE SLOTS:\\n- Scope\\n- Power Cell\\n- Firing Chamber\\n- Beam Splitter\\n- Trigger",
            "Jurgan Kalta wanted to make a big noise in the galaxy. If it was the screams of his enemies, all the better. This weapon was his favorite because it shared his adaptability.\n\nUPGRADE SLOTS:\n- Scope\n- Power Cell\n- Firing Chamber\n- Beam Splitter\n- Trigger",
        ),
    },
    # Stray stat: MeleeHitChance is a real StatDef (confirmed against the live
    # dump) but category PawnCombat, not Weapon -- it is computed per-pawn via
    # capacityOffsets/skillNeedOffsets/StatPart_Age, never read from a weapon's
    # own <statBases>, so setting it here is inert copy-paste debris, not a
    # balance change. Removing it changes nothing observable in play.
    "guy762_vblade_sanasiki": {
        "statBases/MeleeHitChance": ("1.2", None),
    },
    # CRYSTAL_INGEST_EXECUTION_1 item 3 (design/Jawa/mods/crystal_mods_inventory.md
    # ss3, ratified 2026-09-10): "fold the color naming into KOTOR_SmallCrystal_
    # orange's in-fiction identity so it reads as a Deeps mineral rather than a
    # leftover lightsaber-crystal palette." Text-only (fiction) -- defName, label,
    # graphicData/comps/modExtensions all UNCHANGED; the mineable still yields the
    # same guy762_crystalitem_orange lightsaber-crystal-part item. Scoped to the
    # orange member per the item's own wording; the other 6 colors + 3 medium + 2
    # large + Stygium share the same generic "It radiates with Force energy."
    # description and could get the same treatment in a follow-up pass.
    "KOTOR_SmallCrystal_orange": {
        "description": (
            "A small-sized crystal formation, warm to the touch. It radiates with Force energy.",
            "A small-sized crystal formation, warm to the touch. Down in the Lantern Deeps this "
            "warm-hued vein is prized as much for its glow as for the sliver of Force-attuned "
            "lattice at its core -- most who dig here are after light and heat, not a blade.",
        ),
    },
    # Three texture-distinct children shared the abstract base's placeholder
    # label/description verbatim instead of getting their own.
    "GS_Carpet_Star": {
        "label": ("large carpet", "star carpet"),
        "description": ("a big carpet", "a large carpet woven with a radiant star pattern"),
    },
    "GS_Carpet_cult": {
        "label": ("large carpet", "cult carpet"),
        "description": ("a big carpet", "a large carpet bearing an old cult's sigil"),
    },
    "GS_Carpet_forge": {
        "label": ("large carpet", "forge carpet"),
        "description": ("a big carpet", "a large carpet patterned after forge-guild ironwork"),
    },
}

# A cross-mod dependency this pack's OWN content creates, gated at generation
# time for the same "survive every regen" reason as FIXES above --
# DROID_RETIRE_KOTORDROIDS_1 traced 4 guy762_DroidWeapon_{microrocket,railgun,
# seekerrocket,trishot} ammo ThingDefs (consumed via <ammoDef>/<costList> by
# this pack's own ModularPartDefs_HelmetArmorTech.xml/_Wristgun.xml content)
# to guy762.mm.kotorcore's 1.6/AdditionalMods/_DroidsBase folder, which
# kotorcore's OWN LoadFolders.xml gates on IfModActive="guy762.KotORDroids"
# (confirmed; see gen_kotorcore_absorption.py's docstring, which deliberately
# never walks that folder -- it is out of scope for that generator too).
# Retiring guy762.kotordroids therefore silently stops that folder loading
# as well, discarding the 4 ammo ThingDefs out from under these 12 defs (6
# ModularPartsDef consumers + their 6 paired AbilityDefs) with no direct
# reference to kotordroids anywhere in kotorweapons' own source to warn a
# per-donor grep. Gate each with the same MayRequire value this pack's own
# TraderKindDefs already use for this identical dependency
# (Absorbed_KotorWeapons_{Base,Orbital}Trader_Baragwin.xml) -- accepting
# that each ability loses its ammo requirement entirely once kotordroids
# retires, per DROID_RETIRE_KOTORDROIDS_1 option 2 (gate, don't absorb).
MAYREQUIRE_FIXES = {
    "guy762_KotORpartArmorTech_kneerocket": "guy762.KotORDroids",
    "guy762_MW2WeaponVerbAbility_kneerocket": "guy762.KotORDroids",
    "guy762_KotORpartWristgun_trishot": "guy762.KotORDroids",
    "guy762_MW2WeaponVerbAbility_wristgun_trishot": "guy762.KotORDroids",
    "guy762_KotORpartWristgun_microrocket": "guy762.KotORDroids",
    "guy762_MW2WeaponVerbAbility_wristgun_microrocket": "guy762.KotORDroids",
    "guy762_KotORpartWristgun_seeker": "guy762.KotORDroids",
    "guy762_MW2WeaponVerbAbility_wristgun_seeker": "guy762.KotORDroids",
    "guy762_KotORpartWristgun_railgun": "guy762.KotORDroids",
    "guy762_MW2WeaponVerbAbility_wristgun_railgun": "guy762.KotORDroids",
    "guy762_KotORpartWristgun_flamethrower": "guy762.KotORDroids",
    "guy762_MW2WeaponVerbAbility_wristgun_flamethrower": "guy762.KotORDroids",
}

# A THIRD-generation consumer of the same gated parts: guy762_armband_wristgun
# (Absorbed_KotorWeapons_GadgetApparel_KotORModularWristLauncher.xml) lists
# guy762_KotORpartWristgun_microrocket as a CompProperties_ModularWeapon
# <defaultParts><li> -- a nested reference the whole-def MAYREQUIRE_FIXES
# above cannot reach, since guy762_armband_wristgun is not itself gated (it
# has other, ungated parts too). Found live 2026-09-10 when this exact gap
# produced the cross-reference error MAYREQUIRE_FIXES was built to prevent,
# one hop further down. Keyed by (owning ThingDef defName, partsDef value).
DEFAULT_PARTS_MAYREQUIRE_FIXES = {
    ("guy762_armband_wristgun", "guy762_KotORpartWristgun_microrocket"): "guy762.KotORDroids",
}


def apply_content_fixes(el, note=print, warn=None):
    """Mutate `el` (a top-level def Element already parsed from donor
    source) in place per FIXES (text/field fixes) and MAYREQUIRE_FIXES
    (whole-def MayRequire gating), both keyed by its own <defName>. No-op
    for either table the defName isn't in.

    FIXES additionally accepts an ABSTRACT def keyed by its Name= attribute, so
    a placeholder inherited by a whole variant family can be corrected once on
    the parent. MAYREQUIRE_FIXES stays defName-only -- gating an abstract would
    gate every child, which is never what is wanted.

    `warn` (falls back to `note` if the caller doesn't pass one -- this stays
    a no-crash no-op for any older caller) is used specifically for the two
    "the FIXES table's own expected_old no longer matches reality" cases --
    ABSORPTION_FIX_NEWLINE_ESCAPES_1: a mismatched expected_old means the fix
    is silently dead, which is exactly the class of bug that shipped 4 broken
    entries (real newlines in expected_old vs. the donor's literal backslash-n)
    for weeks with nobody noticing among routine NOTE lines. A caller whose
    Report distinguishes warn from note (gen_kotorweapons_absorption.py,
    gen_kotorcore_absorption.py) will surface these in its warnings count."""
    if warn is None:
        warn = note
    dn_el = el.find("defName")
    dn = dn_el.text.strip() if dn_el is not None and dn_el.text else None
    # Abstract defs carry no <defName>; FIXES may key them by Name=.
    fix_key = dn if (dn and dn in FIXES) else (el.get("Name") or dn)

    if dn and dn in MAYREQUIRE_FIXES:
        want = MAYREQUIRE_FIXES[dn]
        cur = el.get("MayRequire")
        if cur is None:
            el.set("MayRequire", want)
            note("MAYREQUIRE FIX APPLIED: %s -> MayRequire=%r" % (dn, want))
        elif cur != want:
            note("MAYREQUIRE FIX SKIPPED (already has different MayRequire=%r): %s" % (cur, dn))
        # else: already correctly gated (e.g. a future regen re-reading this
        # generator's own prior output) -- no-op.

    if dn:
        for li in el.iter("li"):
            pd_el = li.find("partsDef")
            if pd_el is None or not pd_el.text:
                continue
            key = (dn, pd_el.text.strip())
            if key not in DEFAULT_PARTS_MAYREQUIRE_FIXES:
                continue
            want = DEFAULT_PARTS_MAYREQUIRE_FIXES[key]
            cur = li.get("MayRequire")
            if cur is None:
                li.set("MayRequire", want)
                note("DEFAULT_PARTS MAYREQUIRE FIX APPLIED: %s <defaultParts> %s -> MayRequire=%r" % (dn, key[1], want))
            elif cur != want:
                note("DEFAULT_PARTS MAYREQUIRE FIX SKIPPED (already has different MayRequire=%r): %s / %s" % (cur, dn, key[1]))

    if not fix_key or fix_key not in FIXES:
        return
    dn = fix_key
    for path, (expected_old, new) in FIXES[dn].items():
        field_el = el.find(path)
        if expected_old is MISSING:
            # The donor is expected to have no such field; create it.
            if field_el is not None:
                note("CONTENT FIX SKIPPED (donor now has a %s of its own): %s" % (path, dn))
                continue
            if "/" in path:
                note("CONTENT FIX SKIPPED (MISSING only supports a top-level field): %s <%s>" % (dn, path))
                continue
            import xml.etree.ElementTree as _ET
            new_el = _ET.Element(path)
            new_el.text = new
            label_el = el.find("label")
            el.insert(list(el).index(label_el) + 1 if label_el is not None else len(el), new_el)
            note("CONTENT FIX APPLIED (added): %s <%s>" % (dn, path))
            continue
        if field_el is None:
            warn("CONTENT FIX SKIPPED (no such field): %s <%s>" % (dn, path))
            continue
        cur = field_el.text
        if expected_old is not None and cur != expected_old:
            warn("CONTENT FIX SKIPPED (donor text no longer matches expected): %s <%s>" % (dn, path))
            continue
        if new is None:
            if "/" in path:
                parent = el.find(path.rsplit("/", 1)[0])
            else:
                parent = el
            parent.remove(field_el)
            note("CONTENT FIX APPLIED (removed): %s <%s>" % (dn, path))
        else:
            field_el.text = new
            note("CONTENT FIX APPLIED: %s <%s>" % (dn, path))


# --------------------------------------------------------------------------
# BESTIARY_ARMOURY_DESC_BACKFILL_1, wave 1 (2026-09-11): the donor placeholder
# descriptions in the absorbed KotOR pools -- a literal "." on 42 defs (which
# 69 concrete defs inherit) and "An inconspicuous floor panel." on the four
# smuggling-compartment variants -- plus seven player-facing defs the donor
# shipped with no <description> at all. Written against each def's OWN fields
# (statOffsets, comps, race block), RSW tier register: nothing here names a
# campaign, a world or a faction that would not exist in another Star Wars
# scenario. Registered here rather than hand-edited into the generated XML so
# the next absorption regen keeps them.
DESCRIPTION_BACKFILL = {
    'guy762_SWGravshipOverlayBASE': (
        '.',
        'Starship hull plating laid over the deck as an outer shell. It carries no systems of its own; it is simply the part of the ship that takes the weather.',
    ),
    'guy762_DecorativeTerminalBase': (
        '.',
        'A powered display terminal wired to whatever holofeed is still broadcasting. Colonists will stop and watch it, though it holds their attention about as well as you would expect.',
    ),
    'guy762_KotORpartUnderlay_regen': (
        '.',
        'A mesh of biorestorative filaments worn against the skin, flooding wounds with clotting agents and growth stimulants. Injuries close markedly faster while it is worn.',
    ),
    'guy762_KotORpartUnderlay_strength': (
        '.',
        "A powered myomer weave that takes some of the load off the wearer's own muscles. It hits harder, carries more, and shrugs off pain that would drop an unassisted body.",
    ),
    'guy762_KotORpartUnderlay_armorweave': (
        '.',
        'A fire-resistant armorweave liner worn beneath the plate. It does nothing against a blade, but it is the difference between a scorch and a burn.',
    ),
    'guy762_KotORpartUnderlay_durasteel': (
        '.',
        "A layer of durasteel scale sewn into the suit's lining. It turns blades and blunt force alike, at the cost of every bit of speed the wearer had.",
    ),
    'guy762_KotORpartUnderlay_environment': (
        '.',
        'A sealed environmental liner circulating conditioned air through the suit. The wearer stops noticing the weather entirely, which on most worlds is worth the bulk.',
    ),
    'guy762_KotORpartOverlay_pockets': (
        '.',
        'Armorweave pouches and load loops stitched over the plate. Unglamorous, and the single most useful thing you can bolt onto a suit.',
    ),
    'guy762_KotORpartOverlay_heat': (
        '.',
        'Ablative heat shielding laid over the shell. It blunts blaster scoring and keeps the wearer from cooking inside their own armour.',
    ),
    'guy762_KotORpartOverlay_energy': (
        '.',
        'A layered energy-dispersive overlay that scatters an incoming bolt across the whole plate rather than one hole in it. Excellent against blasters, useless against a knife.',
    ),
    'guy762_KotORpartOverlay_ballistic': (
        '.',
        'Ballistic composite panels bonded to the outside of the suit. Made for slugthrowers and shrapnel, which the galaxy has never quite stopped producing.',
    ),
    'guy762_KotORpartOverlay_armorply': (
        '.',
        "Light armorply panels, matted and contoured to break up the wearer's outline. It adds nothing to the suit's protection; what it buys is free movement and a silhouette that game and sentries both miss.",
    ),
    'guy762_KotORpartUnderlay_forceweave_robe': (
        '.',
        'A robe lining woven from forceweave, a fibre that settles the mind of anyone attuned enough to notice. Psychic strain bleeds off faster while it is worn.',
    ),
    'guy762_KotORpartUnderlay_flex_hvy': (
        '.',
        'An articulated flex liner that lets heavy plate move like something much lighter. The wearer strikes and recovers faster, and is considerably harder to pin down.',
    ),
    'guy762_KotORpartOverlay_ablative_hvy': (
        '.',
        'Sacrificial ablative slabs bolted over heavy plate; every hit carries a little of the armour away with it. Heavy, slow, and very good at surviving blaster fire.',
    ),
    'guy762_KotORpartOverlay_bonded_hvy': (
        '.',
        "Bonded composite plates layered over the suit's shell. They spread the shock of a hit across the whole assembly instead of one unlucky rib.",
    ),
    'guy762_KotORpartOverlay_hvybonded_hvy': (
        '.',
        'The heaviest bonded plating a body can be made to carry. Very little gets through it, and the wearer will not be outrunning anything again.',
    ),
    'guy762_KotORpartOverlay_beskar_hvy': (
        '.',
        'Plates of beskar, the Mandalorian iron that turns blaster bolts and holds against a lightsaber. Priceless, absurdly heavy, and worth every kilogram.',
    ),
    'guy762_KotORpartCore_plastoid': (
        '.',
        'A hollow plastoid core, chosen when speed matters more than force. The weapon becomes very fast and very light, and lands like a training bar.',
    ),
    'guy762_KotORpartCore_bronzium': (
        '.',
        'A bronzium core, balanced rather than heavy. It brings the weapon quickly back on line and sits well in the hand.',
    ),
    'guy762_KotORpartCore_uranium': (
        '.',
        'A depleted uranium core. Dense enough to punch through armour, and slow enough that the wearer of that armour may see it coming.',
    ),
    'guy762_KotORpartCore_durasteel': (
        '.',
        'A solid durasteel core. Nothing clever about it - the weapon is simply heavier, and lands harder for it.',
    ),
    'guy762_KotORpartCore_plasteel': (
        '.',
        'A plasteel core: light, stiff and unwilling to bend. The weapon comes back on guard faster and lands where it was aimed.',
    ),
    'guy762_KotORpartCore_beskar': (
        '.',
        'A beskar core, heavy as a bar of lead and just as forgiving to swing. What it loses in speed it repays by going through armour as though it were not there.',
    ),
    'guy762_KotORpartHelmetTech_verpine': (
        '.',
        'Verpine optics grafted into the helmet, ranging and correcting faster than the eye behind them. The wearer settles onto a target quickly and rarely misses it.',
    ),
    'guy762_KotORpartHelmetTech_neural': (
        '.',
        'Neural stabilizers clamped to the base of the skull, damping pain signals and the panic that follows them. The wearer stays standing, and stays sane, well past the point most would not.',
    ),
    'guy762_KotORpartHelmetTech_lightscan': (
        '.',
        'A visor that paints a low-power scanning grid across the ground ahead. Tripwires and pressure plates light up before a boot finds them.',
    ),
    'guy762_KotORpartHelmetTech_demovisor': (
        '.',
        'A demolitions visor with the full ordnance suite: trap detection, fuse reading and firing solutions. Sappers and mortar crews are markedly better at their work, and markedly more likely to survive it.',
    ),
    'guy762_KotORpartHelmetTech_medical': (
        '.',
        "A field surgeon's visor, overlaying anatomy, vitals and procedure onto whatever is bleeding in front of it. It turns a competent medic into a very good one.",
    ),
    'guy762_KotORpartHelmetTech_breathmask': (
        '.',
        'A sealed rebreather and scrubber stack fitted into the helmet. The wearer can work in fumes, spores and fallout and walk out unbothered.',
    ),
    'guy762_KotORpartHelmetTech_regal': (
        '.',
        "Inlay, filigree and a great deal of expensive trim added to an otherwise sensible helmet. It does nothing for the wearer's safety and a great deal for how seriously anyone takes them.",
    ),
    'guy762_KotORpartHelmetTech_interface': (
        '.',
        "A technician's interface visor, talking directly to whatever machine the wearer is standing in front of. Schematics, fault codes and access ports resolve themselves without a datapad.",
    ),
    'guy762_KotORpartArmorTech_bootspikes': (
        '.',
        'Retractable spikes set into the boot soles. They give the wearer something to fight with when both hands are already occupied.',
    ),
    'guy762_KotORpartArmorTech_stabilizer': (
        '.',
        "Gyroscopic stabilizers built into the suit's frame, holding the wearer upright and on aim. Being hit no longer costs them the next few seconds.",
    ),
    'guy762_KotORpartArmorTech_strength': (
        '.',
        'Powered amplifiers in the gauntlets and shoulders, adding to whatever the wearer can already do with their arms. Purely a melee upgrade.',
    ),
    'guy762_KotORpartArmorTech_dex': (
        '.',
        "A full plasteel exoskeleton carrying the suit's weight so that the body inside does not. The wearer moves faster, dodges better and hauls more than should be possible in armour.",
    ),
    'guy762_KotORpartArmorTech_EVA': (
        '.',
        'Cold-gas verniers mounted at the hips and shoulders for work outside a hull. In vacuum the wearer moves three times as fast; in atmosphere they are four kilograms of dead weight.',
    ),
    'SWPotF_RaceDef_ysalamir': (
        '.',
        'A slow, claw-footed tree lizard whose living body nullifies psychic sensitivity in everything near it. It eats almost nothing, lays eggs and takes training well; keeping one close is a dependable way to make a psychic problem stop being a problem.',
    ),
    'guy762_RebelPilot_suitbox': (
        '.',
        'The chest-mounted life-support pack of a starfighter flight suit. It seals the wearer against cold and vacuum and steadies their hands at the controls, but it will not stop so much as a thrown rock.',
    ),
    'guy762_ImpWorkerHelmet': (
        '.',
        "An Imperial labour helmet, sealed against fumes and dust and rigged to speed the cutting and smoothing of stone. It is armoured better than most soldiers' headgear, which says something about Imperial worksites.",
    ),
    'guy762_SithMask_marauder': (
        '.',
        "A Sith Marauder's neck guard, worked in polished dark alloy. It covers the throat and very little else - a Marauder is not expected to be struck anywhere a neck guard would help.",
    ),
    'guy762_SithMask_colormarauder': (
        '.',
        "A Sith Marauder's neck guard, left plain so it can be dyed to a master's colours. It covers the throat and very little else.",
    ),
    'guy762_SecretFloorPanel_darkwhiteoutlines': (
        'An inconspicuous floor panel.',
        "An inconspicuous floor panel with a smuggler's void cut in beneath it. It swallows a startling amount of cargo and runs cold enough to keep it, and anyone crossing it sees nothing but deck. Finished in hangar plate, white-lined on dark grey.",
    ),
    'guy762_SecretFloorPanel_DoomgiverTile': (
        'An inconspicuous floor panel.',
        "An inconspicuous floor panel with a smuggler's void cut in beneath it. It swallows a startling amount of cargo and runs cold enough to keep it, and anyone crossing it sees nothing but deck. Finished in the heavy dark plate of a capital warship deck.",
    ),
    'guy762_SecretFloorPanel_DreadnaughtCabinTile_blue': (
        'An inconspicuous floor panel.',
        "An inconspicuous floor panel with a smuggler's void cut in beneath it. It swallows a startling amount of cargo and runs cold enough to keep it, and anyone crossing it sees nothing but deck. Finished in blue dreadnaught cabin tile.",
    ),
    'guy762_SecretFloorPanel_DreadnaughtCabinTile_black': (
        'An inconspicuous floor panel.',
        "An inconspicuous floor panel with a smuggler's void cut in beneath it. It swallows a startling amount of cargo and runs cold enough to keep it, and anyone crossing it sees nothing but deck. Finished in black dreadnaught cabin tile.",
    ),
    'guy762_SWGravshipOverlay_DynamicFreighter': (
        MISSING,
        'Hull plating in the Dynamic-class pattern - a mid-bulk hauler flown on every run where the cargo is legal and the margins are not.',
    ),
    'guy762_SWGravshipOverlay_KT400Freighter': (
        MISSING,
        'Hull plating in the KT-400 pattern, a light freighter built in enormous numbers and flown long past the point of sense.',
    ),
    'GS_Banner_Cult': (
        MISSING,
        'A long hanging banner bearing the sigil of an Imperial cult. Hung in a corridor, it announces at some length whose corridor it is.',
    ),
    'GS_Banner_Forge': (
        MISSING,
        'A hanging banner marked with an Imperial forge sigil - the same stamp found on ordnance crates, worn here at three metres tall.',
    ),
    'GS_Banner_Star': (
        MISSING,
        'A hanging banner bearing the Imperial star. Standard issue for any wall the Empire intends to be seen owning.',
    ),
    'GS_ImperialLamp': (
        MISSING,
        'A tall Imperial standard lamp built for open ground. It throws a hard, even light across a wide arc, and draws power steadily to do it.',
    ),
    'KotOR_watertank': (
        MISSING,
        'A pressed-metal water tank of the sort bolted beside every moisture farm and dust-side outpost. This one is a prop: nothing can be drawn from it.',
    ),
    'SWCPTerrain_junkyardgarbage': (
        MISSING,
        "Ground so thoroughly buried in scrap and packaging that the soil beneath is a rumour. Walking it is slow, and nobody has ever called it pretty.",
    ),
    'SWCPTerrain_junkyardgarbage_soggy': (
        MISSING,
        "Trash that has been rained on long enough to rot down into sediment. It sucks at the boots and it stinks.",
    ),
}

for _key, (_old, _new) in DESCRIPTION_BACKFILL.items():
    FIXES.setdefault(_key, {})["description"] = (_old, _new)
