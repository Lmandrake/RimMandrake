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
		/// <summary>L1 (§3.10 G5): the fractional remainder of resourcePerUnit across the boundary, in pipe-net resource, saved and
		/// never rounded away (RM_LiquidTransfer.SettleSend / SettleTake keep tankUnits x per + stored + carry unchanged).</summary>
		public float carry;
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
			Scribe_Values.Look(ref carry, "RM_adapterCarry", 0f);
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
			if (failedClosed || !Bind())
			{
				status = "RMFlow_AdapterBroken".Translate();
				return;
			}
			float per = Props.resourcePerUnit;
			if (float.IsNaN(per) || float.IsInfinity(per) || per <= 0f || float.IsNaN(carry) || float.IsInfinity(carry))
			{
				FailClosed("resourcePerUnit " + per + ", carry " + carry);
				return;
			}
			bool broken = false;
			// L1 (§4, §3.10 G5): every unit crosses through RM_LiquidTransfer.Move. The tank leg goes first; the VE call runs last and
			// its storage is READ BACK, so a short accept puts the shortfall back into the tank and the fraction goes into carry.
			if (feedNet)
			{
				float room = Stored(amountCanAccept);
				int units = Mathf.Min(Props.unitsPerRareTick, Mathf.FloorToInt(room / per));
				// L3 (rev 2 §3.2): drawn by the draw plan (emptiest tank first, split across tanks); a short accept is put back
				// into the plan's LAST parts, so the first parts up to the units sent are the ones credited
				int take = Mathf.Min(units, RM_LiquidNet.Available(parent, Props.liquid));
				List<(Building_LiquidTank tank, int units)> plan = take > 0 ? RM_LiquidNet.DrawPlan(parent, Props.liquid, take) : null;
				if (plan != null)
				{
					LiquidDef fed = Props.liquid;
					RM_TransferLeg ve = RM_TransferLeg.Boundary(k => Stored(amountCanAccept) >= k * per - 1e-3f, k =>
					{
						float before = Stored(amountStored);
						addResource.Invoke(storage, new object[] { k * per });
						int u = RM_LiquidTransfer.SettleSend(Stored(amountStored) - before, per, k, ref carry);
						broken |= u < 0;
						return Mathf.Max(0, u);
					});
					if (RM_LiquidTransfer.Move(take, RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanProvide(k), (i, k) => plan[i].tank.TryRemoveLiquid(k), (i, k) => plan[i].tank.TryAddLiquid(fed, k)), ve, out RM_MoveOutcome mv) > 0)
					{
						foreach ((Building_LiquidTank tank, int units) p in RM_LiquidNet.Committed(plan, mv.Moved)) RM_LiquidNet.Credit(parent, p.tank, fed, p.units, RM_ConversionMath.RareTick);   // credit site: adapter feeds the pipe net
						moved += mv.Moved;
					}
				}
			}
			else
			{
				float stored = Stored(amountStored);
				int units = Mathf.Min(Props.unitsPerRareTick, Mathf.FloorToInt((stored + Mathf.Max(0f, carry)) / per));
				if (units > 0)
				{
					// L3: the room is the whole store's, and the units split across tanks by the fill plan
					units = Mathf.Min(units, RM_LiquidNet.Room(parent, Props.liquid));
					List<(Building_LiquidTank tank, int units)> plan = units > 0 ? RM_LiquidNet.FillPlan(parent, Props.liquid, units) : null;
					if (plan != null)
					{
						RM_TransferLeg ve = RM_TransferLeg.Boundary(k => Stored(amountStored) + Mathf.Max(0f, carry) >= k * per - 1e-3f, k =>
						{
							float before = Stored(amountStored);
							float ask = Mathf.Max(0f, k * per - Mathf.Max(0f, carry));
							if (ask > 0f)
							{
								drawResource.Invoke(storage, new object[] { ask });
							}
							int u = RM_LiquidTransfer.SettleTake(before - Stored(amountStored), per, k, ref carry);
							broken |= u < 0;
							return Mathf.Max(0, u);
						});
						if (RM_LiquidTransfer.Move(units, ve, RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanAccept(Props.liquid, k), (i, k) => plan[i].tank.TryAddLiquid(Props.liquid, k), (i, k) => plan[i].tank.TryRemoveLiquid(k)), out RM_MoveOutcome mv) > 0)
						{
							foreach ((Building_LiquidTank tank, int units) p in RM_LiquidNet.Committed(plan, mv.Moved)) RM_LiquidNet.Credit(parent, p.tank, Props.liquid, p.units, RM_ConversionMath.RareTick);   // credit site: adapter draws from the pipe net
							moved += mv.Moved;
						}
					}
				}
			}
			if (broken)
			{
				FailClosed("a non-finite read-back from " + storage.GetType().FullName);
				return;
			}
			status = (feedNet ? "RMFlow_AdapterFeeding" : "RMFlow_AdapterDrawing").Translate(Props.liquid.label);
		}

		/// <summary>A float property of the VE storage, read by reflection (NaN when it cannot be read: fails closed).</summary>
		private float Stored(PropertyInfo p)
		{
			try
			{
				return Convert.ToSingle(p.GetValue(storage));
			}
			catch (Exception)
			{
				return float.NaN;
			}
		}

		/// <summary>§3.10: a reflection failure or a non-finite ratio stops the adapter for the session (one red line). The Shut
		/// mode of build step L8 is not built yet, so the adapter unbinds and reads "broken" until the next load.</summary>
		private void FailClosed(string why)
		{
			Log.ErrorOnce("[FlowWorks] pipe adapter " + parent.def.defName + " stopped: " + why, parent.def.shortHash ^ 0x5A19);
			status = "RMFlow_AdapterBroken".Translate();
			failedClosed = true;
		}

		private bool failedClosed;

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
