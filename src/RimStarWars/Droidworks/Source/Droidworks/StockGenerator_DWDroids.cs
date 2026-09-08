using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// Sells droids. A trader carrying this generator stocks live pawns of the
    /// listed Droidworks kinds, and buys any droid the player brings.
    ///
    /// WHY THIS EXISTS AT ALL, given two shipping classes already do something
    /// like it (DROID_FACTION_LOADOUTS_1, packet C1, 2026-09-08):
    ///
    ///   Asimov.StockGenerator_Automatons   works today, dies at retirement R3
    ///                                      (design/Jawa/droids/
    ///                                      DROID_UNIFIED_FRAMEWORK_DESIGN.md §2
    ///                                      retires Droid Depot + Asimov). Its
    ///                                      MayRequire is
    ///                                      Neronix17.OuterRim.DroidDepot, not
    ///                                      OuterRim Core - measured in the
    ///                                      donor's own TraderKinds_Base.xml:83.
    ///   StockGenerator_Colonists           guy762.mm.kotorcore only; dies at R4.
    ///   StockGenerator_Colonists (vanilla) does not exist. The name in §3.2 is
    ///                                      that KotOR class, not a vanilla one.
    ///   StockGenerator_Slaves (vanilla)    yields NOTHING unless every ideo of
    ///                                      the trading faction returns
    ///                                      IdeoApprovesOfSlavery()
    ///                                      (StockGenerator_Slaves.cs:20-35), and
    ///                                      the Trade Moot's fixed ideo is The
    ///                                      Salvation. Silently empty, which is
    ///                                      the worst of the four.
    ///
    /// So every off-the-shelf route either dies in this program's own retirement
    /// waves or is silently inert. Forty lines here outlive all of them.
    ///
    /// ⛔ NO SLAVERY GATE, deliberately. A droid is property in this setting;
    /// selling one is not selling a person, and the vanilla ideo check exists to
    /// model the latter. This is the one behavioural difference from
    /// StockGenerator_Slaves and it is the reason that class could not be reused.
    ///
    /// ⚠️ NO RESTRAINING BOLT is applied on generation, and that is not an
    /// oversight. RSW_DW_BoltResentment is seeded by the two APPLICATION routes
    /// (Recipe_InstallRestrainingBolt.ApplyOnPawn and JobDriver_DWClampBolt's
    /// AddFinishAction), never by a hediff merely appearing on a pawn - so a
    /// droid bolted here would carry a bolt that never earns resentment and never
    /// rebels when freed, which is half a mechanism wearing the whole one's face.
    /// Selling bolted droids belongs with DROIDWORKS_BOLT_PAYOFF_1 (B5), seeded
    /// properly.
    /// </summary>
    public class StockGenerator_DWDroids : StockGenerator
    {
        /// <summary>The kinds this trader stocks. Required; an empty list is a config error.</summary>
        public List<PawnKindDef> pawnKinds = new List<PawnKindDef>();

        public override IEnumerable<string> ConfigErrors(TraderKindDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }
            if (pawnKinds.NullOrEmpty())
            {
                yield return "StockGenerator_DWDroids has no pawnKinds - it would stock nothing, silently.";
            }
        }

        public override IEnumerable<Thing> GenerateThings(PlanetTile forTile, Faction faction = null)
        {
            if (pawnKinds.NullOrEmpty())
            {
                yield break;
            }
            int count = countRange.RandomInRange;
            for (int i = 0; i < count; i++)
            {
                PawnKindDef kind = pawnKinds.RandomElement();
                if (kind == null)
                {
                    continue;
                }
                // faction null: stock is nobody's until it is bought. Matching the
                // trader's own faction would make every unsold droid a member of a
                // faction the player may be at war with, and TradeUtility hands the
                // bought pawn to the player either way.
                PawnGenerationRequest request = new PawnGenerationRequest(
                    kind,
                    null,
                    PawnGenerationContext.NonPlayer,
                    forTile,
                    forceGenerateNewPawn: false,
                    allowDead: false,
                    allowDowned: false,
                    canGeneratePawnRelations: false,
                    mustBeCapableOfViolence: false,
                    colonistRelationChanceFactor: 1f,
                    forceAddFreeWarmLayerIfNeeded: false,
                    allowGay: true,
                    allowPregnant: false,
                    allowFood: false,
                    allowAddictions: false);
                yield return PawnGenerator.GeneratePawn(request);
            }
        }

        /// <summary>
        /// What this trader will BUY. Any Droidworks droid: humanlike, tradeable,
        /// and carrying our own flesh type. Keying on the flesh type rather than on
        /// `pawnKinds` is deliberate - the Moot "buys/sells droids of all kinds"
        /// (owner ruling 2), not only the models it happens to be selling today -
        /// and keying on the flesh type rather than on Humanlike alone is what keeps
        /// this from turning the Trade Moot into a slave market.
        /// </summary>
        public override bool HandlesThingDef(ThingDef thingDef)
        {
            if (thingDef == null || thingDef.category != ThingCategory.Pawn)
            {
                return false;
            }
            if (thingDef.race == null || !thingDef.race.Humanlike)
            {
                return false;
            }
            if (thingDef.tradeability == Tradeability.None)
            {
                return false;
            }
            return thingDef.race.FleshType == DroidworksDefOf.RSW_DW_FleshType_Droid;
        }
    }
}
