using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>One end of a span as this anchor stores it. Both ends store the same state; the lower thing id owns
    /// drawing and damage (AerialMath.Owns).</summary>
    public class SpanLink : IExposable
    {
        /// <summary>The partner THING (saved by reference); <see cref="other"/> is its anchor comp.</summary>
        public Thing otherThing;
        private CompAerialAnchor otherComp;
        public CompAerialAnchor other
        {
            get
            {
                if (otherComp == null || otherComp.parent != otherThing) otherComp = CompAerialAnchor.Of(otherThing);
                return otherComp;
            }
            set { otherComp = value; otherThing = value?.parent; }
        }
        public SpanState state = SpanState.Up;
        public float hp = SpanMaxHp;
        public int changedTick = -1;
        public const float SpanMaxHp = 30f;

        public void ExposeData()
        {
            Scribe_References.Look(ref otherThing, "other");
            Scribe_Values.Look(ref state, "state", SpanState.Up);
            Scribe_Values.Look(ref hp, "hp", SpanMaxHp);
        }
    }

    /// <summary>Cable lying on the floor at this anchor: a span whose far anchor died (toward its cell), or one half of
    /// a cut span (toward the cut point). Look only: it shocks nobody (owner 2026-10-02).</summary>
    public class FallenCord : IExposable
    {
        public IntVec3 toward;
        public float length;
        public int seed;
        /// <summary>thingIDNumber of the partner whose cut span this half belongs to; -1 = the partner is dead.</summary>
        public int cutPartner = -1;

        public void ExposeData()
        {
            Scribe_Values.Look(ref toward, "toward");
            Scribe_Values.Look(ref length, "length");
            Scribe_Values.Look(ref seed, "seed");
            Scribe_Values.Look(ref cutPartner, "cutPartner", -1);
        }
    }

    public class CompProperties_AerialAnchor : CompProperties
    {
        public CompProperties_AerialAnchor() => compClass = typeof(CompAerialAnchor);
    }

    /// <summary>
    /// A mast, lamp mast or wall bracket (design 2.3): a plain vanilla Building + power transmitter carrying this comp;
    /// its linked partners count as its cardinal neighbours while a power net is being built (AerialPowerPatch).
    /// Links are saved here (rmAerialLinks); every topology change re-seeds both ends' nets (the despawn gap, design
    /// 2.2). A COMP, not a Building subclass, on purpose: a save then names only our DEFS, never a C# class of ours,
    /// so loading it without the mod gives vanilla's missing-def errors and nothing worse (walk M9b).
    /// The thing-like members below (Position, thingIDNumber, Map ...) forward to the parent.
    /// </summary>
    [StaticConstructorOnStartup]
    public class CompAerialAnchor : ThingComp
    {
        public static CompAerialAnchor Of(Thing t) => t is ThingWithComps tw && IsAnchorDef(t.def) ? tw.GetComp<CompAerialAnchor>() : null;

        private static readonly Dictionary<ThingDef, bool> anchorDefs = new Dictionary<ThingDef, bool>();

        public static bool IsAnchorDef(ThingDef d)
        {
            if (d == null) return false;
            if (!anchorDefs.TryGetValue(d, out bool v)) anchorDefs[d] = v = d.HasComp(typeof(CompAerialAnchor));
            return v;
        }

        public IntVec3 Position => parent.Position;
        public int thingIDNumber => parent.thingIDNumber;
        public bool Spawned => parent.Spawned;
        public Map Map => parent.Map;
        public Faction Faction => parent.Faction;
        public string LabelCap => parent.LabelCap;
        public ThingDef def => parent.def;
        public CompPower PowerComp => (parent as Building)?.PowerComp;

        /// <summary>TEST ONLY (AerialProbe "skipreseed:"): skip the despawn re-seed so validation_aerial.py can show the
        /// despawn gap is real -- a negative control for the fix, never a setting.</summary>
        public static bool debugSkipReseed;

        public List<SpanLink> links = new List<SpanLink>();
        public List<FallenCord> fallen = new List<FallenCord>();

        private static readonly Texture2D IconLink = ContentFinder<Texture2D>.Get("UI/Commands/TryReconnect", false);
        private static readonly Texture2D IconUnlink = ContentFinder<Texture2D>.Get("UI/Designators/Cancel", false);

        public AerialAnchorExtension Ext => def.GetModExtension<AerialAnchorExtension>() ?? DefaultExt;
        private static readonly AerialAnchorExtension DefaultExt = new AerialAnchorExtension();

        public int MaxLinks => Ext.maxLinks;

        /// <summary>Partners whose span is UP and who stand on this map: what the power postfix appends.</summary>
        public IEnumerable<CompAerialAnchor> LivePartners
        {
            get
            {
                for (int i = 0; i < links.Count; i++)
                {
                    SpanLink l = links[i];
                    if (l.state == SpanState.Up && l.other != null && l.other.Spawned && l.other.Map == Map) yield return l.other;
                }
            }
        }

        public SpanLink LinkTo(CompAerialAnchor b) => links.FirstOrDefault(l => l.other == b);

        /// <summary>The insulator point the wire hangs from (ground-plane coordinates; z is the fake height).</summary>
        public Vector3 AttachPoint => AerialMaterials.BracketInsulator(this) is Vector2 bi ? BasePoint + new Vector3(bi.x, 0f, bi.y) : BasePoint + new Vector3(0f, 0f, Ext.attachZ);

        /// <summary>The anchor's foot. A wall-attached anchor (building.isAttachment, the bracket: owner review 2026-10-04 B7)
        /// is drawn ON the wall by its graphic's per-rotation draw offset, so its foot and insulator move with it.</summary>
        public Vector3 BasePoint
        {
            get
            {
                var b = new Vector3(Position.x + 0.5f, 0f, Position.z + 0.5f);
                if (parent.def.building != null && parent.def.building.isAttachment && parent.def.graphicData != null)
                {
                    Vector3 o = parent.def.graphicData.DrawOffsetForRot(parent.Rotation);
                    b.x += o.x; b.z += o.z;
                }
                return b;
            }
        }

        public static int FactionKey(Thing t) => t.Faction == null ? -1 : t.Faction.loadID;

        public AnchorInfo Info() => new AnchorInfo
        {
            Id = thingIDNumber, X = Position.x, Z = Position.z, Faction = FactionKey(parent), MaxLinks = MaxLinks,
            Roofed = Spawned && Map.roofGrid.Roofed(Position),
            Linked = links.Where(l => l.other != null).Select(l => l.other.thingIDNumber).ToList(),
        };

        // ------------------------------------------------------------------ lifecycle
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            Map map = parent.Map;
            RM_MapComponent_Aerial comp = map.GetComponent<RM_MapComponent_Aerial>();
            comp?.Register(this);
            if (!respawningAfterLoad && AerialSettings.enabled && AerialSettings.autoLink) comp?.QueueAutoLink(this);
        }

        /// <summary>Runs after CompPower.PostDeSpawn (the power comp is listed first in the def), so vanilla has already
        /// queued this transmitter's deregistration, which destroys the shared net.</summary>
        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            bool killed = mode == DestroyMode.KillFinalize || mode == DestroyMode.KillFinalizeLeavingsOnly;
            var spans = links.Where(l => l.other != null).Select(l => (l.other.thingIDNumber, l.state)).ToList();
            RemovalPlan plan = AerialMath.PlanRemoval(thingIDNumber, killed, spans);
            var partners = links.Where(l => l.other != null).Select(l => l.other).ToList();
            foreach (CompAerialAnchor p in partners)
            {
                SpanLink mine = LinkTo(p);
                p.links.RemoveAll(l => l.other == this);
                if (plan.Fallen.Any(f => f.Survivor == p.thingIDNumber) && p.Spawned)
                    p.fallen.Add(new FallenCord
                    {
                        toward = Position,
                        length = Vector3.Distance(p.BasePoint, BasePoint) * 1.05f,
                        seed = (int)AerialMath.Hash(p.thingIDNumber, thingIDNumber, 7),
                    });
                // a cut half lying at the survivor stays (it is the survivor's own cable now)
                foreach (FallenCord f in p.fallen) if (f.cutPartner == thingIDNumber) f.cutPartner = -1;
            }
            links.Clear();
            fallen.Clear();
            RM_MapComponent_Aerial comp = map?.GetComponent<RM_MapComponent_Aerial>();
            comp?.Deregister(this, map);
            // re-seed every former partner or its side stays net-less (design 2.2.3).
            foreach (CompAerialAnchor p in partners)
            {
                if (!plan.Reseed.Contains(p.thingIDNumber) || !p.Spawned) continue;
                if (!debugSkipReseed) Reseed(p);
                comp?.DirtyGround(p);
            }
            comp?.Notify_SpansChanged();
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Collections.Look(ref links, "rmAerialLinks", LookMode.Deep);
            Scribe_Collections.Look(ref fallen, "rmAerialFallen", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                links ??= new List<SpanLink>();
                fallen ??= new List<FallenCord>();
                links.RemoveAll(l => l == null || l.other == null);
            }
        }

        public static void Reseed(CompAerialAnchor a)
        {
            if (a == null || !a.Spawned || a.PowerComp == null) return;
            a.Map.powerNetManager.Notfiy_TransmitterTransmitsPowerNowChanged(a.PowerComp);
        }

        // ------------------------------------------------------------------ topology changes (all re-seed both ends)
        public static LinkVerdict Verdict(CompAerialAnchor a, Thing b)
        {
            AnchorInfo bi = Of(b) is CompAerialAnchor bb ? bb.Info() : new AnchorInfo { Id = b.thingIDNumber, X = b.Position.x, Z = b.Position.z, Faction = FactionKey(b), IsAnchor = false };
            return AerialMath.CanLink(a.Info(), bi, AerialSettings.Range);
        }

        public static LinkVerdict TryLink(CompAerialAnchor a, Thing target)
        {
            LinkVerdict v = Verdict(a, target);
            if (v != LinkVerdict.Ok) return v;
            CompAerialAnchor b = Of(target);
            int now = Find.TickManager.TicksGame;
            // a cable that fell toward this very anchor is the one being strung again
            a.fallen.RemoveAll(f => f.cutPartner == -1 && f.toward == b.Position);
            b.fallen.RemoveAll(f => f.cutPartner == -1 && f.toward == a.Position);
            a.links.Add(new SpanLink { other = b, changedTick = now });
            b.links.Add(new SpanLink { other = a, changedTick = now });
            Changed(a, b);
            return v;
        }

        public static bool Unlink(CompAerialAnchor a, CompAerialAnchor b)
        {
            int n = a.links.RemoveAll(l => l.other == b) + b.links.RemoveAll(l => l.other == a);
            a.fallen.RemoveAll(f => f.cutPartner == b.thingIDNumber);
            b.fallen.RemoveAll(f => f.cutPartner == a.thingIDNumber);
            if (n > 0) Changed(a, b);
            return n > 0;
        }

        /// <summary>Part a span. dropHalves: each half falls from its anchor toward the cut point (explosion); false:
        /// both ends are coiled at the anchor (a roof built over an anchor).</summary>
        public static bool Cut(CompAerialAnchor a, CompAerialAnchor b, float atT, bool dropHalves)
        {
            SpanLink la = a.LinkTo(b), lb = b.LinkTo(a);
            if (la == null || lb == null || la.state == SpanState.Cut) return false;
            la.state = lb.state = SpanState.Cut;
            la.changedTick = lb.changedTick = Find.TickManager.TicksGame;
            la.hp = lb.hp = 0f;
            if (dropHalves)
            {
                Vector3 cut = Vector3.Lerp(a.BasePoint, b.BasePoint, Mathf.Clamp01(atT));
                var cell = new IntVec3(Mathf.FloorToInt(cut.x), 0, Mathf.FloorToInt(cut.z));
                a.fallen.Add(new FallenCord { toward = cell, length = Vector3.Distance(a.BasePoint, cut) * 1.05f, seed = (int)AerialMath.Hash(a.thingIDNumber, b.thingIDNumber, 11), cutPartner = b.thingIDNumber });
                b.fallen.Add(new FallenCord { toward = cell, length = Vector3.Distance(b.BasePoint, cut) * 1.05f, seed = (int)AerialMath.Hash(b.thingIDNumber, a.thingIDNumber, 11), cutPartner = a.thingIDNumber });
            }
            Changed(a, b);
            return true;
        }

        public static bool Restring(CompAerialAnchor a, CompAerialAnchor b)
        {
            SpanLink la = a.LinkTo(b), lb = b.LinkTo(a);
            if (la == null || lb == null || la.state == SpanState.Up) return false;
            if (a.Map.roofGrid.Roofed(a.Position) || b.Map.roofGrid.Roofed(b.Position)) return false;
            la.state = lb.state = SpanState.Up;
            la.hp = lb.hp = SpanLink.SpanMaxHp;
            la.changedTick = lb.changedTick = Find.TickManager.TicksGame;
            a.fallen.RemoveAll(f => f.cutPartner == b.thingIDNumber);
            b.fallen.RemoveAll(f => f.cutPartner == a.thingIDNumber);
            Changed(a, b);
            return true;
        }

        private static void Changed(CompAerialAnchor a, CompAerialAnchor b)
        {
            foreach (int id in AerialMath.ReseedOnLinkChange(a.thingIDNumber, b.thingIDNumber))
                Reseed(id == a.thingIDNumber ? a : b);
            RM_MapComponent_Aerial comp = a.Map?.GetComponent<RM_MapComponent_Aerial>();
            if (comp == null) return;
            comp.DirtyGround(a);
            comp.DirtyGround(b);
            comp.Notify_SpansChanged();
        }

        // ------------------------------------------------------------------ UX (design 2.4)
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            if (Faction != Faction.OfPlayer) yield break;
            yield return new Command_Action
            {
                defaultLabel = "Link wire",
                defaultDesc = "String an overhead wire from this anchor to another of your masts or brackets within " +
                              AerialSettings.Range.ToString("0") + " cells. Linked anchors share one power grid. Wires may pass over roofed rooms; the anchors themselves must stand under open sky.",
                icon = IconLink,
                action = () => Find.Targeter.BeginTargeting(new TargetingParameters
                {
                    canTargetBuildings = true, canTargetPawns = false, canTargetItems = false, mapObjectTargetsMustBeAutoAttackable = false,
                    validator = t => Of(t.Thing) != null && Verdict(this, t.Thing) == LinkVerdict.Ok,
                }, t =>
                {
                    LinkVerdict v = t.Thing != null ? TryLink(this, t.Thing) : LinkVerdict.NotAnchor;
                    if (v != LinkVerdict.Ok) Messages.Message("Cannot link: " + VerdictText(v), parent, MessageTypeDefOf.RejectInput, false);
                    else SoundDefOf.Tick_High.PlayOneShotOnCamera();
                }),
                Disabled = links.Count >= MaxLinks,
                disabledReason = "All " + MaxLinks + " insulators are in use.",
            };
            if (links.Count > 0)
            {
                yield return new Command_Action
                {
                    defaultLabel = "Unlink wire",
                    defaultDesc = "Take down one wire (the cable is coiled, not dropped).",
                    icon = IconUnlink,
                    action = () => Find.WindowStack.Add(new FloatMenu(links.Where(l => l.other != null).Select(l =>
                    {
                        CompAerialAnchor o = l.other;
                        return new FloatMenuOption(o.parent.LabelShortCap + " (" + o.Position.x + ", " + o.Position.z + ")" + (l.state == SpanState.Cut ? " - cut" : ""),
                            () => Unlink(this, o));
                    }).ToList())),
                };
                yield return new Command_Action
                {
                    defaultLabel = "Unlink all",
                    defaultDesc = "Take down every wire on this anchor.",
                    icon = IconUnlink,
                    action = () => { foreach (CompAerialAnchor o in links.Select(l => l.other).Where(o => o != null).ToList()) Unlink(this, o); },
                };
            }
            if (links.Any(l => l.state == SpanState.Cut && l.other != null))
            {
                yield return new Command_Action
                {
                    defaultLabel = "Re-string cut wires",
                    defaultDesc = "Haul the fallen halves back up and splice them (both anchors must be under open sky).",
                    icon = IconLink,
                    action = () => { foreach (CompAerialAnchor o in links.Where(l => l.state == SpanState.Cut).Select(l => l.other).Where(o => o != null).ToList()) Restring(this, o); },
                };
            }
            if (Find.Selector.NumSelected > 1)
            {
                yield return new Command_Action
                {
                    defaultLabel = "Auto-link selected",
                    defaultDesc = "Link the selected anchors with the shortest set of wires that joins them all (within range, free insulators only).",
                    icon = IconLink,
                    action = AutoLinkSelected,
                };
            }
        }

        private static int autoLinkFrame = -1;

        /// <summary>Kruskal over the selection (AerialMath.MinimumSpanningLinks). A merged gizmo fires once per selected
        /// building, so it runs once per frame.</summary>
        private static void AutoLinkSelected()
        {
            if (autoLinkFrame == Time.frameCount) return;
            autoLinkFrame = Time.frameCount;
            List<CompAerialAnchor> sel = Find.Selector.SelectedObjects.OfType<Thing>().Select(Of).Where(b => b != null && b.Spawned).ToList();
            var byId = sel.ToDictionary(b => b.thingIDNumber);
            foreach ((int a, int b) in AerialMath.MinimumSpanningLinks(sel.Select(s => s.Info()).ToList(), AerialSettings.Range))
                TryLink(byId[a], byId[b].parent);
        }

        public static string VerdictText(LinkVerdict v)
        {
            switch (v)
            {
                case LinkVerdict.OutOfRange: return "too far (longest span " + AerialSettings.Range.ToString("0") + " cells).";
                case LinkVerdict.Foreign: return "that belongs to someone else. Linking would merge their grid with yours; use a power-tap clamp.";
                case LinkVerdict.NotAnchor: return "wires only run between masts and wall brackets.";
                case LinkVerdict.FullA: return "this anchor has no free insulator.";
                case LinkVerdict.FullB: return "that anchor has no free insulator.";
                case LinkVerdict.Roofed: return "an anchor under a roof cannot hold a wire.";
                case LinkVerdict.AlreadyLinked: return "already linked.";
                case LinkVerdict.Self: return "an anchor cannot link to itself.";
                default: return v.ToString();
            }
        }

        public override string CompInspectStringExtra()
        {
            string s = base.CompInspectStringExtra();
            int up = links.Count(l => l.state == SpanState.Up), cut = links.Count(l => l.state == SpanState.Cut);
            string mine = "Wires: " + up + "/" + MaxLinks + (cut > 0 ? ", " + cut + " cut" : "") + (fallen.Count > 0 ? ", " + fallen.Count + " lying on the ground" : "");
            return s.NullOrEmpty() ? mine : s + "\n" + mine;
        }

        public override void PostDrawExtraSelectionOverlays()
        {
            base.PostDrawExtraSelectionOverlays();
            float r = Mathf.Min(AerialSettings.Range, GenRadial.MaxRadialPatternRadius - 0.01f);
            GenDraw.DrawRadiusRing(Position, r);
        }
    }
}
