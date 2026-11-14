FadedMaterialPool.FadedVersionOf(mat,a) sets an ABSOLUTE alpha, so vanilla's pulsing overlay (NeedsPower/PowerOff) re-fades whatever material we pre-faded and our depth fade is lost: patch every OverlayDrawer.Render*(Thing) to set the fade and swap the material in DrawBatch.DrawMesh.
item: RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE
home: src/RimMandrake/FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs
