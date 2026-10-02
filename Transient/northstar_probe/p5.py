import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from rimdrive.session import Session
def val(s,n): return [f["value"] for f in s.call("jawa/debug_settings",action="list")["fields"] if f["name"]==n]
with Session(strict=False,quiet=True,focus=False) as s:
    for n in ("enableStoryteller","enableRandomMentalStates","enableRandomDiseases"):
        before=val(s,n); r=s.call("jawa/debug_settings",action="set",field=n,value=False); r.pop("operation",None)
        print(n,before,"->",val(s,n), json.dumps(r)[:200])
    for n in ("enableStoryteller","enableRandomMentalStates","enableRandomDiseases"):
        s.call("jawa/debug_settings",action="set",field=n,value=True)
    print("restored", [val(s,n) for n in ("enableStoryteller","enableRandomMentalStates","enableRandomDiseases")])
    r=s.call("jawa/difficulty_tune"); r.pop("operation",None); print("difficulty_tune default:", json.dumps(r)[:300])
    r=s.call("jawa/incident_schedule"); r.pop("operation",None); print("incident_schedule default:", json.dumps(r)[:300])
