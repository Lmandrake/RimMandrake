using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>
    /// One drawn picture of a huge plant (a Graphic_Random sub-texture, or the single texture), measured from the
    /// art by measure_huge_plant_masks.py. Never hand-written: rerun the tool.
    /// </summary>
    public class HugePlantVariant
    {
        /// <summary>The texture's file name without extension; matched against the drawn sub-graphic's path.</summary>
        public string texture;

        /// <summary>Visible-pixel box in quad coordinates: u left->right, v bottom->top, both 0..1, unflipped.</summary>
        public Vector2 opaqueMin = Vector2.zero;
        public Vector2 opaqueMax = Vector2.one;

        /// <summary>Ground-contact cells (dx, dz) relative to the root cell, at full growth (measuredSize), unflipped.</summary>
        public List<IntVec2> contact = new List<IntVec2>();

        [Unsaved] private HugeMask mask;

        /// <summary>This variant as the kernel's mask. wholeQuad: the picture box is the full quad (an unmeasured
        /// picture, whose extent is only known to be the quad).</summary>
        public HugeMask Mask(float measuredSize, bool wholeQuad = false)
        {
            if (mask != null && !wholeQuad) return mask;
            HugeMask m = wholeQuad
                ? new HugeMask { U0 = 0f, V0 = 0f, U1 = 1f, V1 = 1f, MeasuredSize = measuredSize }
                : new HugeMask { U0 = opaqueMin.x, V0 = opaqueMin.y, U1 = opaqueMax.x, V1 = opaqueMax.y, MeasuredSize = measuredSize };
            for (int i = 0; i < contact.Count; i++) m.Contact.Add(RM_HugeFootprintKernel.Key(contact[i].x, contact[i].z));
            if (!wholeQuad) mask = m;
            return m;
        }
    }

    /// <summary>
    /// Opt-in for a huge PLANT. Selection wraps the whole drawn picture; pawns are blocked on the cells where the
    /// art touches the ground (per variant, measured from the art), scaled with growth. The root cell itself is
    /// never blocked: an impassable edifice there would wipe the plant (GenSpawn.SpawningWipes, BlocksPlanting).
    /// An extension with no variants (HugeThingsApi.OptInPlant's default) still gets the whole-picture
    /// selection and blocks nothing.
    /// </summary>
    public class RM_HugePlantExtension : DefModExtension
    {
        /// <summary>drawSize.x * visualMax the contact cells were measured at (the full-growth quad side).</summary>
        public float measuredSize = 0f;

        /// <summary>A3.12: the largest drawn side (drawSize.x x visual max) a giant may have before blocking is refused.</summary>
        public const float MaxDrawExtent = 200f;

        public List<HugePlantVariant> variants = new List<HugePlantVariant>();

        /// <summary>Below this growth the plant blocks nothing (a young fungus is not yet a wall).</summary>
        public float minGrowthToBlock = 0.25f;

        /// <summary>Set at startup by HugeThingsApi.ValidateRenderer: false = selection only, no ground footprint.</summary>
        [Unsaved] public bool blockingSupported = true;

        /// <summary>Set at startup by HugeThingsApi.ValidateRenderer (owner ruling 2026-10-07 21:08): every measured picture
        /// touches the ground only in the plant's own cell, so the plant def itself was made Impassable.</summary>
        [Unsaved] public bool rootImpassable;

        [Unsaved] private HugePlantVariant union;
        [Unsaved] private HugeMask unionMask;

        /// <summary>The kernel mask for the picture drawn: the measured variant, or the union over the whole quad.</summary>
        public HugeMask MaskFor(HugePlantVariant v, bool measured)
        {
            if (measured) return v.Mask(measuredSize);
            return unionMask ?? (unionMask = Union.Mask(measuredSize, wholeQuad: true));
        }

        public HugePlantVariant Find(string texture)
        {
            if (texture == null) return null;
            for (int i = 0; i < variants.Count; i++)
            {
                if (variants[i] != null && variants[i].texture == texture) return variants[i];
            }
            return null;
        }

        /// <summary>For a picture the tool never measured (an immature or leafless graphic): every variant's
        /// contact cells together, and the full quad as the picture.</summary>
        public HugePlantVariant Union
        {
            get
            {
                if (union != null) return union;
                HashSet<IntVec2> all = new HashSet<IntVec2>();
                for (int i = 0; i < variants.Count; i++) if (variants[i]?.contact != null) all.UnionWith(variants[i].contact);
                union = new HugePlantVariant { texture = null, contact = new List<IntVec2>(all) };
                return union;
            }
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (variants.Count > 0 && !(measuredSize > 0f && measuredSize < 200f)) yield return "RM_HugePlantExtension measuredSize " + measuredSize + " is not in (0, 200)";
            if (!(minGrowthToBlock >= 0f && minGrowthToBlock <= 1f)) yield return "RM_HugePlantExtension minGrowthToBlock " + minGrowthToBlock + " is not in [0, 1]";
            HashSet<string> names = new HashSet<string>();
            for (int i = 0; i < variants.Count; i++)
            {
                // PLANT_FOOTPRINT_HARDENING_1 (A3.12): a null <li> variant, and contact cells outside the measured frame
                // (dx within +-measuredSize/2 of the root column, dz in [0, measuredSize)), are data errors.
                if (variants[i] == null) { yield return "RM_HugePlantExtension variant " + i + " is null (an empty <li>)"; continue; }
                if (variants[i].contact == null) { yield return "RM_HugePlantExtension variant " + i + " has a null contact list"; continue; }
                float half = measuredSize / 2f + 1f;
                foreach (IntVec2 c in variants[i].contact)
                {
                    if (c.x < -half || c.x > half || c.z < 0 || c.z > measuredSize)
                    {
                        yield return "RM_HugePlantExtension variant " + variants[i].texture + " contact cell " + c + " is outside its measured frame (size " + measuredSize + ")";
                        break;
                    }
                }
                if (variants[i].texture.NullOrEmpty()) yield return "RM_HugePlantExtension variant " + i + " has no texture";
                else if (!names.Add(variants[i].texture)) yield return "RM_HugePlantExtension variant " + variants[i].texture + " is listed twice";
                Vector2 mn = variants[i].opaqueMin, mx = variants[i].opaqueMax;
                if (!(mn.x >= 0f && mn.y >= 0f && mx.x <= 1f && mx.y <= 1f && mn.x < mx.x && mn.y < mx.y))
                    yield return "RM_HugePlantExtension variant " + variants[i].texture + " opaque box " + mn + ".." + mx + " is not inside 0..1";
                if (variants[i].contact.Contains(IntVec2.Zero)) yield return "RM_HugePlantExtension variant " + variants[i].texture + " blocks the root cell";
            }
        }
    }

    /// <summary>
    /// Opt-in for a huge PAWN race: a selection hitbox of (drawn body size x hitboxFraction) cells, centred
    /// on the pawn, never smaller than its footprint (Large Pawns' square when present).
    /// </summary>
    public class RM_HugePawnExtension : DefModExtension
    {
        /// <summary>Share of the current life stage's drawSize that counts as body (sprites carry margin).</summary>
        public float hitboxFraction = 0.6f;
    }
}
