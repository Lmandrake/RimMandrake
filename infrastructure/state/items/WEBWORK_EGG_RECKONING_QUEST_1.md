## spec

Design: `design/Jawa/worldbuilding/biomes/webwork_egg_blackmarket_2026-09-24.md`
§2 (the assassination quest family) and §3 (the hatch mechanism), S5 rulings
2, 3, 6, 7. Split out of `WEBWORK_EGG_BLACKMARKET_BUILD_1` because it is
genuinely the largest, riskiest piece of that item and the design's own text
says so honestly (§2b: "this is the family's one C# verb"; skill's own rule:
"a custom C# root has a failure mode XML does not — dropped at selection
time with no log entry at all").

**Why deferred rather than forced this pass:**

1. **A real dependency chain, not yet fully landed.** The quest references
   `RM_OllathrixEgg` (built by `WEBWORK_NEST_EGG_ECONOMY_1`, landing
   concurrently this session — check it is closed and re-read its final shape
   before writing the quest's `ThingDef` references) and the Cartel egg-market
   trader/faction (`RUT_Caravan_HuttCartel_EggMarket`,
   `RUT_Jawa_HuttCartel` — both now built by this item's own
   `WEBWORK_EGG_BLACKMARKET_BUILD_1` pass, see `ShokkweaveEggBlackMarket.xml`
   and `RUT_HuttCartel_EggMarket.xml`).
2. **One genuinely new C# verb, unbuilt:** §2b's plant-watcher — "deliver an
   item covertly to a cell inside an enemy site" has no vanilla `QuestNode`.
   Needs a small `QuestPart`/`QuestNode` pair watching (a) the egg Thing's
   position reaching the marked cell and (b) the site's hostile-alert state,
   emitting a completion signal either way (planted vs. discovered-first). §3
   then needs a second small C# piece: at the night tick after a completed
   plant, spawn one hostile `RM_Ollathrix` at a **juvenile life-stage age**
   (ruling 3 — no new PawnKindDef) at the egg's cell and despawn the egg.
3. **Several numeric rulings are still `❓` in the accepted design**, not
   pinned by S5 rulings 1-7 (which cover mechanism, not numbers): the offer
   window (`expireDaysRange`), the completion timer, the three paths' exact
   silver amounts, the discovery-chance-per-hour, and the night-window bounds
   (`❓23h-02h`). These need either owner numbers or defensible invented ones
   before the def is final — do not invent them silently; the skill's own
   §2 ten-question gate treats a vague deadline/reward as a rewrite, not a
   detail.
4. **No deterministic offline verify exists for the stealth/hatch logic.**
   `skills/rimworld-quests/scripts/validate_quest.py` checks node shape,
   signals, grammar and firing routes — it cannot exercise "does the
   plant-watcher actually detect the egg reaching the cell" or "does the
   juvenile Ollathrix actually spawn hostile and scaled correctly," both of
   which need a live quicktest map (`rimworld-debug-testing` skill) or a
   dev-mode quest generation pass, i.e. bridge/game-up work this item is not
   scoped for (`needs: offline`).

**What ships when this is picked up:**

- `RUT_HistoryEvent_EggAssassination` (`HistoryEventDef`) — fires on every
  path-3 completion regardless of discovery (§2d).
- `RUT_Reckoning` (placeholder name; bind the real defName at build time per
  `NAMING_SCHEME_PLAN.md`) `QuestScriptDef`: the three-path structure in §2a
  (pay / capture-alive / plant-the-egg), `givenBy` the Cartel trader channel
  as the primary route with a low-weight random-pool fallback (§2a "Giver and
  firing route").
- The plant-watcher + night-hatch C# (new files under a campaign-tier
  assembly — `mandrake.rut.shokkweaveeconomy`'s own `Source/` is the natural
  home since it already owns the egg economy, or a small dedicated quest-verb
  assembly if that one's `.csproj` shape doesn't fit; check
  `EnableDefaultCompileItems false` conventions before adding files — CLAUDE.md
  "ceiling fields" note applies to any `.csproj` here).
- Register the new `.cs` file(s) explicitly in the owning `.csproj`'s
  `<Compile Include>` list, rebuild via Windows-native `dotnet.exe`, and
  regenerate the `.srchash` sidecar (`DLL_SOURCE_STAMP_GUARD_1`) before
  committing the DLL.
- Run `python3 skills/rimworld-quests/scripts/validate_quest.py` on the new
  def before any load; read every WARN, since the calibration note says the
  false-positive rate is low.
- `WEBWORK_EGG_WEAPON_VERSION_1` (S5 ruling 7, filed as v2 by BENCH) is
  explicitly OUT of this item's scope — quest-only planting stands here; the
  free-form colony-weapon version needs its own owner card before it builds.

## verify

Offline: `validate_quest.py` clean (0 errors, warnings read and triaged).
Live (separate, game-up pass, not this item's `needs: offline` scope): dev
Generate Quest, walk all three paths including a deliberately-discovered
plant, confirm the juvenile spawn is genuinely losable and genuinely
dangerous, confirm total deniability (zero goodwill change) on an
undiscovered kill per ruling 6.
