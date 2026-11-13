# ExplosiveKnockback: parked for you (ceiling)

his card 2026-11-13 ~11:55 PST (OWNER:1794599570900465333) allowed one more judge: rm-coverage-judge-1794599960 not_covered, 6 gaps (1 new: sweep animal/mech masses unpinned under creatureMassLimit 90; 5 carried as unfixed only because no coverage_fixes.json claim was written, its reasons say they look fixed); no second judge. Nothing runs on it, no Designer run and no judge, until your word on RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH. Item RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH, stage 5 (Lock).

## QUICK LOOK OFFERED

Enough code exists (20 built capabilities: inv_kernel, inv_hook, inv_pawn_flyer, inv_which_blasts, inv_items_teleport, inv_shelf_skip, inv_who_is_spared, inv_shield, inv_recovery, inv_caps, inv_settings, inv_pits_receive, inv_pit_floor_haul, inv_proof_scenes, inv_weapon_ext_fields, inv_killed_corpse, inv_pit_floor_goods_stay, inv_big_corpse_spared, inv_mass_limit_skip, inv_too_weak_skip). A short look in game could settle these 6 gaps at once.

## Settled

- Stages accepted: 0 Read, 1 Argue the idea, 2 Argue the edge, 3 Write, 4 Exam.
- Root: Every blast in RimWorld now throws what it hits. A mortar shell beside a colonist hurls them three cells straight away from it, clean over sandbags, until a wall stops them hard; anything light goes too, so loose goods and corpses fly through the air, spinning and rebounding off walls, and no open shelf keeps them safe. When gas catches, it goes off clump by clump, each small burst scattering whatever lies near it, as the fire whooshes through the whole cloud. And where a blast meets a pit, its cover breaks and whoever it throws in falls.
- 46 decisions on record, 29 tree leaves, 30 inventory capabilities.

## Refused, and why

The coverage judge (rm-coverage-judge-1794599960) says not covered: The five carried gaps (g1 to g5) look fixed in the entries shown, though none was claimed, and I do not repeat them. The flowworks dependency now matches Cauldron About.xml. sc_mass_and_power has an injury-absorbing hook, the thrumbo at the 250 kg limit is staged at 1 then 3 cells, and the colonist band is 64 to 76 kg. The kernel arithmetic, re-run from RM_KnockbackMath.cs, gives every stated cell count. The thrumbo's 240 kg checks out from its defs (Mass 60 x body size 4) [measured]. The sweep now names only the free-flying pawns as going farther. inv_who_is_spared has its coverage_rest entry back by sc_spared, and the showcase check prints 'showcase set accepted'. One change opens a new gap: the sweep's new creatureMassLimit 90 run pins only the second animal's mass. An unweighed 'animal' or 'mech' over 90 kg would also be skipped and break 'each change alters only its own outcome'. It is a one-line edit to scenes.json, so the verdict is not_covered.
1. sc_settings_sweep's creatureMassLimit 90 run expects only the second animal to be skipped, but the lane's 'an animal' and 'a mech' have no mass assertion, so a correct build that also skips either one (any of them over 90 kg) fails 'each change alters only its own outcome' (scenes.json sc_settings_sweep: start lane line (245), action (251), expect (252); ids settings_scale_and_switch, inv_creature_mass_limit, inv_settings; returns to stage 3)
2. The Cauldron's dependency list stated in the gas scenes omits mandrake.rm.flowworks, so three scenes state and assert an incomplete list (scenes.json sc_gas_chain, sc_cauldron_gas, sc_settings_sweep start lines (the same wording in sc_cover_breaks and sc_gas_shove_into_pit); ids inv_gas_chain, inv_gas_tags, gas_goes_clump_by_clump, our_gases_burn, inv_settings, settings_scale_and_switch; returns to stage 3)
3. sc_mass_and_power stages real Bomb damage (50, then 100) one cell from a rat and a colonist, with nothing to keep them alive, yet expects each thrown creature 'alive and stunned' at its kernel cells (scenes.json sc_mass_and_power start (blast line) and expect; tree.json heavier_flies_less; ids heavier_flies_less, inv_blast_power_damage; returns to stage 3)
4. sc_mass_and_power's stated numbers do not match its leaf or its own assertion band: the leaf oracle's thrumbo '1 then 3 cells' is never staged, and the colonist band of 60 to 90 kg lets a correct build fail the strict order (tree.json heavier_flies_less oracle_proposed; scenes.json sc_mass_and_power start (masses), expect, control; ids heavier_flies_less; returns to stage 3)
5. sc_settings_sweep expects the double-damage blast to throw 'each pawn farther' than the frag grenade, which is false for the lane pawns a wall, a door or a shield belt holds (scenes.json sc_settings_sweep expect (blastPowerFromDamage clause); ids settings_scale_and_switch, inv_settings, inv_blast_power_damage; returns to stage 3)
6. inv_who_is_spared, a built and approved capability, lost its coverage_rest entry and is now claimed only by showcase mass_and_power, whose scene stages none of its states; without it the showcase newly exercises 2 capabilities, under min_new_after_first 3 (scenes.json coverage_rest (inv_who_is_spared removed) and showcase mass_and_power exercises; record.json inv_who_is_spared; ids inv_who_is_spared, the_spared, heavier_flies_less; returns to stage 3)

## Smallest fixes

- The Designer can fix 6 gap(s) at stage 3 without you: 1, 2, 3, 4, 5, 6.

## What you must decide

- Then one note on RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH (your words, or a card): rework it, certify it as it stands, waive a gap, or stop.
