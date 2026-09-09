# STAT_NORMALIZATION_AUDIT_1

Owner, verbatim (2026-09-09): "Assess our mod stack to see if anything is messing
with the numbers we might be about to normalize. Things adjusting animal damage,
rarity, appearance, size, or plants and their parameters including growth rates.
I'm remembering wild animal spawn, dangerous animals, and other mods. We likely
won't need any of those things anymore now that we're just owning our whole
loadout. Find all such conflicting influences and make a plan to assess them for
retirement so we don't end up including them and then normalizing against their
modifications pointlessly."

## spec

**This is a census + risk-ordered retirement PLAN. Do not retire anything in this
pass.** Mirror `STARWARS_DONOR_SUNSET_1`'s scoping discipline (measured candidate
table, waves by real risk, nothing touched live).

1. **Census.** Read the live `ModsConfig.xml` (whatever it says at the time you
   run, note the count) and, for every active third-party mod, determine whether
   it actually modifies any of:
   - Animal combat/damage stats (melee/ranged damage, verbs, armor, health)
   - Animal rarity/commonality/spawn weighting (wild spawn rates, biome animal
     tables, "dangerous animals" difficulty knobs)
   - Animal appearance (retextures, recolors, size/scale overrides)
   - Animal body size / `bodySizeFactor`-style stat overrides
   - Plant parameters (growth rate, yield, harvest work, wild plant density)
   Do not trust a mod's NAME to answer this — open its actual Defs/Patches and
   confirm mechanically. A mod named suggestively but touching none of the above
   is a false positive; a plainly-named mod that turns out narrower than
   expected should be characterized by what it ACTUALLY does.

2. **Overlap check — this is the part that matters.** For each candidate mod,
   determine whether its patches apply to:
   (a) vanilla defs we still use unmodified,
   (b) donor defs we have already absorbed into our own tier (RM_/RSW_/RUT_),
   or (c) our own authored defs directly.
   (b) and (c) are the real conflict — a future normalization pass tunes OUR
   numbers, and a third-party mod silently re-multiplying them on top makes
   that tuning meaningless. (a) is lower priority but still worth naming.

3. **🔴 Save cross-reference check before recommending retirement of ANY mod.**
   Tonight (2026-09-09) two separate donor retirements (`STARWARS_DONOR_SUNSET_1`
   Wave 4, `DROID_RETIRE_DEPOT_ASIMOV_1`) each passed a thorough whole-active-
   mod-list dependency check and were still unsafe — the live CAMPAIGN SAVE held
   direct cross-references to the donors' defs (placed pawns/objects), which a
   mod-to-mod XML dependency check cannot see. Both had to be reverted live and
   cost three consecutive game reboots. For every mod you flag as a retirement
   candidate, also check the actual campaign save file for defName references
   tied to that mod (see the `rimworld-savegame` skill — this is doable OFFLINE
   by reading the `.rws` directly, no bridge needed) before calling it safe.
   Name this check explicitly in your output per mod, don't just imply it.

4. **Waves.** Group findings into risk-ordered waves the same way
   `STARWARS_DONOR_SUNSET_1` did: genuinely-quick/no-touch first, entangled-with-
   other-open-items next, needs-an-explicit-owner-call last (e.g. anything where
   cutting it would also remove content nobody has decided whether to port).

## verify
Every mod named in the census has been opened and read (not name-guessed); every
retirement candidate has both a mod-list dependency finding AND a save cross-
reference finding recorded; waves are ordered by real measured risk, not
alphabetically or by guess.

## criteria
A written census + wave plan exists in this item file (or a linked doc under
`design/Jawa/` if long), covering every currently-active mod touching animal or
plant balance parameters, with the save-cross-reference check done for every
retirement candidate. Nothing is retired by this item — that is explicitly
follow-on work for whoever executes a wave.

## Owner RULED — question cards, 2026-09-09

1. **Scope WIDENED**: not fauna/flora only — any third-party mod touching
   damage, armor, work-speed, or other gameplay-number balance (weapons,
   apparel, pawn stats included), since all of it conflicts with a future
   own-numbers normalization pass the same way.
2. **Cosmetic-only mods (zero gameplay-number impact) get their own separate,
   lower-priority bucket** — flagged, not dropped, not merged into the main
   numeric-conflict list.
3. **No specific mod names supplied** — census proceeds as pure from-scratch
   discovery, exactly as scoped.
4. **Mods that ADD unique content (new creatures/plants) alongside rebalancing
   existing ones get flagged separately from pure knob-turners**, with an
   explicit "retiring this loses content X unless ported first" note — same
   treatment this repo's donor-retirement items already give absorbable
   content.

⚠️ **Modlist-source correction, same day**: at the time this ruling landed, the
live `ModsConfig.xml` held only ~11 entries — a temporary minimal list another
agent had swapped in for fast crash-recovery quicktest iteration, NOT the
owner's real campaign list. The census must NOT be built against the live file
in that state; use `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`
or the most recent dated full-list backup, and cross-check against the live
file once the full list is confirmed restored.
