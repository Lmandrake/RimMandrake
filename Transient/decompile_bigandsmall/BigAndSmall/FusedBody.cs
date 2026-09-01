using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public class FusedBody
{
	public static readonly Dictionary<string, FusedBody> FusedBodies = new Dictionary<string, FusedBody>();

	public static readonly Dictionary<ThingDef, FusedBody> FusedBodyByThing = new Dictionary<ThingDef, FusedBody>();

	public BodyDef generatedBody;

	public MergableBody[] mergableBodies;

	private ThingDef thing;

	public MergableBody fuseSetBody;

	public bool fake;

	public bool isMechanical;

	public MergableBody SourceBody => mergableBodies[0];

	public ThingDef Thing
	{
		get
		{
			return thing;
		}
		private set
		{
			thing = value;
		}
	}

	public FusedBody(BodyDef generatedBody, MergableBody fusetSetBody, bool mechanical, params MergableBody[] mergableBodies)
	{
		isMechanical = mechanical;
		this.generatedBody = generatedBody;
		this.mergableBodies = mergableBodies;
		fuseSetBody = fusetSetBody;
		FusedBodies[GetKey(mechanical, mergableBodies.Select((MergableBody x) => x.bodyDef).ToArray())] = this;
	}

	public void SetThing(ThingDef thing)
	{
		Thing = thing;
		FusedBodyByThing[thing] = this;
	}

	private static string GetKey(bool mechanical, BodyDef[] bodyDefs)
	{
		string.Join("|", bodyDefs.OrderBy((BodyDef x) => ((Def)x).defName));
		return string.Join("|", bodyDefs.OrderBy((BodyDef x) => ((Def)x).defName));
	}

	public static FusedBody TryGetBody(bool mechanical, params BodyDef[] bodyDefs)
	{
		string text = (mechanical ? "mechanical" : "biological");
		if (FusedBodies.TryGetValue(GetKey(mechanical, bodyDefs), out var value))
		{
			return value;
		}
		if (bodyDefs.Count() > 1)
		{
			Dictionary<string, FusedBody> fusedBodies = FusedBodies;
			List<BodyDef> list = new List<BodyDef>();
			list.Add(GetSubstituted(bodyDefs).First());
			list.AddRange(bodyDefs.Skip(1));
			if (fusedBodies.TryGetValue(GetKey(mechanical, list.ToArray()), out var value2))
			{
				return value2;
			}
			bool mechanical2 = mechanical;
			BodyDef val = GetSubstituted(bodyDefs).First();
			List<BodyDef> substituted = GetSubstituted(bodyDefs.Skip(1).ToArray());
			int num = 0;
			BodyDef[] array = (BodyDef[])(object)new BodyDef[1 + substituted.Count];
			array[num] = val;
			num++;
			foreach (BodyDef item in substituted)
			{
				array[num] = item;
				num++;
			}
			if (FusedBodies.TryGetValue(GetKey(mechanical2, array), out var value3))
			{
				return value3;
			}
		}
		if (!FusedBodies.TryGetValue(GetKey(mechanical, GetSubstituted(bodyDefs).ToArray()), out var value4))
		{
			return null;
		}
		return value4;
	}

	private static List<BodyDef> GetSubstituted(BodyDef[] bodyDefs)
	{
		List<BodyDef> list = bodyDefs.ToList();
		List<Substitutions> substitutions = BodyDefFusionsHelper.Substitutions;
		foreach (BodyDef inBody in bodyDefs)
		{
			Substitutions substitutions2 = GenCollection.FirstOrDefault<Substitutions>(substitutions, (Predicate<Substitutions>)((Substitutions x) => x.bodyDefs.Contains(inBody)));
			if (substitutions2 != null)
			{
				list.Remove(inBody);
				if (substitutions2.target != null)
				{
					list.Add(substitutions2.target);
				}
			}
		}
		return list;
	}

	public static BodyDef TryGetNonFused(params BodyDef[] bodyDefs)
	{
		if (GetSubstituted(bodyDefs).Count == 1)
		{
			return GetSubstituted(bodyDefs).First();
		}
		return null;
	}

	public static bool HasKey(bool mechanical, params BodyDef[] bodyDefs)
	{
		return FusedBodies.ContainsKey(GetKey(mechanical, bodyDefs));
	}
}
