using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.JawaIonWeapons
{
    /// <summary>
    /// Applies an accumulating hediff on hit WITHOUT ever dealing an injury.
    ///
    /// WHY THIS EXISTS
    /// ===============
    /// The Jawa ion blaster is a capture weapon: it must never wound or kill a
    /// fleshy target, but it must wear one down until they collapse alive. No
    /// stock damage worker can do both.
    ///
    ///   * The StunBase family (which RSW_JawaIon_Damage belongs to) cannot kill,
    ///     but never reaches DamageWorker_AddInjury.ApplyDamageToPart -- and
    ///     that method is the ONLY thing in the game that reads a DamageDef's
    ///     additionalHediffs. Every Core def using additionalHediffs is an
    ///     injury damage in Damages_MeleeWeapon.xml. So the buildup block in
    ///     DamageDefs_JawaIon.xml has never once executed.
    ///   * DamageWorker_AddInjury does read additionalHediffs, but it deals a
    ///     real injury, and any injury can kill. That loses the whole point.
    ///
    /// This worker closes that gap: base.Apply for the impact sound and vanilla
    /// bookkeeping, then the hediff applied by hand.
    ///
    /// WHY SUBCLASSING DamageWorker IS SAFE FOR THE MECH HALF  [verified from IL]
    /// =========================================================================
    /// Verse.Thing::TakeDamage calls dinfo.Def.Worker.Apply and never reads
    /// causeStun; neither does Pawn::PostApplyDamage. Stun is resolved outside
    /// the worker entirely. Vanilla EMP proves it -- EMP declares no workerClass
    /// at all, so it runs on the base DamageWorker and still stuns. Therefore
    /// deriving from DamageWorker and calling base.Apply leaves the EMP-style
    /// stun on mechanoids and droids exactly as it is today.
    ///
    /// Verse.DamageWorker::Apply itself, with harmsHealth=false, does nothing
    /// but play the impact sound: its only other branch is guarded by
    /// `useHitPoints AND harmsHealth`. So nothing is lost by calling it and the
    /// impact sound is gained.
    ///
    /// TUNING LIVES IN XML
    /// ===================
    /// Severity is read from the DamageDef's own additionalHediffs entries
    /// rather than hardcoded, so that block stops being dead weight and stays
    /// the tuning surface. severityFixed wins if set, otherwise
    /// severityPerDamageDealt * damage. Hediff.Severity clamps itself to the
    /// HediffDef's maxSeverity, so no clamping is done here.
    /// </summary>
    public class DamageWorker_IonBuildup : DamageWorker
    {
        public override DamageResult Apply(DamageInfo dinfo, Thing victim)
        {
            DamageResult result = base.Apply(dinfo, victim);

            ApplyMachineTier(dinfo, victim);
            ApplyShieldBreak(dinfo, victim);

            // MOD_OPTIONS_RETROFIT_1: the flesh/droid buildup tier is one of the
            // player's per-mechanic switches. Off = no hediff is ever deposited;
            // base.Apply above has already run, so the bolt still lands and still
            // makes its noise.
            if (!RSW_JawaIonWeaponsSettings.fleshBuildupEnabled)
            {
                return result;
            }

            Pawn pawn = victim as Pawn;
            if (pawn == null || pawn.Dead || pawn.health == null)
            {
                return result;
            }

            // Skip TRUE MECHANOIDS only -- not every non-flesh pawn.
            //
            // This guard used to read `!pawn.RaceProps.IsFlesh`, on the
            // assumption that droids were already covered by causeStun. They
            // were not, and the assumption collided with our own doctrine
            // patch: Jawa_Doctrine/Patches/DroidsAreMachines.xml deliberately
            // sets isOrganic:false so that EMP/ion CAN stun droids
            // (StunHandler::CanBeStunnedByDamage only stuns on EMP when
            // !IsFlesh). So the very flag that switched stunning ON switched
            // buildup OFF, and ion stunned a droid briefly and never downed it.
            //
            // MEASURED LIVE 2026-08-12 on the 573 stack, before this change:
            //   OuterRim_BattleDroid  isFlesh=False  fleshType=Asimov_Automaton
            //                         isMechanoid=False  intelligence=Humanlike
            //   after EMP:            stunTicksLeft=1500, hediffs 0 -> 0,
            //                         downed=false
            // Zero hediffs accumulated: the guard bit exactly here.
            //
            // IsMechanoid is the right line because the two cases genuinely
            // differ. JDS Separatist droids are true mechanoids and are
            // force-killed on downing, so buildup that ends in Downed is wasted
            // work on them. OuterRim battle droids are non-flesh, non-mechanoid
            // humanlikes -- downing is capacity-based and works, which is what
            // makes them capturable via OuterRim_DataSpike (requires Downed ||
            // IsPrisoner).
            //
            // ⚠️ Do NOT "fix" the underlying issue by setting isOrganic back to
            // true. That stops EMP/ion stunning droids at all, re-enables
            // medical tending of droids against the doctrine ruling, and makes
            // droid corpses rot -- which currently protects the salvage loop.
            // Full argument: runtime/droid_ruling.md.
            if (pawn.RaceProps == null || pawn.RaceProps.IsMechanoid)
            {
                return result;
            }

            List<DamageDefAdditionalHediff> entries = dinfo.Def?.additionalHediffs;
            if (entries == null)
            {
                return result;
            }

            for (int i = 0; i < entries.Count; i++)
            {
                DamageDefAdditionalHediff entry = entries[i];
                if (entry?.hediff == null)
                {
                    continue;
                }

                float severity = entry.severityFixed > 0f
                    ? entry.severityFixed
                    : entry.severityPerDamageDealt * dinfo.Amount;

                // MOD_OPTIONS_RETROFIT_1: player multiplier on top of the XML number.
                // Default 1.0 -> identical to shipped behavior.
                severity *= RSW_JawaIonWeaponsSettings.stunBuildupMultiplier;

                // Owner ruling 2026-08-29 (ION_STUN_IGNORES_BODY_SIZE_1): the overload
                // barrier scales with the SQUARE of the target's body size. A Human
                // (BodySize 1) is the unscaled reference point -- the weapon's identity
                // against people is untouched. A rat (BodySize ~0.2) drops in one hit.
                // A 32x-bodySize creature (AA_Behemoth) needs 1024x the severity --
                // deliberately: "It should take a ship-weapon-scale ion gun to take
                // this thing down, and that's good." No cap, no softening curve.
                //
                // The exponent is now the settings value bodySizeResistExponent, whose
                // DEFAULT IS 2 -- i.e. the literal bodySize*bodySize this shipped with
                // (BodySizeDivisor special-cases exactly 2, so no float drift).
                severity /= RSW_JawaIonWeaponsSettings.BodySizeDivisor(pawn.BodySize);

                if (severity <= 0f)
                {
                    continue;
                }

                // GetOrAddHediff returns the existing instance if the pawn already
                // carries one, which is what makes this accumulate rather than
                // stacking duplicate hediffs.
                Hediff hediff = pawn.health.GetOrAddHediff(entry.hediff, null, dinfo, result);
                if (hediff == null)
                {
                    continue;
                }

                hediff.Severity += severity;
            }

            return result;
        }

        /// <summary>
        /// D1's TOP TWO TIERS. Stuns a machine or a droid by re-applying the hit as
        /// vanilla EMP, which is the only route that reaches them.
        ///
        /// WHY causeStun ON OUR OWN DEF HAS NEVER DONE ANYTHING  [read from source]
        /// =====================================================================
        /// StunHandler::CanBeStunnedByDamage whitelists Core DamageDefs BY IDENTITY
        /// for pawns, and a modded def is not on the list:
        ///
        ///     if (def == DamageDefOf.Stun) return true;
        ///     if (def == DamageDefOf.EMP &amp;&amp; !pawn.RaceProps.IsFlesh) return true;
        ///     if (Biotech &amp;&amp; def == MechBandShockwave &amp;&amp; IsMechanoid) return true;
        ///     if (def == DamageDefOf.NerveStun &amp;&amp; !IsMechanoid) return true;
        ///     return false;
        ///
        /// So `causeStun: true` on RSW_JawaIon_Damage stunned NOTHING, and the earlier
        /// comment in DamageDefs_JawaIon.xml claiming we inherit "the flesh-vs-mech
        /// resistance gradient" from EMP was wrong: EMP's mech half is not inherited,
        /// it is keyed on the def OBJECT. Measured live 2026-08-22: Mech_Scyther took
        /// RSW_JawaIon_Damage x13 at up to 20 and reported stunned=False, stunTicks=0,
        /// while one vanilla EMP at 20 gave it 570 ticks.
        ///
        /// ⚠️ NON-PAWNS ALREADY WORKED and are deliberately left alone. The non-Pawn
        /// branch of CanBeStunnedByDamage only asks `def.causeStun`, so turrets,
        /// vehicles-as-things and other stunnable buildings have been taking the ion
        /// stun correctly all along. Only pawns were dark.
        ///
        /// WHY RE-APPLY EMP RATHER THAN CALL StunFor DIRECTLY
        /// ==================================================
        /// StunFor is public and would "work", but it skips everything around it:
        /// EMPResistance, the per-def adaptation timer that stops a mech being
        /// perma-locked, the stunFromEMP flag that draws the DisabledByEMP effecter,
        /// and the battle log entry. Adaptation in particular is PRIVATE state inside
        /// StunHandler, so a direct call could never honour it. Going back through
        /// Thing::TakeDamage with DamageDefOf.EMP buys all four for free, and EMP is
        /// harmsHealth:false / makesBlood:false, so it cannot wound or kill.
        ///
        /// No recursion: the EMP def runs Core's plain DamageWorker, not this one.
        /// </summary>
        private void ApplyMachineTier(DamageInfo dinfo, Thing victim)
        {
            // MOD_OPTIONS_RETROFIT_1: the machine/droid tier is its own switch.
            if (!RSW_JawaIonWeaponsSettings.machineTierEnabled)
            {
                return;
            }

            Pawn pawn = victim as Pawn;
            if (pawn == null || pawn.Dead || !pawn.Spawned || pawn.RaceProps == null)
            {
                return;
            }

            // FLESH IS THE BOTTOM TIER AND TAKES NO STUN. D1 is explicit that a person
            // must be worn down and gang-tackled, never disabled outright; that is the
            // whole capture-not-kill pillar. The buildup below Apply() is their tier.
            if (pawn.RaceProps.IsFlesh)
            {
                return;
            }

            IonDamageDef def = dinfo.Def as IonDamageDef;
            if (def == null)
            {
                return;
            }

            bool machine = pawn.RaceProps.IsMechanoid || pawn.RaceProps.IsDrone;
            float amount = machine ? def.empAmountMachine : def.empAmountDroid;
            if (amount <= 0f)
            {
                return;
            }

            // MOD_OPTIONS_RETROFIT_1: player multiplier, default 1.0 -> unchanged.
            amount *= RSW_JawaIonWeaponsSettings.machineTierMultiplier;

            // Same body-size^2 ruling as the flesh tier (ION_STUN_IGNORES_BODY_SIZE_1,
            // owner 2026-08-29) applied here too: a superheavy mech is BodySize-huge
            // and should not drop as fast as a battle droid. StunHandler turns this
            // amount into ticks (amount * 30) before EMPResistance, so scaling the
            // amount itself scales the resulting stun duration the same way.
            // Exponent from settings; default 2 is that ruled curve, unchanged.
            amount /= RSW_JawaIonWeaponsSettings.BodySizeDivisor(pawn.BodySize);
            if (amount <= 0f)
            {
                return;
            }

            DamageInfo emp = new DamageInfo(
                DamageDefOf.EMP,
                amount,
                0f,
                dinfo.Angle,
                dinfo.Instigator,
                null,
                dinfo.Weapon,
                DamageInfo.SourceCategory.ThingOrUnknown,
                dinfo.IntendedTarget);
            emp.SetIgnoreArmor(true);
            victim.TakeDamage(emp);
        }

        /// <summary>
        /// DROIDWORKS_ION_SHIELD_BODYSIZE_1 (packet B6). "Ion breaks shields" -
        /// droid_ruling.md section 5A item 3: "have the ion projectile also
        /// deliver a small amount of real EMP damage", so
        /// CompShield.PostPreApplyDamage's `dinfo.Def == DamageDefOf.EMP`
        /// reference-equality check fires and breaks it (read from source:
        /// that check is unconditional on amount - ANY EMP hit on an active
        /// shield instantly zeroes its energy and calls Break()).
        ///
        /// 🔴 CORRECTED, live-tested: ApplyMachineTier does NOT already cover
        /// this for droids/machines, despite sending a real DamageDefOf.EMP
        /// hit. `emp.SetIgnoreArmor(true)` on THAT dispatch (correct for its
        /// own stun purpose - armor should not block an EMP stun pulse) also
        /// skips the ENTIRE apparel-comp loop that shields hook into:
        /// Pawn_HealthTracker.PreApplyDamage's own source reads
        /// `if (this.pawn.apparel != null &amp;&amp; !dinfo.IgnoreArmor)` around the
        /// `wornApparel[i].CheckPreAbsorbDamage(dinfo)` loop that is the ONLY
        /// path to CompShield.PostPreApplyDamage - an IgnoreArmor hit never
        /// reaches a shield at all, worn by flesh or droid alike. First
        /// attempt at this fix (flesh-only, IgnoreArmor left true) was tried
        /// live and DEMONSTRABLY DID NOT WORK (a shielded colonist still
        /// absorbed a bullet after an ion hit, identically to an un-ion'd
        /// control) - caught before commit, not shipped broken.
        ///
        /// Fix: a SEPARATE dispatch, for every pawn regardless of flesh/
        /// droid/mech, that does NOT ignore armor - CompShield's own EMP
        /// branch never checks dinfo.Amount or armor rating before breaking,
        /// and ordinary armor apparel has no PostPreApplyDamage of its own to
        /// interfere (armor reduction happens later, inside
        /// DamageWorker.ApplyDamageToPart, after this comp-absorb pass), so
        /// letting armor apply here costs nothing and is what lets the hit
        /// reach the shield's own comp check at all. amount 1 is too small to
        /// matter for anything that reads it; StunHandler's own gate
        /// (`!pawn.RaceProps.IsFlesh`) still refuses to stun a flesh pawn
        /// from EMP regardless of amount, and EMP is harmsHealth:false /
        /// makesBlood:false, so this is a genuine no-op on anyone with no
        /// active shield - it does not need to check for one first.
        /// </summary>
        private void ApplyShieldBreak(DamageInfo dinfo, Thing victim)
        {
            // MOD_OPTIONS_RETROFIT_1: shield-popping is its own switch. Off = this
            // extra dispatch never happens at all, so a shield belt absorbs ion fire
            // like any other shot.
            if (!RSW_JawaIonWeaponsSettings.shieldBreakEnabled)
            {
                return;
            }

            Pawn pawn = victim as Pawn;
            if (pawn == null || pawn.Dead || !pawn.Spawned)
            {
                return;
            }

            DamageInfo emp = new DamageInfo(
                DamageDefOf.EMP,
                1f,
                0f,
                dinfo.Angle,
                dinfo.Instigator,
                null,
                dinfo.Weapon,
                DamageInfo.SourceCategory.ThingOrUnknown,
                dinfo.IntendedTarget);
            // Deliberately NOT SetIgnoreArmor(true) here - see this method's
            // own header for why that flag is exactly what breaks the fix.
            victim.TakeDamage(emp);
        }
    }
}
