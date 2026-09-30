using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.Warcasket
{
    // WARCASKET_CASK_BAY_AND_SARCOPHAGI_1 — the lead-lined cask bay.
    // The owner approved ("7) yrs", WASTELAND_BEDAZZLE_SITTING_1 turn 2,
    // 2026-09-28) this slate item, verbatim: "The lead-lined cask bay
    // (gravship touch) — a shielded hardpoint that lets the ship haul the
    // Throat's casks, unlocking your own authored waste-run dilemma (the five
    // destinations, each a moral verdict)." It is a gravship hazmat hold,
    // NOT a warcasket crafting bench.
    //
    // The building (RM_CaskBay.xml) is a Building_Storage that needs gravship
    // substructure, so it flies with the ship. This comp is the "shielded"
    // half: every rare tick it holds each stored cask's vanilla
    // CompDissolution clock at zero (a wastepack in the bay never dissolves
    // or pollutes), and SarcophagusCoreDose reads IsShielded() so a core in
    // the bay gives off no dose.
    //
    // Mod Settings: caskBayShieldingEnabled. Off: the bay is ordinary
    // cask-only storage and casks inside dissolve/dose as they would anywhere.

    public class RM_CompProperties_CaskShielding : CompProperties
    {
        public RM_CompProperties_CaskShielding()
        {
            compClass = typeof(RM_CompCaskShielding);
        }
    }

    public class RM_CompCaskShielding : ThingComp
    {
        // CompDissolution.dissolveTicks is private; read once, no Harmony.
        private static readonly FieldInfo DissolveTicksField =
            typeof(CompDissolution).GetField("dissolveTicks", BindingFlags.Instance | BindingFlags.NonPublic);

        public static bool ShieldingActive =>
            RM_WarcasketSettings.masterEnabled && RM_WarcasketSettings.caskBayShieldingEnabled;

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!ShieldingActive || !parent.Spawned || DissolveTicksField == null)
            {
                return;
            }
            Map map = parent.Map;
            foreach (IntVec3 c in parent.OccupiedRect())
            {
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    CompDissolution diss = things[i].TryGetComp<CompDissolution>();
                    if (diss != null)
                    {
                        DissolveTicksField.SetValue(diss, 0);
                    }
                }
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!ShieldingActive)
            {
                return "Shielding disabled in Mod Settings: stored casks behave as they would anywhere.";
            }
            return "Lead-lined: stored casks neither dissolve nor dose.";
        }

        // True when the thing (or whatever holds it) sits on a cell of a
        // spawned cask bay with shielding active.
        public static bool IsShielded(Thing t)
        {
            if (!ShieldingActive || t == null)
            {
                return false;
            }
            Map map = t.MapHeld;
            if (map == null || !t.Spawned)
            {
                return false;
            }
            List<Thing> things = t.Position.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is ThingWithComps twc && twc.GetComp<RM_CompCaskShielding>() != null)
                {
                    return true;
                }
            }
            return false;
        }
    }

    // The half-extracted core's hazard: a loose core doses the pawns around
    // it through vanilla ToxicUtility (the dose-layer ruling: "mostly
    // pollution mechanism"), so ToxicResistance / ToxicEnvironmentResistance
    // — a warcasket's own 0.9 — apply. Carried or in an inventory it doses
    // its holder's surroundings. In a shielded cask bay it is silent.
    public class RM_CompProperties_CoreDose : CompProperties
    {
        public float radius = 4f;

        // extraFactor on vanilla's per-CheckInterval dose at the core
        // (1 = standing on polluted ground); falls linearly to 0 at radius.
        public float toxicFactor = 1f;

        public RM_CompProperties_CoreDose()
        {
            compClass = typeof(RM_CompCoreDose);
        }
    }

    public class RM_CompCoreDose : ThingComp
    {
        // Dose every 4 rare ticks, scaled so the rate matches vanilla's
        // per-ToxicUtility.CheckInterval figure.
        private const int RaresPerDose = 4;
        private int rareCount;

        private RM_CompProperties_CoreDose Props => (RM_CompProperties_CoreDose)props;

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (++rareCount < RaresPerDose)
            {
                return;
            }
            rareCount = 0;
            if (!RM_WarcasketSettings.masterEnabled || !RM_WarcasketSettings.coreDoseEnabled)
            {
                return;
            }
            Map map = parent.MapHeld;
            if (map == null || RM_CompCaskShielding.IsShielded(parent))
            {
                return;
            }
            IntVec3 pos = parent.PositionHeld;
            float rateScale = (float)(GenTicks.TickRareInterval * RaresPerDose) / ToxicUtility.CheckInterval;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead)
                {
                    continue;
                }
                float dist = p.Position.DistanceTo(pos);
                if (dist > Props.radius)
                {
                    continue;
                }
                float falloff = 1f - dist / (Props.radius + 1f);
                ToxicUtility.DoPawnToxicDamage(p, Props.toxicFactor * falloff * rateScale);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WarcasketSettings.masterEnabled || !RM_WarcasketSettings.coreDoseEnabled)
            {
                return null;
            }
            return RM_CompCaskShielding.IsShielded(parent)
                ? "Shielded in a cask bay: no dose."
                : "Unshielded: doses everyone within " + Props.radius.ToString("0") + " cells.";
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref rareCount, "rareCount", 0);
        }
    }
}
