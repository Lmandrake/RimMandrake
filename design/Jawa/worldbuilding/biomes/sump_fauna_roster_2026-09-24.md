# The Sump — invented fauna roster

_Drafted by a Fable design subagent, 2026-09-24, against the frozen sheet, for the
`RM_TheSump` sitting._

**Status: DESIGN PROPOSAL. Nothing authored.**

Subject: `RM_TheSump` (packageId `mandrake.rm.thesump`, `THESUMP_RM_MOD_BUILD_1`).
Companion doc: `sump_flora_roster_2026-09-24.md`. Frozen sheet: `the_sump.md` —
its rulings bind; this roster adds detail and never changes one.

## READ FIRST — nine residents, and two deliberate absences

Every row is **`RM_` tier — invented, franchise-free, cast inline** (Q11a). The
free mod must stand rich alone; the campaign layer only adds (§8). Sheet §0's
correction governs the head-count: animalDensity 3.5 dropped to
**sparse-but-strange** — nine rows at low commonalities is a full cast here,
not a thin one, and the near-emptiness of the black is itself the design.

⛔ **Two things are out of scope and must not be folded in:**

| not here | why | who owns it |
|---|---|---|
| **the tar beast** | 🔴 sheet §6 ban 2: never a fightable/wild spawn — a set-piece woken by cause, evacuated ahead of, never fought. Its scaffold is shipped (`RUT_BeastBulge`, `RUT_SumpTarBeastGenStep`, `RM_CompBeastWakeRelay`, `RM_CompStationEater`, `DEPLOY_HOLD` for art); its eventual creature content is Patient-family work registered with `sarlacc_spec.md` | `SUMP_MECHANICS_1` / the Patient family |
| **the 5 current roster rows** (3 wired donors + 2 unwired imports) | evictions are stopped; dispositions are **PROPOSED in §7** at this biome's own sitting and executed by nobody here | the owner |

🔑 **One-home law**: every row below is Sump-only, one home, no exceptions
claimed. Nothing migrates, nothing has a moving life stage — the biome is a
trap; its animals do not leave.

🔑 **Flight**: no row flies, and that is a design statement, not an oversight —
sheet §9's motion doctrine is *"mice, derrick-nod, lamp-flicker — and the
pools, never."* A flier would hand the dead-flat horizontals a second motion
the theme refuses. Open ruling 1 puts the category to the owner before any
within-category question exists. (If he ever wants one, the standing rule
applies: real `MaxFlightTime`, stat-not-bool.)

### The silhouette brief is the specification

Every form must be nameable from a top-down sprite in permanent dusk against
black-on-black — the hardest legibility environment on the planet. Palette
discipline (sheet §9): every black, plus at most one pale or rust accent per
row. A row whose form duplicates another's has failed.

---

## At a glance

| the black (on/in the tar) | the under-layer (beneath it) | the margin ring |
|---|---|---|
| **sump-mouse** — runs the black; the instrument | **thrummel** — the warm hive under the lid | **brommet** — the ring's wool-backed grazer |
| **gulveth** — the tar's own grazer | **thrummel warden** — the mound's temper | **skarrid** — the still hunter that mimics a bulge |
| **wrissen** — what a dig wakes | **thrummel broodmother** — the deep heart | **dredgel** — the dig-site sifter |

---

## 1. The rulings this roster serves

| ruling | source | what the roster owes it |
|---|---|---|
| **Sparse-but-strange** | sheet §0 (animalDensity correction) | 9 rows, low commonalities, no ambient filler — every row is an instrument, an industry or a hazard |
| **Mice run the black; where they won't, you don't** | sheet §4, §5 | row 1 is the prey base AND the biome's navigation system; two other rows (pallick, skarrid) are read *through* it |
| **The under-layer is kept** (hives beneath the insulating tar, aggressive at their mounds) | sheet §0 (BENCH call, roster verdict keep) | rows 2–4 replace the donor bumbledrones 1:1 in fiction — warm colonies, chitin and wax economy, mound aggression |
| **The tar defends; nothing crosses it willingly** | sheet §3 | no pursuit predator exists here (the roster JSON evicted Blurrg on exactly this); the one hunter is an ambusher that never chases |
| **The tar preserves — including live things** | sheet §3, §7 ("the tar preserves everything, including intentions") | row 8: some of what the archive keeps is still running. Open ruling 2 |
| **Tar beast = set-piece only** | sheet §6 ban 2 | absent from this roster on purpose; row 9 (skarrid) *mimics* its bulge, which is a question (open ruling 8) |
| **No vanilla-Earth fauna; no partial/whole Assailant or Rakatan spawns** | sheet §6 bans 1, 6 | zero Earth-nameable rows; nothing here is an ancient — the archive's dead stay dig-table content |
| **Chitin and honey-wax economy** | sheet §7 | the thrummel family carries it — invented product names (`seepwax`, thrummel chitin), no donor def |
| **One animal, one biome** | owner ruling 2026-09-21 | every one-home note below names why the creature *cannot* live elsewhere |
| **The free mod stands rich alone** | Q11a | nine rows, no donor, no canon needed |

## Rows

### 2. The instrument — `RM_SumpMouse` (row 1)

| field | value |
|---|---|
| defName / label | `RM_SumpMouse` / sump-mouse *(sheet-named by the owner — keeps its plain name; open ruling 6)* |
| silhouette FORM | **tiny pale wedge on absurdly broad star-feet, always mid-dash, always in a LINE** |
| look, one line | A palm-sized silver-grey mouse-analog on splayed snowshoe feet, coat beaded with shed oil — never alone, never wandering: sump-mice move in lines, and the lines are the map. |
| niche / trap-identity | ⭐ **The prey base, the charm, and the instrument** (sheet §4): mice cross tar freely *except where they won't*. A stretch of black the lines detour around is a beast's back; an unbroken pale crust no line touches is pallick's lie (flora §4). Junkers read mouse-lines the way sailors read water — and so does the player. |
| danger / utility | Harmless. Utility is the reading — and, if ruled tameable (open ruling 4), a kept cage of them becomes a living tar-detector a caravan carries. |
| commonality | 0.8 — the most common animal here; the base of every chain |
| mechanism | ⚠️ PARTIAL — the placeholder shipped (`RUT_Placeholder_SumpMouseRace`/`RUT_Placeholder_SumpMouse`, `RUT_ThinkTree_SumpMouseWander`); the line-telegraphy stack is ✅ built (`RM_MapComponent_DreadField` + `RM_JobGiver_DreadAvoidWander` + `RM_CompFilthTrail` + `RUT_Filth_MouseTrack`, `DEPLOY_HOLD` art). **Real def replacing the placeholder is this roster's work.** Free tar-crossing for the race: no vanilla per-race terrain-cost exemption exists — small NEW patch or stat trick, UNMEASURED which is cheapest (build item's call) |
| art | **OWED** — and the sprite must read at line density, not as one animal; track filth art also OWED |

### 3. The tar's own grazer — `RM_Gulveth` (row 2)

| field | value |
|---|---|
| defName / label | `RM_Gulveth` / gulveth |
| silhouette FORM | **low glossy black barge-back with a wide dredging head, half-sunk profile** |
| look, one line | A sofa-sized, tar-slick grazer that wades the shallows like a barge, skimming the black with a squared dredge-mouth — the only big living thing you will ever see touching the pools. |
| niche / trap-identity | **The tar's own grazer** — it eats the tar (the biologically rich larder), inheriting donor `AA_TarGuzzler`'s slot (§7). It is the visible proof the black is food, and its unbothered wading is what makes a *still* pool read dangerous by contrast. |
| danger / utility | Placid unless provoked; huntable for dense fat and a tar-cured hide (waterproof leather — the biome's own coat). Slow: spd ~2, the donor's register kept. |
| commonality | 0.45 |
| mechanism | none new — "eats what no normal animal eats" is diet/def work; no C# |
| art | **OWED** |

### 4. The under-layer — the thrummel family (rows 3–5)

The donor bumbledrones' fiction, kept by ruling and re-founded as ours: warm
heat-huddled colonies tunneling beneath the insulating tar, aggressive at their
entrance mounds — a second "something beneath," in miniature (sheet §0). One
species, three castes, one hive economy: **thrummel chitin** and **seepwax**
(the honey-wax analog — combs provisioned with tar-sugars the workers crack).

| field | `RM_Thrummel` (row 3) | `RM_ThrummelWarden` (row 4) | `RM_ThrummelBroodmother` (row 5) |
|---|---|---|---|
| label | thrummel | thrummel warden | thrummel broodmother |
| silhouette FORM | **round furred bumbler, heat-shimmer soft edges** | **the same body armoured, head-heavy, planted at a mound** | **swollen wax-pale abdomen dragging a small fore-body** |
| look, one line | A fist-and-a-half of dense-furred, soot-dark burrower, comically round, forever hurrying between mound and dark. | A thrummel built into a wedge — plated brow, bigger jaws, standing sentry in the mound-mouth. | A pale, wax-sheened matriarch the size of a dog, rarely surfaced, glistening like her own comb. |
| niche | the worker caste; the warm under-layer's traffic | 🔴 the mound's temper — the aggression radius made flesh | the deep heart of a colony; kill or capture ends the hive |
| danger / utility | harmless singly; **chitin + seepwax** on the comb (sheet §7's economy) | dangerous AT the mound, indifferent a step away — mound-raiding is a deliberate, priced choice | guarded; the jackpot raid and the moral of it |
| commonality | 0.35 | 0.15 | 0.05 |
| one-home note | the hive works ONLY under an insulating tar lid over cold ground — the biome's physics is the species' physiology; nowhere else on the planet has the lid | rides the hive | rides the hive |
| mechanism | 🆕 NEW (small) — mound Thing + defend-radius aggression. ⚠️ Vanilla's insect `Hive` comp family (`CompSpawnerPawn` etc.) is the near-fit engine pattern; whether it reskins cleanly without Harmony is an engine question — **UNMEASURED on this machine**, flag for the Desktop | rides the mound | rides the mound |
| replaces | donor `AA_Bumbledrone` (0.35) | donor `AA_BumbledroneHierophant` (0.2) | unwired import `AA_BumbledroneQueen` (§7) |
| art | **OWED** | **OWED** | **OWED** |

### 5. The margin ring — `RM_Brommet` and `RM_Dredgel` (rows 6–7)

| field | `RM_Brommet` (row 6) | `RM_Dredgel` (row 7) |
|---|---|---|
| label | brommet | dredgel |
| silhouette FORM | **small round-backed grazer under a grey wool mantle, head down in a rosette patch** | **long low many-legged sifter, tail-dragging, parked at broken ground** |
| look, one line | A knee-high, wool-mantled edge-grazer the colour of the margin scrub, cropping skelver rosettes in twos and threes. | A forearm-long armoured sifter that combs opened digs and old shafts, feeling through spoil with wire-thin fore-limbs. |
| niche / trap-identity | **The ring's herbivore** — something must eat the edge-flora (flora §3), and the Junkers must eat something with legs. The biome's only ordinary meat and a modest wool. | **The archive's janitor.** It eats the organic fringe of what digs expose — and so it *finds digs*: dredgel parked on flat ground means broken tar below, an old shaft, someone's abandoned claim (sheet §8's dig fields, read by fauna). |
| danger / utility | none; meat, wool, charm | harmless; a free prospecting hint, and chitin if shot |
| commonality | 0.4 | 0.2 |
| one-home note | its gut runs on chemotroph wax-flora — the ring is the only pasture of its chemistry on the planet | its food is what tar-digs expose; no digs, no dredgel |
| mechanism | none | placement/wander biased to dug or shaft cells — ✅ mostly EXISTS as a pattern (`RM_JobGiver_DreadAvoidWander` shows the JobGiver shape; this is its attract-mode cousin, small NEW) |
| art | **OWED** | **OWED** |

### 6. The two frighteners — `RM_Wrissen` and `RM_Skarrid` (rows 8–9)

| field | `RM_Wrissen` (row 8) | `RM_Skarrid` (row 9) |
|---|---|---|
| label | wrissen | skarrid |
| silhouette FORM | **a boil of thumb-length slivers, read as a MASS, never singly** | **flat glossy hummock with a seam — a bulge that is slightly too small to be the Beast** |
| look, one line | Thumb-sized segmented biters, tar-black and dripping, that erupt as a swarm from broken deep tar — moving like one angry liquid. | A flattened, glass-smooth ambusher that lies half-sunk at the glass-reach margins, indistinguishable from a swell in the tar until the seam opens. |
| niche / trap-identity | ⭐ 🔴 **What the archive keeps alive.** Wrissen are preserved dormant in the deep black — the tar takes slowly and keeps *perfectly*, and sometimes what it kept is still running. A deep dig, a greedy pump, a moat cut too deep can open a pocket; the swarm is the trap remembering you. | ⭐ **The still hunter.** It takes sump-mice (and the unwary hand) at the margins, by stillness: the pools never move — *until* (sheet §9). Mouse-lines detour around a skarrid exactly as around the Beast's back, so every skarrid is a small, survivable lesson in reading the black. |
| danger / utility | a burst hazard — painful, mob-scale, finite; the pocket empties and the swarm starves fast on the surface. Never map-persistent wildlife | genuinely dangerous to a lone pawn; its glassy hide is a prized black leather. It never chases far off the black — ambush, not pursuit (sheet §3) |
| commonality | 0 as ambient — **event-spawned by the dig lottery / beast-wake causes only** (open ruling 2); at most 0.05 near dig fields if the owner wants strays | 0.25 |
| one-home note | exists only inside deep tar; it *is* the biome | its whole hunt is mouse-lines on glass margins; no other biome has either |
| mechanism | ⚠️ PARTIAL — the causes are built (`RM_CompWorkedLottery` outcomes, `RM_CompBeastWakeRelay` for cause-plumbing); a **spawn-pawns lottery outcome kind** is NEW (small): whether `RM_LotteryTableDef` rows can already name a pawn spawn is UNMEASURED — check before writing one | ambush stillness: vanilla predator hunting covers the kill; the *mimic-bulge* read is art + a dread-field registration — ⚠️ PARTIAL (`RM_MapComponent_DreadField` exists; registering skarrid as a mobile minor dread source is small NEW) |
| art | **OWED** — must read as a mass | **OWED** — must be mistakable for `RUT_BeastBulge`'s art at a glance, and distinguishable on a stare (open ruling 8) |

## 6b. Legibility matrix — the acceptance test

| form | row | reads as |
|---|---|---|
| pale wedge on star-feet, in a line | sump-mouse | the map, moving |
| half-sunk black barge with a dredge-mouth | gulveth | proof the black is food |
| round soot bumbler, hurrying | thrummel | warm industry underfoot |
| the same, armoured, planted in a mound-mouth | thrummel warden | a priced door |
| wax-pale matriarch, glistening | thrummel broodmother | the jackpot and the moral |
| wool mantle over a grazing rosette-cropper | brommet | ordinary dinner (the only one) |
| low many-legged sifter parked on flat ground | dredgel | someone dug here |
| a boil of black slivers | wrissen | the archive, objecting |
| a bulge that is slightly too small | skarrid | **the Beast — which is the lie** |

🔑 Two rows are deliberately deceptive and the matrix records it on purpose:
**skarrid** must be mistakable for a beast-bulge (its survival strategy and the
player's recurring false alarm), and **pallick** (flora §4) must be mistakable
for mirrelin. Both lies are broken the same honest way: *the mice tell you.*
An art pass that makes either unmistakable has deleted the biome's literacy
game.

## 7. What is replaced — disposition of today's 5 roster rows (PROPOSED)

The live `RUT_Sump` def carries 3 wired donor rows; the roster JSON adds 2
unwired imports (build item §3/§5). ⚠️ Evictions are stopped — these
dispositions are PROPOSED for **this biome's own sitting** and executed by
nobody here.

| row today | comm. | proposed disposition | why, in one line |
|---|---|---|---|
| `AA_TarGuzzler` (donor, `sarg.alphaanimals`) | 0.5 | **replace with `RM_Gulveth`** | same slot, same register (slow tar-grazer), ours — the standalone mod cannot depend on Alpha Animals |
| `AA_Bumbledrone` (donor) | 0.35 | **replace with `RM_Thrummel`** | the kept under-layer fiction, re-founded as our species |
| `AA_BumbledroneHierophant` (donor) | 0.2 | **replace with `RM_ThrummelWarden`** | rides the hive verdict |
| `AA_BumbledroneQueen` (unwired import) | 0.5 | **land as `RM_ThrummelBroodmother` instead of wiring the donor** | it was never wired; wiring a 4th donor def the day before replacing it is backwards |
| `Hssiss` → `RSW_Hssiss` (unwired import, RULED 2026-09-10: the Sump move STANDS — tar-sleeper, partial-remains register) | 0.18 | **keep, via the planned Utinni patch `WildAnimals_Sump.xml`** (build item §3 — file confirmed not existing yet) | genuine canon → campaign layer by Q11; the ruling that seated it here is not touched by this roster |

A donor row cut *here* and alive elsewhere is that biome's business, not ours
(cut-scope ruling, 2026-09-21).

## 8. Canon injection (additive, Utinni layer)

- **`RSW_Hssiss`** is the biome's one seated canon beast (ruled 2026-09-10,
  §7): a tar-sleeper in the partial-remains register, riding the future
  `UtinniPatches/Patches/WildAnimals_Sump.xml` onto `RM_TheSump` — additive,
  beside the free cast, exactly as Q11 requires.
- **No further canon injection is recommended.** The Sump's cast is a reading
  lesson — instrument, industry, two lies — and no surveyed candidate earns a
  slot past the opportunistic bar. Any future candidate is verified through the
  Wookieepedia search API, never a donor defName, and absence from
  `canon_references/` proves nothing.

## Mechanism inventory (exists / partial / new) — roll-up

| proposal | status |
|---|---|
| mouse-line telegraphy (dread field, avoid-wander, track filth) | ✅ EXISTS — `RM_MapComponent_DreadField`, `RM_JobGiver_DreadAvoidWander`, `RM_CompFilthTrail`, `RUT_Filth_MouseTrack` (+`RUT_TarShallow_FilthAcceptance`), `RUT_ThinkTree_SumpMouseWander` |
| sump-mouse real def (replacing placeholder) | ⚠️ PARTIAL — `RUT_Placeholder_SumpMouseRace`/`RUT_Placeholder_SumpMouse` shipped as placeholders; this roster's row 1 is the real content |
| mouse free tar-crossing | 🆕 NEW (small) — no vanilla per-race terrain-cost exemption; UNMEASURED which implementation is cheapest |
| beast set-piece plumbing (out of roster scope, listed to prevent re-invention) | ✅ EXISTS — `RUT_BeastBulge`, `RUT_SumpTarBeastGenStep` + `_Register`, `RM_CompBeastWakeRelay`, `RM_CompStationEater`, `RUT_BeastBulge_DreadRegistration` |
| dig lottery (wrissen's trigger) | ✅ EXISTS — `RM_LotteryTableDef`, `RUT_DigStratumTable`, `RM_CompWorkedLottery`, `RM_WorkGiver_WorkLottery`, `RM_JobDriver_WorkLottery`, `RUT_DigShaft` |
| lottery outcome that spawns pawns (wrissen burst) | ⚠️ PARTIAL/UNMEASURED — tables exist; whether an outcome row can name a pawn spawn is unchecked. Check before writing new C# |
| thrummel mound + defend radius | 🆕 NEW (small) — vanilla `Hive`/`CompSpawnerPawn` is the near-fit pattern; clean-reskin feasibility is an engine question, UNMEASURED here |
| skarrid as mobile minor dread source (mouse-lines detour) | ⚠️ PARTIAL — dread field exists; mobile registration is small NEW |
| dredgel dig-site attraction | 🆕 NEW (small) — attract-mode cousin of the shipped avoid-wander JobGiver |
| gulveth tar diet | ✅ def-only — no C# |
| moat/burn, dusk lock, smoke column (context the cast lives in) | ✅ EXISTS — `RM_CompFloodIgniter`, `RM_CompTimedTerrainBurn`, `RM_MapComponent_ThresholdSmokeColumn`, `RUT_SumpDuskLock`/`RUT_SumpWeather`, `RUT_TarMoat`/`RUT_TarSpent`, `RUT_MoatFusePost`, `RUT_TarBlaze` |

## Open rulings for the owner

At most eight, category-first, each with a recommendation. Simple words.

1. **Should anything fly in the Sump?** The sheet's motion list is mice,
   derrick-nod, lamp-flicker — and the pools, never. A flier would add a fourth
   motion to a place built on stillness. **Recommendation: no flier at all.**
   (If yes, we design one new — it gets real flight per the standing rule.)
2. **When a dig goes wrong, should it sometimes wake up small LIVE things** —
   a burst of preserved biters (the wrissen) — alongside the ruled traps and
   treasure? It says the sheet's line out loud: the tar keeps everything,
   perfectly. **Recommendation: yes, rare, and only from digs/deep works —
   never as ordinary wildlife.**
3. **Do you want a farmable food crop here** (the dorvel, flora doc §2), so a
   Sump colony can feed itself without sunlamps, the way the stations do?
   **Recommendation: yes — it is the stations' fiction and the biome's
   playability in one plant.**
4. **Should sump-mice be tameable?** A kept cage of mice is a living
   tar-detector a caravan can carry — the biome's instrument made portable.
   **Recommendation: yes, cheap and easy — charm plus utility, no combat
   value.**
5. **May a plant lie?** The pallick (flora doc §4) mimics safe crust over deep
   tar; stepping on it mires and hurts, never kills outright, and the mice
   always tell the truth about it. **Recommendation: yes — it is "the trap
   that remembers" as a plant, with an honest tell.**
6. **Naming voice: keep your plain names for the things you named** (sump-mouse,
   wick-plant, tar beast) **and invented words for the rest** (gulveth,
   thrummel, skarrid…)? **Recommendation: yes — both voices are yours; the
   sheet's own names stay.**
7. **The hive replacement (thrummel): keep the bumbledrone deal exactly** —
   warm under-layer, chitin + wax, aggressive only at the mounds — **just as
   ours instead of the donor's?** **Recommendation: yes, 1:1 — the fiction was
   ruled kept; only the ownership changes.**
8. **May the skarrid (the ambusher) look like a small tar-beast bulge?** It
   trains players to fear bulges — and gives false alarms on purpose. Or is
   the bulge shape reserved for the real Beast alone? **Recommendation: let it
   mimic, smaller and subtly wrong — the false alarm is the biome teaching.**

## Appendix — collision sweep (MEASURED, this pass)

Same instrument as the flora roster (python, never a zsh loop; 4,584 files
under `design/` and `src/`; sanity probes `korrum` 39 / `stoneback` 164 /
`hawkbat` 261 — the instrument sees). **All 8 new fauna names (`gulveth`,
`thrummel`, `skarrid`, `dredgel`, `brommet`, `wrissen`, plus caste labels) have
0 occurrences outside the Sump sitting docs.** `SumpMouse` exists only as the
shipped placeholder pair this roster's row 1 replaces — the intended
continuity, not a collision.
