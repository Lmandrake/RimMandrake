# FALL_LINE_ARRIVAL_MECHANISM_1 — build the Fall Line arrival delivery for the 15 species pulled from ambient wildAnimals

## what is wrong

`EXTREME_DESERT_UNRULED_VERMIN_1` removed all 15 Fall-Line-injected fauna/droid
rows from the ambient `wildAnimals` tables of `RUT_ExtremeDesert`, `RUT_Desert`
and `RUT_AridShrubland`, per the owner's 2026-09-20 ruling
(`design/Jawa/worldbuilding/biomes/fall_line.md` §8a): these species are not
biome fauna, they are **arrivals** — things you meet via injected wreckage
content or a subregion encounter, not things that live in the sand at a fixed
commonality. Nothing was built to deliver them that way. Right now none of
these 15 species can be encountered on the Fall Line at all — the ambient
route is gone and no replacement route exists yet.

## why it matters

This is deliberately a hole, not a bug — the owner wants the deep desert bare
by default, with these species meaningful again only once they arrive with
purpose (wreckage, a hunted survivor, a joke rat falling out of a crashed
ship). Until this item is built, the Fall Line's signature content (its own
named vermin, its droid population, the "feral race"/"feral droid" hunting-
ground beat from §8b) simply does not exist in the game.

## the full species list (preserved from `fall_line.json`'s `injection_layer`
before it was deleted — see `FALL_LINE_INJECTION_DEAD_BIOME_KEYS_1`)

All originally authored in
`design/Jawa/worldbuilding/biomes/rosters/fall_line.json`, `defNames`
`["ExtremeDesert","Desert","AridShrubland"]` (dead pre-rename keys — see that
item), transplanted by hand into the live `RUT_*` BiomeDef XML at authoring
time 2026-09-09, and removed by `EXTREME_DESERT_UNRULED_VERMIN_1` 2026-09-20.
Live defNames as they existed in the biome XML (naming drifted slightly per
biome — `RUT_ExtremeDesert`/`RUT_Desert` use `RSW_`-ported names,
`RUT_AridShrubland` still used bare donor-mod names):

**ship-vermin band:**
- `RSW_Scavrat` / `Scavrat` — commonality 0.6 (ExtremeDesert), 1.0 (Desert,
  boosted for ecosystem-pyramid law), 0.6 (AridShrubland). "the name is the
  job — eats what falls."
- `RSW_WompRat` / `WompRat` — 0.4 (ExtremeDesert), 0.7 (Desert, boosted), 0.4
  (AridShrubland). "icon; nests under hulls."
- `RSW_Mynock` / `Mynock` — 0.3 all three biomes. "icon — hull parasite, its
  literal canon niche."
- `RSW_Cindermite` (ex `VFEI2_Fuelmite`, ex-`RSW_Cindermite` rename per
  `BENCH_REBOOT_HANDOFF_202609201705.md` same-day work — verify current
  defName before wiring) / `VFEI2_Fuelmite` (AridShrubland still used this
  donor defName) — 0.3 all three biomes. "'fuelmite' — eats fuel; homeless
  after the dune-sea band cut."
- `Rat` (Core vanilla def) — 0.1 (ExtremeDesert, AridShrubland), 0.2 (Desert,
  boosted). 🔑 **Stays, deliberately, per the owner's ruling** — "actual
  terrestrial rats might be fun to fall from a ship as a white lab rat." It is
  otherwise exactly the "instantly-nameable Earth organism" this sheet bans;
  it must arrive out of a wreck, never spawn as ambient biome fauna.

**feral-droid band (all 7, "invisible to the food web" per deep_desert §4, a
good fit for arrival-scoping — the sheet's own words):**
- `RSW_DW_OuterRim_MSEDroid` — 0.1
- `RSW_DW_OuterRim_SalvageAssistDroid` — 0.1
- `RSW_DW_OuterRim_DUMDroid` — 0.08
- `RSW_DW_OuterRim_GNKDroid` — 0.08
- `RSW_DW_OuterRim_FX7Droid` — 0.05
- `RSW_DW_OuterRim_MuckrakerDroid` — 0.05
- `RSW_DW_OuterRim_DestroyerDroid` — 0.02 ("rare dangerous fall; still
  flee-prone by ruling §8b")

(`fall_line.json`'s `fauna` array additionally names `OuterRim_AstromechDroid`
at 0.08 — icon-protected feral droid — but this one was never actually wired
into any of the three live biome XML files; it is UNMEASURED whether it was
dropped on purpose or simply missed. Worth a look before this item builds the
arrival mechanism, so it isn't silently lost twice.)

**wreckage creatures (named in `fall_line.json`'s `fauna` array but never wired
into any live biome XML at all — always intended as Fall-specific, never
ambient):**
- `BMT_BunkerBug` — commonality 0.5 in the roster. "owner review 2026-09
  (round2 move mapping): Superb for the Fall wreckage creature."
- `BMT_Megapleura` — commonality 0.5 in the roster. "wreckage-based creature
  for the Fall."

## the work

Design and build a delivery mechanism that puts these 15+2 species (17 total,
counting the two wreckage creatures that were never live) in front of the
player as **arrivals**, not ambient fauna. Per §8a and §8b, the shape is open:

- A wreck-site incident/quest that spawns a cluster of these near a crashed
  ship, gated so it only fires on the Fall Line subregion.
- A subregion landmark (a `TileMutatorDef` or similar) that, once entered,
  has its own local encounter table drawing from this list — "something you
  walk into," per the owner's verbatim ruling.
- A generator-driven equivalent that produces the same effect procedurally.
  The owner explicitly said a generator route is acceptable — "if we pursue
  the generator option to produce the same" — this is not required to be
  hand-authored content.
- The feral-race/feral-droid capture mechanics from fall_line.md §8b (wily,
  flee-prone; capture-to-slave for races with permanent mental-scar hediff,
  capture-to-memwipe for droids with no droid-relations hit) are the
  gameplay payoff this item should wire toward, even if the full capture
  system is itself a separate build — at minimum, don't build a delivery
  mechanism that forecloses it.

## watch out

- This item does NOT include re-authoring `fall_line.json`'s injection
  layer — that data has been deleted (`FALL_LINE_INJECTION_DEAD_BIOME_KEYS_1`)
  and this file is now the durable record of what it held. Re-derive the
  wiring from this list, not from git history of the roster file, so nothing
  is silently missed.
- `RSW_Cindermite` may be mid-rename/rebuild as an owned C# def as of
  2026-09-20 (`BENCH_REBOOT_HANDOFF_202609201705.md`: "Cindermite (ex-
  Fuelmite) lose chemfuel ejection. Rebuilding them in our own C#") —
  confirm the live defName and whether it still exists as a spawnable
  PawnKindDef before wiring it into any arrival content.
- `RSW_Scavrat.xml` and `RSW_WompRat.xml` (their own `ThingDef.race.wildBiomes`
  dicts, not the BiomeDef side this item's predecessor touched) still carry
  their own hard-coded commonalities for the OLD pre-rename biome keys
  `AridShrubland`/`Desert`/`ExtremeDesert` (0.6/0.4/0.3 and 0.4/0.4/0.3
  respectively). MEASURED: these keys are dead — no live `RUT_*`-tier world
  tile uses the old pre-migration biome defNames, so today this is inert, not
  a live second ambient-spawn route. But it is a second place these species'
  biome affinity is authored, separate from anything `EXTREME_DESERT_
  UNRULED_VERMIN_1` touched, and worth cleaning up (or at minimum
  understanding) in the same pass as building the arrival mechanism, so a
  future rekey of those dead keys doesn't silently reopen ambient spawning
  this ruling closed.
- Do not build this by re-adding rows to any `wildAnimals` table — that is
  exactly the mechanism the owner rejected.

## verify

Each of the 17 species above can be encountered by the player specifically
through a Fall-Line arrival (wreck incident, subregion landmark, or
generator output) and NOT via any biome's ambient `wildAnimals` commonality.

## criteria

The Fall Line delivers its named content (ship-vermin, feral droids, the two
wreckage creatures, and the joke rat) as arrivals, matching the owner's
2026-09-20 ruling in `fall_line.md` §8a/§8b.

## 🔴 owner reinforcement, 2026-09-21 (BENCH, question card, `DESERT_FAMILY_PORT_EXECUTION_1`)

Asked directly whether the 7 Droid Depot droids should be authored as biome roster rows,
verbatim: *"They get injected by the wreckage thing. Not the random spawn of the
biome."* Same disposition this item already carries — no new item was filed for it,
this is the same ruling reconfirmed from a different angle. Recorded here rather than
silently dropped so a future reader doesn't wonder why `DESERT_FAMILY_PORT_EXECUTION_1`
mentions "the wreckage thing" and finds nothing.
