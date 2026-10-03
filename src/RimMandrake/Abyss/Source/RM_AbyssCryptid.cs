using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Grammar;

namespace RimMandrake.Abyss
{
    // ════════════════════════════════════════════════════════════════════
    // ABYSS_FREE_CRYPTID_1 -- the Abyss's cryptid: signs, never sightings.
    // Spec: design/Jawa/worldbuilding/biomes/abyss_free_cryptid_2026-10-01.md (sections 3-5, 7).
    //
    // Ban 7: no pawn, faction or certain structure of theirs exists, and nothing is ever seen. Every sign can
    // be explained away, most of them by the durrgak. The NAME lives in one place, RulePackDef RM_AbyssCryptid
    // (cryptid_name, cryptid_whisper): letters resolve it here, the whisper interaction and the tale include
    // it (RulePack.include, RimSage-read 2026-10-03). defNames stay neutral. The campaign layer only ADDS a
    // whisper line to that pack (UtinniPatches Abyss_CryptidSithWhisper.xml).
    //
    // Signs built here (all off with cryptidSignsEnabled):
    //   - rumor-sites: RM_GenStep_AbyssRumorSites, 0-2 more runs of the durrgak's own placement, so neither
    //     can be told from the other;
    //   - the exchange: an unforbidden item lying inside a ring of shards (a cell with 3+ durrgak cairns within
    //     2.9) while the Dark lies and no colonist has it in sight is, now and then, gone, with goods of about
    //     its value left on the same spot and a letter. Never while watched;
    //   - a clear pocket around nothing: very rarely, while the Dark lies, a pocket opens over empty ground far
    //     from anyone and any building, holds a few hours, closes (hook in RM_MapComponent_Dark.DarknessAt);
    //   - the whisper (RM_AbyssWhisper interaction, Abyss maps only) and the tale it leaves for art;
    //   - after a long stay, a sleeping colonist may wake with RM_DreamtNoLight.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_AbyssCryptid
    {
        private static RulePackDef pack;
        public static RulePackDef Pack => pack ?? (pack = DefDatabase<RulePackDef>.GetNamedSilentFail("RM_AbyssCryptid"));

        public static string Name => Resolve("cryptid_name", "them");
        public static string Whisper => Resolve("cryptid_whisper", "");

        private static string Resolve(string key, string fallback)
        {
            if (Pack == null)
            {
                return fallback;
            }
            GrammarRequest req = default(GrammarRequest);
            req.Includes.Add(Pack);
            return GrammarResolver.Resolve(key, req, "RM_AbyssCryptid", false, null, null, null, false);
        }

        public static bool On(Map map)
        {
            return RM_AbyssSettings.cryptidSignsEnabled && map?.Biome != null && map.Biome.defName == "RM_Abyss";
        }
    }

    /// <summary>Rumor-sites: more runs of the durrgak's own placement (den, ring row, sometimes a cache in a ring).</summary>
    public class RM_GenStep_AbyssRumorSites : RM_GenStep_DurrgakSigns
    {
        public IntRange sites = new IntRange(0, 2);

        public override int SeedPart => 418230977;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_AbyssSettings.cryptidSignsEnabled) return;
            int n = sites.RandomInRange;
            for (int i = 0; i < n; i++)
            {
                Place(map);
            }
        }
    }

    public class RM_InteractionWorker_AbyssWhisper : InteractionWorker
    {
        public const float Weight = 0.02f;

        public override float RandomSelectionWeight(Pawn initiator, Pawn recipient)
        {
            return RM_AbyssCryptid.On(initiator?.Map) && initiator.RaceProps.Humanlike && recipient.RaceProps.Humanlike
                ? Weight : 0f;
        }

        public override void Interacted(Pawn initiator, Pawn recipient, List<RulePackDef> extraSentencePacks,
            out string letterText, out string letterLabel, out LetterDef letterDef, out LookTargets lookTargets)
        {
            base.Interacted(initiator, recipient, extraSentencePacks, out letterText, out letterLabel, out letterDef, out lookTargets);
            TaleDef tale = DefDatabase<TaleDef>.GetNamedSilentFail("RM_WhisperedInTheDark");
            if (tale != null)
            {
                TaleRecorder.RecordTale(tale, initiator);
            }
        }
    }

    public class RM_MapComponent_AbyssCryptid : MapComponent
    {
        public const float ExchangeChancePerHour = 0.12f;
        public const float WatchRange = 40f;
        public const float PhantomChancePerHour = 1f / (24f * 10f);
        public const float DreamAfterDays = 30f;
        public const float DreamChancePerSleepingHour = 0.01f;

        private struct Phantom
        {
            public IntVec3 cell;
            public float radius;
            public int until;
        }

        private readonly List<Phantom> phantoms = new List<Phantom>();
        public int exchanges;
        public int phantomsOpened;

        public RM_MapComponent_AbyssCryptid(Map map) : base(map) { }

        public static RM_MapComponent_AbyssCryptid For(Map map) => map?.GetComponent<RM_MapComponent_AbyssCryptid>();

        /// <summary>0..1: how much a no-source clear pocket clears this cell (the Dark multiplies by 1 - this).</summary>
        public static float PhantomClearanceAt(Map map, IntVec3 c)
        {
            RM_MapComponent_AbyssCryptid comp = For(map);
            if (comp == null || comp.phantoms.Count == 0 || !RM_AbyssSettings.cryptidSignsEnabled) return 0f;
            float best = 0f;
            for (int i = 0; i < comp.phantoms.Count; i++)
            {
                Phantom p = comp.phantoms[i];
                float d = (p.cell - c).LengthHorizontal;
                if (d < p.radius)
                {
                    best = Mathf.Max(best, 1f - Mathf.SmoothStep(0f, 1f, d / p.radius));
                }
            }
            return best;
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % GenDate.TicksPerHour != 113) return;
            int now = Find.TickManager.TicksGame;
            phantoms.RemoveAll(p => now >= p.until);
            if (!RM_AbyssCryptid.On(map)) return;
            if (RM_MapComponent_Dark.DarkPresent(map))
            {
                ExchangePass(false);
                if (Rand.Chance(PhantomChancePerHour)) OpenPhantom();
            }
            DreamPass();
        }

        // ── the exchange ───────────────────────────────────────────────

        /// <summary>Cells inside a ring: 3+ durrgak cairns within 2.9.</summary>
        public HashSet<IntVec3> CircleCells()
        {
            var counts = new Dictionary<IntVec3, int>();
            var result = new HashSet<IntVec3>();
            ThingDef cairn = DefDatabase<ThingDef>.GetNamedSilentFail("RM_DurrgakCairn");
            if (cairn == null) return result;
            foreach (Thing t in map.listerThings.ThingsOfDef(cairn))
            {
                foreach (IntVec3 c in GenRadial.RadialCellsAround(t.Position, 2.9f, true))
                {
                    if (!c.InBounds(map)) continue;
                    counts.TryGetValue(c, out int n);
                    counts[c] = n + 1;
                    if (n + 1 >= 3) result.Add(c);
                }
            }
            return result;
        }

        public bool Watched(IntVec3 c)
        {
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
            {
                if (p.Downed || !p.Awake()) continue;
                if (p.Position.InHorDistOf(c, WatchRange) && GenSight.LineOfSight(p.Position, c, map, true)) return true;
            }
            return false;
        }

        /// <summary>One pass. force = the proof (every eligible item swaps). Returns how many swapped.</summary>
        public int ExchangePass(bool force)
        {
            int swapped = 0;
            foreach (IntVec3 c in CircleCells())
            {
                foreach (Thing t in new List<Thing>(c.GetThingList(map)))
                {
                    if (t.def.category != ThingCategory.Item || t is Corpse || t.IsForbidden(Faction.OfPlayer)) continue;
                    if (Watched(c)) break;
                    if (!force && !Rand.Chance(ExchangeChancePerHour)) continue;
                    Exchange(t, c);
                    swapped++;
                }
            }
            return swapped;
        }

        private void Exchange(Thing taken, IntVec3 c)
        {
            float value = Mathf.Max(5f, taken.MarketValue * taken.stackCount) * Rand.Range(0.8f, 1.3f);
            string takenLabel = taken.LabelCap;
            taken.Destroy(DestroyMode.Vanish);
            var left = new List<string>();
            ThingDef tholin = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Tholin");
            foreach (ThingDef def in new[] { ThingDefOf.ComponentIndustrial, tholin, ThingDefOf.Steel })
            {
                if (def == null || value < def.BaseMarketValue) continue;
                int n = Mathf.Min(def.stackLimit, Mathf.FloorToInt(value * (def == ThingDefOf.Steel ? 1f : 0.4f) / def.BaseMarketValue));
                if (n <= 0) continue;
                Thing g = ThingMaker.MakeThing(def);
                g.stackCount = n;
                value -= n * def.BaseMarketValue;
                if (GenPlace.TryPlaceThing(g, c, map, ThingPlaceMode.Near)) left.Add(g.LabelCap);
            }
            exchanges++;
            string name = RM_AbyssCryptid.Name;
            Find.LetterStack.ReceiveLetter("Something was taken",
                takenLabel + " was left on a ring of shards in the Dark, and nobody was watching it. It is gone. In its place, "
                + "set down neatly: " + (left.Count == 0 ? "nothing at all" : string.Join(", ", left)) + ".\n\n"
                + "A durrgak, perhaps; they tidy. The colonists say " + name + ", and not loudly.",
                LetterDefOf.NeutralEvent, new LookTargets(new TargetInfo(c, map)));
        }

        // ── a clear pocket around nothing ─────────────────────────────

        public bool OpenPhantom()
        {
            for (int i = 0; i < 40; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (c.Roofed(map) || c.CloseToEdge(map, 10) || c.Fogged(map)) continue;
                if (GenRadial.RadialDistinctThingsAround(c, map, 8f, true).Any(t => t is Building)) continue;
                bool near = false;
                foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
                {
                    if (p.Position.InHorDistOf(c, 15f)) { near = true; break; }
                }
                if (near) continue;
                phantoms.Add(new Phantom
                {
                    cell = c,
                    radius = Rand.Range(2.5f, 4f),
                    until = Find.TickManager.TicksGame + Rand.RangeInclusive(2, 5) * GenDate.TicksPerHour
                });
                phantomsOpened++;
                return true;
            }
            return false;
        }

        // ── the dream ─────────────────────────────────────────────────

        private void DreamPass()
        {
            if (map.AgeInDays < DreamAfterDays) return;
            ThoughtDef dream = DefDatabase<ThoughtDef>.GetNamedSilentFail("RM_DreamtNoLight");
            if (dream == null) return;
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
            {
                if (p.Awake() || p.needs?.mood?.thoughts?.memories == null) continue;
                if (p.needs.mood.thoughts.memories.GetFirstMemoryOfDef(dream) != null) continue;
                if (Rand.Chance(DreamChancePerSleepingHour)) p.needs.mood.thoughts.memories.TryGainMemory(dream);
            }
        }

        // ── bridge proofs (jawa/static_call), chain cryptid in validation.py ──

        /// <summary>"NAME the Nhaleth WHISPER ... " -- the name and a whisper resolved from the one pack.</summary>
        public static string ProofName(Map map)
        {
            return "NAME " + RM_AbyssCryptid.Name + " | WHISPER " + RM_AbyssCryptid.Whisper;
        }

        /// <summary>Lays a ring of four cairns near the map centre, drops 10 silver inside it and runs one forced
        /// exchange pass. Never swaps while a colonist sees the ring: "watched=False swapped=1 circle=(x,z)";
        /// with a colonist in sight it must read "watched=True swapped=0".</summary>
        public static string ProofExchange(Map map)
        {
            RM_MapComponent_AbyssCryptid comp = For(map);
            ThingDef cairn = DefDatabase<ThingDef>.GetNamedSilentFail("RM_DurrgakCairn");
            if (comp == null || cairn == null) return "REFUSED: no cryptid component or no RM_DurrgakCairn";
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 20, c =>
                    GenRadial.RadialCellsAround(c, 2.9f, true).All(n => n.InBounds(map) && n.Standable(map) && n.GetEdifice(map) == null), out IntVec3 center))
            {
                return "REFUSED: no clear 5x5 near the centre";
            }
            foreach (IntVec3 off in GenAdj.DiagonalDirections)
            {
                GenSpawn.Spawn(ThingMaker.MakeThing(cairn), center + off * 2, map);
            }
            Thing silver = ThingMaker.MakeThing(ThingDefOf.Silver);
            silver.stackCount = 10;
            GenSpawn.Spawn(silver, center, map);
            bool watched = comp.Watched(center);
            int swapped = comp.ExchangePass(true);
            return "watched=" + watched + " swapped=" + swapped + " circle=" + center;
        }

        /// <summary>Opens one clear pocket around nothing and reads the Dark's clearance at its heart: "PHANTOM cell=(x,z) clearance=1.00".</summary>
        public static string ProofPhantom(Map map)
        {
            RM_MapComponent_AbyssCryptid comp = For(map);
            if (comp == null) return "REFUSED: no cryptid component";
            if (!comp.OpenPhantom()) return "REFUSED: no open ground far from buildings and colonists";
            Phantom p = comp.phantoms[comp.phantoms.Count - 1];
            return "PHANTOM cell=" + p.cell + " clearance=" + PhantomClearanceAt(map, p.cell).ToString("0.00");
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref exchanges, "rmCryptidExchanges", 0);
            Scribe_Values.Look(ref phantomsOpened, "rmCryptidPhantoms", 0);
        }
    }
}
