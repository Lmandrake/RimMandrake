using Verse;

namespace BigAndSmall;

public interface IResourcePool
{
	Pawn Pawn { get; }

	string Label { get; }

	float TargetValue { get; set; }

	float Value { get; set; }

	float Max { get; set; }

	float ValueForDisplay { get; }

	float MaxForDisplay { get; }

	int Increments { get; }

	float ValuePercent { get; }

	void SetTargetValuePct(float value);
}
