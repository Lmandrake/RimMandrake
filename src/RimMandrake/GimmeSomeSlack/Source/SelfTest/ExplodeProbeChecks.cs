// NOT-COMPILED by the normal SelfTest project. selftest_gss_explode_parse.py materializes
// this extraction template with the exact production explode branch and compiles it separately.
// Engine doubles exercise lookup/dispatch/identity, not actual engine explosion effects.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Aerial;

class DamageDef { public string defName; public bool harmsHealth = true; public DamageDef(string name) { defName = name; } }
static class DamageDefOf { public static readonly DamageDef Bomb = new DamageDef("Bomb"); }
static class DefDatabase<T> where T : class
{
    public static readonly DamageDef Named = new DamageDef("RM_Repulse_Palm");
    public static T GetNamedSilentFail(string name) =>
        (name == "Bomb" ? DamageDefOf.Bomb : name == "RM_Repulse_Palm" ? Named : null) as T;
}
struct IntVec3 { public int x, z; public IntVec3(int x, int y, int z) { this.x = x; this.z = z; } }
static class GenExplosion
{
    public static DamageDef Last;
    public static void DoExplosion(IntVec3 c, object map, float radius, DamageDef damage, object who, int amount) { Last = damage; }
}
class Link { public SpanState state = SpanState.Up; public Anchor other; }
class Anchor { public int thingIDNumber; public IntVec3 BasePoint; public List<Link> links = new List<Link>(); }
class Component
{
    public int explosionCuts = 0, kineticSways = 0;
    public List<Anchor> Anchors;
    public Component()
    {
        var a = new Anchor { thingIDNumber = 1, BasePoint = new IntVec3(0, 0, 2) };
        var b = new Anchor { thingIDNumber = 2, BasePoint = new IntVec3(10, 0, 2) };
        a.links.Add(new Link { other = b }); b.links.Add(new Link { other = a });
        Anchors = new List<Anchor> { a, b };
    }
}
// The real shipping method reads the DefModExtension type; that engine-bound check is not emulated here.
static class Patch_GenExplosion_CutSpans { public static bool IsKineticBlast(DamageDef d) => d.defName == "RM_Repulse_Palm"; }
namespace RimMandrake.GimmeSomeSlack.Core
{
    // Unused bracket-render constants needed to compile the full production AerialMath file.
    static class WallMount { public const double SouthBand = 0.4, SideBevel = 0.18; }
}
class ExplodeProbeChecks
{
    static readonly DamageDef Synthetic = new DamageDef("Bomb");
    static DamageDef KineticDamage() => Synthetic;
    static string S(string s) => JsonSerializer.Serialize(s);
    static string B(bool b) => b ? "true" : "false";
    static string Ok(string cmd, string fields) => "{\"success\":true,\"cmd\":" + S(cmd) + "," + fields + "}";
    static string Fail(string cmd, string error) => "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":" + S(error) + "}";
    static string Run(string request)
    {
        // PRODUCTION_REQUEST_NORMALIZATION
        object map = new object();
        var comp = new Component();
        try
        {
            // PRODUCTION_EXPLODE_BRANCH
            return Fail(cmd, "not explode");
        }
        catch (Exception ex) { return Fail(cmd, ex.Message); }
    }
    static int failures;
    static void Check(bool ok, string name)
    {
        Console.WriteLine((ok ? "PASS " : "FAIL ") + name);
        if (!ok) failures++;
    }
    static void Blast(string suffix, DamageDef expected, bool synthetic)
    {
        GenExplosion.Last = null;
        var reply = Run("explode:1,2,2.5,50" + suffix);
        Console.WriteLine(reply);
        using var json = JsonDocument.Parse(reply);
        var value = json.RootElement;
        Check(value.GetProperty("success").GetBoolean() && ReferenceEquals(GenExplosion.Last, expected), "actual dispatched object " + suffix);
        Check(value.TryGetProperty("damageDef", out var name) && name.GetString() == expected.defName &&
              value.TryGetProperty("synthetic", out var flag) && flag.GetBoolean() == synthetic, "reply identity " + suffix);
    }
    static int Main()
    {
        Blast("", DamageDefOf.Bomb, false);
        Blast(",Bomb", DamageDefOf.Bomb, false);
        Blast(",kinetic", Synthetic, true);
        Blast(",RM_Repulse_Palm", DefDatabase<DamageDef>.Named, false);
        foreach (string args in new[] { "1,2,2.5,50,UnknownDamage", "1,2,2.5,50,bomb", "1,2,2.5,50,",
                 "1,2,2.5,50, RM_Repulse_Palm", "1,2,2.5,50,RM_Repulse_Palm ", "1,2,2.5,50,kinetic ",
                 "1,2,2.5,50,RM_Repulse_Palm\t", "1,2,2.5,50,RM-Bad",
                 "1,2,2.5,50,1Bad", "1,2,2.5,50,éBad", "1,2,2.5,50,Bomb,kinetic", "1,2,2.5" })
        {
            GenExplosion.Last = null;
            var reply = Run("explode:" + args);
            Console.WriteLine(reply);
            using var json = JsonDocument.Parse(reply);
            Check(!json.RootElement.GetProperty("success").GetBoolean() && GenExplosion.Last == null, "refuse without explosion " + args);
        }
        // Existing synthetic-token semantics and blast verdicts stay on their normal SelfTest entry points too.
        Check(AerialMath.ExplodeWantsKinetic("1,2,3,4,kinetic".Split(',')) &&
              !AerialMath.ExplodeWantsKinetic("1,2,3,4,RM_Repulse_Palm".Split(',')), "existing token helper");
        Check(AerialMath.BlastKindFor(true, true, 50, true, true) == AerialMath.BlastKind.Sway &&
              AerialMath.BlastKindFor(true, true, 50, true, false) == AerialMath.BlastKind.None, "existing kinetic setting verdict");
        Console.WriteLine("failures=" + failures);
        return failures == 0 ? 0 : 1;
    }
}
