using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class FacilityExtension : DefModExtension
{
	public bool linkOnInteractionSpots;

	public ThingDef equivalentToFacility;

	public List<ThingDef> copyLinksFrom;

	public bool disableAffectedByFacilitiesExtensionLinking;

	public override void ResolveReferences(Def parentDef)
	{
		((DefModExtension)this).ResolveReferences(parentDef);
		if (equivalentToFacility != null)
		{
			VanillaExpandedFramework_CompAffectedByFacilities_CanPotentiallyLinkTo_Patch.isActive = true;
		}
		if (copyLinksFrom == null)
		{
			return;
		}
		ThingDef def = (ThingDef)(object)((parentDef is ThingDef) ? parentDef : null);
		if (def == null)
		{
			return;
		}
		CompProperties_Facility parentFacility = def.GetCompProperties<CompProperties_Facility>();
		if (parentFacility == null)
		{
			return;
		}
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			foreach (ThingDef item in copyLinksFrom)
			{
				List<ThingDef> list = item.GetCompProperties<CompProperties_Facility>()?.linkableBuildings;
				if (list != null)
				{
					foreach (ThingDef item2 in list)
					{
						if (!parentFacility.linkableBuildings.Contains(item2))
						{
							CompProperties_AffectedByFacilities compProperties = item2.GetCompProperties<CompProperties_AffectedByFacilities>();
							if (compProperties != null)
							{
								AffectedByFacilitiesExtension modExtension = ((Def)item2).GetModExtension<AffectedByFacilitiesExtension>();
								if (modExtension == null || !modExtension.disableFacilityExtensionLinking)
								{
									compProperties.linkableFacilities.Add(def);
									parentFacility.linkableBuildings.Add(item2);
								}
							}
						}
					}
				}
			}
		});
	}

	public static bool AreFacilitiesEquivalent(ThingDef currentlyLinkedFacility, ThingDef newFacility)
	{
		if (currentlyLinkedFacility == newFacility)
		{
			return true;
		}
		FacilityExtension modExtension = ((Def)newFacility).GetModExtension<FacilityExtension>();
		if (modExtension?.equivalentToFacility != null && modExtension.equivalentToFacility == currentlyLinkedFacility)
		{
			return true;
		}
		FacilityExtension modExtension2 = ((Def)currentlyLinkedFacility).GetModExtension<FacilityExtension>();
		if (modExtension2?.equivalentToFacility != null)
		{
			if (modExtension2.equivalentToFacility == newFacility)
			{
				return true;
			}
			if (modExtension2.equivalentToFacility == modExtension?.equivalentToFacility)
			{
				return true;
			}
		}
		return false;
	}
}
