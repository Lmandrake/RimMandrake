# The Fall Line — definition sheet

> 🧊 **FROZEN — `BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07.** The rulings in this
> sheet are frozen: **amendments add detail; they never change a ruling.** The
> unfreeze path is an owner ruling at a sitting, recorded on the item that
> changes it; contradiction cards from the freeze review amend under this rule.


_Owner + BENCH, 2026-09-05. Supersedes the unruled `wreck_fields.md`, which was
groping for this place before we found it already canon._

🔴 **NOT A NEW BIOME** (owner, 2026-09-05: *"I would prefer not to have yet another
biome but just inject such things with inhabited as needed."*). The Fall Line is a
**named region painted on existing arid biomes**, given its identity by an
**injection layer** — wreckage, shade, and feral inhabitants — not by a `BiomeDef`.
Everything below is an admission test for what gets injected, not a def to author.

## 0. What is already on the map (measured, not proposed)

`world/ASHKARR_VIVIFIED_2026-08-24_tiles.csv`, region `The Fall Line`:

| | |
|---|---|
| **Tiles** | **308** |
| **Biomes** | `ExtremeDesert` **252** (82%) · `Desert` **44** (14%) · `AridShrubland` **12** (4%) |
| **Arc (θ)** | 40.0° – 65.1°, median **50°** — mid-dayside, well short of the terminator |
| **Temperature** | 28.4 – 49.3 °C, median **42.1 °C** |
| **Rainfall** | 0 – 16 mm, median **0** — it does not rain here |
| **Elevation** | 8 – 1505 m, median **446 m**; the *Fall Line* ridge itself is **780 m**, at (26,352) (34,357) (43,2) (52,6) (61,9) |
| **Mutators** | 209 across the region |
| **Roads** | 28 tiles carry road |

🔑 The owner's ruling and the map already agree: **82% is `ExtremeDesert`**, so
"`ExtremeDesert` + a shade mechanic" costs no repaint. The `Desert` and
`AridShrubland` minority are the ridge flanks and the road corridor.

## 1. What it is

A belt of hot, rainless, low-relief desert **downwind of the plateau**, on the Gray
flank, where the superrotating winds bend everything that re-enters the atmosphere
down onto the same ground. The orbital war stopped; the falling did not. Nothing
here is old: the wreckage is *fresh*, replenished on a timescale of seasons, and the
whole region is a slow rain of other people's ruined machinery. Walking it means
walking between wrecks — a hull section here, a spar there — each throwing the only
shade for a hundred metres, and each with something living under it.

The Empire claims the salvage rights. It holds the pass and three hundred people on
a wall, and it audits four hundred and six species exemptions from a desk. It cannot
enforce any of it past bowshot of the garrison.

## 2. Planetary position

**Mid-dayside (θ 40–65°) × the wind-corridor anomaly.** Not an impact scar and not a
crash site — a *deposition zone*. The plateau upwind forces the superrotating flow
up and over; everything the atmosphere is carrying comes down in the lee. The
anomaly is meteorological, which is why the belt is long and narrow and follows the
wind rather than a ring of arc.

## 3. Driving forces

Orbital debris on decaying trajectories is sorted by the atmosphere, not by chance:
the plateau's standing wave drops it in a repeatable lee, so one strip of desert
receives what the whole hemisphere sheds — and that strip therefore has the one
resource on Ash'karr that **regenerates**.

## 4. How the biology adapted

- **Shade is the limiting resource, and it is manufactured.** In open `ExtremeDesert`
  nothing persists through the noon. Under a hull plate, ground temperature drops
  enough that a soil community survives. So life here is **obligately commensal with
  wreckage** — it does not live in the desert, it lives in the desert's *furniture*.
  Every pocket is an island, and the islands move as the wrecks are buried, salvaged,
  or replaced by the next one down.
- **The falling delivers organics.** Re-entering hulls carry hydroponics, stores,
  bodies, and the biology of wherever they came from. This is the only place on the
  planet with a **continuous exogenous carbon input** — vermin here eat what falls,
  not what grows.
- **Everything is transient by design.** No lineage can specialise on a *particular*
  wreck, so the adaptations are generalist, fast-cycling, and good at relocating.
  Long-lived, deeply-rooted or territorial forms cannot work here.
- **Some wrecks still have power.** A cell that has not quite died, a compartment
  still holding pressure, a light still on. Life colonises those hardest — warmth,
  water from a condenser still condensing, and a machine still running its cycle.

## 5. Always true

- The wreckage is **fresh and renewable**. Salvage taken is replaced. This is the one
  non-depleting resource on the planet.
- **It is still falling.** Debris strike is an ambient hazard, not a scripted event.
- Every shade pocket has an occupant, and the occupant is there **because** of the
  shade.
- **Anything alive here is either feral, vermin, or passing through.** Nothing is
  native and nothing is settled except the Empire's garrison.
- A wreck may be **partially functional**. Power, light, atmosphere, a working door,
  a still-cycling machine — rare, and always the best thing on the tile.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No new `BiomeDef`.** Fall Line content is injected onto `ExtremeDesert` /
   `Desert` / `AridShrubland` tiles in the region. A def whose `biome` is a bespoke
   Fall Line biome is a violation.
2. 🔴 **No standing vegetation in the open.** Any plant injected here must be gated
   on a wreckage/shade pocket. A plant that spawns on bare Fall Line desert is a
   violation.
3. 🔴 **No faction affiliation on the ferals** (owner). They are `Faction=null`
   wildlife-analogues. A feral with a `defaultFactionType` is a violation.
4. 🔴 **Killing a feral droid must not anger neutral droids** (owner). No
   `factionRelationImpact`, no shared faction with the Free Droid Enclave.
5. 🔴 **No water.** Median rainfall is 0 and it does not rain. No rivers, no marsh,
   no standing water except what a wreck's condenser makes.
6. 🔴 **No long-lived or territorial fauna.** Nothing that defends a fixed range —
   the substrate moves.
7. 🔴 **The recognizability rule applies** — no terrestrial referent a player can
   instantly name. The Star Wars icon carve-out still protects icons.
8. 🔴 **No lush.** The Fall Line is dayside and has no river or coast, so the
   three-part lush rule forbids it outright.

## 7. Uniquely available

- **Renewable salvage** — the only source that does not deplete.
- **Intact orbital tech** — components and advanced parts that exist nowhere else
  on the surface.
- **Partially functional wrecks** — a found power cell, a working door, a machine
  still running. Operable, never relocatable (the CoreDrill precedent).
- **Exogenous organics** — falling stores and cargo, the region's only food import.
- **Recoverable people and droids** — see §8b. The Fall Line is the only place you
  acquire labour by capture rather than by recruitment or trade.

## 8. Inhabited objects

Injected, not painted. The roster draws on `structure_injection_roster.md` and
`tile_augmentation_matrix.md`:

- **Fresh wreck** (the signature) — a hull section, half-buried, throwing shade;
  scattered plate and spar; a debris scar upwind of it.
- **Live wreck** — as above, but something still runs. The tile's prize.
- **Salvager camp** — transient, nobody's faction, abandoned as often as occupied.
- **The Fall Line pass / Ashgarrison** — the Empire's chokepoint seat, one of only
  **three** Imperial world holdings (`ASHKARR_WORLD_DEFINITION.md` §7). Three hundred
  people, forty on a wall, nine years without an attack, and a species-exemption
  clerk (`INHABITED_CAST_EMPIRE.md`).
- **`AncientGarrison` at tile 9167** — the V3 vault candidate, "somebody defended
  this once" (`vault_siting_prep.md`).
- **Ship vermin nests** under the larger hulls, living on what falls.

### 8b. The ferals — 🔴 OWNER RULING, 2026-09-05 (verbatim intent)

> *"Not just droids. Droids and normally sentient races gone feral by hideous
> survival after crashing. Can be captured and turned into slaves (races) or
> memwiped (droids) to restore. But they should be very wily and prone to flee
> rather than attack. No faction affiliation. Wiping them does not incur neutral
> droid hatred. Races have permanent mental problems that remain as a slave that
> make them much less valuable. Possible in v2 there could be a mental treatment to
> heal their broken mind from the more advanced settlements (helix and deep water)."*

Survivors of the falling. They came down alive and stayed alive by doing whatever it
took, alone, in the heat, for years.

| | **Feral races** | **Feral droids** |
|---|---|---|
| **Origin** | crash survivors, sentient, broken by survival | crash survivors, corrupted by damage and time |
| **Behaviour** | **wily, flee-prone** — they run first and fight only cornered | same |
| **Faction** | 🔴 none | 🔴 none |
| **Capture yields** | a **slave** | a droid to **memwipe and restore** |
| **Permanent cost** | 🔴 **permanent mental problems that persist through enslavement** — much less valuable than a normal slave | none once wiped — restoration is clean |
| **Killing them** | ordinary | 🔴 **does not anger neutral droids** |

**v2 only, do not build now:** a **mental treatment** available from the advanced
settlements (**Helix**, and the deep-water holdings) that heals a feral race's broken
mind — turning the cheap damaged slave into a full person. This is the payoff that
makes capturing them worth doing, and it is deliberately gated behind the settlements
the player must reach to earn.

🔑 **Design consequence:** the Fall Line is a **hunting ground, not a battlefield**.
Its inhabitants run. The gameplay verb is *pursuit and capture*, which is why the
wreckage matters — it is the cover they break for.

## 8a. 🔴 RULED — the fall fauna are ARRIVALS, not biome fauna (owner, 2026-09-20)

Verbatim: *"These falling injections should not be listed as 'sometimes appears'
in the deep desert but rather arrive with injected content from inhabited from
wreckage or, alternatively, if we pursue the generator option to produce the
same. They are not part of 'the biome' there are simply events and subregions
where you can meet them."*

🔑 **This ruling AGREES with this roster's own note and overrules the
implementation.** `rosters/fall_line.json` already says *"NOT a BiomeDef (ban 1).
Entries are ADDITIONS injected over the underlying defs"* — but the 15 rows were
wired as ordinary `wildAnimals` entries on the underlying biome defs, which is
precisely "sometimes appears in the biome". Design said arrival; the build said
ambient.

### What this means concretely

- ⛔ **A Fall Line row is NOT a `wildAnimals` entry on `RUT_ExtremeDesert`,
  `RUT_Desert` or `RUT_AridShrubland`.** Ambient commonality is the wrong
  mechanism for all 15.
- ✅ They attach to **injected wreckage content and to subregions** — a place you
  walk into, or an event that brings them. A generator producing the same effect
  is an acceptable alternative route, not a different ruling.
- 🔑 **The consequence that matters for the deep desert:** with these removed,
  `RUT_ExtremeDesert`'s ambient cast loses its two heaviest rows (`Scavrat` 0.6,
  `WompRat` 0.4). That is the intended result, not a hole to backfill with more
  ambient vermin — the deep desert is supposed to be empty, and what you meet
  there should be something that *arrived*.

### The one deliberate exception

**`Rat` (0.1) STAYS.** Owner, verbatim: *"the rat was there because actual
terrestrial rats might be fun to fall from a ship as a white lab rat. That is
all. So keep it."*

⚠️ It stays **as a fall arrival**, not as ambient biome fauna — the ruling above
still applies to it. A plain Earth rat is otherwise exactly the "instantly
nameable Earth organism" this sheet bans, so 🔴 **do not let a linter or a future
purity sweep cut it**: it is ruled in, for the joke, and the joke needs it to
arrive out of a wreck rather than to live in the sand.

### Watch out

- ⚠️ **`FALL_LINE_INJECTION_DEAD_BIOME_KEYS_1` is now solving the wrong problem.**
  It proposed rekeying `defNames` from the dead `ExtremeDesert`/`Desert`/
  `AridShrubland` to the live `RUT_*` names. Under this ruling the rows do not
  belong in a biome table under EITHER key. Re-home them first; rekey only
  whatever genuinely remains biome-scoped.
- ⚠️ The 7 `OuterRim_*` droid rows are the sheet's "invisible to the food web"
  beat and are a good fit for arrival-scoped content — they are wreck salvage
  that walks. Do not drop them when the vermin come out.

## 9. Artistic theme

**"A slow rain of other people's ruin, and everything alive is hiding under it."**

- **Palette:** bleached bone-white hardpan and pale sand under a white noon sky —
  the flattest, most washed-out ground on the planet — punctuated by **hard black
  shade** and the **scorched, oxidised colour of fresh re-entry**: heat-blued metal,
  ablative char, rust that has not had time to go orange yet.
- **Silhouette language:** **long horizontals broken by one wrong vertical.** The
  land reads as an empty line; the wrecks are the only tall things, and they are the
  wrong shape for a landscape — a spar, a fin, a hull rib. Debris scars are long
  gouges pointing the same direction, because the wind sorts them.
- **Light:** brutal, vertical, near-shadowless in the open; the shade under a wreck
  is **near-black and sharp-edged**, and that contrast is the whole composition. The
  live wrecks add the only artificial light on the dayside — a status lamp still
  green in the black under a hull.
- **Motion:** nothing moves but heat shimmer and, occasionally, something small
  going flat-out from one shadow to the next.

---

## Open, not ruled

- Whether the **ridge line itself** (780 m, five points) gets its own treatment or
  just reads as high ground within the belt.
- Which existing feral-droid / feral-pawn mods can supply §8b, versus what we author.
  The capture→slave and capture→memwipe paths, and the "no droid hatred" carve-out,
  are the parts most likely to need our own C#.
