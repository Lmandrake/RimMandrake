using UnityEngine;

namespace BigAndSmall;

public interface IRacialFeature
{
	string Label { get; }

	string DescriptionFull { get; }

	Texture2D Icon { get; }

	Color IconColor { get; }
}
