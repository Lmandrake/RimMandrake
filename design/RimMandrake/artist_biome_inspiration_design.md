# Artist biome inspiration ("the Muse") — design

Item: `ARTIST_BIOME_INSPIRATION_MOD_1`. Build item: `ARTIST_BIOME_INSPIRATION_BUILD_RESTLESS_MUSE`.

The owner's idea (2026-09-29): artists above about skill 10 get an inspirational biome that boosts the art
they make there. Perhaps a hated biome as well, or an unpredictable inspiration that moves once it is used.
He called the moving one "more Jawa", because it keeps the caravan travelling.

The idea covers every biome, so it is a RimMandrake-tier mod:

| | |
|---|---|
| mod folder | `RimMandrake/ArtistMuse` |
| packageId | `mandrake.rimmandrake.artistmuse` |
| namespace | `RimMandrake.ArtistMuse` |
| def prefix | `RM_` |

## Engine seam (read, not guessed)

Decompiled from `Assembly-CSharp.dll` (RimWorld 1.6, `RimWorld.QualityUtility`) with ilspycmd, 2026-11-03.

- All art quality goes through
  `QualityUtility.GenerateQualityCreatedByPawn(Pawn pawn, SkillDef relevantSkill, bool consumeInspiration = true)`.
  That method:
  1. rolls `GenerateQualityCreatedByPawn(int level, bool inspired)`, a Gaussian around a per-level mean;
  2. applies `Inspired_Creativity` as +2 levels and then ends the inspiration;
  3. applies an Ideology role's `RoleEffect_ProductionQualityOffset`.
- `AddLevels` caps at 6 (Legendary). Without an inspiration or a role, the base roll clamps at 5
  (Masterwork). So in vanilla, Legendary is reached only through an inspiration or a role.
- One Harmony **postfix** on the `(Pawn, SkillDef, bool)` overload, filtered to
  `relevantSkill == SkillDefOf.Artistic`, reaches every sculpture, and nothing else.
  The biome is `pawn.MapHeld?.Biome`. Pocket, orbit and space maps get no bonus, and neither does a
  pawn with no map.

## Variants weighed

The axes are: what it feels like, how well it fits the Jawa fantasy, cost, balance risk, and what it
leaves the player to do.

### 1. A fixed inspirational biome

Each qualifying artist rolls one muse biome, once, and keeps it for life. Art made there gets +1 quality
level, capped at Masterwork unless the pawn is also inspired.

- **For:** cheapest to build: one postfix and one saved field per pawn. Easy to read ("Tavi loves the
  dunes"). It gives a reason to found an outpost or a sculpture camp.
- **Against:** set and forget. Once the colony sits in, or never reaches, that biome, the feature is
  either always on or never seen. It does nothing for a caravan clan. Balance is fine because of the
  cap.
- **Verdict:** sound, but inert. Keep it as a settings mode, not as the default.

### 2. The fixed biome plus a hated biome

As in variant 1, plus one hated biome: −1 quality level there, and a small mood thought
(`RM_Muse_HatedBiome`, −3) while the pawn stays on a map of that biome.

- **For:** gives each pawn some character, and creates a choice about which artists to take on a
  caravan.
- **Against:** a permanent penalty that is invisible until it hurts. A colony that lives in the hated
  biome has a pawn who is always unhappy and always worse. That reads as a defect, not as flavour. It
  doubles what the player must remember for a small gain.
- **Verdict:** reject the permanent hated biome. Its good half survives as the "spent" biome in
  variant 3.

### 3. A restless inspiration (recommended)

The pawn's muse names one biome. The first finished art piece the pawn makes in that biome gets the
bonus, and that **spends** the muse. A letter follows ("Tavi's muse has moved on: she dreams of the
salt flats now"), and the muse rerolls to a different biome. The biome just spent is **stale** for a
while (each spent biome carries its own expiry; see the judge's fix 5): no bonus if it rerolls there again, and a small "this place is used up for me" thought (−2)
while the pawn is still on a map of that biome.

- **For:** this is the owner's Jawa reading. The bonus is a destination, so it pulls the caravan along.
  It is never permanently on or permanently off. It gives a story beat every time it is spent. The
  stale biome gives variant 2's character with no permanent penalty.
- **Against:** more state per pawn (the biome, a stale biome, a stale timer). The reroll pool needs
  care: it must hold only biomes the player can actually reach.
- **Balance:** one bonus per muse, and the muse moves after each use, so it is bounded by how much the
  colony travels. A spent muse gives **+2 levels, capped at Legendary**, like a Creativity inspiration,
  because the trip is the cost. Stacking it with a real inspiration still caps at Legendary (6).
- **Verdict:** the default.

### Decision table

| | 1 fixed | 2 fixed + hated | 3 restless |
|---|---|---|---|
| Jawa fit (keeps the caravan moving) | low | low | **high** |
| Always on, or never seen | yes | yes | no |
| Permanent penalty | no | **yes** | no (the stale period is temporary) |
| Build cost | S | S+ | M |
| Story beats | 0 | 0 | one per use |

## Recommended design

**Who qualifies.** A colonist with Artistic ≥ `minSkill` (default **10**, the owner's "~10") and
without Artistic incapability gets a muse the first time this is checked: on a periodic rare tick, or
when they reach the skill. It is checked against the current skill level, so a pawn who drops below
the minimum keeps the muse but cannot spend it until they climb back.

**The reroll pool.** The pool is the BiomeDefs that have at least one tile on the **live world grid**
(`Find.WorldGrid`) and are not water biomes. The muse's current biome and the stale biome are left out.
Picks are weighted toward reachable biomes: weight `1 / (1 + distance in tiles / reachTiles)` from
the colony's home tile, with `reachTiles` = 60 by default.

- This only reads the world; nothing is generated, so the no-worldgen ruling is not touched.
- A biome on 0 tiles is simply absent from the pool. That is the expected state until the planet is
  painted (the 2026-09-20 ruling), not a defect.
- The fixed shipped world is the one this pool reads in play.

**Spending the muse.** The postfix runs on art quality only. The bonus applies when the pawn qualifies
and the pawn's map biome is the muse biome. After it applies:

- a Positive letter, `RM_Muse_Spent`;
- a mood memory, `RM_Muse_Fulfilled` (+6, 5 days);
- the stale biome is set, with a `staleDays` timer (default 15);
- the muse rerolls.

A pawn on a map of the stale biome gets the situational thought `RM_Muse_StaleBiome` (−2).

**The player can see it.** One line on the pawn's inspect pane ("Muse: Salt flats"), or "Muse: stale
here" on the stale map. A world-map overlay of the muse biome is not v1. A dev gizmo forces a reroll.

**State.** A `WorldComponent`, `RM_MuseTracker`, holds `Dictionary<Pawn, MuseState>`. It is saved with
`Scribe_Collections` (key by reference, value deep), and dead or discarded pawns are pruned.
`MuseState` holds `BiomeDef muse`, `BiomeDef stale` and `int staleUntilTick`.

**Mod Settings** (defaults are the shipped behaviour; turning everything off is the vanilla game):

| setting | default |
|---|---|
| Enabled | on |
| Mode | Restless (Fixed / Restless) |
| Minimum Artistic skill | 10 |
| Quality bonus in Restless mode | +2, capped at Legendary |
| Quality bonus in Fixed mode | +1, capped at Masterwork unless inspired |
| Stale period | 15 days |
| Stale mood thought | on, −2 |
| Fulfilled mood thought | on, +6 |
| Letters | on |
| Reach weighting | 60 tiles; 0 = uniform |

Fixed mode is variant 1. It never rerolls and has no stale biome. The hated biome is deliberately not
offered.

**Bounds.** This mod has no biome-specific code. It reads a biome's identity only, so it works the same
in vanilla biomes and ours. Its tests run in our biomes (the 2026-10-15 ruling that biome mechanics are
promised only inside our biomes). No worldgen.

**First functional script** (required of every new mod): run offline in Python first, then port.

- Sweep the quality arithmetic: every base 0–5, inspired or not, a role offset of −1..+1, each mode.
  Check the bonus never goes past its cap and that turning the mod off gives exactly vanilla.
- Check the pool weighting: the muse biome and the stale biome are never picked, and an empty pool
  leaves the pawn with no muse rather than throwing.
- One live clause: on a quicktest map of biome X, with the muse forced to X, a sculpture comes out
  shifted, then the muse rerolls to a biome other than X and the letter fires.

## Ruling

**Variant 3 (restless) is the default, with variant 1 (fixed) as a settings mode. Variant 2's
permanent hated biome is rejected; its character survives as the temporary stale biome.**

This is a delegated design call (`delegation_policy.md` §2: a mod design is not on the reserved list;
*"Agents decide nearly everything"*, owner 2026-10-22). It follows the owner's own lean (*"more Jawa"*).
It was judged by an independent model that did not write this doc (GPT via
`src/RimMandrake/Utils/gpt_consult.py`; verdict below). It was logged on the ledger with
`--why "delegated: mod design ruling"`, so it reaches him in the daily digest. He may overrule it.

### Independent judge's verdict

GPT, consult job `consult-20261103-002059-1919842`, 2026-11-03. Verdict: *"3 (restless) should be default
for the travel fantasy; retain 1 as an option and reject 2."* It found six defects, and all six are
adopted. They bind the build item:

1. **The bonus is applied once, to vanilla's final result.** Never reroll, and never apply the
   inspiration or role bonus twice. The result is `max(vanilla, min(cap, vanilla + bonus))`, so an
   existing Legendary is never lowered. Whether the pawn was inspired is captured in a prefix, before
   vanilla ends the inspiration.
2. **Spend the muse only when real art is made.** State changes only on a call with
   `consumeInspiration == true`. The build lists every caller of that overload and confirms which ones
   are previews. Pocket, orbit and space maps are excluded explicitly (`Map.IsPocketMap`, and biomes
   flagged as space or orbit), not only by a null map.
3. **Balance, so cheap round trips cannot farm it.** A new muse cannot be spent until
   `museCooldownDays` (default 10) after it was rolled. The muse rerolls on spend, but the move must
   happen before the bonus can repeat. `RM_Muse_Fulfilled` sets `stackLimit 1`. A sculpture
   carried in unfinished counts in the biome where it is *finished*. That is accepted: carrying it
   there is still travel.
4. **The pool holds only tiles a colony can use.** A tile counts only if it is passable and not
   impassable terrain. Each biome is weighted by its nearest eligible tile from the artist's
   **current** tile (the home tile when the pawn is on a map, the caravan tile when caravanning). If
   the artist has no tile, the weighting is uniform. `reachTiles = 0` also means uniform, as its own
   explicit branch.
5. **Each spent biome has its own expiry.** Stale state is a `Dictionary<BiomeDef, int expiryTick>`,
   not one field, so A→B→A cannot skip A's stale period. The order on spend is: apply the bonus →
   mark the biome stale → clear expired entries → reroll. If the pool is empty, the muse is `null`
   with a `retryTick` one day later, so it does not reroll every tick.
6. **Saving.** `MuseState : IExposable`. Defs are saved with `Scribe_Defs`, and the stale dictionary
   with `Scribe_Collections` (LookMode.Def → Value). The tracker dictionary uses working lists
   (`Scribe_Collections.Look(ref d, "states", LookMode.Reference, LookMode.Deep, ref keys, ref vals)`).
   Post-load repair drops null keys. Only pawns that are destroyed and not resurrectable are pruned.
   Turning the mod off, or switching mode, **freezes** state and never deletes it, so a toggle cannot
   reset cooldowns or farm muses. Switching Fixed↔Restless keeps the current muse as the fixed biome.
