using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_MECHANICS_BUILD_1 part 6 — the ripple.
    //
    // Owner ruling Q9 (card, 2026-10-15): "Ripple -> Hiding with a faint shimmer". Small wild creatures under the
    // fuzz cannot be targeted; the player still sees them as a shimmer.
    //
    // Mechanism (no new engine): the vanilla HediffComp_Invisibility on RM_RippleHidden with visibleToPlayer=true.
    // Read from the decompiled 1.6 source (RimSage):
    //   InvisibilityUtility.IsPsychologicallyInvisible -> a pawn with that hediff is not targetable (Verb, hunting,
    //     predators: FoodUtility skips invisible prey, turrets: GenHostility).
    //   PawnRenderer: an invisible pawn is drawn through InvisibilityMatPool (the distortion shimmer);
    //   HediffComp_Invisibility.GetAlpha returns 1 when visibleToPlayer, so the player sees a full-strength shimmer
    //   instead of nothing. That is the "faint shimmer over the hidden ones"; it is feedback, not a warning meter.
    //   Damage, burning, being carried or downed force it visible (vanilla ForcedVisible).
    //
    // Cover = a plant whose def carries RM_RippleCoverExtension (Patches/RM_Ripple_Cover.xml puts it on the fuzz
    // carpet). Who hides is RM_RippleKernel.Hidden: wild, not downed, on cover, body size within the limit (doubled in
    // the Gale), and not moving during the Stall or in a windbreak's calm wake (part 2, leanWakesEnabled).
    // Gate: modEnabled && rippleEnabled. Off: every hidden creature is shown again on the next pass.
    // ════════════════════════════════════════════════════════════════════
    public class RM_RippleCoverExtension : DefModExtension
    {
    }

    public class RM_MapComponent_Ripple : MapComponent
    {
        private bool anyHidden = true; // true after load so the first pass sweeps up saved hediffs
        private readonly List<Pawn> tmpPawns = new List<Pawn>();

        public RM_MapComponent_Ripple(Map map) : base(map)
        {
        }

        public static bool OnCover(Pawn p)
        {
            Plant plant = p.Position.GetPlant(p.Map);
            return plant != null && plant.def.GetModExtension<RM_RippleCoverExtension>() != null;
        }

        public bool ShouldHide(Pawn p, bool on)
        {
            bool wild = p.Faction == null && p.RaceProps.Animal;
            bool cover = wild && OnCover(p);
            bool still = RM_WindCalendar.IsStall(map) || (on && cover && InWindbreakLee(p.Position));
            return RM_RippleKernel.Hidden(on, wild, p.Downed, cover, p.BodySize,
                RM_LeaningScrubSettings.rippleMaxBodySize, RM_WindCalendar.IsGale(map), still,
                p.pather != null && p.pather.Moving);
        }

        /// <summary>Part 2 windbreak calm wake: a wind-blocking edifice (vanilla ThingDef.blockWind, the field wind
        /// turbines read) within WakeLength cells upwind on a leaning map. Gate: leanWakesEnabled.</summary>
        public bool InWindbreakLee(IntVec3 c)
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.leanWakesEnabled)) return false;
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            if (lean == null) return false;
            UnityEngine.Vector2 dir = lean.Downwind;
            return RM_RippleKernel.InLee(c.x, c.z, dir.x, dir.y, RM_RippleKernel.WakeLength, (x, z) =>
            {
                IntVec3 u = new IntVec3(x, 0, z);
                if (!u.InBounds(map)) return false;
                Building b = u.GetEdifice(map);
                return b != null && b.def.blockWind;
            });
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % RM_RippleKernel.CheckInterval != 0)
            {
                return;
            }
            Pass();
        }

        /// <summary>One hide/show pass over the map. Returns how many creatures are hidden after it.</summary>
        public int Pass()
        {
            bool on = RM_WindCalendar.On(RM_LeaningScrubSettings.rippleEnabled);
            HediffDef def = RM_LeaningScrubDefOf.RM_RippleHidden;
            if (!on && !anyHidden)
            {
                return 0;
            }
            int hidden = 0;
            tmpPawns.Clear();
            tmpPawns.AddRange(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn p = tmpPawns[i];
                if (p.Dead || p.health == null)
                {
                    continue;
                }
                Hediff have = p.health.hediffSet.GetFirstHediffOfDef(def);
                bool want = ShouldHide(p, on);
                if (want && have == null)
                {
                    p.health.AddHediff(def);
                }
                else if (!want && have != null)
                {
                    p.health.RemoveHediff(have);
                }
                if (want)
                {
                    hidden++;
                }
            }
            tmpPawns.Clear();
            anyHidden = hidden > 0;
            return hidden;
        }
    }

    // Proof hook for jawa/static_call (validation.py chain "ripple"). Spawns a small wild animal on a cover cell, drives
    // the SHIPPED pass under each wind state, reads the invisibility state, cleans up.
    public static class RM_RippleProof
    {
        public static string ProofRipple(string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            var comp = map.GetComponent<RM_MapComponent_Ripple>();
            if (comp == null) return "FAIL: RM_MapComponent_Ripple not on the map";
            IntVec3 cell = IntVec3.Invalid;
            foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant))
            {
                if (t.def.GetModExtension<RM_RippleCoverExtension>() != null && t.Position.Standable(map) && t.Position.GetFirstPawn(map) == null)
                {
                    cell = t.Position;
                    break;
                }
            }
            if (!cell.IsValid) return "UNMEASURED: no fuzz cover plant on this map";
            PawnKindDef kind = null;
            foreach (PawnKindDef k in DefDatabase<PawnKindDef>.AllDefsListForReading)
            {
                if (k.RaceProps != null && k.RaceProps.Animal && k.race.race.baseBodySize <= 0.3f && !k.RaceProps.Dryad) { kind = k; break; }
            }
            if (kind == null) return "UNMEASURED: no small animal kind loaded";
            bool savedMod = RM_LeaningScrubSettings.modEnabled, savedRipple = RM_LeaningScrubSettings.rippleEnabled;
            WeatherDef savedWeather = map.weatherManager.curWeather;
            Pawn p = null;
            try
            {
                RM_LeaningScrubSettings.modEnabled = true;
                RM_LeaningScrubSettings.rippleEnabled = mode != "off";
                p = PawnGenerator.GeneratePawn(kind);
                GenSpawn.Spawn(p, cell, map);
                comp.Pass();
                bool hiddenWind = p.IsPsychologicallyInvisible();
                map.weatherManager.curWeather = RM_LeaningScrubDefOf.RM_Stall;
                comp.Pass();
                bool hiddenStallStill = p.IsPsychologicallyInvisible();
                map.weatherManager.curWeather = savedWeather;
                string st = string.Format("kind={0} wind={1} stallStill={2}", kind.defName, hiddenWind, hiddenStallStill);
                if (mode == "off")
                {
                    return hiddenWind ? "FAIL: rippleEnabled off but the creature hid " + st : "PASS off " + st;
                }
                if (savedWeather == RM_LeaningScrubDefOf.RM_Stall) return "UNMEASURED: the map is in the Stall; run again in wind " + st;
                if (!hiddenWind) return "FAIL: small wild creature on fuzz in wind was not hidden " + st;
                if (!hiddenStallStill) return "FAIL: a still creature in the Stall lost its cover " + st;
                return "PASS " + st;
            }
            finally
            {
                map.weatherManager.curWeather = savedWeather;
                if (p != null && !p.Destroyed) p.Destroy();
                RM_LeaningScrubSettings.modEnabled = savedMod;
                RM_LeaningScrubSettings.rippleEnabled = savedRipple;
            }
        }
    }
}
