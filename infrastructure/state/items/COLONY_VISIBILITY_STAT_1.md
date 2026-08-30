## spec
Design pass (per F18/F12, `design/Jawa/salvation_engine_review.md`, and the
item's own brief) is DONE and offline: `design/Jawa/worldbuilding/colony_visibility_stat.md`,
linked from `design/Jawa/divine_satiation_engine.md` under the Matrix status
line. Nothing invented — every raise/lower hook cites an existing DEED,
BOON, DEMAND or CURSE already SHIPPED on a matrix page (Ishko, Ozzik, Ohm,
Sh'kaar, Ta'Baa); no new god behavior.

**The stat:** 0–100, five-band ladder (Hidden/Discreet/Noticed/Marked/
Exposed), tracked as a GameComponent (not MapComponent — the gravship's own
map persists across launches, so a MapComponent would never naturally
reset). Visible from campaign start, unlike the veiled nine (F4) — the
*number* needs to be legible from day one; only the per-god *attribution*
unlocks progressively as each god manifests.

**F12 (replace, don't stack):** read `StorytellerUtility.DefaultThreatPointsNow`
from RimWorld source via RimSage (`Source/RimWorld/StorytellerUtility.cs:131-189`)
rather than guessed — it sums a wealth term (`PointsPerWealthCurve`) and a
per-pawn combat-power term, then applies random/adaptation/threatScale/
days-passed multipliers, clamped to `GlobalPointsMin()`..10000. It is called
from ~45 places (raids, quests, insects, fleshmass, mechhive, ancient-complex
sentries, thrumbo herds…), so patching it globally would silently reshape
systems that have nothing to do with visibility — the doc scopes the
replacement to the actual raid call sites only (`IncidentWorker_RaidEnemy`,
`IncidentWorker_RaidFriendly`, `TimedDetectionRaids`,
`QuestNode_GenerateThreats`) via a Harmony call-site transpiler, replacing
only the wealth term (keeping the pawn-power term — that's "how many
defenders you have," not "wealth" in F12's sense). Sh'kaar's escalation
meter multiplies the *derived raid-points output*, not the displayed 0–100
number, to keep the ladder legible.

**Not written:** the actual Harmony transpiler / `RaidThreatPointsNow`
reimplementation. It requires re-implementing the per-pawn combat-power loop
(the wealth and pawn-power terms are summed inside vanilla's private method
before any multiplier runs, so they can't be un-mixed after the fact) — a
real, self-contained method, not a guess-write. Flagged explicitly as the
deferred fragile-edge build item. An illustrative (not filed/compiled)
GameComponent skeleton for the safe core is in the design doc §5 — no mod
project exists yet for the satiation engine at all, so nothing was written
into `src/`.

## decisions owed (owner/BENCH, not mine to make)
1. Scoped raid-call-site F12 replacement (recommended) vs. the maximal
   "touch `DefaultThreatPointsNow` everywhere" reading.
2. Sh'kaar's meter multiplying the derived points only (recommended) vs.
   multiplying the displayed number too.
3. All S/M/L deltas and the Visibility→raid-points curve anchors — explicitly
   left untuned, deferred to a throwaway-save test rig per the engine doc's
   own §9/§10 convention.
4. Launch-reset floor (illustrative 5–15) and whether a "snatched free with
   enemies boarding" launch resets lower than a routine one.
5. Per-settlement Visibility for a colony that settles (F14) — out of scope
   v1, flagged only.

## Watch out
🔴 **The transpiler is the risky half; do not build it from this item alone
without a fresh read of the design doc's §4** — the wealth/pawn-power split
inside vanilla's method is the part most likely to be mis-copied.

🔑 **This item stays `doing`, not `closed`** — per its own brief and the
CHARTER pattern for other F## items, whether to build the full raid-point
replacement (vs. shipping only the safe-core dial) is the owner's/BENCH's
call, not decided here.
