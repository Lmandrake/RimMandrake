using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Webwork
{
    /// <summary>
    /// WEBWORK_DEAD_GIANT_BUILD_1. Deterministic reads/triggers for jawa/static_call on the CURRENT map (a quicktest map
    /// is fine). Each sets the settings it needs for the call and restores them. The world/planet half of the first
    /// criterion is a separate world read; nothing here touches Find.WorldGrid.
    /// </summary>
    public static class RM_UrravethProof
    {
        private static Map Map => Find.CurrentMap;
        private static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

        private static List<RM_Building_UrravethPiece> Pieces(Map map) => RM_Urraveth.PiecesOn(map).ToList();

        /// <summary>args "chance" (default 1). Rolls the site gate at that chance, places the site if it passes.
        /// "SITE rolled B | placed N | pieces A->B | layoutRows R | pieceDefs D | allWrapped B | <def>=n ..."</summary>
        public static string ProofSite(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            float chance = float.TryParse((args ?? "1").Trim(), NumberStyles.Float, Inv, out float c) ? c : 1f;
            float was = RM_WebworkSettings.urravethSiteChance;
            try
            {
                RM_WebworkSettings.urravethSiteChance = chance;
                int before = Pieces(map).Count;
                bool rolled = RM_GenStep_UrravethRemains.RollSite();
                int placed = rolled ? new RM_GenStep_UrravethRemains().PlaceSite(map) : 0;
                List<RM_Building_UrravethPiece> after = Pieces(map);
                string perDef = string.Join(" ", RM_Urraveth.PieceDefs.Select(d => d.defName + "=" + after.Count(p => p.def == d)));
                return "SITE rolled " + rolled + " | placed " + placed + " | pieces " + before + "->" + after.Count
                    + " | layoutRows " + RM_GenStep_UrravethRemains.Layout.Length + " | pieceDefs " + RM_Urraveth.PieceDefs.Count
                    + " | allWrapped " + after.All(p => p.wrapped) + " | " + perDef;
            }
            finally
            {
                RM_WebworkSettings.urravethSiteChance = was;
            }
        }

        /// <summary>args a piece defName (first still-wrapped one of it is read), "all" (every wrapped piece) or "final"
        /// (open the last wrapping on the skull). "READ <what> | wrapped(def) B | chapters [..] | complete B |
        /// outlineCells N | thrixweaveNear N"</summary>
        public static string ProofRead(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            string a = (args ?? "").Trim();
            RM_MapComponent_UrravethReading r = map.GetComponent<RM_MapComponent_UrravethReading>();
            if (r == null) return "REFUSED: no RM_MapComponent_UrravethReading";
            List<RM_Building_UrravethPiece> pieces = Pieces(map);
            if (pieces.Count == 0) return "REFUSED: no urraveth pieces on this map (ProofSite first)";
            string what;
            RM_Building_UrravethPiece focus;
            if (a == "all")
            {
                foreach (RM_Building_UrravethPiece p in pieces.Where(p => p.wrapped)) p.FinishExamine(null);
                what = "all";
                focus = pieces.FirstOrDefault(p => p.Ext.isSkull);
            }
            else if (a == "final")
            {
                focus = pieces.FirstOrDefault(p => p.Ext.isSkull);
                if (focus == null) return "REFUSED: no skull";
                what = focus.FinishExamine(null);
            }
            else
            {
                focus = pieces.FirstOrDefault(p => p.def.defName == a && p.wrapped);
                if (focus == null) return "REFUSED: no wrapped " + a;
                what = focus.FinishExamine(null);
            }
            ThingDef weave = RM_Urraveth.Def("Hyperweave");
            int near = 0;
            if (focus != null && weave != null)
            {
                near = map.listerThings.ThingsOfDef(weave).Where(t => (t.Position - focus.Position).LengthHorizontal <= 6f).Sum(t => t.stackCount);
            }
            return "READ " + what + " | wrapped(" + (focus?.def.defName ?? "-") + ") " + (focus?.wrapped.ToString() ?? "-")
                + " | chapters [" + string.Join(",", r.Chapters) + "] | complete " + r.complete
                + " | outlineCells " + r.outlineCells + " | thrixweaveNear " + near
                + " | perPieceSetting " + RM_WebworkSettings.urravethThrixweavePerPiece;
        }

        /// <summary>args "pawns|mode" with mode clear | leave | idle. Picks the rib section that holds up another piece,
        /// spawns N player pawns in its footprint and evaluates load. clear: removes them before the window ends.
        /// leave: runs the whole window. idle: no pawns, 240 rare ticks (60,000 ticks).</summary>
        public static string ProofLoad(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            string[] a = (args ?? "").Split('|');
            int n = a.Length > 0 && int.TryParse(a[0].Trim(), out int k) ? k : 3;
            string mode = a.Length > 1 ? a[1].Trim() : "leave";
            List<RM_Building_UrravethPiece> pieces = Pieces(map);
            RM_Building_UrravethPiece rib = pieces.FirstOrDefault(p => p.def.defName == "RM_Urraveth_RibSection" && p.Supported().Any())
                                         ?? pieces.FirstOrDefault(p => p.def.defName == "RM_Urraveth_RibSection");
            if (rib == null) return "REFUSED: no rib section (ProofSite first)";
            if (mode == "idle")
            {
                bool ever = false;
                for (int i = 0; i < 240; i++)
                {
                    rib.StepLoad(250);
                    ever |= rib.Creaking;
                }
                return "IDLE load " + rib.CurrentLoad().ToString("0.00", Inv) + " | everCreaking " + ever + " | spawned " + rib.Spawned;
            }
            List<IntVec3> cells = rib.OccupiedRect().Cells.Where(c => c.Standable(map)).ToList();
            if (cells.Count == 0) return "REFUSED: rib footprint is not standable";
            List<Pawn> pawns = new List<Pawn>();
            for (int i = 0; i < n; i++)
            {
                Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
                GenSpawn.Spawn(p, cells[i % cells.Count], map);
                p.jobs?.StopAll();
                pawns.Add(p);
            }
            RM_Building_UrravethPiece neighbour = rib.Supported().FirstOrDefault();
            float load = rib.CurrentLoad();
            rib.StepLoad(250);
            bool creaking = rib.Creaking;
            int ticksLeft = rib.creakTicksLeft;
            int window = rib.WindowTicks;
            string head = "LOAD pawns " + n + " | load " + load.ToString("0.00", Inv) + " | capacity "
                + rib.Ext.loadCapacity.ToString("0.00", Inv) + " | creaking " + creaking + " | ticksLeft " + ticksLeft + " | window " + window;
            if (mode == "clear")
            {
                foreach (Pawn p in pawns) if (p.Spawned) p.DeSpawn();
                rib.StepLoad(250);
                bool hurt = pawns.Any(p => p.health.hediffSet.hediffs.Any(h => h is Hediff_Injury));
                foreach (Pawn p in pawns) p.Destroy();
                return head + " | CLEAR creaking " + rib.Creaking + " | ribSpawned " + rib.Spawned + " | anyPawnHurt " + hurt;
            }
            IntVec3 at = rib.Position;
            CellRect footprint = rib.OccupiedRect();
            int guard = 0;
            while (rib.Spawned && guard++ < 10000)
            {
                foreach (Pawn p in pawns.Where(p => p.Spawned)) p.jobs?.StopAll();
                rib.StepLoad(250);
            }
            ThingDef rubble = RM_Urraveth.Def(rib.Ext?.rubbleFilth ?? "Filth_RubbleRock");
            int rubbleCells = rubble == null ? -1 : footprint.Cells.Count(c => c.GetThingList(map).Any(t => t.def == rubble));
            bool damaged = pawns.Any(p => p.Dead || p.health.hediffSet.hediffs.Any(h => h is Hediff_Injury));
            string res = head + " | LEAVE ribGone " + !rib.Spawned + " | rubbleCells " + rubbleCells + " | pawnDamaged " + damaged
                + " | neighbour " + (neighbour?.def.defName ?? "none") + " creaking " + (neighbour != null && neighbour.Creaking);
            foreach (Pawn p in pawns) if (!p.Destroyed) p.Destroy();
            return res;
        }
    }
}
