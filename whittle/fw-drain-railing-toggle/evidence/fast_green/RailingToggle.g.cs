// GENERATED: complete production methods.
namespace RimMandrake.FlowWorks.SelfTest.RailingHarness { internal sealed partial class RM_MapComponent_SuspensionBridges {
public SuspensionBridgeRecord RecordAt(IntVec3 c)
		{
			return index.TryGetValue(c, out SuspensionBridgeRecord r) ? r : null;
		}
public static Building_SuspensionDeck DeckAt(Map map, IntVec3 c)
		{
			return RM_SpanUtility.DeckAt(map, c) as Building_SuspensionDeck;
		}
public static Building_SuspensionDeck StructuralDeckAt(Map map, IntVec3 c)
		{
			Building_SuspensionDeck d = BuiltAt<Building_SuspensionDeck>(map, c);
			return d != null && d.Spawned && !d.Collapsed ? d : null;
		}
public static T BuiltAt<T>(Map map, IntVec3 c) where T : Thing
		{
			if (map == null || !c.InBounds(map))
			{
				return null;
			}
			List<Thing> things = map.thingGrid.ThingsListAtFast(c);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is T t)
				{
					return t;
				}
			}
			return null;
		}
public static bool RailedAt(Map map, IntVec3 c)
		{
			return BuiltAt<Building_SuspensionRailing>(map, c) != null;
		}
public static Gizmo RailingGizmo(Map map, SuspensionBridgeRecord r)
		{
			if (map == null || r == null)
			{
				return null;
			}
			RM_MapComponent_SuspensionBridges b = map.GetComponent<RM_MapComponent_SuspensionBridges>();
			bool want = !r.railings;
			return new Command_Toggle
			{
				defaultLabel = "Railings: " + (r.railings ? "on" : "off"),
				defaultDesc = "Order railings built on every square of this suspension bridge (+50% of the deck's cost), or taken "
					+ "down. A railed edge never drops anyone; an open edge lets people fall off when staggered, blasted or slipping, "
					+ "and lets them jump down into the hole on purpose. Railings give no cover.",
				icon = TexCommand.ForbidOff,
				isActive = () => r.railings,
				toggleAction = () => b.SetRailings(r, want),
			};
		}
public void SetRailings(SuspensionBridgeRecord r, bool on)
		{
			if (r.railings == on)
			{
				return;
			}
			r.railings = on;
			for (int lane = 0; lane < r.width; lane++)
			{
				for (int i = 1; i <= r.LastDeck; i++)
				{
					IntVec3 c = r.Cell(lane, i);
					if (on)
					{
						if (DeckAt(map, c) != null)
						{
							PlaceRailing(c);
						}
					}
					else
					{
						RemoveRailing(c);
					}
				}
			}
		}
private void PlaceRailing(IntVec3 c)
		{
			ThingDef rail = RM_SuspensionDefOf.RM_SuspensionRailing;
			if (rail == null)
			{
				return;
			}
			if (RailedAt(map, c))
			{
				// Re-enabling before removal keeps the built railings, cancelling only their queued deconstruction.
				foreach (Thing t in c.GetThingList(map))
				{
					if (t is Building_SuspensionRailing existing)
					{
						map.designationManager.DesignationOn(existing, DesignationDefOf.Deconstruct)?.Delete();
					}
				}
				return;
			}
			foreach (Thing t in c.GetThingList(map))
			{
				if (t.def.entityDefToBuild == rail)
				{
					return;
				}
			}
			if (GenConstruct.CanPlaceBlueprintAt(rail, c, Rot4.North, map).Accepted)
			{
				string look = RecordAt(c)?.look;
				// RAILING_MATERIAL_FIX_MADE_OF_NOTHING: the railing is madeFromStuff, so both paths pass a material (the deck's when
				// it can make one, else the default) -- stuff null logged 'madeFromStuff but stuff=null' once per railing, live 2026-10-22.
				ThingDef stuff = RailingStuffFor(rail, StructuralDeckAt(map, c));
				if (DebugSettings.godMode)
				{
					Thing t = ThingMaker.MakeThing(rail, stuff);
					t.SetFactionDirect(Faction.OfPlayer);
					RM_SuspensionLooks.Apply(t, look);
					GenSpawn.Spawn(t, c, map, Rot4.North);
				}
				else
				{
					GenConstruct.PlaceBlueprintForBuild(rail, c, map, Rot4.North, Faction.OfPlayer, stuff, null, RM_SuspensionLooks.StyleFor(rail, look));
				}
			}
		}
public static ThingDef RailingStuffFor(ThingDef rail, Building_SuspensionDeck deck)
		{
			if (rail == null || !rail.MadeFromStuff)
			{
				return null;
			}
			if (deck != null)
			{
				if (deck.Stuff != null && deck.Stuff.stuffProps != null && deck.Stuff.stuffProps.CanMake(rail))
				{
					return deck.Stuff;
				}
				if (deck.def.costList != null)
				{
					foreach (ThingDefCountClass tc in deck.def.costList)
					{
						if (tc.thingDef != null && tc.thingDef.IsStuff && tc.thingDef.stuffProps.CanMake(rail))
						{
							return tc.thingDef;
						}
					}
				}
			}
			return GenStuff.DefaultStuffFor(rail);
		}
private void RemoveRailing(IntVec3 c)
		{
			List<Thing> things = new List<Thing>(c.GetThingList(map));
			foreach (Thing t in things)
			{
				if (t.def.entityDefToBuild == RM_SuspensionDefOf.RM_SuspensionRailing && (t.def.IsBlueprint || t.def.IsFrame))
				{
					t.Destroy(DestroyMode.Cancel);
				}
				else if (t is Building_SuspensionRailing rail)
				{
					if (DebugSettings.godMode)
					{
						rail.Destroy(DestroyMode.Vanish);
					}
					else if (map.designationManager.DesignationOn(rail, DesignationDefOf.Deconstruct) == null)
					{
						map.designationManager.AddDesignation(new Designation(rail, DesignationDefOf.Deconstruct));
					}
				}
			}
		}
} }
