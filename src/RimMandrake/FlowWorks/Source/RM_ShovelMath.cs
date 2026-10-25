namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SHOVELS_BUILD_NO_DIGGING_BARE_HANDED (owner 2026-10-25: "You can't dig without them. Hands don't work"; "Shovels now
	/// v1."). The pure rules, no Verse, so the SelfTest compiles this very file (ShovelChecks.cs). The game side is
	/// RM_Shovels.cs. Design: design/RimMandrake/shovels_v1_2026-10-25.md §2, §4.
	/// </summary>
	public static class RM_ShovelMath
	{
		/// <summary>PROVISIONAL (design §4a): the share of an assault raid's tool-users who bring a shovel.</summary>
		public const float DefaultRaiderShovelShare = 0.25f;

		/// <summary>PROVISIONAL (design §4a): the share of a sapper raid's tool-users who bring a shovel. Owner 2026-10-25 (Q1):
		/// "Siege is mortar-based. Sappers however would bring shovels &amp; ladders."</summary>
		public const float DefaultSapperShovelShare = 0.5f;

		/// <summary>Whether a pawn needs a shovel to dig or fill: only with the setting on, never machine labour (a mechanoid
		/// or an RM_MachineDigger race digs as it always did), never a race or flesh type marked RM_DigsBareHanded.</summary>
		public static bool NeedsShovel(bool settingOn, bool machineLabour, bool digsBareHanded)
		{
			return settingOn && !machineLabour && !digsBareHanded;
		}

		/// <summary>The share of a raid that brings shovels: none for a siege (mortar-based: it shells, it never digs), the
		/// sapper share for sappers, else the assault share; clamped to [0, 1].</summary>
		public static float ShareFor(bool siege, bool sappers, float assaultShare, float sapperShare)
		{
			if (siege)
			{
				return 0f;
			}
			float s = sappers ? sapperShare : assaultShare;
			return s < 0f ? 0f : (s > 1f ? 1f : s);
		}

		/// <summary>Whether this raider brings a shovel: deterministic per pawn id (a reload does not re-roll), its own hash
		/// so the shovel and jump-pack shares are not the same people. share &lt;= 0: nobody; &gt;= 1: everyone.</summary>
		public static bool GetsShovel(int pawnId, float share)
		{
			if (share <= 0f)
			{
				return false;
			}
			if (share >= 1f)
			{
				return true;
			}
			unchecked
			{
				uint h = ((uint)pawnId ^ 0x5bd1e995u) * 0x9E3779B1u;
				h ^= h >> 15;
				h *= 0x2c1b3c6du;
				h ^= h >> 12;
				return (h % 10000u) < (uint)(share * 10000f);
			}
		}
	}
}
