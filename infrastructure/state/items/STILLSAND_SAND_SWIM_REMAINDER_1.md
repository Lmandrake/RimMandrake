# STILLSAND_SAND_SWIM_REMAINDER_1 — the rest of the sand-swim kit: thumper, sand fishing, the Listening, wake records

The rest of `STILLSAND_SAND_SWIM_KIT_1` (spec there, §1–§9). Design source unchanged:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.0, §2.1, §4.

**Already built, by the kit pass** (CreatureBehaviors, `RM_SandSwimExtension.cs` + `RM_CompSandSwim.cs`,
`Defs/HediffDefs/RM_SandSwim_Hediffs.xml`):
- The extension alone wires a race: `RM_SandSwimStartup` injects `RM_CompSandSwim` onto every race
  that carries it.
- Submerge on swim terrain via `RM_SandSubmerged` (vanilla `HediffComp_Invisibility`). The default
  swim set is `Sand`, `SoftSand` and `RM_DeepSand`. It throws wake dust puffs and keeps a rumble
  sustainer scaled by body size. It breaches (dust burst, optional `breachSound`, stagger) on a strike,
  in melee, on non-swim ground or when hit, and stays up `surfacedTicks` afterwards.
- No vanishing: the hidden marker hediff `RM_SandSwimmer` hears the swimmer's kills
  (`Hediff.Notify_KilledPawn`). Each take lays `RM_Filth_DisturbedSand` and sends a letter (player
  victims) or a message (wild ones). A submerged swimmer carrying a corpse lays `RM_Filth_DragMark`
  on each cell.
- §4 droid immunity: while submerged, the swimmer drops any attack on a pawn whose flesh is not
  organic (`RaceProps.IsFlesh`).
- §8 the piinnok query: `RM_SandSwimUtility.SubmergedSwimmersNear(map, cell, radius, minBodySize, list)`.
- §9 settings: `sandSwimEnabled`, `sandSwimDroidImmunity`, `sandSwimRumbleVolume`.
- Consumers wired: `RM_Vekka`, and `RSW_SandStalker`, `RSW_KraytDragon`, `RSW_GreaterKraytDragon`.
  The RSW ones are in their own def files, behind `MayRequire` on the extension `<li>`. The krayts
  stay wild.

## spec

What is still owed:

1. **Wake trough records** onto the shared track grid, once `FOOTPRINT_TRACK_GRID_1` exists.
   Write the record from `RM_CompSandSwim.TickSubmerged`. Today the wake is dust flecks only, and
   by design no filth Thing is laid for it.
2. **Drift depth ≥ 0.3 as swim ground.** Read the dunes engine's sand depth from
   `MapComponent_DuneField` (MovingDunes is a separate assembly, so this needs a soft lookup).
3. **More consumers.** `RM_Qorrax` and `RM_Duumma` do not exist yet; they come from
   `STILLSAND_BEDAZZLE_CONTENT_1`. Two consumers already manage submersion with their own comps:
   `RM_Drazzik` (`RM_CompDrumLure` uses its own `RM_DrumLureSubmersion` hediff) and
   `RSW_SarlaccSwimmer` (`CompSarlaccSwimmer` lays its own funnel). Pick one visibility owner for
   each before adding the extension, or two comps will fight over the invisibility hediff.
4. **The thumper (§5).** `RM_Thumper` holds a water charge, wets a small radius when it beats, and
   draws swimmer wakes only while charged. `RUT_Groundcaller` becomes a variant of it by patch. Hook
   it into `RM_CompSandSwim`: a submerged swimmer within radius of a charged, beating thumper takes
   a Goto toward it. Add a settings toggle.
5. **Sand fishing (§6).** Add `fishTypes` on `RM_Stillsand` (the catch family after the content
   item's tier move; the RSW catches by Utinni patch). A fishing session on deep sand has a small
   chance to draw a stalker wake. Add a settings toggle.
6. **The Listening (§7).** Wind-scaled hiss and saltation on `RM_MapComponent_ProximitySoundscape`.
   Singing-dune one-shots come from `MapComponent_DuneField`'s transport batch. Add the one-line
   warning the first time a singing slip face is within N cells of a player building, and author the
   rumble and breach `SoundDef`s (placeholder grain). Each gets a settings toggle.
7. **Live criteria**, on a Stillsand quicktest by state read: submerged and surfaced, the take signs
   plus the letter, mech immunity, and a catch.

## criteria

The criteria of `STILLSAND_SAND_SWIM_KIT_1` still stand. Each is proven by a state read, never by a
screenshot hunt.
