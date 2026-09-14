using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M6 build (greentide_kit_spec.md M6, "Three-feller
    // tree fall"). Generic RM_-tier tag, not Greentide-hardcoded — "build once,
    // pay three times" per the spec's own framing extends past the three
    // fellers to the tag itself: any biome with a Plant it wants to
    // participate in RM_TreeFallUtility.FellTree just carries this.
    //
    // A Plant ThingDef opts in by carrying this extension. RM_TreeFallUtility
    // falls back to Default (below) for an untagged Plant, so FellTree() never
    // throws for a tree with no extension — only the tuning changes.
    //
    //   <ThingDef ParentName="TreeBase">
    //     <defName>RUT_Placeholder_GreentideGiantTree</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_FellableTreeExtension">
    //         <isGiantClass>true</isGiantClass>
    //         <fellLength>10</fellLength>
    //         <fallDamageRange>70~120</fallDamageRange>
    //         <heartRadius>1</heartRadius>
    //         <hardwoodDropRange>2~4</hardwoodDropRange>
    //         <greenwoodStackRange>10~25</greenwoodStackRange>
    //         <greenwoodDropChancePerCell>0.6</greenwoodDropChancePerCell>
    //       </li>
    //     </modExtensions>
    //   </ThingDef>
    public class RM_FellableTreeExtension : DefModExtension
    {
        // INVENTED (kit spec M6: "giants also drop RUT_Hardwood at the heart
        // cells" — the ONLY place the spec distinguishes tree class at all).
        // Drives three things in RM_TreeFallUtility.FellTree: the fall-damage
        // tier, whether Hardwood drops at all, and (via fellLength) the
        // player-experience line's own number — "a giant comes down across
        // ten tiles."
        public bool isGiantClass = false;

        // INVENTED. Cells the swath covers, walked from the trunk outward in
        // the fall direction. Player-experience text gives the giant number
        // directly (ten); standard trees default much shorter.
        public int fellLength = 10;

        // INVENTED (spec: "damage 30-120 by tree class" — the range itself,
        // not a fixed number, so a per-def override is how "by tree class"
        // is expressed: standard trees default low in the range, a giant's
        // own XML overrides it high).
        public FloatRange fallDamageRange = new FloatRange(30f, 70f);

        // Cells from the trunk (inclusive of the trunk cell itself) eligible
        // to drop Hardwood — "heart cells" per the spec's own wording.
        // INVENTED.
        public int heartRadius = 1;

        // Only rolled when isGiantClass. INVENTED — 0~0 (i.e. no field
        // override) is the correct default for a non-giant def, so the
        // extension is still safe to attach to a standard tree that only
        // wants Greenwood.
        public IntRange hardwoodDropRange = new IntRange(0, 0);

        // What actually drops. Generic ThingDef fields (like
        // RM_LivingBoleBiomeExtension's own heartwoodThing/coreMarkerThing)
        // rather than a hardcoded RUT_Greenwood/RUT_Hardwood lookup — a
        // different biome's giant tree can name its own resource defs.
        // greenwoodDef along the swath, INVENTED drop odds/size; hardwoodDef
        // only ever rolled when isGiantClass.
        public ThingDef greenwoodDef;
        public ThingDef hardwoodDef;
        public IntRange greenwoodStackRange = new IntRange(5, 15);
        public float greenwoodDropChancePerCell = 0.5f;

        // Falls back to SoundDefOf.Roof_Collapse / a plain dust puff in
        // RM_TreeFallUtility when left unset — see that class's own header
        // for why a shared vanilla sound is the correct default rather than
        // a new SoundDef (no audio asset owed for the mechanism to compile
        // and be reachable).
        public SoundDef crashSound;
        public float dustPuffScale = 1.4f;

        public override System.Collections.Generic.IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (fellLength <= 0)
            {
                yield return "RM_FellableTreeExtension.fellLength must be > 0.";
            }

            if (fallDamageRange.min < 0f || fallDamageRange.max < fallDamageRange.min)
            {
                yield return "RM_FellableTreeExtension.fallDamageRange is invalid.";
            }

            if (greenwoodDef == null)
            {
                yield return "RM_FellableTreeExtension has no greenwoodDef — a felled tree would drop no wood at all.";
            }

            if (isGiantClass && hardwoodDef == null)
            {
                yield return "RM_FellableTreeExtension.isGiantClass is set but hardwoodDef is null.";
            }
        }
    }
}
