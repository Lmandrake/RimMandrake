using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace Outposts;

public class Outpost : MapParent, IRenameable
{
	[CompilerGenerated]
	private sealed class _003C_003Ec__DisplayClass72_0
	{
		public Pawn p;

		public Outpost _003C_003E4__this;

		internal void _003CGetGizmos_003Eb__4()
		{
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			CaravanMaker.MakeCaravan(Gen.YieldSingle<Pawn>(_003C_003E4__this.RemovePawn(p)), ((Thing)p).Faction, ((WorldObject)_003C_003E4__this).Tile, true);
		}
	}

	[CompilerGenerated]
	private sealed class _003C_003Ec__DisplayClass72_1
	{
		public Map map;

		public Outpost _003C_003E4__this;

		internal void _003CGetGizmos_003Eb__8()
		{
			_003C_003E4__this.deliveryMap = map;
		}
	}

	[CompilerGenerated]
	private sealed class _003CGetGizmos_003Ed__72 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Gizmo _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public Outpost _003C_003E4__this;

		private IEnumerator<Gizmo> _003C_003E7__wrap1;

		Gizmo IEnumerator<Gizmo>.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		object IEnumerator.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		[DebuggerHidden]
		public _003CGetGizmos_003Ed__72(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			int num = _003C_003E1__state;
			if (num == -3 || num == 1)
			{
				try
				{
				}
				finally
				{
					_003C_003Em__Finally1();
				}
			}
			_003C_003E7__wrap1 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			//IL_030a: Unknown result type (might be due to invalid IL or missing references)
			//IL_030f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0321: Unknown result type (might be due to invalid IL or missing references)
			//IL_0331: Expected O, but got Unknown
			//IL_0347: Unknown result type (might be due to invalid IL or missing references)
			//IL_034c: Unknown result type (might be due to invalid IL or missing references)
			//IL_035e: Unknown result type (might be due to invalid IL or missing references)
			//IL_036e: Expected O, but got Unknown
			//IL_0185: Unknown result type (might be due to invalid IL or missing references)
			//IL_018a: Unknown result type (might be due to invalid IL or missing references)
			//IL_019c: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a2: Unknown result type (might be due to invalid IL or missing references)
			//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
			//IL_01b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_01c6: Unknown result type (might be due to invalid IL or missing references)
			//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
			//IL_01e5: Unknown result type (might be due to invalid IL or missing references)
			//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ff: Expected O, but got Unknown
			//IL_03d2: Unknown result type (might be due to invalid IL or missing references)
			//IL_03d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_03e2: Unknown result type (might be due to invalid IL or missing references)
			//IL_03e8: Unknown result type (might be due to invalid IL or missing references)
			//IL_03f7: Unknown result type (might be due to invalid IL or missing references)
			//IL_040e: Expected O, but got Unknown
			//IL_038c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0391: Unknown result type (might be due to invalid IL or missing references)
			//IL_03a3: Unknown result type (might be due to invalid IL or missing references)
			//IL_03ae: Unknown result type (might be due to invalid IL or missing references)
			//IL_03be: Expected O, but got Unknown
			//IL_02c2: Unknown result type (might be due to invalid IL or missing references)
			//IL_02c7: Unknown result type (might be due to invalid IL or missing references)
			//IL_02d9: Unknown result type (might be due to invalid IL or missing references)
			//IL_02e4: Unknown result type (might be due to invalid IL or missing references)
			//IL_02f4: Expected O, but got Unknown
			//IL_0235: Unknown result type (might be due to invalid IL or missing references)
			//IL_023a: Unknown result type (might be due to invalid IL or missing references)
			//IL_024c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0252: Unknown result type (might be due to invalid IL or missing references)
			//IL_0261: Unknown result type (might be due to invalid IL or missing references)
			//IL_011e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0123: Unknown result type (might be due to invalid IL or missing references)
			//IL_0135: Unknown result type (might be due to invalid IL or missing references)
			//IL_013b: Unknown result type (might be due to invalid IL or missing references)
			//IL_014a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0150: Unknown result type (might be due to invalid IL or missing references)
			//IL_015f: Unknown result type (might be due to invalid IL or missing references)
			//IL_016f: Expected O, but got Unknown
			//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f6: Unknown result type (might be due to invalid IL or missing references)
			//IL_0106: Expected O, but got Unknown
			//IL_027e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0283: Unknown result type (might be due to invalid IL or missing references)
			//IL_0292: Unknown result type (might be due to invalid IL or missing references)
			//IL_02a2: Expected O, but got Unknown
			try
			{
				int num = _003C_003E1__state;
				Outpost CS_0024_003C_003E8__locals29 = _003C_003E4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					_003C_003E7__wrap1 = CS_0024_003C_003E8__locals29._003C_003En__0().GetEnumerator();
					_003C_003E1__state = -3;
					goto IL_0092;
				case 1:
					_003C_003E1__state = -3;
					goto IL_0092;
				case 2:
					_003C_003E1__state = -1;
					goto IL_0184;
				case 3:
					_003C_003E1__state = -1;
					goto IL_0184;
				case 4:
					_003C_003E1__state = -1;
					if (OutpostsMod.Settings.DeliveryMethod != DeliveryMethod.Store && !GenText.NullOrEmpty(CS_0024_003C_003E8__locals29.ProductionString()))
					{
						Command_Action val2 = new Command_Action
						{
							action = delegate
							{
								//IL_008a: Unknown result type (might be due to invalid IL or missing references)
								//IL_0094: Expected O, but got Unknown
								//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
								//IL_00b8: Expected O, but got Unknown
								List<FloatMenuOption> list = new List<FloatMenuOption>();
								using (IEnumerator<Map> enumerator2 = (from m in Find.Maps
									where m.IsPlayerHome
									orderby Find.WorldGrid.ApproxDistanceInTiles(((WorldObject)m.Parent).Tile, ((WorldObject)CS_0024_003C_003E8__locals29).Tile)
									select m).GetEnumerator())
								{
									while (enumerator2.MoveNext())
									{
										_003C_003Ec__DisplayClass72_1 CS_0024_003C_003E8__locals11 = new _003C_003Ec__DisplayClass72_1
										{
											_003C_003E4__this = CS_0024_003C_003E8__locals29,
											map = enumerator2.Current
										};
										list.Add(new FloatMenuOption(((WorldObject)CS_0024_003C_003E8__locals11.map.Parent).LabelCap, (Action)delegate
										{
											CS_0024_003C_003E8__locals11._003C_003E4__this.deliveryMap = CS_0024_003C_003E8__locals11.map;
										}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
									}
								}
								Find.WindowStack.Add((Window)new FloatMenu(list));
							},
							defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.DeliveryColony.Label"))
						};
						Map deliveryMap = CS_0024_003C_003E8__locals29.deliveryMap;
						((Command)val2).defaultDesc = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.Commands.DeliveryColony.Desc", NamedArgument.op_Implicit((deliveryMap != null) ? ((WorldObject)deliveryMap.Parent).LabelCap : null)));
						((Command)val2).icon = (Texture)(object)SettleUtility.SettleCommandTex;
						_003C_003E2__current = (Gizmo)val2;
						_003C_003E1__state = 5;
						return true;
					}
					goto IL_02b7;
				case 5:
					_003C_003E1__state = -1;
					goto IL_02b7;
				case 6:
					_003C_003E1__state = -1;
					_003C_003E2__current = (Gizmo)new Command_Action
					{
						action = delegate
						{
							//IL_0038: Unknown result type (might be due to invalid IL or missing references)
							DamageInfo val = default(DamageInfo);
							((DamageInfo)(ref val))._002Ector(DamageDefOf.Crush, 10f, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false);
							((DamageInfo)(ref val)).SetIgnoreInstantKillProtection(true);
							((Thing)GenCollection.RandomElement<Pawn>((IEnumerable<Pawn>)CS_0024_003C_003E8__locals29.occupants)).TakeDamage(val);
						},
						defaultLabel = "Dev: Random pawn takes 10 damage"
					};
					_003C_003E1__state = 7;
					return true;
				case 7:
					_003C_003E1__state = -1;
					_003C_003E2__current = (Gizmo)new Command_Action
					{
						action = delegate
						{
							foreach (Pawn occupant in CS_0024_003C_003E8__locals29.occupants)
							{
								((Need)occupant.needs.food).CurLevel = 0f;
							}
						},
						defaultLabel = "Dev: All pawns 0% food"
					};
					_003C_003E1__state = 8;
					return true;
				case 8:
					_003C_003E1__state = -1;
					if (CS_0024_003C_003E8__locals29.Packing)
					{
						_003C_003E2__current = (Gizmo)new Command_Action
						{
							action = delegate
							{
								CS_0024_003C_003E8__locals29.ticksTillPacked = 1;
							},
							defaultLabel = "Dev: Pack now",
							defaultDesc = "Reduce ticksTillPacked to 1"
						};
						_003C_003E1__state = 9;
						return true;
					}
					goto IL_03d1;
				case 9:
					_003C_003E1__state = -1;
					goto IL_03d1;
				case 10:
					{
						_003C_003E1__state = -1;
						return false;
					}
					IL_0184:
					_003C_003E2__current = (Gizmo)new Command_Action
					{
						action = delegate
						{
							//IL_0021: Unknown result type (might be due to invalid IL or missing references)
							//IL_002b: Expected O, but got Unknown
							Find.WindowStack.Add((Window)new FloatMenu(((IEnumerable<Pawn>)CS_0024_003C_003E8__locals29.occupants).Select((Func<Pawn, FloatMenuOption>)delegate(Pawn p)
							{
								//IL_0057: Unknown result type (might be due to invalid IL or missing references)
								//IL_005d: Expected O, but got Unknown
								_003C_003Ec__DisplayClass72_0 CS_0024_003C_003E8__locals21 = new _003C_003Ec__DisplayClass72_0
								{
									_003C_003E4__this = CS_0024_003C_003E8__locals29,
									p = p
								};
								Name name = CS_0024_003C_003E8__locals21.p.Name;
								return new FloatMenuOption(GenText.CapitalizeFirst(((name != null) ? name.ToStringFull : null) ?? ((Entity)CS_0024_003C_003E8__locals21.p).Label), (Action)delegate
								{
									//IL_0027: Unknown result type (might be due to invalid IL or missing references)
									CaravanMaker.MakeCaravan(Gen.YieldSingle<Pawn>(CS_0024_003C_003E8__locals21._003C_003E4__this.RemovePawn(CS_0024_003C_003E8__locals21.p)), ((Thing)CS_0024_003C_003E8__locals21.p).Faction, ((WorldObject)CS_0024_003C_003E8__locals21._003C_003E4__this).Tile, true);
								}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
							}).ToList()));
						},
						defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Remove.Label")),
						defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Remove.Desc")),
						icon = (Texture)(object)TexOutposts.RemoveTex,
						Disabled = (CS_0024_003C_003E8__locals29.occupants.Count == 1),
						disabledReason = TaggedString.op_Implicit(Translator.Translate("Outposts.Command.Remove.Only1"))
					};
					_003C_003E1__state = 4;
					return true;
					IL_0092:
					if (_003C_003E7__wrap1.MoveNext())
					{
						Gizmo current = _003C_003E7__wrap1.Current;
						_003C_003E2__current = current;
						_003C_003E1__state = 1;
						return true;
					}
					_003C_003Em__Finally1();
					_003C_003E7__wrap1 = null;
					if (CS_0024_003C_003E8__locals29.Packing)
					{
						_003C_003E2__current = (Gizmo)new Command_Action
						{
							action = delegate
							{
								CS_0024_003C_003E8__locals29.ticksTillPacked = -1;
							},
							defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.StopPack.Label")),
							defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.StopPack.Desc")),
							icon = (Texture)(object)TexOutposts.StopPackTex
						};
						_003C_003E1__state = 2;
						return true;
					}
					_003C_003E2__current = (Gizmo)new Command_Action
					{
						action = delegate
						{
							CS_0024_003C_003E8__locals29.ticksTillPacked = Mathf.RoundToInt((float)CS_0024_003C_003E8__locals29.TicksToPack * OutpostsMod.Settings.TimeMultiplier);
						},
						defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Pack.Label")),
						defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Pack.Desc")),
						icon = (Texture)(object)TexOutposts.PackTex
					};
					_003C_003E1__state = 3;
					return true;
					IL_02b7:
					if (DebugSettings.ShowDevGizmos)
					{
						_003C_003E2__current = (Gizmo)new Command_Action
						{
							action = delegate
							{
								CS_0024_003C_003E8__locals29.ticksTillProduction = 10;
							},
							defaultLabel = "Dev: Produce now",
							defaultDesc = "Reduce ticksTillProduction to 10"
						};
						_003C_003E1__state = 6;
						return true;
					}
					goto IL_03d1;
					IL_03d1:
					_003C_003E2__current = (Gizmo)new Command_Action
					{
						icon = (Texture)(object)TexButton.Rename,
						defaultLabel = TaggedString.op_Implicit(Translator.Translate("Rename")),
						action = delegate
						{
							Find.WindowStack.Add((Window)(object)new Dialog_RenameOutpost(CS_0024_003C_003E8__locals29));
						}
					};
					_003C_003E1__state = 10;
					return true;
				}
			}
			catch
			{
				//try-fault
				((IDisposable)this).Dispose();
				throw;
			}
		}

		bool IEnumerator.MoveNext()
		{
			//ILSpy generated this explicit interface implementation from .override directive in MoveNext
			return this.MoveNext();
		}

		private void _003C_003Em__Finally1()
		{
			_003C_003E1__state = -1;
			if (_003C_003E7__wrap1 != null)
			{
				_003C_003E7__wrap1.Dispose();
			}
		}

		[DebuggerHidden]
		void IEnumerator.Reset()
		{
			throw new NotSupportedException();
		}

		[DebuggerHidden]
		IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
		{
			_003CGetGizmos_003Ed__72 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CGetGizmos_003Ed__72(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			return result;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Gizmo>)this).GetEnumerator();
		}
	}

	private Material cachedMat;

	private List<Thing> containedItems = new List<Thing>();

	private bool costPaid;

	private OutpostExtension extensionCached;

	public string Name;

	private List<Pawn> occupants = new List<Pawn>();

	private bool skillsDirty = true;

	private int ticksTillPacked = -1;

	private int ticksTillProduction;

	public Map deliveryMap;

	public float raidPoints;

	public Faction raidFaction;

	public static Type VehiclePawnType = AccessTools.TypeByName("Vehicles.VehiclePawn");

	public static MethodInfo VehicleRemoveAllPawns;

	private List<Hediff_Injury> tmpHediffInjuries = new List<Hediff_Injury>();

	private List<Hediff_MissingPart> tmpHediffMissing = new List<Hediff_MissingPart>();

	private readonly Dictionary<SkillDef, int> totalSkills = new Dictionary<SkillDef, int>();

	public virtual float RestPerTickResting => 0.014285715f;

	public IEnumerable<Pawn> AllPawns => occupants;

	public int PawnCount => occupants.Count;

	public override Color ExpandingIconColor => ((WorldObject)this).Faction.Color;

	public virtual int TicksPerProduction => Ext?.TicksPerProduction ?? 900000;

	public override bool HasName => !GenText.NullOrEmpty(Name);

	public override string Label => Name;

	public virtual int TicksToPack => (Ext?.TicksToPack ?? 420000) / occupants.Count;

	public bool Packing => ticksTillPacked > 0;

	public virtual int Range => Ext?.Range ?? (-1);

	public IEnumerable<Thing> Things => containedItems;

	public IEnumerable<Pawn> CapablePawns => AllPawns.Where(IsCapable);

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

	public string BaseLabel => ((Def)((WorldObject)this).def).label;

	public string InspectLabel => RenamableLabel;

	public override Material Material
	{
		get
		{
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			if ((Object)(object)cachedMat == (Object)null)
			{
				cachedMat = MaterialPool.MatFrom(((WorldObject)this).Faction.def.settlementTexturePath, ShaderDatabase.WorldOverlayTransparentLit, ((WorldObject)this).Faction.Color, 3550);
			}
			return cachedMat;
		}
	}

	public virtual ThingDef ProvidedFood => Ext?.ProvidedFood ?? ThingDefOf.MealSimple;

	public OutpostExtension Ext => extensionCached ?? (extensionCached = ((Def)((WorldObject)this).def).GetModExtension<OutpostExtension>());

	public virtual string TimeTillProduction => ColoredText.Colorize(GenDate.ToStringTicksToPeriodVerbose(ticksTillProduction, true, true), ColoredText.DateTimeColor);

	public virtual List<ResultOption> ResultOptions => Ext.ResultOptions;

	public void AddItem(Thing t)
	{
		containedItems.Add(t);
	}

	public Thing TakeItem(Thing t)
	{
		containedItems.Remove(t);
		return t;
	}

	public List<Thing> TakeItems(ThingDef thingDef, int stackCount)
	{
		List<Thing> list = new List<Thing>();
		foreach (Thing containedItem in containedItems)
		{
			if (containedItem.def == thingDef)
			{
				if (stackCount < containedItem.stackCount)
				{
					list.Add(containedItem.SplitOff(stackCount));
					stackCount = 0;
				}
				else
				{
					stackCount = -containedItem.stackCount;
					list.Add(TakeItem(containedItem));
				}
			}
			if (stackCount == 0)
			{
				break;
			}
		}
		return list;
	}

	public override void PostAdd()
	{
		((WorldObject)this).PostAdd();
		ticksTillProduction = Mathf.RoundToInt((float)TicksPerProduction * OutpostsMod.Settings.TimeMultiplier);
	}

	public override void DrawExtraSelectionOverlays()
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		((MapParent)this).DrawExtraSelectionOverlays();
		if (Range > 0)
		{
			GenDraw.DrawWorldRadiusRing(((WorldObject)this).Tile, Range, (Material)null);
		}
	}

	public override void ExposeData()
	{
		((MapParent)this).ExposeData();
		Scribe_Collections.Look<Pawn>(ref occupants, "occupants", (LookMode)2, Array.Empty<object>());
		Scribe_Values.Look<int>(ref ticksTillProduction, "ticksTillProduction", 0, false);
		Scribe_Values.Look<string>(ref Name, "name", (string)null, false);
		Scribe_Collections.Look<Thing>(ref containedItems, "containedItems", (LookMode)2, Array.Empty<object>());
		Scribe_Values.Look<bool>(ref costPaid, "costPaid", false, false);
		Scribe_Values.Look<int>(ref ticksTillPacked, "ticksTillPacked", 0, false);
		Scribe_References.Look<Faction>(ref raidFaction, "raidFaction", false);
		Scribe_Values.Look<float>(ref raidPoints, "raidPoints", 0f, false);
		Scribe_References.Look<Map>(ref deliveryMap, "deliveryMap", false);
		try
		{
			RecachePawnTraits();
		}
		catch (Exception ex)
		{
			Log.Error("Error recaching pawn traits in " + ((WorldObject)this).Label + " - " + ex.ToString());
		}
	}

	public override IEnumerable<FloatMenuOption> GetTransportersFloatMenuOptions(IEnumerable<IThingHolder> pods, Action<PlanetTile, TransportersArrivalAction> launchAction)
	{
		return ((MapParent)this).GetTransportersFloatMenuOptions(pods, launchAction).Concat(TransportPodsArrivalAction_AddToOutpost.GetFloatMenuOptions(pods, launchAction, this));
	}

	public override void Tick()
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		((WorldObject)this).Tick();
		if (PawnCount == 0)
		{
			Find.LetterStack.ReceiveLetter(Translator.Translate("Outposts.Abandoned"), TranslatorFormattedStringExtensions.Translate("Outposts.Abandoned.Desc", NamedArgument.op_Implicit(Name)), LetterDefOf.NegativeEvent, (string)null, 0, true);
			((WorldObject)this).Destroy();
		}
		if (((MapParent)this).Map == null)
		{
			SatisfyNeeds();
		}
	}

	public override void TickInterval(int delta)
	{
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		((MapParent)this).TickInterval(delta);
		if (Packing)
		{
			ticksTillPacked -= delta;
			if (ticksTillPacked <= 0)
			{
				ConvertToCaravan();
			}
		}
		else if (TicksPerProduction > 0)
		{
			ticksTillProduction -= delta;
			if (ticksTillProduction <= 0)
			{
				ticksTillProduction = Mathf.RoundToInt((float)TicksPerProduction * OutpostsMod.Settings.TimeMultiplier);
				Produce();
			}
		}
		Caravan val = Find.WorldObjects.PlayerControlledCaravanAt(((WorldObject)this).Tile);
		if (val != null && !val.pather.MovingNow)
		{
			foreach (Pawn item in val.PawnsListForReading)
			{
				if (item.needs?.rest == null)
				{
					continue;
				}
				Need_Rest rest = item.needs.rest;
				((Need)rest).CurLevel = ((Need)rest).CurLevel + RestPerTickResting * (float)delta;
				if (!Gen.IsHashIntervalTick((Thing)(object)item, 300, delta))
				{
					continue;
				}
				Need_Food val2 = item.needs?.food;
				if (val2 == null || !(((Need)val2).CurLevelPercentage <= item.RaceProps.FoodLevelPercentageWantEat))
				{
					continue;
				}
				ThingDef providedFood = ProvidedFood;
				if (providedFood != null && providedFood.IsNutritionGivingIngestible && ProvidedFood.ingestible.HumanEdible)
				{
					Thing val3 = ThingMaker.MakeThing(ProvidedFood, (ThingDef)null);
					if (val3.IngestibleNow && item.RaceProps.CanEverEat(val3))
					{
						((Need)val2).CurLevel = ((Need)val2).CurLevel + val3.Ingested(item, val2.NutritionWanted);
					}
				}
			}
		}
		if (((MapParent)this).Map == null)
		{
			SatisfyNeedsInterval(delta);
		}
	}

	public virtual IEnumerable<Thing> ProducedThings()
	{
		return ResultOptions.SelectMany((ResultOption resultOption) => resultOption.Make(CapablePawns.ToList()));
	}

	public virtual void Produce()
	{
		Deliver(ProducedThings());
	}

	public override void SpawnSetup()
	{
		((WorldObject)this).SpawnSetup();
		if (deliveryMap == null)
		{
			deliveryMap = (from m in Find.Maps
				where m.IsPlayerHome
				orderby Find.WorldGrid.ApproxDistanceInTiles(((WorldObject)m.Parent).Tile, ((WorldObject)this).Tile)
				select m).FirstOrDefault();
		}
		RecachePawnTraits();
		OutpostsMod.Notify_Spawned(this);
	}

	public virtual void RecachePawnTraits()
	{
		skillsDirty = true;
		foreach (Pawn item in containedItems.OfType<Pawn>().ToList())
		{
			containedItems.Remove((Thing)(object)item);
			Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)item);
			if (caravan != null)
			{
				caravan.RemovePawn(item);
			}
			AddPawn(item);
		}
	}

	public bool AddPawn(Pawn pawn)
	{
		if (VehiclePawnType != null && VehiclePawnType.IsAssignableFrom(((object)pawn).GetType()))
		{
			if ((object)VehicleRemoveAllPawns == null)
			{
				VehicleRemoveAllPawns = AccessTools.Method(VehiclePawnType, "RemoveAllPawns", (Type[])null, (Type[])null);
			}
			VehicleRemoveAllPawns.Invoke(pawn, null);
			return false;
		}
		if (!Ext.CanAddPawn(pawn, out var _))
		{
			return false;
		}
		Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)pawn);
		if (caravan != null)
		{
			foreach (Thing item in from item in CaravanInventoryUtility.AllInventoryItems(caravan)
				where CaravanInventoryUtility.GetOwnerOf(caravan, item) == pawn
				select item)
			{
				CaravanInventoryUtility.MoveInventoryToSomeoneElse(pawn, item, caravan.PawnsListForReading, new List<Pawn> { pawn }, item.stackCount);
			}
			if (!GenCollection.Except<Pawn>((IEnumerable<Pawn>)caravan.PawnsListForReading, pawn).Any((Pawn p) => p.RaceProps.Humanlike))
			{
				foreach (Thing item2 in CaravanInventoryUtility.AllInventoryItems(caravan).ToList())
				{
					Pawn ownerOf = CaravanInventoryUtility.GetOwnerOf(caravan, item2);
					containedItems.Add(item2);
					((ThingOwner)ownerOf.inventory.innerContainer).Remove(item2);
				}
			}
			pawn.ownership.UnclaimAll();
			caravan.RemovePawn(pawn);
			if (!GenCollection.Any<Pawn>(caravan.PawnsListForReading, (Predicate<Pawn>)((Pawn p) => p.RaceProps.Humanlike)))
			{
				containedItems.AddRange(caravan.AllThings);
				if (!costPaid)
				{
					List<ThingDefCountClass> costToMake = Ext.CostToMake;
					if (costToMake != null && costToMake.Count > 0)
					{
						List<ThingDefCountClass> costs = ((IEnumerable<ThingDefCountClass>)Ext.CostToMake).Select((Func<ThingDefCountClass, ThingDefCountClass>)((ThingDefCountClass tdcc) => new ThingDefCountClass(tdcc.thingDef, tdcc.count))).ToList();
						containedItems.RemoveAll(delegate(Thing thing)
						{
							ThingDefCountClass val = GenCollection.FirstOrDefault<ThingDefCountClass>(costs, (Predicate<ThingDefCountClass>)((ThingDefCountClass tdcc) => tdcc.thingDef == thing.def));
							if (val == null)
							{
								return false;
							}
							if (val.count > thing.stackCount)
							{
								val.count -= thing.stackCount;
								return true;
							}
							if (val.count < thing.stackCount)
							{
								Thing obj = thing;
								obj.stackCount -= val.count;
								costs.Remove(val);
								return false;
							}
							costs.Remove(val);
							return true;
						});
						if (!GenCollection.Any<ThingDefCountClass>(costs))
						{
							costPaid = true;
						}
					}
				}
				if (!((WorldObject)caravan).Destroyed)
				{
					((WorldObject)caravan).Destroy();
				}
			}
		}
		ThingOwner holdingOwner = ((Thing)pawn).holdingOwner;
		if (holdingOwner != null)
		{
			holdingOwner.Remove((Thing)(object)pawn);
		}
		if (Find.WorldPawns.Contains(pawn))
		{
			Find.WorldPawns.RemovePawn(pawn);
		}
		if (!occupants.Contains(pawn))
		{
			occupants.Add(pawn);
		}
		RecachePawnTraits();
		return true;
	}

	public override void PostRemove()
	{
		((MapParent)this).PostRemove();
		OutpostsMod.Notify_Removed(this);
	}

	public void ConvertToCaravan()
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		Caravan val = CaravanMaker.MakeCaravan((IEnumerable<Pawn>)occupants, ((WorldObject)this).Faction, ((WorldObject)this).Tile, true);
		if (containedItems != null)
		{
			foreach (Thing item in containedItems.Except(val.AllThings))
			{
				val.AddPawnOrItem(item, true);
			}
		}
		if (Find.WorldSelector.IsSelected((WorldObject)(object)this))
		{
			Find.WorldSelector.Select((WorldObject)(object)val, false);
		}
		((WorldObject)this).Destroy();
	}

	public override IEnumerable<Gizmo> GetCaravanGizmos(Caravan caravan)
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Expected O, but got Unknown
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Expected O, but got Unknown
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_012e: Expected O, but got Unknown
		return ((WorldObject)this).GetCaravanGizmos(caravan).Append((Gizmo)new Command_Action
		{
			action = delegate
			{
				//IL_0039: Unknown result type (might be due to invalid IL or missing references)
				//IL_0043: Expected O, but got Unknown
				Find.WindowStack.Add((Window)new FloatMenu(((IEnumerable<Pawn>)caravan.PawnsListForReading).Select((Func<Pawn, FloatMenuOption>)delegate(Pawn p)
				{
					//IL_0067: Unknown result type (might be due to invalid IL or missing references)
					//IL_006c: Unknown result type (might be due to invalid IL or missing references)
					//IL_006f: Unknown result type (might be due to invalid IL or missing references)
					//IL_0074: Unknown result type (might be due to invalid IL or missing references)
					//IL_0094: Unknown result type (might be due to invalid IL or missing references)
					//IL_009a: Expected O, but got Unknown
					//IL_0034: Unknown result type (might be due to invalid IL or missing references)
					//IL_003e: Unknown result type (might be due to invalid IL or missing references)
					//IL_0044: Unknown result type (might be due to invalid IL or missing references)
					//IL_005b: Unknown result type (might be due to invalid IL or missing references)
					//IL_0061: Expected O, but got Unknown
					if (Ext.CanAddPawn(p, out var reason))
					{
						TaggedString val = p.NameFullColored;
						val = ((TaggedString)(ref val)).CapitalizeFirst();
						return new FloatMenuOption(((TaggedString)(ref val)).Resolve(), (Action)delegate
						{
							AddPawn(p);
						}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
					}
					return new FloatMenuOption(TaggedString.op_Implicit(p.NameFullColored + " - " + reason), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
				}).ToList()));
			},
			defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.AddPawn.Label")),
			defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.AddPawn.Desc")),
			icon = (Texture)(object)TexOutposts.AddTex
		}).Append((Gizmo)new Command_Action
		{
			action = delegate
			{
				Find.WindowStack.Add((Window)(object)new Dialog_TakeItems(this, caravan));
			},
			defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.TakeItems.Label")),
			defaultDesc = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.Commands.TakeItems.Desc", NamedArgument.op_Implicit(Name))),
			icon = (Texture)(object)TexOutposts.RemoveItemsTex
		})
			.Append((Gizmo)new Command_Action
			{
				action = delegate
				{
					Find.WindowStack.Add((Window)(object)new Dialog_GiveItems(this, caravan));
				},
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.GiveItems.Label")),
				defaultDesc = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.Commands.GiveItems.Desc", NamedArgument.op_Implicit(caravan.Name))),
				icon = (Texture)(object)TexOutposts.RemoveItemsTex
			});
	}

	[IteratorStateMachine(typeof(_003CGetGizmos_003Ed__72))]
	public override IEnumerable<Gizmo> GetGizmos()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGetGizmos_003Ed__72(-2)
		{
			_003C_003E4__this = this
		};
	}

	public Pawn RemovePawn(Pawn p)
	{
		Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)p);
		if (caravan != null)
		{
			caravan.RemovePawn(p);
		}
		ThingOwner holdingOwner = ((Thing)p).holdingOwner;
		if (holdingOwner != null)
		{
			holdingOwner.Remove((Thing)(object)p);
		}
		occupants.Remove(p);
		RecachePawnTraits();
		return p;
	}

	public override string GetInspectString()
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		string[] obj = new string[6]
		{
			((MapParent)this).GetInspectString(),
			((Def)((WorldObject)this).def).LabelCap.Line(),
			TranslatorFormattedStringExtensions.Translate("Outposts.Contains", NamedArgument.op_Implicit(occupants.Count)).Line(),
			TranslatorFormattedStringExtensions.Translate("Outposts.Packing", NamedArgument.op_Implicit(ColoredText.Colorize(GenDate.ToStringTicksToPeriodVerbose(ticksTillPacked, true, true), ColoredText.DateTimeColor))).Line(Packing),
			ProductionString().Line(!Packing),
			null
		};
		string input = RelevantSkillDisplay();
		OutpostExtension ext = Ext;
		obj[5] = input.Line(ext != null && ext.RelevantSkills?.Count > 0);
		return string.Concat(obj);
	}

	public void Deliver(IEnumerable<Thing> items)
	{
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0100: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		//IL_014e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0153: Unknown result type (might be due to invalid IL or missing references)
		//IL_0280: Unknown result type (might be due to invalid IL or missing references)
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		//IL_0181: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_0199: Unknown result type (might be due to invalid IL or missing references)
		//IL_0337: Unknown result type (might be due to invalid IL or missing references)
		//IL_033c: Unknown result type (might be due to invalid IL or missing references)
		//IL_034e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0357: Expected O, but got Unknown
		//IL_03a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_03f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0409: Unknown result type (might be due to invalid IL or missing references)
		//IL_040e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0438: Unknown result type (might be due to invalid IL or missing references)
		//IL_043d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0442: Unknown result type (might be due to invalid IL or missing references)
		//IL_044e: Unknown result type (might be due to invalid IL or missing references)
		//IL_045e: Expected O, but got Unknown
		List<Thing> list = items.ToList();
		Map map = deliveryMap ?? (from m in Find.Maps
			where m.IsPlayerHome
			orderby Find.WorldGrid.ApproxDistanceInTiles(((WorldObject)m.Parent).Tile, ((WorldObject)this).Tile)
			select m).FirstOrDefault();
		if (map == null)
		{
			Log.Warning("Vanilla Outpost Expanded Tried to deliver to a null map, storing instead");
			{
				foreach (Thing item2 in list)
				{
					containedItems.Add(item2);
				}
				return;
			}
		}
		TaggedString val = TranslatorFormattedStringExtensions.Translate("Outposts.Letters.Items.Text", NamedArgument.op_Implicit(Name)) + "\n";
		List<ThingDefCountClass> list2 = new List<ThingDefCountClass>();
		List<Thing> lookAt = new List<Thing>();
		Rot4 rotFromTo = Find.WorldGrid.GetRotFromTo(((WorldObject)map.Parent).Tile, ((WorldObject)this).Tile);
		switch (OutpostsMod.Settings.DeliveryMethod)
		{
		case DeliveryMethod.Teleport:
		{
			Building val2 = default(Building);
			IntVec3 val3 = default(IntVec3);
			if (GenCollection.TryRandomElement<Building>((IEnumerable<Building>)map.listerBuildings.AllBuildingsColonistOfDef(Outposts_DefOf.VEF_OutpostDeliverySpot), ref val2))
			{
				val3 = ((Thing)val2).Position;
			}
			else if (!CellFinder.TryFindRandomEdgeCellWith((Predicate<IntVec3>)((IntVec3 x) => !GridsUtility.Fogged(x, map) && GenGrid.Standable(x, map) && GenCollection.Any<Pawn>(map.mapPawns.FreeColonistsSpawned, (Predicate<Pawn>)((Pawn p) => ReachabilityUtility.CanReach(p, LocalTargetInfo.op_Implicit(x), (PathEndMode)1, (Danger)2, false, false, (TraverseMode)0)))), map, rotFromTo, CellFinder.EdgeRoadChance_Always, ref val3))
			{
				val3 = CellFinder.RandomEdgeCell(rotFromTo, map);
			}
			foreach (Thing item3 in list)
			{
				GenPlace.TryPlaceThing(item3, val3, map, (ThingPlaceMode)1, (Action<Thing, int>)delegate(Thing t, int i)
				{
					lookAt.Add(t);
				}, (Predicate<IntVec3>)null, (Rot4?)null, 1);
			}
			break;
		}
		case DeliveryMethod.PackAnimal:
			Deliver_PackAnimal(list, map, rotFromTo, lookAt);
			break;
		case DeliveryMethod.Store:
			foreach (Thing item4 in list)
			{
				containedItems.Add(item4);
			}
			break;
		case DeliveryMethod.ForcePods:
			Deliver_Pods(list, map, lookAt);
			break;
		case DeliveryMethod.PackOrPods:
			if (Outposts_DefOf.TransportPod.IsFinished)
			{
				Deliver_Pods(list, map, lookAt);
			}
			else
			{
				Deliver_PackAnimal(list, map, rotFromTo, lookAt);
			}
			break;
		default:
			throw new ArgumentOutOfRangeException();
		}
		List<Thing> list3 = new List<Thing>();
		QualityCategory val4 = default(QualityCategory);
		foreach (Thing item in list)
		{
			if (((BuildableDef)item.def).MadeFromStuff || (item.def.useHitPoints && item.HitPoints < item.MaxHitPoints) || QualityUtility.TryGetQuality(item, ref val4))
			{
				list3.Add(item);
				continue;
			}
			ThingDefCountClass val5 = list2.Find((ThingDefCountClass cc) => cc.thingDef == item.def);
			if (val5 == null)
			{
				val5 = new ThingDefCountClass
				{
					thingDef = item.def,
					count = 0
				};
				list2.Add(val5);
			}
			ThingDefCountClass obj = val5;
			obj.count += item.stackCount;
		}
		foreach (Thing item5 in list3)
		{
			val += "  - " + ((Entity)item5).LabelCap + "\n";
		}
		foreach (ThingDefCountClass item6 in list2)
		{
			val += "  - " + item6.Summary + "\n";
		}
		Find.LetterStack.ReceiveLetter(TranslatorFormattedStringExtensions.Translate("Outposts.Letters.Items.Label", NamedArgument.op_Implicit(Name)), val, LetterDefOf.PositiveEvent, new LookTargets((IEnumerable<Thing>)lookAt), (Faction)null, (Quest)null, (List<ThingDef>)null, (string)null, 0, true);
	}

	private static void Deliver_Pods(IEnumerable<Thing> items, Map map, List<Thing> lookAt)
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		Building val = default(Building);
		IntVec3 val2;
		if (GenCollection.TryRandomElement<Building>((IEnumerable<Building>)map.listerBuildings.AllBuildingsColonistOfDef(Outposts_DefOf.VEF_OutpostDeliverySpot), ref val))
		{
			lookAt.Add((Thing)(object)val);
			val2 = ((Thing)val).Position;
		}
		else
		{
			val2 = DropCellFinder.TradeDropSpot(map);
		}
		IntVec3 val3 = default(IntVec3);
		foreach (Thing item in items)
		{
			if (!DropCellFinder.TryFindDropSpotNear(val2, map, ref val3, false, false, false, (IntVec2?)null, true))
			{
				val3 = DropCellFinder.RandomDropSpot(map, true);
			}
			TradeUtility.SpawnDropPod(val3, map, item);
		}
	}

	private void Deliver_PackAnimal(IEnumerable<Thing> items, Map map, Rot4 dir, List<Thing> lookAt)
	{
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0127: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		PawnKindDef muffalo = default(PawnKindDef);
		if (!GenCollection.TryRandomElement<PawnKindDef>(((WorldObject)this).Biome.AllWildAnimals.Where((PawnKindDef x) => x.RaceProps.packAnimal), ref muffalo))
		{
			muffalo = PawnKindDefOf.Muffalo;
		}
		IntVec3 val = default(IntVec3);
		if (!CellFinder.TryFindRandomEdgeCellWith((Predicate<IntVec3>)((IntVec3 x) => !GridsUtility.Fogged(x, map) && GenGrid.Standable(x, map)), map, dir, CellFinder.EdgeRoadChance_Always, ref val) && !RCellFinder.TryFindRandomPawnEntryCell(ref val, map, CellFinder.EdgeRoadChance_Always, false, (Predicate<IntVec3>)null))
		{
			val = CellFinder.RandomEdgeCell(dir, map);
		}
		Pawn animal = PawnGenerator.GeneratePawn(muffalo, Faction.OfPlayer, (PlanetTile?)null);
		lookAt.Add((Thing)(object)animal);
		foreach (Thing item in items)
		{
			animal.inventory.TryAddItemNotForSale(item);
		}
		GenSpawn.Spawn((Thing)(object)animal, val, map, (WipeMode)0);
		Building val2 = default(Building);
		IntVec3 deliverLoc = default(IntVec3);
		if (GenCollection.TryRandomElement<Building>((IEnumerable<Building>)map.listerBuildings.AllBuildingsColonistOfDef(Outposts_DefOf.VEF_OutpostDeliverySpot), ref val2))
		{
			deliverLoc = ((Thing)val2).Position;
		}
		else if (!RCellFinder.TryFindRandomSpotJustOutsideColony(animal, ref deliverLoc))
		{
			deliverLoc = CellFinderLoose.RandomCellWith((Predicate<IntVec3>)((IntVec3 x) => !GridsUtility.Fogged(x, map) && GenGrid.Standable(x, map) && ReachabilityUtility.CanReach(animal, LocalTargetInfo.op_Implicit(x), (PathEndMode)1, (Danger)3, false, false, (TraverseMode)0)), map, 1000);
		}
		LordMaker.MakeNewLord(Faction.OfPlayer, (LordJob)(object)new LordJob_Deliver(deliverLoc), map, (IEnumerable<Pawn>)(object)new Pawn[1] { animal });
	}

	public virtual void SatisfyNeeds()
	{
		for (int i = 0; i < occupants.Count; i++)
		{
			SatisfyNeeds(occupants[i]);
		}
	}

	public virtual void SatisfyNeedsInterval(int delta)
	{
		for (int i = 0; i < occupants.Count; i++)
		{
			SatisfyNeedsInterval(occupants[i], delta);
		}
	}

	public virtual void SatisfyNeeds(Pawn pawn)
	{
		if (pawn != null && !((Thing)pawn).Spawned && !pawn.Dead)
		{
			OutpostHealthTick(pawn);
			if (pawn.Dead)
			{
				occupants.Remove(pawn);
				containedItems.Add((Thing)(object)pawn.Corpse);
			}
		}
	}

	public virtual void SatisfyNeedsInterval(Pawn pawn, int delta)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		if (pawn == null || ((Thing)pawn).Spawned || pawn.Dead)
		{
			return;
		}
		if (GenLocalDate.HourInteger(((WorldObject)this).Tile) >= 23 || GenLocalDate.HourInteger(((WorldObject)this).Tile) <= 5)
		{
			Pawn_NeedsTracker needs = pawn.needs;
			if (needs != null)
			{
				Need_Rest rest = needs.rest;
				if (rest != null)
				{
					rest.TickResting(0.75f * (float)delta);
				}
			}
		}
		Pawn_AgeTracker ageTracker = pawn.ageTracker;
		if (ageTracker != null)
		{
			ageTracker.AgeTickInterval(delta);
		}
		OutpostHealthTickInterval(pawn, delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)pawn, 300, delta))
		{
			return;
		}
		Need_Food val = pawn.needs?.food;
		if (val != null && ((Need)val).CurLevelPercentage <= pawn.RaceProps.FoodLevelPercentageWantEat)
		{
			ThingDef providedFood = ProvidedFood;
			if (providedFood != null && providedFood.IsNutritionGivingIngestible && ProvidedFood.ingestible.HumanEdible)
			{
				Thing val2 = ThingMaker.MakeThing(ProvidedFood, (ThingDef)null);
				if (val2.IngestibleNow && pawn.RaceProps.CanEverEat(val2))
				{
					((Need)val).CurLevel = ((Need)val).CurLevel + val2.Ingested(pawn, val.NutritionWanted);
				}
			}
		}
		if (pawn.needs == null)
		{
			return;
		}
		foreach (Need need in pawn.needs.needs)
		{
			if ((need is Need_Chemical || need is Need_Chemical_Any) ? true : false)
			{
				need.CurLevel = need.MaxLevel;
			}
		}
	}

	public virtual void OutpostHealthTick(Pawn pawn)
	{
		if (pawn.health?.hediffSet == null || pawn.Dead)
		{
			return;
		}
		bool flag = false;
		Pawn_HealthTracker health = pawn.health;
		for (int num = health.hediffSet.hediffs.Count - 1; num >= 0; num--)
		{
			Hediff val = health.hediffSet.hediffs[num];
			if ((val is Hediff_ChemicalDependency || val is Hediff_Addiction) ? true : false)
			{
				val.Severity = 0f;
			}
			else
			{
				try
				{
					val.Tick();
					val.PostTick();
				}
				catch
				{
					health.RemoveHediff(val);
				}
			}
			if (pawn.Dead)
			{
				return;
			}
			if (val.ShouldRemove)
			{
				health.hediffSet.hediffs.RemoveAt(num);
				val.PostRemoved();
				flag = true;
			}
		}
		if (flag)
		{
			health.Notify_HediffChanged((Hediff)null);
		}
	}

	public virtual void OutpostHealthTickInterval(Pawn pawn, int delta)
	{
		//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0212: Unknown result type (might be due to invalid IL or missing references)
		//IL_0219: Expected O, but got Unknown
		if (pawn.health?.hediffSet == null || pawn.Dead)
		{
			return;
		}
		bool flag = false;
		Pawn_HealthTracker health = pawn.health;
		for (int num = health.hediffSet.hediffs.Count - 1; num >= 0; num--)
		{
			Hediff val = health.hediffSet.hediffs[num];
			if ((!(val is Hediff_ChemicalDependency) && !(val is Hediff_Addiction)) || 1 == 0)
			{
				try
				{
					val.TickInterval(delta);
					val.PostTickInterval(delta);
				}
				catch
				{
					health.RemoveHediff(val);
				}
			}
			if (pawn.Dead)
			{
				return;
			}
			if (val.ShouldRemove)
			{
				health.hediffSet.hediffs.RemoveAt(num);
				val.PostRemoved();
				flag = true;
			}
		}
		if (flag)
		{
			health.Notify_HediffChanged((Hediff)null);
			flag = false;
		}
		health.immunity.ImmunityHandlerTickInterval(delta);
		if (Gen.IsHashIntervalTick((Thing)(object)pawn, 600, delta))
		{
			if (pawn.health.HasHediffsNeedingTend(false))
			{
				Pawn val2 = GenCollection.MaxBy<Pawn, float>(AllPawns.Where((Pawn p) => p.RaceProps.Humanlike && !p.Downed), (Func<Pawn, float>)delegate(Pawn p)
				{
					Pawn_SkillTracker skills = p.skills;
					int? obj2;
					if (skills == null)
					{
						obj2 = null;
					}
					else
					{
						SkillRecord skill = skills.GetSkill(SkillDefOf.Medicine);
						obj2 = ((skill != null) ? new int?(skill.Level) : ((int?)null));
					}
					return ((float?)obj2) ?? (-1f);
				});
				if (val2 != null)
				{
					Medicine val3 = null;
					float num2 = 0f;
					CheckNoDestroyedOrNoStack();
					foreach (Thing item in containedItems.ToList())
					{
						if (item.def.IsMedicine && (pawn.playerSettings == null || MedicalCareUtility.AllowsMedicine(pawn.playerSettings.medCare, item.def)))
						{
							float statValue = StatExtension.GetStatValue(item, StatDefOf.MedicalPotency, true, -1);
							if (statValue > num2 || val3 == null)
							{
								num2 = statValue;
								val3 = (Medicine)TakeItem(item);
							}
						}
					}
					TendUtility.DoTend(val2, pawn, val3);
				}
			}
			if (pawn.health.hediffSet.HasNaturallyHealingInjury())
			{
				float num3 = 16f;
				foreach (Hediff hediff in pawn.health.hediffSet.hediffs)
				{
					HediffStage curStage = hediff.CurStage;
					if (curStage != null && curStage.naturalHealingFactor != -1f)
					{
						num3 *= curStage.naturalHealingFactor;
					}
				}
				pawn.health.hediffSet.GetHediffs<Hediff_Injury>(ref tmpHediffInjuries, (Predicate<Hediff_Injury>)((Hediff_Injury x) => HediffUtility.CanHealNaturally(x)));
				Hediff_Injury val4 = GenCollection.RandomElement<Hediff_Injury>((IEnumerable<Hediff_Injury>)tmpHediffInjuries);
				((Hediff)val4).Heal(num3 * pawn.HealthScale * 0.01f * StatExtension.GetStatValue((Thing)(object)pawn, StatDefOf.InjuryHealingFactor, true, -1));
				if (((Hediff)val4).ShouldRemove)
				{
					pawn.health.hediffSet.hediffs.Remove((Hediff)(object)val4);
					((Hediff)val4).PostRemoved();
					flag = true;
				}
			}
			if (pawn.health.hediffSet.HasTendedAndHealingInjury())
			{
				pawn.health.hediffSet.GetHediffs<Hediff_Injury>(ref tmpHediffInjuries, (Predicate<Hediff_Injury>)((Hediff_Injury x) => HediffUtility.CanHealFromTending(x)));
				Hediff_Injury val5 = GenCollection.RandomElement<Hediff_Injury>((IEnumerable<Hediff_Injury>)tmpHediffInjuries);
				((Hediff)val5).Heal(0.08f * GenMath.LerpDouble(0f, 1f, 0.5f, 1.5f, Mathf.Clamp01(HediffUtility.TryGetComp<HediffComp_TendDuration>((Hediff)(object)val5).tendQuality)) * pawn.HealthScale * StatExtension.GetStatValue((Thing)(object)pawn, StatDefOf.InjuryHealingFactor, true, -1));
				if (((Hediff)val5).ShouldRemove)
				{
					pawn.health.hediffSet.hediffs.Remove((Hediff)(object)val5);
					((Hediff)val5).PostRemoved();
					flag = true;
				}
			}
			if (flag)
			{
				pawn.health.Notify_HediffChanged((Hediff)null);
			}
		}
		if (!Gen.IsHashIntervalTick((Thing)(object)pawn, 15, delta) || !pawn.health.hediffSet.HasRegeneration)
		{
			return;
		}
		float num4 = 0f;
		foreach (Hediff hediff2 in pawn.health.hediffSet.hediffs)
		{
			HediffStage curStage2 = hediff2.CurStage;
			if (curStage2 != null && curStage2.regeneration != -1f)
			{
				num4 += curStage2.regeneration;
			}
		}
		num4 *= 0.00025f;
		if (!(num4 > 0f))
		{
			return;
		}
		pawn.health.hediffSet.GetHediffs<Hediff_Injury>(ref tmpHediffInjuries, (Predicate<Hediff_Injury>)null);
		foreach (Hediff_Injury tmpHediffInjury in tmpHediffInjuries)
		{
			float num5 = Mathf.Min(num4, ((Hediff)tmpHediffInjury).Severity);
			num4 -= num5;
			((Hediff)tmpHediffInjury).Heal(num5);
			pawn.health.hediffSet.Notify_Regenerated(num5);
			if (num4 <= 0f)
			{
				break;
			}
		}
		if (!(num4 > 0f))
		{
			return;
		}
		pawn.health.hediffSet.GetHediffs<Hediff_MissingPart>(ref tmpHediffMissing, (Predicate<Hediff_MissingPart>)((Hediff_MissingPart hediff) => ((Hediff)hediff).Part.parent != null && !GenCollection.Any<Hediff_MissingPart>(tmpHediffMissing, (Predicate<Hediff_MissingPart>)((Hediff_MissingPart x) => ((Hediff)x).Part == ((Hediff)hediff).Part.parent)) && pawn.health.hediffSet.GetFirstHediffMatchingPart<Hediff_MissingPart>(((Hediff)hediff).Part.parent) == null && pawn.health.hediffSet.GetFirstHediffMatchingPart<Hediff_AddedPart>(((Hediff)hediff).Part.parent) == null));
		Hediff_MissingPart val6 = default(Hediff_MissingPart);
		if (GenCollection.TryRandomElement<Hediff_MissingPart>((IEnumerable<Hediff_MissingPart>)tmpHediffMissing, ref val6))
		{
			BodyPartRecord part = ((Hediff)val6).Part;
			pawn.health.RemoveHediff((Hediff)(object)val6);
			Hediff val7 = pawn.health.AddHediff(HediffDefOf.Misc, part, (DamageInfo?)null, (DamageResult)null);
			float partHealth = pawn.health.hediffSet.GetPartHealth(part);
			val7.Severity = Mathf.Max(partHealth - 1f, partHealth * 0.9f);
			pawn.health.hediffSet.Notify_Regenerated(partHealth - val7.Severity);
		}
	}

	public int TotalSkill(SkillDef skill)
	{
		if (skillsDirty)
		{
			foreach (SkillDef allDef in DefDatabase<SkillDef>.AllDefs)
			{
				totalSkills[allDef] = CapablePawns.Sum((Pawn p) => p.skills.GetSkill(skill).Level);
			}
		}
		return totalSkills[skill];
	}

	protected virtual bool IsCapable(Pawn pawn)
	{
		if (!pawn.RaceProps.Humanlike)
		{
			return false;
		}
		if (pawn.skills == null)
		{
			return false;
		}
		return !GenCollection.Any<SkillDef>(Ext.RelevantSkills, (Predicate<SkillDef>)((SkillDef skill) => pawn.skills.GetSkill(skill).TotallyDisabled));
	}

	public bool Has(Pawn pawn)
	{
		return occupants.Contains(pawn);
	}

	public void CheckNoDestroyedOrNoStack()
	{
		if (!GenCollection.Any<Thing>(containedItems, (Predicate<Thing>)((Thing x) => x.Destroyed || x.stackCount == 0)))
		{
			return;
		}
		foreach (Thing item in containedItems.Where((Thing x) => x.Destroyed || x.stackCount == 0).ToList())
		{
			containedItems.Remove(item);
		}
	}

	public virtual string ProductionString()
	{
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0103: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_013b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		List<ResultOption> resultOptions = ResultOptions;
		if (Ext == null || resultOptions == null || resultOptions.Count <= 0)
		{
			return "";
		}
		TaggedString val;
		switch (resultOptions.Count)
		{
		case 1:
			val = TranslatorFormattedStringExtensions.Translate("Outposts.WillProduce.1", NamedArgument.op_Implicit(resultOptions[0].Amount(CapablePawns.ToList())), NamedArgument.op_Implicit(((Def)resultOptions[0].Thing).label), NamedArgument.op_Implicit(TimeTillProduction));
			return ((TaggedString)(ref val)).RawText;
		case 2:
			val = TranslatorFormattedStringExtensions.Translate("Outposts.WillProduce.2", NamedArgument.op_Implicit(resultOptions[0].Amount(CapablePawns.ToList())), NamedArgument.op_Implicit(((Def)resultOptions[0].Thing).label), NamedArgument.op_Implicit(resultOptions[1].Amount(CapablePawns.ToList())), NamedArgument.op_Implicit(((Def)resultOptions[1].Thing).label), NamedArgument.op_Implicit(TimeTillProduction));
			return ((TaggedString)(ref val)).RawText;
		default:
			val = TranslatorFormattedStringExtensions.Translate("Outposts.WillProduce.N", NamedArgument.op_Implicit(TimeTillProduction), NamedArgument.op_Implicit(GenText.ToLineList(resultOptions.Select((ResultOption ro) => ro.Explain(CapablePawns.ToList())), "  - ", false)));
			return ((TaggedString)(ref val)).RawText;
		}
	}

	public virtual string RelevantSkillDisplay()
	{
		return GenText.ToLineList(Ext.RelevantSkills.Select(delegate(SkillDef skill)
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			TaggedString val = TranslatorFormattedStringExtensions.Translate("Outposts.TotalSkill", NamedArgument.op_Implicit(skill.skillLabel), NamedArgument.op_Implicit(TotalSkill(skill)));
			return ((TaggedString)(ref val)).RawText;
		}), (string)null, false);
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((MapParent)this).GetGizmos();
	}
}
