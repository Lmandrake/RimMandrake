using System.Collections.Generic;
using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_DOOR_FAMILY_1 — the owner's two stuffable canal doors (2026-09-17: "I'd be happy if
	/// we just had Sluice and SecurityGrateDoor and allowed them to be stuffably made too"). Stuff
	/// decides armour, hit points and whether it burns; nothing here hardcodes a material ladder.
	///
	///   • FLOWWORKS_SLUICE_TWO_DOORS_1 (owner 2026-10-06, typed): "There are sealed sluice gates
	///     (standard) and the ones made of metal grates that always allow liquid (this is just a gate,
	///     not a sluice gate then)." A SHUT sluice seals its cell: the depth engine moves no liquid into
	///     or out of it (RM_FlowKernel.sealedCell, fed by SealsLiquid) and the legacy flood walk refuses
	///     it. Lifted, it passes. The grate passes liquid shut or open.
	///   • SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS (owner 2026-10-24): "Needing a colonist to 'walk' through a sluice gate
	///     to re-open it makes no sense. A colonist should be able to open/close a sluice gate while standing 'next' to it
	///     and above or below without walking down to it. And there should be a debug/god-mode click button to force open
	///     or closed. ... Sluice gates do not open by sliding left/right, they slide 'up' to allow the water through. ...
	///     When closed, it is not traversible. When open it is." So the sluice is an operated gate, not a door anyone
	///     walks open: no pawn opens it by walking at it (RM_PitTrapMath.FlowDoorOpens); the player's button orders a lift
	///     or a lower (designation RM_OperateGate) and a colonist works it from any square touching it
	///     (WorkGiver_RM_OperateGate); lifted, it is held open and every pawn passes. God mode adds instant force buttons.
	///     This replaces the old "people and big creatures force a sluice" rule and its setting.
	///   • The grate holds a real prisoner exactly like a vanilla door: that is why it exists. Neither opens for a pawn
	///     held in a superdeep pit (setting flowDoorsSealedFromPitEnabled): the pit spec §4 door rule.
	///   • Both draw as a fixed frame and a panel that slides straight UP (GRATE_DOOR_REBUILD_LIFTS_LIKE_THE_SLUICE, owner:
	///     "it would still make more sense for them to slide 'up'"), never two leaves sliding apart.
	///   • Ruling #18 (owner card, 2026-10-11): both may be PLACED on a wet canal cell (RM_Patch_FlowDoorOnWetCanal).
	///     A blueprint or frame on a dry cut also survives the cut flooding (the same terrain verdict). The half-built
	///     frame is not a door: it seals nothing (SealsLiquid reads only a finished Building_RM_FlowDoor), so liquid runs
	///     through the frame cell until the door is finished; then a shut sluice seals it.
	/// The verdicts are RM_PitTrapMath.FlowDoorOpens and GateLiftOffset (Verse-free, covered by the C# selftest).
	/// </summary>
	public class RM_FlowDoorExtension : DefModExtension
	{
		/// <summary>True for the sluice: an operated gate (lifted and lowered by a colonist beside it), and a shut one seals
		/// liquid. False for the grate: a door.</summary>
		public bool isSluice;

		/// <summary>How far, in cells, the panel rises fully open (Tools/fw_gate_lift.py solves it against the art).</summary>
		public float liftCells = 0.5f;
	}

	public class Building_RM_FlowDoor : Building_Door
	{
		/// <summary>SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS: the state the player ordered (lifted = true); a colonist carries
		/// it out. Equal to HoldOpen when nothing is pending. A sluice's lifted state IS vanilla's hold-open (scribed by
		/// Building_Door): held open, FreePassage is true for every pawn; let go, the gate closes as soon as its square is clear.</summary>
		public bool wantOpen;

		private Graphic frameGraphic;
		private Graphic panelGraphic;
		private Color layerColor;
		private Color layerColorTwo;
		private int layersState;   // 0 unchecked, 1 both layer textures present, -1 missing (draw the def's graphic)

		public bool IsSluice => RM_FlowDoorRules.IsSluice(def);

		public float LiftCells => def.GetModExtension<RM_FlowDoorExtension>()?.liftCells ?? 0.5f;

		public override bool PawnCanOpen(Pawn p)
		{
			return RM_FlowDoorRules.CanOpen(this, p, base.PawnCanOpen(p));
		}

		/// <summary>The one writer of the gate's state: the colonist's job, the god-mode buttons and the bridge. Open = held
		/// open (vanilla's hold-open) and opening; shut = let go and closing now, or as soon as nothing stands in it (vanilla's
		/// Tick retries a blocked close every tick).</summary>
		public void SetGateOpen(bool open)
		{
			wantOpen = open;
			ClearOrder();
			holdOpenInt = open;
			if (!Spawned)
			{
				openInt = open;
				return;
			}
			if (open)
			{
				DoorOpen();
			}
			else if (openInt && !DoorTryClose())
			{
				ticksUntilClose = 1;
			}
			Map.reachability.ClearCache();
		}

		/// <summary>The player's order: the gate should end lifted (<paramref name="toOpen"/>) or down. Adds (or, when it
		/// already is in that state, removes) the operate designation; the state changes only when a colonist works it.</summary>
		public void Order(bool toOpen)
		{
			wantOpen = toOpen;
			if (wantOpen == HoldOpen)
			{
				ClearOrder();
				return;
			}
			DesignationDef d = RimMandrakeFlowWorks_DefOf.RM_OperateGate;
			if (Spawned && d != null && Map.designationManager.DesignationOn(this, d) == null)
			{
				Map.designationManager.AddDesignation(new Designation(this, d));
			}
		}

		private void ClearOrder()
		{
			DesignationDef d = RimMandrakeFlowWorks_DefOf.RM_OperateGate;
			Designation des = Spawned && d != null ? Map.designationManager.DesignationOn(this, d) : null;
			if (des != null)
			{
				Map.designationManager.RemoveDesignation(des);
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref wantOpen, "rmGateWantOpen", holdOpenInt);   // after base: an old save orders nothing
		}

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (!respawningAfterLoad)
			{
				wantOpen = holdOpenInt;
			}
		}

		public override IEnumerable<Gizmo> GetGizmos()
		{
			bool sluice = IsSluice;
			foreach (Gizmo g in base.GetGizmos())
			{
				// A sluice is lifted by a colonist, not held open from the menu: vanilla's hold-open toggle goes.
				if (sluice && g is Command_Toggle t && t.icon == TexCommand.HoldOpen)
				{
					continue;
				}
				yield return g;
			}
			if (sluice && Faction == Faction.OfPlayer)
			{
				yield return new Command_Toggle
				{
					defaultLabel = (wantOpen ? "RMFlow_GateLifted" : "RMFlow_GateLowered").Translate().ToString()
						+ (wantOpen != HoldOpen ? " " + "RMFlow_LadderOrdered".Translate().ToString() : ""),
					defaultDesc = "RMFlow_GateToggleDesc".Translate(),
					icon = TexCommand.HoldOpen,
					hotKey = KeyBindingDefOf.Misc3,
					isActive = () => wantOpen,
					toggleAction = () => Order(!wantOpen),
				};
			}
			if (DebugSettings.godMode)
			{
				yield return new Command_Action
				{
					defaultLabel = "RMFlow_GateForceOpen".Translate(),
					defaultDesc = "RMFlow_GateForceDesc".Translate(),
					icon = TexCommand.HoldOpen,
					action = () => SetGateOpen(true),
				};
				yield return new Command_Action
				{
					defaultLabel = "RMFlow_GateForceClose".Translate(),
					defaultDesc = "RMFlow_GateForceDesc".Translate(),
					icon = TexCommand.HoldOpen,
					action = () => SetGateOpen(false),
				};
			}
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			if (!IsSluice)
			{
				return s;
			}
			string line = (HoldOpen ? "RMFlow_GateLiftedInspect" : "RMFlow_GateLoweredInspect").Translate().ToString();
			if (wantOpen != HoldOpen)
			{
				line += " " + (wantOpen ? "RMFlow_GateLiftOrdered" : "RMFlow_GateLowerOrdered").Translate().ToString();
			}
			return s.NullOrEmpty() ? line : s + "\n" + line;
		}

		/// <summary>GRATE_DOOR_REBUILD_LIFTS_LIKE_THE_SLUICE / SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS: draw the fixed FRAME at
		/// the cell and the PANEL behind it, raised straight up by RM_PitTrapMath.GateLiftOffset(liftCells, OpenPct), for
		/// both facings. The art is upright and unrotated in both (FLOWDOOR_EW_PERSPECTIVE, owner 2026-10-18: the side view
		/// is the def's _east drawing, as Graphic_Multi's own side views draw). The layers are the def's texPath + "_Frame" /
		/// "_Panel" (cut from the gate art by Tools/fw_gate_lift.py); if either is missing the def's graphic draws as a
		/// vanilla door, so a missing texture never draws pink.</summary>
		protected override void DrawAt(Vector3 drawLoc, bool flip = false)
		{
			DoorPreDraw();
			if (!EnsureLayers())
			{
				base.DrawAt(drawLoc, flip);
				return;
			}
			RM_PitTrapMath.GateLiftOffset(LiftCells, OpenPct, out float dx, out float dz);
			float alt = AltitudeLayer.DoorMoveable.AltitudeFor();
			Vector3 scale = new Vector3(def.size.x, 1f, def.size.z);
			Vector3 panelPos = drawLoc;
			panelPos.y = alt;
			panelPos.x += dx;
			panelPos.z += dz;
			UnityEngine.Graphics.DrawMesh(panelGraphic.MeshAt(Rotation), Matrix4x4.TRS(panelPos, Quaternion.identity, scale),
				panelGraphic.MatAt(Rotation, this), 0);
			Vector3 framePos = drawLoc;
			framePos.y = alt + Altitudes.AltInc * 0.5f;
			UnityEngine.Graphics.DrawMesh(frameGraphic.MeshAt(Rotation), Matrix4x4.TRS(framePos, Quaternion.identity, scale),
				frameGraphic.MatAt(Rotation, this), 0);
			Graphic.ShadowGraphic?.DrawWorker(framePos, Rotation, def, this, 0f);
			Comps_PostDraw();
		}

		/// <summary>Resolves the two layer graphics in the door's stuff colour (re-resolved when the colour changes).</summary>
		private bool EnsureLayers()
		{
			GraphicData gd = def.graphicData;
			if (layersState == 0)
			{
				string path = gd?.texPath;
				layersState = path != null && gd.graphicClass == typeof(Graphic_Multi)
					&& ContentFinder<Texture2D>.Get(path + "_Frame_south", false) != null
					&& ContentFinder<Texture2D>.Get(path + "_Panel_south", false) != null ? 1 : -1;
			}
			if (layersState < 0)
			{
				return false;
			}
			Color c = DrawColor;
			Color c2 = DrawColorTwo;
			if (frameGraphic == null || c != layerColor || c2 != layerColorTwo)
			{
				Shader shader = gd.shaderType != null ? gd.shaderType.Shader : ShaderDatabase.Cutout;
				frameGraphic = GraphicDatabase.Get<Graphic_Multi>(gd.texPath + "_Frame", shader, gd.drawSize, c, c2);
				panelGraphic = GraphicDatabase.Get<Graphic_Multi>(gd.texPath + "_Panel", shader, gd.drawSize, c, c2);
				layerColor = c;
				layerColorTwo = c2;
			}
			return true;
		}
	}

	/// <summary>SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS: the colonist half of the gate button's order. Offers a sluice only
	/// with a pending order; the pawn stands on any square touching the gate (the bank above it or the canal below it), never
	/// in it. Only designated gates are scanned: nobody works a gate unordered.</summary>
	public class WorkGiver_RM_OperateGate : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.Touch;

		public override Danger MaxPathDanger(Pawn pawn)
		{
			return Danger.Deadly;
		}

		public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
		{
			DesignationDef d = RimMandrakeFlowWorks_DefOf.RM_OperateGate;
			if (d == null)
			{
				yield break;
			}
			foreach (Designation des in pawn.Map.designationManager.SpawnedDesignationsOfDef(d))
			{
				yield return des.target.Thing;
			}
		}

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			DesignationDef d = RimMandrakeFlowWorks_DefOf.RM_OperateGate;
			return d == null || !pawn.Map.designationManager.AnySpawnedDesignationOfDef(d);
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			if (!(t is Building_RM_FlowDoor gate) || !gate.IsSluice || gate.wantOpen == gate.HoldOpen
				|| pawn.Map.designationManager.DesignationOn(t, RimMandrakeFlowWorks_DefOf.RM_OperateGate) == null)
			{
				return false;
			}
			return !t.IsForbidden(pawn) && pawn.CanReserve(t, 1, -1, null, forced);
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			return JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_OperateGateJob, t);
		}
	}

	/// <summary>SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS: walk to a square touching the gate, work the winch a moment, then
	/// lift or lower it as ordered.</summary>
	public class JobDriver_RM_OperateGate : JobDriver
	{
		private Building_RM_FlowDoor Gate => job.targetA.Thing as Building_RM_FlowDoor;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			this.FailOn(() => Gate == null || Gate.wantOpen == Gate.HoldOpen
				|| Map.designationManager.DesignationOn(job.targetA.Thing, RimMandrakeFlowWorks_DefOf.RM_OperateGate) == null);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
			yield return Toils_General.Wait(90, TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A);
			Toil work = ToilMaker.MakeToil("RM_OperateGate");
			work.initAction = () =>
			{
				Building_RM_FlowDoor gate = Gate;
				if (gate == null)
				{
					EndJobWith(JobCondition.Incompletable);
					return;
				}
				gate.SetGateOpen(gate.wantOpen);
			};
			work.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return work;
		}
	}

	/// <summary>Ruling #18: GenConstruct.CanBuildOnTerrain is the one terrain gate for placing a blueprint, for
	/// TerrainGrid.DoTerrainChangedEffects cancelling a blueprint or frame whose cell changed, and for spawning a building.
	/// A flow door on a dug cell holding liquid passes it (RM_PitTrapMath.FlowDoorStandsOn). Early-outs on every
	/// already-allowed call and every non-door def, so map generation pays one bool test.</summary>
	[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanBuildOnTerrain))]
	[RimMandrake.Shared.PatchFeature("Sluices, grates, ladders, walls and pillars stand in flooded cuts")]
	public static class RM_Patch_FlowDoorOnWetCanal
	{
		public static void Postfix(ref bool __result, BuildableDef entDef, IntVec3 c, Map map, Rot4 rot, Thing thingToIgnore, ThingDef stuffDef)
		{
			if (__result || map == null || !(entDef is ThingDef td))
			{
				return;
			}
			bool door = RM_FlowDoorRules.IsFlowDoorDef(td) || StandsInWetPit(td);
			bool standing = !door && RimMandrakeFlowWorksSettings.buildInDugWaterEnabled && StandsInWater(td);
			if (!door && !standing)
			{
				return;
			}
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null)
			{
				return;
			}
			TerrainAffordanceDef need = td.GetTerrainAffordanceNeed(stuffDef);
			CellRect rect = GenAdj.OccupiedRect(c, rot, td.Size);
			foreach (IntVec3 cell in rect)
			{
				if (!cell.InBounds(map) || HasTerrainOrder(cell, map, thingToIgnore))
				{
					return;
				}
				if (need != null && cell.GetAffordances(map).Contains(need))
				{
					continue;   // a footprint cell vanilla's own affordance already carries (a part on the bank, part in the cut)
				}
				int dug = eng.ExcavatedDepthAt(cell), fill = eng.FillAt(cell);
				if (door ? !RM_PitTrapMath.FlowDoorStandsOn(false, true, dug, fill)
					: !RM_PitTrapMath.StandsInDugWater(false, true, true, dug, fill))
				{
					return;
				}
			}
			__result = true;
		}

		/// <summary>WATERED_PIT_FIX_NO_WAY_IN — the pit's own way out stands in its water too: every ladder
		/// (RM_LadderUtility.IsLadderDef) and the pit ramp. Owner 2026-10-24, of a 1.5 m pit holding 1.5 m of water: "I can't
		/// place any ramp or ladder within the pit. I should be able to build in that pit just like normal despite the water."
		/// The wet rungs of the water ladder (vanilla WaterShallowBase family) lack the Light affordance BuildingBase asks for.</summary>
		public static bool StandsInWetPit(ThingDef td)
		{
			return td != null && (RM_LadderUtility.IsLadderDef(td)
				|| (td.thingClass != null && typeof(RM_Building_PitRamp).IsAssignableFrom(td.thingClass)));
		}

		/// <summary>DEEP_WATER_BUILD_REFUSED_BY_LIGHT_AFFORDANCE: the structures that stand in a flooded cut
		/// (RM_PitTrapMath.StandsInWater decides; this reads the def). Vanilla's column is matched by defName.
		/// A suspension bridge part is never in this set: RM_Patch_SuspensionAffordance owns it (and refuses an anchor on a wet
		/// ledge on purpose), so a second postfix here must not overrule it.</summary>
		public static bool StandsInWater(ThingDef td)
		{
			return td != null && td.category == ThingCategory.Building && !td.HasModExtension<Pits.RM_SuspensionExtension>()
				&& RM_PitTrapMath.StandsInWater(td.IsWall, td.IsFence, td.defName == "Column", td.HasModExtension<RM_StandsInWaterExtension>());
		}

		/// <summary>A floor blueprint or frame under the door: any such order keeps the refusal (stricter than vanilla, which
		/// refuses only a floor lacking the door's affordance; a floor cannot be ordered on a wet canal cell anyway). Only the
		/// missing Light of the wet cell itself is overridden.</summary>
		private static bool HasTerrainOrder(IntVec3 cell, Map map, Thing thingToIgnore)
		{
			List<Thing> things = cell.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] != thingToIgnore && things[i].def.entityDefToBuild is TerrainDef)
				{
					return true;
				}
			}
			return false;
		}
	}

	/// <summary>DEEP_WATER_BUILD_REFUSED_BY_LIGHT_AFFORDANCE: the opt-in marker for a building that should stand in the water of
	/// a flooded cut although it is not a wall, fence, column or bridge part (another mod's pillar or pier). Add it by XML
	/// patch: <c>&lt;li Class="RimMandrake.FlowWorks.RM_StandsInWaterExtension" /&gt;</c> under the def's modExtensions.</summary>
	public class RM_StandsInWaterExtension : DefModExtension
	{
	}

	/// <summary>SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR: vanilla re-turns every 1x1 door and door blueprint each frame it draws
	/// (Building_Door.DoorPreDraw, Blueprint_Door.DrawAt) through DoorUtility.DoorRotationAt; a flow door (or its blueprint)
	/// standing on a dug cell is re-scored so its leaf spans between the canal banks (RM_FlowDoorFacingMath). Every other
	/// door pays one edifice-grid read. A frame keeps its placed rotation, as vanilla's does.</summary>
	[HarmonyPatch(typeof(DoorUtility), nameof(DoorUtility.DoorRotationAt))]
	[RimMandrake.Shared.PatchFeature("Sluices and grates turn across their canal like doors between walls")]
	public static class RM_Patch_FlowDoorFacing
	{
		private delegate int AlignQualityFn(IntVec3 c, IntVec3 offset, Map map, bool preferFences);

		/// <summary>Vanilla's private side score; null (a renamed method) leaves vanilla's verdict alone rather than throwing
		/// on every door's draw.</summary>
		private static readonly AlignQualityFn AlignQualityAgainst = Bind();

		private static AlignQualityFn Bind()
		{
			System.Reflection.MethodInfo m = AccessTools.Method(typeof(DoorUtility), "AlignQualityAgainst",
				new[] { typeof(IntVec3), typeof(IntVec3), typeof(Map), typeof(bool) });
			if (m == null)
			{
				Log.ErrorOnce("[FlowWorks] DoorUtility.AlignQualityAgainst not found: sluices and grates keep vanilla's door rotation.", 0x5F10D0);
				return null;
			}
			return AccessTools.MethodDelegate<AlignQualityFn>(m);
		}

		public static void Postfix(ref Rot4 __result, IntVec3 loc, Map map, bool preferFences)
		{
			if (AlignQualityAgainst == null || map == null || !loc.InBounds(map) || !FlowDoorStandsAt(loc, map))
			{
				return;
			}
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null || !eng.IsExcavated(loc))
			{
				return;
			}
			int e = Side(loc, IntVec3.East, map, preferFences, eng);
			int w = Side(loc, IntVec3.West, map, preferFences, eng);
			int n = Side(loc, IntVec3.North, map, preferFences, eng);
			int s = Side(loc, IntVec3.South, map, preferFences, eng);
			__result = RM_FlowDoorFacingMath.FacesNorth(e, w, n, s) ? Rot4.North : Rot4.East;
		}

		private static int Side(IntVec3 loc, IntVec3 offset, Map map, bool preferFences, RM_MapComponent_Excavation eng)
		{
			IntVec3 c = loc + offset;
			bool inBounds = c.InBounds(map);
			return RM_FlowDoorFacingMath.SideQuality(true, inBounds,
				inBounds && (eng.IsExcavated(c) || eng.IsSourceCell(c)),
				inBounds && DoorOrDoorBlueprintAt(c, map),
				AlignQualityAgainst(loc, offset, map, preferFences));
		}

		/// <summary>The flow door itself, or (no edifice yet) a flow door blueprint. Vanilla doors stop at the edifice read.</summary>
		private static bool FlowDoorStandsAt(IntVec3 loc, Map map)
		{
			Building edifice = loc.GetEdifice(map);
			if (edifice != null)
			{
				return edifice is Building_RM_FlowDoor;
			}
			List<Thing> things = loc.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Blueprint bp && RM_FlowDoorRules.IsFlowDoorDef(bp.def.entityDefToBuild as ThingDef))
				{
					return true;
				}
			}
			return false;
		}

		private static bool DoorOrDoorBlueprintAt(IntVec3 c, Map map)
		{
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				Thing t = things[i];
				if (t is Building_Door || (t is Blueprint bp && bp.def.entityDefToBuild is ThingDef td && td.IsDoor))
				{
					return true;
				}
			}
			return false;
		}
	}

	public static class RM_FlowDoorRules
	{
		/// <summary>True for the sluice and the grate defs (their thingClass), blueprint and frame excluded.</summary>
		public static bool IsFlowDoorDef(ThingDef def)
		{
			return def?.thingClass != null && typeof(Building_RM_FlowDoor).IsAssignableFrom(def.thingClass);
		}

		public static bool IsFlowDoor(Thing t)
		{
			return t is Building_RM_FlowDoor;
		}

		public static bool IsSluice(ThingDef def)
		{
			RM_FlowDoorExtension ext = def?.GetModExtension<RM_FlowDoorExtension>();
			return ext != null && ext.isSluice;
		}

		/// <summary>FLOWWORKS_SLUICE_TWO_DOORS_1: the verdict for the edifice on a cell — only a shut sluice
		/// holds liquid back. Pure on its two inputs so the selftest covers it (RM_PitTrapMath.FlowDoorSeals).</summary>
		public static bool SealsLiquid(Building edifice)
		{
			Building_RM_FlowDoor door = edifice as Building_RM_FlowDoor;
			return door != null && RM_PitTrapMath.FlowDoorSeals(IsSluice(door.def), door.Open);
		}

		/// <summary>The legacy flood walk's edifice verdict: a flow door that is not sealing, or a flow door's frame (ruling
		/// #18: the half-built frame seals nothing). Every other edifice holds liquid back.</summary>
		public static bool LetsLiquidThrough(Building edifice)
		{
			if (edifice is Frame frame)
			{
				return IsFlowDoorDef(frame.def.entityDefToBuild as ThingDef);
			}
			return IsFlowDoor(edifice) && !SealsLiquid(edifice);
		}

		public static bool CanOpen(Building_Door door, Pawn p, bool vanillaOpens)
		{
			if (p == null || door == null)
			{
				return false;
			}
			return RM_PitTrapMath.FlowDoorOpens(vanillaOpens,
				RM_SuperdeepTrap.IsHeld(p), RimMandrakeFlowWorksSettings.flowDoorsSealedFromPitEnabled,
				IsSluice(door.def));
		}

		private static Building_RM_FlowDoor DoorAt(Map map, IntVec3 c)
		{
			return map == null || !c.InBounds(map) ? null : c.GetEdifice(map) as Building_RM_FlowDoor;
		}

		/// <summary>Bridge proof (jawa/static_call): every pawn within 3 cells of the flow door at
		/// <paramref name="cell"/>, and whether the door would open for it walking up to it shut (a sluice: never).
		/// "DOOR RM_Sluice stuff WoodLog lifted=False want=False | Human123 SHUT held=False w=1 | Muffalo9 SHUT ..." (ThingIDs,
		/// as jawa/spawn_pawn returns them).</summary>
		public static string ProofOpen(Map map, IntVec3 cell)
		{
			Building_RM_FlowDoor door = DoorAt(map, cell);
			if (door == null)
			{
				return "REFUSED: no flow door at " + cell;
			}
			StringBuilder sb = new StringBuilder();
			sb.Append("DOOR ").Append(door.def.defName).Append(" stuff ").Append(door.Stuff?.defName ?? "none")
				.Append(" lifted=").Append(door.HoldOpen).Append(" want=").Append(door.wantOpen);
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (p.Position.DistanceTo(cell) > 3.01f)
				{
					continue;
				}
				sb.Append(" | ").Append(p.ThingID)
					.Append(door.PawnCanOpen(p) ? " OPEN" : " SHUT")
					.Append(" held=").Append(RM_SuperdeepTrap.IsHeld(p))
					.Append(" w=").Append(RM_SuperdeepTrap.RequiredWidth(p));
			}
			return sb.ToString();
		}

		/// <summary>Bridge tool (jawa/static_call): set the flow door at <paramref name="cell"/> lifted (open) or down, as the
		/// god-mode buttons do. "DOOR RM_Sluice lifted=True open=True".</summary>
		public static string ProofSetGate(Map map, IntVec3 cell, bool open)
		{
			Building_RM_FlowDoor door = DoorAt(map, cell);
			if (door == null)
			{
				return "REFUSED: no flow door at " + cell;
			}
			door.SetGateOpen(open);
			return "DOOR " + door.def.defName + " lifted=" + door.HoldOpen + " open=" + door.Open;
		}

		/// <summary>Bridge proof (jawa/static_call): the liquid under a flow door — dug depth and
		/// fill F at the door cell, so a chain can show the level passing a CLOSED grate and stopping at a
		/// CLOSED sluice. "DOOR RM_SecurityGrateDoor open=False seals=False | depth 2 fill 1".</summary>
		public static string ProofLiquid(Map map, IntVec3 cell)
		{
			Building_RM_FlowDoor door = DoorAt(map, cell);
			if (door == null)
			{
				return "REFUSED: no flow door at " + cell;
			}
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			int depth = eng == null ? 0 : eng.DepthAt(cell);
			int fill = eng == null ? 0 : eng.FillAt(cell);
			return "DOOR " + door.def.defName + " open=" + door.Open + " seals=" + SealsLiquid(door) +
				" | depth " + depth + " fill " + fill;
		}
	}
}
