using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // shd:loadout-tradeoff: "the same shields, you're just installing
    // modules to increase their switching capacity/configuration." One
    // building, one mode active at a time; a module item is consumed once
    // to permanently unlock an additional mode on THIS building.
    public class CompShieldModuleSwitch : ThingComp
    {
        private HashSet<ShieldFieldMode> unlockedModes;
        private ShieldFieldMode currentMode;

        public CompProperties_ShieldModuleSwitch Props => (CompProperties_ShieldModuleSwitch)props;

        public ShieldFieldMode CurrentMode => currentMode;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (unlockedModes == null)
            {
                unlockedModes = new HashSet<ShieldFieldMode> { Props.defaultMode };
                currentMode = Props.defaultMode;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref currentMode, "currentMode", Props.defaultMode);
            Scribe_Collections.Look(ref unlockedModes, "unlockedModes", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && unlockedModes == null)
            {
                unlockedModes = new HashSet<ShieldFieldMode> { Props.defaultMode };
            }
        }

        public bool IsUnlocked(ShieldFieldMode mode)
        {
            return unlockedModes != null && unlockedModes.Contains(mode);
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo gizmo in base.CompGetGizmosExtra())
            {
                yield return gizmo;
            }

            if (unlockedModes != null && unlockedModes.Count > 1)
            {
                yield return new Command_Action
                {
                    defaultLabel = "Cycle shield field",
                    defaultDesc = "Switch which field this generator is currently configured for. Only one field is active at a time. Current: " + currentMode + ".",
                    action = CycleMode,
                };
            }

            yield return new Command_Action
            {
                defaultLabel = "Install shield module",
                defaultDesc = "Consume a compatible shield module to permanently unlock a new field configuration for this generator.",
                action = OpenInstallMenu,
            };
        }

        private void CycleMode()
        {
            if (unlockedModes == null || unlockedModes.Count <= 1)
            {
                return;
            }

            List<ShieldFieldMode> modes = unlockedModes.OrderBy(m => (byte)m).ToList();
            int index = modes.IndexOf(currentMode);
            currentMode = modes[(index + 1) % modes.Count];
            Messages.Message("Shield reconfigured to " + currentMode + " field.", parent, MessageTypeDefOf.NeutralEvent, historical: false);
        }

        private void OpenInstallMenu()
        {
            Map map = parent.Map;
            if (map == null || Props.moduleMappings == null)
            {
                return;
            }

            List<FloatMenuOption> options = new List<FloatMenuOption>();
            foreach (ShieldModuleMapping mapping in Props.moduleMappings)
            {
                if (mapping?.moduleDef == null || IsUnlocked(mapping.mode))
                {
                    continue;
                }

                Thing item = map.listerThings.ThingsOfDef(mapping.moduleDef).FirstOrDefault(t => !t.Destroyed);
                if (item == null)
                {
                    continue;
                }

                ShieldFieldMode capturedMode = mapping.mode;
                Thing capturedItem = item;
                options.Add(new FloatMenuOption("Install " + mapping.moduleDef.label, () =>
                {
                    capturedItem.Destroy();
                    unlockedModes.Add(capturedMode);
                    currentMode = capturedMode;
                    Messages.Message("Installed " + capturedMode + " shield module.", parent, MessageTypeDefOf.PositiveEvent, historical: false);
                }));
            }

            if (options.Count == 0)
            {
                Messages.Message("No compatible shield modules available.", MessageTypeDefOf.RejectInput, historical: false);
                return;
            }

            Find.WindowStack.Add(new FloatMenu(options));
        }
    }
}
