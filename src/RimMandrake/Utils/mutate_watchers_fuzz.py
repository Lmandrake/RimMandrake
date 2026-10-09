#!/usr/bin/env python3
"""Mutation proof for the Watchers fuzz: plants each defect in the kernel (RM_WatcherKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_watchers_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/Watchers/Source/Kernel/RM_WatcherKernel.cs"
MUTATIONS = [
    ("disabled mod does not interrupt", "if (!s.watchersEnabled || !s.onMedium) return StepFlags.EndInterrupted;", "if (!s.onMedium) return StepFlags.EndInterrupted;"),
    ("leaving the medium does not interrupt", "if (!s.watchersEnabled || !s.onMedium) return StepFlags.EndInterrupted;", "if (!s.watchersEnabled) return StepFlags.EndInterrupted;"),
    ("geophone does not make it hide", "if (s.hideAndFlinch && (s.inFlinch || s.geophone || s.cue || s.alarmed))", "if (s.hideAndFlinch && (s.inFlinch || s.cue || s.alarmed))"),
    ("a cue does not make it hide", "if (s.hideAndFlinch && (s.inFlinch || s.geophone || s.cue || s.alarmed))", "if (s.hideAndFlinch && (s.inFlinch || s.geophone || s.alarmed))"),
    ("an alarm does not make it hide", "if (s.hideAndFlinch && (s.inFlinch || s.geophone || s.cue || s.alarmed))", "if (s.hideAndFlinch && (s.inFlinch || s.geophone || s.cue))"),
    ("a hunt order sends it under", "if (s.hideAndFlinch && (s.inFlinch || s.geophone || s.cue || s.alarmed))", "if (s.hideAndFlinch && (s.inFlinch || s.geophone || s.cue || s.alarmed || s.huntMarked))"),
    ("flinch ignores the setting", "if (s.hideAndFlinch && (s.inFlinch || s.geophone || s.cue || s.alarmed))", "if (s.inFlinch || s.geophone || s.cue || s.alarmed)"),
    ("hunt order kept as it goes under", "if (s.huntMarked) f |= StepFlags.DropHunt;\n                    if", "if"),
    ("hunt order kept while it stays under", "else if (s.huntMarked) f |= StepFlags.DropHunt;", ""),
    ("hunt order dropped from a visible watcher", "if (s.turnToFace && s.hasNearest) f |= StepFlags.Face;", "if (s.turnToFace && s.hasNearest) f |= StepFlags.Face;\n                if (s.huntMarked) f |= StepFlags.DropHunt;"),
    ("a body hide raises no alarm", "if (s.inFlinch || s.geophone) f |= StepFlags.RaiseAlarm;", ""),
    ("an alarm hide raises a new alarm (loop)", "if (s.inFlinch || s.geophone) f |= StepFlags.RaiseAlarm;", "f |= StepFlags.RaiseAlarm;"),
    ("hide also ends the job", "f |= StepFlags.Hide;\n                    if (s.huntMarked)", "f |= StepFlags.Hide | StepFlags.EndSucceeded;\n                    if (s.huntMarked)"),
    ("faces without the setting", "if (s.turnToFace && s.hasNearest) f |= StepFlags.Face;", "if (s.hasNearest) f |= StepFlags.Face;"),
    ("faces with nobody near", "if (s.turnToFace && s.hasNearest) f |= StepFlags.Face;", "if (s.turnToFace) f |= StepFlags.Face;"),
    ("watch time exclusive", "if (s.now - s.watchStart >= s.maxWatchTicks) f |= StepFlags.EndSucceeded;", "if (s.now - s.watchStart > s.maxWatchTicks) f |= StepFlags.EndSucceeded;"),
    ("watch never ends", "if (s.now - s.watchStart >= s.maxWatchTicks) f |= StepFlags.EndSucceeded;", ""),
    ("sign never restored", "if (s.signMissing) f |= StepFlags.RestoreSign;", ""),
    ("emerges at the hide time inclusive", "(s.now >= s.hiddenUntil && !s.inFlinch", "(s.now > s.hiddenUntil && !s.inFlinch"),
    ("emerges into the flinch circle", "(s.now >= s.hiddenUntil && !s.inFlinch && !s.geophone", "(s.now >= s.hiddenUntil && !s.geophone"),
    ("emerges while the geophone pings", "!s.inFlinch && !s.geophone && !s.cue && !s.alarmed))", "!s.inFlinch && !s.cue && !s.alarmed))"),
    ("emerges while a cue holds", "!s.inFlinch && !s.geophone && !s.cue && !s.alarmed))", "!s.inFlinch && !s.geophone && !s.alarmed))"),
    ("emerges while alarmed", "!s.inFlinch && !s.geophone && !s.cue && !s.alarmed))", "!s.inFlinch && !s.geophone && !s.cue))"),
    ("setting off does not bring it up", "if (!s.hideAndFlinch || s.hungry ||", "if (s.hungry ||"),
    ("hunger does not bring it up", "if (!s.hideAndFlinch || s.hungry ||", "if (!s.hideAndFlinch ||"),
    ("hungry emerge does not end the job", "if (s.hungry) f |= StepFlags.EndSucceeded;\n            }", "}"),
    ("emerge does not reset the watch clock", "f |= StepFlags.Emerge | StepFlags.ResetWatchClock;", "f |= StepFlags.Emerge;"),
    ("hide time ignores the slider", "return now + (int)(rolledTicks * emergeDelayScale);", "return now + rolledTicks;"),
    ("hide time truncates to zero", "return now + (int)(rolledTicks * emergeDelayScale);", "return now + (int)(rolledTicks * emergeDelayScale) / 2;"),
    ("flinch radius ignores the scale", "return flinchRadius * scale;", "return flinchRadius;"),
    ("scan skips the watch edge", "if (d > watchSq) continue;", "if (d >= watchSq) continue;"),
    ("scan flinch edge exclusive", "if (d <= flinchSq) inFlinch = true;", "if (d < flinchSq) inFlinch = true;"),
    ("scan picks the last of equals", "if (d < bestSq) { bestSq = d; best = i; }", "if (d <= bestSq) { bestSq = d; best = i; }"),
    ("scan flinch counts creatures out of watch range", "if (d > watchSq) continue;\n                if (d <= flinchSq) inFlinch = true;", "if (d <= flinchSq) inFlinch = true;\n                if (d > watchSq) continue;"),
    ("giver without a comp", "if (!hasComp) return false;", ""),
    ("giver ignores hunger", "if (hasFoodNeed && foodPercent < emergeWhenFoodBelow) return false;", ""),
    ("giver hunger inclusive", "if (hasFoodNeed && foodPercent < emergeWhenFoodBelow) return false;", "if (hasFoodNeed && foodPercent <= emergeWhenFoodBelow) return false;"),
    ("giver starts off its medium", "if (!onMedium) return false;", ""),
    ("giver with both behaviours off", "if (!hideAndFlinch && !turnToFace) return false;", ""),
    ("giver ignores a downed animal", "if (!spawned || downed || inMentalState || !hasMap) return false;", "if (!spawned || inMentalState || !hasMap) return false;"),
    ("giver cap exclusive", "return !wanderRoll && activeWatchers < maxActivePerMap;", "return !wanderRoll && activeWatchers <= maxActivePerMap;"),
    ("giver ignores the wander roll", "return !wanderRoll && activeWatchers < maxActivePerMap;", "return activeWatchers < maxActivePerMap;"),
    ("backstop interrupts a flee", "if (hasCurrentJob && !currentJobIsIdle) return false;", ""),
    ("backstop ignores a failed search", "|| inMentalState || noMediumReachable || onMedium)", "|| inMentalState || onMedium)"),
    ("config drops the wander check", "if (wanderChance < 0f || wanderChance > 1f)", "if (false)"),
    ("config drops the hunger-threshold check", "if (emergeWhenFoodBelow < 0f || emergeWhenFoodBelow > 1f)", "if (false)"),
    ("config accepts flinch beyond watch", "if (flinchRadius <= 0f || watchRadius < flinchRadius)", "if (flinchRadius <= 0f)"),
    ("config accepts a reversed hide range", "if (hideMin <= 0 || hideMax < hideMin)", "if (hideMin <= 0)"),
    ("config accepts a missing sign class", "else if (!signClassOk)", "else if (false)"),
    ("config boundary: flinch equal to watch rejected", "watchRadius < flinchRadius", "watchRadius <= flinchRadius"),
    ("config accepts a NaN fragility ceiling", "if (!(maxLethalDamage > 0f))", "if (maxLethalDamage <= 0f)"),
    ("fragility ignores baseHealthScale", "return LethalDamagePerHealthScale * baseHealthScale * lifeStageHealthFactor;", "return LethalDamagePerHealthScale * lifeStageHealthFactor;"),
    ("fragility audit never fails", "if (!(lethal <= maxLethalDamage))", "if (false)"),
    ("fragility audit edge exclusive", "if (!(lethal <= maxLethalDamage))", "if (!(lethal < maxLethalDamage))"),
    ("sign outlives a dead owner", "return hasOwner && ownerSpawned && !ownerDead && ownerInWatchJob && jobSignIsThis;", "return hasOwner && ownerSpawned && ownerInWatchJob && jobSignIsThis;"),
    ("duplicate sign kept", "return hasOwner && ownerSpawned && !ownerDead && ownerInWatchJob && jobSignIsThis;", "return hasOwner && ownerSpawned && !ownerDead && ownerInWatchJob;"),
    ("orphan sign kept", "return hasOwner && ownerSpawned && !ownerDead && ownerInWatchJob && jobSignIsThis;", "return hasOwner && ownerSpawned && !ownerDead && jobSignIsThis;"),
    ("alarm never expires", "return now - startTick < L.maxAgeTicks;", "return true;"),
    ("alarm age edge inclusive", "return now - startTick < L.maxAgeTicks;", "return now - startTick <= L.maxAgeTicks;"),
    ("alarm ignores the hop limit", "if (!AlarmLive(now, startTick, L) || hop >= L.maxHops) return picked;", "if (!AlarmLive(now, startTick, L)) return picked;"),
    ("alarm ignores the count cap", "for (int k = 0; k < order.Count && picked.Count < room; k++)", "for (int k = 0; k < order.Count; k++)"),
    ("alarm re-reaches a watcher", "if (!eligible[i] || alreadyReached[i]) continue;", "if (!eligible[i]) continue;"),
    ("alarm reaches a hidden/busy watcher", "if (!eligible[i] || alreadyReached[i]) continue;", "if (alreadyReached[i]) continue;"),
    ("alarm ignores the hop radius", "if (distSqFromPasser[i] > hopSq || distSqFromOrigin[i] > originSq) continue;", "if (distSqFromOrigin[i] > originSq) continue;"),
    ("alarm ignores the origin distance", "if (distSqFromPasser[i] > hopSq || distSqFromOrigin[i] > originSq) continue;", "if (distSqFromPasser[i] > hopSq) continue;"),
    ("alarm picks farthest first", "distSqFromPasser[a].CompareTo(distSqFromPasser[b])", "distSqFromPasser[b].CompareTo(distSqFromPasser[a])"),
    ("alarm has no delay", "return passerTick + L.minDelayTicks + (int)(r * (L.maxDelayTicks - L.minDelayTicks));", "return passerTick;"),
    ("step interval 60", "public const int StepInterval = 30;", "public const int StepInterval = 60;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_watchers_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
