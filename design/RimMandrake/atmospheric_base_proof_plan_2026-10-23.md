# AtmosphericBase proof plan (2026-10-23)

Owner's words, passed on by the parent seat: "add and exercise all your new validation capabilities on
[AtmosphericBase] and make a thorough but fair script for it. Tricky given it is time dependent."

The script is `src/RimMandrake/AtmosphericBase/proof_atmosphere.py`. It complements `validation.py`, the modcheck
Suite with the Phase 1-2 chains, and does not replace it. It can be run offline with `--selftest`, which uses a stub
bridge. Live, it runs under python.exe from the repo root and its output is piped through `tr -d '\r'`.

## 1. How time is handled

The mod runs on real time (L10). The compositor runs in `MapComponentUpdate` every 6 frames, reading
`Time.realtimeSinceStartup`. Game ticks do not drive it, so stepping ticks proves nothing about it, and a
wall-clock proof of a 900 s territory turn would be slow and flaky. The proof therefore uses three clocks.

| clock | what drives it | used for | why it is fair |
|---|---|---|---|
| **V** virtual | the proof hook calls the SHIPPED `RM_Compositor.Evaluate(comp, t)` at `t0 + k*dt` | every law row | The code is the one that ships, and only the time argument is supplied. The result is deterministic, instant and repeatable. A 900 s turn is 241 calls. |
| **R** real | the running game, paused | L10 only (light moves while paused) | This is the one property that needs the real frame loop. A pause is proven by a `ticksGame` delta of 0, because `set_time_speed` lies about it. |
| **G** game ticks / Scribe | `save_game` and `load_game` | R1 only (opt-in, `--with-reload`) | Save/reload is the only property that depends on Scribe. Cost is timed inside the hook (C1), not over a tick window. |

The V clock uses three seeds, and every seed must pass:

- `t0 = 1000.0`;
- `t0 = 1000 + 0.37 * period`, so the run does not start on a phase boundary;
- `t0 = 86400.5`, a day of uptime. `realtimeSinceStartup` is a float32, so this seed catches loss of precision.

Sampling steps are set by the law, not by what the code currently does:

- territory: `dt = period / StepsPerTurn` (3.75 s at the shipped 900 s) over one full turn plus one step;
- tremor: `dt <= flicker / 2` (0.4 s) over at least 240 s;
- mood: `dt = 0.5 s` over `2 * massPeriod`.

## 2. Hook contract (to be built by the C# helper; until then the rows read UNMEASURED/HARNESS)

`RimMandrake.AtmosphericBase.RM_AtmosphericBaseProof.ProofSample(string args)` returns JSON as text and is called
through `jawa/static_call`. The `args` are `cmd=<name> k=v ...`, separated by spaces.

| cmd | returns |
|---|---|
| `sanity` | `{"lamp":id, "forced":[[r,g,b],[r,g,b]], "a":[r,g,b], "b":[r,g,b], "static_id":id}`. The hook forces one fixture to the two `forced` colours in turn, and reads each back as `a` and `b`. |
| `pick` | `{"fixtures":[ids], "lit":n, "spread":cells, "untaken":id}`, the lit fixtures on the current map, plus one lit fixture the mod does not hold (the L10 and S2 control) |
| `series scenario=S t0= dt= n= [period=]` | `{"period":P, "lead_share":s, "lead_expected":k, "lead_claimant":name, "palettes":{"lead":[..],"other":[..],"tremor":[[..],..],"mood":[..]}, "same_t_writes":0, "samples":[{"t","step","fx":[[id,r,g,b,owner,role,contrib]..],"writes","contributors","ctl":[r,g,b]}..]}`. `gesture` and `narrator_alarm` add `t_g`, `D` and `twin`; `unlit` adds `unlit_id`, `unlit_writes` and `skipped_unlit_delta`; `white_scheme` returns `{"valid":bool}`; an unbuilt scenario returns `{"unknown_scenario":S}`, and a scenario nothing shipped can show returns `{"unsupported":why}`. |
| `counters` | the compositor counters plus `RM_PaletteGuard.violations` |
| `settings` | `{"settings":{..Cur..}, "default_scheme":{defName, palette, mayGoDark, flasherCount, massPeriodSeconds}, "dark_scheme":{..}}` |
| `cost n=` | `{"ms_per_eval":x, "fixtures":n}`, a Stopwatch around `Evaluate`. `jawa/map_comp_timing` cannot see this mod: it times only `MapComponentTick`, and the mod has none (lesson 20261024T030644Z). |
| `snapshot` | `{"fx":[[id,r,g,b]..]}` |
| `hold id=` / `release id=` / `is_taken id=` / `showing id=` | `{"ok":bool}` / `{"ok":bool}` / `{"taken":bool}` / `{"showing":"<scheme>:<index>" or null}`. These wrap `RM_AtmosphericBaseAPI`, which takes a `Thing` that `jawa/static_call` cannot build from an id string; the hook resolves the ThingID. They are used by L10 and R1. |

The scenarios are `one_mood`, `territory`, `territory_swap`, `territory_short_period`, `tremor`, `default`, `dark`,
`unlit`, `white_scheme`, `gesture`, `narrator_alarm`. In `role`: L = lead, O = other, T = tremor flicker, N = Narrator,
S = substrate, and `owner` is 0, 1 or -1.

The hook restores settings, moods and fixture colours in a `finally` block. Row R2 proves that it did, by comparing
`snapshot` before and after.

If a method or command is missing, the row is UNMEASURED/HARNESS. If fewer than 10 lit fixtures are spread over at
least 8 cells, the row is UNMEASURED/SITE. Neither is ever PASS.

## 3. Rows and bands

The bands come from the laws and the kernel constants in `RM_TerritoryKernel` and `RM_TremorKernel`, not from
current output.

| id | law | measures | band, and why |
|---|---|---|---|
| P1 | - | the offline gate: the hook source declares `ProofSample` | present, or else all V rows are HARNESS |
| P2 | - | the bridge answers, and the running tier list includes the mod | the mod is running |
| P3 | - | log revive and a sentinel round-trip | alive, or Z1 is UNMEASURED |
| S1 | sanity | the forced palette[0] and palette[1] read back distinct, each equal to what was forced | the sampler can see a colour change |
| S2 | sanity | an untaken, static fixture | zero variance over the series. This is a negative control: the sampler does not invent motion. |
| S3 | sanity | determinism: the same `t0` run twice | byte-identical samples |
| L4 | L4 | colours outside the union of declared palettes, across all seeds | 0, and the `PaletteGuard` delta is 0 |
| W1 | §2.6 | the writes reported against the per-fixture value changes counted from the samples | equal at every step; a re-evaluation at the same `t` writes 0 |
| L5a | L5 | the leader count against `LeadCount(N, share)` = ceil(N * clamp(share, 0.5, 0.8)) | exact at every sample. Ragged moves only the bearing, never the count, because the lead holds a contiguous wedge of `LeadCount` fixtures. Both claimants hold at least 1. |
| L5b | L5 | allocation, not mixing: each fixture's colour is in its owner's palette | 0 exceptions |
| L5c | L5 | the boundary moves: the share of fixtures that flip owner at least once in one turn | at least `1 - lead_share`. A rotating straight front sweeps `2 * (1 - lead)` of the fixtures; half of that is the margin for ragged and for clustered layouts. |
| L5d | L5 | the front has its own clock: owner changes happen only at `ClockStep` boundaries, and the period is at least 240 s | an off-boundary flip fails; a 60 s setting clamps to 240 |
| L5e | L5 | rank order: swapping the ranks swaps the leader | the lead claimant changes |
| L6a | L6 | the tremor contributor count at each step | at most 3 (LawCap) |
| L6b | L6 | fixtures flickering at the same instant | at most `max(1, floor(N * 0.10))` |
| L6c | L6 | each flicker colour against its contributor's own tremor palette | 0 exceptions; a tremor never reads as territory |
| L8 | L8 | in a `mayGoDark` scheme, every window of one `massPeriod` | at least one non-black frame and variance above 0. UNMEASURED if no shipped scheme goes dark. |
| L9 | L9 | an unlit fixture | 0 writes to it, and `skippedUnlit` rises |
| L10 | L10 | paused and verified by a 0 tick delta, `Showing(Thing)` sampled every 2 s for one mass period plus 10 s (130 s for Lamplight) | at least 1 transition, in each of two runs. If the tick delta is not 0, the row is UNMEASURED/HARNESS. Control: an untaken fixture shows null throughout. |
| L11a | L11 | non-Narrator samples with every channel at or above 200 | 0 |
| L11b | L11 | the `white_scheme` scenario | rejected by `Valid` |
| L12 | L12 | Narrator against alarm, at the same instant | the Narrator's role wins |
| L13 | L13 | after a gesture, against a COUNTERFACTUAL twin (the substrate evaluated at the same `t`, with no gesture) | exactly equal for `t >= t_g + D`. The pre-gesture snapshot cannot be the reference, because the substrate moves. |
| N1 | §Narrator | the envelope | rises to white; the dim never increases and lasts longer than the rise |
| D1 | gentle | the defaults read offline from `RM_AtmosphericBaseSettings.cs` and the scheme XML | `flasherCount` 0, `mayGoDark` false, no white, period at least 240, `tremorMaxFraction` at most 0.10, cap at most 3 |
| D2 | gentle | the same defaults, read live from the hook's `settings` | equal to D1 |
| D3 | gentle | the light-show meter on the `default` series, per fixture | at most 6 transitions per minute, and never two changes within 2 s |
| C1 | cost | ms per evaluation at the live fixture count | PROVISIONAL: at most 0.1 ms per evaluation per 100 fixtures |
| K | - | the mod's own self-judging hooks `ProofTakeover`, `ProofCompositor` and `ProofTerritory` | every key that validation.py wants reads True. A missing key is UNMEASURED/HARNESS. |
| X1 | - | the K answers against the independent V rows (boundary, tremor cap, palette) | they agree. A disagreement means one of the two instruments is wrong. |
| R1 | save | opt-in (`--with-reload`): take over, save, reload, Release | the claim survives the reload, and after Release no fixture is stuck in a scheme |
| R2 | hygiene | the fixture snapshot before and after the run | identical |
| Z1 | log | warn+ lines from the mod during the run, through the LogTap | 0. UNMEASURED if `lost > 0` or the log is not alive. |

These are Phase 5+ rows (gesture and Narrator), with `L13` and `N1` among them. Until the hook knows the scenario
they read UNMEASURED/HARNESS ("not built"); they never pass by default.

## 4. Negative controls

`--selftest` runs a good stub model, a Phase-5 model, and eleven bad ones. Each bad model must flip its own row to
the expected status and class:

| bad model | row it must flip |
|---|---|
| an off-palette colour | L4 FAIL |
| a static boundary | L5c FAIL |
| mixed colours | L5b FAIL |
| 30% tremor | L6b FAIL |
| a white non-Narrator colour | L11a FAIL |
| a gesture that does not restore | L13 FAIL |
| a pause that did not take | L10 UNMEASURED/HARNESS |
| no hook | V rows UNMEASURED/HARNESS |
| no fixtures | UNMEASURED/SITE |
| a blind sampler | S1 FAIL, V rows UNMEASURED/HARNESS |
| a hook that leaves a fixture changed | R2 FAIL |

Each pure metric also has synthetic controls. For example, a black, static series fails L8, and a flip off the
clock boundary fails L5d.

## 5. A live sitting

You need a colony map with at least 10 lit standing lamps spread out (a dev quicktest will do), the mod on the
running list, the bridge held, and the C# hook `ProofSample` built and deployed. The bridge calls are:

- `jawa/static_call`: `ProofSample` (about 30 series and probe calls, plus about 260 `showing` calls for L10), the
  three existing hooks, and `Verse.Log` Clear and Warning for the log revive;
- `jawa/time_clock` and `jawa/set_game_speed` (the pause);
- `rimbridge/list_logs` (the tap);
- `jawa/running_mods` (P2);
- `rimworld/save_game` and `rimworld/load_game` (R1, only with `--with-reload`).

It takes about 6 minutes without R1: 2 × 130 s for L10, and a minute or two for the rest, depending on how fast the
hook returns 241-sample series. R1 adds one reload, about 30 s on a minimal list. Run R1 only on the minimal list,
because a full-list reload takes about 25 minutes.
