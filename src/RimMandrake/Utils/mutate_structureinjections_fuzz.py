#!/usr/bin/env python3
"""Mutation proof for the StructureInjections fuzz: plants each defect in the kernel (RM_PlanKernel.cs) and the plan reader (RimplacePlan.cs),
demands the fuzz FAILS, restores each file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_structureinjections_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/StructureInjections/Source/Kernel/RM_PlanKernel.cs"
PLAN = "src/RimMandrake/StructureInjections/Source/RimplacePlan.cs"
KERNEL_MUTATIONS = [
    ("offset ignores the footprint origin", "int pcx = fx + fw / 2, pcz = fz + fh / 2;", "int pcx = fw / 2, pcz = fh / 2;"),
    ("offset centre uses the full width", "int pcx = fx + fw / 2, pcz = fz + fh / 2;", "int pcx = fx + fw, pcz = fz + fh / 2;"),
    ("offset drops the explicit offset on an anchor", "dx = anchorX - pcx + offsetX; dz = anchorZ - pcz + offsetZ;", "dx = anchorX - pcx; dz = anchorZ - pcz;"),
    ("offset drops the explicit offset on the map centre", "dx = mapCenterX - pcx + offsetX; dz = mapCenterZ - pcz + offsetZ;", "dx = mapCenterX - pcx; dz = mapCenterZ - pcz;"),
    ("centring beats the anchor", "if (hasAnchor) { dx = anchorX", "if (hasAnchor && !centerOnMap) { dx = anchorX"),
    ("centring ignores its switch", "else if (centerOnMap) {", "else {"),
    ("no footprint still moves the plan", "if (!hasFootprint) return;", ""),
    ("x and z swapped on the anchor", "dx = anchorX - pcx + offsetX; dz = anchorZ - pcz + offsetZ;", "dx = anchorZ - pcx + offsetX; dz = anchorX - pcz + offsetZ;"),
    ("direction accepts a substring", "if (dir == null || dir.Length != 1) return -1;", "if (dir == null) return -1; if (dir.Length != 1) return \"NESW\".IndexOf(dir, StringComparison.Ordinal);"),
    ("direction accepts empty", "if (dir == null || dir.Length != 1) return -1;", "if (dir == null) return -1; if (dir.Length == 0) return 0;"),
    ("direction is case-insensitive", 'return "NESW".IndexOf(dir[0]);', 'return "NESW".IndexOf(char.ToUpperInvariant(dir[0]));'),
    ("north steps south", "case 0: sz = 1; break;", "case 0: sz = -1; break;"),
    ("east steps west", "case 1: sx = 1; break;", "case 1: sx = -1; break;"),
    ("bad direction steps nowhere", 'default: throw new ArgumentOutOfRangeException("dirIndex");', "default: break;"),
    ("unknown clear mode reads as all", "return ClearMode.Unknown;\n        }\n\n        public enum PawnState", "return ClearMode.All;\n        }\n\n        public enum PawnState"),
    ("clear mode case-insensitive", 'if (mode == "all") return ClearMode.All;', 'if (mode != null && mode.ToLowerInvariant() == "all") return ClearMode.All;'),
    ("a typo'd pawn state kills the pawn", "default: return PawnState.Unknown;", "default: return PawnState.Dead;"),
    ("skeleton is its own state", 'case "dessicated":\n                case "skeleton": return PawnState.Dessicated;', 'case "dessicated": return PawnState.Dessicated;\n                case "skeleton": return PawnState.Unknown;'),
    ("dead pawns stay alive", 'case "dead": return PawnState.Dead;', 'case "dead": return PawnState.Alive;'),
    ("a colonist may be spawned", 'if (faction == "player") return FactionKind.Refused;', ""),
    ("blank faction names a def", 'if (string.IsNullOrEmpty(faction) || faction == "wild") return FactionKind.Wild;', 'if (faction == "wild") return FactionKind.Wild;'),
    ("player check is case-insensitive", 'if (faction == "player") return FactionKind.Refused;', 'if (faction != null && faction.ToLowerInvariant() == "player") return FactionKind.Refused;'),
    ("run steps past a blocker", "if (p == RunProbe.Blocked) break;", ""),
    ("run places over an existing run", "if (p == RunProbe.Free) place(x, z);", "place(x, z);"),
    ("run never places", "if (p == RunProbe.Free) place(x, z);", ""),
    ("run leaves the map on the far edge", "x < width && z < height", "x <= width && z < height"),
    ("run leaves the map on the near edge", "x >= 0 && z >= 0 &&", "x >= -1 && z >= 0 &&"),
    ("run counts the blocker as walked", "if (p == RunProbe.Blocked) break;\n                if (p == RunProbe.Free) place(x, z);\n                walked++;", "if (p == RunProbe.Free) place(x, z);\n                walked++;\n                if (p == RunProbe.Blocked) break;"),
    ("transmitters last", "(transmits(t) ? first : rest).Add(t);", "(transmits(t) ? rest : first).Add(t);"),
    ("transmitters reversed", "(transmits(t) ? first : rest).Add(t);", "if (transmits(t)) first.Insert(0, t); else rest.Add(t);"),
    ("rest dropped", "first.AddRange(rest);", ""),
]
PLAN_MUTATIONS = [
    ("blank lines parsed as directives", "if (line.Length == 0 || line[0] == '#') return;", "if (line[0] == '#') return;"),
    ("comments parsed as directives", "if (line.Length == 0 || line[0] == '#') return;", "if (line.Length == 0) return;"),
    ("trailing whitespace kept", "var line = raw.TrimEnd();", "var line = raw;"),
    ("first footprint wins", "plan.HasFootprint = true;", "plan.HasFootprint = plan.HasFootprint || true; if (plan.FootprintW != 0) return;"),
    ("thing stuff dash kept", 'Stuff = f[5] == "-" ? null : f[5],\n                        });\n                        break;\n                    case "RUN":', 'Stuff = f[5],\n                        });\n                        break;\n                    case "RUN":'),
    ("thing x and z swapped", "X = int.Parse(f[2]),\n                            Z = int.Parse(f[3]),\n                            Rot", "X = int.Parse(f[3]),\n                            Z = int.Parse(f[2]),\n                            Rot"),
    ("run dir and def swapped", "Dir = f[3],\n                            DefName = f[4],", "Dir = f[4],\n                            DefName = f[3],"),
    ("clear mode dropped", "Mode = f[5],", ""),
    ("pawn faction and state swapped", "Faction = f[4],\n                            State = f[5],", "Faction = f[5],\n                            State = f[4],"),
    ("unknown verbs vanish", "plan.UnknownDirectives[f[0]] = n + 1;", ""),
    ("unknown verbs counted once", "plan.UnknownDirectives[f[0]] = n + 1;", "plan.UnknownDirectives[f[0]] = 1;"),
    ("malformed line not located", 'throw new System.FormatException("plan line " + lineNo + " is malformed (" + ex.GetType().Name + "): " + raw);', 'throw new System.FormatException("plan is malformed");'),
    ("malformed line swallowed", 'throw new System.FormatException("plan line " + lineNo + " is malformed (" + ex.GetType().Name + "): " + raw);', "continue;"),
    ("line numbers start at zero", "lineNo++;\n                try", "try"),
    ("roof read as terrain", 'case "ROOF":\n                        plan.Roof.Add', 'case "ROOF":\n                        plan.Terrain.Add'),
    ("paint and floor colour merged", 'case "FLOORCOLOR":\n                        plan.FloorColor.Add', 'case "FLOORCOLOR":\n                        plan.Paint.Add'),
]

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rc = run_mutations(KERNEL, "selftest_structureinjections_fuzz.py", KERNEL_MUTATIONS, only)
    rc2 = run_mutations(PLAN, "selftest_structureinjections_fuzz.py", PLAN_MUTATIONS, only)
    sys.exit(rc or rc2)
