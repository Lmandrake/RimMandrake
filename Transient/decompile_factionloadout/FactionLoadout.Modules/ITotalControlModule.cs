using System.Collections.Generic;
using FactionLoadout.UISupport;
using RimWorld;
using Verse;

namespace FactionLoadout.Modules;

public interface ITotalControlModule
{
	string ModuleKey { get; }

	string ModuleName { get; }

	bool IsActive { get; }

	void Initialize();

	void AddTabs(PawnKindEdit edit, PawnKindDef defaultKind, List<Tab> tabs);

	void ExposeData(PawnKindEdit edit);

	void Apply(PawnKindEdit edit, PawnKindDef def, PawnKindEdit global);

	void CopyData(PawnKindEdit source, PawnKindEdit dest);

	void AddFactionUI(FactionEdit edit, Listing_Standard ui);

	void ExposeFactionData(FactionEdit edit);

	void ApplyFaction(FactionEdit edit, FactionDef def);
}
