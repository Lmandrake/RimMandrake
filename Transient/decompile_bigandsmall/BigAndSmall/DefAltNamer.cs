using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public class DefAltNamer : Def
{
	public abstract class Rename
	{
		public string labelMechanoid;

		public string labelBloodfeeder;

		public string labelFantasy;
	}

	public class RenameGene : Rename
	{
		public GeneDef def;
	}

	public List<RenameGene> geneRenames = new List<RenameGene>();

	private static Dictionary<GeneDef, RenameGene> allGeneRenames = new Dictionary<GeneDef, RenameGene>();

	public static Dictionary<GeneDef, RenameGene> AllGeneRenames => allGeneRenames ?? (allGeneRenames = SetupDict());

	public static void Initialize()
	{
		allGeneRenames = SetupDict();
	}

	public static Dictionary<GeneDef, RenameGene> SetupDict()
	{
		if (!DefDatabase<DefAltNamer>.AllDefs.Any())
		{
			return new Dictionary<GeneDef, RenameGene>();
		}
		return (from x in DefDatabase<DefAltNamer>.AllDefs.SelectMany((DefAltNamer x) => x.geneRenames.Select((RenameGene y) => (def: y?.def, y: y)))
			where x.y != null && x.def != null
			select x).ToDictionary(((GeneDef def, RenameGene y) x) => x.def, ((GeneDef def, RenameGene y) x) => x.y);
	}
}
