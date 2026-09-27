using System.Collections.Generic;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // GREYSEA_BRINE_ELDERS_1 — the persisted PER-TILE novelty seen-set.
    // "This is the whole economy" (the prior FOUNDRY note, verbatim).
    //
    // Owner ruling, verbatim (2026-09-26): "ONLY grey sea, but there's one
    // per grey sea tile" + "an Elder values a novelty ONCE, so a specimen
    // already traded to one tile's Elder is still novel to the next tile's
    // … the Grey's ~429 tiles [are] a distributed market."
    //
    // ⇒ The seen-set is keyed by WORLD TILE ID, never by Map. A Grey Sea
    // floor is a POCKET map (PocketMapParent) that this project's own
    // convention culls when nothing keeps it home (see the
    // "generated-map-culled-unless-home" lesson) — so persisting state on
    // the pocket Map or on the RM_BrineElder Thing itself would silently
    // lose the whole economy the moment a player leaves and the map is
    // discarded. A GameComponent survives independently of any Map, exactly
    // like the ship/gravship state this campaign already treats as the
    // only thing that "carries" between dives (world_remake lesson).
    //
    // 🔴 "One example of each" (the singular RM_ treasures) is a SEPARATE,
    // PER-WORLD (not per-tile) flag, per the sheet's own words: "One example
    // of each is a per-world flag." Tracked here too, in its own set, keyed
    // by defName so a future Utinni-patch-added canon treasure (lightsaber,
    // navcore, droid brain — owed to that layer per Q11a, NOT built here)
    // slots into the same mechanism with no code change.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GameComponent_BrineElders : GameComponent
    {
        private List<RM_ElderTileRecord> tileRecords = new List<RM_ElderTileRecord>();
        private List<string> grantedUniqueTreasureDefNames = new List<string>();

        public RM_GameComponent_BrineElders(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref tileRecords, "elderTileRecords", LookMode.Deep);
            Scribe_Collections.Look(ref grantedUniqueTreasureDefNames, "elderGrantedUniqueTreasures", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (tileRecords == null)
                {
                    tileRecords = new List<RM_ElderTileRecord>();
                }
                if (grantedUniqueTreasureDefNames == null)
                {
                    grantedUniqueTreasureDefNames = new List<string>();
                }
            }
        }

        private RM_ElderTileRecord RecordFor(int tile, bool createIfMissing)
        {
            for (int i = 0; i < tileRecords.Count; i++)
            {
                if (tileRecords[i].tile == tile)
                {
                    return tileRecords[i];
                }
            }
            if (!createIfMissing)
            {
                return null;
            }
            RM_ElderTileRecord rec = new RM_ElderTileRecord { tile = tile, seenKeys = new List<string>() };
            tileRecords.Add(rec);
            return rec;
        }

        /// <summary>Has THIS tile's Elder already been shown this novelty
        /// key? False = novel, "worth a great deal"; true = already seen,
        /// "nearly worthless".</summary>
        public bool HasSeen(int tile, string noveltyKey)
        {
            RM_ElderTileRecord rec = RecordFor(tile, createIfMissing: false);
            return rec != null && rec.seenKeys.Contains(noveltyKey);
        }

        public void MarkSeen(int tile, string noveltyKey)
        {
            RM_ElderTileRecord rec = RecordFor(tile, createIfMissing: true);
            if (!rec.seenKeys.Contains(noveltyKey))
            {
                rec.seenKeys.Add(noveltyKey);
            }
        }

        public bool IsUniqueTreasureGranted(string defName)
        {
            return grantedUniqueTreasureDefNames.Contains(defName);
        }

        /// <summary>Atomically claims a still-ungranted unique treasure for
        /// this save. Returns false if it was already given out by any
        /// Elder on any tile — "typically only one example of each" made
        /// literal.</summary>
        public bool TryClaimUniqueTreasure(string defName)
        {
            if (grantedUniqueTreasureDefNames.Contains(defName))
            {
                return false;
            }
            grantedUniqueTreasureDefNames.Add(defName);
            return true;
        }
    }

    public class RM_ElderTileRecord : IExposable
    {
        public int tile;
        public List<string> seenKeys = new List<string>();

        public void ExposeData()
        {
            Scribe_Values.Look(ref tile, "tile", -1);
            Scribe_Collections.Look(ref seenKeys, "seenKeys", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && seenKeys == null)
            {
                seenKeys = new List<string>();
            }
        }
    }
}
