using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER (2026-10-17) — the Mod Settings switch for the albino dragonsnake
    // (RSW_DragonsnakeAlbino, Defs/ThingDefs_Races/RSW_DragonsnakeAlbino.xml), a rare pale variant of RSW_Dragonsnake.
    //
    // Off (RSW_BeastMechanicsSettings.albinoDragonsnakeEnabled == false): once at startup, before any map asks a biome
    // for a commonality, the albino is taken out of every BiomeDef's wildAnimals / pollutionWildAnimals /
    // coastalWildAnimals list and its own race.wildBiomes rows are cleared, and the three lazy commonality caches are
    // reset. It then never spawns wild; one already on a map, in a save or in a trader's stock is left alone, and the
    // canon RSW_Dragonsnake is untouched. Precedent: Scarlands' RM_WarscarStartup (same private fields, same timing).
    // The def may be absent (its file is held from deploy until its art is installed): then this does nothing.
    [StaticConstructorOnStartup]
    public static class RSW_DragonsnakeAlbinoToggle
    {
        public const string AlbinoDefName = "RSW_DragonsnakeAlbino";

        private static readonly string[] RosterFields = { "wildAnimals", "pollutionWildAnimals", "coastalWildAnimals" };
        private static readonly string[] CacheFields = { "cachedAnimalCommonalities", "cachedPollutionAnimalCommonalities", "cachedCoastalAnimalCommonalities" };

        static RSW_DragonsnakeAlbinoToggle()
        {
            if (RSW_BeastMechanicsSettings.albinoDragonsnakeEnabled) return;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(AlbinoDefName);
            if (kind == null) return;
            int removed = RemoveFromRosters(kind);
            Log.Message("[RSW_DragonsnakeAlbino] Mod Settings: albino dragonsnake switched off; removed " + removed + " biome roster row(s).");
        }

        /// <summary>Remove every roster row naming <paramref name="kind"/> and its own wildBiomes rows; returns how many rows went.</summary>
        public static int RemoveFromRosters(PawnKindDef kind)
        {
            int removed = 0;
            var rosters = new List<FieldInfo>();
            foreach (string name in RosterFields)
            {
                FieldInfo f = AccessTools.Field(typeof(BiomeDef), name);
                if (f == null) Log.Warning("[RSW_DragonsnakeAlbino] BiomeDef." + name + " not found; that roster is not filtered.");
                else rosters.Add(f);
            }
            var caches = new List<FieldInfo>();
            foreach (string name in CacheFields)
            {
                FieldInfo f = AccessTools.Field(typeof(BiomeDef), name);
                if (f == null) Log.Warning("[RSW_DragonsnakeAlbino] BiomeDef." + name + " not found; that cache is not reset.");
                else caches.Add(f);
            }

            foreach (BiomeDef biome in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                foreach (FieldInfo f in rosters)
                {
                    if (f.GetValue(biome) is List<BiomeAnimalRecord> rows)
                        removed += rows.RemoveAll(r => r != null && r.animal == kind);
                }
                foreach (FieldInfo f in caches) f.SetValue(biome, null);
            }

            List<AnimalBiomeRecord> own = kind.race?.race?.wildBiomes;
            if (own != null)
            {
                removed += own.Count;
                own.Clear();
            }
            return removed;
        }
    }
}
