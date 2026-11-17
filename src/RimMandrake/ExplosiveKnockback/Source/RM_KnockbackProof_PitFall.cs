#if RM_PROOFS
// Proof build only (RM_PROOFS). sc_pit_fall (design/concepts/ExplosiveKnockback/scenes.json, bar thrown_into_pit_falls) as the
// scene writes it: an open lane (a colonist and a stack beside a 1-wide open pit) and a covered lane (a colonist and a stack
// aimed at a 1-wide covered pit), one blast between them; every lane's planned landing cell lies beyond the pit's far rim
// (asserted from the launch journal, INVALID otherwise). pit_colonist_control: the same throws with no pit, landing on the
// planned cell beyond the rim, no descent. RIMMANDRAKE_DROP_THROWS_INTO_COVERED_PITS_K08_MUST_FLIP: the kernel treated a cover
// as ground and a thrown pawn never broke one, and the scene had no covered lane to see it. pit_enemy keeps its own staging.
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    public static partial class RM_KnockbackProof
    {
        // the open lane runs east (+x), the covered lane west (-x), from one blast at the origin; each pit is 1 wide, 3 deep
        // in z, its cell on the throw line RimDx cells out, and each lane starts StartDx cells out beside the blast
        private const int PitFallStartDx = 1, PitFallRimDx = 3;

        private static string PitFall(Scene s)
        {
            bool control = s.name == "pit_colonist_control";
            if (!RM_KnockbackCompat.FlowWorks)
            {
                return "FlowWorks not loaded";
            }
            if (!control)
            {
                if (!Pit(O(s, PitFallRimDx, -1), 1, 3) || !Pit(O(s, -PitFallRimDx, -1), 1, 3))
                {
                    return "could not dig the pits";
                }
                foreach (IntVec3 c in new CellRect(s.o.x - PitFallRimDx, s.o.z - 1, 1, 3))
                {
                    Build("RM_PitCover_WovenScrap", c);
                }
                if (RM_KnockbackCompat.CoverAt(Map, O(s, -PitFallRimDx, 0)) == null)
                {
                    return "the cover over the west pit is not intact after building it";
                }
            }
            Colonist(s, "p", O(s, PitFallStartDx, 0));
            Item(s, "s", "Steel", 10, O(s, PitFallStartDx, 0));
            Colonist(s, "pc", O(s, -PitFallStartDx, 0));
            Item(s, "sc", "Steel", 10, O(s, -PitFallStartDx, 0));
            // the blast reaches the throwers (distance 1) and not the cover (distance 3 > 2.9), so only a landing can break it
            Blast(s.o, 2.9f);
            s.verdict = sc => PitFallVerdict(sc, control);
            return null;
        }

        private static string PitFallVerdict(Scene sc, bool control)
        {
            var lanes = new[] { ("p", "s", 1), ("pc", "sc", -1) };
            var parts = new List<string>();
            bool ok = true;
            foreach ((string pk, string sk, int dir) in lanes)
            {
                bool covered = dir < 0;
                IntVec3 pitCell = O(sc, dir * PitFallRimDx, 0);
                Thing p = sc.things[pk], st = sc.things[sk];
                var launch = ForThing(sc, "launch", p);
                var move = ForThing(sc, "item_move", st);
                if (launch.Count != 1 || move.Count != 1)
                {
                    return "INVALID " + sc.name + " " + pk + " launches=" + launch.Count + " " + sk + " moves=" + move.Count + " (want 1 each)";
                }
                int pPlanned = System.Convert.ToInt32(launch[0]["planned"]), sPlanned = System.Convert.ToInt32(move[0]["planned"]);
                // the planned landing cell beyond the far rim: an untouched throw would cross the pit (sc_pit_fall start)
                int reach = PitFallRimDx - PitFallStartDx;
                if (pPlanned <= reach || sPlanned <= reach)
                {
                    return "INVALID " + sc.name + " " + pk + " planned " + pPlanned + ", " + sk + " planned " + sPlanned
                        + " cells: not beyond the far rim (want > " + reach + ")";
                }
                var land = ForThing(sc, "land", p);
                var desc = ForThing(sc, "descent", p);
                var sLand = ForThing(sc, "item_land", st);
                IntVec3 pAt = land.Count == 1 ? (IntVec3)land[0]["at"] : IntVec3.Invalid;
                IntVec3 sAt = sLand.Count == 1 ? (IntVec3)sLand[0]["to"] : IntVec3.Invalid;
                Pawn pp = p as Pawn;
                bool pInPit = pp != null && pp.Spawned && RM_KnockbackCompat.IsSuperdeep(Map, pp.Position);
                bool sInPit = st.Spawned && RM_KnockbackCompat.IsSuperdeep(Map, st.Position) && RM_KnockbackCompat.CoverAt(Map, st.Position) == null;
                string line = (covered ? "covered" : "open") + ": " + pk + " planned=" + pPlanned + " landed=" + pAt.x + "," + pAt.z
                    + " descents=" + desc.Count + " inPit=" + pInPit + "; " + sk + " planned=" + sPlanned + " landed=" + sAt.x + "," + sAt.z
                    + " lands=" + sLand.Count + " inPit=" + sInPit;
                bool laneOk;
                if (control)
                {
                    // no pit: each lands on flat ground on its planned cell, beyond where the rim would be, and nothing descends
                    IntVec3 pTo = (IntVec3)launch[0]["to"], sTo = (IntVec3)move[0]["to"];
                    laneOk = pAt == pTo && sAt == sTo && dir * (pAt.x - sc.o.x) > PitFallRimDx && dir * (sAt.x - sc.o.x) > PitFallRimDx
                        && desc.Count == 0 && !pInPit && !sInPit;
                }
                else
                {
                    laneOk = pAt == pitCell && desc.Count == 1 && pInPit && sAt == pitCell && sLand.Count == 1 && sInPit;
                    if (covered)
                    {
                        // broken by a landing of this lane, not by the blast: the cover_break line names the colonist or the stack
                        var breaks = Recs(sc, "cover_break").Where(r => r.TryGetValue("thingId", out object id)
                            && (System.Convert.ToInt32(id) == p.thingIDNumber || System.Convert.ToInt32(id) == st.thingIDNumber) && r["broken"] is bool b && b).ToList();
                        bool gone = RM_KnockbackCompat.CoverAt(Map, pitCell) == null;
                        if (gone && breaks.Count == 0)
                        {
                            return "INVALID " + sc.name + " the cover went without a landing breaking it (the blast reached it?): " + line;
                        }
                        laneOk &= gone && breaks.Count == 1;
                        line += " coverGone=" + gone + " breaksByLanding=" + breaks.Count;
                    }
                }
                ok &= laneOk;
                parts.Add(line);
            }
            return Result(sc, ok, string.Join(" | ", parts));
        }
    }
}
#endif
