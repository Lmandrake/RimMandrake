using System.Collections.Generic;
using System.Reflection;
using System.Text;
using Verse;

namespace RimMandrake.StarWars.Patches
{
    /// <summary>
    /// STARWARS_JUNK_RESKIN_1 live proof hook, read-only (bridge: jawa/static_call type=RimMandrake.StarWars.Patches.RSW_JunkReskinProof
    /// method=Report args=x). For each reskinned junk def it reads the BUILT graphic, not the XML: Graphic_Random, every variant
    /// texture loaded from the RSW_Junk/&lt;defName&gt; folder, and for rotatable defs that every variant is a Single drawn rotated
    /// (ShouldDrawRotated), which is what turns the north-drawn picture with the building. One line per def; the first line
    /// is "PASS n/n" or "FAIL k/n". Spawns nothing and changes nothing.
    /// </summary>
    public static class RSW_JunkReskinProof
    {
        public static readonly string[] Defs =
        {
            "AncientRustedCar", "AncientRustedCarFrame", "AncientPodCar", "AncientRustedTruck", "AncientRustedJeep",
            "AncientRustedEngineBlock", "AncientLargeRustedEngineBlock", "AncientWheel", "AncientGiantWheel",
            "AncientTankTrap", "AncientAPC", "AncientTank", "AncientWarwalkerClaw", "AncientWarwalkerLeg",
            "AncientWarwalkerFoot", "AncientWarwalkerTorso", "AncientWarwalkerShell", "AncientWarspiderRemains",
            "AncientMiniWarwalkerRemains", "AncientJetEngine", "AncientDropshipEngine", "AncientRustedDropship",
            "AncientMegaCannonBarrel", "AncientMegaCannonTripod",
        };

        private static readonly FieldInfo SubGraphics =
            typeof(Graphic_Collection).GetField("subGraphics", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);

        public static string Report(string args)
        {
            var lines = new List<string>();
            int ok = 0;
            lines.Add("junkReskin setting=" + RSW_StarWarsPatchesSettings.junkReskin);
            foreach (string name in Defs)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                string why = Check(def, name, out string detail);
                if (why == null) ok++;
                lines.Add((why == null ? "ok   " : "FAIL ") + name + " " + (why ?? detail));
            }
            var sb = new StringBuilder();
            sb.Append(ok == Defs.Length ? "PASS " : "FAIL ").Append(ok).Append('/').Append(Defs.Length);
            foreach (string l in lines) sb.Append('\n').Append(l);
            return sb.ToString();
        }

        private static string Check(ThingDef def, string name, out string detail)
        {
            detail = "";
            if (def == null) return "def not loaded";
            if (!(def.graphic is Graphic_Random g)) return "graphic is " + (def.graphic?.GetType().Name ?? "null") + ", want Graphic_Random";
            if (SubGraphics == null) return "Graphic_Collection.subGraphics not found (engine changed)";
            var subs = SubGraphics.GetValue(g) as Graphic[];
            if (subs == null || subs.Length == 0) return "no variants loaded";
            string want = "RSW_Junk_" + name + "_";
            int rotated = 0;
            foreach (Graphic s in subs)
            {
                string tex = s?.MatSingle?.mainTexture?.name ?? "null";
                if (!tex.StartsWith(want)) return "variant texture '" + tex + "' is not from RSW_Junk/" + name;
                if (s.ShouldDrawRotated) rotated++;
            }
            if (def.rotatable && rotated != subs.Length)
                return "rotatable but only " + rotated + "/" + subs.Length + " variants draw rotated";
            detail = subs.Length + " variants, rotatable=" + def.rotatable + ", drawRotated " + rotated + "/" + subs.Length
                     + ", label '" + def.label + "'";
            return null;
        }
    }
}
