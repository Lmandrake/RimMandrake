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
				case "FeedPatient":   // DRAINED_HOLE_IS_A_PRISON: a downed prisoner is fed by hand from a lip that touches him
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
			/// <summary>DRAINED_HOLE_IS_A_PRISON: a downed person in a bare hole where no lip touches him: nobody could feed him
			/// there (he cannot get up to food, and the hand-feeding warden must touch him), so he is not taken (BedlessDowned).</summary>
			DownedNoLip,
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

		/// <summary>DRAINED_HOLE_IS_A_PRISON (owner card 2026-11-05, "Drained moat is a prison": capture from the rim works with
		/// NO bed, and the hole is the prison). Capture down's two last gates, held and prison, each pass for a person the pit
		/// TRAPS (RM_SuperdeepTrap.IsTrapped: no way out at its climb) while the bedless switch is on. With the switch off, or
		/// a pawn that can climb out, the bed rule stands: a bare hole is still NoPrisonBed.</summary>
		public static bool BedlessPrison(bool roomIsPrison, bool bedlessOn, bool trapped)
		{
			return roomIsPrison || bedlessOn && trapped;
		}

		/// <summary>DRAINED_HOLE_IS_A_PRISON: the held gate. The room-depth size rule (HoldsBySize) is the bed prison's; a hole that
		/// traps the pawn holds it whatever its depth.</summary>
		public static bool BedlessHeld(bool heldBySize, bool bedlessOn, bool trapped)
		{
			return heldBySize || bedlessOn && trapped;
		}

		/// <summary>DRAINED_HOLE_IS_A_PRISON: vanilla's FoodAvailableInRoomTo rule, read over the prisoner's pocket instead of its
		/// room (a shallow hole's room is the outdoors): food enough is down there when what lies in the pocket covers what the
		/// hungry prisoners in it want, with vanilla's 0.5 nutrition of slack.</summary>
		public static bool FoodEnoughInPocket(bool carryingEdible, float nutritionInPocket, float nutritionWanted)
		{
			return carryingEdible || nutritionInPocket + 0.5f >= nutritionWanted;
		}

		/// <summary>DRAINED_HOLE_IS_A_PRISON: a cell food can be dropped onto for a lip-served prisoner: in its pocket and its room
		/// (a meal is socially proper to a prisoner only in its own room: SocialProperness.IsSociallyProper), standable, and on
		/// the pocket's rim (a cell beside it is outside the pocket, so a lip can touch it).</summary>
		public static bool DropCell(bool inPocket, bool sameRoom, bool standable, bool onRim)
		{
			return inPocket && sameRoom && standable && onRim;
		}

		/// <summary>DRAINED_HOLE_IS_A_PRISON: a cell whose food the pocket count adds up. Vanilla's FoodAvailableInRoomTo counts
		/// only the prisoner's room, and he may eat only food in his own room: a sloped pocket can span two rooms (the deep part
		/// a pit room, the shallow end the outdoors), and food in the other one feeds nobody.</summary>
		public static bool FoodCellCounts(bool inPocket, bool sameRoom)
		{
			return inPocket && sameRoom;
		}

		/// <summary>DRAINED_HOLE_IS_A_PRISON: vanilla's WardenFeedUtility.ShouldBeFed wants a bed. A downed lip-served prisoner on
		/// the bare floor is fed by hand too (vanilla Feed: the warden carries food to him and must touch him), when he can be
		/// brought food and a lip cell touches him.</summary>
		public static bool FedFromLip(bool vanilla, bool lipServed, bool downed, bool inBed, bool canBeBroughtFood, bool touchLip)
		{
			return vanilla || lipServed && downed && !inBed && canBeBroughtFood && touchLip;
		}

		/// <summary>DRAINED_HOLE_IS_A_PRISON: capture down's last word on a bedless capture. A downed person no lip touches would
		/// starve where he lies (nobody can hand him food), so he is not taken; with a lip beside him, or a bed prison, the
		/// verdict stands.</summary>
		public static CaptureDownVerdict BedlessDowned(CaptureDownVerdict v, bool viaBedless, bool downed, bool touchLip)
		{
			return v == CaptureDownVerdict.Allowed && viaBedless && downed && !touchLip ? CaptureDownVerdict.DownedNoLip : v;
		}

		/// <summary>DRAINED_HOLE_IS_A_PRISON: may a remembered lip answer (one warden, one prisoner) be used again? A "yes" holds
		/// only while its lip still serves where the prisoner stands now (within the kind's radius, still a good spot); a "no"
		/// holds only while he has not moved. A stale "yes" sends the warden to a lip that no longer serves, the path patch
		/// finds none, and vanilla restarts the job in the same tick until its 10-jobs guard trips.</summary>
		public static bool LipMemoGood(bool ok, bool prisonerMoved, float lipToPrisoner, float radius, bool goodForKind)
		{
			return ok ? lipToPrisoner <= radius && goodForKind : !prisonerMoved;
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

		/// <summary>What the capture-down warden does on reaching a lip cell.</summary>
		public enum CaptureStep
		{
			/// <summary>Touching the held pawn from open ground: pin it and take the moment.</summary>
			Hold,
			/// <summary>The held pawn moved out of reach (it wanders in the pit), or the warden is on a pit cell: find a new lip.</summary>
			Repath,
			/// <summary>It kept moving: end the job rather than chase forever.</summary>
			GiveUp,
		}

		/// <summary>How many times the warden walks to a fresh lip before giving up.</summary>
		public const int CaptureRepathLimit = 6;

		/// <summary>PIT_CAPTURE_FIX_HOSTILE_NOT_PRISONER: a held pawn is not frozen, so the lip the job was given can stop
		/// touching it before the warden arrives. Repath (bounded) instead of failing the hold.</summary>
		public static CaptureStep CaptureDownNext(bool wardenTouchesVictim, bool wardenOnPitFloor, int repaths)
		{
			if (wardenTouchesVictim && !wardenOnPitFloor)
			{
				return CaptureStep.Hold;
			}
			return repaths < CaptureRepathLimit ? CaptureStep.Repath : CaptureStep.GiveUp;
		}

		/// <summary>Where the capture-down warden walks.</summary>
		public enum CaptureLip
		{
			/// <summary>A lip cell 8-adjacent to the held pawn: walk there and hold.</summary>
			Touch,
			/// <summary>No lip touches it (the centre of a 3x3 pit): wait at the nearest lip in talking range for it to come close.</summary>
			Wait,
			/// <summary>No lip at all within reach: the job cannot be done.</summary>
			None,
		}

		/// <summary>PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES: a held pawn on a cell no lip touches (the 3x3 pit's centre;
		/// testq J20261026T004751Z ended at 96,167) used to end the job at once with the repath budget unspent.</summary>
		public static CaptureLip CaptureLipPick(bool touchLipFound, bool nearLipFound)
		{
			return touchLipFound ? CaptureLip.Touch : nearLipFound ? CaptureLip.Wait : CaptureLip.None;
		}

		/// <summary>PROVISIONAL (no owner number): one second at the lip before looking again, so a repath gives the held
		/// pawn time to move instead of spending the whole budget in a few ticks.</summary>
		public const int CaptureRepathPauseTicks = 60;

		/// <summary>The pause before a walk: none on the first approach, CaptureRepathPauseTicks after a repath.</summary>
		public static int CapturePauseTicks(int repaths)
		{
			return repaths <= 0 ? 0 : CaptureRepathPauseTicks;
		}
	}
}
