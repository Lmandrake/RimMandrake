<!-- status: live -->
# Colony Visibility — the shared dial (F18 design, COLONY_VISIBILITY_STAT_1)

_Design pass for `salvation_engine_review.md` F18 ("Colony Visibility as a
first-class, player-facing stat... that *owns* threat-point modulation,
solving F12's double-billing in the same stroke") and F12 ("replace, don't
stack — the mod takes ownership of threat-point modulation into one number
the gods contest"). Pointer target from
`design/Jawa/divine_satiation_engine.md`; do not duplicate the pantheon
mechanics here — this doc only adds the Visibility dial and cites the matrix
pages it draws from. Register: SPEC, not yet built — files as a build item
when the owner calls it (per CHARTER's item-decision pattern; this doc is the
offline design pass COLONY_VISIBILITY_STAT_1 asked for)._

---

## 1. What it is

**Colony Visibility** is a new tracked scalar, **0–100, unsigned**, read by a
**five-band ladder** (mirroring the satiation engine's band-width convention,
`divine_satiation_engine.md` §1):

| Band | Range | Reads to the player as |
|---|---|---|
| **Hidden** | 0–19 | the desert does not know you are here |
| **Discreet** | 20–39 | quiet, a little smoke on the wind |
| **Noticed** | 40–59 | someone is asking after you |
| **Marked** | 60–79 | your name travels ahead of you |
| **Exposed** | 80–100 | everyone who matters knows exactly where you are |

It is **not one of the nine gods' satiation tracks** — it is a *shared*
pressure clock the pantheon's existing mechanics feed, extending the four
pressure-clocks already named in `divine_satiation_engine.md` §2.0d
(Zizzik's slumber, Sh'kaar's escalation, Ta'Baa's rooted-erosion, Ozzik's
pride-meter). It is the one the *player* is meant to watch directly, because
it is also the raid-threat dial (§4).

**Scope: the home map, not every map.** Tracked as a **GameComponent**
field (`shipVisibility`), not a MapComponent — because the gravship's own
map persists across launches (Odyssey gravships relocate the *same* map;
they do not regenerate it), so a MapComponent would never naturally reset,
and because F2 (`salvation_engine_review.md`) already ruled that away-team
maps (caravans, outposts, raid destinations) run *attenuated* — they read a
derived fraction of the ship's number, they do not carry an independent
track of their own. One value now; per-settlement tracks (for a colony that
settles per F14) are an explicit v2 extension, out of scope here.

**Not veiled like the nine (resolves a tension with F4).** F4 rules the nine
gods start veiled and manifest one at a time. Visibility is different: it is
the survival mechanic itself, and the player needs to be managing it from
day one, so **the number and its band are visible from the start.** What
stays veiled, and unlocks god-by-god per F4, is the *attribution* — which
god's hand is on a given swing (see §5, interface). A player who has not yet
met Sh'kaar sees "Marked, rising" before they see "Marked, rising — Sh'kaar
tastes blood" once his manifestation has fired.

---

## 2. What raises it, what lowers it — grounded in the shipped matrix

Every hook below cites an existing DEED, BOON, DEMAND or CURSE already
shipped on a matrix page in `divine_satiation_engine.md` (§"The Matrix", all
nine SHIPPED 2026-08-30). **No new god behavior is invented here** — this
section only routes existing mechanics onto the new dial. Magnitudes follow
the doc's own convention (small/med/large, tunable — "for agent G to tune",
§8b) and are illustrative, not final.

### Raises Visibility

| Source | Matrix citation | Size |
|---|---|---|
| Colony spotted / raided at home | Ishko DEEDS− "spotted/raided at home" | L |
| A challenge broadcast is sent | Ishko DEEDS− "challenge broadcasts" | M |
| A public triumph is broadcast (player-initiated) | Ozzik DEMANDS L "a public triumph BROADCAST" | L |
| **Renown** fires | Ozzik CURSE M "your name spreads unbidden — wealth and position leak... envoys and rivals arrive drawn by a legend you never broadcast" | M, and this curse's own text is literally rewritten to spend on Visibility instead of "raid points calculate higher" directly — **this is F12's named double-billing example, closing itself** |
| **THE SHAMING** fires | Ozzik CURSE L, "the humbling catastrophe... Zizzik and Sh'kaar arrive fed" | L |
| **Overcurrent** fires | Ohm CURSE S, "lights blaze at night — feeding Sh'kaar, galling Ishko" | S |
| Melee fighting | Sh'kaar skill-grid "close, exposed, brutal is his purest war"; also feeds his escalation meter (§3 below) | S, ambient |
| Lighting a flare/lamp in the field | §8b "light a flare/lamp in the field → ▲Sh'kaar + ↓Ishko" | S, ambient |

### Lowers Visibility

| Source | Matrix citation | Size |
|---|---|---|
| Ambush/from-cover kills | Ishko DEEDS+ | S, ambient |
| A raid survived undetected / enemies leave without finding the colony | Ishko DEEDS+ | M |
| Concealed / under-mountain construction | Ishko DEEDS+ | S |
| Operating in darkness | Ishko DEEDS+ | S, ambient |
| **Blackout reign** held (the literal F18 "blackout") | Ishko DEMANDS L, "no outdoor light, no comms" | L, deliberate — and costly: no comms also blocks trade/quest contact while active, a real trade-off, not a free lever |
| **Orange Dusk** boon active | Ishko BOON S, "exterior lights dim, small detection-clock slow" | S — this boon's "detection clock" language is the pre-F18 placeholder for exactly this stat; reread as a temporary Visibility decay-rate bonus |
| **The Long Shadow** boon active | Ishko BOON M, "detection clock pauses at night" | Visibility does not rise at night while banked |
| **Unseen Berth** fires | Ishko BOON L, "one detection-clock reset, or one guaranteed raid-free stretch" | large one-time drop |
| The Unburdening rite (F13's potlatch, once specced) | Ozzik DEEDS− "humility — wealth given away, trophies melted, staying small, declining glory" | M–L, and gives F13's Unburdening a second, more legible payoff beyond venting the pride-meter |

### Multiplies it, does not add to it — Sh'kaar's escalation meter

F18's own wording is "Sh'kaar's meter multiplies it," distinct from every
other hook above, which is additive. Read literally against Sh'kaar's
shipped page (§3⑧/§8⑧-reframe, the battle-escalation meter — every violent
battle wakes him hungrier, cooling only through stillness or the
prisoner-death-match lever): the meter should **multiply the raid-points
output derived from Visibility, not the displayed 0–100 number itself.**

Reasoning: if the escalation meter swung the *displayed* band, the ladder
would jitter with combat tempo and stop being legible (a colony deep in a
justified defensive war would flicker between Marked and Exposed every
fight, defeating the "read the ship the way a sailor reads the sky" goal
F8 already set for Mood). Keeping the display clean and applying Sh'kaar's
multiplier only to the derived raid-threat number (§4) still delivers what
his own curse text already promises — THE SEARING: "the meter cashes out:
the next raid arrives massive, burning, early" — without corrupting the
player-facing dial. **Flagged as a design decision, not free of debate**;
the alternative (multiply the display too) is recorded here so a future
build item can override it deliberately rather than by drift.

### Resets it — Ta'Baa's launch

Ta'Baa DEEDS+ "LAUNCHING (the holiest; big spike per liftoff)" is the
literal F18 "Ta'Baa's launch resets it." On a successful launch, Visibility
drops to a low floor near the Hidden band (illustrative: 5–15, not 0 — a
ship that just fled somewhere is not *unknown*, it is *unplaced*, and some
residual "someone saw you leave" carries over; exact floor is a tuning
call). This closes Ta'Baa's own curse loop cleanly: **The Burning of the
Root**'s exit-verb is "until something FLIES" — the curse's own remedy is
the same act that resets the dial it fed.

---

## 3. Interface — F17 territory, proposed not built

F17's own ruling took all three options ("reign-calendar, letter rewrite
layer, inspect tags"). Visibility should use all three, consistently:

1. **Reign-calendar line.** The date-line rewrite F17 already specs ("Third
   day of Rekko's reign") gets a Visibility clause appended when the band is
   Marked or worse: *"Third day of Rekko's reign, and the desert has begun
   to ask after you."* Silent at Hidden/Discreet/Noticed — dread is cheap
   when it is rare.
2. **Letters on band-crossing, signed per F9.** Crossing into a worse band
   fires a Narrator letter naming the *proximate* cause where one is known
   (attribution unlocks per-god per F4 — see §1): *"Renown still rings off
   the hull. Something is now Marked that was Noticed this morning."* No
   unsigned crossings (F9's rule, adopted matrix-wide, applies here too).
3. **Inspect tag on the ship/settlement.** Clicking the colony's home
   structure (or a dedicated gizmo) shows the current band name plus, once
   unlocked, whichever god's hand is heaviest on the current value — the
   same "sacred tags visible where the player already looks" F17 asks for
   on salvageable wrecks, applied to the colony itself.

No new UI widget is proposed beyond what F17 already commits to building;
Visibility is additional *content* fed into that layer, not a fourth
interface mechanism.

---

## 4. Replacing vanilla wealth-based raid scaling (F12)

### 4.1 The mechanism being replaced — read from source, not guessed

`RimWorld.StorytellerUtility.DefaultThreatPointsNow(IIncidentTarget target)`
(confirmed via RimSage, `Source/RimWorld/StorytellerUtility.cs:131-189`) is
the actual vanilla raid-sizing function. Condensed:

```
num  = PointsPerWealthCurve.Evaluate(playerWealthForStoryteller)      // the wealth term
num2 = Σ over player pawns of PointsPerColonistByWealthCurve.Evaluate(wealth)
       (+ animal/mech/subhuman terms, health-scaled, slave-discounted)  // the pawn-power term
num4 = (num + num2) * target.IncidentPointsRandomFactorRange.RandomInRange
num5 = Lerp(1, watcherAdaptation.TotalThreatPointsFactor, difficulty.adaptationEffectFactor)
return Clamp(num4 * num5 * difficulty.threatScale
             * storyteller.def.pointsFactorFromDaysPassed.Evaluate(daysPassedSinceSettle),
             GlobalPointsMin(), 10000f)
```

`GlobalPointsMin()` floors at `Rand.RangeSeeded(35, difficulty.MinThreatPointsCeiling, ...)`.

**This single function is called from ~45 places** across raids, quests,
insect/fleshbeast/mechhive threat sizing, ancient-complex sentry counts,
gravcore and relic-hunt quest generation, thrumbo herd sizing, and more
(full list pulled via `search_source`, not estimated). That breadth is the
reason a *global* override is the wrong shape — see 4.3.

### 4.2 Design: replace the wealth term, keep the pawn-power term

Per F12's own framing ("the mod takes ownership of threat-point
modulation") and the anti-exponential pillar the review keeps citing
(`num`, the `PointsPerWealthCurve` term, is exactly the exponential-feeling
scaling the campaign fights): **replace `num` with a Visibility-driven
term; leave `num2` (the per-colonist/mech/animal combat-power sum) alone.**

Rationale for the split: `num2` is not "wealth" in the sense F12 objects
to — it is "how many capable defenders do you have," which vanilla's own
raid-balance depends on to avoid a raid that trivializes or one-shots the
colony regardless of Visibility. Folding it into the replacement too would
mean a heavily-armed, perfectly-hidden colony faces raids sized as if it had
no defenders at all — not "we are hiders," just "combat has no
consequences." Keep it.

Proposed replacement term (illustrative anchors, **not tuned** — tuning is
explicitly deferred to the throwaway-save test rig `divine_satiation_engine.md`
§9/§10 already names for this kind of number):

| Visibility | Replacement factor (vs. `PointsPerWealthCurve`'s role) |
|---|---|
| 0 (Hidden floor) | ~0.3× — near `GlobalPointsMin()`, a genuinely quiet colony draws almost nothing |
| 20 | ~0.6× |
| 40 | ~1.0× — parity anchor, roughly a mid-wealth vanilla colony |
| 60 | ~1.6× |
| 80 | ~2.4× |
| 100 (Exposed) | ~3.5× — deliberately steeper than vanilla's wealth curve at its top end, because Exposed is meant to hurt |

Then, per §2's multiplier design: `finalFactor = visibilityFactor(V) *
shkaarEscalationMultiplier` before feeding into the existing
`num4 * num5 * threatScale * daysPassedFactor` chain, clamped exactly as
vanilla does (`GlobalPointsMin()`..10000).

### 4.3 Where to apply it — scoped, not global

**Do not patch `DefaultThreatPointsNow` itself.** It is shared with systems
that have nothing to do with "does the world know where I am" — insect
infestations, fleshmass/mechhive growth, ancient-complex sentry density,
thrumbo herd size, gravcore/relic-hunt quest difficulty. Patching the shared
function would silently reshape all of those around a stat they were never
designed to read, which is the same "double-billing by accident" failure
mode F12 was filed to kill, just relocated.

**Target the actual raid call sites** instead, via a Harmony **transpiler
call-site swap** (redirect the specific `call
StorytellerUtility.DefaultThreatPointsNow(...)` IL instruction to a new
`ColonyVisibilityEngine.RaidThreatPointsNow(...)` method), applied to:

- `IncidentWorker_RaidEnemy.TryExecuteWorker` — `Source/RimWorld/IncidentWorker_RaidEnemy.cs:88`
- `IncidentWorker_RaidFriendly.TryExecuteWorker` — `Source/RimWorld/IncidentWorker_RaidFriendly.cs:69`
- `Planet/TimedDetectionRaids` — `Source/RimWorld/Planet/TimedDetectionRaids.cs:138` (the detection-raid ×1.5 case — thematically the most on-the-nose one to touch, since it already means "they found you")
- `QuestGen/QuestNode_GenerateThreats` — `Source/RimWorld/QuestGen/QuestNode_GenerateThreats.cs:56`, gates quest-triggered raids the same way

A call-site transpiler is the standard, surgical Harmony technique for
"redirect this one call in this one method" and is why it is preferred here
over a stack-trace-sniffing postfix on the shared function (fragile, and
pays a `StackTrace` cost on every one of the ~45 unrelated callers too).

**Why `RaidThreatPointsNow` cannot simply call vanilla and adjust the
result:** the wealth term (`num`) and pawn-power term (`num2`) are summed
*inside* the private vanilla method before any multiplier is applied — the
returned float has no way to be un-mixed after the fact. `RaidThreatPointsNow`
therefore has to **reimplement the pawn-power loop** (copy `num2`'s logic —
straightforward, it is fully visible via RimSage, ModsConfig/Biotech age
scaling included) and substitute the Visibility term for `num`. This is a
real, self-contained method, not a two-line patch — which is exactly why
this pass specs it precisely but does not write it. **This is the piece
flagged NOT low-risk; it is the deferred build item.**

### 4.4 What is explicitly NOT being touched

Sh'kaar's SEARING, Ozzik's Renown/exposure bias, and Ishko's
detection-clock boons stop independently touching raid math (F12's
double-billing) — their effects now route through Visibility (§2) instead.
Everything else that calls `DefaultThreatPointsNow` — insects, fleshmass,
mechhive, ancient-complex sentries, thrumbo herds, gravcore/relic-hunt
quests — is **left on vanilla wealth scaling**, deliberately, because none
of those are "does the world know where you are" questions. If the owner
wants the maximal reading of F12 ("the mod takes ownership of threat-point
modulation" everywhere), that is a strict superset of this scope and should
be a separate, explicitly-called decision, not a default.

---

## 5. Implementation shape

**Safe core (build first, matches the engine's own §9 safe/fragile split):**
the GameComponent field, its `ExposeData` persistence, the additive
raise/lower hooks (§2, all pure state + narration), the band ladder, and the
interface layer (§3, pure read/narrate). None of this touches live raid
generation and can ship, be played, and be tuned entirely on its own —
exactly like the rest of the satiation engine's safe core.

**Fragile edge (build second, and the one piece not drafted here):** the §4
transpiler and `RaidThreatPointsNow` reimplementation. Everything in §4 is
specced precisely enough to execute directly; none of it is written, per
the item's own instruction not to guess-write a raid-point Harmony patch
blind.

**Illustrative skeleton — not filed as a build artifact.** No mod project
exists yet for the satiation engine at all (confirmed: no C# under
`src/RimMandrake/` references any of the nine gods or satiation; the matrix
"files when the owner calls the build," `divine_satiation_engine.md` last
line). Writing a loose `.cs` file with no `About.xml`/`.csproj` home (the
pattern every other local mod here follows, e.g.
`src/RimMandrake/JawaRules/{About,Source}/`) would be scaffolding nobody can
build or deploy yet. The shape below is illustrative for whichever mod the
engine build lands in:

```csharp
// Illustrative only — wire into the satiation-engine mod's Source/ once that
// project exists (name TBD, §8b: "Ninefold" / "The Front" / "Dispensations").
public class GameComponent_ColonyVisibility : GameComponent
{
    public float shipVisibility = 10f; // Hidden-band start

    public GameComponent_ColonyVisibility(Game game) { }

    public override void ExposeData()
    {
        Scribe_Values.Look(ref shipVisibility, "shipVisibility", 10f);
    }

    public VisibilityBand Band => BandFor(shipVisibility);

    // Called from the existing deed/boon/curse hooks (§8b-style event audit)
    // with the matrix citation as the reason string, for the F9-signed letter.
    public void Adjust(float delta, string godReason)
    {
        shipVisibility = Mathf.Clamp(shipVisibility + delta, 0f, 100f);
        // fire band-crossing letter if Band changed — see §3.2
    }

    // Called from the Ta'Baa launch hook (§2, "Resets it").
    public void ResetOnLaunch()
    {
        shipVisibility = Mathf.Clamp(shipVisibility * 0.15f, 5f, 15f);
    }
}

public enum VisibilityBand { Hidden, Discreet, Noticed, Marked, Exposed }
```

This is a genuinely low-risk skeleton (a tracked field, a getter, two
mutators, no live-game side effects) offered as a starting point; it is not
built or deployed, and it changes nothing until a build item creates the
actual mod project around it.

---

## 6. Open questions for the owner / a future build item

1. **Scope of the F12 replacement** — the scoped raid-call-site patch (§4.3)
   vs. the maximal "touch `DefaultThreatPointsNow` everywhere" reading.
   Recommendation: scoped. Needs a ruling before the fragile edge is built.
2. **Sh'kaar-multiplies-the-display vs. multiplies-the-derived-points-only**
   (§2) — recommendation: derived-points-only, for ladder legibility.
3. **Exact tuning** of every S/M/L delta and the Visibility→factor curve
   anchors in §4.2 — explicitly deferred to a throwaway-save test rig, same
   as the rest of the engine's magnitudes (§9/§10).
4. **Launch-reset floor** (5–15 illustrative) and whether it should vary
   with how the launch happened (a snatched-free-with-enemies-boarding
   launch, Ta'Baa's own maximum-sacred case, might reasonably reset lower
   than a routine one).
5. **Per-settlement Visibility** for a colony that settles (F14) rather
   than staying nomadic — out of scope v1, flagged for whenever multi-site
   play is real.

---

_Pointer: this doc is cited from `design/Jawa/divine_satiation_engine.md`
under the Matrix status line. Edit visibility mechanics here only._

---

## Annex A — the threat-point choke point, VERIFIED against source (BENCH merge, 2026-08-30)

_Merged from a parallel BENCH pass the same day (its duplicate file deleted; this
doc stays the one of record). Everything below marked VERIFIED was read out of
the decompiled 1.6 source via rimsage this sitting, not remembered:_

## 3. Threat-point modulation — the mechanism (replace, don't stack)

**VERIFIED (read 2026-08-30, `Source/RimWorld/StorytellerUtility.cs:131`):**
`StorytellerUtility.DefaultThreatPointsNow(IIncidentTarget)` is the single
choke point. Formula as shipped: wealth → `PointsPerWealthCurve`; + per-pawn
points (colonists by wealth curve; release-trained animals 0.08×combatPower;
colony mechs & subhumans by curve; ×health lerp 0.65; slaves ×0.75; Biotech
age curve); × `IncidentPointsRandomFactorRange`; × adaptation
(`Find.StoryWatcher.watcherAdaptation.TotalThreatPointsFactor` lerped by
`difficulty.adaptationEffectFactor`); × `difficulty.threatScale` ×
`pointsFactorFromDaysPassed`; clamped to `[GlobalPointsMin(), 10000]`.
**VERIFIED callers:** ~50 sites — enemy raids (`IncidentWorker_RaidEnemy:88`),
friendly raids, quest point budgets (slate "points"), site generation, ambient
threats (infestation curves, manhunters via ThreatsGenerator), and even
benign sizing (thrumbo herd count).

**We do NOT rewrite the wealth curves** (that fights every mod and DLC).
Visibility multiplies the output: `points ×= VisibilityToThreatCurve(vis)`,
first-guess curve `0→0.55 · 25→0.80 · 50→1.00 · 75→1.25 · 100→1.60`,
re-clamped to `GlobalPointsMin()` (**VERIFY** its value) so "Unseen" never
breaks the storyteller's floor.

**The scope decision (OPEN-FOR-OWNER, the one real fork):**
- **Option A — global postfix** on `DefaultThreatPointsNow`: one Harmony
  patch, everything coherent — but quest budgets shrink too, and points drive
  quest *rewards* as well as challenge, and thrumbo herds get smaller when
  you hide. A hidden colony is offered smaller stories. Defensible, weird at
  the edges.
- **Option B — threat-scoped (recommended v1):** targeted patches on the
  hostile paths only: `IncidentWorker_RaidEnemy` (**VERIFIED** callsite),
  `ThreatsGenerator` (**VERIFIED**), `TimedDetectionRaids` (**VERIFIED**),
  infestation/manhunter workers (**VERIFY** the full hostile list against the
  caller inventory above). Player-legible: Visibility affects THREATS.
  More patch surface, surgical behavior.
- Adaptation note: vanilla adaptation keeps running underneath either option
  and will partially re-inflate a long-hidden colony's raids; that is
  acceptable (the storyteller resents being cheated — very Zizzik) but must
  be in the tuning measurements, not discovered live.

## 5. Tuning protocol (MEASURED before shipped)

1. Throwaway-save rig on the 22s minimal list; fixed-wealth test colony.
2. **VERIFIED instrument:** the storyteller debug readout prints
   `Base points` (`Storyteller.cs:382`) and `DebugOutputsIncidents` logs
   `DefaultThreatPointsNow` — measure points at Visibility ∈ {0, 25, 50, 75,
   100} × 3 wealth bands, 10 samples each (random factor needs averaging).
3. Acceptance: monotone in Visibility; Unseen ≈ 0.5–0.6× Noticed; Blazing ≈
   1.5–1.7×; adaptation drift over 30 simulated days < 15% of the Visibility
   effect. Publish the table in this doc before the mod ships.

## 6. OPEN-FOR-OWNER

1. §3 scope: global (A) vs threat-only (**B recommended**).
2. Curve endpoints — how safe is perfectly hidden (0.55×?) and how brutal is
   Blazing (1.6×?). These ARE the campaign difficulty knobs.
3. Bands-with-needle vs raw number (recommended: bands + itemized inspect).
4. Do friendly raids / thrumbo passes scale (only relevant under Option A)?
5. Killground designator: name and whether it is Ishko-gated (only usable
   once Ishko has manifested — pairs with F4 discovery).
6. Does Visibility persist per-tile when the ship leaves and returns
   (a remembered tile), or is every landing a clean floor? (Ta'Baa says
   clean; Ishko says the desert remembers. Genuinely his call.)
