"""Run aerial --flips; require both fresh exact kineticSway MOD rows and whole-driver success."""
import sys

from restring_style_proof import read_result, run_proof
from validation_aerial import KINETIC_DAMAGE, KINETIC_ROWS


def check_result(path, started, finished):
    rows = read_result(path, started, finished, "flips")
    if any(r.get("status") in ("FAIL", "UNMEASURED") for r in rows):
        raise ValueError("aerial driver has failed or unmeasured rows")
    selected = []
    for rid, enabled in zip(KINETIC_ROWS, (True, False)):
        exact = [r for r in rows if r.get("id") == rid]
        if len(exact) != 1 or exact[0].get("status") != "PASS" or exact[0].get("class") != "MOD":
            raise ValueError("requires exactly one %s MOD PASS" % rid)
        detail = exact[0].get("detail")
        if not isinstance(detail, dict) or type(detail.get("schema")) is not int or detail["schema"] != 1 or \
                detail.get("setting") != "kineticSway" or detail.get("enabled") is not enabled or \
                detail.get("damageDef") != KINETIC_DAMAGE:
            raise ValueError("requires registered kineticSway census evidence")
        delta = detail.get("censusSwayDelta")
        if detail.get("synthetic") is not False or detail.get("kinetic") is not True or detail.get("harmsHealth") is not True or \
                type(detail.get("spansReached")) is not int or detail["spansReached"] <= 0 or \
                detail.get("settingBefore") != str(enabled) or detail.get("settingAfter") != str(enabled) or \
                type(delta) is not int or not (delta > 0 if enabled else delta == 0) or \
                type(detail.get("censusCutDelta")) is not int or detail["censusCutDelta"] != 0 or detail.get("spanStillUp") is not True:
            raise ValueError("requires observed real kinetic blast, setting readbacks and census deltas")
        selected.append(exact[0])
    return selected


def main(argv=None):
    return run_proof(argv, mode="flips", prefix="kinetic-", check=check_result)


if __name__ == "__main__":
    sys.exit(main())
