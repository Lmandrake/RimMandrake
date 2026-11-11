// Engine stand-in for L0 only. Production adapter/kernel files are compiled directly; L1 uses actual engine Pawn.BodySize.
using System.Collections.Generic;
using System.Linq;
namespace Verse {
 public class Def { public string defName; }
 public class DefModExtension { }
 public class ThingDef : Def { public RaceProperties race; public List<DefModExtension> modExtensions;
  public T GetModExtension<T>() where T:DefModExtension => modExtensions?.OfType<T>().FirstOrDefault(); }
 public class RaceProperties { public float baseBodySize; public List<LifeStageAge> lifeStageAges; }
 public class LifeStageAge { public RimWorld.LifeStageDef def; }
 public class Pawn { public ThingDef def; public float factor; public RaceProperties RaceProps => def?.race; public float BodySize => factor * RaceProps.baseBodySize; }
 public static class DefDatabase<T> { public static List<T> AllDefsListForReading = new List<T>(); }
 public static class Log { public static int Errors; public static void Error(string message) { Errors++; } }
}
namespace RimWorld { public class LifeStageDef : Verse.Def { public float bodySizeFactor = 1f; } }
namespace RimMandrake.HugeThings {
 public static class RM_HugeThingsSettings {
  public static bool giantAnimalsEnabled=true, tierThresholdsCustom=false;
  public static bool TierThresholdsCustomActive => giantAnimalsEnabled && tierThresholdsCustom;
  public static float tierT1MinBodySize=4, tierT2MinBodySize=8, tierT3MinBodySize=20;
 }
}
