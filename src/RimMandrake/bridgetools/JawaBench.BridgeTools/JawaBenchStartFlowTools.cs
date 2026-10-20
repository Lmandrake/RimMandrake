// JawaBenchStartFlowTools.cs - drive the NEW-GAME pages without clicking: pick a scenario,
// pick the landing tile, load a .rid ideoligion.
//
// Written 2026-10-20 for the unattended world-remake conductor
// (design/RimMandrake/world_remake_2026-10-19/15_conductor_plan.md S4, S5, S10), which had no
// tool for any of the three and was routing them through OS clicks at guessed rects.
//
// Each tool does what the page's OWN button handler does, read from 1.6 source via RimSage
// (2026-10-20), and nothing the page would not:
//
//   scenario_select   Page_SelectScenario keeps the pick in a PRIVATE field `curScen`; its
//                     row click is `curScen = scen`. Next = CanDoNext() (which itself runs
//                     BeginScenarioConfiguration: new Game, InitData, Scenario, PreConfigure,
//                     stitches GetFirstConfigPage) then Page.DoNext().
//   start_site_select Page_SelectStartingSite reads Find.WorldInterface.SelectedTile every
//                     frame into Find.GameInitData.startingTile. Next = CanDoNext()
//                     (TileFinder.IsValidTileForNewSettlement) then DoNext(), which may pop a
//                     settlement-proximity confirmation (SettlementProximityGoodwillUtility.
//                     CheckConfirmSettle) BEFORE it commits startingTile and opens the next page.
//   ideo_load_rid     Page_ChooseIdeoPreset.DoLoad's returner, step for step:
//                     GameDataSaveLoader.TryLoadIdeo -> IdeoGenerator.InitLoadedIdeo ->
//                     AssignIdeoToPlayer (private) -> IdeoManager.RemoveUnusedStartingIdeos ->
//                     Scenario.PostIdeoChosen -> next.prev = page -> Page.DoNext. classicMode is
//                     set false, as Page_ChooseIdeoPreset.DoNext does for any non-classic pick.
//
// Page order (Scenario.GetFirstConfigPage, 1.6): Storyteller -> CreateWorldParams ->
// SelectStartingSite (absent with ScenPart_ForcedMap) -> ChooseIdeoPreset (Ideology) ->
// the scenario's own config pages (starting pawns). So the ideo page comes AFTER the
// landing site, not before world generation.
//
// Every success is read back from the raw state the page itself reads (curScen, SelectedTile,
// GameInitData.startingTile, Faction.OfPlayer.ideos.PrimaryIdeo) and the window stack after.
// Pure decisions (which scenario a string names, which file a .rid arg names, which candidate
// tile to take) live in JawaBenchStartFlowCore.cs and are unit-tested offline.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Core = JawaBench.BridgeTools.JawaBenchStartFlowCore;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const BindingFlags StartFlowInst = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;

        private static List<string> StartFlowWindows() =>
            Find.WindowStack == null
                ? new List<string>()
                : Find.WindowStack.Windows.Select(w => w.GetType().Name).ToList();

        /// <summary>Page.CanDoNext is protected virtual; reflection Invoke dispatches to the override.</summary>
        private static bool StartFlowCanDoNext(Page page) =>
            (bool)typeof(Page).GetMethod("CanDoNext", StartFlowInst).Invoke(page, null);

        private static void StartFlowDoNext(Page page) =>
            typeof(Page).GetMethod("DoNext", StartFlowInst).Invoke(page, null);

        private static object StartFlowMessageBoxes() =>
            Find.WindowStack.Windows.OfType<Dialog_MessageBox>()
                .Select(d => new { title = d.title, text = d.text.ToString() }).ToList();

        // ================================================================ scenario

        [Tool(
            "jawa/scenario_select",
            Description =
                "NEW GAME, scenario page: select a scenario by ScenarioDef defName (or exact display " +
                "name) on Page_SelectScenario - the same assignment the row click makes - and read the " +
                "page's private pick back. At the main menu (ProgramState Entry) with no scenario page " +
                "open it opens one first, exactly as the New colony button does (openIfAbsent). " +
                "advance=true then presses Next through the page's own CanDoNext/DoNext, which CREATES " +
                "THE NEW Game object and opens the storyteller page; it is read back from " +
                "Current.Game.Scenario. REFUSES: no scenario page and not at the main menu; an unknown " +
                "or ambiguous name (no fuzzy pick - near matches are listed); a scenario hidden from the " +
                "list (showInUI=false), disabled, or flagged invalid (the game would run a version-check " +
                "dialog - do that one by hand). Does not act on a running colony.",
            ResultDescription =
                "success, selected {defName, name, category}, pickReadBack (the page's curScen is the " +
                "same object), advanced, gameScenario (Current.Game.Scenario name when advanced), " +
                "nextPage, windows[] after.")]
        public static async Task<object> ScenarioSelect(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "ScenarioDef defName (e.g. 'Scenario_Utinni'), or the exact name shown in the list.")]
            string scenario = null,
            [ToolParameter(Description = "Press Next after selecting (creates the new Game). Default false.")]
            bool advance = false,
            [ToolParameter(Description = "At the main menu, open the scenario page if none is open. Default true.")]
            bool openIfAbsent = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var page = Find.WindowStack.Windows.OfType<Page_SelectScenario>().FirstOrDefault();
                bool opened = false;
                if (page == null)
                {
                    if (Current.ProgramState != ProgramState.Entry || !openIfAbsent)
                        return Fail("No scenario page is open" +
                                    (Current.ProgramState != ProgramState.Entry ? " and the game is not at the main menu (programState " + Current.ProgramState + ")." : " (openIfAbsent=false)."),
                                    new { windows = StartFlowWindows() });
                    page = new Page_SelectScenario();
                    Find.WindowStack.Add(page);
                    opened = true;
                }

                var defOf = new Dictionary<Scenario, string>();
                foreach (var d in DefDatabase<ScenarioDef>.AllDefs)
                    if (d.scenario != null && !defOf.ContainsKey(d.scenario)) defOf[d.scenario] = d.defName;
                var scens = ScenarioLister.AllScenarios().Where(s => s != null).ToList();
                var entries = scens.Select(s => new Core.ScenarioEntry(
                    defOf.TryGetValue(s, out var dn) ? dn : null, s.name, s.Category.ToString())).ToList();

                int idx = Core.MatchScenario(entries, scenario, out string err);
                if (idx < 0) return Fail(err, new { pageOpenedByThisCall = opened, listed = entries.Count });
                Scenario scen = scens[idx];
                var described = new { defName = entries[idx].DefName, name = entries[idx].Name, category = entries[idx].Category };
                if (!scen.showInUI) return Fail("Scenario " + Core.Describe(entries[idx]) + " is hidden from the list (showInUI=false); the page cannot select it.", described);
                if (!scen.enabled) return Fail("Scenario " + Core.Describe(entries[idx]) + " is disabled (unsubscribed workshop item?).", described);
                if (!scen.valid) return Fail("Scenario " + Core.Describe(entries[idx]) + " is flagged invalid (ScenPart error); the game routes its selection through a version-check dialog. Select it by hand.", described);

                var curField = typeof(Page_SelectScenario).GetField("curScen", StartFlowInst);
                if (curField == null) return Fail("Could not reflect Page_SelectScenario.curScen (game version changed?).");
                curField.SetValue(page, scen);
                bool pickReadBack = ReferenceEquals(curField.GetValue(page), scen);
                if (!pickReadBack) return Fail("Wrote curScen but it reads back as a different scenario.", described);

                if (!advance)
                    return (object)new
                    {
                        success = true, selected = described, pickReadBack, pageOpenedByThisCall = opened,
                        advanced = false, windows = StartFlowWindows(),
                    };

                bool can = StartFlowCanDoNext(page);
                if (!can) return Fail("The page refused Next (CanDoNext false: tutorial gate?). The pick stands.", new { selected = described, windows = StartFlowWindows() });
                var nextPage = page.next;
                StartFlowDoNext(page);
                bool gameHasIt = Current.Game != null && ReferenceEquals(Current.Game.Scenario, scen);
                bool pageClosed = !Find.WindowStack.IsOpen(page);
                bool nextOpen = nextPage != null && Find.WindowStack.IsOpen(nextPage);
                bool ok = gameHasIt && pageClosed && (nextOpen || nextPage == null);
                return (object)new
                {
                    success = ok,
                    message = ok ? null : "Next ran but the read-back disagrees (gameHasScenario=" + gameHasIt + ", pageClosed=" + pageClosed + ", nextOpen=" + nextOpen + ").",
                    selected = described, pickReadBack, pageOpenedByThisCall = opened,
                    advanced = true,
                    gameScenario = Current.Game?.Scenario?.name,
                    nextPage = nextPage?.GetType().Name,
                    windows = StartFlowWindows(),
                };
            });
        }

        // ================================================================ start tile

        [Tool(
            "jawa/start_site_select",
            Description =
                "NEW GAME, landing-site page: select the starting tile on Page_SelectStartingSite by " +
                "SURFACE tile id - sets Find.WorldInterface.SelectedTile (what a click on the globe sets) " +
                "and GameInitData.startingTile (what the page copies it to every frame), optionally " +
                "jumps the world camera there, and reads both back with the tile's biome. tiles may list " +
                "several ids in preference order: the first one TileFinder.IsValidTileForNewSettlement " +
                "accepts is taken, and every skipped one is returned with the game's own reason - never " +
                "a silent substitution. advance=true presses Next through the page's CanDoNext/DoNext; " +
                "if the tile is near another settlement the game opens a CONFIRMATION dialog first and " +
                "this returns success=false with pendingConfirmation (the selection stands; confirm " +
                "with a UI click, or pick a farther tile). REFUSES: page not open; a tile out of range; " +
                "every candidate invalid. Surface layer only.",
            ResultDescription =
                "success, chosen, refused[] {tile, reason}, selectedTileReadBack, startingTileReadBack, " +
                "biome, hilliness, landmark, advanced, pendingConfirmation[] {title,text}, nextPage, windows[].")]
        public static async Task<object> StartSiteSelect(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "Surface tile id, or several comma-separated in preference order (e.g. '17007,1621,17011').")]
            string tiles = null,
            [ToolParameter(Description = "Press Next after selecting. Default false.")]
            bool advance = false,
            [ToolParameter(Description = "Centre the world camera on the chosen tile. Default true.")]
            bool jumpCamera = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var page = Find.WindowStack.Windows.OfType<Page_SelectStartingSite>().FirstOrDefault();
                if (page == null)
                    return Fail("The landing-site page (Page_SelectStartingSite) is not open.", new { programState = Current.ProgramState.ToString(), windows = StartFlowWindows() });
                if (Find.World == null || Find.WorldGrid == null || Find.GameInitData == null)
                    return Fail("No world / GameInitData yet.");

                var candidates = Core.ParseTileList(tiles, out string perr);
                if (candidates == null) return Fail(perr);
                PlanetLayer surface = Find.WorldGrid.Surface;
                int count = surface.TilesCount;
                var pick = Core.PickFirstAcceptable(candidates, id =>
                {
                    if (id >= count) return "out of range: the surface layer has " + count + " tiles (wrong planet subdivision?)";
                    var sb = new StringBuilder();
                    if (!TileFinder.IsValidTileForNewSettlement(new PlanetTile(id, surface), sb))
                        return "game refuses settlement here: " + (sb.Length > 0 ? sb.ToString() : "(no reason given)");
                    return null;
                });
                var refused = pick.Refused.Select(kv => new { tile = kv.Key, reason = kv.Value }).ToList();
                if (pick.Chosen < 0) return Fail("No candidate tile is a valid starting site.", new { refused });

                var pt = new PlanetTile(pick.Chosen, surface);
                Find.WorldSelector.ClearSelection();
                Find.WorldInterface.SelectedTile = pt;
                Find.GameInitData.startingTile = pt;
                if (jumpCamera) Find.WorldCameraDriver.JumpTo(pt);

                PlanetTile sel = Find.WorldInterface.SelectedTile;
                PlanetTile st = Find.GameInitData.startingTile;
                bool selOk = sel.Valid && sel.tileId == pick.Chosen && sel.Layer == surface;
                bool stOk = st.Valid && st.tileId == pick.Chosen && st.Layer == surface;
                Tile tile = pt.Tile;
                var common = new
                {
                    chosen = pick.Chosen, refused,
                    selectedTileReadBack = sel.Valid ? sel.tileId : -1,
                    startingTileReadBack = st.Valid ? st.tileId : -1,
                    biome = tile?.PrimaryBiome?.defName,
                    hilliness = tile?.hilliness.ToString(),
                    landmark = tile?.Landmark?.name,
                };
                if (!selOk || !stOk) return Fail("Selection did not read back (selected=" + common.selectedTileReadBack + ", startingTile=" + common.startingTileReadBack + ").", common);

                if (!advance)
                    return (object)new { success = true, common.chosen, common.refused, common.selectedTileReadBack, common.startingTileReadBack, common.biome, common.hilliness, common.landmark, advanced = false, windows = StartFlowWindows() };

                if (!StartFlowCanDoNext(page))
                    return Fail("The page refused Next (CanDoNext false; tutorial gate or a validity rule this tool did not pre-check). Selection stands.", common);
                var nextPage = page.next;
                StartFlowDoNext(page);
                bool pageClosed = !Find.WindowStack.IsOpen(page);
                bool nextOpen = nextPage != null && Find.WindowStack.IsOpen(nextPage);
                var boxes = Find.WindowStack.Windows.OfType<Dialog_MessageBox>().ToList();
                if (!pageClosed && boxes.Count > 0)
                    return Fail("A confirmation dialog is open (settlement proximity); the landing is NOT committed yet. Confirm it with a UI click or choose a farther tile.",
                        new { common, pendingConfirmation = StartFlowMessageBoxes(), windows = StartFlowWindows() });
                bool committed = Find.GameInitData.startingTile.Valid && Find.GameInitData.startingTile.tileId == pick.Chosen;
                bool ok = pageClosed && committed && (nextOpen || nextPage == null);
                return (object)new
                {
                    success = ok,
                    message = ok ? null : "Next ran but the read-back disagrees (pageClosed=" + pageClosed + ", startingTileCommitted=" + committed + ", nextOpen=" + nextOpen + ").",
                    common.chosen, common.refused, common.selectedTileReadBack,
                    startingTileReadBack = Find.GameInitData.startingTile.Valid ? Find.GameInitData.startingTile.tileId : -1,
                    common.biome, common.hilliness, common.landmark,
                    advanced = true, nextPage = nextPage?.GetType().Name, windows = StartFlowWindows(),
                };
            });
        }

        // ================================================================ .rid ideoligion

        [Tool(
            "jawa/ideo_load_rid",
            Description =
                "Load a saved ideoligion (.rid) file. TWO MODES, chosen by game state: (1) NEW GAME, " +
                "Page_ChooseIdeoPreset open: does what that page's Load button does after the file " +
                "dialog - loads, gives it a fresh id, makes it the player's primary and initial ideo, " +
                "drops unused starting ideos, runs Scenario.PostIdeoChosen, sets classicMode=false, and " +
                "ADVANCES to the next page (the page would otherwise still hold its Classic default and " +
                "override the load on Next). (2) RUNNING GAME (Playing): adds the ideo to the IdeoManager " +
                "and, with setPlayerPrimary=true, makes it the player faction's primary - EXISTING " +
                "COLONISTS KEEP THEIR OWN IDEO (convert them with the pawn ideo tools); in a classic-mode " +
                "save the ideo loads but ideology mechanics stay off (classicMode is read back, not " +
                "changed). path: absolute Windows path, a /mnt/<drive>/ path, or a bare name in the " +
                "game's Ideos folder. dryRun=true loads and describes the file without registering " +
                "anything. REFUSES: missing file, non-.rid, a load failure (the game's own " +
                "'Exception loading ideo' goes to Player.log), an ideo of the same name already present " +
                "(allowDuplicateName), neither the ideo page nor a running game.",
            ResultDescription =
                "success, mode (page|playing), path, ideo {id, name, memes[], preceptCount, culture}, " +
                "isPlayerPrimary, initialPlayerIdeo, inIdeoManager, classicMode, playerIdeos[], " +
                "nextPage, windows[].")]
        public static async Task<object> IdeoLoadRid(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "The .rid: absolute Windows path (D:\\...\\The Salvation.rid), /mnt/d/... path, or bare name ('The Salvation') in the game's Ideos folder.")]
            string path = null,
            [ToolParameter(Description = "Running-game mode only: make it the player faction's primary ideo. Default true. (Page mode always does.)")]
            bool setPlayerPrimary = true,
            [ToolParameter(Description = "Load an ideo even if one with the same name exists. Default false.")]
            bool allowDuplicateName = false,
            [ToolParameter(Description = "Load and describe the file only; register nothing, advance nothing. Default false.")]
            bool dryRun = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string abs = Core.ResolveRidPath(path, GenFilePaths.AbsPathForIdeo, out string perr);
                if (abs == null) return Fail(perr);
                if (!File.Exists(abs)) return Fail("No file at '" + abs + "'.");

                var page = Find.WindowStack.Windows.OfType<Page_ChooseIdeoPreset>().FirstOrDefault();
                string mode = page != null ? "page" : (Current.ProgramState == ProgramState.Playing ? "playing" : null);
                if (mode == null)
                    return Fail("Neither the ideoligion page (Page_ChooseIdeoPreset) is open nor a game running (programState " + Current.ProgramState + ").", new { windows = StartFlowWindows() });
                if (Find.IdeoManager == null || Faction.OfPlayer == null || Faction.OfPlayer.ideos == null)
                    return Fail("No IdeoManager / player faction ideos (Ideology inactive?).");

                if (!GameDataSaveLoader.TryLoadIdeo(abs, out Ideo ideo) || ideo == null)
                    return Fail("The game could not load '" + abs + "' (TryLoadIdeo false; see Player.log 'Exception loading ideo').");

                var clash = Find.IdeoManager.IdeosListForReading.FirstOrDefault(i => i != null && i.name == ideo.name);
                if (clash != null && !allowDuplicateName)
                    return Fail("An ideoligion named '" + ideo.name + "' is already present (id " + clash.id + "). Pass allowDuplicateName=true to load a second.");

                object Describe(Ideo i) => new
                {
                    id = i.id, name = i.name,
                    memes = i.memes?.Select(m => m.defName).ToList(),
                    preceptCount = i.PreceptsListForReading?.Count ?? -1,
                    culture = i.culture?.defName,
                };

                if (dryRun)
                    return (object)new { success = true, dryRun = true, mode, path = abs, ideo = Describe(ideo), wouldAdvance = mode == "page", note = "id is the file's, not yet reassigned" };

                ideo = IdeoGenerator.InitLoadedIdeo(ideo);
                Page next = null;
                if (mode == "page")
                {
                    Find.IdeoManager.classicMode = false;
                    var assign = typeof(Page_ChooseIdeoPreset).GetMethod("AssignIdeoToPlayer", StartFlowInst);
                    if (assign == null) return Fail("Could not reflect Page_ChooseIdeoPreset.AssignIdeoToPlayer (game version changed?). Nothing registered.");
                    assign.Invoke(page, new object[] { ideo });
                    Find.IdeoManager.RemoveUnusedStartingIdeos();
                    Find.Scenario.PostIdeoChosen();
                    next = page.next;
                    if (next != null) next.prev = page;
                    typeof(Page_ChooseIdeoPreset).GetMethod("ResetSelection", StartFlowInst)?.Invoke(page, null);
                    // Page.DoNext's body, non-virtually (the page's override would re-dispatch on its
                    // Classic selection): open next, run nextAct, tutor events, close.
                    if (next != null) Find.WindowStack.Add(next);
                    page.nextAct?.Invoke();
                    TutorSystem.Notify_Event("PageClosed");
                    TutorSystem.Notify_Event("GoToNextPage");
                    page.Close();
                }
                else
                {
                    Find.IdeoManager.Add(ideo);
                    if (setPlayerPrimary) Faction.OfPlayer.ideos.SetPrimary(ideo);
                }

                bool inMgr = Find.IdeoManager.IdeosListForReading.Contains(ideo);
                bool isPrimary = ReferenceEquals(Faction.OfPlayer.ideos.PrimaryIdeo, ideo);
                bool wantPrimary = mode == "page" || setPlayerPrimary;
                bool pageClosed = page == null || !Find.WindowStack.IsOpen(page);
                bool nextOpen = next == null || Find.WindowStack.IsOpen(next);
                bool ok = inMgr && (!wantPrimary || isPrimary) && (mode != "page" || (pageClosed && nextOpen && !Find.IdeoManager.classicMode));
                return (object)new
                {
                    success = ok,
                    message = ok ? null : "Read-back disagrees (inIdeoManager=" + inMgr + ", isPlayerPrimary=" + isPrimary + ", pageClosed=" + pageClosed + ", nextOpen=" + nextOpen + ", classicMode=" + Find.IdeoManager.classicMode + ").",
                    mode, path = abs, ideo = Describe(ideo),
                    isPlayerPrimary = isPrimary, initialPlayerIdeo = ideo.initialPlayerIdeo,
                    inIdeoManager = inMgr, classicMode = Find.IdeoManager.classicMode,
                    playerIdeos = Faction.OfPlayer.ideos.AllIdeos.Select(i => i.name).ToList(),
                    nextPage = next?.GetType().Name,
                    windows = StartFlowWindows(),
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
