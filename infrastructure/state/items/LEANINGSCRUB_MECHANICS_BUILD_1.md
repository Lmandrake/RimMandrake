# LEANINGSCRUB_MECHANICS_BUILD_1 — Build the Leaning Scrub mechanics

From `LEANINGSCRUB_BEDAZZLE_SITTING_1` (owner: "Yes in 1" admitted the whole
slate spine; final ruling trimmed the warning theme). Analysis + engine notes:
`design/Jawa/worldbuilding/biomes/leaningscrub_bedazzle_review_2026-09-29.md`
§Candidate mechanics slate. Mod: `src/RimMandrake/LeaningScrub/`.

🔴 **Trim law (owner, final ruling): "Too much focus on constant advanced
warning... Players arent that into it."** Build the systems, not the
instruments: no alarm buildings, no radar features, no warning-UI. The Stall's
natural silence and the ecology's behavior may still be *noticed* by a player —
they are never built as a warning product.

## spec

1. **The Stall and the Gale** (names RULED 2026-09-21, WeatherDefs at last;
   ban 5 enforced — every ordinary weather carries wind). Stall: wind dies,
   small fauna freeze, stallhawk (RM_Zellik) rises, concealment penalties for
   movers. Gale: hearing/speech shot, turbine surge past capacity with
   breakdown risk on the surplus, raid-arrival weighting toward Gale windows.
2. **The Lean** — per-map locked wind vector (darkward→sunward): v1 scope is
   animals-smell-pawns downwind (hunt from upwind or spook) + fire spread bias
   downwind + windbreak calm wakes as microcells. No hunting-AI rewrite.
3. **Vaporator + V-blight** (discoverable tech): buildable moisture farm that
   works anywhere, meager yield per the frozen trade ruling (§7 of the sheet:
   wind must also power the growlights); each vaporator dries a V-shaped wake
   downwind — owned crust terrain morphing to barrens over days (caps and
   heals, never strip-mines the map), fixing ban 7 with an owned crust
   TerrainDef while at it; wild animals raid vaporators like an oasis. Taught
   by studying a dead farmstead ruin (ties to §6 injections).
4. **The smother-craft**: smother-blanket item (fuzz fiber + giant wool),
   blanket job turns a thicket into a banked claim, seasons-long timer
   (Scribe the timestamp; legible inspect-string countdown), harvest = dead
   venomvine, the region's finest fuel.
5. **Calling-pyre + fire-stamping giants**: any open fire above threshold
   pulls thunderstep herds to stamp it and its source (roofed/enclosed fires
   exempt or every stove summons gods); the calling-pyre Ideology ritual
   torches your own fields to bring the herds down on all who remain
   (precept variants forbidden/last-rite/venerated). Fire implies folly.
6. **The ripple** — canopy concealment as a weather-keyed field (strong in
   wind, doubled in Gale, cancelled by moving in the Stall); a subtle shimmer
   is acceptable as feedback, not a warning meter.
7. **Rich soundscape** (owner-typed, REVERSES the old silence concept): "A
   rich soundscape of bugs and birds and stranger animals in the wind." —
   layered ambient SoundDefs: tikkit click-chorus, flutterer wingbursts,
   stranger calls carried on the wind state; the Stall simply goes quiet
   because the wind does.
8. **Inhabited injections** (owner-typed): "Lots of inhabited injections all
   over here from ruins to current living denizens." — mapgen scatter set:
   dead farmsteads (vaporator ruins, the §3 study source), smother-claim
   fields mid-cycle, venomvine curtain-wall homesteads, and CURRENT denizens
   (camps/sites of living locals), spread wide. FOUNDRY specs the set-piece
   list; PlacedSetPieces reuse where it fits.
9. **Twitcher lash** — MapComponent proximity strike for
   `RM_TwitcherVenomvine` (⛔ plant comps only TickLong; the lash cannot ride
   a plant comp).

Feature-gate everything in Mod Settings; defaults = shipped; all-off degrades
gracefully. Live verifies by STATE READ, never unattended screenshot hunts.

## criteria

- Nine-mark re-score at close: expected end-state is mark 6 (gravship) as the
  one owner-accepted MISS (both halves cut by his word, 2026-09-28); every
  other mark HAVE.
