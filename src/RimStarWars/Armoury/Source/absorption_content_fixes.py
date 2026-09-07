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

FIXES = {
    # Verbatim copy-paste: CrystalPart_heart's description was the sibling
    # CrystalPart_mantle's description under a different label/defName.
    "guy762_SWForceLightsabers_CrystalPart_heart": {
        "description": (
            "The Mantle of the Force is an item assembled by Suvam Tan from pieces found in the ruins of Exar Kun's temples on the fourth moon orbiting Yavin. It appears to be the remains of an even older artifact of unknown origin. It is not known if it was used by Exar Kun, or just uncovered when his temples were destroyed. Nor is it known what the original properties of the item were, but given the current abilities, in its original state it must have been fearsome indeed.\n\nThe Mantle is a crystalline lattice, resembling a lightsaber crystal in many ways, but having the additional property of being able to radically alter the flow of energy that passes through it. Additionally, the Mantle seems to almost act as a focusing tool for Force-sensitive individuals, leading to the idea that the original artifact may once have been a powerful tool of the Sith, or perhaps something they took with them when the dark Jedi originally split from the Order.",
            "The Heart of the Guardian shares the Mantle of the Force's crystalline lattice, recovered from the same ruined temples on Yavin's fourth moon, but where the Mantle unmakes and redirects the energy that passes through it, the Heart holds steady -- it seems built to anchor a wielder rather than to focus one, and radiates a faint warmth even when cut from its housing.",
        ),
    },
    # Donor placeholder "." left in place of real flavor text, ahead of the
    # generator-appended UPGRADE SLOTS block (compare guy762_vblade_sanasiki
    # or guy762_brifle_jurgan in the same packs, which both have real prose
    # here -- this is the shape every other entry in these files follows).
    "guy762_MalgusArmor": {
        "description": (
            ".\n\nUPGRADE SLOTS:\n- Armor Underlay (heavy)\n- Armor Overlay (heavy)\n- Armor Tech",
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
            ".\n\nUPGRADE SLOTS:\n- Armor Underlay (robe)",
            "Plain robes worn by a wanderer who trusts her other senses more than her eyes.\n\nUPGRADE SLOTS:\n- Armor Underlay (robe)",
        ),
    },
    # Typo: "wanteed" -> "wanted".
    "guy762_brifle_jurgan": {
        "description": (
            "Jurgan Kalta wanteed to make a big noise in the galaxy. If it was the screams of his enemies, all the better. This weapon was his favorite because it shared his adaptability.\n\nUPGRADE SLOTS:\n- Scope\n- Power Cell\n- Firing Chamber\n- Beam Splitter\n- Trigger",
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


def apply_content_fixes(el, note=print):
    """Mutate `el` (a top-level def Element already parsed from donor
    source) in place per FIXES, keyed by its own <defName>. No-op if the
    defName isn't in FIXES."""
    dn_el = el.find("defName")
    dn = dn_el.text.strip() if dn_el is not None and dn_el.text else None
    if not dn or dn not in FIXES:
        return
    for path, (expected_old, new) in FIXES[dn].items():
        field_el = el.find(path)
        if field_el is None:
            note("CONTENT FIX SKIPPED (no such field): %s <%s>" % (dn, path))
            continue
        cur = field_el.text
        if expected_old is not None and cur != expected_old:
            note("CONTENT FIX SKIPPED (donor text no longer matches expected): %s <%s>" % (dn, path))
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
