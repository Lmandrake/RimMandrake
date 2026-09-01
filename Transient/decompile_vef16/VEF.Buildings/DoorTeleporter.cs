using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace VEF.Buildings;

[StaticConstructorOnStartup]
public class DoorTeleporter : ThingWithComps, IRenameable
{
	[HarmonyPatch(typeof(JobGiver_AIFollowPawn), "TryGiveJob")]
	public static class JobGiver_AIFollowPawn_TryGiveJob_Patch
	{
		private static Func<JobGiver_AIFollowPawn, Pawn, Pawn> GetFolloweeInfo = (Func<JobGiver_AIFollowPawn, Pawn, Pawn>)Delegate.CreateDelegate(typeof(Func<JobGiver_AIFollowPawn, Pawn, Pawn>), AccessToolsExtensions.Method(typeof(JobGiver_AIFollowPawn), "GetFollowee", (Type[])null, (Type[])null));

		public static void Postfix(JobGiver_AIFollowPawn __instance, Pawn pawn, ref Job __result)
		{
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0051: Unknown result type (might be due to invalid IL or missing references)
			//IL_0111: Unknown result type (might be due to invalid IL or missing references)
			//IL_011f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0124: Unknown result type (might be due to invalid IL or missing references)
			if (__result != null && pawn.CurJobDef == VEFDefOf.VEF_UseDoorTeleporter)
			{
				__result = JobMaker.MakeJob(VEFDefOf.VEF_UseDoorTeleporter, pawn.CurJob.targetA);
				__result.globalTarget = pawn.CurJob.globalTarget;
			}
			if (__result != null)
			{
				return;
			}
			Pawn followee = GetFolloweeInfo(__instance, pawn);
			if (followee == null || ((Thing)followee).Map == ((Thing)pawn).Map)
			{
				return;
			}
			DoorTeleporter doorTeleporter = (from x in WorldComponent_DoorTeleporterManager.Instance.DoorTeleporters
				where ((Thing)x).Map == ((Thing)pawn).Map && ReachabilityUtility.CanReach(pawn, LocalTargetInfo.op_Implicit((Thing)(object)x), (PathEndMode)1, (Danger)3, false, false, (TraverseMode)0)
				orderby IntVec3Utility.DistanceTo(((Thing)x).Position, ((Thing)pawn).Position)
				select x).FirstOrDefault();
			if (doorTeleporter != null)
			{
				DoorTeleporter doorTeleporter2 = (from x in WorldComponent_DoorTeleporterManager.Instance.DoorTeleporters
					where ((Thing)x).Map == ((Thing)followee).Map && ReachabilityUtility.CanReach(followee, LocalTargetInfo.op_Implicit((Thing)(object)x), (PathEndMode)1, (Danger)3, false, false, (TraverseMode)0)
					orderby IntVec3Utility.DistanceTo(((Thing)x).Position, ((Thing)followee).Position)
					select x).FirstOrDefault();
				if (doorTeleporter2 != null)
				{
					__result = JobMaker.MakeJob(VEFDefOf.VEF_UseDoorTeleporter, LocalTargetInfo.op_Implicit((Thing)(object)doorTeleporter));
					__result.globalTarget = GlobalTargetInfo.op_Implicit((Thing)(object)doorTeleporter2);
				}
			}
		}
	}

	public Material backgroundMat;

	public RenderTexture background1;

	public RenderTexture background2;

	public float rotation;

	public float distortAmount = 1.5f;

	public Vector2 backgroundOffset;

	public Sustainer sustainer;

	public static Dictionary<ThingDef, DoorTeleporterMaterials> doorTeleporterMaterials;

	public Dictionary<Thing, Effecter> teleportEffecters = new Dictionary<Thing, Effecter>();

	public string Name { get; set; }

	public string RenamableLabel
	{
		get
		{
			return Name ?? BaseLabel;
		}
		set
		{
			Name = value;
		}
	}

	public string BaseLabel => ((Def)((Thing)this).def).label;

	public string InspectLabel => RenamableLabel;

	static DoorTeleporter()
	{
		DoorTeleporter.doorTeleporterMaterials = new Dictionary<ThingDef, DoorTeleporterMaterials>();
		foreach (ThingDef allDef in DefDatabase<ThingDef>.AllDefs)
		{
			if (typeof(DoorTeleporter).IsAssignableFrom(allDef.thingClass))
			{
				DoorTeleporterMaterials doorTeleporterMaterials2 = (DoorTeleporter.doorTeleporterMaterials[allDef] = new DoorTeleporterMaterials());
				doorTeleporterMaterials2.Init(allDef);
			}
		}
	}

	public override void SpawnSetup(Map map, bool respawningAfterLoad)
	{
		((ThingWithComps)this).SpawnSetup(map, respawningAfterLoad);
		WorldComponent_DoorTeleporterManager.Instance.DoorTeleporters.Add(this);
		DoorTeleporterMaterials mat = doorTeleporterMaterials[((Thing)this).def];
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Expected O, but got Unknown
			//IL_0058: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Expected O, but got Unknown
			//IL_006d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0077: Expected O, but got Unknown
			background1 = new RenderTexture(((Texture)mat.backgroundTex).width, ((Texture)mat.backgroundTex).height, 0);
			background2 = new RenderTexture(((Texture)mat.backgroundTex).width, ((Texture)mat.backgroundTex).height, 0);
			backgroundMat = new Material(ShaderDatabase.TransparentPostLight);
			RecacheBackground();
		});
	}

	protected override void Tick()
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		((ThingWithComps)this).Tick();
		rotation = (rotation + 0.5f) % 360f;
		distortAmount += 0.01f;
		if (distortAmount >= 3f)
		{
			distortAmount = 1.5f;
		}
		backgroundOffset += Vector2.one * 0.001f;
		RecacheBackground();
		DoorTeleporterExtension modExtension = ((Def)((Thing)this).def).GetModExtension<DoorTeleporterExtension>();
		if (modExtension.sustainer != null)
		{
			PlaySustainer(modExtension.sustainer);
		}
	}

	protected virtual void PlaySustainer(SoundDef soundDef)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		if (sustainer == null || sustainer.Ended)
		{
			sustainer = SoundStarter.TrySpawnSustainer(soundDef, SoundInfo.op_Implicit((Thing)(object)this));
		}
		Sustainer obj = sustainer;
		if (obj != null)
		{
			obj.Maintain();
		}
	}

	public void RecacheBackground()
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		if (!((Object)(object)backgroundMat == (Object)null))
		{
			DoorTeleporterMaterials doorTeleporterMaterials = DoorTeleporter.doorTeleporterMaterials[((Thing)this).def];
			Graphics.Blit((Texture)(object)doorTeleporterMaterials.backgroundTex, background1, Vector2.one, backgroundOffset, 0, 0);
			Graphics.Blit((Texture)(object)background1, background2, doorTeleporterMaterials.maskMat);
			backgroundMat.mainTexture = (Texture)(object)background2;
		}
	}

	public override void DeSpawn(DestroyMode mode = 0)
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		Sustainer obj = sustainer;
		if (obj != null)
		{
			obj.End();
		}
		sustainer = null;
		((ThingWithComps)this).DeSpawn(mode);
		WorldComponent_DoorTeleporterManager.Instance.DoorTeleporters.Remove(this);
		Object.Destroy((Object)(object)background1);
		Object.Destroy((Object)(object)background2);
		Object.Destroy((Object)(object)backgroundMat);
	}

	public virtual void DoTeleportEffects(Thing thing, int ticksLeftThisToil, Map targetMap, ref IntVec3 targetCell, DoorTeleporter dest)
	{
	}

	public virtual void Teleport(Thing thing, Map mapTarget, IntVec3 cellTarget)
	{
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null)
		{
			Thing carriedThing = val.carryTracker.CarriedThing;
			if (carriedThing != null)
			{
				val.carryTracker.TryDropCarriedThing(((Thing)val).Position, (ThingPlaceMode)1, ref carriedThing, (Action<Thing, int>)null);
				((Entity)carriedThing).DeSpawn((DestroyMode)0);
				GenSpawn.Spawn(carriedThing, cellTarget, mapTarget, (WipeMode)0);
			}
			bool drafted = val.drafter != null && val.Drafted;
			bool num = Find.Selector.IsSelected((object)val);
			val.teleporting = true;
			val.ClearAllReservations(false);
			val.ExitMap(false, Rot4.Invalid);
			val.teleporting = false;
			GenSpawn.Spawn((Thing)(object)val, cellTarget, mapTarget, (WipeMode)0);
			if (val.drafter != null)
			{
				val.drafter.Drafted = drafted;
			}
			if (num)
			{
				Find.Selector.Select((object)val, true, true);
			}
		}
		else
		{
			((Entity)thing).DeSpawn((DestroyMode)0);
			GenSpawn.Spawn(thing, cellTarget, mapTarget, (WipeMode)0);
		}
		teleportEffecters.Remove(thing);
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		DoorTeleporterMaterials doorTeleporterMaterials = DoorTeleporter.doorTeleporterMaterials[((Thing)this).def];
		Vector3 val = default(Vector3);
		((Vector3)(ref val))._002Ector((float)((Thing)this).def.size.x, 1f, (float)((Thing)this).def.size.z);
		Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(drawLoc, Quaternion.AngleAxis(rotation, Vector3.up), val * 1.5f), doorTeleporterMaterials.MainMat, 0);
		if ((Object)(object)backgroundMat != (Object)null)
		{
			Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(drawLoc - Altitudes.AltIncVect / 2f, Quaternion.identity, val * 1.5f), backgroundMat, 0);
		}
		Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(Vector3Utility.Yto0(drawLoc) + Vector3.up * Altitudes.AltitudeFor((AltitudeLayer)28), Quaternion.identity, val * distortAmount * 2f), doorTeleporterMaterials.DistortionMat, 0);
	}

	public override IEnumerable<Gizmo> GetGizmos()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		foreach (Gizmo item2 in GetDoorTeleporterGismoz())
		{
			yield return item2;
		}
	}

	public virtual IEnumerable<Gizmo> GetDoorTeleporterGismoz()
	{
		DoorTeleporterExtension extension = ((Def)((Thing)this).def).GetModExtension<DoorTeleporterExtension>();
		DoorTeleporterMaterials doorMaterials = doorTeleporterMaterials[((Thing)this).def];
		if ((Object)(object)doorMaterials.DestroyIcon != (Object)null)
		{
			yield return (Gizmo)new Command_Action
			{
				defaultLabel = TaggedString.op_Implicit(Translator.Translate(extension.destroyLabelKey)),
				defaultDesc = TaggedString.op_Implicit(Translator.Translate(extension.destroyDescKey)),
				icon = (Texture)(object)doorMaterials.DestroyIcon,
				action = delegate
				{
					((Thing)this).Destroy((DestroyMode)0);
				}
			};
		}
		if ((Object)(object)doorMaterials.RenameIcon != (Object)null)
		{
			yield return (Gizmo)new Command_Action
			{
				defaultLabel = TaggedString.op_Implicit(Translator.Translate(extension.renameLabelKey)),
				defaultDesc = TaggedString.op_Implicit(Translator.Translate(extension.renameDescKey)),
				icon = (Texture)(object)doorMaterials.RenameIcon,
				action = delegate
				{
					Find.WindowStack.Add((Window)(object)new Dialog_RenameDoorTeleporter(this));
				}
			};
		}
	}

	public override string GetInspectString()
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		string inspectString = ((ThingWithComps)this).GetInspectString();
		StringBuilder obj = (inspectString.Any() ? new StringBuilder(inspectString + "\n") : new StringBuilder());
		obj.AppendLine(TaggedString.op_Implicit(Translator.Translate("VEF.Name") + ": " + Name));
		return GenText.TrimEndNewlines(obj.ToString());
	}

	public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Pawn selPawn)
	{
		foreach (FloatMenuOption item in _003C_003En__1(selPawn))
		{
			yield return item;
		}
		if (!ReachabilityUtility.CanReach(selPawn, LocalTargetInfo.op_Implicit((Thing)(object)this), (PathEndMode)1, (Danger)3, false, false, (TraverseMode)0))
		{
			TaggedString val = Translator.Translate("NoPath");
			yield return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CannotUseReason", NamedArgument.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst()))), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			yield break;
		}
		foreach (DoorTeleporter doorTeleporter in GenCollection.Except<DoorTeleporter>((IEnumerable<DoorTeleporter>)WorldComponent_DoorTeleporterManager.Instance.DoorTeleporters, this))
		{
			yield return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.TeleportTo", NamedArgument.op_Implicit(doorTeleporter.Name))), (Action)delegate
			{
				//IL_0010: Unknown result type (might be due to invalid IL or missing references)
				//IL_0022: Unknown result type (might be due to invalid IL or missing references)
				//IL_0027: Unknown result type (might be due to invalid IL or missing references)
				//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
				//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
				//IL_00de: Unknown result type (might be due to invalid IL or missing references)
				Job val2 = JobMaker.MakeJob(VEFDefOf.VEF_UseDoorTeleporter, LocalTargetInfo.op_Implicit((Thing)(object)this));
				val2.globalTarget = GlobalTargetInfo.op_Implicit((Thing)(object)doorTeleporter);
				selPawn.jobs.StartJob(val2, (JobCondition)16, (ThinkNode)null, false, true, (ThinkTreeDef)null, (JobTag?)null, false, true, (bool?)null, false, true, false);
				foreach (Pawn item2 in ((Thing)selPawn).Map.mapPawns.AllPawnsSpawned)
				{
					if (item2.CurJobDef == JobDefOf.FollowClose && ((LocalTargetInfo)(ref item2.CurJob.targetA)).Pawn == selPawn)
					{
						Job val3 = JobMaker.MakeJob(VEFDefOf.VEF_UseDoorTeleporter, LocalTargetInfo.op_Implicit((Thing)(object)this));
						val3.globalTarget = GlobalTargetInfo.op_Implicit((Thing)(object)doorTeleporter);
						item2.jobs.TryTakeOrderedJob(val3, (JobTag?)(JobTag)0, false);
					}
				}
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
		}
	}

	public override void ExposeData()
	{
		((ThingWithComps)this).ExposeData();
		string name = Name;
		Scribe_Values.Look<string>(ref name, "name", (string)null, false);
		Name = name;
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((ThingWithComps)this).GetGizmos();
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<FloatMenuOption> _003C_003En__1(Pawn selPawn)
	{
		return ((ThingWithComps)this).GetFloatMenuOptions(selPawn);
	}
}
