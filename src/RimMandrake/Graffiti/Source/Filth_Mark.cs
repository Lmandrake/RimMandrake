using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 mechanism 1: "A Filth subclass
    // carrying provenance (maker pawn, maker faction, maker ideo, subject,
    // placed tick, placer)." Everything else this item adds - relation-keyed
    // reactions, going-over, scrub protection, tier-A sigil rendering -
    // reads these fields. RM_BaseGraffiti's <thingClass> now names this
    // class instead of plain Filth (Defs/ThingDefs_Graffiti.xml).
    //
    // References are Scribe_References, not Scribe_Deep - maker/subject are
    // Pawns and makerFaction/makerIdeo are Factions/Ideos that already exist
    // elsewhere in the save (Pawn, Faction and Ideo are all
    // ILoadReferenceable - Ideo confirmed via RimSage this pass,
    // RimWorld/Ideo.cs:9 "public class Ideo : IExposable,
    // ILoadReferenceable"). A dead pawn counts as destroyed, and
    // Scribe_References writes "null" for a destroyed thing unless
    // saveDestroyedThings is set (Verse/Scribe_References.cs): every
    // memorial forgot who it was for at its first save (live, pass 10:
    // Lark's memorial to Pell saved rmMarkSubject null, lost Pell's painted
    // face, and Lark painted Pell another). The pawns are kept the way
    // vanilla keeps a relation's: saveDestroyedThings, and a pawn the
    // world has discarded is let go before the save so nothing warns.
    public class Filth_Mark : Filth
    {
        public Pawn maker;
        public Faction makerFaction;
        public Ideo makerIdeo;
        public Pawn subject;
        public int placedTick = -1;

        // GRAFFITI_WALLFACE (owner, by card 2026-10-22: "Q9 → Graffiti floor cell drawn offset facing wall"): the side of the
        // floor cell the wall it was painted on stands (RM_GraffitiKernel.WallSide; Rot4 int, NoWall = none). Read at the
        // first spawn (a mark from an older save has none and reads it then). The paint goes with its wall
        // (RaidExitTagger's sibling WallLossPatch): nothing may hang in the air. Print draws the mark on that wall cell and turned to face it.
        public int wallSide = RM_GraffitiKernel.NoWall;

        // Which of the def's drawings this is, and its pigment, chosen when painted to differ from what's already on this stretch of
        // wall. -1 (an older save's mark): the old pick by thing id.
        public int variant = -1;
        public int pigment;

        // The faction a mark insults; the name of who it's about, for when their body is long gone; who crossed it out.
        public Faction targetFaction;
        public string subjectName;
        public bool defaced;
        public Pawn defacedBy;

        // Who has read this mark and when; which factions' visitors have; how it landed, for anyone who inspects the wall.
        private Dictionary<int, int> readBy = new Dictionary<int, int>();
        private List<int> factionsRead = new List<int>();
        private int angered, amused, moved;
        private bool skipCleanNotice;

        // Owner, 2026-11-07: "Please ensure that a person's art skill goes into the art's effect." The painter's hand, rolled by the game's own
        // quality roll when the mark is made (RM_GraffitiKernel.CraftBeauty, CraftReach, CraftLook). A mark from an older save, or with no
        // maker, has no craft and keeps its def's Beauty.
        public int craft = RM_GraffitiKernel.Normal;
        public bool hasCraft;

        // Paint weathers (RM_GraffitiKernel.WeatherDays): it fades over the last 40% of its life and then is gone. A permanent mark never does:
        // left for the owner's later Luminous Pigments, which make graffiti permanent. weatherStep is the fade drawn now, 0..4.
        public bool permanent;
        internal int weatherStep;

        // A reply in paint, painted over the mark it answers: the last word. Whoever it's about may scrub it, cross it out or have it out
        // with the painter, but not paint back (live pass 13: Karen and Lark painted a mockery over each other's every four hours, seven
        // messages in seven hours, and nothing ever ended it).
        public bool lastWord;

        // The share of its drawing's full size this mark was painted at, squeezed into a gap (GraffitiPool.FitFor). Its width on the wall
        // is Width, which every overlap and gap measure uses, so a smaller tag is neither erased nor erasing as if it were full size.
        public float fit = 1f;

        internal float Width => GraffitiPool.WidthOf(def) * fit;

        // Who held this mark dear: readers it moved, a tribute's subject, a mourner. Somebody who scrubs it in a cleaning fit answers to them.
        private List<int> valuedBy = new List<int>();

        // Tier-A rendering cache (design §3.1): built lazily from
        // ModExtension_Graffiti.sigilTierA + sigilFrameTexPath + makerIdeo.
        // Never Scribed - rebuilt from the (Scribed) fields above every
        // load, same as any other Material/Graphic cache in vanilla.
        private Material cachedFrameMat;
        private Material cachedIconMat;
        private Material cachedHeadMat;
        private bool sigilMatsBuilt;

        /// <summary>Test reads (RM_GraffitiProof, GRAFFITI_V1_LIVE_PROOF_1 A3): the tier-A composite's two materials, null when absent.</summary>
        internal Material ProbeFrameMat => cachedFrameMat;
        internal Material ProbeIconMat => cachedIconMat;

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            // Before base.SpawnSetup, which registers the mark for the map mesh that Print then builds.
            if (wallSide == RM_GraffitiKernel.NoWall)
            {
                wallSide = ReadWallSide(Position, map);
            }
            base.SpawnSetup(map, respawningAfterLoad);
            weatherStep = WeatherStepNow(out _);
            if (placedTick < 0 && !respawningAfterLoad)
            {
                placedTick = Find.TickManager.TicksGame;
            }
            // Materials wait for Print: this can run on the loading thread, and painting an icon needs the main one.
            sigilMatsBuilt = false;
            MapComponent_GraffitiSocial.For(map)?.marks.Add(this);
        }

        public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
        {
            MapComponent_GraffitiSocial.For(Map)?.marks.Remove(this);
            base.DeSpawn(mode);
        }

        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            if (Spawned && !skipCleanNotice)
            {
                GraffitiSocial.Notify_Cleaned(this);
            }
            if (Spawned) GraffitiSocial.Notify_MockeryGone(this);
            base.Destroy(mode);
        }

        /// <summary>Where the paint is: on the face of its wall, three quarters of a cell on from the floor cell the mark stands on. The
        /// scrub order's icon, the selection bracket, the cleaning dust and its progress bar go to the paint, not the floor before it (live
        /// 2026-11-08: every scrub icon sat on the floor). Print draws from the wall itself and takes only this altitude.</summary>
        public override Vector3 DrawPos
        {
            get
            {
                Vector3 v = base.DrawPos;
                if (wallSide < 0 || wallSide > 3) return v;
                IntVec3 f = new Rot4(wallSide).FacingCell;
                return v + new Vector3(f.x * 0.75f, 0f, f.z * 0.75f);
            }
        }

        /// <summary>This mark is going by another hand than the cleaning job, and that hand tells the story itself.</summary>
        internal void SkipCleanNotice() { skipCleanNotice = true; }

        /// <summary>What this mark says, from its def, or worked out from the kind of mark it is.</summary>
        public RM_Meaning Meaning
        {
            get
            {
                ModExtension_Graffiti ext = def.GetModExtension<ModExtension_Graffiti>();
                if (ext == null) return RM_Meaning.None;
                // A tribute to someone who has died since is their memorial now: nobody is jealous of the dead, and a friend reading it
                // mourns (GPT broaden pass 13, lead 6).
                if (ext.meaning == RM_Meaning.Tribute && subject != null && subject.Dead) return RM_Meaning.Memorial;
                if (ext.meaning != RM_Meaning.None) return ext.meaning;
                if (ext.sigilTierA || !ext.requiresAnyMeme.NullOrEmpty()) return RM_Meaning.Devotion;
                if (ext.category == GraffitiCategory.Mural) return RM_Meaning.Beauty;
                if (ext.category == GraffitiCategory.Jest && ext.form != GraffitiForm.Scrawl) return RM_Meaning.Jest;
                return RM_Meaning.None;
            }
        }

        public string SubjectName => subject?.LabelShort ?? subjectName ?? "someone";

        internal bool ReadyToBeRead(Pawn viewer, int now)
        {
            return !readBy.TryGetValue(viewer.thingIDNumber, out int last) || now - last >= RM_GraffitiKernel.ReadAgainTicks;
        }

        /// <summary>Has this pawn never read this mark? Opinion and grudges come only from the first reading.</summary>
        internal bool FirstReadBy(Pawn viewer) { return !readBy.ContainsKey(viewer.thingIDNumber); }

        internal void NoteValued(Pawn p) { if (p != null && !valuedBy.Contains(p.thingIDNumber)) valuedBy.Add(p.thingIDNumber); }

        internal bool ValuedBy(Pawn p) { return p != null && valuedBy.Contains(p.thingIDNumber); }

        /// <summary>How far its meaning reaches, by its maker's hand: a clumsy insult is laughed off and a great one sticks.</summary>
        public float Reach => hasCraft ? RM_GraffitiKernel.CraftReach(craft) : 1f;

        public string CraftLabel => hasCraft ? ((QualityCategory)craft).GetLabel() : null;

        /// <summary>How weathered the mark is drawn and counted now: its last weather step, 0 fresh to 1 gone.</summary>
        internal float Fade => weatherStep * 0.25f;

        /// <summary>The weather step its age has reached (0..4), 0 for a permanent mark or one with no date.</summary>
        internal int WeatherStepNow(out float fade)
        {
            fade = 0f;
            if (permanent || placedTick == -1 || !Spawned) return 0;     // -1 is no date; a proof may date a mark back before the game began
            ModExtension_Graffiti ext = def.GetModExtension<ModExtension_Graffiti>();
            float life = RM_GraffitiKernel.WeatherDays(ext?.form ?? GraffitiForm.Scrawl, hasCraft ? craft : RM_GraffitiKernel.Normal, !Map.roofGrid.Roofed(Position), thingIDNumber);
            fade = RM_GraffitiKernel.WeatherFade((Find.TickManager.TicksGame - placedTick) / (float)GenDate.TicksPerDay, life);
            return RM_GraffitiKernel.WeatherStep(fade);
        }

        // The room counts a mark's beauty on the floor cell it was painted from (CellBeauty ignores whatever stands on a wall's own cell), and
        // under a roof it counts filth at 0.3. This undoes that for craft, so a masterwork is worth its table value indoors and out.
        public override float GetBeauty(bool outside)
        {
            if (!hasCraft) return base.GetBeauty(outside);
            float net = NetBeauty;
            return Spawned && Map.roofGrid.Roofed(Position) ? net / 0.3f : net;
        }

        /// <summary>What this mark does to its cell's beauty, roofs aside: its craft, or a crossed-out ruin of it.</summary>
        public float NetBeauty
        {
            get
            {
                float worn = 1f - 0.6f * Fade;
                if (!hasCraft) return this.GetStatValue(StatDefOf.Beauty) * worn;
                float net = RM_GraffitiKernel.CraftBeauty(craft);
                return (defaced ? System.Math.Min(net, RM_GraffitiKernel.CraftBeauty(RM_GraffitiKernel.Poor)) : net) * worn;
            }
        }

        /// <summary>The same mark painted again where it stands is a new piece of work, by a new hand: nobody has read it, nobody has crossed it out.</summary>
        private void MadeAfresh()
        {
            readBy.Clear();
            factionsRead.Clear();
            valuedBy.Clear();
            angered = amused = moved = 0;
            defaced = false;
            defacedBy = null;
        }

        internal void NoteRead(Pawn viewer, int now) { readBy[viewer.thingIDNumber] = now; }

        internal bool FactionHasRead(Faction f) { return factionsRead.Contains(f.loadID); }

        internal void NoteFactionRead(Faction f) { factionsRead.Add(f.loadID); }

        internal void NoteReaction(RM_Reaction r)
        {
            switch (r)
            {
                case RM_Reaction.Humiliated: case RM_Reaction.FriendDefends: case RM_Reaction.Jealous: case RM_Reaction.Offended: case RM_Reaction.RivalTag:
                case RM_Reaction.Disapproves: case RM_Reaction.Scoffs: case RM_Reaction.Defiant: case RM_Reaction.Uneasy:
                    angered++;
                    break;
                case RM_Reaction.Amused: case RM_Reaction.Gleeful: case RM_Reaction.ShrugsOff:
                    amused++;
                    break;
                case RM_Reaction.Moved: case RM_Reaction.Honored: case RM_Reaction.Mourning: case RM_Reaction.Uplifted: case RM_Reaction.Warmed: case RM_Reaction.FriendTag:
                    moved++;
                    break;
            }
        }

        /// <summary>A brush through it: it stays on the wall, crossed out, and has lost its power over anyone but its maker.</summary>
        internal void CrossOut(Pawn by)
        {
            defaced = true;
            defacedBy = by;
            if (Spawned) Map.mapDrawer.MapMeshDirty(Position, MapMeshFlagDefOf.Things);
        }

        /// <summary>The story of this mark, for whoever inspects its wall.</summary>
        internal string StoryLines()
        {
            string line = def.LabelCap;
            if (hasCraft) line += " (" + CraftLabel + ")";
            if (weatherStep > 0) line += weatherStep >= 3 ? ", nearly weathered away" : ", fading";
            if (maker != null) line += ", by " + maker.LabelShort;
            else if (makerFaction != null) line += ", by " + makerFaction.Name;
            if (subject != null || !subjectName.NullOrEmpty()) line += ", about " + SubjectName + (subject != null && subject.Dead && def != RMGraffitiDefOf.RM_Graffiti_Memorial ? " (dead since)" : "");
            if (targetFaction != null) line += ", insulting " + targetFaction.Name;
            if (defaced) line += defacedBy != null ? ". Crossed out by " + defacedBy.LabelShort : ". Crossed out";
            if (angered + amused + moved > 0)
            {
                var felt = new List<string>();
                if (angered > 0) felt.Add(angered + " angered");
                if (amused > 0) felt.Add(amused + " amused");
                if (moved > 0) felt.Add(moved + " moved");
                line += " (" + string.Join(", ", felt) + ")";
            }
            return line;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            if (Scribe.mode == LoadSaveMode.Saving)
            {
                if (maker != null && maker.Discarded) maker = null;
                if (subject != null && subject.Discarded) subject = null;
                if (defacedBy != null && defacedBy.Discarded) defacedBy = null;
            }
            Scribe_References.Look(ref maker, "rmMarkMaker", saveDestroyedThings: true);
            Scribe_References.Look(ref makerFaction, "rmMarkMakerFaction");
            Scribe_References.Look(ref makerIdeo, "rmMarkMakerIdeo");
            Scribe_References.Look(ref subject, "rmMarkSubject", saveDestroyedThings: true);
            Scribe_Values.Look(ref placedTick, "rmMarkPlacedTick", -1);
            Scribe_Values.Look(ref permanent, "rmMarkPermanent");
            Scribe_Values.Look(ref lastWord, "rmMarkLastWord");
            Scribe_Values.Look(ref fit, "rmMarkFit", 1f);
            Scribe_Values.Look(ref wallSide, "rmMarkWallSide", RM_GraffitiKernel.NoWall);
            Scribe_Values.Look(ref variant, "rmMarkVariant", -1);
            Scribe_Values.Look(ref pigment, "rmMarkPigment", 0);
            Scribe_References.Look(ref targetFaction, "rmMarkTargetFaction");
            Scribe_Values.Look(ref subjectName, "rmMarkSubjectName");
            Scribe_Values.Look(ref defaced, "rmMarkDefaced");
            Scribe_References.Look(ref defacedBy, "rmMarkDefacedBy", saveDestroyedThings: true);
            Scribe_Collections.Look(ref readBy, "rmMarkReadBy", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref factionsRead, "rmMarkFactionsRead", LookMode.Value);
            Scribe_Values.Look(ref angered, "rmMarkAngered");
            Scribe_Values.Look(ref amused, "rmMarkAmused");
            Scribe_Values.Look(ref moved, "rmMarkMoved");
            Scribe_Values.Look(ref craft, "rmMarkCraft", RM_GraffitiKernel.Normal);
            Scribe_Values.Look(ref hasCraft, "rmMarkHasCraft");
            Scribe_Collections.Look(ref valuedBy, "rmMarkValuedBy", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                sigilMatsBuilt = false;
                readBy = readBy ?? new Dictionary<int, int>();
                factionsRead = factionsRead ?? new List<int>();
                valuedBy = valuedBy ?? new List<int>();
                // A form's ceiling can come down between versions (pass 9: a scrawl is never better than poor work); a saved mark keeps to it.
                ModExtension_Graffiti ext = def?.GetModExtension<ModExtension_Graffiti>();
                if (hasCraft && ext != null) craft = System.Math.Min(craft, RM_GraffitiKernel.CraftCeiling(ext.form));
            }
        }

        // Stamps provenance on a freshly (or already-)made mark. Called by
        // GraffitiPool's placers instead of FilthMaker.TryMakeFilth
        // directly, so every placer (spree, joy, designator, raid-exit)
        // shares one going-over + provenance implementation.
        //
        // Going-over (design §1.6 / fork F4, ruled 2026-10-09: "going-over in v1"): a rival
        // mark already at the cell is destroyed first, never thickened
        // alongside the new one - two different marks papering over each
        // other, not one filth pile growing. "Rival" = any other
        // Filth_Mark whose def differs from markDef; thickening the SAME
        // def (the vanilla FilthMaker behaviour) is left alone.
        public static Filth_Mark MakeMark(IntVec3 cell, Map map, ThingDef markDef, Pawn maker, Pawn subject = null, Faction targetFaction = null, bool ordered = false, bool reply = false, float fit = 1f)
        {
            bool repaint = false;
            // A mark that sends its own message carries the going-over in it: one act, one line.
            bool tells = subject != null || targetFaction != null;
            var over = new System.Collections.Generic.List<string>();
            // GPT deep review 2026-10-22 #6: rivals are collected first and destroyed only once the new mark exists, so a
            // refused placement no longer erases the old mark and leaves the wall bare
            var rivals = new System.Collections.Generic.List<Filth_Mark>();
            if (cell.IsValid && map != null)
            {
                foreach (Thing t in cell.GetThingList(map))
                {
                    if (t is Filth_Mark rival && RM_GraffitiKernel.IsRival(true, rival.def == markDef))
                    {
                        rivals.Add(rival);
                    }
                    else if (t is Filth_Mark same && same.def == markDef)
                    {
                        repaint = true;
                        if (same.maker != null && same.maker != maker)
                        {
                            GraffitiSocial.Notify_WentOver(same, maker, tells, reply, same);    // the same drawing, repainted by this hand
                            if (!over.Contains(same.maker.LabelShort)) over.Add(same.maker.LabelShort);
                        }
                    }
                }
                // Going over reaches along the wall: whatever this mark's drawing will lie on top of, on either face of it.
                int side = ReadWallSide(cell, map);
                if (side != RM_GraffitiKernel.NoWall)
                {
                    foreach (Filth_Mark under in MarksOverlapping(cell + new Rot4(side).FacingCell, side, GraffitiPool.WidthOf(markDef) * fit / 2f, map, null))
                    {
                        if (under.Position != cell && !rivals.Contains(under))
                        {
                            rivals.Add(under);
                        }
                    }
                }
            }
            // GRAFFITI_V1_LIVE_PROOF_1 (GPT review): no propagation. Vanilla filth spills onto a neighbour when the cell will not
            // take it; a mark is painted on THIS wall cell or not at all, and a spill elsewhere would let the going-over below erase
            // the rival with nothing painted over it.
            if (!FilthMaker.TryMakeFilth(cell, map, markDef, out Filth outFilth, 1, FilthSourceFlags.None, false) || outFilth == null
                || outFilth.Position != cell)
            {
                return null;
            }
            foreach (Filth_Mark rival in rivals)
            {
                if (rival.Destroyed) continue;
                GraffitiSocial.Notify_WentOver(rival, maker, tells, reply, outFilth as Filth_Mark);
                if (rival.maker != null && rival.maker != maker && !over.Contains(rival.maker.LabelShort)) over.Add(rival.maker.LabelShort);
                rival.SkipCleanNotice();
                rival.Destroy();
            }
            if (!(outFilth is Filth_Mark mark))
            {
                return null;
            }
            if (repaint) mark.MadeAfresh();
            mark.fit = fit;
            mark.maker = maker;
            mark.makerFaction = maker?.Faction;
            mark.makerIdeo = GraffitiJobUtility.IdeoOf(maker);
            mark.subject = subject;
            mark.subjectName = subject?.LabelShort;
            mark.targetFaction = targetFaction;
            if (mark.placedTick < 0)
            {
                mark.placedTick = Find.TickManager.TicksGame;
            }
            mark.hasCraft = maker?.skills != null && maker.RaceProps.Humanlike;
            // Ordered work may spend an inspiration; a tag dashed off in an idle moment doesn't use one up (personality pass, section 9).
            mark.craft = mark.hasCraft ? (int)QualityUtility.GenerateQualityCreatedByPawn(maker, SkillDefOf.Artistic, ordered) : RM_GraffitiKernel.Normal;
            ModExtension_Graffiti form = markDef.GetModExtension<ModExtension_Graffiti>();
            if (form != null) mark.craft = System.Math.Min(mark.craft, RM_GraffitiKernel.CraftCeiling(form.form));
            mark.sigilMatsBuilt = false;
            mark.RebuildSigilMats();
            mark.ChooseLook(cell, map);
            map.mapDrawer.MapMeshDirty(cell, MapMeshFlagDefOf.Things);
            // The room's beauty and impressiveness were worked out when the mark spawned, before its craft was rolled.
            cell.GetRoom(map)?.Notify_ContainedThingSpawnedOrDespawned(mark);
            // Painting a mockery over the one its subject painted of you is a reply, whatever road the brush came by.
            mark.lastWord = reply || (subject != null && rivals.Any(r => r.subject == maker && r.maker == subject && r.def == RMGraffitiDefOf.RM_Graffiti_Mockery));
            GraffitiSocial.Notify_Painted(mark, maker, tells && over.Count > 0 ? string.Join(" and ", over) : null);
            return mark;
        }

        /// <summary>This mark's drawing and pigment, unlike what's near it on the same line of sight: a second tag on this wall is
        /// the same hand in another colour or another hand, not a stamp.</summary>
        private void ChooseLook(IntVec3 cell, Map map)
        {
            var usedVariants = new System.Collections.Generic.HashSet<int>();
            var usedPigments = new System.Collections.Generic.HashSet<int>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(cell, LookRadius, useCenter: true))
            {
                if (!c.InBounds(map)) continue;
                foreach (Thing t in c.GetThingList(map))
                {
                    if (t is Filth_Mark m && m != this && m.def == def)
                    {
                        usedVariants.Add(m.variant);
                        usedPigments.Add(m.pigment);
                    }
                }
            }
            int count = Graphic is Graphic_Random random ? random.SubGraphicsCount : 1;
            variant = RM_GraffitiKernel.PickFree(count, usedVariants, Rand.Value);
            // A pigment the wall would swallow is no choice at all: chalk on marble, soot on slate.
            Color wallColor = WallPlane.FaceColor(cell + new Rot4(wallSide == RM_GraffitiKernel.NoWall ? 0 : wallSide).FacingCell, map);
            for (int i = 0; i < RM_GraffitiKernel.PigmentCount; i++)
            {
                if (!RM_GraffitiKernel.PigmentReads(i, wallColor.r, wallColor.g, wallColor.b)) usedPigments.Add(i);
            }
            pigment = RM_GraffitiKernel.PickFree(RM_GraffitiKernel.PigmentCount, usedPigments, Rand.Value);
            // A tag is its writer's: the same hand in the same colour, wherever they go, and one crew's raiders in one colour. So a wall shows
            // whose it is. A colour the wall would swallow falls through to the pick above.
            bool tag = def.GetModExtension<ModExtension_Graffiti>()?.form == GraffitiForm.Tag;
            int who = maker != null && maker.Faction == Faction.OfPlayer ? maker.thingIDNumber : (makerFaction?.loadID ?? -1);
            if (tag && who >= 0)
            {
                variant = RM_GraffitiKernel.HandChoice(who, count, 1);
                int own = RM_GraffitiKernel.HandChoice(who, RM_GraffitiKernel.PigmentCount, 2);
                if (RM_GraffitiKernel.PigmentReads(own, wallColor.r, wallColor.g, wallColor.b)) pigment = own;
            }
        }

        private const float LookRadius = 9f;

        /// <summary>An older save's pigment that its wall swallows under today's rule (RM_GraffitiKernel.PigmentReads: soot needs a pale wall)
        /// goes to the next one that reads, so the same mark keeps a colour, just a visible one. True if it changed.</summary>
        internal bool RepickUnreadPigment()
        {
            if (wallSide == RM_GraffitiKernel.NoWall || def.GetModExtension<ModExtension_Graffiti>()?.pigmented != true) return false;
            Color wall = WallPlane.FaceColor(Position + new Rot4(wallSide).FacingCell, Map);
            if (RM_GraffitiKernel.PigmentReads(pigment, wall.r, wall.g, wall.b)) return false;
            for (int k = 1; k < RM_GraffitiKernel.PigmentCount; k++)
            {
                int p = (pigment + k) % RM_GraffitiKernel.PigmentCount;
                if (!RM_GraffitiKernel.PigmentReads(p, wall.r, wall.g, wall.b)) continue;
                pigment = p;
                sigilMatsBuilt = false;
                Map.mapDrawer.MapMeshDirty(Position, MapMeshFlagDefOf.Things);
                return true;
            }
            return false;
        }

        /// <summary>A poor hand's paint: overmixed toward mud, the colours gone brown and dull.</summary>
        private static Color Muddied(Color c, float mud)
        {
            if (mud <= 0f) return c;
            RM_Rgb m = RM_GraffitiKernel.Mud;
            Color muddy = new Color(m.r, m.g, m.b) * (0.6f + 0.4f * c.grayscale) * 1.6f;
            Color o = Color.Lerp(c, muddy, mud);
            o.a = 1f;
            return o;
        }

        private static Color PigmentOf(int index)
        {
            RM_Rgb p = RM_GraffitiKernel.PigmentColor(index);
            return new Color(p.r, p.g, p.b);
        }

        public override string GetInspectString()
        {
            string baseText = base.GetInspectString();
            float beauty = NetBeauty;
            string line = StoryLines() + "\nBeauty " + beauty.ToString("+0;-0;0") + ": " + RM_GraffitiKernel.BeautyWord(beauty);
            return string.IsNullOrEmpty(baseText) ? line : baseText + "\n" + line;
        }

        private void RebuildSigilMats()
        {
            sigilMatsBuilt = true;
            cachedFrameMat = null;
            cachedIconMat = null;
            cachedHeadMat = null;
            ModExtension_Graffiti ext = def.GetModExtension<ModExtension_Graffiti>();
            if (ext != null && subject != null && ext.hasSubject)
            {
                Texture2D head = WallPlane.PaintedPortrait(subject, pigment);
                if (head != null) cachedHeadMat = MaterialPool.MatFrom(head, ShaderDatabase.Mote, Color.white);
            }
            else if (ext != null && targetFaction != null)
            {
                Texture2D emblem = WallPlane.PaintedIcon(targetFaction.def.FactionIcon);
                if (emblem != null) cachedHeadMat = MaterialPool.MatFrom(emblem, ShaderDatabase.Mote, Color.Lerp(targetFaction.Color, new Color(0.45f, 0.42f, 0.38f), 0.3f));
            }
            if (ext == null || !ext.sigilTierA || makerIdeo == null)
            {
                return;
            }
            if (!string.IsNullOrEmpty(ext.sigilFrameTexPath))
            {
                cachedFrameMat = MaterialPool.MatFrom(ext.sigilFrameTexPath, ShaderDatabase.Mote);
            }
            Texture2D icon = WallPlane.PaintedIcon(makerIdeo.Icon) ?? makerIdeo.Icon;
            if (icon != null)
            {
                // Ideoligion colours are clean UI colours; on a wall they are the same hue in a mixed pigment.
                Color pigmentOfIdeo = Color.Lerp(makerIdeo.Color, new Color(0.45f, 0.42f, 0.38f), 0.3f) * 0.9f;
                pigmentOfIdeo.a = 1f;
                cachedIconMat = MaterialPool.MatFrom(icon, ShaderDatabase.Mote, pigmentOfIdeo);
            }
        }

        // A painted mark lies in its wall's plane (WallPlane, RM_GraffitiKernel.MarkPieces): stopped at the crease and the corners,
        // squashed the way the camera squashes that face. Tier-A sigils print the same way, frame then ideo icon. A mark with no
        // wall recorded draws as vanilla filth, flat on its floor.
        public override void Print(SectionLayer layer)
        {
            if (!sigilMatsBuilt)
            {
                RebuildSigilMats();
            }
            if (wallSide == RM_GraffitiKernel.NoWall)
            {
                base.Print(layer);
                return;
            }
            ModExtension_Graffiti ext = def.GetModExtension<ModExtension_Graffiti>();
            Vector2 size = def.graphicData?.drawSize ?? Vector2.one;
            RM_GraffitiKernel.HandOf(thingIDNumber, size.x, out float slope, out float scale, out float slide, out float lift, out bool flip);
            if (ext?.form == GraffitiForm.Scrawl)
            {
                scale = 1f;     // the ugliest thing on the wall gets no modest hand: the picture agrees with its Beauty
            }
            // A mark nobody's hand made (a staged one, a save from before craft) looks as its form allows: a scrawl is never neat.
            int look = hasCraft ? craft : (ext != null ? System.Math.Min(RM_GraffitiKernel.Normal, RM_GraffitiKernel.CraftCeiling(ext.form)) : RM_GraffitiKernel.Normal);
            RM_GraffitiKernel.CraftLook(look, out float craftThrough, out float wobble, out float mud);
            if (RM_GraffitiStage.smearOver) RM_GraffitiKernel.CraftLookBefore(look, ref mud);
            if (RM_GraffitiStage.oldWeather) craftThrough += RM_GraffitiKernel.CraftThroughPass16(look);
            slope *= wobble;
            float width = size.x * scale * fit;
            float height = RM_GraffitiKernel.ClimbHeight * Mathf.Min(1f, size.y) * scale * fit;
            float fade = Fade;
            float through = Mathf.Clamp(ThroughOf(ext) + craftThrough + 0.1f * fade, 0.04f, 0.85f);
            if (cachedFrameMat == null && cachedIconMat == null)
            {
                if (cachedHeadMat != null)
                {
                    // Their head in the gap the art leaves, under the art: the horns go over the hair.
                    float tc = WallPlane.CenterT(this, width, height, slope, lift);
                    float headH = height * ext.gapSize;
                    // The head is paint like the rest: it weathers with its frame and the wall comes back through it (pass 16; it had stayed crisp
                    // and lit like the UI while the horns round it wore away).
                    Material head = cachedHeadMat;
                    if (fade > 0f && head.mainTexture != null)
                    {
                        Texture2D eatenHead = WallPlane.Weathered(head.mainTexture, weatherStep, thingIDNumber);
                        if (eatenHead != null) head = MaterialPool.MatFrom(new MaterialRequest(eatenHead, head.shader, new Color(1f, 1f, 1f, 1f - 0.08f * fade)));
                    }
                    WallPlane.Print(layer, this, head, headH * 0.92f, headH, slide, slope, lift, false, through, 0f, tc + (ext.gapV - 0.5f) * height);
                }
                Graphic g = Graphic;
                if (g is Graphic_Random random)
                {
                    g = variant >= 0 ? random.SubGraphicAtIndex(variant) : random.SubGraphicFor(this);
                }
                if (g == null) return;
                Material mat = g.MatAt(Rot4.North, this);
                if (ext != null && ext.pigmented && !string.IsNullOrEmpty(g.path))
                {
                    mat = MaterialPool.MatFrom(g.path, g.Shader, Muddied(PigmentOf(pigment), mud));
                }
                else if (mud > 0f && !string.IsNullOrEmpty(g.path))
                {
                    mat = MaterialPool.MatFrom(g.path, g.Shader, Muddied(Color.white, mud));
                }
                // A gouge is the wall, and the wall doesn't run.
                float runs = RM_GraffitiStage.oldWeather || ext?.wallThrough == 0f ? 0f : RM_GraffitiKernel.CraftDrips(look);
                if (runs > 0f && mat.mainTexture != null)
                {
                    Texture2D run = WallPlane.Dripped(mat.mainTexture, runs, thingIDNumber);
                    if (run != null) mat = MaterialPool.MatFrom(new MaterialRequest(run, g.Shader, mat.color));
                }
                if (fade > 0f && mat.mainTexture != null)
                {
                    // Worn in patches, not thinned all over (WallPlane.Weathered): what's left is still paint.
                    // A pigment on a pale drawing chalks the way the drawing's own colours do in Weathered: paler in its hue, not thinner
                    // (pass 16; thinned, old paint over a wall read as a stain).
                    Color worn = Color.Lerp(mat.color, Color.white, WallPlane.BleachPerStep * (RM_GraffitiStage.oldWeather ? 1.7f : 1.2f) * weatherStep);
                    worn.a = mat.color.a * (1f - 0.08f * fade);
                    Texture2D eaten = WallPlane.Weathered(mat.mainTexture, weatherStep, thingIDNumber);
                    mat = eaten != null ? MaterialPool.MatFrom(new MaterialRequest(eaten, g.Shader, worn)) : MaterialPool.MatFrom(g.path, g.Shader, worn);
                }
                float smear = RM_GraffitiKernel.CraftSmear(look);
                if (smear > 0f && !RM_GraffitiStage.smearOver)
                {
                    // A clumsy hand's first go, off true and squashed, in thin paint UNDER the shape it then went over: the ghost of a hand that
                    // couldn't, around a shape that still reads. Live 2026-11-08: drawn over the mark with its own wall show-through, it washed a poor
                    // glyph into a green smudge on the day-19 wall, a mess rather than a message.
                    Color thin = mat.color;
                    thin.a *= RM_GraffitiStage.oldWeather ? RM_GraffitiKernel.SmearAlpha : RM_GraffitiKernel.SmearAlphaFull;
                    Material under = MaterialPool.MatFrom(new MaterialRequest((Texture2D)mat.mainTexture, mat.shader, thin) { renderQueue = mat.renderQueue - 1 });
                    WallPlane.Print(layer, this, under, width * (1f + 0.12f * smear), height * (1f - 0.18f * smear), slide + 0.09f * smear * width,
                        -slope, lift - 0.04f * smear, flip && cachedHeadMat == null, 0f, 0.0005f);
                }
                // A portrait can't flip with its frame: a mark about someone keeps their face the right way round.
                WallPlane.Print(layer, this, mat, width, height, slide, slope, lift, flip && cachedHeadMat == null, through, 0.001f);
                if (smear > 0f && RM_GraffitiStage.smearOver)
                {
                    WallPlane.Print(layer, this, mat, width * (1f + 0.12f * smear), height * (1f - 0.18f * smear), slide + 0.09f * smear * width,
                        -slope, lift - 0.04f * smear, flip && cachedHeadMat == null, Mathf.Clamp(through + 0.22f, 0.04f, 0.6f), 0.0015f);
                }
                if (!defaced && fade < 0.5f && !string.IsNullOrEmpty(g.path)) PrintSkill(layer, g, mat, look, width, height, slide, slope, lift, flip && cachedHeadMat == null);
                PrintSignature(layer, ext, WallPlane.PaintColor(mat), width, height, slide, slope, lift, through, mat.renderQueue + 2);
                PrintCrossOut(layer, width, height, slide, slope, lift);
                return;
            }
            if (cachedFrameMat != null)
            {
                WallPlane.Print(layer, this, cachedFrameMat, width, height, slide, slope, lift, flip, cachedIconMat == null ? through : 0f);
            }
            if (cachedIconMat != null)
            {
                // The icon's square in the wall's plane, centred in its frame. An icon may have text-like symmetry, so no flip.
                float iconH = height * 0.78f;
                WallPlane.Print(layer, this, cachedIconMat, iconH * 0.8f, iconH, slide, slope, lift, false, through, 0.001f, WallPlane.CenterT(this, width, height, slope, lift));
            }
            PrintSignature(layer, ext, WallPlane.PaintColor(cachedFrameMat ?? cachedIconMat), width, height, slide, slope, lift, through, (cachedIconMat ?? cachedFrameMat).renderQueue + 2);
            PrintCrossOut(layer, width, height, slide, slope, lift);
        }

        /// <summary>A skilled hand's piece stands off the wall: its block shadow under the paint, down and along, in the paint's own darkest
        /// shade; a master's carries shine glints on its letters' top edges. Nothing for normal work or worse.</summary>
        private void PrintSkill(SectionLayer layer, Graphic g, Material paint, int look, float width, float height, float slide, float slope, float lift, bool flip)
        {
            RM_GraffitiKernel.CraftDepth(look, out float drop, out int steps, out int glints);
            if (steps <= 0) return;
            Color tone = paint.color;
            Color dark = new Color(0.05f + tone.r * 0.16f, 0.045f + tone.g * 0.14f, 0.05f + tone.b * 0.16f, 0.88f * tone.a);
            // A queue under the paint's, so only the block's edge shows past the letters. An altitude bump alone doesn't decide it: live, the
            // block drew over the letters and a masterwork went to a dark mass.
            Material shadow = MaterialPool.MatFrom(new MaterialRequest((Texture2D)paint.mainTexture, g.Shader, dark) { renderQueue = paint.renderQueue - 1 });
            float tc = WallPlane.CenterT(this, width, height, slope, lift);
            for (int i = 1; i <= steps; i++)
            {
                float d = drop * i / steps;
                WallPlane.Print(layer, this, shadow, width, height, slide + d, slope, lift, flip, 0f, 0.0005f, tc - d * 1.4f);
            }
            if (glints <= 0) return;
            Texture tex = paint.mainTexture;
            float[] grid = WallPlane.AlphaGrid(tex, out int cols, out int rows);
            if (grid == null) return;
            Material shine = MaterialPool.MatFrom(new MaterialRequest(WallPlane.GlintTexture(), ShaderDatabase.Mote, new Color(1f, 1f, 1f, 0.95f)) { renderQueue = paint.renderQueue + 2 });
            foreach (float[] p in RM_GraffitiKernel.ShinePoints(grid, cols, rows, glints, thingIDNumber))
            {
                WallPlane.PointOn(this, width, height, slide, slope, lift, flip, p[0], p[1], out float s, out float t);
                float size = 0.2f + 0.05f * (look - RM_GraffitiKernel.Masterwork);
                WallPlane.Print(layer, this, shine, size, size, s, 0f, lift, false, 0f, 0.003f, t);
            }
        }

        private static readonly string[] SignatureDefs = { "RM_Graffiti_Tag_A", "RM_Graffiti_Tag_B", "RM_Graffiti_Tag_C" };

        /// <summary>The writer's own tag (RM_GraffitiKernel.Signed), in the hand their tags carry everywhere (PickLook) and in a colour that stands off
        /// both the wall and the shape it signs, along the shape's lower right, in a quick hand's slant: the symbol was cut once, the signature is theirs.
        /// Nobody's hand (a staged or very old mark), nothing.</summary>
        private void PrintSignature(SectionLayer layer, ModExtension_Graffiti ext, Color paint, float width, float height, float slide, float slope, float lift, float through, int queue)
        {
            if (RM_GraffitiStage.oldWeather || ext == null || defaced || Fade >= 0.75f) return;
            if (!RM_GraffitiKernel.Signed(ext.form, ext.hasSubject, !ext.requiresAnyMeme.NullOrEmpty())) return;
            int who = maker != null && maker.Faction == Faction.OfPlayer ? maker.thingIDNumber : (makerFaction?.loadID ?? -1);
            if (who < 0) return;
            ThingDef tagDef = DefDatabase<ThingDef>.GetNamedSilentFail(SignatureDefs[RM_GraffitiKernel.HandChoice(who, SignatureDefs.Length, 3)]);
            if (!(tagDef?.graphic is Graphic_Random tags) || tags.SubGraphicsCount == 0) return;
            Graphic hand = tags.SubGraphicAtIndex(RM_GraffitiKernel.HandChoice(who, tags.SubGraphicsCount, 1));
            Color wall = WallPlane.FaceColor(Position + new Rot4(wallSide).FacingCell, Map);
            int ink = RM_GraffitiKernel.ContrastingPigment(RM_GraffitiKernel.HandChoice(who, RM_GraffitiKernel.PigmentCount, 2), paint.r, paint.g, paint.b, wall.r, wall.g, wall.b);
            if (ink < 0) return;
            Material mat = MaterialPool.MatFrom(new MaterialRequest((Texture2D)hand.MatSingle.mainTexture, ShaderDatabase.Mote, PigmentOf(ink)) { renderQueue = queue });
            float tw = Mathf.Min(width * 0.64f, 0.85f), th = tw * 0.62f;
            float tc = WallPlane.CenterT(this, width, height, slope, lift) - height * 0.26f;
            WallPlane.Print(layer, this, mat, tw, th, slide + width * 0.5f - tw * 0.48f, 0.1f - slope * 0.5f, lift, false, through, 0.002f, tc);
        }

        private void PrintCrossOut(SectionLayer layer, float width, float height, float slide, float slope, float lift)
        {
            if (!defaced) return;
            Material strike = MaterialPool.MatFrom("Things/Filth/Art/RM_Graffiti_CrossOut/crossout_" + (thingIDNumber & 1), ShaderDatabase.Mote);
            WallPlane.Print(layer, this, strike, Mathf.Min(width * 1.05f, 3f), height, slide, slope, lift, (thingIDNumber & 2) != 0, 0f, 0.0015f, WallPlane.CenterT(this, width, height, slope, lift));
        }

        /// <summary>How much of the wall stays visible through paint: paper hides most of it, a gouge is the wall, spray and a dry brush let it through.</summary>
        private static float ThroughOf(ModExtension_Graffiti ext)
        {
            if (ext == null) return 0.24f;
            return ext.wallThrough >= 0f ? ext.wallThrough : (ext.form == GraffitiForm.Paste ? 0.18f : 0.24f);
        }

        /// <summary>A wall is gone: every mark painted on it goes too.</summary>
        internal static void Notify_WallGone(IntVec3 wall, Map map)
        {
            for (int i = 0; i < 4; i++)
            {
                Rot4 side = new Rot4(i);
                IntVec3 floor = wall - side.FacingCell;
                if (!floor.InBounds(map)) continue;
                foreach (Thing t in floor.GetThingList(map).ToArray())
                {
                    if (t is Filth_Mark m && m.wallSide == i && !m.Destroyed)
                    {
                        GraffitiSocial.Trace(m.def.defName.Replace("RM_Graffiti_", "") + "@" + m.Position + " went with its wall at " + wall);
                        m.SkipCleanNotice();
                        m.Destroy();
                    }
                }
            }
        }

        /// <summary>Marks whose drawing overlaps a width centred on `wall`, a wall cell: looked for along the wall's line, on this one face.
        /// The other side of a one-thick wall is another face and carries its own.</summary>
        internal static System.Collections.Generic.List<Filth_Mark> MarksOverlapping(IntVec3 wall, int side, float halfWidth, Map map, Filth_Mark except)
        {
            var found = new System.Collections.Generic.List<Filth_Mark>();
            Rot4 dir = new Rot4(side);
            IntVec3 along = dir.Rotated(RotationDirection.Clockwise).FacingCell;
            IntVec3 normal = dir.FacingCell;
            for (int k = -WallSearchCells; k <= WallSearchCells; k++)
            {
                IntVec3 onWall = wall + along * k;
                IntVec3 floor = onWall - normal;
                if (!floor.InBounds(map)) continue;
                foreach (Thing t in floor.GetThingList(map))
                {
                    if (!(t is Filth_Mark m) || m == except || m.wallSide != side) continue;
                    if (RM_GraffitiKernel.WallMarksOverlap(k, halfWidth, m.Width / 2f) && !found.Contains(m))
                    {
                        found.Add(m);
                    }
                }
            }
            return found;
        }

        private const int WallSearchCells = 4;

        /// <summary>The side of `cell` the wall stands on (RM_GraffitiKernel.WallSide), NoWall with none.</summary>
        internal static int ReadWallSide(IntVec3 cell, Map map)
        {
            if (map == null || !cell.IsValid)
            {
                return RM_GraffitiKernel.NoWall;
            }
            return RM_GraffitiKernel.WallSide(
                GraffitiJobUtility.IsFullWallAt(cell + IntVec3.North, map),
                GraffitiJobUtility.IsFullWallAt(cell + IntVec3.East, map),
                GraffitiJobUtility.IsFullWallAt(cell + IntVec3.South, map),
                GraffitiJobUtility.IsFullWallAt(cell + IntVec3.West, map));
        }

        /// <summary>Test probe (jawa/static_call; GRAFFITI_WALLFACE): every Filth_Mark on the current map ->
        /// "marks=N;onWall=N;sides=n,e,s,w;mismatch=N" where mismatch counts marks whose recorded side no longer has a wall.</summary>
        public static string ProbeWallFaces()
        {
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return "error=no current map";
            }
            int marks = 0, onWall = 0, mismatch = 0;
            int[] sides = new int[4];
            foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Filth))
            {
                if (!(t is Filth_Mark m))
                {
                    continue;
                }
                marks++;
                if (m.wallSide >= 0 && m.wallSide <= 3)
                {
                    onWall++;
                    sides[m.wallSide]++;
                    if (!GraffitiJobUtility.IsFullWallAt(m.Position + new Rot4(m.wallSide).FacingCell, map))
                    {
                        mismatch++;
                    }
                }
            }
            return "marks=" + marks + ";onWall=" + onWall + ";sides=" + sides[0] + "," + sides[1] + "," + sides[2] + "," + sides[3]
                + ";mismatch=" + mismatch;
        }
    }
}
