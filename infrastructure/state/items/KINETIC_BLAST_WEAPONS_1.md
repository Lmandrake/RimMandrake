# KINETIC_BLAST_WEAPONS_1

Owner, 2026-10-06 21:40, typed into a question card (verbatim), on whether thump cannon blasts should throw:

> Thump cannons throw farther... and I can see a whole class of weaponry to create that create Kinetic Blast-type
> attacks that are unusually cool! We should commission such a range of projective kinetic blasts

## spec
- Explosive Knockback: thump cannon shells throw farther than a mortar of equal damage (per-weapon throw multiplier).
- Design a range of projectile weapons whose main effect is a kinetic blast (throw, little damage): tiers, ammo, research, factions, art. Star Wars style names allowed in the RM_ tier if invented; canon items route through the Utinni layer.
- Commission their art once designed.

## built (FOUNDRY, 2026-10-06/07)
Design §10 (v1, BENCH) + §11 (finish pass): `ff6330011` Explosive Knockback per-projectile lookup, impactFactor,
body-size override, stun-lock guard, shield absorbs throw; `53186050e` Kinetic Arms ruins loot, palm arrest, grav-ram
override, cord marker + Gimme Some Slack skip, ring fleck, full settings, both validation walks with levels.
`fd920d3b5` (BENCH, 2026-10-07) where they drop: every vanilla Ancient Danger temple (35%, Mod Setting), and ancient
complex room loot (weight 0.15, as rare as spacer components) and security crates (0.4), setting "found in ancient
complexes". Picks by rarity tier: thudder 30, palm thumper 20, slam launcher 15, thump shell 15, kicker mine 12, repulsor
rifle 10, pulse cannon 5, grav-ram 3 (of 110). Rakatan vaults are loot-free by design. Test tier: `modset_builder.py
--tier kineticarms` (13 mods).
**PROVISIONAL numbers:** ruins chance 35% per ancient temple, rarity weights, complex weights 0.15/0.4, thump-shell stack 5–12, recovery window 120 ticks, shield
drain 10 damage-equivalents per point of force. New proof scenes are written, not yet run live.

## criteria
- EK.K L0: kernel selftest K-01..K-16 PASS (selftest_explosiveknockback_kernel.py)
- EK.static L0: validation.py STATIC PASS: config lookup, shield/landing hooks, settings saved+reset, walk coverage
- EK.mock L0: validation.py --mock stages every scene
- EK.load L1: explosiveknockback tier loads with no red error from this mod; Harmony patches applied
- EK.scenes18 L2: the 18 v1 scenes still PASS after the 2026-10-06 config/guard/shield change
- EK.config L2: lookup_projectile, lookup_zero_wins, impact_factor, body_override PASS
- EK.guards L2: immunity_window and shield_counter PASS
- EK.reload L2: recovery-window stamps survive a save/reload (no scene yet)
- EK.feel L4: owner watches a blast and a shield belt: reads right
- KA.K L0: kernel selftest KA-01..KA-16 PASS (selftest_kineticarms_kernel.py)
- KA.static L0: validation.py STATIC PASS: defs/art/patch/settings/GSS-marker wiring, walk coverage
- KA.mock L0: validation.py --mock stages every scene
- KA.load L1: explosiveknockback tier + kineticarms loads, no red error; fleck and ruins maker resolve
- KA.scenes18 L2: the 18 v1 scenes still PASS on the rebuilt DLLs
- KA.new6 L2: palm_arrest_wall, gravram_big_body, ruins_loot, kicker_hidden, cords_marker, ring_fleck PASS
- KA.cords L2: with Gimme Some Slack: repulsor blast under a span leaves it whole; a frag grenade cuts it
- KA.temple L2: a debug-generated ancient temple (chance 100) holds one kinetic weapon or minified mine/cannon
- KA.complex L2: ruins_loot scene reports complexes=True (all three ancient-complex tables carry RM_ThingSetMaker_KineticComplex)
- KA.shield L2: a repulsor hit on a shield-belted raider: not thrown, belt drained (EK shield_counter via KA)
- KA.feel L4: owner: a repulsor line reads as a moving wall; a kicker mine at a pit lip as an ejection gate
