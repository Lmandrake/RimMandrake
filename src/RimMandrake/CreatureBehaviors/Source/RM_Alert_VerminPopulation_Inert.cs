using RimWorld;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1 crash fix. Exists ONLY to keep
	/// RM_Alert_VerminPopulationBase from ever being a reflection "leaf".
	///
	/// Root cause (found live, 2026-09-11): RimWorld.AlertsReadout's constructor
	/// does `foreach (Type t in typeof(Alert).AllLeafSubclasses()) Activator.
	/// CreateInstance(t)` with NO abstract check and NO try/catch (RimSage-verified,
	/// RimWorld/AlertsReadout.cs). "Leaf" means "nothing subclasses it in the
	/// currently loaded type universe" — it does NOT mean "concrete". With no
	/// consumer mod loaded (ShipVermin's RM_Alert_ShipVermin, a future Greentide
	/// or Shokk alert), the abstract RM_Alert_VerminPopulationBase itself became
	/// the leaf, Activator.CreateInstance threw MissingMethodException
	/// (abstract types have no constructor to invoke), and the uncaught exception
	/// crashed AlertsReadout's ctor -> UIRoot_Play's ctor -> Find.MapUI stayed
	/// null -> every subsequent Update()/OnGUI()/MapComponentTick() NREs on
	/// Find.MapUI, on EVERY map-add path (fresh quicktest and loaded saves alike),
	/// independent of which content mod rode alongside it. Mistaken for a bug in
	/// one of the two auto-constructed MapComponents at first (LESSONS_INBOX,
	/// SHOKK_RSW_MOD_1) — it was never a MapComponent at all.
	///
	/// This sealed, always-inactive subclass makes the base permanently non-leaf
	/// regardless of which (if any) consumer mod is active, so creaturebehaviors
	/// is safe to load standalone.
	/// </summary>
	internal sealed class RM_Alert_VerminPopulation_Inert : RM_Alert_VerminPopulationBase
	{
		protected override string GroupTag => string.Empty;

		public override AlertReport GetReport()
		{
			return AlertReport.Inactive;
		}
	}
}
