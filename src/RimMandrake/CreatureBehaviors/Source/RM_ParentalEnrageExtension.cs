using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHRUBLAND_GIANT_ENRAGE_1. Attach to a race ThingDef to give it
	/// "GIANT WITH YOUNG": a pawn of this race that is still in a juvenile
	/// life stage is GUARDED — let a tool-user or humanlike walk within
	/// triggerRadius of it and the nearest ADULT of the same race drops into a
	/// short, scoped rage aimed at that one intruder. No warning is given: the
	/// trigger is proximity, not any player action.
	///
	/// design/Jawa/worldbuilding/biomes/arid_shrubland.md §4, the owner-ratified
	/// size ladder: "Large — giants' children only, and approach is attack: the
	/// parent enrages if you even get near the young. No warning is given."
	///
	/// RM tier: this names no species, no biome and no campaign. Carry the
	/// extension (plus RM_CompProperties_ParentalEnrage, the ticker) on any
	/// future "giant with young" race and it reuses every line here — that is
	/// the whole reason this is a DefModExtension on the shared kit rather than
	/// per-species C#.
	///
	/// ── Why this shape, MEASURED against the decompiled 1.6 engine ──
	///
	/// 1. There is NO vanilla parent/offspring bond to hook for a WILD herd.
	///    Hediff_Pregnant.DoBirthSpawn does add a real
	///    PawnRelationDefOf.Parent direct relation for any flesh race that
	///    gives live birth — so a calf BORN on the map genuinely knows its
	///    mother — but wildlife spawned by map gen or an ambient animal
	///    incident is generated pawn-by-pawn and has no such relation at all.
	///    So the relation is used as a PREFERENCE when it happens to exist
	///    (see preferTrueParent) and "nearest adult of the same race" is the
	///    fallback that always works.
	/// 2. The trigger is a bounded radial scan on the YOUNG pawn's own comp at
	///    CompTickRare (250 ticks), never a per-tick or full-map scan. Only
	///    juveniles pay it; the comp is inert on every adult carrier. The
	///    expensive half (finding the guardian, a wider search) runs only after
	///    an intruder has actually been found, which is rare.
	/// 3. The rage itself is a real MentalStateDef whose stateClass derives
	///    from vanilla MentalState_Manhunter, because MentalStateNonCritical
	///    dispatches manhunting through ThinkNode_ConditionalMentalStateClass
	///    — an IsInstanceOfType check, NOT a def-identity check like its
	///    sibling ThinkNode_ConditionalMentalState. A subclass therefore
	///    inherits JobGiver_Manhunter's whole chase-and-melee behaviour with
	///    no think-tree patch of any kind. That is the load-bearing fact of
	///    this whole build.
	/// 4. The SCOPE comes from GenHostility.HostileTo consulting
	///    MentalState.ForceHostileTo(Thing): RM_MentalState_ParentalEnrage
	///    answers true for the one intruder and false for everything else, so
	///    JobGiver_Manhunter's target search finds exactly that pawn and
	///    nobody else. It is a rage at ONE trespasser, never a manhunter flip
	///    against the map.
	/// </summary>
	public class RM_ParentalEnrageExtension : DefModExtension
	{
		/// <summary>
		/// The mental state the guardian adult is put into. Set this in XML to
		/// RM_ParentalEnrage (this kit's own def) or to any other state whose
		/// stateClass derives from RM_MentalState_ParentalEnrage. Null leaves
		/// the extension inert — an unfilled extension is never a race that
		/// rages by accident.
		/// </summary>
		public MentalStateDef enrageState;

		/// <summary>
		/// How close (in cells) an intruder has to get to the young before it
		/// counts as an approach. INVENTED: 5 — well outside melee reach, so
		/// the rage reads as "you came too near", not "you touched it", which
		/// is what "approach is attack" means.
		/// </summary>
		public float triggerRadius = 5f;

		/// <summary>
		/// How far from the young to look for the adult that answers.
		/// INVENTED: 30 — a herd's own spread. Beyond it the calf is genuinely
		/// alone and nothing happens, which is the interesting case rather
		/// than a defect.
		/// </summary>
		public float guardianSearchRadius = 30f;

		/// <summary>
		/// The rage is force-ended after this many ticks no matter what, via
		/// MentalState.forceRecoverAfterTicks (a real vanilla field that
		/// MentalState.MentalStateTick already honours). INVENTED: 2500
		/// (~1 in-game hour) — long enough to run an intruder off the calf,
		/// far short of vanilla Manhunter's own 10000-tick floor, which is the
		/// whole point of "time-boxed, not a permanent manhunter flip".
		/// </summary>
		public int enrageDurationTicks = 2500;

		/// <summary>
		/// Ticks between one guardian being roused by this young pawn and the
		/// next, so a group standing in range does not re-rage the herd every
		/// rare tick. INVENTED: 1250 (~30 in-game minutes), this assembly's own
		/// RM_CompProximityPsychicStun cooldown pattern at half the interval.
		/// </summary>
		public int cooldownTicks = 1250;

		/// <summary>
		/// Life-stage index at or below which a pawn of this race counts as
		/// "young" and is guarded. -1 (the default) means "every life stage
		/// except the last one the race declares", which is correct for any
		/// ordinary baby/juvenile/adult ladder without naming a life stage.
		/// </summary>
		public int youngLifeStageMaxIndex = -1;

		/// <summary>
		/// Only a pawn of ToolUser or Humanlike intelligence trips the
		/// trigger. On by default: the biome's ruling is about YOU getting
		/// near the young, and a passing hare should not enrage a giant.
		/// </summary>
		public bool onlyToolUserOrHumanlikeTriggers = true;

		/// <summary>
		/// A pawn of the same race as the young never trips the trigger — the
		/// herd walks among its own calves all day.
		/// </summary>
		public bool exemptSameRace = true;

		/// <summary>
		/// A pawn sharing the young's OWN faction never trips the trigger, so
		/// once a herd is tamed the colony's own handlers can walk past its
		/// calves. A wild young has no faction, so this exempts nobody while
		/// wild — which is the wanted asymmetry, not an oversight.
		/// </summary>
		public bool exemptSameFaction = true;

		/// <summary>
		/// Require line of sight from the young to the intruder before it
		/// counts as an approach. OFF by default: "no warning is given" cuts
		/// both ways — a herd that smells you through a wall is the ruling,
		/// and a calf does not need to see you to bawl.
		/// </summary>
		public bool requireLineOfSight;

		/// <summary>
		/// When a real PawnRelationDefOf.Parent relation exists (a calf born
		/// on this map rather than spawned by map gen), prefer that parent
		/// over a merely closer adult. Distance decides among everything else.
		/// </summary>
		public bool preferTrueParent = true;
	}
}
