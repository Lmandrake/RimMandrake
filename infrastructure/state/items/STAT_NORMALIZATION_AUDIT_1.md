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

*(The owner's four rulings that widened this scope are recorded once, below,
under "Owner RULED". The field list here is the widened one.)*

1. **Census.** Read the campaign's active mod list (⚠️ **NOT** the live
   `ModsConfig.xml` while a minimal-list swap is in effect — see the Instrument
   note in the census doc) and, for every active third-party mod, determine
   whether it actually modifies any of:
   - Animal combat/damage stats (melee/ranged damage, verbs, armor, health)
   - Animal rarity/commonality/spawn weighting (wild spawn rates, biome animal
     tables, "dangerous animals" difficulty knobs)
   - Animal appearance (retextures, recolors, size/scale overrides)
   - Animal body size / `bodySizeFactor`-style stat overrides
   - Plant parameters (growth rate, yield, harvest work, wild plant density)
   - **(widened)** Weapon damage / armour penetration / accuracy / cooldown
   - **(widened)** Apparel armour ratings, insulation, equipped stat offsets
   - **(widened)** Work-speed, research-speed, construction/mining multipliers,
     `WorkToBuild`/`WorkToMake`, recipe work amounts
   - **(widened)** Market values, costLists, and any global `StatDef` retune
   Do not trust a mod's NAME to answer this — open its actual Defs/Patches and
   confirm mechanically. A mod named suggestively but touching none of the above
   is a false positive; a plainly-named mod that turns out narrower than
   expected should be characterized by what it ACTUALLY does.
   🔴 **A pure-C# mod has no XML to scan** and will be invisible to any
   Defs/Patches sweep — the exact gap `outgrown_audit_2026-08-30.md` flagged in
   its own honesty note. Those are found by their Keyed/Settings strings and
   assembly, not by grepping Defs.

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

## CENSUS + WAVE PLAN DELIVERED (FOUNDRY, 2026-09-09, offline — game mid-reboot)

📄 **`design/Jawa/mods/stat_normalization_audit_2026-09-09.md`** — the full
census, the per-mod save cross-reference table, and the four waves.

**Instrument used** (and why not the live file): the census ran against
`infrastructure/state/modlists/ModsConfig_before_droid_donor_fix_2026-09-09.xml`
(mtime 13:38, **587 `<activeMods>`**) because the live `ModsConfig.xml` held a
6-mod minimal list at census time. The campaign save's own `<modIds>` (590)
differs from that snapshot by exactly the three droid mods being reverted
tonight and nothing else, which is what makes the snapshot trustworthy.
⚠️ A final cross-check against the live file is OWED once the full list is
restored — not this item's job.

**Numbers**: 587 active mods walked, every one's own XML opened (names never
trusted); **131** carry a PatchOperation landing on a balance-number surface,
**124** of them third-party; **31 are real conflicts**. 90 active mods are
pure-C# and invisible to any Defs/Patches sweep — those were characterised from
About/Keyed/`Config/Mod_*.xml` and are marked as characterisations, not
measurements. 23 mods sit in the cosmetic-only bucket.

**Waves**: 1 — 13 mods, zero content, zero save presence (quick, real win).
2 — 9 save-clean but content-bearing (a keep-or-port sitting). 3 — 6 entangled
with open research/work-economy items. 4 — the rest, several of which are
**NOT retirable** and are recommended as permanent keeps.

**Top finding**: `fluxilis.germanquality` ("Quality Affects HP") is a
1,114-byte, zero-def mod that adds a `StatPart_Quality` to `MaxHitPoints` —
**0.5× awful to 10× legendary, globally, on everything with a quality level**.
It is the widest silent multiplier in the stack and costs nothing to remove.
Runner-up, and the mod the owner was remembering: `zylle.moredangerousgame`, a
C# predator/prey and revenge overhaul with no settings file ever written.

🔴 **Save-cross-reference landmine the mod-graph check would have missed**:
`sarg.alphabiomes` holds **23,819 placed `AB_Obsidianstone` instances** in
`CANONICAL_ASHKARR_2026-09-09.rws`, and ten of our 23 painted biomes are its
BiomeDefs. No active mod declares a dependency on it — it would have read as
retirable and taken the campaign with it. Same shape one order down:
`grimterra.biomesmod` (782 placed), `sarg.alphamemes` (622), `regrowth.botr.core`
(563), `oskarpotocki.vfe.tribals` (312), `vanillaexpanded.vmemese` (234).

**Nothing was retired. `ModsConfig.xml` was not touched.** Four questions for
the owner are at the foot of the census doc; the item stays open for his ruling.
