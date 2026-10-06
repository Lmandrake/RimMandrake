using System;
using System.Collections.Generic;
using System.Reflection;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>
	/// Per-net adapter (design §4 "Universal tank interop": existing tank families are ADOPTED — per-net
	/// adapters let every supported pipe network feed from and draw into our tanks). The adapter def carries
	/// the pipe mod's own storage comp (VE PipeSystem's CompResourceStorage, so it joins that net like any of
	/// its tanks) plus this comp, which moves units between that storage and the FlowWorks tanks on the
	/// adapter's liquid net. FlowWorks never references PipeSystem: the storage is found by type NAME and
	/// driven by reflection (AmountStored / AmountCanAccept / AddResource / DrawResource, read from
	/// PipeSystem.dll's metadata 2026-10-05), and the adapter defs themselves are patch-added only when the
	/// pipe mod is present (PatchOperationFindMod). Mode gizmo: feed the pipe net, or draw from it.
	/// Mod Setting: pipeAdaptersEnabled + the adapter's own machine switch.
	/// </summary>
	public class CompProperties_LiquidPipeAdapter : CompProperties
	{
		public LiquidDef liquid;
		public string storageCompTypeName = "PipeSystem.CompResourceStorage";
		/// <summary>Tank units moved per rare tick (PROVISIONAL).</summary>
		public int unitsPerRareTick = 10;
		/// <summary>Pipe-net resource per tank unit (PROVISIONAL 1:1; VE chemfuel counts chemfuel items).</summary>
		public float resourcePerUnit = 1f;

		public CompProperties_LiquidPipeAdapter()
		{
			compClass = typeof(CompLiquidPipeAdapter);
		}
	}

	public class CompLiquidPipeAdapter : ThingComp
	{
		public bool feedNet = true;
		public int moved;
		private string status = "";

		private ThingComp storage;
		private PropertyInfo amountStored;
		private PropertyInfo amountCanAccept;
		private MethodInfo addResource;
		private MethodInfo drawResource;

		public CompProperties_LiquidPipeAdapter Props => (CompProperties_LiquidPipeAdapter)props;

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref feedNet, "RM_adapterFeedNet", true);
			Scribe_Values.Look(ref moved, "RM_adapterMoved", 0);
		}

		private bool Bind()
		{
			if (storage != null)
			{
				return true;
			}
			foreach (ThingComp c in parent.AllComps)
			{
				Type t = c.GetType();
				for (Type k = t; k != null; k = k.BaseType)
				{
					if (k.FullName == Props.storageCompTypeName)
					{
						storage = c;
						break;
					}
				}
				if (storage != null)
				{
					break;
				}
			}
			if (storage == null)
			{
				Log.ErrorOnce("[FlowWorks] pipe adapter " + parent.def.defName + " has no " + Props.storageCompTypeName, parent.def.shortHash ^ 0x5A17);
				return false;
			}
			Type st = storage.GetType();
			const BindingFlags F = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
			amountStored = st.GetProperty("AmountStored", F);
			amountCanAccept = st.GetProperty("AmountCanAccept", F);
			addResource = st.GetMethod("AddResource", F, null, new[] { typeof(float) }, null);
			drawResource = st.GetMethod("DrawResource", F, null, new[] { typeof(float) }, null);
			if (amountStored == null || amountCanAccept == null || addResource == null || drawResource == null)
			{
				Log.ErrorOnce("[FlowWorks] pipe adapter " + parent.def.defName + ": " + st.FullName
					+ " lacks AmountStored/AmountCanAccept/AddResource(float)/DrawResource(float) — pipe mod API changed.",
					parent.def.shortHash ^ 0x5A18);
				storage = null;
				return false;
			}
			return true;
		}

		public override void CompTickRare()
		{
			base.CompTickRare();
			if (parent.Map == null || Props.liquid == null)
			{
				return;
			}
			if (!RM_MachinerySettings.pipeAdaptersEnabled || !RM_MachinerySettings.MachineOn(parent.def))
			{
				status = "RMFlow_MachineOffInSettings".Translate();
				return;
			}
			if (!Bind())
			{
				status = "RMFlow_AdapterBroken".Translate();
				return;
			}
			float per = Mathf.Max(0.0001f, Props.resourcePerUnit);
			if (feedNet)
			{
				float room = Convert.ToSingle(amountCanAccept.GetValue(storage));
				int units = Mathf.Min(Props.unitsPerRareTick, Mathf.FloorToInt(room / per));
				foreach (Building_LiquidTank t in RM_LiquidNet.TanksFor(parent))
				{
					if (units <= 0)
					{
						break;
					}
					if (t.Empty || t.storedLiquid != Props.liquid)
					{
						continue;
					}
					int take = Mathf.Min(units, t.storedUnits);
					if (take > 0 && t.TryRemoveLiquid(take))
					{
						addResource.Invoke(storage, new object[] { take * per });
						units -= take;
						moved += take;
					}
				}
			}
			else
			{
				float stored = Convert.ToSingle(amountStored.GetValue(storage));
				int units = Mathf.Min(Props.unitsPerRareTick, Mathf.FloorToInt(stored / per));
				if (units > 0)
				{
					Building_LiquidTank t = RM_LiquidNet.TankToFill(parent, Props.liquid, 1);
					if (t != null)
					{
						units = Mathf.Min(units, t.Capacity - t.storedUnits);
						if (units > 0 && t.TryAddLiquid(Props.liquid, units))
						{
							drawResource.Invoke(storage, new object[] { units * per });
							moved += units;
						}
					}
				}
			}
			status = (feedNet ? "RMFlow_AdapterFeeding" : "RMFlow_AdapterDrawing").Translate(Props.liquid.label);
		}

		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			foreach (Gizmo g in base.CompGetGizmosExtra())
			{
				yield return g;
			}
			yield return new Command_Toggle
			{
				defaultLabel = feedNet ? "RMFlow_AdapterModeFeed".Translate() : "RMFlow_AdapterModeDraw".Translate(),
				defaultDesc = "RMFlow_AdapterModeDesc".Translate(),
				icon = TexCommand.ForbidOff,
				isActive = () => feedNet,
				toggleAction = () => feedNet = !feedNet
			};
		}

		public override string CompInspectStringExtra()
		{
			return status + "\n" + "RMFlow_AdapterMoved".Translate(moved);
		}
	}
}
