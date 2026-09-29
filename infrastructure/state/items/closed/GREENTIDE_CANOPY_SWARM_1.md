# GREENTIDE_CANOPY_SWARM_1 — the insect axis: a new canopy-hazard swarm

## the ruling

**Owner, decision taken by question card, 2026-09-25 20:47** (on `GREENTIDE_RISK_REWARD_EXCHANGE_1`'s
Q3, "are the insects their own kind of threat, or just more animals?"). Recorded on the ledger:

> *"Canopy-hazard insects = a NEW canopy swarm layer (new creature + art + behaviour), not folded into
> the existing cast."*

⇒ The insects are their **own** layer (card option A's shape), and they are a **genuinely new
creature** — not a reuse of the 27-row `WildAnimals_Greentide.xml` cast, and **not** the same thing as
`RM_Skerrel`/`RM_SkerrelGall` (the sting-stacking gall wasps of `GREENTIDE_WASP_SWARM_1`, which is
already fully designed and separately in flight — do not conflate the two insect items).

## why this axis was empty, and why it is cheap to fill

From the design pass's audit (`design/Jawa/worldbuilding/biomes/greentide_risk_reward_2026-09-22.md`
§1d, MEASURED against `src/`): **the Greentide had no authored insect mechanic at all before this
session.** But the mechanic this card is choosing — "insects work on the *forest*, not on you; they
chew tree bases, they bring giants down, they are why the canopy is dangerous overhead" — already has
its machinery **built and unwired**:

| mechanic | class | state |
|---|---|---|
| the Gnawers (fell trees by chewing bases) | `RM_JobGiver_GnawTreeBase` / `RM_JobDriver_GnawTreeBase` | ✅ built (M6, feller 3) — **no creature uses it** |
| the Shatterers (bring down weakened trees) | `fellsTreesBelowHealthFraction` hook in `HediffComp_PeriodicAreaAttack` | ✅ built (M6, feller 2) — **wired to no live creature** |

Both feed `RM_TreeFallUtility` (shipped, three fellers routed through one utility). ⇒ **The missing
piece is a real creature def and its art, not new mechanism.** The two placeholder defs in the repo —
`RUT_Placeholder_GreentideGnawer` (a recoloured Squirrel) and `RUT_Placeholder_GreentideLunger`
(Alligator fields copied down) — are deliberately unwired into any biome or GenStep and are not this
creature; they were scoped-out stand-ins, not drafts to finish.

## what this is NOT

- **Not `RM_Skerrel`** (`GREENTIDE_WASP_SWARM_1`) — the tiny sting-stacking gall wasp, already fully
  designed, tiering resolved (`RM_`), hosts named (`RM_Sarquin`, `RM_Nemmer`), and blocked on
  `REACTION_MECHANISM_GENERALISE_1`'s shared-budget reaction event. That item is NOT this one and this
  item does not inherit its blocker — this canopy-hazard creature's mechanic is tree-felling via the
  already-shipped `RM_TreeFallUtility`, not swarm-propagation-on-trigger.
- **Not a reuse of any of the existing 27 `WildAnimals_Greentide.xml` rows** — the ruling explicitly
  says "not folded into the existing cast."

## spec

1. **Design the creature concept as a card set first**, per this project's standing practice for a new
   creature (`HOSTILE_MOBILE_PLANTS_1`'s own spec: "design sitting first... author nothing before
   that"). At minimum: silhouette (large, insectoid, canopy-dwelling per the ruling), tier
   (`RM_`-invented per §7/Q11a — check the name against the Wookieepedia search API before assuming
   invented is safe), whether it operates solo or in a coordinated group, and which of the Gnawer vs.
   Shatterer mechanic(s) it drives (or both, at different life stages/sizes).
2. **Wire it to the existing mechanics, do not invent new ones.** `RM_JobGiver_GnawTreeBase` and the
   `fellsTreesBelowHealthFraction` hook are both shipped and tested-to-compile; this item's job is a
   def (and a `PawnKindDef`, `race`, real AI) that uses them, plus art.
3. **If it flies or lairs in the canopy, apply the standing flight rule** (`MaxFlightTime` stat, not a
   bool) — "canopy" and "overhead" in the ruling's wording suggest an airborne or canopy-clinging
   creature; confirm which before authoring the race block.
4. Roster placement (commonality, band) goes through the Greentide's own review sitting, not a
   sweep, per the standing per-biome fauna law.
5. Mod Settings toggle per the standing every-mod-ships-settings rule.

## verify

A new, invented (`RM_`-tier unless a canon name is deliberately chosen and routed through the patch
layer) creature exists with real AI, drives at least one of the Gnawer/Shatterer mechanics, and is
distinct in silhouette and mechanism from `RM_Skerrel`. It does not appear in
`WildAnimals_Greentide.xml`'s existing 27 rows (it is additive). `validate_patch.py` clean on every
touched file. ⛔ No live-proven claim from the Mac.

## criteria

You hear trees falling in the canopy before you ever see what is doing it.

## Watch out

- ⛔ **Do not confuse this with `RM_Skerrel`.** Two different insects, two different mechanics, two
  different items — the ledger note that created this item names both in one breath and it is easy to
  merge them by accident.
- ⛔ **Do not reach for `RUT_Placeholder_GreentideGnawer`/`RUT_Placeholder_GreentideLunger`** as a
  shortcut — they are recoloured vanilla stand-ins, deliberately unwired, and finishing them would
  violate the fauna law against reusing rather than authoring new content.
- ⚠️ The design pass's own audit found the Gnawer/Shatterer split ambiguous as to whether one creature
  or two drives both mechanics — settle that explicitly rather than defaulting to "one creature does
  everything" without saying so.
