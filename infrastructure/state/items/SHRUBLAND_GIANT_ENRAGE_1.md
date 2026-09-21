# SHRUBLAND_GIANT_ENRAGE_1 — RSW_ShrublandGiant: large-young life-stage + parental enrage-on-approach C#

## what is wrong

`COMMISSION_LEDGER_CLEANUP_1`'s arid_shrubland sheet slug
`the-huge-grazer-large-young-parental-enrage-body-donors-famb` shipped its
**def** this pass (`RSW_ShrublandGiant`,
`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ShrublandGiant.xml` — a
reskin of the already-ported `RSW_Fambaa`/`RSW_Dewback` body and art, wired
into `RUT_AridShrubland.xml`'s `wildAnimals` at 0.35) but ships as a plain
grazer with no special behaviour, exactly the `DESERT_SHADE_WHALE_FILTERFEED_1`
precedent (def lands first, mechanic comp follows in its own item).

`arid_shrubland.md`'s own size ladder (§4, owner-ratified) is explicit:

> **Large** — giants' children only, and 🔴 **approach is attack: the parent
> enrages if you even get near the young.** No warning is given.

And the biome doc's own "Owed" section lists this as part of a **still-unrun
engine feasibility pass**: "parental enrage on approach" sits alongside
venomvine's passability as one of the mechanics this biome has never had
checked against the actual engine.

## why it matters

Without it, "the large band is a void populated by exactly one thing — the
young of the huge" is prose with a juvenile lifestage sprite (already free,
Fambaa's own `Fambaa_j_*` art) but no teeth: nothing punishes getting close to
a calf, so the size ladder's own defining rule ("approach is attack") does not
exist in play.

## the work

1. **Engine feasibility check first** — this biome doc explicitly flags this
   as part of an unrun feasibility pass. Before writing C#, confirm what
   vanilla/Harmony hook can detect "a hostile-or-neutral pawn entered melee/
   interaction range of a juvenile-lifestage pawn of this race" without a
   per-tick full-map scan. Candidates to survey: a `Thing.Tick` override on
   the juvenile checking nearby pawns periodically (cheap, bounded radius);
   or a `JobGiver`/mental-state trigger on the ADULT that fires when its own
   juvenile (if `RSW_ShrublandGiant` gets any parent/offspring bond tracking
   vanilla already supports — check `Pawn_RelationsTracker`) is approached.
2. **The enrage state itself**: likely a short mental state (`MentalStateDef`,
   manhunter-like but scoped and time-boxed, "aggressive" toward the
   approaching pawn only) on the ADULT nearest the threatened juvenile, not a
   permanent manhunter flip — "no warning is given" describes the trigger,
   not a request for a berserk animal.
3. Wire onto `RSW_ShrublandGiant`'s `ThingDef` via a new `DefModExtension` +
   comp, same shape as `RM_ShadeSeekingWanderExtension`/
   `RM_FilterFeedExtension` (`RimMandrake.CreatureBehaviors`), so it can be
   MayRequire-gated and reused by any other "giant with young" species later
   without new C# per species.

## Watch out

- Do not touch `RSW_Fambaa` itself — `RSW_ShrublandGiant` is a separate
  defName reusing its body/art only, and `RSW_Fambaa` stays placed wherever
  it already is (swamp biomes, unrelated to this item).
- `RSW_ShrublandGiant`'s own comment block documents everything already
  decided about it (stats, life stages, working name) — read it before
  touching the def.
- This is a working-name def (`ARIDSHRUBLAND_SHIPPING_NAMES_1`); a rename
  there does not block this item, but keep both in sync if the rename lands
  first.

## criteria

Approaching a juvenile `RSW_ShrublandGiant` triggers a scoped aggressive
response from its nearest adult, verified live (quicktest or full load) —
this is explicitly a "never-observed mechanism" until someone runs it, same
caution `VENOMVINE_LIVE_VERIFY_1` records for its own build.
