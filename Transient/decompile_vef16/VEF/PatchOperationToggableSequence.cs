using System.Collections.Generic;
using System.Xml;
using Verse;

namespace VEF;

public class PatchOperationToggableSequence : PatchOperation
{
	public bool enabled;

	public string label;

	private readonly List<string> mods = new List<string>();

	private readonly List<PatchOperation> operations = new List<PatchOperation>();

	private PatchOperation lastFailedOperation;

	protected override bool ApplyWorker(XmlDocument xml)
	{
		if (ModsFound())
		{
			string key = label.Replace(" ", "");
			if (!GenDictionary.NullOrEmpty<string, bool>(VFEGlobal.settings.toggablePatch) && VFEGlobal.settings.toggablePatch.ContainsKey(key))
			{
				VFEGlobal.settings.toggablePatch.TryGetValue(key, out var value);
				if (value)
				{
					return ApplyPatches(xml);
				}
			}
			else if (enabled)
			{
				return ApplyPatches(xml);
			}
		}
		return true;
	}

	private bool ApplyPatches(XmlDocument xml)
	{
		foreach (PatchOperation operation in operations)
		{
			if (!operation.Apply(xml))
			{
				lastFailedOperation = operation;
				return false;
			}
		}
		return true;
	}

	public override string ToString()
	{
		int num = ((operations != null) ? operations.Count : 0);
		string text = $"{((object)this).ToString()}(count={num}";
		if (lastFailedOperation != null)
		{
			text = text + ", lastFailedOperation=" + (object)lastFailedOperation;
		}
		return text + ")";
	}

	public override void Complete(string modIdentifier)
	{
		((PatchOperation)this).Complete(modIdentifier);
		lastFailedOperation = null;
	}

	public bool ModsFound()
	{
		for (int i = 0; i < mods.Count; i++)
		{
			if (!ModLister.HasActiveModWithName(mods[i]))
			{
				return false;
			}
		}
		return true;
	}
}
