using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShipMemory
{
    // ANOMALY_EXCEPTION_ACCESS_1 -- the Memory-Core revelation. Reveals the
    // seven patched buildables (RUT_ShipMemory_ContainmentGate.xml) the
    // moment the clan ties down its first live beast, stockpiles 50+
    // Bioferrite, or the Assailant dungeon's core signals it. One
    // ChoiceLetter, no quest, no research row -- design/Jawa/
    // anomaly_exception_access_spec.md is the full spec this implements.
    //
    // One-shot by construction: Find.HiddenItemsManager's own saved
    // dictionary is the only state this needs -- SetDiscovered flips the
    // entry once and the entry survives save/load (Scribe'd on
    // HiddenItemsManager itself), so this component carries no ExposeData
    // of its own.
    public class GameComponent_ShipMemory : GameComponent, ISignalReceiver
    {
        private const int CheckIntervalTicks = 600; // 10s at 1x
        private const int BioferriteThreshold = 50;

        private static ThingDef Gate => DefDatabase<ThingDef>.GetNamed("RUT_ShipMemory_Containment");

        private static List<ThingDef> sixBuildings;
        private static List<ThingDef> SixBuildings => sixBuildings ?? (sixBuildings = new List<ThingDef>
        {
            DefDatabase<ThingDef>.GetNamed("HoldingPlatform"),
            DefDatabase<ThingDef>.GetNamed("ElectricInhibitor"),
            DefDatabase<ThingDef>.GetNamed("ShardInhibitor"),
            DefDatabase<ThingDef>.GetNamed("BioferriteHarvester"),
            DefDatabase<ThingDef>.GetNamed("Electroharvester"),
            DefDatabase<ThingDef>.GetNamed("BioferriteGenerator"),
        });

        public GameComponent_ShipMemory(Game game)
        {
        }

        // Signal receivers are not saved -- re-register every load, exactly
        // once (FinalizeInit runs once per load; registering in the
        // constructor too would double-register and log an error).
        public override void FinalizeInit()
        {
            Find.SignalManager.RegisterReceiver(this);
        }

        public override void GameComponentTick()
        {
            if (!ModsConfig.AnomalyActive) return;
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0) return;
            if (!Find.HiddenItemsManager.Hidden(Gate)) return;

            foreach (Map map in Find.Maps)
            {
                if (!map.IsPlayerHome) continue;

                Building_HoldingPlatform occupied = map.listerBuildings
                    .AllBuildingsColonistOfClass<Building_HoldingPlatform>()
                    .FirstOrDefault(p => p.HeldPawn != null);
                if (occupied != null)
                {
                    Reveal(occupied, assailant: false);
                    return;
                }

                if (map.resourceCounter.GetCount(ThingDefOf.Bioferrite) >= BioferriteThreshold)
                {
                    Thing stack = map.listerThings.ThingsOfDef(ThingDefOf.Bioferrite).FirstOrDefault();
                    Reveal(stack, assailant: false);
                    return;
                }
            }
        }

        // The Assailant dungeon's core band sends a signal ending in this
        // tag (prefixed with its own quest id -- match by EndsWith, never
        // equality, per spec §3).
        public void Notify_SignalReceived(Signal signal)
        {
            if (!ModsConfig.AnomalyActive) return;
            if (!Find.HiddenItemsManager.Hidden(Gate)) return;
            if (signal.tag != null && signal.tag.EndsWith("RUT_ShipMemory_Containment"))
                Reveal(null, assailant: true);
        }

        private void Reveal(Thing target, bool assailant)
        {
            Find.HiddenItemsManager.SetDiscovered(Gate);

            Letter letter = LetterMaker.MakeLetter(
                "RUT_ShipMemory_Containment_Label".Translate(),
                (assailant ? "RUT_ShipMemory_Containment_Text_Assailant" : "RUT_ShipMemory_Containment_Text").Translate(),
                LetterDefOf.PositiveEvent,
                target != null ? new LookTargets(target) : null,
                hyperlinkThingDefs: SixBuildings);
            Find.LetterStack.ReceiveLetter(letter);
        }
    }
}
