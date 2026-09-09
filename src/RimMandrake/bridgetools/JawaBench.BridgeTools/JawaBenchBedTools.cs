// JawaBenchBedTools.cs - PITCELL_PRISONER_BED_BRIDGE_GAP_1.
//
// WHY THIS EXISTS
// ===============
// Nothing on this bridge could put an eligible PRISONER on a fresh test map, so
// PitCell's prisoner-intake gizmos (RM_PlaceInPitCell, RM_FeedCaptive, the
// assign-nearest and gate toggles) could not be exercised end to end without a
// human clicking. The chain that blocks it:
//
//   Verse/DebugToolsPawns.cs  AddGuest(GuestStatus.Prisoner) walks
//     Find.CurrentMap.listerBuildings.AllBuildingsColonistOfClass<Building_Bed>()
//     and SKIPS every bed for which !bed.ForPrisoners. On a fresh map no bed is
//     a prisoner bed, so the debug action iterates, matches nothing, and returns
//     having done nothing at all - the exact silent-success class this bridge
//     exists to expose.
//
//   RimWorld/Building_Bed.cs  ForPrisoners / ForOwnerType are PUBLIC SETTABLE
//     properties, but in game the only thing that writes them is the bed's own
//     Command_SetBedOwnerType / Command_Toggle gizmo, which the bridge cannot
//     click. There is no debug-menu leaf for it either.
//
// This tool writes the property directly, which is the whole point.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   RimWorld/Building_Bed.cs   BedOwnerType ForOwnerType  { get; set; }  - setter
//                              runs RemoveAllOwners(), writes forOwnerType,
//                              Notify_ColorChanged(), NotifyRoomBedTypeChanged().
//                              It is SILENT on refusal: the whole body is inside
//                              `if (value != forOwnerType && def.building
//                              .bed_humanlike && !ForHumanBabies && (value !=
//                              BedOwnerType.Slave || ModLister.CheckIdeology
//                              ("Slavery")))`, so a non-humanlike bed, a crib, or
//                              Slave without Ideology writes nothing and says
//                              nothing. Every one of those is checked and
//                              REPORTED here instead.
//   RimWorld/Building_Bed.cs   bool ForPrisoners { get; set; } - the set half is
//                              deliberately NOT used: setting it false Log.Errors
//                              ("should it be for colonists or slaves?") because
//                              it cannot express the three-way. ForOwnerType is
//                              the honest API; ForPrisoners is reported as a
//                              read-back.
//   RimWorld/Building_Bed.cs   bool Medical { get; set; } - same silent-refusal
//                              shape (a true write no-ops unless
//                              def.building.bed_canBeMedical).
//   Verse/Thing.cs             Notify_ColorChanged() - nulls graphicInt and, IF
//                              SPAWNED, dirties the Things mesh. Called by the
//                              setter itself, so no manual refresh is owed here.
//   Verse/Room.cs              IsPrisonCell, TouchesMapEdge - reported so a
//                              caller can see what the gizmo path would have
//                              enforced and this path deliberately does not.
//
// 🔴 THE BYPASS, STATED PLAINLY: Building_Bed.SetBedOwnerTypeByInterface (the
// gizmo path) does room-wide propagation and REFUSES to make a bed a prisoner
// bed when its room touches the map edge. Writing ForOwnerType directly skips
// all of that - which is what makes a bare quicktest bed usable as a prisoner
// bed, and also means the caller owns the consequences. The room flags are in
// the result so the difference is visible rather than assumed.
//
// GATING: ungated. This edits one building the caller named; it does not hand
// the world permission to act on the player. Same tier as jawa/set_thing_props.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // Is this bed one of the beds DebugToolsPawns.AddGuest would even look at,
        // and would it accept it? Returns the blockers, empty meaning eligible.
        // ⚠️ AnyUnownedSleepingSlot Log.Warnings on a medical bed, so it is only
        // reached on the same branch the engine reaches it on.
        private static List<string> BedPrisonerIntakeBlockers(Building_Bed bed, Map map)
        {
            var blockers = new List<string>();
            if (!bed.Spawned || bed.Map != map)
                blockers.Add("bed is not spawned on the current map (AddGuest only walks the current map's lister)");
            else if (!map.listerBuildings.AllBuildingsColonistOfClass<Building_Bed>().Contains(bed))
                blockers.Add("bed is not in listerBuildings.allBuildingsColonist - AddGuest never sees it. Faction is "
                             + (bed.Faction != null ? bed.Faction.Name : "null") + "; it must be the player faction.");
            if (!bed.ForPrisoners)
                blockers.Add("ForOwnerType is " + bed.ForOwnerType + ", not Prisoner - AddGuest(GuestStatus.Prisoner) skips it.");
            if (bed.OwnersForReading.Any() && !bed.Medical && !bed.AnyUnownedSleepingSlot)
                blockers.Add("every sleeping slot is already owned (" + bed.OwnersForReading.Count + " owner(s)).");
            return blockers;
        }

        private static object BedRow(Building_Bed bed, Map map)
        {
            var room = bed.Spawned ? bed.GetRoom() : null;
            return new
            {
                thingId = bed.ThingID,
                label = bed.LabelCap,
                def = bed.def.defName,
                pos = bed.Spawned ? new { x = bed.Position.x, z = bed.Position.z } : null,
                ownerType = bed.ForOwnerType.ToString(),
                forPrisoners = bed.ForPrisoners,
                medical = bed.Medical,
                bedHumanlike = bed.def.building != null && bed.def.building.bed_humanlike,
                forHumanBabies = bed.ForHumanBabies,
                faction = bed.Faction != null ? bed.Faction.Name : null,
                owners = bed.OwnersForReading.Count,
                sleepingSlots = bed.SleepingSlotsCount,
                roomIsPrisonCell = room != null ? (bool?)room.IsPrisonCell : null,
                roomTouchesMapEdge = room != null ? (bool?)room.TouchesMapEdge : null,
                prisonerIntakeBlockers = BedPrisonerIntakeBlockers(bed, map)
            };
        }

        [Tool(
            "jawa/set_bed_owner_type",
            Description =
                "Force a spawned Building_Bed to Colonist/Prisoner/Slave by writing " +
                "Building_Bed.ForOwnerType directly - the property the in-game gizmo writes, " +
                "which the bridge cannot click. This is what makes vanilla's own 'Add Prisoner' " +
                "debug action work on a fresh quicktest map: it walks the current map's colonist " +
                "beds and skips every bed whose ForPrisoners is false, matching nothing and " +
                "reporting nothing. Build a bed with jawa/build_batch (faction must end up the " +
                "player's), point this at it, then run the debug action or set status directly " +
                "with jawa/pawn_set_guest_status. " +
                "🔴 BYPASSES THE GIZMO'S ROOM RULES: the interface path propagates the change " +
                "across the room and refuses Prisoner when the room touches the map edge; the " +
                "raw property does neither, so a bare bed in open air CAN be a prisoner bed. " +
                "roomIsPrisonCell and roomTouchesMapEdge are returned so that is visible. " +
                "REFUSES, rather than silently no-opping the way the setter does, when: no " +
                "current map; the thing is not a Building_Bed; the bed is not spawned; the game " +
                "is not in ProgramState.Playing; def.building.bed_humanlike is false (animal " +
                "bed); ForHumanBabies is true (crib); ownerType=Slave without Ideology; or " +
                "medical=true on a bed whose def.building.bed_canBeMedical is false. " +
                "⚠️ ANY successful ownerType or medical change calls RemoveAllOwners() first - " +
                "every pawn assigned to the bed is unclaimed and gets a message. ownersBefore " +
                "reports how many that was. " +
                "Call with no 'thing' to get a census of every bed on the current map instead " +
                "of writing anything - that census is the instrument for 'why did Add Prisoner " +
                "do nothing', since it returns prisonerIntakeBlockers per bed.",
            ResultDescription =
                "mode ('set' or 'census'). For set: success, thingId, label, ownerTypeBefore, " +
                "ownerTypeAfter (read back from ForOwnerType, the raw field, not from what was " +
                "asked for), forPrisonersAfter, medicalBefore, medicalAfter, changed[] (which of " +
                "ownerType/medical were actually written), ownersBefore (owners unclaimed by the " +
                "write), faction, roomIsPrisonCell, roomTouchesMapEdge, prisonerIntakeBlockers[] " +
                "(EMPTY means vanilla's Add Prisoner debug action will now use this bed), " +
                "ticksGame. For census: bedCount, beds[] of the same per-bed fields, truncated.")]
        public static async Task<object> SetBedOwnerType(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Bed thing id (as reported by jawa/list_things, with or without the 'Thing_' prefix). Omit for a census of every bed on the current map.")]
            string thing = null,
            [ToolParameter(Description = "BedOwnerType: Colonist, Prisoner or Slave. Omit to leave unchanged (a read-back).")]
            string ownerType = null,
            [ToolParameter(Description = "'true'/'false' to set the bed's Medical flag. Omit to leave unchanged. A prisoner bed must be non-medical for a pawn to own it.")]
            string medical = null,
            [ToolParameter(Description = "Census only: max beds to return (default 100).")]
            int limit = 0)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();

                string err;
                var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                // ---- census mode ------------------------------------------------
                if (string.IsNullOrWhiteSpace(thing))
                {
                    var all = map.listerThings.AllThings.OfType<Building_Bed>().ToList();
                    int cap = limit > 0 ? limit : 100;
                    var rows = new List<object>();
                    foreach (var b in all.Take(cap)) rows.Add(BedRow(b, map));
                    return new
                    {
                        success = true,
                        mode = "census",
                        bedCount = all.Count,
                        truncated = all.Count > cap,
                        beds = rows,
                        ticksGame = TicksGameSafe()
                    };
                }

                // ---- set mode ---------------------------------------------------
                var t = FindLiveThingById(thing, out err);
                if (t == null) return Fail(err);
                var bed = t as Building_Bed;
                if (bed == null)
                    return Fail("Thing '" + t.LabelCap + "' (" + t.def.defName + ") is a " + t.GetType().Name +
                                ", not a Building_Bed. Call with no 'thing' for a census of the beds on this map.");
                if (!bed.Spawned)
                    return Fail("Bed '" + bed.LabelCap + "' is not spawned (minified or in a container). " +
                                "Place it first: AddGuest only walks spawned colonist buildings.");
                if (Current.ProgramState != ProgramState.Playing)
                    return Fail("Game is in ProgramState." + Current.ProgramState + ", not Playing. The bed owner-type " +
                                "write unclaims owners and notifies the room, both of which assume a live map.");

                bool wantsWrite = !string.IsNullOrWhiteSpace(ownerType) || !string.IsNullOrWhiteSpace(medical);

                BedOwnerType target = bed.ForOwnerType;
                if (!string.IsNullOrWhiteSpace(ownerType))
                {
                    // Enum.TryParse also accepts a raw number ("7" parses), which would be
                    // scribed straight into forOwnerType and throw in GetInspectString.
                    if (!Enum.TryParse(ownerType.Trim(), true, out target) ||
                        !Enum.IsDefined(typeof(BedOwnerType), target))
                        return Fail("'" + ownerType + "' is not a BedOwnerType. Accepted: " +
                                    string.Join(", ", Enum.GetNames(typeof(BedOwnerType))));

                    // Each of these is a SILENT no-op inside the setter. Refuse loudly instead.
                    if (bed.def.building == null || !bed.def.building.bed_humanlike)
                        return Fail("'" + bed.def.defName + "' is not a humanlike bed (def.building.bed_humanlike is " +
                                    "false) - the ForOwnerType setter would write nothing and report nothing.");
                    if (bed.ForHumanBabies)
                        return Fail("'" + bed.def.defName + "' is a baby bed (bed_maxBodySize " +
                                    bed.def.building.bed_maxBodySize + " < child body size) - the ForOwnerType " +
                                    "setter refuses cribs silently.");
                    if (target == BedOwnerType.Slave && !ModsConfig.IdeologyActive)
                        return Fail("ownerType=Slave needs the Ideology DLC active (the setter calls " +
                                    "ModLister.CheckIdeology, which Log.Errors and refuses without it).");
                }

                bool? targetMedical = null;
                if (!string.IsNullOrWhiteSpace(medical))
                {
                    bool mv;
                    if (!bool.TryParse(medical.Trim(), out mv))
                        return Fail("medical must be 'true' or 'false', got '" + medical + "'.");
                    if (mv && (bed.def.building == null || !bed.def.building.bed_canBeMedical))
                        return Fail("'" + bed.def.defName + "' cannot be a medical bed " +
                                    "(def.building.bed_canBeMedical is false) - the Medical setter no-ops silently.");
                    targetMedical = mv;
                }

                var ownerTypeBefore = bed.ForOwnerType;
                bool medicalBefore = bed.Medical;
                int ownersBefore = bed.OwnersForReading.Count;
                var changed = new List<string>();

                try
                {
                    if (targetMedical.HasValue && targetMedical.Value != medicalBefore)
                        bed.Medical = targetMedical.Value;
                    if (!string.IsNullOrWhiteSpace(ownerType) && target != ownerTypeBefore)
                        bed.ForOwnerType = target;
                }
                catch (Exception e)
                {
                    return Fail("Writing the bed flags threw " + e.GetType().Name + ": " + e.Message,
                                new { ownerTypeAfter = bed.ForOwnerType.ToString(), medicalAfter = bed.Medical });
                }

                // Read back the raw property, never the value that was asked for.
                if (bed.ForOwnerType != ownerTypeBefore) changed.Add("ownerType");
                if (bed.Medical != medicalBefore) changed.Add("medical");

                // An empty changed[] on a write is NOT a silent refusal here - every
                // refusal path above returned already - so it is reported as
                // alreadyInRequestedState rather than left to look like one.
                var room = bed.GetRoom();
                return new
                {
                    success = true,
                    mode = wantsWrite ? "set" : "read",
                    thingId = bed.ThingID,
                    label = bed.LabelCap,
                    def = bed.def.defName,
                    ownerTypeBefore = ownerTypeBefore.ToString(),
                    ownerTypeAfter = bed.ForOwnerType.ToString(),
                    forPrisonersAfter = bed.ForPrisoners,
                    medicalBefore,
                    medicalAfter = bed.Medical,
                    changed,
                    alreadyInRequestedState = wantsWrite && changed.Count == 0,
                    ownersBefore,
                    ownersAfter = bed.OwnersForReading.Count,
                    faction = bed.Faction != null ? bed.Faction.Name : null,
                    roomIsPrisonCell = room != null ? (bool?)room.IsPrisonCell : null,
                    roomTouchesMapEdge = room != null ? (bool?)room.TouchesMapEdge : null,
                    prisonerIntakeBlockers = BedPrisonerIntakeBlockers(bed, map),
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
