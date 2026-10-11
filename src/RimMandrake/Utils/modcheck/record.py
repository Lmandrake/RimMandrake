"""modcheck.record -- record a functional script's LIVE result without swapping ModsConfig.

    python3 -m modcheck.cli record FlowWorks --result <validation_v2_result_*.json> [--tier flowworks]

WHY (debug_process.md section 1 item 4): `modcheck run` swaps the owner's ModsConfig.xml and
records only a mod's own validation.py; `northstar_driver run` never calls record_run. A
functional script that already ran live on a tier the SEAT set up (FlowWorks/northstar/
validation_v2.py) had no sanctioned way into modcheck_status.json. This is that way, and the
only one: it calls `status.record_run`, never writes the registry itself.

It REFUSES (exit 2, nothing written) unless all of these hold -- each is a way a result can
describe something other than the mod as it is now:
  * the result is a LIVE run of this mod's script that did not abort;
  * its `mod_hash` (computed by the script at run start with status.mod_hash) equals the mod's
    hash NOW -- a result older than the last edit is STALE, exactly like a GREEN entry is;
  * its `env.running` (jawa/running_mods, read by the script DURING the run) is the declared
    tier's resolved list as a SET (modset_builder.resolve_tier): a run on the full list, or on
    a list with a forbidden donor, is not this tier's run. Read-only: ModsConfig is never touched.

The verdict is never 'all rows passed, so GREEN'. Per north_star_validation_spec.md section 5:
  * any FAIL / UNMEASURED row          -> RED
  * all rows ok but UNBUILT/UNCOVERED  -> REFUSED, naming every such bar (the stated experience
                                          is not all tested, so the mod is not validated)
  * otherwise                          -> status.verdict_for (DRAFT-CHECKLIST /
                                          PENDING-OWNER-REVIEW / GREEN)
The per-row tally and the environment fingerprint ride along in the entry (`components`,
`source`) so `modcheck status` can show what the verdict was made of.

STEP 4 (FLOWWORKS_CHECKOUT_SCOPE_1). A mod shipping `northstar/extension_proof.py` (status.STEP4_SCRIPT) runs its
feature chains as a separate live run after the core proof; `--extensions <extension_result_*.json>` records it in
the same entry as `step4`, judged like the core result:
  * provenance is refused exactly as above (live, this mod, not aborted/refused, current mod hash, declared tier),
    and a PARTIAL run (`--chains` subset) is refused -- it did not run step 4;
  * any component FAIL / UNMEASURED            -> the checkout is not green (RED), like a FAIL row;
  * no step-4 result supplied                  -> step4 UNMEASURED; a core that is otherwise green is REFUSED,
                                                  naming step 4. Never PASS.
`status.check` and `modcheck floor --all` read `step4` back through status.step4_live.
"""
import json
import os

OK_ROWS = ("PASS", "SKIP", "UNCOVERED", "UNBUILT")


def tally(rows):
    """Per-status id lists, in row order."""
    out = {}
    for r in rows:
        out.setdefault(r.get("status") or "?", []).append(r.get("id"))
    return out


def provenance(res, mod, current_hash, expected_pids):
    """Refusals for a result that may describe something other than `mod` as it is now, on its tier. Pure."""
    refusals = []
    if res.get("mode") != "live":
        refusals.append("not a live run (mode=%r)" % res.get("mode"))
    if res.get("mod") != mod:
        refusals.append("result is for mod %r, not %r" % (res.get("mod"), mod))
    if res.get("aborted"):
        refusals.append("run ABORTED: %s" % res["aborted"])
    rh = res.get("mod_hash")
    if not rh:
        refusals.append("result carries no mod_hash (written before `modcheck record` existed) "
                        "-- rerun the script")
    elif rh != current_hash:
        refusals.append("STALE result: run at mod hash %s, mod is now %s" % (rh[:12], current_hash[:12]))
    running = ((res.get("env") or {}).get("running")) or []
    if not running:
        refusals.append("result carries no env.running (live mod list) -- cannot prove the tier")
    elif expected_pids is None:
        refusals.append("declared tier could not be resolved")
    else:
        got, want = {p.lower() for p in running}, {p.lower() for p in expected_pids}
        if got != want:
            refusals.append("live mod set is not the declared tier: extra %s, missing %s"
                            % (sorted(got - want)[:6], sorted(want - got)[:6]))
    return refusals


def judge(res, mod, current_hash, expected_pids):
    """(refusals, all_green, refused_reason, components). Pure: no file, no registry.
    `expected_pids` None means the tier could not be resolved -- that is a refusal, never a skip."""
    refusals = provenance(res, mod, current_hash, expected_pids)
    rows = res.get("rows") or []
    if not rows:
        refusals.append("result has no rows")
    t = tally(rows)
    bad = [i for st, ids in t.items() if st not in OK_ROWS for i in ids]
    all_green = bool(rows) and not bad and not res.get("aborted")
    open_bars = t.get("UNBUILT", []) + t.get("UNCOVERED", [])
    refused = ""
    if all_green and open_bars:
        refused = "%d live rows PASS but %d bars UNBUILT, %d UNCOVERED: %s" % (
            len(t.get("PASS", [])), len(t.get("UNBUILT", [])), len(t.get("UNCOVERED", [])),
            ", ".join(open_bars))
    components = {"counts": {k: len(v) for k, v in t.items()},
                  "not_ok": bad, "unbuilt": t.get("UNBUILT", []), "uncovered": t.get("UNCOVERED", [])}
    return refusals, all_green, refused, components


def _passed(verdict):
    return verdict == "PASS" or (isinstance(verdict, str) and verdict.startswith("PASS"))


def judge_step4(ext, mod, current_hash, expected_pids):
    """(refusals, step4) for a step-4 (extension_proof.py) result. Pure. `ext` None -> step4 UNMEASURED, no refusal:
    the caller decides what a missing step 4 does to the verdict (it is never a pass)."""
    if ext is None:
        return [], {"status": "UNMEASURED", "why": "no step-4 result supplied (--extensions)"}
    refusals = ["step 4: " + r for r in provenance(ext, mod, current_hash, expected_pids)]
    if ext.get("refused"):
        refusals.append("step 4: run REFUSED: %s" % ext["refused"])
    declared, ran = ext.get("chains_declared"), ext.get("chains_run") or []
    if not declared:
        refusals.append("step 4: result carries no chains_declared -- cannot prove it ran every chain; rerun")
    elif set(declared) - set(ran):
        refusals.append("step 4: PARTIAL run, %d of %d chains not run: %s"
                        % (len(set(declared) - set(ran)), len(declared), sorted(set(declared) - set(ran))[:6]))
    comps = [(ch.get("name"), c) for ch in ext.get("chains") or [] for c in ch.get("components") or []]
    if not comps:
        refusals.append("step 4: result has no components")
    fail = ["%s/%s" % (n, c.get("name")) for n, c in comps if c.get("verdict") == "FAIL"]
    unm = ["%s/%s" % (n, c.get("name")) for n, c in comps if not _passed(c.get("verdict")) and c.get("verdict") != "FAIL"]
    st = "FAIL" if fail else ("UNMEASURED" if unm or not comps or not ext.get("all_green") else "PASS")
    step4 = {"status": st, "mod_hash": ext.get("mod_hash"), "components": len(comps),
             "pass": len(comps) - len(fail) - len(unm), "fail": fail, "unmeasured": unm,
             "why": "" if st == "PASS" else ("all_green false with every component PASS" if not fail and not unm
                                             and comps else "")}
    return refusals, step4


def record(mod, result_path, tier, ext_path=None, _resolve=None, _record=None):
    """Validate `result_path` against the mod NOW and the tier, then status.record_run.
    Returns (exit_code, message, entry_or_None). `_resolve`/`_record` are selftest seams."""
    import northstar
    import runner
    import status
    with open(result_path, "r", encoding="utf-8") as f:
        res = json.load(f)
    mod_dir = runner.find_mod_dir(mod)
    current = status.mod_hash(mod_dir)
    if _resolve is None:
        import modset_builder as mb
        def _resolve(name):                            # noqa: E306
            if name not in mb.TIERS:
                return None, ["no such tier %r" % name]
            pids, missing, refusals = mb.resolve_tier(name, mb.scan())
            return pids, (["tier mods not installed: %s" % missing] if missing else []) + list(refusals)
    expected, tier_problems = _resolve(tier)
    refusals, all_green, refused, components = judge(res, mod, current, expected)
    refusals = list(tier_problems or []) + refusals
    step4 = None
    if status.step4_required(mod_dir):
        ext = None
        if ext_path:
            with open(ext_path, "r", encoding="utf-8") as f:
                ext = json.load(f)
        r4, step4 = judge_step4(ext, mod, current, expected)
        refusals += r4
        if ext_path:
            step4["result"] = os.path.relpath(os.path.abspath(ext_path), runner.ROOT).replace(os.sep, "/")
        if step4["status"] != "PASS":
            if all_green and step4["status"] == "UNMEASURED" and ext is None:
                refused = "; ".join(x for x in (refused, "step 4 UNMEASURED: no extension_proof result supplied "
                                                         "(--extensions)") if x)
            else:
                all_green, refused = False, ""         # a FAIL/UNMEASURED step-4 component is RED, like a FAIL row
    elif ext_path:
        refusals.append("%s has no step 4 (%s) -- --extensions does not apply" % (mod, "/".join(status.STEP4_SCRIPT)))
    if refusals:
        return 2, "REFUSED to record %s:\n  - %s" % (mod, "\n  - ".join(refusals)), None
    walk = northstar.find_walk(runner.ROOT, mod)
    run_id = "%s/%s@%s" % (mod, res.get("script", "script"), os.path.basename(result_path))
    rel = os.path.relpath(os.path.abspath(result_path), runner.ROOT).replace(os.sep, "/")
    extra = {"components": components,
             "source": {"verb": "modcheck record", "result": rel, "tier": tier,
                        "started": res.get("started"), "ticks_spent": res.get("ticks_spent"),
                        "env_running_count": len((res.get("env") or {}).get("running") or []),
                        "env_running_sha256": (res.get("env") or {}).get("running_sha256"),
                        "assembly_sha256": (res.get("env") or {}).get("assembly_sha256")}}
    if step4 is not None:
        extra["step4"] = step4
    entry = (_record or status.record_run)(mod, mod_dir, run_id, all_green, walk=walk,
                                           refused=refused, extra=extra)
    return 0, "recorded %s: %s at %s (%s)%s" % (mod, entry["status"], entry["hash"][:12], run_id,
                                                 "" if step4 is None else "; step 4 %s" % step4["status"]), entry
