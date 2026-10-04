using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Miasma
{
    // MIASMA_MOTHERS_PRICE_1 (design: miasma_bedazzle_review_2026-10-02.md §3 "The Mother's Price"; owner card 2026-10-02
    // item 2). A held stranded young is worth a fortune: carry it home to her, or sell it.
    //  - Price: RUT_StrandedDeformation.priceOffset = youngPriceOffset while on (RM_MiasmaSettingsApplier), and any pawn
    //    trader will take one (Tradeable.TraderWillTrade postfix), since the nursery species carry no trade tags.
    //  - The buyer: once per young the colony holds on a home map, a trader caravan comes for it 1-2 days later, with a
    //    letter naming the buyer (RM_MothersPriceExtension on the hediff: generic in the free mod, named by Utinni).
    //  - Sold (Pawn.PreTraded postfix, PlayerSells): its crèche ledger is betrayed (self-taming barred, succession void)
    //    and the mother's tolerance is revoked forever (RM_CompTerritorialAnchor.RevokeForever, reached by reflection:
    //    this assembly holds no reference to the shared kit). Letter.
    //  - Brought back (a held young standing in water, or carried by a colonist standing in water, within her reach):
    //    she takes it back (the young goes wild and loses the deformation), the whole colony is tolerated from then on
    //    (GrantColonyTolerance), letter. A betrayed mother refuses it.
    // The cry while held is MIASMA_YOUNG_CALL_1's (any spawned carrier calls). Numbers // INVENTED.
    public class RM_MothersPriceExtension : DefModExtension
    {
        public string buyerPen = "a dealer in rare beasts";
        public string buyerSea = "a sea-trader who knows what these are worth";
    }

    public static class RM_MothersPrice
    {
        public const string StrandedHediff = "RUT_StrandedDeformation";
        public const string MotherKind = "RM_WardenMother";
        public const string MarkerDef = "RUT_CrecheMarker";

        private static HediffDef strandedDef;

        public static HediffDef StrandedDef => strandedDef ?? (strandedDef = DefDatabase<HediffDef>.GetNamedSilentFail(StrandedHediff));

        public static bool IsStrandedYoung(Pawn p)
        {
            return p != null && !p.Dead && StrandedDef != null && p.health?.hediffSet != null && p.health.hediffSet.HasHediff(StrandedDef);
        }

        public static bool IsWater(IntVec3 c, Map map)
        {
            return c.InBounds(map) && (c.GetTerrain(map)?.IsWater ?? false);
        }

        public static ThingComp AnchorOf(Pawn mother)
        {
            return mother?.AllComps?.FirstOrDefault(c => c.GetType().Name == "RM_CompTerritorialAnchor");
        }

        public static float ReachOf(Pawn mother)
        {
            ThingComp c = AnchorOf(mother);
            object r = c?.props?.GetType().GetField("anchorRadius")?.GetValue(c.props);
            return r is float f && f > 0f ? f : 16f;
        }

        private static object Call(ThingComp comp, string method)
        {
            MethodInfo m = comp?.GetType().GetMethod(method, BindingFlags.Public | BindingFlags.Instance, null, System.Type.EmptyTypes, null);
            return m?.Invoke(comp, null);
        }

        private static bool Get(ThingComp comp, string property)
        {
            return comp?.GetType().GetProperty(property)?.GetValue(comp) is bool b && b;
        }

        public static bool MotherBetrayed(Pawn mother) => Get(AnchorOf(mother), "Betrayed");

        public static bool MotherTolerates(Pawn mother) => Get(AnchorOf(mother), "ColonyTolerated");

        public static RM_MothersPriceExtension Ext => StrandedDef?.GetModExtension<RM_MothersPriceExtension>() ?? new RM_MothersPriceExtension();

        /// <summary>The young's own crèche if it registered with one, else the nearest crèche marker on its map.</summary>
        public static Thing CrecheOf(Pawn young)
        {
            Hediff h = young?.health?.hediffSet?.GetFirstHediffOfDef(StrandedDef);
            Thing marker = (h as HediffWithComps)?.comps?.OfType<RM_HediffComp_SelfTameOnRecord>().FirstOrDefault()?.CrecheMarker;
            if (marker != null && !marker.Destroyed)
            {
                return marker;
            }
            Map map = young?.MapHeld;
            ThingDef md = DefDatabase<ThingDef>.GetNamedSilentFail(MarkerDef);
            if (map == null || md == null)
            {
                return null;
            }
            IntVec3 at = young.PositionHeld;
            return map.listerThings.ThingsOfDef(md).OrderBy(t => t.Position.DistanceToSquared(at)).FirstOrDefault();
        }

        public static Pawn MotherOf(Thing marker, Map fallbackMap, IntVec3 near)
        {
            Pawn m = marker?.TryGetComp<RM_CompCrecheYoungLedger>()?.MotherNow();
            if (m != null && !m.Dead)
            {
                return m;
            }
            Map map = marker?.Map ?? fallbackMap;
            return map?.mapPawns.AllPawnsSpawned.Where(p => p.kindDef?.defName == MotherKind && !p.Dead)
                .OrderBy(p => p.Position.DistanceToSquared(near)).FirstOrDefault();
        }

        /// <summary>Pawn.PreTraded, PlayerSells. Returns what it did (for the proof).</summary>
        public static string Notify_Sold(Pawn young, string buyer)
        {
            if (!RM_MiasmaSettings.mothersPriceEnabled || !IsStrandedYoung(young))
            {
                return "ignored";
            }
            Thing marker = CrecheOf(young);
            marker?.TryGetComp<RM_CompCrecheYoungLedger>()?.Betray(young);
            Pawn mother = MotherOf(marker, young.MapHeld, young.PositionHeld);
            ThingComp anchor = AnchorOf(mother);
            if (anchor != null)
            {
                Call(anchor, "RevokeForever");
            }
            Find.LetterStack.ReceiveLetter("Sold: " + young.LabelShort,
                (buyer.NullOrEmpty() ? "The buyer" : buyer.CapitalizeFirst()) + " paid well for " + young.LabelShort
                + ", and it went on crying all the way to the edge of the map.\n\nIts crèche remembers. The warden mother "
                + "will never tolerate your colony again, and none of her young will ever be yours.",
                LetterDefOf.NegativeEvent, mother != null && mother.Spawned ? new LookTargets(mother) : null);
            return "betrayed marker=" + (marker != null) + " mother=" + (mother != null) + " anchor=" + (anchor != null);
        }

        /// <summary>A held young brought into her water. True when she took it.</summary>
        public static bool TryReturn(Pawn young, Pawn carrier, Pawn mother)
        {
            Map map = mother.Map;
            if (MotherBetrayed(mother))
            {
                Messages.Message("The warden mother will not take it. She remembers the one you sold.", mother,
                    MessageTypeDefOf.NegativeEvent, false);
                return false;
            }
            if (carrier != null && carrier.carryTracker?.CarriedThing == young)
            {
                carrier.carryTracker.TryDropCarriedThing(carrier.Position, ThingPlaceMode.Near, out Thing _);
            }
            if (young.Faction != null)
            {
                young.SetFaction(null);
            }
            Hediff h = young.health.hediffSet.GetFirstHediffOfDef(StrandedDef);
            Thing marker = CrecheOf(young);
            if (h != null)
            {
                young.health.RemoveHediff(h);
            }
            marker?.TryGetComp<RM_CompCrecheYoungLedger>()?.NoteReturned(young);
            Call(AnchorOf(mother), "GrantColonyTolerance");
            Find.LetterStack.ReceiveLetter("She takes it back",
                "You brought " + young.LabelShort + " back into the water, where the warden mother could reach it. She "
                + "took it under her and the crying stopped.\n\nShe will not touch your people now, so long as they "
                + "leave her crèche alone.", LetterDefOf.PositiveEvent, new LookTargets(mother));
            return true;
        }

        /// <summary>The trader caravan for a held young. False when no faction can send one now.</summary>
        public static bool SendBuyer(Pawn young, Map map)
        {
            Faction f = Find.FactionManager.AllFactionsListForReading
                .Where(x => !x.IsPlayer && !x.defeated && !x.Hidden && !x.temporary && !x.HostileTo(Faction.OfPlayer)
                            && x.def.caravanTraderKinds != null && x.def.caravanTraderKinds.Count > 0)
                .RandomElementWithFallback();
            if (f == null)
            {
                return false;
            }
            IncidentParms parms = new IncidentParms
            {
                target = map,
                faction = f,
                traderKind = f.def.caravanTraderKinds.RandomElement(),
                forced = true
            };
            if (!IncidentDefOf.TraderCaravanArrival.Worker.TryExecute(parms))
            {
                return false;
            }
            string buyer = IsWater(young.PositionHeld, map) ? Ext.buyerSea : Ext.buyerPen;
            Find.LetterStack.ReceiveLetter("A buyer for the young",
                "Word has gone round that you hold " + young.LabelShort + ", a stranded young of the warden mother. "
                + buyer.CapitalizeFirst() + " travels with the " + f.Name + " caravan arriving now, and will pay a fortune "
                + "for it.\n\nSell it and her crèche will remember: she will never tolerate your colony, and none of her "
                + "young will ever be yours. Or carry it back into her water.",
                LetterDefOf.NeutralEvent, new LookTargets(young));
            return true;
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_MothersPricePatches
    {
        static RM_MothersPricePatches()
        {
            try
            {
                Harmony h = new Harmony("mandrake.rm.miasma.mothersprice");
                h.Patch(AccessTools.Method(typeof(Pawn), nameof(Pawn.PreTraded)),
                    prefix: new HarmonyMethod(typeof(RM_MothersPricePatches), nameof(PreTradedPrefix)));
                h.Patch(AccessTools.PropertyGetter(typeof(Tradeable), nameof(Tradeable.TraderWillTrade)),
                    postfix: new HarmonyMethod(typeof(RM_MothersPricePatches), nameof(TraderWillTradePostfix)));
            }
            catch (System.Exception e)
            {
                Log.Error("[RM Miasma] mother's price patches failed: " + e);
            }
        }

        // Prefix: the hediff and the crèche link are read before PreTraded clears the young's faction and mind.
        public static void PreTradedPrefix(Pawn __instance, TradeAction action, ITrader trader)
        {
            if (action == TradeAction.PlayerSells && RM_MothersPrice.IsStrandedYoung(__instance))
            {
                RM_MothersPrice.Notify_Sold(__instance, trader?.TraderName);
            }
        }

        public static void TraderWillTradePostfix(Tradeable __instance, ref bool __result)
        {
            if (!__result && RM_MiasmaSettings.mothersPriceEnabled && __instance.AnyThing is Pawn p && RM_MothersPrice.IsStrandedYoung(p))
            {
                __result = true;
            }
        }
    }

    /// <summary>On every map: the return check (250 t) and, on home maps, the buyer for a held young (2500 t).</summary>
    public class RM_MapComponent_MothersPrice : MapComponent
    {
        private const int ReturnPoll = 250;
        private const int BuyerPoll = 2500;
        private const int BuyerDelayMin = 60000;
        private const int BuyerDelayMax = 120000;

        private List<int> offered = new List<int>();
        private Dictionary<int, int> buyerAt = new Dictionary<int, int>();
        private List<int> tmpKeys;
        private List<int> tmpVals;

        public RM_MapComponent_MothersPrice(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (!RM_MiasmaSettings.mothersPriceEnabled)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (now % ReturnPoll == 0)
            {
                CheckReturns();
            }
            if (now % BuyerPoll == 0 && map.IsPlayerHome)
            {
                CheckBuyers(now);
            }
        }

        public int CheckReturns()
        {
            List<Pawn> mothers = map.mapPawns.AllPawnsSpawned.Where(p => p.kindDef?.defName == RM_MothersPrice.MotherKind && !p.Dead && !p.Downed).ToList();
            if (mothers.Count == 0)
            {
                return 0;
            }
            int taken = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
            {
                Pawn young = null;
                Pawn carrier = null;
                if (p.Faction == Faction.OfPlayer && RM_MothersPrice.IsStrandedYoung(p))
                {
                    young = p;
                }
                else if (p.IsColonist && p.carryTracker?.CarriedThing is Pawn c && RM_MothersPrice.IsStrandedYoung(c))
                {
                    young = c;
                    carrier = p;
                }
                if (young == null)
                {
                    continue;
                }
                IntVec3 at = carrier?.Position ?? young.Position;
                if (!RM_MothersPrice.IsWater(at, map))
                {
                    continue;
                }
                Pawn mother = mothers.FirstOrDefault(m => m.Position.DistanceTo(at) <= RM_MothersPrice.ReachOf(m));
                if (mother != null && RM_MothersPrice.TryReturn(young, carrier, mother))
                {
                    taken++;
                }
            }
            return taken;
        }

        public void CheckBuyers(int now)
        {
            foreach (Pawn p in map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer).ToList())
            {
                if (!RM_MothersPrice.IsStrandedYoung(p) || offered.Contains(p.thingIDNumber))
                {
                    continue;
                }
                if (!buyerAt.TryGetValue(p.thingIDNumber, out int at))
                {
                    buyerAt[p.thingIDNumber] = now + Rand.Range(BuyerDelayMin, BuyerDelayMax);
                    continue;
                }
                if (now >= at)
                {
                    if (RM_MothersPrice.SendBuyer(p, map))
                    {
                        offered.Add(p.thingIDNumber);
                        buyerAt.Remove(p.thingIDNumber);
                    }
                    else
                    {
                        buyerAt[p.thingIDNumber] = now + 60000;
                    }
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref offered, "offered", LookMode.Value);
            Scribe_Collections.Look(ref buyerAt, "buyerAt", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpVals);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                offered = offered ?? new List<int>();
                buyerAt = buyerAt ?? new Dictionary<int, int>();
            }
        }
    }

    /// <summary>Proof hooks for the mothers_price chain (static_call, args "current"). Each stages its own young: a
    /// player-owned juvenile of the first wild animal kind on the map with the stranded deformation, beside the mother.</summary>
    public static class RM_MothersPriceProof
    {
        private static Pawn Mother(Map map)
        {
            return map?.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.kindDef?.defName == RM_MothersPrice.MotherKind && !p.Dead);
        }

        private static Pawn SpawnMother(Map map)
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(RM_MothersPrice.MotherKind);
            if (kind == null || !CellFinder.TryFindRandomCellNear(map.Center, map, 60,
                    c => RM_MothersPrice.IsWater(c, map) && c.Standable(map), out IntVec3 cell))
            {
                return null;
            }
            return (Pawn)GenSpawn.Spawn(PawnGenerator.GeneratePawn(kind), cell, map);
        }

        private static Pawn StageYoung(Map map, Pawn mother, bool inWater)
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("Muffalo");
            Pawn y = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, Faction.OfPlayer, fixedBiologicalAge: 0.1f));
            IntVec3 cell = CellFinder.RandomClosewalkCellNear(mother.Position, map, 6,
                c => RM_MothersPrice.IsWater(c, map) == inWater);
            GenSpawn.Spawn(y, cell, map);
            y.health.AddHediff(RM_MothersPrice.StrandedDef);
            return y;
        }

        private static string State(Pawn mother, Pawn young)
        {
            Thing marker = RM_MothersPrice.CrecheOf(young);
            RM_CompCrecheYoungLedger ledger = marker?.TryGetComp<RM_CompCrecheYoungLedger>();
            return "mother=" + (mother != null) + " betrayed=" + RM_MothersPrice.MotherBetrayed(mother)
                   + " tolerated=" + RM_MothersPrice.MotherTolerates(mother)
                   + " ledger=" + (ledger != null) + " ledgerBetrayed=" + (ledger?.Betrayed ?? false)
                   + " successionVoid=" + (ledger?.SuccessionVoid ?? false)
                   + " price=" + (young?.MarketValue ?? 0f).ToString("0");
        }

        /// <summary>Sells a staged young (the PreTraded seam the trade dialog calls) and reads the mother back.</summary>
        public static string ProofSell(Map map)
        {
            map = map ?? Find.CurrentMap;
            Pawn mother = Mother(map) ?? SpawnMother(map);
            if (mother == null || RM_MothersPrice.StrandedDef == null)
            {
                return "ERROR no warden mother and no water cell for one on this map";
            }
            Pawn young = StageYoung(map, mother, false);
            string before = State(mother, young);
            string did = RM_MothersPrice.Notify_Sold(young, "the proof buyer");
            return "SOLD " + did + " before[" + before + "] after[" + State(mother, young) + "]";
        }

        /// <summary>Stages a held young in her water and runs the return check once.</summary>
        public static string ProofReturn(Map map)
        {
            map = map ?? Find.CurrentMap;
            Pawn mother = Mother(map) ?? SpawnMother(map);
            if (mother == null || RM_MothersPrice.StrandedDef == null)
            {
                return "ERROR no warden mother and no water cell for one on this map";
            }
            Pawn young = StageYoung(map, mother, true);
            int taken = map.GetComponent<RM_MapComponent_MothersPrice>()?.CheckReturns() ?? -1;
            return "RETURN taken=" + taken + " youngWild=" + (young.Faction == null) + " stillStranded="
                   + RM_MothersPrice.IsStrandedYoung(young) + " " + State(mother, young);
        }
    }
}
