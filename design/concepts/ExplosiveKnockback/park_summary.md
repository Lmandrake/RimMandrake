# ExplosiveKnockback: parked for you (ceiling)

his card "EK next -> Fix, then one judge" (OWNER:1794592220102307459) allowed one exam and one judge run, then parked: exam10 passed 119/119; judge rm-coverage-judge-1794593824 not_covered, 5 gaps, all stage-3 edits, none needing your answer. Nothing runs on it, no Designer run and no judge, until your word on RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH. Item RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH, stage 5 (Lock).

## QUICK LOOK OFFERED

Enough code exists (20 built capabilities: inv_kernel, inv_hook, inv_pawn_flyer, inv_which_blasts, inv_items_teleport, inv_shelf_skip, inv_who_is_spared, inv_shield, inv_recovery, inv_caps, inv_settings, inv_pits_receive, inv_pit_floor_haul, inv_proof_scenes, inv_weapon_ext_fields, inv_killed_corpse, inv_pit_floor_goods_stay, inv_big_corpse_spared, inv_mass_limit_skip, inv_too_weak_skip). A short look in game could settle these 5 gaps at once.

## Settled

- Stages accepted: 0 Read, 1 Argue the idea, 2 Argue the edge, 3 Write, 4 Exam.
- Root: Every blast in RimWorld now throws what it hits. A mortar shell beside a colonist hurls them three cells straight away from it, clean over sandbags, until a wall stops them hard; anything light goes too, so loose goods and corpses fly through the air, spinning and rebounding off walls, and no open shelf keeps them safe. When gas catches, it goes off clump by clump, each small burst scattering whatever lies near it, as the fire whooshes through the whole cloud. And where a blast meets a pit, its cover breaks and whoever it throws in falls.
- 46 decisions on record, 29 tree leaves, 30 inventory capabilities.

## Refused, and why

The coverage judge (rm-coverage-judge-1794593824) says not covered: Not covered: five gaps, each an edit at stage 3, none needing the owner. Claimed fixes: - g1 fixed: the panel's patch exists, and the Armoury dependencies the scene states match its About.xml. - g2 fixed: one 250 kg container limit, stated the same way throughout. - g3 fixed: vanillaCratesClosed is declared and swept. - g4 fixed: the per-part off list matches across the leaf, sheet, record and sweep. - g5 unfixed: the stated Cauldron dependencies omit mandrake.rm.flowworks. - g6 fixed: the leaf and sheet now say a gas shove into an open pit drops the pawn, and the melee contest is filed. The mass and blast-power change opened four gaps: - sc_mass_and_power stages real damage with nothing to keep the creatures alive. - Its leaf oracle and its colonist mass band disagree with the scene. - The sweep claims 'each pawn farther', which is false for its walled, door-backed and belted pawns. - inv_who_is_spared's coverage row was removed, and showcase mass_and_power claims it without staging any of its states. Not checked: whether LWM's weapons locker can reach 76 kg. That row is asserted INVALID otherwise, so it cannot pass falsely.
1. The Cauldron's dependency list stated in the gas scenes omits mandrake.rm.flowworks, so three scenes state and assert an incomplete list (scenes.json sc_gas_chain, sc_cauldron_gas, sc_settings_sweep start lines (the same wording in sc_cover_breaks and sc_gas_shove_into_pit); ids inv_gas_chain, inv_gas_tags, gas_goes_clump_by_clump, our_gases_burn, inv_settings, settings_scale_and_switch; returns to stage 3)
2. sc_mass_and_power stages real Bomb damage (50, then 100) one cell from a rat and a colonist, with nothing to keep them alive, yet expects each thrown creature 'alive and stunned' at its kernel cells (scenes.json sc_mass_and_power start (blast line) and expect; tree.json heavier_flies_less; ids heavier_flies_less, inv_blast_power_damage; returns to stage 3)
3. sc_mass_and_power's stated numbers do not match its leaf or its own assertion band: the leaf oracle's thrumbo '1 then 3 cells' is never staged, and the colonist band of 60 to 90 kg lets a correct build fail the strict order (tree.json heavier_flies_less oracle_proposed; scenes.json sc_mass_and_power start (masses), expect, control; ids heavier_flies_less; returns to stage 3)
4. sc_settings_sweep expects the double-damage blast to throw 'each pawn farther' than the frag grenade, which is false for the lane pawns a wall, a door or a shield belt holds (scenes.json sc_settings_sweep expect (blastPowerFromDamage clause); ids settings_scale_and_switch, inv_settings, inv_blast_power_damage; returns to stage 3)
5. inv_who_is_spared, a built and approved capability, lost its coverage_rest entry and is now claimed only by showcase mass_and_power, whose scene stages none of its states; without it the showcase newly exercises 2 capabilities, under min_new_after_first 3 (scenes.json coverage_rest (inv_who_is_spared removed) and showcase mass_and_power exercises; record.json inv_who_is_spared; ids inv_who_is_spared, the_spared, heavier_flies_less; returns to stage 3)

## Smallest fixes

- The Designer can fix 5 gap(s) at stage 3 without you: 1, 2, 3, 4, 5.

## What you must decide

- Then one note on RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH (your words, or a card): rework it, certify it as it stands, waive a gap, or stop.
