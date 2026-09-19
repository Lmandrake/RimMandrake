using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1 (owner's own words, Grabber: "Give it great
    // strength to Hold someone with its pincer and slowly crush them each
    // round"). Attach to the GRABBER's own race. The hold itself is the
    // RM_Grappled hediff on the victim (delivered by the pincer tool's
    // DamageDef, see RM_Grapple_DamageDefs.xml); this comp is the crushing
    // half and the rescue half:
    //
    //   - every crushIntervalTicks, while the grabber is alive, not downed,
    //     not fleeing and still adjacent, every pawn it holds takes
    //     crushDamage of crushDamageDef to the torso (the race body's
    //     corePart) — real injuries, so bruising, pain and death come from
    //     vanilla's own injury rules, not an invisible gauge;
    //   - a melee hit on the grabber from a THIRD pawn (not the grabber, not
    //     one of its own victims) has breakHoldChanceOnHit to break every
    //     hold it currently has — "break the hold by hurting the grabber".
    //
    //   <comps>
    //     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_Grappler" />
    //   </comps>
    public class RM_CompProperties_Grappler : CompProperties
    {
        /// <summary>Ticks between crush rounds. INVENTED: 120 (2 s) — the
        /// brief's default; frequent enough to read as a continuous squeeze.</summary>
        public int crushIntervalTicks = 120;

        /// <summary>Damage dealt to the held pawn's torso each round, before
        /// the mod-settings multiplier. INVENTED: 4 — a human torso (40 HP)
        /// is destroyed in roughly 20 s of uninterrupted hold, which is
        /// "slowly" in melee terms and leaves time for a rescue.</summary>
        public float crushDamage = 4f;

        /// <summary>Damage type of the crush. Null = vanilla Blunt.</summary>
        public DamageDef crushDamageDef;

        /// <summary>Armor penetration of the crush. INVENTED: 0.15 — a
        /// pincer squeeze is not a knife; armour matters, but a
        /// bodySize-4 grip still gets through some of it.</summary>
        public float crushArmorPenetration = 0.15f;

        /// <summary>Chance that ONE melee hit on the grabber from a third
        /// pawn breaks each hold it has. INVENTED: 0.35 — the brief's
        /// default; two or three hits from a rescuer usually free the victim.</summary>
        public float breakHoldChanceOnHit = 0.35f;

        /// <summary>Cells the grabber may be from a held pawn and still
        /// crush it. INVENTED: 1.5 — adjacent (including diagonals), the
        /// same reach RM_HediffDef_Grapple.releaseRadius defaults to.</summary>
        public float crushRadius = 1.5f;

        public RM_CompProperties_Grappler()
        {
            compClass = typeof(RM_CompGrappler);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (crushIntervalTicks <= 0)
            {
                yield return "RM_CompProperties_Grappler crushIntervalTicks must be > 0.";
            }

            if (crushDamage < 0f)
            {
                yield return "RM_CompProperties_Grappler crushDamage must be >= 0.";
            }

            if (breakHoldChanceOnHit < 0f || breakHoldChanceOnHit > 1f)
            {
                yield return "RM_CompProperties_Grappler breakHoldChanceOnHit must be between 0 and 1.";
            }

            if (crushRadius <= 0f)
            {
                yield return "RM_CompProperties_Grappler crushRadius must be > 0.";
            }
        }
    }
}
