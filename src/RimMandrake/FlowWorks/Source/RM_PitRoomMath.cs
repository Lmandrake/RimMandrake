namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SUPERDEEP_PRISON_ROOM_1 — the Verse-free half of "an enclosed superdeep area is a room".
	/// Selftested (SelfTest/Program.cs). The Harmony seams live in Superdeep/RM_PitRooms.cs.
	///
	/// LAW 2 exception [D] (owner, 2026-09-17, by card): depth may bound a ROOM. This is the
	/// whole of the exception: whether a cell is a dug SUPERDEEP cell (D = 4) splits regions,
	/// districts and rooms. Nothing else about rooms, and no other system, reads depth because
	/// of it — D 1-3 never bound anything, and this is not a precedent for any future reader.
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

		/// <summary>Capture down is a short act, not a fight: the pit already did the work.
		/// PROVISIONAL (no owner number): 3 seconds.</summary>
		public const int CaptureDownTicks = 180;
	}
}
