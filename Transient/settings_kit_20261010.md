# SETTINGS_SCREEN_KIT_1 - A5 fix 2026-10-10
Cause: A5 failed honestly. The kit Draw() existed but FlowWorks drew only the reset button; no search box, no collapsible sections (item note + belt_g screenshot).
Fix: RimMandrakeFlowWorksMod.cs - 12 sections now go through Section(): collapsible header, kit reset button, kit search box (matches section title or setting names, case-insensitive via SettingsKitCore.Matches; a search opens matching sections). Scroll height now measured (collapsing no longer leaves blank space; first frame 11600).
Offline: winbuild FlowWorks succeeds (0 warn / 0 err). A5 is L1 -> live look owed (rimflow verify after a game screenshot).
Limit: search matches title + field names, not tooltip text.
