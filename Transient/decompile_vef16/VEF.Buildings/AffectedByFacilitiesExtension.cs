using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class AffectedByFacilitiesExtension : DefModExtension
{
	public List<ThingDef> copyLinksFrom;

	public bool disableFacilityExtensionLinking;

	public override void ResolveReferences(Def parentDef)
	{
		((DefModExtension)this).ResolveReferences(parentDef);
		if (copyLinksFrom == null)
		{
			return;
		}
		ThingDef def = (ThingDef)(object)((parentDef is ThingDef) ? parentDef : null);
		if (def == null)
		{
			return;
		}
		CompProperties_AffectedByFacilities parentComp = def.GetCompProperties<CompProperties_AffectedByFacilities>();
		if (parentComp == null)
		{
			return;
		}
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			foreach (ThingDef item in copyLinksFrom)
			{
				List<ThingDef> list = item.GetCompProperties<CompProperties_AffectedByFacilities>()?.linkableFacilities;
				if (list != null)
				{
					foreach (ThingDef item2 in list)
					{
						if (!parentComp.linkableFacilities.Contains(item2))
						{
							CompProperties_Facility compProperties = item2.GetCompProperties<CompProperties_Facility>();
							if (compProperties != null)
							{
								FacilityExtension modExtension = ((Def)item2).GetModExtension<FacilityExtension>();
								if (modExtension == null || !modExtension.disableAffectedByFacilitiesExtensionLinking)
								{
									compProperties.linkableBuildings.Add(def);
									parentComp.linkableFacilities.Add(item2);
								}
							}
						}
					}
				}
			}
		});
	}
}
