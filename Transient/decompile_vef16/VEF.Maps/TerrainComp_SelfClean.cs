using RimWorld;
using Verse;

namespace VEF.Maps;

public class TerrainComp_SelfClean : TerrainComp
{
	public float cleanProgress = float.NaN;

	public Filth currentFilth;

	public TerrainCompProperties_SelfClean Props => (TerrainCompProperties_SelfClean)props;

	protected virtual bool CanClean => true;

	public void StartClean()
	{
		if (currentFilth == null)
		{
			Log.Warning("Cannot start clean for filth because there is no filth selected. Canceling.");
		}
		else if (((Thing)currentFilth).def.filth == null)
		{
			Log.Error("Filth of def " + ((Def)((Thing)currentFilth).def).defName + " cannot be cleaned because it has no FilthProperties.");
		}
		else
		{
			cleanProgress = ((Thing)currentFilth).def.filth.cleaningWorkToReduceThickness;
		}
	}

	public override void CompTick()
	{
		base.CompTick();
		if (CanClean)
		{
			DoCleanWork();
		}
	}

	public virtual void DoCleanWork()
	{
		if (currentFilth == null)
		{
			cleanProgress = float.NaN;
			if (!FindFilth())
			{
				return;
			}
		}
		if (float.IsNaN(cleanProgress))
		{
			StartClean();
		}
		if (cleanProgress > 0f)
		{
			cleanProgress -= 1f;
		}
		else
		{
			FinishClean();
		}
	}

	public bool FindFilth()
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Expected O, but got Unknown
		if (currentFilth != null)
		{
			return true;
		}
		Filth val = (Filth)GridsUtility.GetThingList(parent.Position, parent.Map).Find((Thing f) => f is Filth);
		if (val != null)
		{
			currentFilth = val;
			return true;
		}
		return false;
	}

	public void FinishClean()
	{
		if (currentFilth == null)
		{
			Log.Warning("Cannot finish clean for filth because there is no filth selected. Canceling.");
			return;
		}
		currentFilth.ThinFilth();
		if (((Thing)currentFilth).Destroyed)
		{
			currentFilth = null;
		}
		else
		{
			cleanProgress = float.NaN;
		}
	}

	public override void PostExposeData()
	{
		base.PostExposeData();
		Scribe_Values.Look<float>(ref cleanProgress, "cleanProgress", float.NaN, false);
		Scribe_References.Look<Filth>(ref currentFilth, "currentFilth", false);
	}
}
