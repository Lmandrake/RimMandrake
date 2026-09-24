# VANILLA_BEAST_EXCISION_1 — no vanilla beasts in the Utinni scenario

## the ruling

Owner, 2026-09-24, typed, verbatim: *"As for the vanilla creatues, we shouldn't
be patching them. We should be cutting them. No vanilla beasts in Utinni
scenario. We make our own."*

Said when asked whether official-content creatures in our rosters (Toxalope —
Biotech; LavaSnail, StoneCrab, ColossusToad — Odyssey) should be renamed. The
answer is neither rename nor keep: **cut, at the Utinni scenario layer**. The
campaign's fauna is entirely our own (plus ruled canon Star Wars beasts).

## scope

- **CUT (Utinni layer only):** every vanilla + DLC animal — Core beasts
  (muffalo, thrumbo, warg, elephant…), Biotech (toxalope…), Odyssey (lava
  snail, stone crab, colossus toad…), and the vanilla insect family (already
  half-ruled: infestations are Dune-Sea-only and the insects there become sand
  busters — `STILLSAND_RM_MOD_BUILD_1`).
- **NOT cut:** the `RM_` tier keeps whatever it keeps — the tier line is IP/
  scenario, and the free `RM_` biome mods stand alone (Q11a). This excision is
  a **scenario-layer** act (Cherry Picker / Utinni patches), never an edit to
  vanilla defs and never a label patch.
- **NOT this item:** authoring the replacements. "We make our own" is the
  per-biome sitting work already running; a biome's cut lands when its own
  cast can carry it — do not strip a roster bare ahead of its sitting
  (owner's eviction-stop principle, 2026-09-22, applies in spirit).

## spec

1. Census every vanilla/DLC animal reachable in the Utinni scenario: biome
   rosters (read patch-added rosters via the PatchOperation's own xpath, not
   BiomeDefs alone), pawnkinds, and event/quest routes.
2. Cut via the existing Cherry Picker + scenario machinery, biome by biome as
   each biome's own cast is ready — never a one-day planet sweep.
3. Close every non-roster route a vanilla beast walks in: manhunter pulses,
   farm-animals-wander-in, self-tame, quest rewards (animal gifts), trade
   caravan stock, and **caravan pack animals** — the muffalo slot needs an
   owned pack beast before the muffalo goes.

## Watch out

- 🔴 A Cherry Picker cut is commonality-0, invisible to the def dump
  (`cherry-picker-cuts-invisible-to-dump`); verify cuts live, not by dump.
- 🔴 Cutting the last member of a role (pack animal, farm animal in a quest
  table) breaks the role silently — same family as the weapon-tag trap in
  `rimworld-content-moderation`. Rebuild the role index after each wave.
- ⚠️ Cherry Picker has three cut sources; `OWNER_EXCLUDE` filters only one.

## verify

A full-list live session in the Utinni scenario in which no vanilla/DLC animal
spawns, wanders in, arrives as a quest reward, or appears in trader stock; the
caravan/pack role demonstrably filled by owned beasts.

## criteria

Every animal a Utinni player ever meets is ours or ruled canon. The RM_ tier is
untouched.
