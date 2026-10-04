"""selftest_mod_static.py -- mod_static's offline findings must be able to FAIL, and its chains enumerate offline."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modcheck import mod_static  # noqa: E402

SETTINGS = '''namespace Demo.Mod
{
    public class DemoSettings : ModSettings
    {
        public static bool alphaEnabled = true;
        public static float beta = 1f;
        public override void ExposeData()
        {
            Scribe_Values.Look(ref alphaEnabled, "alphaEnabled", true);
            Scribe_Values.Look(ref beta, "beta", 1f);
        }
        public void DoWindowContents(Rect r) { list.CheckboxLabeled("a", ref alphaEnabled); %s }
    }
    public class DemoMod : Mod { public override void DoSettingsWindowContents(Rect r) { } }
    [HarmonyPatch(typeof(Mineable), nameof(Mineable.DestroyMined))]
    static class P { }
    static class H { static void Go() { new Harmony("demo.mod").PatchAll(); } }
}
'''


def _w(root, rel, txt):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(txt)


def _mod(root, beta_control=True, listed=True, inert=False, bad_xml=False):
    _w(root, "Source/DemoSettings.cs", SETTINGS % ("list.Slider(ref beta);" if beta_control else ""))
    _w(root, "Source/Demo.csproj", '<Project><ItemGroup><Compile Include="DemoSettings.cs" />%s</ItemGroup></Project>'
       % ('<Compile Include="Other.cs" />' if listed else ""))
    _w(root, "Source/Other.cs", "namespace Demo.Mod { }")
    _w(root, "Defs/D.xml", "<Defs><IncidentDef><defName>Demo_Inc</defName></IncidentDef></Defs>" if not bad_xml else "<Defs>")
    op = '<Operation Class="PatchOperationAdd"%s><xpath>/Defs</xpath></Operation>' % (
        ' MayRequire="some.mod"' if inert else "")
    _w(root, "Patches/P.xml", "<Patch>%s</Patch>" % op)


def check(name, cond):
    print("%s %s" % ("PASS" if cond else "FAIL", name))
    return cond


def main():
    ok = True
    with tempfile.TemporaryDirectory() as d:
        _mod(d)
        ok &= check("clean mod has no findings", mod_static.static_findings(d) == [])
        cls, fields = mod_static.settings_class(d)
        ok &= check("settings class full name", cls == "Demo.Mod.DemoSettings")
        ok &= check("bool settings parsed", mod_static.bool_settings(d) == {"alphaEnabled": True})
        hid, targets = mod_static.harmony_targets(d)
        ok &= check("harmony id and target", hid == "demo.mod" and targets == [("Mineable", "DestroyMined")])
        ok &= check("incident defs", mod_static.incident_defs(d) == ["Demo_Inc"])
    for kw, needle in ((dict(beta_control=False), "beta is Scribed but has no control"),
                       (dict(listed=False), "Other.cs is not in"),
                       (dict(inert=True), "inert guard"),
                       (dict(bad_xml=True), "does not parse")):
        with tempfile.TemporaryDirectory() as d:
            _mod(d, **kw)
            f = mod_static.static_findings(d)
            ok &= check("detects: %s" % needle, any(needle in x for x in f))
    with tempfile.TemporaryDirectory() as d:
        _w(d, "Source/X.cs", "namespace N { class X { } }")
        ok &= check("detects missing ModSettings", any("no ModSettings" in x for x in mod_static.static_findings(d)))
    # chains enumerate on the offline declaration probe
    from modcheck.suite import Suite, _DeclarationProbe
    with tempfile.TemporaryDirectory() as d:
        _mod(d)
        vf = os.path.join(d, "validation.py")
        s = Suite("Demo")
        mod_static.add_settings_chain(s, vf)
        mod_static.add_harmony_chain(s, vf)
        mod_static.add_incident_chain(s, vf)
        names = []
        for _n, fn in s.chains:
            p = _DeclarationProbe()
            fn(p)
            names += [c.name for c in p.components]
        ok &= check("components declared offline", names == [
            "setting_alphaEnabled_round_trips", "patched_Mineable_DestroyMined", "dry_run_Demo_Inc"])
    print("%s mod_static selftest" % ("ALL PASS" if ok else "FAILURES"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
