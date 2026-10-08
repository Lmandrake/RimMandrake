using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.Webwork
{
    // ════════════════════════════════════════════════════════════════════════════════════════════════
    // WEBWORK_DEAD_GIANT_BUILD_1 — the wrapped urraveth skeleton (a map site, never a worldgen feature).
    //
    //  RM_GenStep_UrravethRemains   places the seven-piece body on a Webwork map with a Mod Settings chance.
    //  RM_Building_UrravethPiece    one bone piece: wrapped/bare graphic, examine float menu, load -> creak ->
    //                               collapse with warning.
    //  RM_JobDriver_ExamineUrraveth the examine job (custom, NOT vanilla CompStudiable: CompProperties_Studiable is
    //                               Anomaly knowledge plumbing — anomalyKnowledge/knowledgeCategory/monolith level —
    //                               with no per-piece completion hook; read in RimSage 2026-10-06).
    //  RM_MapComponent_UrravethReading  the saved reading: chapters read, complete, outline drawn.
    //
    // Collapse damage is vanilla roof-collapse maths for a THIN roof (RoofCollapserImmediate.ThinRoofCrushDamageRange
    // 15~30 Crush, SourceCategory.Collapse), times the Mod Settings multiplier.
    // Every number marked PROVISIONAL is invented and owes a live pass.
    // ════════════════════════════════════════════════════════════════════════════════════════════════

    public class RM_UrravethPieceExtension : DefModExtension
    {
        public string bareTexPath;
        public string bareLabel;
        /// <summary>pinned | bound | cut | eaten</summary>
        public string chapter;
        public bool isSkull;
        /// <summary>Lower ranks hold up higher ones: limbs 0, pelvis 1, ribs 2, neck 3, skull 4. A piece is loaded by
        /// the loss (or heavy damage) of an ADJACENT piece of strictly lower rank.</summary>
        public int supportRank;
        /// <summary>Load at which the piece starts creaking (pawn body size; items count mass / itemMassPerLoad).</summary>
        public float loadCapacity = 2f;
        public float itemMassPerLoad = 50f;     // PROVISIONAL
        public int examineTicks = 3000;         // PROVISIONAL
        public float nearRadius = 10f;          // PROVISIONAL: the countdown only runs while a pawn is this close
        public string chapterLetterLabel;
        public string chapterLetterText;
        public string finalLetterLabel;
        public string finalLetterText;
        public string creakSound = "Building_Deconstructed";  // PROVISIONAL stand-in: no vanilla creak SoundDef exists
        public string collapseSound = "Roof_Collapse";
        public string rubbleFilth = "Filth_RubbleRock";
        public string rubbleChunk;               // owed: no bone chunk def exists yet; null spawns filth only
        public string outlineFilth = "Filth_LooseGround"; // PROVISIONAL stand-in for a bespoke silk/outline filth
    }

    public static class RM_Urraveth
    {
        public static readonly string[] ChapterOrder = RM_UrravethKernel.ChapterOrder;
        public const float HeavyDamageFraction = RM_UrravethKernel.HeavyDamageFraction;   // PROVISIONAL: "heavily damaged"
        public static readonly IntRange CrushDamage = new IntRange(15, 30); // vanilla thin-roof collapse

        private static List<ThingDef> pieceDefs;

        public static List<ThingDef> PieceDefs
        {
            get
            {
                if (pieceDefs == null)
                {
                    pieceDefs = DefDatabase<ThingDef>.AllDefsListForReading
                        .Where(d => d.thingClass != null && typeof(RM_Building_UrravethPiece).IsAssignableFrom(d.thingClass)
                                    && d.HasModExtension<RM_UrravethPieceExtension>())
                        .ToList();
                }
                return pieceDefs;
            }
        }

        public static IEnumerable<RM_Building_UrravethPiece> PiecesOn(Map map)
        {
            foreach (ThingDef d in PieceDefs)
            {
                foreach (Thing t in map.listerThings.ThingsOfDef(d))
                {
                    if (t is RM_Building_UrravethPiece p && p.Spawned)
                    {
                        yield return p;
                    }
                }
            }
        }

        public static bool Adjacent(CellRect a, CellRect b)
        {
            return RM_UrravethKernel.Adjacent(a.minX, a.minZ, a.maxX, a.maxZ, b.minX, b.minZ, b.maxX, b.maxZ);
        }

        public static SoundDef Sound(string name) => name.NullOrEmpty() ? null : DefDatabase<SoundDef>.GetNamedSilentFail(name);
        public static ThingDef Def(string name) => name.NullOrEmpty() ? null : DefDatabase<ThingDef>.GetNamedSilentFail(name);
    }

    public class RM_Building_UrravethPiece : Building
    {
        public bool wrapped = true;
        public int creakTicksLeft = -1;
        public int lostSupports;

        private Graphic bareGraphic;

        public RM_UrravethPieceExtension Ext => def.GetModExtension<RM_UrravethPieceExtension>();
        public bool Creaking => creakTicksLeft >= 0;

        public override Graphic Graphic
        {
            get
            {
                RM_UrravethPieceExtension ext = Ext;
                if (wrapped || ext == null || ext.bareTexPath.NullOrEmpty())
                {
                    return base.Graphic;
                }
                if (bareGraphic == null)
                {
                    GraphicData gd = new GraphicData();
                    gd.CopyFrom(def.graphicData);
                    gd.texPath = ext.bareTexPath;
                    bareGraphic = gd.Graphic;
                }
                return bareGraphic;
            }
        }

        public override string LabelNoCount
        {
            get
            {
                RM_UrravethPieceExtension ext = Ext;
                return (!wrapped && ext != null && !ext.bareLabel.NullOrEmpty()) ? ext.bareLabel : base.LabelNoCount;
            }
        }

        public RM_MapComponent_UrravethReading Reading => Map?.GetComponent<RM_MapComponent_UrravethReading>();

        public bool CanOpenLastWrapping
        {
            get
            {
                RM_MapComponent_UrravethReading r = Reading;
                return RM_UrravethKernel.CanOpenLastWrapping(Ext != null && Ext.isSkull, wrapped, r != null, r != null && r.complete,
                       Spawned, Spawned && RM_Urraveth.PiecesOn(Map).All(p => !p.wrapped));
            }
        }

        // ── examine ──────────────────────────────────────────────────────────────────────────────
        public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption o in base.GetFloatMenuOptions(selPawn))
            {
                yield return o;
            }
            if (!RM_WebworkSettings.urravethEnabled)
            {
                yield break;
            }
            string what = wrapped ? "Examine the " + LabelNoCount : (CanOpenLastWrapping ? "Open the last wrapping" : null);
            if (what == null)
            {
                yield break;
            }
            if (!selPawn.CanReach(this, PathEndMode.Touch, Danger.Deadly))
            {
                yield return new FloatMenuOption(what + " (cannot reach)", null);
                yield break;
            }
            yield return new FloatMenuOption(what, delegate
            {
                Job job = JobMaker.MakeJob(RM_UrravethDefOf.RM_ExamineUrravethRemains, this);
                selPawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            });
        }

        public int ExamineTicks => RM_UrravethKernel.ExamineTicks(Ext?.examineTicks ?? 3000, wrapped);

        /// <summary>One completed examine. Wrapped: cut the wrapping, drop thrixweave, record the chapter, send its
        /// letter. Bare skull with every piece read: open the last wrapping (complete + outline). Returns what happened.</summary>
        public string FinishExamine(Pawn by)
        {
            RM_UrravethPieceExtension ext = Ext;
            RM_MapComponent_UrravethReading r = Reading;
            ExamineOutcome outcome = RM_UrravethKernel.Examine(ext != null, r != null, Spawned, wrapped, CanOpenLastWrapping);
            if (outcome == ExamineOutcome.Nothing)
            {
                return "nothing";
            }
            if (outcome == ExamineOutcome.ReadChapter)
            {
                wrapped = false;
                DirtyMapMesh(Map);
                ThingDef weave = RM_Urraveth.Def("Hyperweave"); // renamed thrixweave by RM_Thrixweave_Rename.xml
                int n = RM_UrravethKernel.WeaveDropped(RM_WebworkSettings.urravethThrixweavePerPiece, weave != null);
                if (weave != null && n > 0)
                {
                    Thing stack = ThingMaker.MakeThing(weave);
                    stack.stackCount = n;
                    GenPlace.TryPlaceThing(stack, InteractionOrAdjacent(), Map, ThingPlaceMode.Near);
                }
                r.RecordChapter(ext.chapter, this);
                if (!ext.chapterLetterText.NullOrEmpty())
                {
                    Find.LetterStack.ReceiveLetter(ext.chapterLetterLabel ?? "Urraveth remains", ext.chapterLetterText,
                        LetterDefOf.NeutralEvent, this);
                }
                return "read " + ext.chapter;
            }
            r.Complete(this);
            return "complete";
        }

        private IntVec3 InteractionOrAdjacent()
        {
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(this))
            {
                if (c.InBounds(Map) && c.Standable(Map))
                {
                    return c;
                }
            }
            return Position;
        }

        // ── load, creak, collapse ────────────────────────────────────────────────────────────────
        public float CurrentLoad()
        {
            RM_UrravethPieceExtension ext = Ext;
            if (ext == null || !Spawned)
            {
                return 0f;
            }
            float occupants = 0f;
            foreach (IntVec3 c in this.OccupiedRect())
            {
                List<Thing> things = c.GetThingList(Map);
                for (int i = 0; i < things.Count; i++)
                {
                    Thing t = things[i];
                    if (t is Pawn p && !p.Dead)
                    {
                        occupants += p.BodySize;
                    }
                    else if (t.def.category == ThingCategory.Item)
                    {
                        occupants += RM_UrravethKernel.ItemLoad(t.GetStatValue(StatDefOf.Mass), t.stackCount, ext.itemMassPerLoad);
                    }
                }
            }
            int heavy = 0;
            foreach (RM_Building_UrravethPiece s in Supporters())
            {
                if (RM_UrravethKernel.HeavilyDamaged(s.HitPoints, s.MaxHitPoints))
                {
                    heavy++;
                }
            }
            return RM_UrravethKernel.Load(occupants, lostSupports, ext.loadCapacity, heavy);
        }

        public bool Overloaded => Ext != null && RM_UrravethKernel.Overloaded(CurrentLoad(), Ext.loadCapacity);

        /// <summary>Adjacent pieces of strictly lower rank (they hold this one up).</summary>
        public IEnumerable<RM_Building_UrravethPiece> Supporters() => Neighbours().Where(n => RM_UrravethKernel.IsSupporter(n.Ext.supportRank, Ext.supportRank));

        /// <summary>Adjacent pieces of strictly higher rank (this one holds them up).</summary>
        public IEnumerable<RM_Building_UrravethPiece> Supported() => Neighbours().Where(n => RM_UrravethKernel.IsSupported(n.Ext.supportRank, Ext.supportRank));

        public IEnumerable<RM_Building_UrravethPiece> Neighbours()
        {
            if (!Spawned || Ext == null)
            {
                yield break;
            }
            CellRect mine = this.OccupiedRect();
            foreach (RM_Building_UrravethPiece p in RM_Urraveth.PiecesOn(Map))
            {
                if (p != this && p.Ext != null && RM_Urraveth.Adjacent(mine, p.OccupiedRect()))
                {
                    yield return p;
                }
            }
        }

        public bool AnyPawnNear()
        {
            float r = Ext?.nearRadius ?? 10f;
            IntVec3 at = Position;
            foreach (Pawn p in Map.mapPawns.AllPawnsSpawned)
            {
                if (!p.Dead && RM_UrravethKernel.PawnNear(p.Position.x - at.x, p.Position.z - at.z, r, def.size.x, def.size.z))
                {
                    return true;
                }
            }
            return false;
        }

        public int WindowTicks => RM_UrravethKernel.WindowTicks(RM_WebworkSettings.urravethWarningHours);

        public override void TickRare()
        {
            base.TickRare();
            StepLoad(RM_UrravethKernel.RareTicks);
        }

        /// <summary>One load evaluation covering <paramref name="ticks"/> ticks. Public for the proof tool.</summary>
        public void StepLoad(int ticks)
        {
            if (!Spawned || !RM_WebworkSettings.urravethEnabled || Ext == null)
            {
                return;
            }
            switch (RM_UrravethKernel.Step(ref creakTicksLeft, Overloaded, AnyPawnNear, ticks, WindowTicks))
            {
                case CreakEvent.Started:
                    CreakEffects();
                    break;
                case CreakEvent.Settled:
                    Messages.Message("The " + LabelNoCount + " settles. The load is off it.", this, MessageTypeDefOf.NeutralEvent);
                    break;
                case CreakEvent.Tick:
                    FleckMaker.ThrowDustPuff(this.OccupiedRect().RandomCell, Map, 1.2f);
                    break;
                case CreakEvent.Collapse:
                    FleckMaker.ThrowDustPuff(this.OccupiedRect().RandomCell, Map, 1.2f);
                    Collapse();
                    break;
            }
        }

        public void StartCreaking()
        {
            creakTicksLeft = WindowTicks;
            CreakEffects();
        }

        private void CreakEffects()
        {
            RM_Urraveth.Sound(Ext.creakSound)?.PlayOneShot(new TargetInfo(Position, Map));
            FleckMaker.ThrowDustPuff(this.OccupiedRect().RandomCell, Map, 1.6f);
            Messages.Message("The " + LabelNoCount + " creaks under the load. It will give way in about "
                + (creakTicksLeft / 2500f).ToString("0.#") + " hours unless the weight comes off.",
                this, MessageTypeDefOf.NegativeEvent);
        }

        /// <summary>The piece gives way: crush everything in its footprint, leave bone rubble, and load what it held up.
        /// Returns the number of things damaged.</summary>
        public int Collapse()
        {
            Map map = Map;
            if (map == null)
            {
                return 0;
            }
            RM_UrravethPieceExtension ext = Ext;
            CellRect rect = this.OccupiedRect();
            List<Thing> crushed = new List<Thing>();
            foreach (IntVec3 c in rect)
            {
                foreach (Thing t in c.GetThingList(map))
                {
                    if (t != this && (t is Pawn || t.def.category == ThingCategory.Item || t.def.category == ThingCategory.Building))
                    {
                        crushed.Add(t);
                    }
                }
            }
            float mult = RM_WebworkSettings.urravethCollapseDamageMultiplier;
            foreach (Thing t in crushed.Distinct())
            {
                int dmg = RM_UrravethKernel.CollapseDamage(RM_Urraveth.CrushDamage.RandomInRange, mult, Rand.Value);
                if (dmg <= 0 || t.Destroyed)
                {
                    continue;
                }
                DamageInfo dinfo = new DamageInfo(DamageDefOf.Crush, dmg, 0f, -1f, null, null, null, DamageInfo.SourceCategory.Collapse);
                dinfo.SetBodyRegion(BodyPartHeight.Top, BodyPartDepth.Outside);
                t.TakeDamage(dinfo);
            }
            RM_Urraveth.Sound(ext?.collapseSound)?.PlayOneShot(new TargetInfo(Position, map));
            Messages.Message("The " + LabelNoCount + " gives way.", new TargetInfo(Position, map), MessageTypeDefOf.NegativeEvent);
            Destroy(DestroyMode.KillFinalize);
            ThingDef filth = RM_Urraveth.Def(ext?.rubbleFilth);
            foreach (IntVec3 c in rect)
            {
                if (filth != null && c.InBounds(map))
                {
                    FilthMaker.TryMakeFilth(c, map, filth, 2);
                }
                FleckMaker.ThrowDustPuff(c, map, 2f);
            }
            ThingDef chunk = RM_Urraveth.Def(ext?.rubbleChunk);
            if (chunk != null)
            {
                GenPlace.TryPlaceThing(ThingMaker.MakeThing(chunk), rect.CenterCell, map, ThingPlaceMode.Near);
            }
            return crushed.Count;
        }

        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            // Any removal (collapse, deconstruction for bone, destruction) loads every piece this one held up.
            if (Spawned && Ext != null)
            {
                foreach (RM_Building_UrravethPiece s in Supported().ToList())
                {
                    s.lostSupports++;
                    if (RM_UrravethKernel.StartsCreakingOnLoss(RM_WebworkSettings.urravethEnabled, s.Creaking, s.Overloaded))
                    {
                        s.StartCreaking();
                    }
                }
            }
            base.Destroy(mode);
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            List<string> lines = new List<string>();
            RM_UrravethPieceExtension ext = Ext;
            if (ext != null)
            {
                lines.Add(wrapped ? "Wrapped in old silk. Examine it to read the bone."
                                  : "Read: " + (ext.chapter ?? "?").ToUpperInvariant() + (CanOpenLastWrapping ? ". The last wrapping is inside the skull." : "."));
                if (Creaking)
                {
                    lines.Add("Creaking under load: gives way in " + (creakTicksLeft / 2500f).ToString("0.#") + " h unless the weight comes off.");
                }
            }
            string mine = string.Join("\n", lines);
            return s.NullOrEmpty() ? mine : (mine.NullOrEmpty() ? s : s + "\n" + mine);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wrapped, "wrapped", true);
            Scribe_Values.Look(ref creakTicksLeft, "creakTicksLeft", -1);
            Scribe_Values.Look(ref lostSupports, "lostSupports", 0);
        }
    }

    public class RM_JobDriver_ExamineUrraveth : JobDriver
    {
        private RM_Building_UrravethPiece Piece => (RM_Building_UrravethPiece)job.targetA.Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !RM_UrravethKernel.ExamineAllowed(RM_WebworkSettings.urravethEnabled, Piece.wrapped, Piece.CanOpenLastWrapping));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil work = Toils_General.Wait(Piece.ExamineTicks, TargetIndex.A);
            work.WithProgressBarToilDelay(TargetIndex.A);
            work.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            work.activeSkill = () => SkillDefOf.Intellectual;
            yield return work;
            yield return Toils_General.Do(() =>
            {
                Piece.FinishExamine(pawn);
                pawn.skills?.Learn(SkillDefOf.Intellectual, 30f); // PROVISIONAL
            });
        }
    }

    public class RM_MapComponent_UrravethReading : MapComponent
    {
        public bool sitePlaced;
        public bool complete;
        public bool outlineDrawn;
        public int outlineCells;
        public CellRect siteRect = CellRect.Empty;
        private List<string> chapters = new List<string>();

        public RM_MapComponent_UrravethReading(Map map) : base(map)
        {
        }

        /// <summary>Chapters read so far, in the order the bones tell them (pinned, bound, cut, eaten).</summary>
        public List<string> Chapters => RM_UrravethKernel.Ordered(chapters);

        public void RecordChapter(string chapter, Thing from)
        {
            RM_UrravethKernel.RecordChapter(chapters, chapter);
        }

        public void Complete(RM_Building_UrravethPiece skull)
        {
            if (complete)
            {
                return;
            }
            complete = true;
            DrawOutline(skull);
            RM_UrravethPieceExtension ext = skull.Ext;
            Find.LetterStack.ReceiveLetter(ext?.finalLetterLabel ?? "Urraveth remains", ext?.finalLetterText ?? "",
                LetterDefOf.NeutralEvent, skull);
        }

        /// <summary>A one-time filth line tracing the living body: an ellipse around the site, two cells out.</summary>
        private void DrawOutline(RM_Building_UrravethPiece skull)
        {
            if (outlineDrawn)
            {
                return;
            }
            outlineDrawn = true;
            CellRect rect = siteRect.IsEmpty ? skull.OccupiedRect().ExpandedBy(6) : siteRect;
            ThingDef filth = RM_Urraveth.Def(skull.Ext?.outlineFilth);
            if (filth == null)
            {
                return;
            }
            foreach (IntVec3 cell in rect.ExpandedBy(2))
            {
                if (!cell.InBounds(map) || !cell.Standable(map))
                {
                    continue;
                }
                if (RM_UrravethKernel.OutlineCell(cell.x, cell.z, rect.minX, rect.minZ, rect.Width, rect.Height) && FilthMaker.TryMakeFilth(cell, map, filth, 1))
                {
                    outlineCells++;
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref sitePlaced, "sitePlaced", false);
            Scribe_Values.Look(ref complete, "complete", false);
            Scribe_Values.Look(ref outlineDrawn, "outlineDrawn", false);
            Scribe_Values.Look(ref outlineCells, "outlineCells", 0);
            Scribe_Values.Look(ref siteRect, "siteRect", CellRect.Empty);
            Scribe_Collections.Look(ref chapters, "chapters", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && chapters == null)
            {
                chapters = new List<string>();
            }
        }
    }

    /// <summary>Places the urraveth on a Webwork map with chance RM_WebworkSettings.urravethSiteChance. The planet is
    /// never touched: this is a map GenStep, self-gated on map.Biome like RM_GenStep_WebworkNest.</summary>
    public class RM_GenStep_UrravethRemains : GenStep
    {
        public const int SiteWidth = 15, SiteHeight = 9;
        private const int EdgeMargin = 8;
        private const int PlacementAttempts = 200;

        /// <summary>The body, head east: (defName, min corner x, min corner z) inside the 15 x 9 site.</summary>
        public static readonly (string def, int x, int z)[] Layout =
        {
            ("RM_Urraveth_LimbPile", 1, 2),     // hind legs (z 2: touches the pelvis at z 4, so losing them loads it; at z 1 a bare row separated them)
            ("RM_Urraveth_LimbPile", 9, 1),     // forelegs
            ("RM_Urraveth_Pelvis", 0, 4),
            ("RM_Urraveth_RibSection", 3, 3),
            ("RM_Urraveth_RibSection", 6, 3),
            ("RM_Urraveth_NeckRun", 9, 5),
            ("RM_Urraveth_Skull", 12, 4),
        };

        public override int SeedPart => 518204377;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (map.Biome == null || map.Biome.defName != RM_GenStep_WebworkNest.WebworkBiomeDefName)
            {
                return;
            }
            if (!RollSite())
            {
                return;
            }
            PlaceSite(map);
        }

        /// <summary>The Mod Settings gate: enabled, then the per-map site chance.</summary>
        public static bool RollSite() => RM_UrravethKernel.RollSite(RM_WebworkSettings.urravethEnabled, RM_WebworkSettings.urravethSiteChance, Rand.Value);

        /// <summary>Everything after the biome and chance gates. Returns pieces placed, or -1 when nothing was.</summary>
        public int PlaceSite(Map map)
        {
            if (!RM_WebworkSettings.urravethEnabled)
            {
                return -1;
            }
            foreach (var row in Layout)
            {
                if (RM_Urraveth.Def(row.def) == null)
                {
                    Log.Warning("[RM Webwork] RM_GenStep_UrravethRemains: " + row.def + " not found; site skipped.");
                    return -1;
                }
            }
            if (!TryFindSite(map, out CellRect site))
            {
                Log.Message("[RM Webwork] RM_GenStep_UrravethRemains: no open " + SiteWidth + "x" + SiteHeight
                    + " ground on this map; no urraveth here.");
                return -1;
            }
            int placed = 0;
            foreach (var row in Layout)
            {
                ThingDef d = RM_Urraveth.Def(row.def);
                IntVec3 min = new IntVec3(site.minX + row.x, 0, site.minZ + row.z);
                CellRect probe = GenAdj.OccupiedRect(IntVec3.Zero, Rot4.North, d.size);
                IntVec3 center = new IntVec3(min.x - probe.minX, 0, min.z - probe.minZ);
                GenSpawn.Spawn(ThingMaker.MakeThing(d), center, map, Rot4.North, WipeMode.Vanish);
                placed++;
            }
            RM_MapComponent_UrravethReading r = map.GetComponent<RM_MapComponent_UrravethReading>();
            if (r != null)
            {
                r.sitePlaced = true;
                r.siteRect = site;
            }
            Log.Message("[RM Webwork] RM_GenStep_UrravethRemains: placed the urraveth (" + placed + " pieces) at " + site.CenterCell + ".");
            return placed;
        }

        private static bool TryFindSite(Map map, out CellRect site)
        {
            for (int i = 0; i < PlacementAttempts; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                CellRect r = new CellRect(c.x, c.z, SiteWidth, SiteHeight);
                if (!RM_UrravethKernel.SiteInMargin(r.minX, r.minZ, r.maxX, r.maxZ, map.Size.x, map.Size.z, EdgeMargin))
                {
                    continue;
                }
                bool ok = true;
                foreach (IntVec3 x in r)
                {
                    if (!x.Standable(map) || x.GetEdifice(map) != null || x.Roofed(map))
                    {
                        ok = false;
                        break;
                    }
                }
                if (ok)
                {
                    site = r;
                    return true;
                }
            }
            site = CellRect.Empty;
            return false;
        }
    }

    [DefOf]
    public static class RM_UrravethDefOf
    {
        public static JobDef RM_ExamineUrravethRemains;

        static RM_UrravethDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_UrravethDefOf));
        }
    }
}
