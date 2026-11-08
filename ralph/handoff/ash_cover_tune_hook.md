# Live tuning hook for SectionLayer_PyrelandsAsh (pass 20; NOT committed in the source, paste it in to tune, remove before commit)

Why: each look change otherwise costs a 4-minute restart. With this, `jawa/static_call` retunes the cover live and redraws the map.
1. Make the constants static fields (Sub, EdgeBand, Spacing1/2, Amp1/2, Tint via mat.color, DepthAlpha already static), and add
   `private static int version; private int builtVersion = -1;` In Regenerate, before the "rebuild only on a change" return:
   `if (builtVersion != version) { foreach (LayerSubMesh o in subMeshes) if (o.material != Mat) { o.Clear(MeshParts.All); o.disabled = true; } }`
   and make the return `if (builtVersion == version && ...same...) return; builtVersion = version;`
2. Add a public static string Tune(string spec): split "k=v;k=v"; keys: tex|add (absolute png -> _MainTex|_AlphaAddTex via a
   Texture2D.LoadImage, wrap Repeat, Trilinear, Apply(true,false)), color=r,g,b, band, a1, a2, s1, s2 (spacings MUST divide 96:
   s1=10 threw and blanked the layer), d1..d4, queue, shader=rough|fade|hard|snow (new Material(shader), copy mainTexture and
   MatBases.Snow's _AlphaAddTex). Then `noise = null` when a/s change, `version++`,
   `Find.CurrentMap?.mapDrawer.WholeMapChanged(MapMeshFlagDefOf.Things)`.
3. LoadImage needs `<Reference Include="UnityEngine.ImageConversionModule">` in FireEcologyHook.csproj (same HintPath pattern as
   CoreModule). Remove it with the hook.
4. Call: `python.exe src/RimMandrake/Utils/rimbridge_client.py --yes-i-know-this-is-live --call jawa/static_call --json
   '{"type":"RimMandrake.Pyrelands.SectionLayer_PyrelandsAsh","method":"Tune","args":"color=0.56,0.56,0.55;band=0.18"}'`
   or `Transient/pyre_play10/tune.py NAME "SPEC" [X Z RS]` (tune then capture to shots/NAME.png).
Candidate textures used in the session: D:\ClaudeWork\rimmandrake\ralph_pyrelands\ashtune\ (main_soft, main_fine, add_mid,
add_grain, macro_flat; snowmat_* are vanilla's snow textures dumped).
