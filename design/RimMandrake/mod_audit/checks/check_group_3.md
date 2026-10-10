# Mod audit check, group 3 (batches 10-13)

Checker: claude-opus-5-5, 2026-10-10, offline. Rows: `check_group_3.jsonl` (one per mod; corrections carry
old/new/evidence; the assessor files are untouched).

## Counts

| batch | mods | AGREE | AMEND | CHALLENGE |
|---|---|---|---|---|
| 10 factions_pawns | 49 | 36 | 9 | 4 |
| 11 weapons_apparel | 22 | 20 | 1 | 1 |
| 12 buildings_production | 43 | 31 | 12 | 0 |
| 13 misc_content_1 | 48 | 35 | 11 | 2 |
| **total** | **162** | **122** | **33** | **7** |

(Batch 11/12 AGREE counts include rows with verified notes and no correction.) Every card_worthy, ELIMINATE
and REPLACE row was opened by hand (REPLACE: none in this group). The rest were re-derived mechanically
from `facts/mod_facts.jsonl`: patched_by_ours counts per mod, dependants, memory/size/log severities
against RUBRIC §3 thresholds, and source url/confidence. That pass found almost nothing wrong. One size
severity was wrong, one 404 repo was labelled MEASURED, and one "patched_by_ours_refs 2" was really 0 xpath
refs. The first pass is reliable on numbers and weak on rulings.

## Systematic first-pass errors

1. **Missed owner rulings that live outside `design/Jawa/mods/`.** Assessors searched the mod docs.
   They did not search the ledger, commit bodies or the headers of our own patches. One closed item,
   `DONOR_FACTION_PROPER_NOUN_RENAMES_1` (owner 2026-09-11, `8e1ea6c3d` + `6cadd01c4`), had already
   settled four of this group's open questions:
   - Orc Clan was rethemed to Gamorrean Clan.
   - MiningCo. was rethemed to Czerka.
   - Big and Small Races was cut whole.
   - The renaming of the Dark Ages troll faction was dropped.
   Two more rulings were missed in the same way: Route B fog (`OPUS5_HANDOFF.md:179`) and the Factional
   War FULL ACCEPT (`required_mods.md:887`).
2. **Content cut by Cherry Picker is invisible to the def census.** Four mods in this group are shells, or
   part-shells, whose content Cherry Picker already removed: `xmb.ancienturbanruins.mo`,
   `redmattis.bigsmall`, `shavius.medieval.flavour` (26 of 27 cut) and part of
   `neronix17.outland.genetics`. They got three different verdicts. They should get one verdict and one
   owner card (below).
3. **Citation drift.**
   - The auto-defense rule is `forbidden_mods.md:65`, not `required_mods.md:65`. This affects 3 rows.
   - `required_mods.md:930` was read as a general "cut deck-footprint mods" ruling. It is the PARK
     condition on Complementary Odyssey alone. This affects 3 rows.
   - Two rows place the 2026-09-11 permanent-resident ruling in `forbidden_mods.md`. It is in
     `mod_config_rulings.md:71`.
   - The crypts row cites the proper-noun backlog, which does not list that mod.
4. **Our own log errors were charged to donors.** Every "Config error in X: same research view coords and
   tab as Y (RUT_Tree_Hearth)" is caused by our hand-authored `RUT_ResearchTabAssign.xml`. Those errors
   belong to `mandrake.rut.researchretag`, not to Roots of Rimworld or DBH Lite. Separately, the 51
   Biomes! Fossils errors are Scribe dead references held in the save, yet the mod was charged
   severity 3.
5. **`dependants_ours` blind spots.** It reads empty in four cases where we really do depend on the mod:
   - Our founders' xenotype carries two Gender Works genes with no guard (`MandrakeJawaXenotype.xml:143-144`).
   - Our absorbed blast doors use Doors Expanded classes.
   - Our absorbed hand defs use Show Me Your Hands' def type.
   - We ship Better Trees immunity patches.
6. **Card inflation.** Seven rows were marked card-worthy when the question was really a measurement
   against an existing ruling, or a question already asked on another row. Examples: is CAI fog off, is
   the Deep Storage cap set, are DBH Lite toilets off, can a VF vehicle reach the seabed, are wagons in
   scope. Two rows had the opposite problem: they asked the owner about something he had already ruled
   on (Factional War, slavery).

## The 10 highest-impact corrections

1. **`karew.orcclan`: CHALLENGE, ELIMINATE → KEEP-TEMPORARILY-THEN-PHASE-OUT.** The assessor said 9 of
   our 11 refs exist only to defuse it. They are an owner-ruled retheme to "Gamorrean Clan"
   (`OrcClan_GamorreanRename.xml`).
2. **`redmattis.bigsmall`: CHALLENGE, KEEP-TEMPORARILY → ELIMINATE (shared card).** All 86 defs were
   Cherry-Picker cut on 2026-09-11 (`6cadd01c4`), so the card question was already answered.
3. **`mlie.miningcospaceship`: CHALLENGE, card withdrawn.** It has already been rethemed to Czerka
   (`MiningCo_CzerkaRename.xml`), so its fit becomes neutral.
4. **`lovelydovey.sex.withrosaline`: AMEND.** It is a hard dependency of the six founders, through
   SEX_AlwaysAphrodor and SEX_Ovipositor carried with no guard on MandrakeJawa. The facts show 0 edges.
5. **`sr.modrimworld.factionalwarcontinued`: CHALLENGE, card withdrawn.** The owner gave it a FULL ACCEPT
   on 2026-08-06.
6. **`vesper.egihologramsandprojectors`: CHALLENGE, ELIMINATE → KEEP-TEMPORARILY, card.** Holograms are
   on-genre (the owner ruled the gods are holograms), so the dissonance is unproven. The real issue is
   its 1.5 GB texture proxy.
7. **`xmb.ancienturbanruins.mo`: AMEND.** It was left in the list on purpose: the audit recommends
   "via Cherry Picker, not uninstall, per doctrine". ELIMINATE therefore overturns a doctrine, and that
   is the real card.
8. **`mlie.nwnrealfogofwar`: AMEND, card withdrawn.** Route B rules that CAI's fog stays off.
   `FOW_ROUTE_B_INTEGRATION_1` verified it.
9. **`ghost.rootsofrimworld` and `dubwise.dubsbadhygiene.lite`: AMEND.** Their research-tab collision
   errors are ours. They need fixing in `RUT_ResearchTabAssign.xml`, not in these donors. Lite's card is
   also withdrawn: `required_mods.md:581` adopts "NOTHING else from the DBH family".
10. **`shavius.medieval.flavour`: AMEND.** 26 of its 27 backstories are already cut. Save placement is
    MEASURED: one pawn carries `SH_MED_MedievalAlchemist`, so swap it before removal.

Also notable:
- `heatherathebyne.craftingspotslavegear`: CHALLENGE, → KEEP. Slavery is in scope by owner adoption
  (`required_mods.md:1170-1172`).
- `deon.rimtek.digipal`: CHALLENGE. A datapad is not dissonant, and the RimTek trio's verdicts
  contradict each other.

## Ruling conflicts and cross-batch inconsistencies (for the owner or the merge step)

- **Physically remove Cherry-Picker-cut shells, or keep them?** The trim-not-uninstall doctrine
  (`01_campaign.md` pillars; `ancient_ruins_mod_audit.md` §Recommendation) runs against the 8-10 TPS
  measured on the 550-mod list. One card covers `xmb.ancienturbanruins.mo` (+aurad, aurvl in batch 14),
  `redmattis.bigsmall` and `shavius.medieval.flavour`.
- **Alpha Animals and Alpha Memes.** The 2026-09-11 "permanent resident" ruling
  (`mod_config_rulings.md:71`) conflicts with the 2026-09-20 "move everything to our own defs" ruling
  (`DONOR_DEFS_PORT_TO_OURS_1`). The assessor flagged this correctly; it stays open.
- **RimAI Core.** It was adopted on 2026-08-07 and limited to voice-only by `mod_config_rulings.md:66`.
  The later `claude -p`-only rule (2026-09-05) conflicts with it. Fit should be dissonant.
- **Yayo's Combat 3 vs the Combat Extended ban.** The ban covers "equivalent total combat overhauls"
  (`forbidden_mods.md:151-153`), while our weapon register's AP calibration depends on Yayo's numbers.
  This is a real card.
- **RimTek family.** `deon.rimtek.core` got ELIMINATE (batch 01, group 1), `deon.rimtek.docmate` got KEEP
  (batch 12) and `deon.rimtek.digipal` got ELIMINATE (batch 11). Keeping docmate requires keeping core.
- **Fog.** Batch 12's NWN row asked a question that batch 13's CAI row answers from the same ruling.
- **Titan.** `xylthixlm.races.core` was carded while `xylthixlm.races.titan`, the mod it exists for, was not.
