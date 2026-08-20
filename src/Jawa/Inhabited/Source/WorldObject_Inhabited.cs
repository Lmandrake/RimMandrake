using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace Inhabited
{
    /// <summary>
    /// A place on the planet that somebody lives in, and the people themselves.
    ///
    /// The roster is a ThingOwner&lt;Pawn&gt; holding ACTUAL Pawn objects, never
    /// records. Names, skills, relationships, scars and memories therefore survive
    /// map destruction with no serialisation of ours, and "sell a pawn and they
    /// stay there, remembering that you sold them" falls out of the container
    /// choice rather than needing a feature.
    ///
    /// THE WORLD REMEMBERS BY CONSTRUCTION. Nobody writes "12 souls, 3 dead"
    /// anywhere. The roster simply IS the survivors, and the dead are not recorded
    /// at all -- no memorial, no ledger, no counter. The absence is the memory.
    ///
    /// TWO PLACES THIS DIVERGES FROM Caravan, WHICH IT IS OTHERWISE MODELLED ON,
    /// AND BOTH DIVERGENCES ARE LOAD-BEARING:
    ///
    /// 1. LookMode.Deep, not Caravan's LookMode.Reference. Caravan can use
    ///    Reference because its pawns are registered with WorldPawns, which
    ///    deep-saves them -- and WorldPawnGC then protects them by an explicit
    ///    `p.IsCaravanMember()` test inside GetCriticalPawnReason. A custom holder
    ///    matches none of that method's tests, so every resident would return null
    ///    and the collector would discard the whole cast between visits.
    ///    Deep-saving here means they are not world pawns at all and the collector
    ///    never sees them.
    ///
    /// 2. ShouldTickContents is false. WorldObject.DoTick walks its child holders
    ///    and calls ThingOwner.DoTick on each, skipping only owners that are a Map
    ///    or a Caravan -- a hardcoded type test we cannot join. Left alone an
    ///    off-map roster would tick: needs would fall and a cast would starve in a
    ///    box while the player was elsewhere. IThingHolderTickable is the
    ///    supported opt-out, and it is what makes "frozen until visited" true
    ///    rather than merely intended.
    /// </summary>
    public class WorldObject_Inhabited : WorldObject, IThingHolder, IThingHolderTickable
    {
        /// <summary>What the place is.</summary>
        public InhabitedPlaceDef placeDef;

        /// <summary>Who lives in it. Falls back to the place's default cast.</summary>
        public InhabitedCastDef castDef;

        /// <summary>The people. Real pawns, held off-map, frozen.</summary>
        public ThingOwner<Pawn> roster;

        /// <summary>Trade goods AND the larder. Visible, stealable, destroyable.</summary>
        public InhabitedStock stock;

        /// <summary>What the world map reports.</summary>
        public InhabitedState state = InhabitedState.Inhabited;

        /// <summary>
        /// True once the cast has been rolled. A second visit must not re-roll a
        /// place merely because everyone in it is dead -- an emptied place is
        /// abandoned, not restocked.
        /// </summary>
        public bool castInstantiated;

        private string nameInt;

        public WorldObject_Inhabited()
        {
            roster = new ThingOwner<Pawn>(this, oneStackOnly: false, LookMode.Deep);
            stock = new InhabitedStock(this);
        }

        public string Name
        {
            get => nameInt;
            set => nameInt = value;
        }

        public override string Label => nameInt ?? base.Label;

        /// <summary>Frozen until visited. See the class comment, divergence 2.</summary>
        public bool ShouldTickContents => false;

        /// <summary>How many are alive in the roster right now.</summary>
        public int SoulCount => roster?.InnerListForReading.Count(p => p != null && !p.Dead) ?? 0;

        /// <summary>Who lives here, resolved. The world object wins over the place.</summary>
        public InhabitedCastDef Cast => castDef ?? placeDef?.defaultCast;

        /// <summary>True if anyone in the cast deals.</summary>
        public bool HasTrader => Cast?.roles != null && Cast.roles.Any(r => r != null && r.trades);

        public ThingOwner GetDirectlyHeldThings()
        {
            return roster;
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
            if (stock != null)
            {
                outChildren.Add(stock);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref placeDef, "placeDef");
            Scribe_Defs.Look(ref castDef, "castDef");
            Scribe_Deep.Look(ref roster, "roster", this);
            Scribe_Deep.Look(ref stock, "stock", this);
            Scribe_Values.Look(ref state, "state", InhabitedState.Inhabited);
            Scribe_Values.Look(ref castInstantiated, "castInstantiated", defaultValue: false);
            Scribe_Values.Look(ref nameInt, "name");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (roster == null)
                {
                    roster = new ThingOwner<Pawn>(this, oneStackOnly: false, LookMode.Deep);
                }
                if (stock == null)
                {
                    stock = new InhabitedStock(this);
                }
            }
        }

        // ------------------------------------------------------------------
        // Instantiation. Runs ONCE, at the first map generation on this tile.
        // ------------------------------------------------------------------

        /// <summary>
        /// Roll the cast, drawing from the displaced pool BEFORE generating
        /// anybody new. That single ordering rule is the whole recurring-character
        /// effect: the six people at a trade post may be the refinery crew the
        /// player burned out two months ago, and RimWorld's own opinion system
        /// already knows what happened between them.
        ///
        /// This is not a background process. It runs at cast INSTANTIATION -- when
        /// a map generates -- which is why it does not violate "frozen until
        /// visited".
        /// </summary>
        public void InstantiateCast()
        {
            castInstantiated = true;

            InhabitedCastDef cast = Cast;
            if (cast == null || cast.roles.NullOrEmpty())
            {
                return;
            }

            List<PawnKindDef> wanted = new List<PawnKindDef>();
            for (int i = 0; i < cast.roles.Count; i++)
            {
                InhabitedRole role = cast.roles[i];
                if (role?.kind == null)
                {
                    continue;
                }
                int n = role.count.RandomInRange;
                for (int j = 0; j < n; j++)
                {
                    wanted.Add(role.kind);
                }
            }
            if (wanted.Count == 0)
            {
                return;
            }

            // Trim from the BACK, so leaders and traders -- written first -- keep
            // their places when a roll overshoots the archetype's size.
            int size = cast.castSize.RandomInRange;
            if (size > 0 && wanted.Count > size)
            {
                wanted.RemoveRange(size, wanted.Count - size);
            }

            int fromPool = 0;
            DisplacedPool pool = DisplacedPool.Current;
            if (pool != null && Faction != null)
            {
                List<Pawn> drawn = pool.Draw(Faction, wanted.Count);
                for (int i = 0; i < drawn.Count; i++)
                {
                    if (roster.TryAdd(drawn[i], canMergeWithExistingStacks: false))
                    {
                        fromPool++;
                    }
                }
            }

            for (int i = fromPool; i < wanted.Count; i++)
            {
                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                    wanted[i],
                    Faction,
                    PawnGenerationContext.NonPlayer,
                    Tile,
                    forceGenerateNewPawn: true,
                    allowDead: false,
                    allowDowned: false,
                    canGeneratePawnRelations: true,
                    mustBeCapableOfViolence: false,
                    colonistRelationChanceFactor: 1f,
                    forceAddFreeWarmLayerIfNeeded: false,
                    allowGay: true,
                    allowPregnant: false,
                    allowFood: true,
                    allowAddictions: true,
                    inhabitant: true));
                if (p == null)
                {
                    continue;
                }
                if (!roster.TryAdd(p, canMergeWithExistingStacks: false))
                {
                    p.Destroy();
                }
            }

            if (placeDef != null && stock != null)
            {
                stock.Fill(placeDef.larder);
                stock.Fill(placeDef.stock);
            }
        }

        // ------------------------------------------------------------------
        // The world map is the census.
        // ------------------------------------------------------------------

        public override string GetInspectString()
        {
            StringBuilder sb = new StringBuilder();
            string baseStr = base.GetInspectString();
            if (!baseStr.NullOrEmpty())
            {
                sb.AppendLine(baseStr);
            }

            List<string> parts = new List<string>();
            switch (state)
            {
                case InhabitedState.Abandoned:
                    parts.Add("InhabitedFled".Translate(SoulCount));
                    parts.Add("InhabitedStockSpoiling".Translate());
                    break;
                case InhabitedState.Looted:
                    parts.Add("InhabitedLooted".Translate());
                    break;
                case InhabitedState.Squatted:
                    parts.Add("InhabitedSquatted".Translate());
                    parts.Add("InhabitedSouls".Translate(SoulCount));
                    break;
                default:
                    parts.Add("InhabitedSouls".Translate(SoulCount));
                    if (!placeDef?.stockLabel.NullOrEmpty() ?? false)
                    {
                        parts.Add(placeDef.stockLabel);
                    }
                    if (HasTrader)
                    {
                        parts.Add("InhabitedWillTrade".Translate());
                    }
                    break;
            }
            sb.Append(string.Join(" . ", parts.ToArray()));
            return sb.ToString().TrimEndNewlines();
        }

        public override void Destroy()
        {
            // A place going away does not kill the people in it. Anyone still on
            // the roster becomes placeless and can turn up somewhere else.
            DisplacedPool pool = DisplacedPool.Current;
            if (pool != null && roster != null && roster.Count > 0 && Faction != null)
            {
                List<Pawn> left = roster.InnerListForReading.ToList();
                for (int i = 0; i < left.Count; i++)
                {
                    Pawn p = left[i];
                    if (p == null || p.Dead)
                    {
                        continue;
                    }
                    if (roster.Remove(p))
                    {
                        pool.Absorb(p, Faction, DisplacedReason.Fled, LabelCap);
                    }
                }
            }
            base.Destroy();
        }
    }
}
