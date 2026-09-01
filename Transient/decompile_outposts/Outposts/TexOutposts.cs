using UnityEngine;
using Verse;

namespace Outposts;

[StaticConstructorOnStartup]
public static class TexOutposts
{
	public static readonly Texture2D PackTex = ContentFinder<Texture2D>.Get("UI/Gizmo/AbandonOutpost", true);

	public static readonly Texture2D AddTex = ContentFinder<Texture2D>.Get("UI/Gizmo/AddToOutpost", true);

	public static readonly Texture2D RemoveTex = ContentFinder<Texture2D>.Get("UI/Gizmo/RemovePawnFromOutpost", true);

	public static readonly Texture2D StopPackTex = ContentFinder<Texture2D>.Get("UI/Gizmo/CancelAbandonOutpost", true);

	public static readonly Texture2D RemoveItemsTex = ContentFinder<Texture2D>.Get("UI/Gizmo/RemoveItemsFromOutpost", true);

	public static readonly Texture2D CreateTex = ContentFinder<Texture2D>.Get("UI/Gizmo/SetUpOutpost", true);
}
