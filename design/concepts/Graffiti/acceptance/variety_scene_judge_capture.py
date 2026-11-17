import json,sys
s=json.load(open(sys.argv[1]));sc={x["id"]:x for x in (s["scenes"] if isinstance(s,dict) else s)}["sc_spree_variety"]
blob=json.dumps(sc).lower(); act=json.dumps(sc.get("action")).lower()
ok=("captur" in act and "judge" in act) and "recolour" in json.dumps(sc.get("control") or sc.get("controls")).lower() and "recolours of one" in json.dumps(sc.get("control") or sc.get("controls")).lower()
print("PASS" if ok else "FAIL: sc_spree_variety needs a capture-for-judge action and a recolour-set control expecting 'recolours of one'");sys.exit(0 if ok else 1)
