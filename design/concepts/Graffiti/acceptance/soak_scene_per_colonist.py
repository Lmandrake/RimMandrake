import json,sys
s=json.load(open(sys.argv[1]));sc={x["id"]:x for x in (s["scenes"] if isinstance(s,dict) else s)}["sc_lived_in_soak"]
st=json.dumps(sc.get("start")).lower(); ex=json.dumps(sc.get("expect")).lower(); ctl=json.dumps(sc.get("control")).lower()
ok=("sensitive" in st and "clean" in st and "freak" in st) and ("each colonist" in ex or "per colonist" in ex or "every colonist" in ex) and "unforced" in ex and "summed" not in ex and ("colonist" in ctl)
print("PASS" if ok else "FAIL: sc_lived_in_soak needs a trait-mix start, a per-colonist expect against the control, an unforced-story assertion, a per-colonist control");sys.exit(0 if ok else 1)
