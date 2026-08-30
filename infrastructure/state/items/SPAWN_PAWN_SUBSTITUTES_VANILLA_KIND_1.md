# SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1 — "Spawned 2/2" delivered one of something else

## ✅ TOOL FIX PROVEN LIVE, 🔴 AND THE RATE IS AN ORDER OF MAGNITUDE LOWER THAN RECORDED — 2026-08-30 (FOUNDRY)

Fresh 585-mod quicktest. The fixed `jawa/spawn_pawn` (with `kindActual` /
`kindSubstituted` / `substitutedCount`) is deployed. **480 spawns, 240 per cell** — the
`>=60 per cell` this item's own CORRECTION section demanded, and 12× the sample any
previous cell had.

### The read-back works, and it is honest
All **480 rows** carried `kindRequested`, `kindActual` and `kindSubstituted`. On a
substitution the tool now says so instead of counting it as the requested kind:
```
Spawned 39/40 Jawa_Hutt_Grunt in faction Jawa_HuttCartel.
  ⚠️ 1 did not spawn as asked -- see the rows with ok:false.
  ⚠️ 1 came back as a DIFFERENT PawnKindDef than requested -- see kindActual
     on the rows with kindSubstituted:true.
```
`spawnedCount` dropped to 39, `substitutedCount` read 1, and the offending row named
`kindActual: "Colonist"`. ⇒ **the silent-success this item was filed for is closed.** Every
substitute seen this session was a vanilla `Colonist`, which answers the outstanding
*"record the substituted kind, don't just count it"*.

### 🔴 But the faction attribution does NOT reproduce
| cell | substituted / spawned | rate |
|---|---|---|
| `Jawa_Empire_Grunt` → **`Empire`** (vanilla faction) | **2 / 240** | 0.83% |
| `Jawa_Hutt_Grunt` → **`Jawa_HuttCartel`** (authored) | **1 / 240** | 0.42% |

Against the ~**15% vs ~2%** this item records above. 2-vs-1 at n=240 is noise: **at a
proper sample size there is no detectable faction effect at all**, and the absolute rate is
roughly one-twentieth of what was recorded.

🔑 **The most likely reason the old number was inflated, and it is a method difference, not
a mod-list one.** Every earlier measurement compared a post-hoc `jawa/list_pawns` census
against the kinds requested. A fresh quicktest map **seeds its own wandering/joining
humans**, and a map-resident vanilla `Colonist` standing near the spawn point is
indistinguishable, in a census diff, from a substituted one
([[census-requested-vs-actual-kind]], [[spawn-many-for-bridge-tests]]). The fixed tool reads
`pawn.kindDef` **off the object it just generated, inside the same call**, so it cannot
count a bystander. ⚠️ Stated as the likely explanation, not a proven one — the old runs
cannot be re-examined.

⇒ **Treat the `~15% in vanilla factions` figure and the `it is the faction, not the kind`
attribution below as SUPERSEDED and not reproduced.** What survives: substitution is real
(3 events in 480), it produces a bare vanilla `Colonist`, and the five-patch shortlist and
raid-path reasoning are unaffected — those were read from source, not from these rates.

### Not attempted, deliberately
The mod-disable bisect across the five shortlisted Harmony patches needs a **game restart
per candidate** and was out of scope for this pass. It is also now a harder experiment than
it looked: at ~0.5–0.8% a cell needs on the order of a thousand spawns to separate
"disabled it" from "did not roll one", where the old 15% figure implied a few dozen would do.
**Whoever runs it should size it off 0.8%, not 15%.**

Measured live 2026-08-27, 582 mods.
Evidence: `infrastructure/state/evidence/bridge_session_2026-08-27_BUILD.md`.

```
jawa/spawn_pawn {kindDef:"Jawa_Hutt_Specialist", faction:"Jawa_HuttCartel", count:2}
  -> success: true, "Spawned 2/2 Jawa_Hutt_Specialist in faction Jawa_HuttCartel."

jawa/list_pawns -> Jawa_Hutt_Specialist x1   +   Colonist x1  (xenotype baseliner)
```

The tool counted two spawns and named the kind it was asked for. One of the two is a **vanilla
`Colonist`**. The other three Hutt kinds delivered 2/2 correctly in the same call sequence.

⭐ **And the substituted pawn is the only bare one of the eight.** The seven real Hutt pawns
all carried a weapon and apparel; the `Colonist` carried nothing.

## 🔑 Why this may matter far beyond one tool
`facts/roll_arm_harvest_2026-08-24.md` records **21 of 285** pawns rolling bare across 16 of
49 roster kinds, and attributes 13 to violence-disabling backstories while leaving **8
combat-capable bare pawns unexplained**. If those 8 are substituted vanilla kinds rather than
our kinds failing to arm, the remaining bare-hands mystery is not an arming defect at all.

⚠️ **UNTESTED — this is a hypothesis with one supporting observation.** It is cheap to settle:
spawn N of a roster kind and compare the requested `kindDef` against the `kindDef` read back,
which no previous harvest did. **Do that before anyone tunes another `weaponMoney`.**
🔑 It would also explain the *"baseliners generate in five factions"* gap already filed to
DECIDE in `five-design-gaps-found-auditing-the-seven-authored-factions-3c81ea` — a baseliner
is what a substituted vanilla kind looks like.

## criteria
- [ ] The kind read back matches the kind requested, or the tool reports the substitution.
- [ ] The bare-hands cohort in `roll_arm_harvest` is re-scored with requested-vs-actual kind
      recorded per pawn.

---

## ✅ MEASURED 2026-08-27, 150 spawns — the hypothesis above is CONFIRMED as a cause, and it is not the only one

**Run A — 16 kinds × 5.** 80 spawned: 76 ours, **4 substituted**, and **4 of the 4
substituted pawns were bare**. Substitution appeared only on `Jawa_Empire_Heavy`,
`Jawa_Empire_Specialist`, `Jawa_Hutt_Grunt`, `Jawa_Hutt_Leader`, one pawn each, with
`Spawned 5/5 <requested kind>` reported every time.

**Run B — 7 kinds × 10.** 70 spawned, 0 substituted, 5 bare, and **all 5 carry a
violence-disabling backstory. Zero unexplained.**

🔑 **Together these close the bare-hands question: two causes, no third.** A pacifist
backstory, or a substituted vanilla kind. ⛔ **There is no `weaponMoney` defect** — the
corrected `weapon_affordability.py` reports `always arms 49 · sometimes 0 · never 0 ·
unmeasured 0`, and the live evidence now agrees with it rather than contradicting it.

⭐ **This retires the "8 combat-capable bare pawns" of `roll_arm_harvest_2026-08-24.md`.**
That harvest recorded the **requested** kind, so a substituted vanilla `Colonist` was counted
as one of our kinds arriving bare with no pacifist excuse. Rates agree: 5 in 70 = **7.1%**
against 21 in 285 = **7.4%**.

⚠️ **Substitution rate here is 4 of 80 = 5%, and the sample is small.** What is NOT measured:
why those four kinds and not the others, whether the rate differs at raid generation rather
than direct spawn, and whether the substitution is `spawn_pawn`'s or the engine's
`PawnGenerator` falling back. **The last of those is the one worth knowing** — if it is the
engine, it affects raids too and no bridge fix touches it.

## criteria
- [x] The kind read back is compared against the kind requested — done, twice.
- [ ] The substitution is attributed to `jawa/spawn_pawn` or to `PawnGenerator`.
- [ ] The tool reports the substitution instead of counting it as the requested kind.

---

## 🔑 SHARPENED 2026-08-27 — substitution tracks the FACTION, not the kind

A 240-pawn run split cleanly along one line:

    kinds whose defaultFactionDef is a VANILLA faction (Empire, Pirate)   18 of 160   11%
    kinds sitting in factions we authored                                  0 of  80    0%

The guarded set was `Jawa_Empire_*` (`defaultFactionDef: Empire`, vanilla Royalty) and
`Jawa_Blackstar_*` (`defaultFactionDef: Pirate`). The control was `Jawa_Hutt_Grunt`,
`Jawa_Droid_Heavy`, `Jawa_Wildsteam_Grunt`, `Jawa_TradeMoot_Grunt` — all in authored factions,
**zero substitutions**.

⇒ **The next test is one call:** spawn `Jawa_Empire_Grunt` into an AUTHORED faction and see
whether substitution disappears. If it does, this is a faction-side pawn-generation fallback
and not a `jawa/spawn_pawn` defect at all — which also means it would reach raids, where no
bridge fix could touch it.

⚠️ **Confounded, and say so.** The two groups differ in more than faction: the guarded eight
also carry `requiredWorkTags: Violent`, which is a generation constraint that can itself force
a re-roll. **A constraint that cannot be satisfied is at least as good an explanation as the
faction**, and this run cannot separate them. Test the two independently before believing
either.

---

## ✅ CONFOUND RESOLVED 2026-08-27 — it is the FACTION, and `requiredWorkTags` has no effect

A 2×2, 20 pawns per cell, same session:

| | vanilla faction (`Empire`) | authored faction (`Jawa_HuttCartel`) |
|---|---|---|
| **guarded kind** `Jawa_Empire_Grunt` | **3 of 20 substituted (15%)** | **0 of 20 (0%)** |
| **unguarded kind** `Jawa_Hutt_Grunt` | **3 of 20 substituted (15%)** | **0 of 20 (0%)** |

**The rows are identical and the columns are not.** `requiredWorkTags: Violent` changes
nothing; the faction changes everything. Spawning any of our kinds into a VANILLA faction
substitutes ~15% of them for a vanilla kind; into a faction we authored, never.

## 🔴 Why this is a live gameplay defect, not a bridge curiosity
`Jawa_Empire_*` declare `defaultFactionDef: Empire` and `Jawa_Blackstar_*` declare
`defaultFactionDef: Pirate` — **both vanilla**. Every substituted pawn measured this session
was bare-handed. ⇒ Roughly one in seven Empire and Blackstar pawns arrives as a vanilla kind
carrying nothing, and the shipped `requiredWorkTags` guard cannot prevent it.

🔑 **And this is almost certainly the same defect `AUTHORED_KINDS_MUST_FIELD_1` exists to fix.**
That item wires orphaned role kinds into `TribeCivil`, `Pirate` and `Empire` combat groups.
Our authored factions list our kinds in their `pawnGroupMakers`; vanilla `Empire` and `Pirate`
do not. **Untested prediction:** wiring the Empire and Blackstar kinds into those two factions'
combat groups takes the substitution rate to 0, exactly as it already is for every authored
faction. ⚠️ Prediction, not a measurement — the mechanism (a faction-side fallback to
`basicMemberKind` for a kind the faction does not field) has not been read out of the C#.

## criteria
- [x] Kind read back compared against kind requested.
- [x] Attributed: the faction, not the kind and not `requiredWorkTags`.
- [ ] The mechanism confirmed in `PawnGenerator`/faction fallback source, not inferred.
- [ ] Substitution at 0 for Empire and Blackstar kinds in normal play.

---

## ⚠️ CORRECTION 2026-08-27 — "into an authored faction, never" is TOO STRONG

The 2×2 above read `0 of 20` for `Jawa_Hutt_Grunt` → `Jawa_HuttCartel` and I wrote **never**.
My own earlier run in the same session contradicts it: run A measured
`Jawa_Hutt_Grunt` → `Jawa_HuttCartel` at **1 of 5**, and `Jawa_Hutt_Leader` → `Jawa_HuttCartel`
at **1 of 5**. Two of the four substitutions in that run were inside an AUTHORED faction.

**Pooling every measurement of that one combination this session:**

    Jawa_Hutt_Grunt -> Jawa_HuttCartel    1 substituted of 45   ~2%
    any our-kind    -> Empire / Pirate    ~15%

⇒ **The direction of the effect survives and the absolute claim does not.** A vanilla faction
substitutes roughly an order of magnitude more often than an authored one; an authored one is
not immune. ⛔ Do not build on "never".

🔑 **And the mechanism is NOT "the faction does not list the kind", which was my prediction.**
Measured from the capture: `Empire`, `Pirate` and `TribeCivil` **all** carry our kinds in their
combat `pawnGroupMakers` — `Jawa_Empire_Grunt/Heavy/Specialist`, `Jawa_Blackstar_*`,
`Jawa_DeepDesert_*` respectively, each with its leader in `fixedLeaderKinds`. They are wired
and they still substitute at 15%. ⇒ `AUTHORED_KINDS_MUST_FIELD_1`'s wiring is **live-loaded and
correct**, and it is not the fix for this.

**What a real measurement needs:** ≥60 spawns per cell (5 and 20 are far too few for a ~2–15%
rate), and the substituted kind recorded rather than just counted — the one substitute inspected
all session was a vanilla `Colonist`.

---

## ✅ ATTRIBUTED 2026-08-30 (FOUNDRY) — read out of source, not inferred. It is NOT `jawa/spawn_pawn`, and it is NOT vanilla `PawnGenerator` either.

The open criterion was *"attributed to `jawa/spawn_pawn` or to `PawnGenerator`"*, with the
note that **"if it is the engine, it affects raids too"**. Both named suspects are now
excluded, and the answer to the raid question is **yes anyway** — see the last paragraph.

### 1. `jawa/spawn_pawn` has no kind-selection logic at all
Full source read (`JawaBenchTerrainTools.cs`, `SpawnPawn`). It resolves exactly one
`PawnKindDef` by name via `DefDatabase<PawnKindDef>.GetNamedSilentFail`, **fails hard** if
that name does not resolve, and passes that same object into
`PawnGenerator.GeneratePawn(kind, fac)` — one call, unmodified. There is no fallback kind,
no retry with a different kind, no substitution branch anywhere in the method.

⇒ **The tool cannot be choosing a different kind.** What it *was* doing wrong is narrower
and is now fixed (§3).

### 2. Vanilla `PawnGenerator` has no substitution path either
Three facts, each read from 1.6 source via RimSage:

- `TryGenerateNewPawnInternal` (`Verse/PawnGenerator.cs:734`) assigns
  **`pawn.kindDef = request.KindDef;`** as one of the first things it does to a fresh pawn.
- `GenerateNewPawnInternal` (`:682-725`) retries **the same request** up to 120 times and,
  on total failure, logs `"Pawn generation error: … Too many tries (120), returning null"`
  and **returns null**. It never swaps in an easier kind.
- The one path that reuses an *existing* pawn — `GenerateOrRedressPawnInternal`'s world-pawn
  redress — ends in `RedressPawn`, which calls **`pawn.ChangeKind(request.KindDef)`**
  (`Verse/Pawn.cs:6094`, unconditional) and then `GenerateGearFor(pawn, request)`.

⇒ **There is no vanilla code that answers a request for kind A with a pawn whose `kindDef`
is B.** Vanilla either gives you the kind you asked for, or gives you nothing and says so in
the log. ⛔ So the earlier working theory — *"a faction-side fallback to `basicMemberKind`"* —
is dead: no such fallback exists on this path.

⚠️ **The redress path was the best-looking candidate and it does not fit.** Its probability
formula `ChanceToRedressAnyWorldPawn = min(0.02 + 0.001 × freeWorldPawns, 0.8)` matches this
item's measured **2%–15% band almost exactly**, and `IsValidCandidateToRedress` rejects any
world pawn whose `pawn.Faction != request.Faction`, which is the right *shape* for a
faction-dependent rate. It is still ruled out on two independent counts: the redressed pawn
is force-renamed to the requested kind, and it is **re-geared** — where every substituted
pawn measured in this item was **bare**. Recorded because the numeric coincidence is close
enough to mislead the next reader.

### 3. What was actually broken in the tool — fixed this pass
`jawa/spawn_pawn` **never read `pawn.kindDef` back**. Its per-pawn rows carried `id`, `name`,
`faction`, `xenotype` — and no kind at all — while its `message` printed the **requested**
`kind.defName`. That is why it reported `Spawned 5/5 <requested kind>` over a substituted
pawn: not a wrong claim it computed, a claim it never checked.

Fixed: each row now carries `kindRequested` / `kindActual` / `kindSubstituted`, a mismatch
forces `ok:false` (so it stops counting toward `spawnedCount`), and the response carries
`substitutedCount` plus a message naming what a mismatch means. Compiles clean
(`build.py --gm`: bundle ships only `JawaBench.BridgeTools.dll`, zero tool removals).
⚠️ **Built, NOT deployed** — the running game holds the companion DLL open; deploy at the
next game-down window with `python.exe src/RimMandrake/bridgetools/build.py --gm --apply`.

### 4. Where the substitution must therefore live, and why it reaches raids
Since neither the tool nor the engine can do it, it is a **Harmony patch on the pawn-
generation path**. The live game's own patch dump (harvested from `Player.log` this session,
585 mods) names every candidate with the right signature — only a by-ref parameter can do
this:

| patch | hook | why it qualifies |
|---|---|---|
| `AlienRace.HarmonyPatches:GeneratePawnPrefix(PawnGenerationRequest& request)` | `GeneratePawn` | **by-ref request** — can rewrite `KindDef` before line 734 |
| `AlienRace.HarmonyPatches:TryGenerateNewPawnInternalPrefix(PawnGenerationRequest& request)` | `TryGenerateNewPawnInternal` | same, one level deeper |
| `FactionLoadout.Patches.PawnGenPatchIdeo:Prefix(PawnGenerationRequest& request)` | `GenerateNewPawnInternal` | same; `co.uk.epicguru.factionloadout` is **active** in the 590-entry list |
| `EBSGFramework.HarmonyPatches:TryGenerateNewPawnInternalPostfix(Pawn& __result)` | `TryGenerateNewPawnInternal` | **by-ref result** — can replace the whole pawn |
| `BigAndSmall.GeneratePawns_Patch:GeneratePawnPostfix(Pawn& __result, …)` | `GeneratePawn` | same (`redmattis.betterprerequisites`, active) |

Every other pawn-gen patch in the dump takes `PawnGenerationRequest` or `Pawn __result`
**by value** and is therefore incapable of causing this, whatever else it does.

🔴 **All five sit on `GeneratePawn` / `GenerateNewPawnInternal` / `TryGenerateNewPawnInternal`
— the paths a raid uses.** So the original question resolves: the substitution is **not** a
bridge artifact, it is on the universal generation path, and **a raid can deliver a bare
vanilla `Colonist` in place of one of our kinds exactly as this tool did.** ⛔ What is *not*
established is which of the five, and no amount of source reading settles that — it needs a
live mod-disable bisect with the fixed tool reading `kindActual` back.

## criteria
- [x] Kind read back compared against kind requested.
- [ ] ~~Attributed: the faction, not the kind and not `requiredWorkTags`.~~ 🔴 **RETRACTED
      2026-08-30** — at 240 spawns per cell the vanilla-faction cell reads 0.83% and the
      authored-faction cell 0.42%. No detectable faction effect; the 15%-vs-2% split rested
      on 3-of-20 cells measured by a census diff that could count map-resident pawns.
- [x] **Attributed to neither `jawa/spawn_pawn` nor vanilla `PawnGenerator`** — both
      excluded from source. It is a third-party Harmony patch, shortlisted to five by
      signature, and it is on the raid path. (Unaffected by the retraction above: read from
      source, not from the rates.)
- [x] The tool reports the substitution instead of counting it as the requested kind —
      `kindActual` / `kindSubstituted` / `substitutedCount`, **deployed and proven live on
      480 spawns**, substitute recorded as vanilla `Colonist`.
- [ ] **Which of the five patches** — needs a live mod-disable bisect with a game restart
      per candidate. Size it off the real ~0.8% rate: on the order of a thousand spawns per
      cell, not a few dozen.
- [ ] Substitution at 0 for Empire and Blackstar kinds in normal play.
