using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace Outposts;

public class OutpostExtension : DefModExtension
{
	public List<BiomeDef> AllowedBiomes;

	public List<ThingDefCountClass> CostToMake;

	public List<BiomeDef> DisallowedBiomes;

	public List<SkillDef> DisplaySkills;

	public HistoryEventDef Event;

	[PostToSetings("Outposts.Setting.MinimumPawns", PostToSetingsAttribute.DrawMode.IntSlider, null, 1f, 10f, null, 0)]
	public int MinPawns;

	public ThingDef ProvidedFood;

	[PostToSetings("Outposts.Setting.Range", PostToSetingsAttribute.DrawMode.IntSlider, null, 1f, 30f, null, -1)]
	public int Range = -1;

	public List<AmountBySkill> RequiredSkills;

	public bool RequiresGrowing;

	public List<ResultOption> ResultOptions;

	[PostToSetings("Outposts.Setting.ProductionTime", PostToSetingsAttribute.DrawMode.Time, null, 0f, 0f, null, -1)]
	public int TicksPerProduction = 900000;

	[PostToSetings("Outposts.Setting.PackTime", PostToSetingsAttribute.DrawMode.Time, null, 0f, 0f, null, null)]
	public int TicksToPack = 420000;

	public int TicksToSetUp = -1;

	public List<SkillDef> RelevantSkills => new HashSet<SkillDef>(RequiredSkills.SelectOrEmpty((AmountBySkill rq) => rq.Skill).Concat(ResultOptions.SelectManyOrEmpty((ResultOption ro) => ro.AmountsPerSkills.SelectOrEmpty((AmountBySkill aps) => aps.Skill).Concat(ro.MinSkills.SelectOrEmpty((AmountBySkill ms) => ms.Skill)))).Concat(DisplaySkills.OrEmpty())).ToList();
}
