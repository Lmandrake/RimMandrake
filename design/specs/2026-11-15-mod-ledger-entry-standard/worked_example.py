#!/usr/bin/env python3
"""Measurement for design/specs/2026-11-15-mod-ledger-entry-standard.md §5 (throwaway; NOT the lint).

Mines ten real Gimme Some Slack tickets into mod-ledger events under the entry standard, appends them through the real
`modledger.append` into a temporary root (BACKFILL writer, views off), checks each against the standard's caps with a
prototype checker, feeds the checker five deliberately bad entries to watch it refuse, and prints bytes before/after.

    python3 design/specs/2026-11-15-mod-ledger-entry-standard/worked_example.py
"""
import glob
import json
import os
import re
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import modledger  # noqa: E402

MOD = "GimmeSomeSlack"
LIVE = "proof_all.py --live --no-shots (SteveDesktop testq, tier gimmesomeslack)"
LANE1 = "design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane1/run_lane1.py"
FAULTS = "path:design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/faults.json"
FIXES = "path:design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/fixes.jsonl"
GPT = "ext:Transient/flowworks_takeover_20261023/GPT_REVIEW.md"
STEVE = "ext:D:\\ClaudeWork\\rimmandrake\\conductor\\carryover_20261112\\gss\\steve\\gss_after.json"

TICKETS = [
    "RIMMANDRAKE_UNBEND_GSS_LEAD_AT_JUNCTION_BATTERY_TWICE", "RIMMANDRAKE_TRACE_GSS_ILLEGAL_PATH_ONLY_ON_FIRST_START",
    "RIMMANDRAKE_BUILD_GSS_FLOOR_END_SHOCK_ANSWERED_WEEK_AGO", "RIMMANDRAKE_LIFT_GSS_FALLEN_WIRE_OFF_WALL_CORNER",
    "GSS_POWER_THEFT_FIX_WRONG_VICTIM", "GSS_MULTILINK_FIX_PIPE_POLE_RANGE", "GSS_DETERMINISM_FIX_IGNORES_STALE_PIECES",
    "GSS_COLOUR_SEED_FIX_HIDDEN_CONDUIT_SPLIT", "RIMMANDRAKE_UNBEND_GSS_RANDOM_BASES_SEVEN_SCENES_HID_IT",
    "RIMMANDRAKE_UNGATE_GSS_DROPPED_CORDS_FROM_OVERHEAD_MASTER",
]


def item(i):
    return "item:" + TICKETS[i]


# (kind, subject, body, evidence, extra) — one fact per entry. `kind` names marked NEW are kinds the standard adds;
# the run maps them onto today's modledger kinds (MAP) so the real append accepts them, and counts them as written.
E = [
    # 0 UNBEND_LEAD (open)
    ("finding.open", "finding:" + TICKETS[0], {
        "class": "problem", "bars": ["no_unforced_sharp_turn"], "tags": ["code"],
        "text": "One unforced bend on the core site, same in 3 runs: piece junction:163,153|battery:153,153 at "
                "(156.63,152.78), turn 235.6 deg over 2.3 cells, 6.2 from an end. Planner kink or audit misnaming a "
                "loop: undecided.",
        "proposed_fix": "Dump the strand's points (bends probe rows, or rect:150,148,16,10) and plot; if CordPlanner "
                        "kinks the lead fix the planner, else add the case to CordShapeAudit's LabWorld selftest.",
        "accept": LIVE + ": M2c_no_sharp_bends PASS, unforced 0, that piece absent from `where`"},
     [item(0), STEVE + "#M2c_no_sharp_bends", "sha:4ff9d1df8b", "run:J20261113T075443Z-3da526"], {}),
    # 1 TRACE_ILLEGAL_PATH (open): two facts -> a finding and a trap
    ("finding.open", "finding:" + TICKETS[1], {
        "class": "problem", "bars": ["statics_clear_between_games"], "tags": ["code"],
        "text": "1 of 3 starts (the first after a companion swap): ArgumentException 'Illegal characters in path' in "
                "Path.Combine from ContentFinder.TryFindAssetInModBundles, charged to GSS; the GSS frame was cut off.",
        "proposed_fix": "On the next occurrence read the kept GSS frames (gssFrames on Z, '@ at' on L2) and fix the "
                        "caller; candidates CordMaterials.Tex, GimmeSomeSlackMod.DrawSwatch, ConduitVisuals.",
        "accept": "none, the failing call is not named yet (intermittent); then a selftest feeding it the bad path"},
     [item(1), "sha:4ff9d1df8b", "run:J20261113T075443Z-3da526"], {}),
    ("trap.noted", "trap:z-log-budget-charges-stackless-errors", {  # NEW kind
        "tags": ["instrument"],
        "text": "Z_log_budget charges an error with no stack to the mod by design: 'DrawGUITexture: texture is null' "
                "(run 2, thrower ?) is not evidence against GSS; DrawSwatch already skips a null texture.",
        "where": "src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py#Z_log_budget"},
     [item(1)], {}),
    # 2 BUILD_FLOOR_END_SHOCK (open, built offline, live UNRUN)
    ("question.answer", "q:shock-reach", {
        "said": "Every sparking end shocks, but settable in settings to those three options: None, only downed lines, "
                "or all.",
        "text": "Settles floor_end_shocks_crossers and shock_reach_setting; default All (agent detail on the sheet)."},
     [item(2), "ledger:OWNER:1793996551266756043"], {"authority": {"owner_said": "see said; OWNER tsn "
                                                                  "1793996551266756043, 2026-11-06"}}),
    ("test.run", "bar:shock_reach_setting", {
        "result": "PASS", "bar": "shock_reach_setting", "command": "T_CORE ShockRuleChecks; "
        "src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_proof_leaves.py", "counts": "4508/4508",
        "text": "ShockRule.cs + FloorEndShock.cs; red on the old rule, green after; OWED emptied."},
     [item(2), "sha:46e9a3ed97", "sha:63ac285403"], {"code_sha": "46e9a3ed97"}),
    ("live.run", "bar:floor_end_shocks_crossers", {
        "result": "UNRUN", "bar": "floor_end_shocks_crossers", "command": LIVE + ", rows SC_floor_end_*, "
        "SC_shock_reach_*", "text": "10 rows written; 2 UNMEASURED by design (fixer blueprint order, FlowWorks deck "
        "cord per value)."},
     [item(2)], {}),
    # 3 LIFT_FALLEN_WIRE (open, polish)
    ("finding.open", "finding:" + TICKETS[3], {
        "class": "polish", "bars": ["fallen_span_on_ground"], "tags": ["code"],
        "text": "1 of 1500 lays (seed 97531 trial 117, base (8,31) toward (2.53,30.91)): a grounded point 0.044 cell "
                "inside wall cell (6,31) and the lay not Blocked; LayFallen's contract stops the wire at the first "
                "unwalkable cell.",
        "proposed_fix": "Test the bends of the ground path against walls at sub-cell steps, not only the bare line.",
        "accept": LANE1 + ": row L1_FALLEN_LAY_GROUND PASS (red on 67ddc758e5)"},
     [item(3), FAULTS], {}),
    # 4 POWER_THEFT (open: built twice, live row owed)
    ("finding.open", "finding:" + TICKETS[4], {
        "class": "problem", "bars": ["tap_steals_and_costs_goodwill"], "tags": ["code"],
        "text": "CompPowerTap sums sinceEventWd across victims and raises it against the current one: a clamp that "
                "drains faction A, then switches to B before the 250-tick event, charges A's theft to B.",
        "proposed_fix": "Keep the drained energy and ticks per victim faction within the event window and raise one "
                        "event per faction (CompPowerTap.cs:148-158, PowerTheftConsequences.OnDrained).",
        "accept": "selftest: drain A, switch to B before the event; A charged only A's energy, B only B's (L0); "
                  "one live row (L2)"},
     [item(4), GPT + "#FB_hose_gss_2.5"], {}),
    ("finding.claimed_fixed", "finding:" + TICKETS[4], {
        "text": "Fixed in the GSS DLL; the first built sha 101e561a6e06 no longer resolves (rewritten at landing).",
        "test": "live proof file infrastructure/state/live_proofs/GSS_POWER_THEFT_FIX_WRONG_VICTIM.txt (L2, UNRUN)"},
     [item(4), "sha:c29007b6b66e"], {"code_sha": "c29007b6b66e"}),
    ("trap.noted", "trap:built-sha-rewritten-at-landing", {
        "tags": ["instrument"],
        "text": "A sha cited before ./publish can vanish (rebased at landing): cite only the sha PUBLISHED prints; "
                "101e561a6e06 for the theft fix is dead, c29007b6b66e is the live one.",
        "where": "./publish"},
     [item(4)], {}),
    # 5 MULTILINK (closed: no defect by reading, later guarded)
    ("finding.open", "finding:" + TICKETS[5], {
        "class": "problem", "bars": ["pipe_pole_switch"], "tags": ["code", "instrument"],
        "text": "cmultilink :plan used the power range (20) for pipe poles (12): two pipe poles 16 apart got a planned "
                "pair the real gizmo refuses.",
        "proposed_fix": "Make the probe's :plan branch group by kind and use AerialLineProfiles.RangeFor, as the "
                        "gizmo does.",
        "accept": "none at filing; later the source-shape guard selftest_gss_weakclose_guards.py"},
     [item(5), GPT + "#FB_hose_gss_2.6"], {}),
    ("finding.withdrawn", "finding:" + TICKETS[5], {  # NEW kind
        "how_checked": "reading",
        "text": "No defect at a47aef70c7: :plan and the gizmo both call CompAerialAnchor.AutoLinkPairs (groups by "
                "kind, RangeFor). Weak: no test, no repro; reopen on recurrence, never re-file. Guard added b24ec8298803.",
    }, [item(5), "sha:a47aef70c7", "sha:b24ec8298803"], {"code_sha": "a47aef70c7"}),
    # 6 DETERMINISM (closed by a fix)
    ("finding.open", "finding:" + TICKETS[6], {
        "class": "problem", "bars": [], "tags": ["instrument"],
        "text": "DeterminismChecks.Compare walks fresh keys only and skips EndA==null pieces: a stale incremental-only "
                "cord, or a pile/node difference, reads as zero differences and the scene passes.",
        "proposed_fix": "Also walk the incremental build's keys (count surplus pieces) and stop excluding EndA==null.",
        "accept": "a negative control that plants a surplus incremental piece and must FAIL"},
     [item(6), GPT + "#FE_cs_selftests_4.1"], {}),
    ("finding.claimed_fixed", "finding:" + TICKETS[6], {
        "text": "Compare now checks incremental-only and non-cord pieces; negative control added.",
        "test": "GSS SelfTest 773/773"},
     [item(6), "sha:bf3fa018509b"], {"code_sha": "bf3fa018509b"}),
    # 7 COLOUR_SEED (closed: no defect by reading, later a mutation-checked test)
    ("finding.open", "finding:" + TICKETS[7], {
        "class": "problem", "bars": ["four_looks_one_run"], "tags": ["code"],
        "text": "ComputeNetSeeds unions only laid-piece endpoints, so one net joined through hidden or buried conduit "
                "could get two colour seeds (two colours).",
        "proposed_fix": "Union hidden links into the seed computation (Graph.HiddenLinks) and count nets from that.",
        "accept": "a selftest: two exposed runs joined by hidden conduit share one seed"},
     [item(7), GPT + "#FB_hose_gss_3.5"], {}),
    ("finding.withdrawn", "finding:" + TICKETS[7], {
        "how_checked": "reading+test",
        "text": "No defect at a47aef70c7: ComputeNetSeeds already passes Graph.HiddenLinks to RebuildTail.NetSeeds. "
                "Upgraded from a reading: HiddenConduitSeedChecks, mutation-checked."},
     [item(7), "sha:a47aef70c7", "sha:b24ec8298803"], {"code_sha": "a47aef70c7"}),
    # 8 RANDOM_BASES (closed: fixed, verified)
    ("finding.open", "finding:" + TICKETS[8], {
        "class": "problem", "bars": ["no_unforced_sharp_turn"], "tags": ["code", "test"],
        "text": "CordShapeAudit.BendTally over 80 random scenes (seeds 6000-6039 open, 6500-6539 walled): 82 unforced "
                "of 1381 bends in 728 strands; first rows are one-cell junction-to-device leads hooked at the plug.",
        "proposed_fix": "Add random scenes to the geometry check (lane-1 scene maker), then fix the planner where the "
                        "unforced rows point, starting with plug-end hooks on one-cell leads.",
        "accept": LANE1 + ": rows L1_CORD_BENDS_TALLY and L1_CORD_SHARP_TURN PASS (red on 67ddc758e5, unforced 82)"},
     [item(8), FAULTS], {}),
    ("trap.noted", "trap:geometry-check-reads-seven-oracle-scenes", {
        "tags": ["test", "instrument"],
        "text": "T_CORD_GEOMETRY_OFFLINE was green (4513/4513) while 82 bends were unforced: it read only the 7 oracle "
                "scenes. A green geometry check proves nothing about random sites.",
        "where": "T_CORD_GEOMETRY_OFFLINE"},
     [item(8)], {}),
    ("finding.claimed_fixed", "finding:" + TICKETS[8], {
        "text": "Unforced 82 -> 0 on the judge's 80 scenes. Causes: cut-lead ends kept the old hook and were never "
                "faired; Unbend could not reach hooks in pins; HopWhole refused turns past half a turn; bundles never "
                "hopped.",
        "test": "run_lane1.py --only L1_CORD_BENDS_TALLY rc 0 (rc 1 at 7a9444f717)"},
     [item(8), "sha:6f8bfb47c4", FIXES], {"code_sha": "6f8bfb47c4"}),
    ("finding.verified", "finding:" + TICKETS[8], {
        "text": "Verified by its acceptance rows; red-first record in fixes.jsonl."},
     [item(8), "sha:6f8bfb47c4"], {"code_sha": "6f8bfb47c4"}),
    # 9 UNGATE_DROPPED_CORDS (closed: fixed red-first, live scene UNRUN)
    ("finding.open", "finding:" + TICKETS[9], {
        "class": "problem", "bars": ["shock_reach_setting", "settings_switch_cleanly"], "tags": ["code", "settings",
                                                                                              "other-mod"],
        "text": "With the overhead-lines master off, a FlowWorks dropped deck cord neither shocked nor lit fuel, "
                "whatever shockReach said: RebuildContacts and CheckPawns returned on !AerialSettings.enabled.",
        "proposed_fix": "Gate only the aerial-strand loop of RebuildContacts on the master; let ExternalContacts run; "
                        "in CheckPawns skip only DownedSpan contacts while the master is off.",
        "accept": "src/RimMandrake/GimmeSomeSlack/selftest_gss_dropped_cords_ignore_aerial_master.py exit 0 (6 rows)"},
     [item(9), FAULTS, "sha:67ddc758e5"], {}),
    ("finding.claimed_fixed", "finding:" + TICKETS[9], {
        "text": "Fixed as proposed; red rc 1 on the parent, green rc 0; planted PF_GAME_DROPPED_CORD_MASTER_GATE caught.",
        "test": "selftest_gss_dropped_cords_ignore_aerial_master.py rc 0"},
     [item(9), "sha:6d2aeb9c3f", FIXES], {"code_sha": "6d2aeb9c3f"}),
    ("live.run", "bar:shock_reach_setting", {
        "result": "UNRUN", "bar": "shock_reach_setting", "command": LIVE + ", scene sc_shock_reach (Stage 6)",
        "text": "Game-side half of the dropped-cord fix; no offline test reaches it."},
     [item(9)], {}),
]

# Today's modledger has no trap.* or finding.withdrawn; map them so the real append takes them (§6 owes the kinds).
MAP = {"trap.noted": "note", "finding.withdrawn": "note"}

# The standard's caps (§2 and the rule sheet).
CAP = {"text": 320, "proposed_fix": 320, "accept": 240, "said": 600, "command": 240, "test": 240, "where": 160}
LINE_CAP = 1536
EVIDENCE_MAX, EVIDENCE_REF = 6, 160
REF = re.compile(r"^(sha|path|ext|item|ledger|run|test|card):\S")
STACK = re.compile(r"(\n|```|^\s*at [\w.`<>\[\]]+\(|\bat [A-Z][\w.`]+\.[\w`<>]+\()", re.M)
NARRATION = re.compile(r"^(I |We |Now |Started|Starting|Began|Beginning|Working on|Looking at|Continuing|Next I)")
REQUIRED = {
    "finding.open": ("class", "bars", "text", "proposed_fix", "accept"),
    "finding.claimed_fixed": ("text", "test"),
    "finding.verified": ("text",),
    "finding.withdrawn": ("text", "how_checked"),
    "trap.noted": ("text", "where"),
    "question.answer": ("said",),
    "test.run": ("result", "command"),
    "live.run": ("result", "command"),
}


def check(kind, body, evidence, extra):
    """-> list of refusals, each 'field: what, smallest fix'. Empty = passes the standard."""
    out = []
    for f in REQUIRED.get(kind, ("text",)):
        if f not in body:
            out.append("%s: required for %s; add it" % (f, kind))
    for f, cap in CAP.items():
        v = body.get(f)
        if isinstance(v, str):
            if len(v) > cap:
                out.append("%s: %d chars > %d; one fact per entry: split it, or cite the detail by reference"
                           % (f, len(v), cap))
            if f != "said" and STACK.search(v):
                out.append("%s: pasted log, code or several lines; cite it (path:, run:, test:) instead" % f)
            if f == "text" and NARRATION.match(v):
                out.append("text: narration ('%s...'); state the fact, not what you did" % v[:12])
    if kind.endswith((".claimed_fixed", ".verified", ".withdrawn", ".refuted")) and not extra.get("code_sha"):
        out.append("code_sha: required (the sha ./publish printed)")
    if not evidence:
        out.append("evidence: at least one reference")
    if len(evidence) > EVIDENCE_MAX:
        out.append("evidence: %d refs > %d" % (len(evidence), EVIDENCE_MAX))
    for r in evidence:
        if not REF.match(r) or len(r) > EVIDENCE_REF:
            out.append("evidence %r: a typed reference (sha:/path:/ext:/item:/ledger:/run:/test:/card:) <= %d chars"
                       % (r[:40], EVIDENCE_REF))
    return out


BAD = [
    ("note", "finding:x", {"text": "Started looking at the bend again; nothing new yet."}, ["item:X"], {}),
    ("finding.open", "finding:y", {"class": "problem", "bars": [], "text": "Crash:\n   at Verse.ContentFinder`1."
                                   "TryFindAssetInModBundles(String path)", "proposed_fix": "fix it",
                                   "accept": "none, unknown"}, ["item:Y"], {}),
    ("finding.open", "finding:z", {"class": "problem", "bars": [], "text": "x" * 700, "proposed_fix": "y" * 40,
                                   "accept": "none, unknown"}, ["item:Z"], {}),
    ("finding.claimed_fixed", "finding:w", {"text": "Fixed.", "test": "selftest rc 0"}, ["item:W"], {}),
    ("finding.open", "finding:v", {"class": "problem", "bars": [], "text": "Bend.", "accept": "none, x"},
     ["see the log"], {}),
]


def before_bytes():
    prose = 0
    for t in TICKETS:
        p = os.path.join(REPO, "infrastructure/state/items/%s.md" % t)
        if not os.path.exists(p):
            p = os.path.join(REPO, "infrastructure/state/items/closed/%s.md" % t)
        prose += os.path.getsize(p)
    ev = 0
    for f in glob.glob(os.path.join(REPO, "infrastructure/state/ledger/events/*.jsonl")):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                try:
                    if json.loads(line).get("id") in TICKETS:
                        ev += len(line.encode("utf-8"))
                except ValueError:
                    pass
    return prose, ev


def main():
    fails = 0
    for kind, subj, body, evidence, extra in E:
        why = check(kind, body, evidence, extra)
        if why:
            fails += 1
            print("STANDARD REFUSES good entry %s %s: %s" % (kind, subj, why))
    caught = sum(1 for b in BAD if check(*[b[0], b[2], b[3], b[4]]))
    print("planted bad entries refused: %d of %d" % (caught, len(BAD)))
    for b in BAD:
        print("  %-22s -> %s" % (b[0], "; ".join(check(b[0], b[2], b[3], b[4]))[:150]))
    root = tempfile.mkdtemp(prefix="mlstd-")
    os.environ.pop("RM_MODLEDGER_WRITER", None)
    for kind, subj, body, evidence, extra in E:
        b = dict(body)
        if kind in MAP:
            b["std_kind"] = kind
        modledger.append(root, MOD, "BACKFILL", MAP.get(kind, kind), subj, body=b, version="0.1.0",
                         evidence=evidence, code_sha=extra.get("code_sha"), authority=extra.get("authority"),
                         views=False)
    shard = modledger.shard_path(root, MOD, "BACKFILL")
    with open(shard, "rb") as fh:
        lines = fh.read().splitlines()
    after = sum(len(l) + 1 for l in lines)
    biggest = max(len(l) + 1 for l in lines)
    spilled = os.path.isdir(os.path.join(modledger.ledger_dir(root, MOD), "text"))
    prose, ev = before_bytes()
    print("before: ticket prose %d + rimflow events %d = %d bytes (~%d tokens)" % (prose, ev, prose + ev,
                                                                                (prose + ev) // 4))
    print("after: %d events, %d bytes (~%d tokens), largest line %d bytes (cap %d), spilled %s"
          % (len(lines), after, after // 4, biggest, LINE_CAP, spilled))
    evs = [json.loads(l) for l in lines]
    body = sum(len(json.dumps(e["body"], separators=(",", ":"), ensure_ascii=False).encode("utf-8")) for e in evs)
    evid = sum(len(json.dumps(e["evidence"], separators=(",", ":"), ensure_ascii=False).encode("utf-8")) for e in evs)
    print("after split: body %d, evidence %d, envelope (id, key, ts, writer, kind, subject...) %d"
          % (body, evid, after - body - evid))
    print("good entries the standard refused: %d" % fails)
    return 1 if fails or biggest > LINE_CAP or caught != len(BAD) else 0


if __name__ == "__main__":
    sys.exit(main())
