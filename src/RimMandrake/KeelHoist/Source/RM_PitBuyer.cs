using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.KeelHoist
{
    // HUTT_SLAVE_PIT_SITE_BUILD_1 (design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md §3a, RULED).
    // The generic half of the Hutt slave pit: a sealed holder whose keepers BUY what a hoist lowers into it, a site
    // part that lays out the pit, its fixed head-frame and its keepers, and a quest node that offers such a site.
    // Every name, faction and pawn kind is data on the defs (RUT_ tier: UtinniPatches/Defs/.../RUT_HuttSlavePit.xml).

    /// <summary>On an RM_SealedHolder def: its keepers pay for what is lowered into it, while they hold the place.</summary>
    public class RM_PitBuyerExtension : DefModExtension
    {
        public string buyerLabel = "the keepers";
        public string arenaLabel = "the arena";
        public string workLabel = "the work gangs";
    }

    public class RM_PitSaleRecord : IExposable
    {
        public int tick;
        public string label;
        public int silver;
        public bool fighter;

        public void ExposeData()
        {
            Scribe_Values.Look(ref tick, "tick");
            Scribe_Values.Look(ref label, "label");
            Scribe_Values.Look(ref silver, "silver");
            Scribe_Values.Look(ref fighter, "fighter");
        }
    }

    public static class RM_PitBuyerUtility
    {
        public const int MeleeFighterSkill = 8;
        public const float BeastFighterCombatPower = 100f;

        public static bool IsFighter(Pawn p)
        {
            if (p.RaceProps.Humanlike)
            {
                return p.skills?.GetSkill(SkillDefOf.Melee)?.Level >= MeleeFighterSkill;
            }
            return p.kindDef != null && p.kindDef.combatPower >= BeastFighterCombatPower;
        }

        /// <summary>One week in two (seeded per pit, so every reader agrees) the arena is short of fighters.</summary>
        public static bool ArenaWantsFightersNow(Thing pit)
        {
            if (!KeelHoistSettings.pitArenaHints)
            {
                return false;
            }
            int week = Find.TickManager.TicksGame / (GenDate.TicksPerDay * 7);
            return Rand.ChanceSeeded(0.5f, Gen.HashCombineInt(week, pit.thingIDNumber));
        }

        public static int PriceFor(Pawn p, Thing pit)
        {
            float price = p.MarketValue * KeelHoistSettings.pitPriceMultiplier;
            if (IsFighter(p) && ArenaWantsFightersNow(pit))
            {
                price *= KeelHoistSettings.arenaFighterBonus;
            }
            return Mathf.Max(1, Mathf.RoundToInt(price));
        }

        /// <summary>The pawn becomes the buyer's: a person as their slave, a beast as their animal.</summary>
        public static void TransferToBuyer(Pawn p, Faction buyer)
        {
            if (p.RaceProps.Humanlike && p.guest != null)
            {
                p.guest.SetGuestStatus(buyer, GuestStatus.Slave);
            }
            else if (p.Faction != buyer)
            {
                p.SetFaction(buyer);
            }
        }

        /// <summary>Silver comes back up the cable: one transit per stack, so no stack exceeds its limit.</summary>
        public static void SendSilverUp(RM_KeelHoist hoist, int amount, string from)
        {
            while (amount > 0)
            {
                Thing silver = ThingMaker.MakeThing(ThingDefOf.Silver);
                silver.stackCount = Mathf.Min(amount, ThingDefOf.Silver.stackLimit);
                amount -= silver.stackCount;
                hoist.BeginTransit(silver, up: true, from: from);
            }
        }
    }

    /// <summary>
    /// Lays out a buyer pit on the site map: the sealed holder with its held slaves, a fixed head-frame with its cable
    /// already down the shaft, and the keepers standing guard. The faction is the site's own.
    /// </summary>
    public class RM_BuyerPitSiteExtension : DefModExtension
    {
        public ThingDef holderDef;
        public ThingDef frameDef;
        public ThingDef chuteDef;   // HUTT_LOTTERY_CHUTE_BUILD_1: the house's chance chute, if any
        public PawnKindDef keeperKind;
        public PawnKindDef guardKind;
        public IntRange guardCount = new IntRange(2, 4);
        public List<PawnKindDef> heldKinds = new List<PawnKindDef>();
        public IntRange heldCount = new IntRange(3, 6);
        public FactionDef factionDef;
        public IntRange tileDistance = new IntRange(2, 8);
    }

    public class RM_SitePartWorker_BuyerPit : SitePartWorker
    {
        public override void PostMapGenerate(Map map)
        {
            base.PostMapGenerate(map);
            Site site = map.Parent as Site;
            SitePart part = site?.parts?.FirstOrDefault(sp => sp.def == def);
            Faction faction = part?.site?.Faction ?? site?.Faction;
            RM_BuyerPitSiteExtension ext = def.GetModExtension<RM_BuyerPitSiteExtension>();
            if (ext?.holderDef == null)
            {
                return;
            }
            LayOut(map, ext, faction);
        }

        /// <summary>Public so the proof can lay a pit out on any map (RM_PitBuyerProof).</summary>
        public static RM_SealedHolder LayOut(Map map, RM_BuyerPitSiteExtension ext, Faction faction)
        {
            IntVec3 center = map.Center;
            if (!TryFindClearRect(map, center, ext.holderDef.size, 25, out IntVec3 holderCell))
            {
                return null;
            }
            ClearRect(map, GenAdj.OccupiedRect(holderCell, Rot4.North, ext.holderDef.size).ExpandedBy(4));
            Thing built = ThingMaker.MakeThing(ext.holderDef);
            if (faction != null)
            {
                built.SetFaction(faction);
            }
            RM_SealedHolder holder = GenSpawn.Spawn(built, holderCell, map) as RM_SealedHolder;
            if (holder == null)
            {
                return null;
            }

            int held = ext.heldCount.RandomInRange;
            for (int i = 0; i < held && ext.heldKinds.Count > 0; i++)
            {
                Pawn slave = PawnGenerator.GeneratePawn(new PawnGenerationRequest(ext.heldKinds.RandomElement(), null,
                    PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true, mustBeCapableOfViolence: false));
                if (faction != null)
                {
                    RM_PitBuyerUtility.TransferToBuyer(slave, faction);
                }
                holder.Accept(slave, sale: false);
            }

            ThingDef frameDef = ext.frameDef ?? DefDatabase<ThingDef>.GetNamedSilentFail("RM_HoistFrame");
            var frameExt = new RM_HoistFrameSiteExtension { frameDef = frameDef, maxDistance = 7f };
            if (frameDef != null && RM_GenStep_HoistFrames.TryFindFrameCell(map, holder, frameDef, frameExt, out IntVec3 frameCell))
            {
                if (GenSpawn.Spawn(ThingMaker.MakeThing(frameDef), frameCell, map, frameExt.rotation) is RM_KeelHoist frame)
                {
                    frame.LowerCableTo(new LocalTargetInfo(holder));
                }
            }

            if (ext.chuteDef != null && RM_GenStep_HoistFrames.TryFindFrameCell(map, holder, ext.chuteDef,
                    new RM_HoistFrameSiteExtension { maxDistance = 11f }, out IntVec3 chuteCell))
            {
                Thing chute = ThingMaker.MakeThing(ext.chuteDef);
                if (faction != null)
                {
                    chute.SetFaction(faction);
                }
                GenSpawn.Spawn(chute, chuteCell, map);
            }

            if (faction != null)
            {
                var keepers = new List<Pawn>();
                if (ext.keeperKind != null)
                {
                    keepers.Add(PawnGenerator.GeneratePawn(ext.keeperKind, faction));
                }
                if (ext.guardKind != null)
                {
                    int guards = ext.guardCount.RandomInRange;
                    for (int i = 0; i < guards; i++)
                    {
                        keepers.Add(PawnGenerator.GeneratePawn(ext.guardKind, faction));
                    }
                }
                foreach (Pawn k in keepers)
                {
                    IntVec3 c = CellFinder.StandableCellNear(holder.Position, map, 8f);
                    GenSpawn.Spawn(k, c.IsValid ? c : holder.Position, map);
                }
                if (keepers.Count > 0)
                {
                    LordMaker.MakeNewLord(faction, new LordJob_DefendPoint(holder.Position, 6f, 10f), map, keepers);
                }
            }
            return holder;
        }

        private static bool TryFindClearRect(Map map, IntVec3 near, IntVec2 size, int radius, out IntVec3 found)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, radius, true))
            {
                CellRect rect = GenAdj.OccupiedRect(c, Rot4.North, size).ExpandedBy(1);
                if (rect.InBounds(map) && rect.Cells.All(x => x.Standable(map) && x.GetFirstBuilding(map) == null))
                {
                    found = c;
                    return true;
                }
            }
            found = IntVec3.Invalid;
            return false;
        }

        private static void ClearRect(Map map, CellRect rect)
        {
            foreach (IntVec3 c in rect.ClipInsideMap(map))
            {
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if (t is Plant || t.def.category == ThingCategory.Filth)
                    {
                        t.Destroy();
                    }
                }
            }
        }
    }

    /// <summary>Makes a buyer-pit site a few tiles from the map and stores it as `site`.</summary>
    public class RM_QuestNode_BuyerPitSite : QuestNode
    {
        public SlateRef<SitePartDef> sitePart;
        public SlateRef<string> storeSiteAs = "site";
        public SlateRef<string> storeFactionAs = "keepers";

        private static Faction FactionFor(SitePartDef def)
        {
            FactionDef fd = def?.GetModExtension<RM_BuyerPitSiteExtension>()?.factionDef;
            if (fd == null)
            {
                return null;
            }
            return Find.FactionManager.AllFactions.FirstOrDefault(f => f.def == fd && !f.defeated && !f.HostileTo(Faction.OfPlayer));
        }

        protected override bool TestRunInt(Slate slate)
        {
            SitePartDef def = sitePart.GetValue(slate);
            Map map = slate.Get<Map>("map") ?? QuestGen_Get.GetMap();
            RM_BuyerPitSiteExtension ext = def?.GetModExtension<RM_BuyerPitSiteExtension>();
            return KeelHoistSettings.masterEnabled && KeelHoistSettings.pitSites && map != null && ext != null && FactionFor(def) != null
                   && TileFinder.TryFindNewSiteTile(out PlanetTile _, map.Tile, ext.tileDistance.min, ext.tileDistance.max);
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            SitePartDef def = sitePart.GetValue(slate);
            Map map = slate.Get<Map>("map") ?? QuestGen_Get.GetMap();
            RM_BuyerPitSiteExtension ext = def.GetModExtension<RM_BuyerPitSiteExtension>();
            Faction faction = FactionFor(def);
            if (map == null || faction == null
                || !TileFinder.TryFindNewSiteTile(out PlanetTile tile, map.Tile, ext.tileDistance.min, ext.tileDistance.max))
            {
                return;
            }
            Site site = SiteMaker.MakeSite(def, tile, faction);
            slate.Set(storeSiteAs.GetValue(slate), site);
            slate.Set(storeFactionAs.GetValue(slate), faction);
        }
    }

    /// <summary>Dev proofs, called through jawa/static_call (the pattern every later suite uses).</summary>
    public static class RM_PitBuyerProof
    {
        /// <summary>Lays out the named site part's pit on the current map, owned by its faction.</summary>
        public static string ProofLayOut(string sitePartDefName)
        {
            Map map = Find.CurrentMap;
            SitePartDef def = DefDatabase<SitePartDef>.GetNamedSilentFail(sitePartDefName);
            RM_BuyerPitSiteExtension ext = def?.GetModExtension<RM_BuyerPitSiteExtension>();
            if (map == null || ext == null)
            {
                return "UNMEASURED no map or no RM_BuyerPitSiteExtension on " + sitePartDefName;
            }
            Faction faction = Find.FactionManager.AllFactions.FirstOrDefault(f => f.def == ext.factionDef && !f.defeated);
            RM_SealedHolder holder = RM_SitePartWorker_BuyerPit.LayOut(map, ext, faction);
            if (holder == null)
            {
                return "FAIL no room for the pit";
            }
            RM_KeelHoist frame = map.listerThings.AllThings.OfType<RM_KeelHoist>().FirstOrDefault(h => h.targetHolder == holder);
            int keepers = faction == null ? 0 : map.mapPawns.SpawnedPawnsInFaction(faction).Count;
            RM_ChanceChute chute = map.listerThings.AllThings.OfType<RM_ChanceChute>().FirstOrDefault(c => c.Faction == faction);
            return string.Format("LAIDOUT holder={0} held={1} frame={2} keepers={3} faction={4} gate={5} chute={6}",
                holder.ThingID, holder.HeldCount, frame?.ThingID ?? "none", keepers, faction?.Name ?? "none", holder.GateOpen(out _),
                chute?.ThingID ?? "none");
        }

        /// <summary>
        /// Sells one pawn through the pit's frame: a fresh prisoner of the colony (kind) is put straight into transit
        /// down the cable, the clock is run past its cycle, and the silver that came up is counted.
        /// </summary>
        public static string ProofSell(string pawnKindDefName)
        {
            Map map = Find.CurrentMap;
            RM_KeelHoist frame = map?.listerThings.AllThings.OfType<RM_KeelHoist>().FirstOrDefault(h => h.targetHolder != null
                && h.targetHolder.def.HasModExtension<RM_PitBuyerExtension>());
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(pawnKindDefName);
            if (frame == null || kind == null)
            {
                return "UNMEASURED no buyer pit with a frame on this map (run ProofLayOut first) or no kind " + pawnKindDefName;
            }
            RM_SealedHolder pit = frame.targetHolder;
            int heldBefore = pit.HeldCount;
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true));
            GenSpawn.Spawn(p, CellFinder.StandableCellNear(frame.Position, map, 5f), map);
            if (p.RaceProps.Humanlike)
            {
                p.guest.CapturedBy(Faction.OfPlayer);
            }
            else
            {
                p.SetFaction(Faction.OfPlayer);
            }
            int expected = RM_PitBuyerUtility.PriceFor(p, pit);
            frame.BeginTransit(p, up: false, from: "proof");
            frame.DebugArriveAllNow();
            frame.DebugArriveAllNow();   // the silver's own trip up
            int silverAfter = map.listerThings.ThingsOfDef(ThingDefOf.Silver).Sum(t => t.stackCount);
            // a humanlike buyer's slave keeps its own Faction; the buyer is its HostFaction (guest status Slave)
            bool sold = pit.HeldCount == heldBefore + 1 && (p.Faction == pit.Faction || p.HostFaction == pit.Faction);
            return string.Format("{0} pawn={1} price={2} silverOnMap={3} held={4}->{5} faction={6} sales={7}",
                sold ? "SOLD" : "NOTSOLD", p.LabelShort, expected, silverAfter, heldBefore, pit.HeldCount, (p.Faction?.Name ?? "none") + "/host=" + (p.HostFaction?.Name ?? "none"),
                pit.sales.Count);
        }

        /// <summary>Raises the cradle and reports the gate: sealed while keepers stand, open once they are gone.</summary>
        public static string ProofGate(string mode)
        {
            Map map = Find.CurrentMap;
            RM_KeelHoist frame = map?.listerThings.AllThings.OfType<RM_KeelHoist>().FirstOrDefault(h => h.targetHolder != null);
            if (frame == null)
            {
                return "UNMEASURED no frame with a holder on this map";
            }
            RM_SealedHolder pit = frame.targetHolder;
            if (mode == "conquer" && pit.Faction != null)
            {
                foreach (Pawn k in map.mapPawns.SpawnedPawnsInFaction(pit.Faction).ToList())
                {
                    k.Kill(null);
                }
            }
            bool open = pit.GateOpen(out string why);
            int before = pit.HeldCount;
            frame.RaiseCradle();
            frame.DebugArriveAllNow();
            int prisoners = map.mapPawns.PrisonersOfColonySpawned.Count;
            return string.Format("GATE open={0} heldBefore={1} heldAfter={2} prisonersOfColony={3} why={4}",
                open, before, pit.HeldCount, prisoners, why ?? "-");
        }

    }
}
