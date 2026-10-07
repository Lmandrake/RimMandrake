using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.KeelHoist
{
    // HOIST_FIXED_SITE_FRAMES_1 (design §2a, §2c target 3, §5 row 2).
    //
    // RM_HoistFrame: the keel hoist's comp on a fixed head-frame. Never player-buildable (its def has no
    // designationCategory and no research); only RM_GenStep_HoistFrames places one, beside a portal or holder
    // whose ThingDef carries RM_HoistFrameSiteExtension, and pairs its cable there for good. It needs no power
    // and has no tether (it is not on a ship). Anyone on the site map can load it or raise its cradle.
    public class RM_HoistFrame : RM_KeelHoist
    {
        public override bool FixedCable => true;
    }

    /// <summary>
    /// Target kind 3: a sealed building that holds pawns nobody can enter (the Hutt oubliette is the first use,
    /// HUTT_SLAVE_PIT_TEST_SITE_1). A hoist may lower pawns into it at any time; it lifts them out only once the
    /// gate opens: the holder is ours or unowned, the map's owner is us, or no able member of its faction is left
    /// on the map (design §1b: "if you attacked the place and took it over").
    /// </summary>
    public class RM_SealedHolder : Building, IThingHolder
    {
        private ThingOwner<Pawn> held;

        public RM_SealedHolder()
        {
            held = new ThingOwner<Pawn>(this, oneStackOnly: false);
        }

        public int HeldCount => held.Count;

        public ThingOwner GetDirectlyHeldThings() => held;

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Deep.Look(ref held, "held", this);
            Scribe_Collections.Look(ref sales, "sales", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && held == null)
            {
                held = new ThingOwner<Pawn>(this, oneStackOnly: false);
            }
            if (Scribe.mode == LoadSaveMode.PostLoadInit && sales == null)
            {
                sales = new List<RM_PitSaleRecord>();
            }
        }

        // HUTT_SLAVE_PIT_SITE_BUILD_1: a holder whose def carries RM_PitBuyerExtension is a buyer pit. Its keepers
        // pay for what a hoist lowers into it while they hold the place and are not at war with the player.
        public List<RM_PitSaleRecord> sales = new List<RM_PitSaleRecord>();

        public RM_PitBuyerExtension Buyer => def.GetModExtension<RM_PitBuyerExtension>();

        public bool KeepersBuying => RM_HoistKernel.KeepersBuying(Buyer != null, KeelHoistSettings.pitSales,
            Faction != null && Faction != Faction.OfPlayer, Faction != null && Faction.HostileTo(Faction.OfPlayer), GateOpen(out _));

        public virtual bool CanAccept(Pawn p, out string reason)
        {
            reason = null;
            switch (RM_HoistKernel.HolderRefusal(Buyer != null, p.IsColonist, p.IsSlave, Faction != null && Faction.HostileTo(Faction.OfPlayer),
                Faction != null && Faction != Faction.OfPlayer, GateOpen(out _)))
            {
                case "own":
                    reason = Buyer.buyerLabel.CapitalizeFirst() + " will not take one of your own colonists, and you would not get them back.";
                    return false;
                case "enemy":
                    reason = Buyer.buyerLabel.CapitalizeFirst() + " do not deal with enemies.";
                    return false;
            }
            return true;
        }

        /// <summary>Takes the pawn in. `via` is the hoist that lowered it (the silver goes back up its cable).</summary>
        public bool Accept(Pawn p, RM_KeelHoist via = null, bool sale = true)
        {
            if (!CanAccept(p, out string reason))
            {
                if (via != null && reason != null)
                {
                    Messages.Message(reason, this, MessageTypeDefOf.RejectInput, historical: false);
                }
                return false;
            }
            bool paying = sale && via != null && KeepersBuying;
            int price = paying ? RM_PitBuyerUtility.PriceFor(p, this) : 0;
            bool fighter = paying && RM_PitBuyerUtility.IsFighter(p) && RM_PitBuyerUtility.ArenaWantsFightersNow(this);
            if (p.Spawned)
            {
                p.DeSpawnOrDeselect();
            }
            p.holdingOwner?.Remove(p);
            if (!held.TryAdd(p, canMergeWithExistingStacks: false))
            {
                return false;
            }
            if (paying)
            {
                string label = p.LabelShortCap;
                RM_PitBuyerUtility.TransferToBuyer(p, Faction);
                RM_PitBuyerUtility.SendSilverUp(via, price, LabelCap);
                sales.Add(new RM_PitSaleRecord { tick = Find.TickManager.TicksGame, label = label, silver = price, fighter = fighter });
                string where = fighter
                    ? "Fighters fetch more this week: " + label + " is bound for " + Buyer.arenaLabel + "."
                    : label + " goes to " + Buyer.workLabel + ".";
                Find.LetterStack.ReceiveLetter("Sold to the pit: " + label,
                    Buyer.buyerLabel.CapitalizeFirst() + " paid " + price + " silver for " + label + ". The silver is coming up the cable.\n\n" + where,
                    LetterDefOf.NeutralEvent, new LookTargets(via));
            }
            return true;
        }

        public List<Pawn> TakeAll()
        {
            List<Pawn> list = held.InnerListForReading.ToList();
            foreach (Pawn p in list)
            {
                held.Remove(p);
            }
            return list;
        }

        public bool GateOpen(out string reason)
        {
            reason = null;
            Faction owner = Faction;
            bool ownerFree = owner == null || owner == Faction.OfPlayer || owner.defeated;
            bool keepersLeft = !ownerFree && Map?.ParentFaction != Faction.OfPlayer && Map != null && Map.mapPawns.SpawnedPawnsInFaction(owner)
                .Any(p => !p.Dead && !p.Downed && !p.IsPrisoner && !p.IsSlave);
            if (!RM_HoistKernel.GateOpen(ownerFree, Map?.ParentFaction == Faction.OfPlayer, keepersLeft))
            {
                reason = LabelCap + " is sealed while " + owner.Name + " hold this place.";
                return false;
            }
            return true;
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string mine = "Holds " + held.Count + ". " + (GateOpen(out string why) ? "Its keepers are gone: a hoist can lift them out." : "Sealed.");
            if (KeepersBuying)
            {
                mine += "\n" + Buyer.buyerLabel.CapitalizeFirst() + " buy what a hoist lowers in (" + sales.Count + " sold here)."
                        + (RM_PitBuyerUtility.ArenaWantsFightersNow(this) ? " Fighters fetch more this week." : "");
            }
            return s.NullOrEmpty() ? mine : s + "\n" + mine;
        }

        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            if (Spawned && held.Count > 0)
            {
                held.TryDropAll(Position, Map, ThingPlaceMode.Near);
            }
            base.Destroy(mode);
        }
    }

    /// <summary>On a portal or holder ThingDef: "a fixed head-frame stands beside me", with this chance.</summary>
    public class RM_HoistFrameSiteExtension : DefModExtension
    {
        public float chance = 1f;
        public ThingDef frameDef;
        public float maxDistance = 6f;
        public Rot4 rotation = Rot4.South;
    }

    /// <summary>
    /// Places RM_HoistFrame beside every spawned thing whose def carries RM_HoistFrameSiteExtension (rolled per
    /// thing) and pairs the frame's cable to it. Registered on Base_Player after the portal scatterers.
    /// </summary>
    public class RM_GenStep_HoistFrames : GenStep
    {
        public override int SeedPart => 61140411;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!KeelHoistSettings.masterEnabled)
            {
                return;
            }
            var sites = map.listerThings.AllThings
                .Where(t => t.def.HasModExtension<RM_HoistFrameSiteExtension>() && (t is MapPortal || t is RM_SealedHolder))
                .ToList();
            foreach (Thing site in sites)
            {
                if (site is RM_KeelHoist)
                {
                    continue;
                }
                RM_HoistFrameSiteExtension ext = site.def.GetModExtension<RM_HoistFrameSiteExtension>();
                if (!Rand.Chance(ext.chance))
                {
                    continue;
                }
                ThingDef frameDef = ext.frameDef ?? DefDatabase<ThingDef>.GetNamedSilentFail("RM_HoistFrame");
                if (frameDef == null)
                {
                    continue;
                }
                if (!TryFindFrameCell(map, site, frameDef, ext, out IntVec3 cell))
                {
                    continue;
                }
                Thing built = GenSpawn.Spawn(ThingMaker.MakeThing(frameDef), cell, map, ext.rotation);
                if (built is RM_KeelHoist frame)
                {
                    frame.LowerCableTo(new LocalTargetInfo(site));
                }
            }
        }

        public static bool TryFindFrameCell(Map map, Thing site, ThingDef frameDef, RM_HoistFrameSiteExtension ext, out IntVec3 found)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(site.Position, ext.maxDistance, true).InRandomOrder())
            {
                CellRect rect = GenAdj.OccupiedRect(c, ext.rotation, frameDef.Size);
                if (rect.Overlaps(site.OccupiedRect().ExpandedBy(1)))
                {
                    continue;
                }
                bool ok = true;
                foreach (IntVec3 r in rect)
                {
                    if (!r.InBounds(map) || !r.Standable(map) || r.GetEdifice(map) != null || r.GetFirstBuilding(map) != null)
                    {
                        ok = false;
                        break;
                    }
                }
                if (ok)
                {
                    found = c;
                    return true;
                }
            }
            found = IntVec3.Invalid;
            return false;
        }
    }
}
