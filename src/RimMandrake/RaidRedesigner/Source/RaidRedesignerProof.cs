// RAIDREDESIGNER_COVERAGE_GAPS_1 -- live proof hooks for the north-star script (jawa/static_call).
// ProofRoster drives the REAL GameComponent_OldFriends.RecordEncounter (cap/prune, idempotence, role upgrade-only,
// grudge/notability multiplier + clamps, master switch, pinning on/off, dead collapse) on a scratch roster;
// ProofHooks calls the SHIPPED Harmony postfix bodies (flee, escaped, released, captured, kidnapper) directly with
// generated pawns -- the engine events cannot be triggered from the bridge, the hook bodies can. The real roster,
// settings and world-pawn pins are restored in finally. Property-dependent BetrayedTrader is not touched here (it
// would load RimMandrakeProperty.dll).
using System.Collections.Generic;
using System.Globalization;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.RaidRedesigner
{
    public static class RaidRedesignerProof
    {
        private static string B(bool v) => v ? "True" : "False";

        private static Pawn Make(Faction f)
        {
            return PawnGenerator.GeneratePawn(PawnKindDefOf.Villager, f);
        }

        private static void Release(Pawn p)
        {
            try
            {
                WorldPawns wp = Find.WorldPawns;
                if (wp != null)
                {
                    wp.ForcefullyKeptPawns.Remove(p);
                    if (wp.Contains(p)) wp.RemoveAndDiscardPawnViaGC(p);
                }
                if (!p.Destroyed && !p.Spawned) p.Destroy();
            }
            catch (System.Exception) { }
        }

        private static OldFriendEntry Find1(GameComponent_OldFriends c, Pawn p)
        {
            for (int i = 0; i < c.Entries.Count; i++)
                if (c.Entries[i].Pawn == p) return c.Entries[i];
            return null;
        }

        public static string ProofRoster(string args)
        {
            GameComponent_OldFriends comp = GameComponent_OldFriends.Instance;
            if (comp == null) return "ERROR no GameComponent_OldFriends (no game running)";
            bool wasOn = RaidRedesignerSettings.rosterTrackingEnabled;
            int wasMax = RaidRedesignerSettings.maxLivingEntries;
            float wasMult = RaidRedesignerSettings.grudgeNotabilityMultiplier;
            bool wasPin = RaidRedesignerSettings.pinEncounteredPawns;
            List<OldFriendEntry> real = comp.ProofSwapEntries(new List<OldFriendEntry>());
            List<Pawn> made = new List<Pawn>();
            try
            {
                Faction f = Find.FactionManager.FirstFactionOfDef(FactionDefOf.Pirate) ?? Faction.OfPlayer;
                RaidRedesignerSettings.rosterTrackingEnabled = true;
                RaidRedesignerSettings.maxLivingEntries = 3;
                RaidRedesignerSettings.grudgeNotabilityMultiplier = 1f;
                RaidRedesignerSettings.pinEncounteredPawns = true;
                Pawn p1 = Make(f), p2 = Make(f), p3 = Make(f), p4 = Make(f), p5 = Make(f);
                made.Add(p1); made.Add(p2); made.Add(p3); made.Add(p4); made.Add(p5);

                OldFriendEntry e1 = comp.RecordEncounter(p1, f, RoleTag.FledRaider, 100, "a", 10, 5, false);
                string s = "a_count=" + comp.Entries.Count + " a_grudge=" + e1.Grudge + " a_notab=" + e1.Notability + " a_enc=" + e1.Encounters.Count;
                comp.RecordEncounter(p1, f, RoleTag.Captain, 200, "b");
                s += " b_count=" + comp.Entries.Count + " b_role=" + e1.Role + " b_enc=" + e1.Encounters.Count + " b_seen=" + e1.LastSeenTick;
                comp.RecordEncounter(p1, f, RoleTag.FledRaider, 300, "c");
                s += " c_role=" + e1.Role;
                comp.RecordEncounter(p2, f, RoleTag.FledRaider, 400, "p2", 0, 20);
                comp.RecordEncounter(p3, f, RoleTag.FledRaider, 500, "p3", 0, 30);
                comp.RecordEncounter(p4, f, RoleTag.FledRaider, 600, "p4", 0, 40);
                s += " cap_count=" + comp.Entries.Count + " cap_p1=" + B(Find1(comp, p1) != null) + " cap_p4=" + B(Find1(comp, p4) != null);

                RaidRedesignerSettings.grudgeNotabilityMultiplier = 2f;
                OldFriendEntry e2 = comp.RecordEncounter(p2, f, RoleTag.FledRaider, 700, "m", 10, 10);
                s += " mult_grudge=" + e2.Grudge + " mult_notab=" + e2.Notability;
                comp.RecordEncounter(p2, f, RoleTag.FledRaider, 710, "hi", 200, 200);
                s += " clamp_grudge_hi=" + e2.Grudge + " clamp_notab_hi=" + e2.Notability;
                comp.RecordEncounter(p2, f, RoleTag.FledRaider, 720, "lo", -200, -200);
                s += " clamp_grudge_lo=" + e2.Grudge + " clamp_notab_lo=" + e2.Notability;
                RaidRedesignerSettings.grudgeNotabilityMultiplier = 1f;

                int before = comp.Entries.Count;
                RaidRedesignerSettings.rosterTrackingEnabled = false;
                OldFriendEntry off = comp.RecordEncounter(p5, f, RoleTag.FledRaider, 800, "off", 5, 5, true);
                s += " off_null=" + B(off == null) + " off_count=" + (comp.Entries.Count - before)
                    + " off_pinned=" + B(Find.WorldPawns.ForcefullyKeptPawns.Contains(p5));
                RaidRedesignerSettings.rosterTrackingEnabled = true;

                OldFriendEntry e3 = Find1(comp, p3);
                int total0 = comp.Entries.Count;
                e3.MarkDead(1000, "died");
                comp.RecordEncounter(p5, f, RoleTag.FledRaider, 900, "p5", 0, 50);
                s += " dead_flag=" + B(e3.Dead) + " dead_summary_has_cause=" + B(e3.DeadSummary != null && e3.DeadSummary.Contains("died"))
                    + " dead_kept=" + B(Find1(comp, p3) != null) + " dead_total=" + comp.Entries.Count;
                string once = e3.DeadSummary;
                e3.MarkDead(2000, "again");
                s += " dead_idempotent=" + B(once == e3.DeadSummary);

                RaidRedesignerSettings.maxLivingEntries = 30;
                RaidRedesignerSettings.pinEncounteredPawns = true;
                Pawn p6 = Make(f), p7 = Make(f), p8 = Make(f);
                made.Add(p6); made.Add(p7); made.Add(p8);
                comp.RecordEncounter(p6, f, RoleTag.FledRaider, 1000, "pin", 0, 1, true);
                s += " pin_on=" + B(Find.WorldPawns.ForcefullyKeptPawns.Contains(p6));
                comp.RecordEncounter(p8, f, RoleTag.FledRaider, 1000, "nopinarg", 0, 1, false);
                s += " pin_arg_false=" + B(Find.WorldPawns.ForcefullyKeptPawns.Contains(p8));
                RaidRedesignerSettings.pinEncounteredPawns = false;
                comp.RecordEncounter(p7, f, RoleTag.FledRaider, 1000, "setoff", 0, 1, true);
                s += " pin_setting_off=" + B(Find.WorldPawns.ForcefullyKeptPawns.Contains(p7));
                return s;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                comp.ProofSwapEntries(real);
                RaidRedesignerSettings.rosterTrackingEnabled = wasOn;
                RaidRedesignerSettings.maxLivingEntries = wasMax;
                RaidRedesignerSettings.grudgeNotabilityMultiplier = wasMult;
                RaidRedesignerSettings.pinEncounteredPawns = wasPin;
                for (int i = 0; i < made.Count; i++) Release(made[i]);
            }
        }

        public static string ProofHooks(string args)
        {
            GameComponent_OldFriends comp = GameComponent_OldFriends.Instance;
            if (comp == null) return "ERROR no GameComponent_OldFriends (no game running)";
            bool wasOn = RaidRedesignerSettings.rosterTrackingEnabled;
            bool wasPin = RaidRedesignerSettings.pinEncounteredPawns;
            int wasMax = RaidRedesignerSettings.maxLivingEntries;
            List<OldFriendEntry> real = comp.ProofSwapEntries(new List<OldFriendEntry>());
            List<Pawn> made = new List<Pawn>();
            try
            {
                RaidRedesignerSettings.rosterTrackingEnabled = true;
                RaidRedesignerSettings.pinEncounteredPawns = true;
                RaidRedesignerSettings.maxLivingEntries = 40;
                Faction pirate = Find.FactionManager.FirstFactionOfDef(FactionDefOf.Pirate);
                Faction other = null;
                foreach (Faction fac in Find.FactionManager.AllFactionsListForReading)
                    if (!fac.IsPlayer && !fac.Hidden && fac != pirate && fac.def.humanlikeFaction) { other = fac; break; }
                Map map = Find.CurrentMap;
                string s = "pirate=" + B(pirate != null) + " other=" + B(other != null) + " map_home=" + B(map != null && map.IsPlayerHome);
                if (pirate == null) return s;

                Pawn flee = Make(pirate); made.Add(flee);
                if (map != null && map.IsPlayerHome)
                {
                    Patch_FledRaiderAndCaptain.Postfix(flee, map);
                    OldFriendEntry e = Find1(comp, flee);
                    s += " flee_role=" + (e == null ? "-" : e.Role.ToString()) + " flee_grudge=" + (e == null ? -1 : e.Grudge)
                        + " flee_pinned=" + B(Find.WorldPawns.ForcefullyKeptPawns.Contains(flee));
                    Pawn friend = Make(Faction.OfPlayer); made.Add(friend);
                    Patch_FledRaiderAndCaptain.Postfix(friend, map);
                    s += " flee_friend_recorded=" + B(Find1(comp, friend) != null);
                }
                else s += " flee_role=- flee_grudge=- flee_pinned=- flee_friend_recorded=-";

                Pawn esc = Make(pirate); made.Add(esc);
                Patch_PrisonerEscaped.Postfix(esc);
                OldFriendEntry ee = Find1(comp, esc);
                s += " esc_role=" + (ee == null ? "-" : ee.Role.ToString()) + " esc_grudge=" + (ee == null ? -1 : ee.Grudge)
                    + " esc_pinned=" + B(Find.WorldPawns.ForcefullyKeptPawns.Contains(esc));

                Pawn rel = Make(pirate); made.Add(rel);
                Patch_PrisonerReleased.Postfix(rel);
                OldFriendEntry er = Find1(comp, rel);
                s += " rel_blackstar_role=" + (er == null ? "-" : er.Role.ToString()) + " rel_blackstar_grudge=" + (er == null ? -99 : er.Grudge);
                if (other != null)
                {
                    Pawn rel2 = Make(other); made.Add(rel2);
                    Patch_PrisonerReleased.Postfix(rel2);
                    OldFriendEntry er2 = Find1(comp, rel2);
                    s += " rel_other_role=" + (er2 == null ? "-" : er2.Role.ToString());
                }
                else s += " rel_other_role=-";

                Pawn cap = Make(pirate); made.Add(cap);
                Patch_NamedHunterCaptured.Postfix(Faction.OfPlayer, cap);
                OldFriendEntry ec = Find1(comp, cap);
                s += " cap_role=" + (ec == null ? "-" : ec.Role.ToString()) + " cap_notab=" + (ec == null ? -1 : ec.Notability)
                    + " cap_pinned=" + B(Find.WorldPawns.ForcefullyKeptPawns.Contains(cap));
                Pawn notmine = Make(pirate); made.Add(notmine);
                Patch_NamedHunterCaptured.Postfix(pirate, notmine);
                s += " cap_not_by_player_recorded=" + B(Find1(comp, notmine) != null);

                Pawn kid = Make(pirate); made.Add(kid);
                Pawn victim = Make(Faction.OfPlayer); made.Add(victim);
                Patch_ColonistKidnapped.Postfix(victim, kid);
                OldFriendEntry ek = Find1(comp, kid);
                s += " kid_role=" + (ek == null ? "-" : ek.Role.ToString()) + " kid_grudge=" + (ek == null ? -1 : ek.Grudge)
                    + " kid_names_victim=" + B(ek != null && ek.Encounters.Count > 0 && ek.Encounters[0].Summary.Contains(victim.LabelShortCap));
                Patch_ColonistKidnapped.Postfix(victim, null);

                int count = comp.Entries.Count;
                RaidRedesignerSettings.rosterTrackingEnabled = false;
                Pawn off = Make(pirate); made.Add(off);
                Patch_PrisonerEscaped.Postfix(off);
                s += " hook_off_recorded=" + B(Find1(comp, off) != null) + " hook_off_count_delta=" + (comp.Entries.Count - count);
                return s;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                comp.ProofSwapEntries(real);
                RaidRedesignerSettings.rosterTrackingEnabled = wasOn;
                RaidRedesignerSettings.pinEncounteredPawns = wasPin;
                RaidRedesignerSettings.maxLivingEntries = wasMax;
                for (int i = 0; i < made.Count; i++) Release(made[i]);
            }
        }
    }
}
