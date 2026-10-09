using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // GELATINOUSSLIME_VAULT_SEAL_PLUG_1 (owner ruling by question card 2026-10-09): a flesh plug across the Slough vault's
    // inner door. Ordinary damage (explosives, tools, fire) is absorbed and does nothing; only a slime chunk dissolves it.
    //
    // The dissolve hook (PROVISIONAL until GELATINOUSSLIME_TITAN_CHUNK_BOMB_1 names its real defs): the plug watches, every
    // 60 ticks, for a Thing whose defName is in dissolverDefNames within dissolveRadius cells (a planted or landed chunk), and
    // dissolves. Names are strings so an unbuilt def is not a load error. The chunk bomb may instead call
    // CompFleshSeal.DissolveAround(map, cell, radius) from its burst. A Mod Setting turns the seal off (the plug then dissolves
    // when it spawns, so the vault is simply open).
    public class CompProperties_FleshSeal : CompProperties
    {
        public List<string> dissolverDefNames = new List<string> { "RM_TitanoslimeChunk" };
        public float dissolveRadius = 3.9f;   // PROVISIONAL
        public CompProperties_FleshSeal() { compClass = typeof(CompFleshSeal); }
    }

    public class CompFleshSeal : ThingComp
    {
        private CompProperties_FleshSeal P => (CompProperties_FleshSeal)props;

        public override void PostPreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            // everything is absorbed: the plug can only be dissolved (see Dissolve), never damaged to death
            absorbed = StructureInjectionsRUTSettings.fleshSealEnabled;
        }

        public override void CompTick()
        {
            if (!parent.Spawned) return;
            if (!StructureInjectionsRUTSettings.fleshSealEnabled) { Dissolve(); return; }
            if (!parent.IsHashIntervalTick(60)) return;
            Map map = parent.Map;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, P.dissolveRadius, true))
            {
                if (!c.InBounds(map)) continue;
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                    if (things[i] != parent && P.dissolverDefNames.Contains(things[i].def.defName)) { Dissolve(); return; }
            }
        }

        public void Dissolve()
        {
            if (parent.Destroyed) return;
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            parent.Destroy(DestroyMode.Vanish);
            if (map != null) FilthMaker.TryMakeFilth(pos, map, ThingDefOf.Filth_Slime, 3);
            Messages.Message("The flesh plug across the door sloughs away.", new TargetInfo(pos, map), MessageTypeDefOf.PositiveEvent, false);
        }

        /// <summary>The chunk bomb's hook: dissolve every flesh seal within radius of a burst.</summary>
        public static int DissolveAround(Map map, IntVec3 center, float radius)
        {
            int n = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, radius, true))
            {
                if (!c.InBounds(map)) continue;
                List<Thing> things = c.GetThingList(map);
                for (int i = things.Count - 1; i >= 0; i--)
                {
                    CompFleshSeal s = things[i].TryGetComp<CompFleshSeal>();
                    if (s != null) { s.Dissolve(); n++; }
                }
            }
            return n;
        }
    }
}
