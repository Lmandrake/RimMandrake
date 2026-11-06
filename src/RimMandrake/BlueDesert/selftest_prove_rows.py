"""selftest for prove_rows.py: a refused driver run says why on its last line (GAMEENV_FIX_PROOFSITE_22E336EE_ITEMS_WAIT).
    python3 src/RimMandrake/BlueDesert/selftest_prove_rows.py
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prove_rows as P  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rimflow"))
import relentless_live as L  # noqa: E402

ZOMBIE = "get_game_info answered with no ticksGame -- loaded-looking ZOMBIE state (aborted load); success flags prove nothing"
IDS = ["flora_harvest.site_ready_flora", "flora_harvest.harvest_yields_Chemfuel_from_RM_Wartshrub"]


def run(doc, ids=IDS):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump(doc, fh)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            code = P.main(["prove_rows.py", fh.name] + ids)
    finally:
        os.unlink(fh.name)
    lines = buf.getvalue().splitlines()
    log = tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8")
    log.write(buf.getvalue())
    log.close()
    try:
        asked = L.asked_reload(log.name)
    finally:
        os.unlink(log.name)
    return code, lines, asked


def main():
    fails = []

    def check(name, ok, got):
        if not ok:
            fails.append("%s: %r" % (name, got))

    # the 08:56Z shape (A3.json of that sitting): a zombie game refused at preflight -> reload, read by the live tier
    code, lines, asked = run({"bars": [], "refused": "game_loaded FAIL; no_modal FAIL; site:map_size FAIL",
                              "preflight": [{"name": "tool_census", "status": "PASS"},
                                            {"name": "game_loaded", "status": "FAIL", "evidence": ZOMBIE}]})
    check("zombie exit", code == 2, code)
    check("zombie rows", lines[0].startswith("MISSING") and lines[1].startswith("MISSING"), lines)
    check("zombie last line asks reload", asked and "ZOMBIE" in asked and "game_loaded" in asked, lines[-1])

    # a site refusal (the 11-04 settings_defaults shape): no reload, its own cause text
    code, lines, asked = run({"bars": [], "refused": "site:settings_defaults FAIL",
                              "preflight": [{"name": "game_loaded", "status": "PASS"}]})
    check("site exit", code == 2, code)
    check("site last line", lines[-1] == "UNMEASURED: the driver refused: site:settings_defaults FAIL", lines[-1])
    check("site no reload", asked is None, asked)
    # two different refusals are two different causes to the live tier
    z = run({"bars": [], "refused": "game_loaded FAIL", "preflight": [
        {"name": "game_loaded", "status": "FAIL", "evidence": ZOMBIE}]})[1][-1]
    check("causes differ", L.cause(z) != L.cause(lines[-1]), (z, lines[-1]))

    # ran, but a named row absent
    code, lines, asked = run({"bars": [{"id": IDS[0], "status": "PASS", "evidence": "PASS"}], "preflight": []})
    check("absent exit", code == 2, code)
    check("absent last line", lines[-1] == "UNMEASURED: the results hold no row %s" % IDS[1], lines[-1])

    # unchanged behaviour: all PASS -> 0 and no extra line; a FAIL -> 1
    code, lines, _ = run({"bars": [{"id": i, "status": "PASS", "evidence": "PASS"} for i in IDS]})
    check("pass exit", code == 0 and len(lines) == 2, (code, lines))
    code, lines, _ = run({"bars": [{"id": IDS[0], "status": "FAIL", "evidence": "x"},
                                   {"id": IDS[1], "status": "UNMEASURED", "evidence": "y"}]})
    check("fail exit", code == 1 and len(lines) == 2, (code, lines))

    if fails:
        print("FAIL selftest_prove_rows:\n  " + "\n  ".join(fails))
        return 1
    print("selftest_prove_rows: all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
