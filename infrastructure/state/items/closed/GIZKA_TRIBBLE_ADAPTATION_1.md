# GIZKA_TRIBBLE_ADAPTATION_1 — examine the Tribble module; build the Gizka from it

Owner, 2026-09-06: just SUBSCRIBED (⚠️ not installed — do not activate) a Tribble module.
We want a creature LIKE it in the game: **the Gizka** (KotOR's hopping ship-pest).
*"Finding one of these in the ships should be an event... cute at first but then becomes
a real problem."*

## spec

1. **Examine the Tribble module** (find its workshop folder by About.xml name scan; it is
   inactive, so ModsConfig won't list it): what it ships — breeding mechanic, feed/growth
   curve, event hooks, any C#. Plan-read only; never activate it.
2. **Locate the prior donor art** the owner believes we hold — search the
   `Absorbed_KotorCore` / KotOR donor pools for gizka textures before commissioning any.
3. **Design the Gizka as an EVENT, not a spawn**: found aboard ships (gravship holds,
   wreck salvage, purchased cargo) — one animal, small, endearing (cuteness mood bonus,
   colonists name it). Then the curve turns: fed and warm it breeds fast, raids food
   stores, chews wiring and components (breakdown events), crowds rooms. Escalation
   stages, each with fair warning signs.
4. **The exits are the fun**: cull them (mood hits — they are CUTE), sell them onward
   (the classic KotOR scam — somebody always buys gizka; a Jawa solution), poison bait,
   cold (vent the hold), or lean in and farm the problem. Each exit priced.
5. Anti-exponential check: the exponential belongs to the PEST, never the player — a
   gizka economy must stay a bad idea that is funny, not a ladder.
6. Naming per the tier grammar (`RSW_` — Star Wars, not campaign-specific).

## verify

Design doc reviewed with the owner; Tribble module examined without ever entering the
active mod list; donor art found or its absence MEASURED before any generation.

## Recon done 2026-09-12 (BENCH belt wave) — parts 1-2
`Transient/GIZKA_TRIBBLE_RECON_2026-09-12.md`. Tribble module =
`zylle.TribbleTrouble` (WS 2400590961), inactive, breeding in ZTribble.dll
(`CompProperties_TribbleSpawner`), arrival is a random ThreatBig roll — the
shape to REJECT (we want a found-aboard event, not a raid roll). Gizka ALREADY
EXISTS in active `mlie.starwarsanimalcollection` (WS 3497316713): full
ThingDef/PawnKindDef/BodyDef, art in a Unity AssetBundle (any "art absent"
claim is stale — bundle, not loose PNG); RSW_ gizka sounds + a biome spawn
patch already exist in SWBestiary. UNKNOWN: whether the bundle sprite renders
live (quicktest check). Next: design draft (parts 3-6) → owner cards.

## Design draft done 2026-09-12 (BENCH belt wave, Fable agent)
`design/RimStarWars/gizka_ship_pest_draft.md` — discovery event (never a raid
roll), 4 escalation stages each with a readable warning, 5 priced exits,
anti-exponential arithmetic, Mod Settings per MOD_OPTIONS_RETROFIT_1, owner
cards at the end. NOTE: a 2026-09-08 spec (`gizka_ship_pest_spec.md`) already
existed unrecorded on this item — its factual base (creature/art absent) was
wrong per the recon, so it was deleted (git holds it); its intent is carried
in the draft. Open: quicktest whether the donor AssetBundle gizka sprite
renders; SWBestiary's RSW_Pawn_Gizka_* sounds duplicate the donor's own set
(fold into the build). Cards await the owner.

## Cards ruled 2026-09-12 (owner sitting) — build gated on the hold hook
Tunable escalation with slow default; ~15 silver price patch; watched-cull
guilt IN; free-gift gag deferred by default. 🔴 Launch scope: HOLD the whole
feature until the gravship-hold discovery hook is confirmed —
GIZKA_HOLD_HOOK_SPIKE_1 (FOUNDRY) is the gate. Rulings recorded in the
draft's Owner cards section.
