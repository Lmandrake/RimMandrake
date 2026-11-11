"""Pure live-runner aggregation. Classification is evidence coverage, not gameplay success."""


def aggregate(rows, required):
    rows = list(rows)
    required = set(required)
    ids = [r.get("id") for r in rows]
    complete = bool(required) and required.issubset(ids) and len(ids) == len(set(ids))
    classified = complete and all(r.get("status") == "PASS" or
                                (r.get("status") == "FAIL" and r.get("cls") == "MOD") for r in rows)
    gameplay = complete and all(r.get("status") == "PASS" and r.get("cls") != "OWED" for r in rows)
    return dict(all_rows_classified=classified, gameplay_pass=gameplay)


def scrape_widening(dead, widened):
    if not dead:
        return "UNMEASURED"
    return "PASS" if set(dead).issubset(widened) else "FAIL"
