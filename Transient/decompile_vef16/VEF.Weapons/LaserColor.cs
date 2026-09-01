using RimWorld;
using Verse;

namespace VEF.Weapons;

public class LaserColor
{
	private static LaserColor[] colors = new LaserColor[7]
	{
		new LaserColor
		{
			index = 0,
			name = "RimlaserBeamBrown"
		},
		new LaserColor
		{
			index = 1,
			name = "RimlaserBeamOrange"
		},
		new LaserColor
		{
			index = 2,
			name = "RimlaserBeamRed"
		},
		new LaserColor
		{
			index = 3,
			name = "RimlaserBeamPink"
		},
		new LaserColor
		{
			index = 4,
			name = "RimlaserBeamBlue"
		},
		new LaserColor
		{
			index = 5,
			name = "RimlaserBeamTeal"
		},
		new LaserColor
		{
			index = 6,
			name = "RimlaserBeamRedBlack",
			allowed = false
		}
	};

	public int index;

	public string name;

	public bool allowed = true;

	internal static int IndexBasedOnThingQuality(int index, Thing gun)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Expected I4, but got Unknown
		if (index != -1)
		{
			return index;
		}
		QualityCategory val = default(QualityCategory);
		if (QualityUtility.TryGetQuality(gun, ref val))
		{
			switch ((int)val)
			{
			case 0:
				return 0;
			case 1:
				return 1;
			case 2:
				return 2;
			case 3:
				return 3;
			case 4:
				return 4;
			case 5:
				return 5;
			case 6:
				return 6;
			}
		}
		return 2;
	}
}
