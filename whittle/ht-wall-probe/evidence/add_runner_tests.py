from pathlib import Path
p=Path(__file__).resolve().parents[3]/'src/RimMandrake/Utils/selftest_hugethings_test_races.py'
s=p.read_text();a=s.index('\n\nSRC_LIVE = ')
s=s[:a]+'''

def roofwall_modes():
    """All four calls, mode readbacks and restoration must contribute to R4."""
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "HugeThings", "northstar"))
    import titan_test_races_live as L
    class Fake:
        def __init__(self, fault=""):
            self.settings = {f:"False" for f in L.ROOF_FIELDS}
            self.initial = dict(self.settings)
            self.rows, self.probes, self.fault = [], [], fault
        def get(self, f):
            return self.settings[f]
        def put(self, f, v):
            self.settings[f] = str(v)
            return True
        def hook(self, method, args):
            self.probes.append((method,args,dict(self.settings)))
            control = args.startswith(L.CTL + "|")
            legacy = self.settings["wallsSlotsEnabled"] == "False"
            if self.fault == "refused control" and control:
                return False, "FAIL missing kind"
            hp = 175 if legacy and not control and self.fault != "always intact" else 195
            if self.fault == "mode drift":
                self.settings["wallsSlotsEnabled"] = "False"
            return True, ("%s tier=%s roofAfter=%s wallHpBefore=195 wallHpAfter=%d wallDestroyed=False" %
                (L.CTL if control else L.T2, "None" if control else "T2", "RoofConstructed" if control else "none", hp))
        def row(self, rid, status, cls, detail):
            self.rows.append(dict(id=rid,status=status,cls=cls,detail=detail))
    for fault in ("", "always intact", "refused control", "mode drift"):
        r=Fake(fault)
        L.roofwall_row(r, [(100,100)])
        check("R4 bounded both modes/control + strict aggregate: %s" % (fault or "good"),
              len(r.probes)==4 and len(r.rows)==1 and (r.rows[0]["status"]=="PASS") == (fault==""))
        check("R4 exact raw settings restored: %s" % (fault or "good"), r.settings==r.initial)
        check("R4 alone cannot satisfy default full runner", L.verdict(r.rows)==1)
''' +s[a:]
s=s.replace('    judges()\n', '    judges()\n    roofwall_modes()\n')
p.write_text(s)
