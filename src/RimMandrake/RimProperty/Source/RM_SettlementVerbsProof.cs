using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Bribe;
using RimMandrake.HirePlaceless;
using RimMandrake.Pickpocket;
using RimMandrake.SalvageClaim;
using RimMandrake.WalkableCommerce;
using RimWorld;
using Verse;

namespace RimMandrake.Property
{
    // SETTLEMENT_VERBS_WAVE_1: a click-through proof of the five settlement verbs, run by the bridge with
    // jawa/static_call (type RimMandrake.Property.RM_SettlementVerbsProof, method RunOne, args = one verb name).
    // Each run, on the current map: picks a free colonist, gives it silver, spawns its own target beside it, builds the
    // REAL right-click menu (FloatMenuMakerMap.GetOptions, so the provider's own gate runs), clicks the option, reads the
    // property ledger, then turns the verb's Mod Settings toggle off and checks the option is gone. Everything it made
    // is destroyed and the silver it gave is taken back. No ticks pass inside a run.
    // Returns "PASS <verb> ..." or "FAIL <verb> <reason>"; never throws.
    //   salvage   A1  claim fee on a weakly foreign-claimed item: fee = ComputeFeeSilver, record ClaimFeePaid for the
    //                 payer, the fee scales with prior-claim strength and with recognizability (not flat)
    //   droid     A2  claim fee on a downed mechanoid pawn: record ClaimFeePaid for the payer
    //   commerce  A3  buy a merchant-claimed item: record Purchased for the buyer, price paid
    //   pickpocket A4 lift the best item off a non-hostile pawn: item moves to the thief, record Stolen for the victim
    //   hire      A5  hire a factionless pawn: record Purchased (pawn) for the payer, fee paid
    //   bribe     A6  buy a faction pawn a round: the payer's suspicion in that faction falls by bribeDampenFraction
    public static class RM_SettlementVerbsProof
    {
        private const int GiftSilver = 1000;

        public static string RunAll()
        {
            return string.Join(" ; ", new[] { "salvage", "droid", "commerce", "pickpocket", "hire", "bribe" }.Select(RunOne));
        }

        public static string RunOne(string verb)
        {
            verb = (verb ?? "").Trim().ToLowerInvariant();
            var made = new List<Thing>();
            Pawn actor = null;
            int silverBefore = 0;
            // Every verb toggle on for the run, and perception OFF so pickpocket's unauthorized Take leaves no witness
            // entry against the real colonist; all six restored on exit.
            bool[] saved = { PropertySettings.salvageClaimFeeEnabled, PropertySettings.walkableCommerceEnabled,
                PropertySettings.pickpocketEnabled, PropertySettings.hirePlacelessEnabled, PropertySettings.bribeEnabled,
                PropertySettings.perceptionEnabled };
            PropertySettings.salvageClaimFeeEnabled = PropertySettings.walkableCommerceEnabled = PropertySettings.pickpocketEnabled
                = PropertySettings.hirePlacelessEnabled = PropertySettings.bribeEnabled = true;
            PropertySettings.perceptionEnabled = false;
            try
            {
                GameComponent_PropertyLedger ledger = GameComponent_PropertyLedger.Get();
                Map map = Find.CurrentMap;
                if (ledger == null || map == null)
                {
                    return "FAIL " + verb + " no live game or no current map";
                }
                actor = map.mapPawns.FreeColonistsSpawned.FirstOrDefault(p => !p.Downed && !p.InMentalState
                    && p.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation));
                if (actor == null)
                {
                    return "FAIL " + verb + " no able free colonist on the current map";
                }
                silverBefore = SalvageClaimFeeUtility.CountSilverInInventory(actor);
                Thing silver = ThingMaker.MakeThing(ThingDefOf.Silver);
                silver.stackCount = GiftSilver;
                if (!actor.inventory.innerContainer.TryAdd(silver))
                {
                    return "FAIL " + verb + " could not put silver in " + actor.LabelShort + "'s inventory";
                }
                string result;
                switch (verb)
                {
                    case "salvage": result = Salvage(ledger, map, actor, made); break;
                    case "droid": result = Droid(ledger, map, actor, made); break;
                    case "commerce": result = Commerce(ledger, map, actor, made); break;
                    case "pickpocket": result = Pickpocket(ledger, map, actor, made); break;
                    case "hire": result = Hire(ledger, map, actor, made); break;
                    case "bribe": result = Bribe(ledger, map, actor, made); break;
                    default: return "FAIL " + verb + " unknown verb (salvage|droid|commerce|pickpocket|hire|bribe)";
                }
                return result.StartsWith("FAIL") ? result : "PASS " + verb + " " + result;
            }
            catch (Exception e)
            {
                return "FAIL " + verb + " threw " + e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                Cleanup(made, actor, silverBefore);
                PropertySettings.salvageClaimFeeEnabled = saved[0];
                PropertySettings.walkableCommerceEnabled = saved[1];
                PropertySettings.pickpocketEnabled = saved[2];
                PropertySettings.hirePlacelessEnabled = saved[3];
                PropertySettings.bribeEnabled = saved[4];
                PropertySettings.perceptionEnabled = saved[5];
            }
        }

        // ── the five verbs ────────────────────────────────────────────────────────────────────

        private static string Salvage(GameComponent_PropertyLedger ledger, Map map, Pawn actor, List<Thing> made)
        {
            Faction other = OtherFaction(actor, requireNonHostile: false, requireHumanlike: false);
            if (other == null) return "FAIL salvage no non-player faction on the world";
            Thing gun = SpawnItem("Gun_Revolver", map, actor, made);
            if (gun == null) return "FAIL salvage could not spawn Gun_Revolver beside " + actor.LabelShort;
            int now = Find.TickManager.TicksGame;
            // A weak, old foreign claim (a battlefield wreck someone else once owned).
            ledger.RecordClaim(gun, new ClaimRecord(ClaimantRef.OfCommons(other), 0.3f, ClaimBasis.BattleLootOrigin, now));

            // Not flat: the fee follows prior-claim strength and recognizability (SalvageClaimFeeUtility.ComputeFeeSilver).
            ClaimantRef o = ClaimantRef.OfCommons(other);
            int feeNone = SalvageClaimFeeUtility.ComputeFeeSilver(gun, null);
            int feeWeak = SalvageClaimFeeUtility.ComputeFeeSilver(gun, new ClaimResolution(o, 0.2f, ClaimBasis.Looted, true, now));
            int feeStrong = SalvageClaimFeeUtility.ComputeFeeSilver(gun, new ClaimResolution(o, 1f, ClaimBasis.Looted, true, now));
            // Recognizability moves the price with everything else held fixed: the same kernel ComputeFeeSilver calls,
            // at the gun's own score and at a much lower one, same strong claim.
            float recGun = RecognizabilityUtility.Score(gun);
            int feeRecLow = RM_PropertyKernel.SalvageFee(recGun * 0.25f, true, 1f, PropertySettings.salvageClaimFeeMultiplier,
                SalvageClaimFeeUtility.MinFeeSilver, SalvageClaimFeeUtility.MaxFeeSilver, SalvageClaimFeeUtility.UnclaimedStrengthFloor);
            int feeRecGun = RM_PropertyKernel.SalvageFee(recGun, true, 1f, PropertySettings.salvageClaimFeeMultiplier,
                SalvageClaimFeeUtility.MinFeeSilver, SalvageClaimFeeUtility.MaxFeeSilver, SalvageClaimFeeUtility.UnclaimedStrengthFloor);
            string scale = "fee none/weak/strong=" + feeNone + "/" + feeWeak + "/" + feeStrong
                + " recog=" + recGun.ToString("F2") + " fee@recog/quarter=" + feeRecGun + "/" + feeRecLow;
            if (!(feeStrong > feeWeak)) return "FAIL salvage fee does not rise with prior-claim strength: " + scale;
            if (!(recGun > 0f)) return "FAIL salvage a revolver scores recognizability 0: " + scale;
            if (feeRecGun != feeStrong) return "FAIL salvage ComputeFeeSilver disagrees with the kernel at the gun's score: " + scale;
            if (!(feeRecGun > feeRecLow)) return "FAIL salvage fee does not follow recognizability: " + scale;

            ClaimResolution? prior = ClaimEngine.ResolveClaim(gun, now);
            int fee = SalvageClaimFeeUtility.ComputeFeeSilver(gun, prior);
            string off = ToggleOff(() => PropertySettings.salvageClaimFeeEnabled, v => PropertySettings.salvageClaimFeeEnabled = v, map, actor, gun, "Pay salvage claim fee");
            if (off != null) return "FAIL salvage " + off;
            string clicked = Click(map, actor, gun, "Pay salvage claim fee (" + fee + " silver) on", out string menu);
            if (clicked != null) return "FAIL salvage " + clicked + "; menu: " + menu;
            string paid = CheckPaid(actor, fee);
            if (paid != null) return "FAIL salvage " + paid;
            if (!HasRecord(ledger, gun, ClaimantRef.OfPawn(actor), ClaimBasis.ClaimFeePaid)) return "FAIL salvage no ClaimFeePaid record for the payer on the gun";
            ClaimResolution? after = ClaimEngine.ResolveClaim(gun, Find.TickManager.TicksGame);
            if (!after.HasValue || !after.Value.Claimant.Equals(ClaimantRef.OfPawn(actor))) return "FAIL salvage the payer does not now hold the winning claim";
            return "A1 fee=" + fee + " ClaimFeePaid winner=payer " + scale + " toggleOff=absent";
        }

        private static string Droid(GameComponent_PropertyLedger ledger, Map map, Pawn actor, List<Thing> made)
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("Mech_Lancer")
                ?? DefDatabase<PawnKindDef>.AllDefs.FirstOrDefault(k => k.race?.race != null && k.race.race.IsMechanoid && k.race.race.baseBodySize < 2f);
            if (kind == null) return "FAIL droid no mechanoid PawnKindDef";
            Pawn mech = SpawnPawn(kind, Faction.OfMechanoids, map, actor, made);
            if (mech == null) return "FAIL droid could not spawn " + kind.defName;
            HealthUtility.DamageUntilDowned(mech, false);
            if (mech.Dead || !mech.Downed) return "FAIL droid " + kind.defName + " is not downed-and-alive after DamageUntilDowned (dead=" + mech.Dead + ")";
            int now = Find.TickManager.TicksGame;
            ClaimResolution? prior = ClaimEngine.ResolveClaim(mech, now);
            int fee = SalvageClaimFeeUtility.ComputeFeeSilver(mech, prior);
            string clicked = Click(map, actor, mech, "Pay salvage claim fee (" + fee + " silver) on", out string menu);
            if (clicked != null) return "FAIL droid " + clicked + "; menu: " + menu;
            string paid = CheckPaid(actor, fee);
            if (paid != null) return "FAIL droid " + paid;
            if (!HasRecord(ledger, mech, ClaimantRef.OfPawn(actor), ClaimBasis.ClaimFeePaid)) return "FAIL droid no ClaimFeePaid record for the payer on the mech";
            return "A2 " + kind.defName + " downed fee=" + fee + " prior=" + (prior.HasValue ? prior.Value.Basis.ToString() : "none") + " ClaimFeePaid";
        }

        private static string Commerce(GameComponent_PropertyLedger ledger, Map map, Pawn actor, List<Thing> made)
        {
            Faction merchant = OtherFaction(actor, requireNonHostile: false, requireHumanlike: false);
            if (merchant == null) return "FAIL commerce no non-player faction on the world";
            Thing ware = SpawnItem("Gun_Revolver", map, actor, made);
            if (ware == null) return "FAIL commerce could not spawn Gun_Revolver";
            ledger.RecordClaim(ware, new ClaimRecord(ClaimantRef.OfCommons(merchant), 1f, ClaimBasis.Purchased, Find.TickManager.TicksGame));
            int price = BuyMerchandiseUtility.ComputePriceSilver(ware);
            string off = ToggleOff(() => PropertySettings.walkableCommerceEnabled, v => PropertySettings.walkableCommerceEnabled = v, map, actor, ware, "Buy " + ware.LabelShort + " (");
            if (off != null) return "FAIL commerce " + off;
            string clicked = Click(map, actor, ware, "Buy " + ware.LabelShort + " (" + price + " silver)", out string menu);
            if (clicked != null) return "FAIL commerce " + clicked + "; menu: " + menu;
            string paid = CheckPaid(actor, price);
            if (paid != null) return "FAIL commerce " + paid;
            if (!HasRecord(ledger, ware, ClaimantRef.OfPawn(actor), ClaimBasis.Purchased)) return "FAIL commerce no Purchased record for the buyer";
            return "A3 price=" + price + " Purchased toggleOff=absent";
        }

        private static string Pickpocket(GameComponent_PropertyLedger ledger, Map map, Pawn actor, List<Thing> made)
        {
            Faction f = OtherFaction(actor, requireNonHostile: true, requireHumanlike: true);
            if (f == null) return "FAIL pickpocket no non-hostile humanlike faction on the world";
            Pawn mark = SpawnPawn(f.def.basicMemberKind, f, map, actor, made);
            if (mark == null) return "FAIL pickpocket could not spawn a " + f.Name + " pawn";
            Thing gold = ThingMaker.MakeThing(ThingDefOf.Gold);
            gold.stackCount = 20;
            mark.inventory.innerContainer.TryAdd(gold);
            Thing loot = PickpocketUtility.FindStealableItem(mark);
            if (loot == null) return "FAIL pickpocket FindStealableItem found nothing on a pawn carrying 20 gold";
            string clicked = Click(map, actor, mark, "Pickpocket " + loot.LabelShort + " from", out string menu);
            if (clicked != null) return "FAIL pickpocket " + clicked + "; menu: " + menu;
            if (!actor.inventory.innerContainer.Contains(loot)) return "FAIL pickpocket " + loot.LabelShort + " is not in the thief's inventory";
            if (mark.inventory.innerContainer.Contains(loot)) return "FAIL pickpocket the victim still holds " + loot.LabelShort;
            made.Add(loot);
            if (!HasRecord(ledger, loot, ClaimantRef.OfPawn(mark), ClaimBasis.Stolen)) return "FAIL pickpocket no Stolen record naming the victim";
            Thing gold2 = ThingMaker.MakeThing(ThingDefOf.Gold);
            gold2.stackCount = 20;
            mark.inventory.innerContainer.TryAdd(gold2);
            string off = ToggleOff(() => PropertySettings.pickpocketEnabled, v => PropertySettings.pickpocketEnabled = v, map, actor, mark, "Pickpocket ");
            if (off != null) return "FAIL pickpocket " + off;
            return "A4 took " + loot.LabelShort + " Stolen(victim) toggleOff=absent";
        }

        private static string Hire(GameComponent_PropertyLedger ledger, Map map, Pawn actor, List<Thing> made)
        {
            Pawn drifter = SpawnPawn(PawnKindDefOf.WildMan, null, map, actor, made);
            if (drifter == null) return "FAIL hire could not spawn a factionless WildMan";
            if (drifter.Faction != null) return "FAIL hire the WildMan came with faction " + drifter.Faction.Name;
            int fee = HirePlacelessUtility.ComputeHireFeeSilver();
            string clicked = Click(map, actor, drifter, "Hire " + drifter.LabelShort + " (" + fee + " silver)", out string menu);
            if (clicked != null) return "FAIL hire " + clicked + "; menu: " + menu;
            string paid = CheckPaid(actor, fee);
            if (paid != null) return "FAIL hire " + paid;
            if (!HasRecord(ledger, drifter, ClaimantRef.OfPawn(actor), ClaimBasis.Purchased)) return "FAIL hire no Purchased record on the hired pawn";
            return "A5 fee=" + fee + " Purchased(pawn)";
        }

        private static string Bribe(GameComponent_PropertyLedger ledger, Map map, Pawn actor, List<Thing> made)
        {
            Faction f = OtherFaction(actor, requireNonHostile: true, requireHumanlike: true);
            if (f == null) return "FAIL bribe no non-hostile humanlike faction on the world";
            Pawn drinker = SpawnPawn(f.def.basicMemberKind, f, map, actor, made);
            if (drinker == null) return "FAIL bribe could not spawn a " + f.Name + " pawn";
            int now = Find.TickManager.TicksGame;
            ClaimantRef suspect = ClaimantRef.OfPawn(actor);
            FactionRecord rec = ledger.GetOrCreateFactionRecord(f);
            // Snapshot the colonist's real entries in this faction so the run can put them back exactly.
            var entries = (List<WitnessEntry>)typeof(FactionRecord).GetField("entries",
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic).GetValue(rec);
            var real = entries.Where(e => e.Suspect.Equals(suspect)).ToDictionary(e => e, e => e.Confidence);
            float frac = PropertySettings.bribeDampenFraction;
            int fee = BribeUtility.ComputeBribeFeeSilver();
            try
            {
                // Silence them for the run, so the reading is the planted entry alone and never clamped at 1.
                foreach (WitnessEntry e in real.Keys) e.Confidence = 0f;
                // A witness two days old, so its contribution has propagated above zero (a fresh entry reads 0).
                rec.RegisterWitness(suspect, 0.5f, now - 2 * GenDate.TicksPerDay);
                float before = rec.GetSuspicion(suspect, now);
                if (before <= 0f) return "FAIL bribe instrument blind: a 2-day-old 0.5 witness reads suspicion " + before;
                string clicked = Click(map, actor, drinker, "Buy " + drinker.LabelShort + " a round (" + fee + " silver)", out string menu);
                if (clicked != null) return "FAIL bribe " + clicked + "; menu: " + menu;
                string paid = CheckPaid(actor, fee);
                if (paid != null) return "FAIL bribe " + paid;
                float afterS = rec.GetSuspicion(suspect, now);
                float want = before * (1f - frac);
                string nums = "suspicion " + before.ToString("F4") + " -> " + afterS.ToString("F4") + " want " + want.ToString("F4");
                if (!(afterS < before) || Math.Abs(afterS - want) > 0.02f * Math.Max(1e-3f, before) + 1e-4f) return "FAIL bribe " + nums;
                string off = ToggleOff(() => PropertySettings.bribeEnabled, v => PropertySettings.bribeEnabled = v, map, actor, drinker, "Buy " + drinker.LabelShort + " a round");
                if (off != null) return "FAIL bribe " + off;
                return "A6 fee=" + fee + " " + nums + " toggleOff=absent";
            }
            finally
            {
                // drop the planted entry, restore the real ones' confidence
                entries.RemoveAll(e => e.Suspect.Equals(suspect) && !real.ContainsKey(e));
                foreach (KeyValuePair<WitnessEntry, float> kv in real) kv.Key.Confidence = kv.Value;
            }
        }

        // ── helpers ───────────────────────────────────────────────────────────────────────────

        // Builds the real right-click menu for `actor` on `target`'s cell and clicks the option whose label starts with
        // `labelStart`. Returns null on a click, else why not; `menu` lists the labels seen.
        private static string Click(Map map, Pawn actor, Thing target, string labelStart, out string menu)
        {
            Find.Selector.ClearSelection();
            Find.Selector.Select(actor, false, false);
            List<FloatMenuOption> opts = FloatMenuMakerMap.GetOptions(new List<Pawn> { actor }, target.TrueCenter(), out FloatMenuContext _);
            menu = string.Join(" / ", opts.Select(o => o.Label));
            FloatMenuOption hit = opts.FirstOrDefault(o => o.Label.StartsWith(labelStart));
            if (hit == null) return "no option starting '" + labelStart + "'";
            if (hit.Disabled || hit.action == null) return "option '" + hit.Label + "' is disabled";
            lastSilver = SalvageClaimFeeUtility.CountSilverInInventory(actor);
            hit.action();
            return null;
        }

        // Runs while the option is still offered (the caller clicks it after, or re-arms the target), so "absent" means
        // the toggle removed it. Restores the toggle to its value on entry.
        private static string ToggleOff(Func<bool> get, Action<bool> set, Map map, Pawn actor, Thing target, string labelStart)
        {
            bool was = get();
            set(false);
            try
            {
                Find.Selector.ClearSelection();
                Find.Selector.Select(actor, false, false);
                List<FloatMenuOption> opts = FloatMenuMakerMap.GetOptions(new List<Pawn> { actor }, target.TrueCenter(), out FloatMenuContext _);
                FloatMenuOption hit = opts.FirstOrDefault(o => o.Label.StartsWith(labelStart));
                return hit == null ? null : "toggle off still offers '" + hit.Label + "'";
            }
            finally
            {
                set(was);
            }
        }

        private static string CheckPaid(Pawn actor, int amount)
        {
            int have = SalvageClaimFeeUtility.CountSilverInInventory(actor);
            return have == lastSilver - amount ? null : "silver went " + lastSilver + " -> " + have + ", want -" + amount;
        }

        // Silver in hand just before the last click (set by Click).
        private static int lastSilver;

        private static bool HasRecord(GameComponent_PropertyLedger ledger, Thing thing, ClaimantRef who, ClaimBasis basis)
        {
            return ledger.TryGetRecords(thing, out List<ClaimRecord> recs) && recs.Any(r => r.Basis == basis && r.Claimant.Equals(who));
        }

        private static Faction OtherFaction(Pawn actor, bool requireNonHostile, bool requireHumanlike)
        {
            return Find.FactionManager.AllFactionsListForReading.FirstOrDefault(f => !f.IsPlayer && !f.defeated && !f.Hidden
                && (!requireNonHostile || !f.HostileTo(actor.Faction))
                && (!requireHumanlike || (f.def.humanlikeFaction && f.def.basicMemberKind != null)));
        }

        private static bool FreeCell(IntVec3 c, Map map)
        {
            return c.InBounds(map) && c.Standable(map) && !c.Fogged(map) && c.GetFirstItem(map) == null && c.GetFirstPawn(map) == null;
        }

        private static IntVec3 CellBeside(Map map, Pawn actor)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(actor.Position, 6f, false))
            {
                if (FreeCell(c, map) && actor.CanReach(c, Verse.AI.PathEndMode.Touch, Danger.Deadly)) return c;
            }
            return IntVec3.Invalid;
        }

        private static Thing SpawnItem(string defName, Map map, Pawn actor, List<Thing> made)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            IntVec3 cell = CellBeside(map, actor);
            if (def == null || !cell.IsValid) return null;
            Thing t = ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
            GenSpawn.Spawn(t, cell, map);
            made.Add(t);
            return t;
        }

        private static Pawn SpawnPawn(PawnKindDef kind, Faction faction, Map map, Pawn actor, List<Thing> made)
        {
            IntVec3 cell = CellBeside(map, actor);
            if (kind == null || !cell.IsValid) return null;
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, faction, forceGenerateNewPawn: true));
            GenSpawn.Spawn(p, cell, map);
            made.Add(p);
            return p;
        }

        private static void Cleanup(List<Thing> made, Pawn actor, int silverBefore)
        {
            GameComponent_PropertyLedger ledger = GameComponent_PropertyLedger.Get();
            foreach (Thing t in made)
            {
                try
                {
                    ledger?.ClearForeignClaims(t, ClaimantRef.Unclaimed);
                    if (t.ParentHolder is Pawn_InventoryTracker inv) inv.innerContainer.Remove(t);
                    if (!t.Destroyed) t.Destroy(DestroyMode.Vanish);
                }
                catch (Exception e)
                {
                    Log.Warning("[RM_SettlementVerbsProof] cleanup of " + t + " threw " + e.Message);
                }
            }
            if (actor != null)
            {
                int extra = SalvageClaimFeeUtility.CountSilverInInventory(actor) - silverBefore;
                if (extra > 0) SalvageClaimFeeUtility.RemoveSilverFromInventory(actor, extra);
                Find.Selector.ClearSelection();
            }
        }
    }
}
