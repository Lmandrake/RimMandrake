using RimWorld;
using Verse;

namespace VEF.Buildings;

public class StudiableBuildingDetails : DefModExtension
{
	public ThingDef buildingLeft;

	public SoundDef deconstructSound;

	public string gizmoTexture;

	public string gizmoText;

	public string gizmoDesc;

	public bool craftingInspiration;

	public SkillDef skillForStudying;

	public string overlayTexture;

	public bool showProgressBar;

	public bool showResearchEffecter = true;
}
