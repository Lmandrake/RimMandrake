using System.Collections.Generic;
using Verse;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// WATCHER_CREATURES_MOD_1, design §3. Put this on a race ThingDef to make it a watcher; the
    /// comp is injected by RM_WatcherStartup, so a member writes XML only. Every number here is a
    /// per-member value; the Mod Settings scale the radius and the delay for all members at once.
    /// </summary>
    public class RM_WatcherExtension : DefModExtension
    {
        /// <summary>The one medium it lives in (owner ruling, Q9). Empty = no medium lock (a cover
        /// watcher, hides anywhere). A member whose medium comes from another mod lists it with
        /// MayRequire; if that mod is absent the list is empty and the lock falls away.</summary>
        public List<TerrainDef> mediumTerrains = new List<TerrainDef>();

        /// <summary>A pawn that is not its own kind this close makes it hide (ruled flinch cue).</summary>
        public float flinchRadius = 6f;

        /// <summary>How far it looks for a pawn to turn and face, and the geophone's reach.</summary>
        public float watchRadius = 14f;

        /// <summary>How long it stays under once hidden, before it may peek out again.</summary>
        public IntRange hideTicks = new IntRange(2500, 7500);

        /// <summary>The hediff that hides it. Must carry HediffComp_Invisibility with
        /// visibleToPlayer false, or it is not hidden at all.</summary>
        public HediffDef hiddenHediff;

        /// <summary>The Thing left on its cell while hidden (an RM_WatcherSign).</summary>
        public ThingDef signDef;

        /// <summary>Above 0: a submerged sand swimmer of at least this body size within watchRadius
        /// sends it under (needs CreatureBehaviors' sand-swim kit loaded). 0 = no geophone.</summary>
        public float geophoneMinBodySize;

        /// <summary>A watch bout ends after this long so the think tree can re-decide (eat, sleep).</summary>
        public int maxWatchTicks = 2500;

        /// <summary>Chance a think-tree pass skips the watch and wanders on its medium instead.</summary>
        public float wanderChance = 0.15f;

        /// <summary>The fragility ceiling (owner ruling 2026-10-08: "Should take almost no damage to destroy them"). The startup audit
        /// logs an error when an adult of the race would survive more than this much damage (150 x race baseHealthScale).</summary>
        public float maxLethalDamage = 5f;

        /// <summary>What it leaves when it dies (owner ruling 2026-10-08: "Remains are of highly dubious value and kind of sad"). Set: the
        /// corpse is replaced by remainsCount of this item. Null: the ordinary corpse stays. Every member owes one (its death asset).</summary>
        public ThingDef remainsDef;

        public int remainsCount = 1;

        /// <summary>Hidden and this hungry: it comes up so it can feed.</summary>
        public float emergeWhenFoodBelow = 0.25f;

        public float puffScale = 0.6f;

        /// <summary>The optional non-body flinch cues (gas, heat, fire, steam, shade, buried, light), owner ruling 2026-10-08.
        /// Null or an absent node = the member flinches from bodies (and the geophone) only. See RM_WatcherCues.</summary>
        public RM_WatcherCues cues;

        public bool HasMedium => !mediumTerrains.NullOrEmpty();

        public bool IsMedium(TerrainDef t)
        {
            return !HasMedium || (t != null && mediumTerrains.Contains(t));
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            foreach (string err in RM_WatcherKernel.ConfigErrors(hiddenHediff != null, signDef != null,
                signDef != null && typeof(RM_WatcherSign).IsAssignableFrom(signDef.thingClass), flinchRadius, watchRadius,
                hideTicks.min, hideTicks.max, maxWatchTicks, wanderChance, emergeWhenFoodBelow, geophoneMinBodySize, maxLethalDamage))
            {
                yield return "RM_WatcherExtension: " + err;
            }
            if (remainsDef != null && remainsCount <= 0)
            {
                yield return "RM_WatcherExtension: remainsCount must be positive when remainsDef is set";
            }
            if (cues != null)
            {
                foreach (string err in cues.ConfigErrors())
                {
                    yield return "RM_WatcherExtension: " + err;
                }
            }
        }
    }
}
