namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SUPERDEEP_PRISON_ROOM_1 — the Verse-free half of "an enclosed superdeep area is a room".
	/// Selftested (SelfTest/Program.cs). The Harmony seams live in Superdeep/RM_PitRooms.cs.
	///
	/// LAW 2 exception [D] (owner, 2026-09-17, by card): depth may bound a ROOM. Since the relative rules a pit room is a
	/// person-band pocket whose floor is at least the room depth (RM_PitRooms.IsPitCell). PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER
	/// (owner card 2026-10-18): that depth is 3.0 m for a person, scaled by body height — <i>"deep enough that an athletic
	/// human could not reasonably raise their arms over their head and jump a little to grab the edge, then scramble up"</i>.
	/// </summary>
	public static class RM_PitRoomMath
	{
		/// <summary>Two cells (or regions, or districts) may share a room only on the same side
		/// of the pit wall: both superdeep or both not.</summary>
		public static bool SameSide(bool aPit, bool bPit)
		{
			return aPit == bPit;
		}

		/// <summary>How a warden job is served from the lip instead of from inside the pit.</summary>
		public enum LipKind
		{
			/// <summary>Not a lip-served job: vanilla pathing, untouched.</summary>
			None,
			/// <summary>Needs to touch the target (tend, capture down): a lip cell 8-adjacent.</summary>
			Touch,
			/// <summary>A social interaction (recruit, convert, enslave, reduce will, interrogate):
			/// vanilla's own rule is within 6 cells with line of sight, so any such lip cell.</summary>
			Interact,
			/// <summary>Food delivery: the food is dropped down onto its cell from an 8-adjacent lip.</summary>
			Drop,
		}

		/// <summary>Vanilla 1.6 JobDef names (Core / Ideology / Anomaly Jobs_Work.xml).</summary>
		public static LipKind KindOf(string jobDefName)
		{
			switch (jobDefName)
			{
				case "TendPatient":
				case "RM_CaptureDown":
					return LipKind.Touch;
				case "PrisonerAttemptRecruit":
				case "PrisonerConvert":
				case "PrisonerEnslave":
				case "PrisonerReduceWill":
				case "PrisonerInterrogateIdentity":
					return LipKind.Interact;
				case "DeliverFood":
					return LipKind.Drop;
				default:
					return LipKind.None;
			}
		}

		/// <summary>The radius a lip cell may be from the target cell for this kind.
		/// 1.5 = the 8 neighbours; 6 = vanilla's SocialInteractionUtility range.</summary>
		public static float RadiusFor(LipKind kind)
		{
			return kind == LipKind.Interact ? 6f : kind == LipKind.None ? 0f : 1.5f;
		}

		/// <summary>A lip cell: NOT superdeep (so nobody ever stands in the pit to do the job),
		/// standable, within the radius.</summary>
		public static bool LipCandidate(bool cellIsSuperdeep, bool standable, float distToTarget, float radius)
		{
			return !cellIsSuperdeep && standable && distToTarget <= radius;
		}

		public enum CaptureDownVerdict
		{
			Allowed,
			SettingOff,
			NotAPerson,
			OwnSide,
			AlreadyPrisoner,
			NotHeld,
			NoPrisonBed,
		}

		/// <summary>
		/// "Capture down" (owner, 2026-09-17: <i>"easy prisoner capture once they're in the pit, and no
		/// you don't have to go down and enter the room to capture them"</i>). Only a person the pit
		/// actually HOLDS (owner Q4 width rule — a creature too wide for its pit is not trapped, so it is
		/// not offered), and only into a pit that is a prison room (a prisoner bed in it: "it's just a
		/// room until you put a prisoner bed in it").
		/// </summary>
		public static CaptureDownVerdict CaptureDown(bool settingOn, bool humanlike, bool ownSide,
			bool alreadyPrisoner, bool held, bool roomIsPrison)
		{
			if (!settingOn) return CaptureDownVerdict.SettingOff;
			if (!humanlike) return CaptureDownVerdict.NotAPerson;
			if (ownSide) return CaptureDownVerdict.OwnSide;
			if (alreadyPrisoner) return CaptureDownVerdict.AlreadyPrisoner;
			if (!held) return CaptureDownVerdict.NotHeld;
			if (!roomIsPrison) return CaptureDownVerdict.NoPrisonBed;
			return CaptureDownVerdict.Allowed;
		}

		/// <summary>PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER (owner card 2026-10-18): a pit room's floor is 3.0 m down for a person
		/// (a 1.75 m human's reach overhead, about 2.2 m, plus a small jump). The Mod Setting pitRoomMinDepthMetres is this
		/// person figure; 0 = any depth.</summary>
		public const float DefaultRoomDepthMetres = 3.0f;

		/// <summary>The person the room depth is stated for: RM_RelativeRulesMath.HeightByBand[2].</summary>
		public const float ReferenceHeightMetres = 1.75f;

		/// <summary>The room depth for a creature of this height: the person figure scaled by height / 1.75 m (a 0.5 m creature
		/// needs about 0.86 m, a 3.5 m one 6 m). A non-positive person figure means any depth (0).</summary>
		public static float RoomDepthMetresFor(float personMetres, float heightMetres)
		{
			if (!(personMetres > 0f))
			{
				return 0f;
			}
			if (!(heightMetres > 0f) || float.IsInfinity(heightMetres))
			{
				heightMetres = ReferenceHeightMetres;
			}
			return personMetres * heightMetres / ReferenceHeightMetres;
		}

		/// <summary>Is a floor this deep a pit room for this creature (it cannot reach up, jump and scramble out)?</summary>
		public static bool DeepEnoughFor(float floorMetres, float personMetres, float heightMetres)
		{
			return floorMetres + 1e-4f >= RoomDepthMetresFor(personMetres, heightMetres);
		}

		/// <summary>PIT_ALERT_BUILD_RED_MEANS_HELP (owner card Q12, 2026-10-18): the red "colonist stuck in a pit" alert names a
		/// free colonist the pit holds who cannot reach food or a bed (only the needs it has count).</summary>
		public static bool StuckAlert(bool settingOn, bool freeColonist, bool held, bool needsFood, bool foodReachable,
			bool needsRest, bool bedReachable)
		{
			return settingOn && freeColonist && held && ((needsFood && !foodReachable) || (needsRest && !bedReachable));
		}

		/// <summary>Capture down is a short act, not a fight: the pit already did the work.
		/// PROVISIONAL (no owner number): 3 seconds.</summary>
		public const int CaptureDownTicks = 180;
	}
}
