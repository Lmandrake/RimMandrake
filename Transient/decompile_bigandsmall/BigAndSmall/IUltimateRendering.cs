using UnityEngine;
using Verse;

namespace BigAndSmall;

public interface IUltimateRendering
{
	PawnRenderNode Base { get; }

	bool ScaleSet { get; set; }

	Vector2 CachedScale { get; set; }

	bool AllowTexPathFor => false;
}
