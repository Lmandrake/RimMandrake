using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// One entry in the wild-droid pool. A plain class with plain fields and a
    /// plain &lt;li&gt; list - deliberately NOT vanilla's PawnGenOption, which
    /// carries a LoadDataFromXmlCustom and therefore has to be written as
    /// &lt;KindDefName&gt;weight&lt;/KindDefName&gt;; a stray &lt;li&gt; against
    /// such a field silently discards the WHOLE containing def with no error.
    /// </summary>
    public class WildDroidOption
    {
        public PawnKindDef kind;
        public float weight = 1f;
    }

    /// <summary>
    /// DROIDWORKS_WILD_DROIDS_1 (packet E4). Data half of the incident, so the
    /// pool can be re-weighted or extended in XML without touching the DLL.
    /// </summary>
    public class WildDroidCrashExtension : DefModExtension
    {
        public List<WildDroidOption> options = new List<WildDroidOption>();
    }

    /// <summary>
    /// DROIDWORKS_WILD_DROIDS_1 (packet E4). The owner's ruling 2, verbatim:
    /// "there's the wild droids that have gone crazy from being left out in the
    /// desert after crashing". One such droid walks in off the map edge,
    /// belonging to NO faction (ruling 2 also forbids a rogue-droid faction
    /// outright), in ManhunterPermanent - and can then be downed, captured, and
    /// reprogrammed with RSW_DW_DataSpike_Wild, whose factionless key
    /// (CompDWDataSpike.Props.factionless) was built for exactly this pawn.
    ///
    /// Shaped after vanilla IncidentWorker_AggressiveAnimals: same entry-cell
    /// finder, same spawn-then-TryStartMentalState order, same
    /// SignalForceNormalSpeedShort. Three deliberate differences:
    ///
    /// 1. ONE droid, never a pack. MentalState_Manhunter.ForceHostileTo(Thing)
    ///    returns true for a factionless pawn if that pawn is Humanlike - and
    ///    every Droidworks droid race IS humanlike (HAR). Two wild droids on
    ///    the same map would therefore be force-hostile to EACH OTHER and
    ///    brawl on arrival instead of coming for the colony. Vanilla never
    ///    hits this because its manhunters are animals, which that same line
    ///    excludes. If a pack is ever wanted, it needs a faction or a
    ///    different mental state, not a bigger count here.
    ///
    /// 2. No points scaling and no combatPower-driven kind choice. Every
    ///    utility droid kind in this mod carries the combatPower 99999
    ///    sentinel (PawnKinds_OuterRim.xml's own convention, "never picked by
    ///    a points-based raid pool"), so any Cost/points arithmetic over this
    ///    pool would silently exclude precisely the abandoned-labour droids
    ///    that are the most on-theme. The pool is a flat weighted pick.
    ///
    /// 3. No exitMapAfterTick. A humanlike pawn in MentalState_Manhunter runs
    ///    the MentalStateNonCritical subtree (SubTrees_Misc.xml), which holds
    ///    JobGiver_Manhunter and JobGiver_WanderAnywhere and no exit-map
    ///    giver at all - setting the tick would have promised a departure the
    ///    think tree never delivers. The droid stays until it is killed or
    ///    taken, which is also the honest fiction: it has nowhere to go.
    /// </summary>
    public class IncidentWorker_WildDroidCrash : IncidentWorker
    {
        private PawnKindDef PickKind()
        {
            WildDroidCrashExtension ext = def.GetModExtension<WildDroidCrashExtension>();
            if (ext == null || ext.options.NullOrEmpty()) return null;

            IEnumerable<WildDroidOption> legal = ext.options.Where(o => o?.kind != null && o.weight > 0f);
            if (!legal.Any()) return null;
            return legal.RandomElementByWeight(o => o.weight).kind;
        }

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms)) return false;
            if (!(parms.target is Map map)) return false;
            if (PickKind() == null) return false;
            return RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 _, map, CellFinder.EdgeRoadChance_Animal);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            if (!(parms.target is Map map)) return false;

            PawnKindDef kind = PickKind();
            if (kind == null) return false;

            IntVec3 entry = parms.spawnCenter;
            if (!entry.IsValid &&
                !RCellFinder.TryFindRandomPawnEntryCell(out entry, map, CellFinder.EdgeRoadChance_Animal))
            {
                return false;
            }

            // faction: null is the whole point of the packet - it is what makes
            // RSW_DW_DataSpike_Wild (factionless=true) the only spike that will
            // ever match this pawn, and it is what ruling 2 requires.
            Pawn droid = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                kind,
                null,
                PawnGenerationContext.NonPlayer,
                map.Tile,
                forceGenerateNewPawn: true,
                allowDead: false,
                allowDowned: false,
                canGeneratePawnRelations: false,
                mustBeCapableOfViolence: false,
                colonistRelationChanceFactor: 0f,
                forceAddFreeWarmLayerIfNeeded: false,
                allowGay: true,
                allowPregnant: false,
                allowFood: false,
                allowAddictions: false));

            IntVec3 loc = CellFinder.RandomClosewalkCellNear(entry, map, 6);
            GenSpawn.Spawn(droid, loc, map, Rot4.FromAngleFlat((map.Center - entry).AngleFlat));
            QuestUtility.AddQuestTag(droid, parms.questTag);

            // forced + forceWake so a droid that generated asleep or with no
            // mood need (format tiers gate Mood off below PROGRAMMABLE, packet
            // B1) still enters the state; transitionSilently so the inherited
            // "has become a manhunter!" letter does not double up with ours.
            droid.mindState.mentalStateHandler.TryStartMentalState(
                MentalStateDefOf.ManhunterPermanent,
                "left in the desert too long after a crash",
                forced: true, forceWake: true, transitionSilently: true);

            SendStandardLetter(
                "Wild droid",
                "A " + droid.KindLabel + " has come out of the desert.\n\n" +
                "Its casing is scoured to bare metal and whatever it was told to do, it stopped " +
                "understanding a long time ago. It is not owned by anyone and it will attack anything it sees.\n\n" +
                "Bring it down without wrecking it, take it prisoner, and a wild-keyed data spike will "
                + "eventually overwrite what is left of its core - though a crashed droid's core does not "
                + "give in on the first try.",
                def.letterDef ?? LetterDefOf.ThreatSmall,
                parms,
                droid);

            Find.TickManager.slower.SignalForceNormalSpeedShort();
            return true;
        }
    }
}
