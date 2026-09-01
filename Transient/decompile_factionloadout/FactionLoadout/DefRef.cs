using System;
using FactionLoadout.Util;
using Verse;

namespace FactionLoadout;

public class DefRef<T> : IExposable, IDeepCopyable<DefRef<T>> where T : Def, new()
{
	private string defName;

	private string modName;

	private T def;

	public bool HasValue => def != null;

	public bool IsMissing
	{
		get
		{
			if (def == null)
			{
				return defName != null;
			}
			return false;
		}
	}

	public string DefName => defName;

	public string ModName => modName;

	public string LabelCap
	{
		get
		{
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			object obj = Def;
			TaggedString? val = ((obj != null) ? new TaggedString?(((Def)obj).LabelCap) : ((TaggedString?)null));
			if (!val.HasValue)
			{
				return null;
			}
			return TaggedString.op_Implicit(val.GetValueOrDefault());
		}
	}

	public T Def
	{
		get
		{
			return def;
		}
		set
		{
			def = value;
			defName = ((Def)(((object)value)?)).defName;
			object obj = value;
			object obj2;
			if (obj == null)
			{
				obj2 = null;
			}
			else
			{
				ModContentPack modContentPack = ((Def)obj).modContentPack;
				obj2 = ((modContentPack != null) ? modContentPack.Name : null);
			}
			modName = (string)obj2;
		}
	}

	public Type GenericType => typeof(T);

	public DefRef()
	{
	}

	public DefRef(T def)
	{
		Def = def;
	}

	public virtual void ExposeData()
	{
		Scribe_Values.Look<string>(ref defName, "defName", (string)null, true);
		Scribe_Values.Look<string>(ref modName, "modName", (string)null, true);
		Scribe_Defs.Look<T>(ref def, "def");
		if (def == null && defName != null)
		{
			def = DefDatabase<T>.GetNamed(defName, false);
			ModCore.Log("Trying to restore missing def: " + defName + "... " + ((def == null) ? "Failed!" : "Success!"));
		}
	}

	public override string ToString()
	{
		string text = "<null>";
		if (IsMissing)
		{
			text = "<missing:" + defName + ">";
		}
		if (HasValue)
		{
			text = "(" + ((Def)def).defName + ")";
		}
		return "DefRef<" + GenericType.Name + "> " + text;
	}

	public DefRef<T> DeepClone()
	{
		return new DefRef<T>(def)
		{
			defName = defName,
			modName = modName
		};
	}

	public static implicit operator T(DefRef<T> r)
	{
		if (r == null)
		{
			return default(T);
		}
		return r.Def;
	}

	public static implicit operator DefRef<T>(T def)
	{
		return new DefRef<T>(def);
	}
}
