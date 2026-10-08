#!/usr/bin/env python3
"""Mutation proof for the Inhabited fuzz: plants each defect in the production kernels (InhabitedFateKernel.cs, InhabitedCustodyKernel.cs), runs
the fuzz wrapper, demands a FAIL, restores the file byte-identical (engine: mutate_explosivegrowth_fuzz.run_mutations).

    python3 src/RimMandrake/Utils/mutate_inhabited_fuzz.py [name-substring]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

# Dropped as equivalent: DrawInto with count == 0 returns 0 through its loop condition (moved < count) whether or not the early-out says so.
FATE = [
    ("resident can be threatened", "case InhabitedFate.Resident:\n                    return null;", "case InhabitedFate.Resident:\n                    return Menace(stockAreaExists, fireOnStockArea, factionHostile, colonistsOnMap, groundedCount, countCast, stockSpawnedCount, stockLeftOnMap, robbedFraction);"),
    ("transient has no cause", "case InhabitedFate.Transient:\n                    return CauseTransient;", "case InhabitedFate.Transient:\n                    return null;"),
    ("arrival flees without a ship", "return playerHasGravEngine() ? CauseGravship : null;", "return CauseGravship;"),
    ("arrival never flees", "return playerHasGravEngine() ? CauseGravship : null;", "return null;"),
    ("fire needs no stock area", "if (stockAreaExists && fireOnStockArea())", "if (fireOnStockArea())"),
    ("fire scan runs without a stock area", "if (stockAreaExists && fireOnStockArea())", "if (fireOnStockArea() && stockAreaExists)"),
    ("hostility ignored", "if (factionHostile)\n            {\n                return CauseHostile;\n            }", ""),
    ("harm needs no colonists", "if (colonistsOnMap && groundedCount > 0)", "if (groundedCount > 0)"),
    ("harm with an empty cast", "if (colonistsOnMap && groundedCount > 0)", "if (colonistsOnMap)"),
    ("downed is not harm", "if (c.anyDowned)\n                {\n                    return CauseHarmed;\n                }", ""),
    ("casualty is not harm", "if (c.standing < groundedCount)", "if (c.standing < 0)"),
    ("casualty off by one", "if (c.standing < groundedCount)", "if (c.standing <= groundedCount)"),
    ("robbery without stock", "if (stockSpawnedCount > 0)", "if (true)"),
    ("robbery threshold inclusive", "if (left < stockSpawnedCount * robbedFraction)", "if (left <= stockSpawnedCount * robbedFraction)"),
    ("robbery threshold ignores the fraction", "if (left < stockSpawnedCount * robbedFraction)", "if (left < stockSpawnedCount)"),
    ("cause order: hostile before burned", "if (stockAreaExists && fireOnStockArea())\n            {\n                return CauseBurned;\n            }\n            if (factionHostile)\n            {\n                return CauseHostile;\n            }", "if (factionHostile)\n            {\n                return CauseHostile;\n            }\n            if (stockAreaExists && fireOnStockArea())\n            {\n                return CauseBurned;\n            }"),
    ("apply a resident place", "return threatened && fate != InhabitedFate.Resident;", "return threatened;"),
    ("apply an unthreatened place", "return threatened && fate != InhabitedFate.Resident;", "return fate != InhabitedFate.Resident;"),
    ("emptied larder reads Abandoned", "return stockThingCount == 0 ? InhabitedState.Looted : InhabitedState.Abandoned;", "return stockThingCount == 0 ? InhabitedState.Abandoned : InhabitedState.Looted;"),
    ("recall overwrites a looted place", "return soulCount == 0 && state == InhabitedState.Inhabited ? InhabitedState.Abandoned : state;", "return soulCount == 0 ? InhabitedState.Abandoned : state;"),
    ("recall abandons an occupied place", "return soulCount == 0 && state == InhabitedState.Inhabited ? InhabitedState.Abandoned : state;", "return state == InhabitedState.Inhabited ? InhabitedState.Abandoned : state;"),
    ("stack split loses the remainder", "int n = Math.Min(limit, remaining);\n                parts.Add(n);\n                remaining -= n;", "int n = Math.Min(limit, remaining);\n                if (n == limit) parts.Add(n);\n                remaining -= n;"),
    ("stack split exceeds the limit", "int n = Math.Min(limit, remaining);", "int n = Math.Min(limit + 1, remaining);"),
    ("stack limit zero loops", "int limit = Math.Max(1, stackLimit);", "int limit = stackLimit;"),
    ("stack split of zero", "while (remaining > 0)", "while (remaining >= 0)"),
    ("goods: corpses are place goods", "if (!spawnedAndAlive || !isItem || isCorpse || playerOwned)", "if (!spawnedAndAlive || !isItem || playerOwned)"),
    ("goods: the player's own are place goods", "if (!spawnedAndAlive || !isItem || isCorpse || playerOwned)", "if (!spawnedAndAlive || !isItem || isCorpse)"),
    ("goods: unspawned are place goods", "if (!spawnedAndAlive || !isItem || isCorpse || playerOwned)", "if (!isItem || isCorpse || playerOwned)"),
    ("goods: non-items are place goods", "if (!spawnedAndAlive || !isItem || isCorpse || playerOwned)", "if (!spawnedAndAlive || isCorpse || playerOwned)"),
    ("goods: ledger and area both needed", "return inLedger || inStockArea;", "return inLedger && inStockArea;"),
    ("goods: only the ledger", "return inLedger || inStockArea;", "return inLedger;"),
    ("sleep: equal hours sleep", "if (sleepStartHour == wakeHour)\n            {\n                return false;\n            }", ""),
    ("sleep: same-day end inclusive", "return hour >= sleepStartHour && hour < wakeHour;", "return hour >= sleepStartHour && hour <= wakeHour;"),
    ("sleep: wraps wrongly", "return hour >= sleepStartHour || hour < wakeHour;", "return hour >= sleepStartHour && hour < wakeHour;"),
    ("sleep: wake hour sleeps", "return hour >= sleepStartHour || hour < wakeHour;", "return hour >= sleepStartHour || hour <= wakeHour;"),
    ("defend window", "public const int DefendTicks = 1200;", "public const int DefendTicks = 1000;"),
    ("defend without a lord", "if (hasLord && ticksGame - lastPawnHarmTick < DefendTicks)", "if (ticksGame - lastPawnHarmTick < DefendTicks)"),
    ("defend window inclusive", "ticksGame - lastPawnHarmTick < DefendTicks", "ticksGame - lastPawnHarmTick <= DefendTicks"),
    ("sleeping place works", "return sleepingHour ? RouteStance.AtRest : RouteStance.AtWork;", "return sleepingHour ? RouteStance.AtWork : RouteStance.AtRest;"),
]

CUSTODY = [
    ("record forgets the order", "displacedAt[id] = nextOrder++;", "displacedAt[id] = nextOrder;"),
    ("record keeps old metadata on re-entry", "reasons[id] = reason;\n            origins[id] = origin;", "if (!reasons.ContainsKey(id)) reasons[id] = reason;\n            origins[id] = origin;"),
    ("forget leaves the reason", "reasons.Remove(id);\n            origins.Remove(id);\n            displacedAt.Remove(id);", "origins.Remove(id);\n            displacedAt.Remove(id);"),
    ("forget leaves the order", "origins.Remove(id);\n            displacedAt.Remove(id);\n        }", "origins.Remove(id);\n        }"),
    ("unknown order sorts first", "return displacedAt.TryGetValue(id, out int o) ? o : int.MaxValue;", "return displacedAt.TryGetValue(id, out int o) ? o : -1;"),
    ("unknown reason is not Fled", "return reasons.TryGetValue(id, out DisplacedReason r) ? r : DisplacedReason.Fled;", "return reasons.TryGetValue(id, out DisplacedReason r) ? r : DisplacedReason.Enslaved;"),
    ("the dead enter the pool", "if (deadOrDestroyed)\n            {\n                return false;\n            }\n            prepare?.Invoke();", "prepare?.Invoke();"),
    ("prepare runs for the dead", "if (deadOrDestroyed)\n            {\n                return false;\n            }\n            prepare?.Invoke();", "prepare?.Invoke();\n            if (deadOrDestroyed)\n            {\n                return false;\n            }"),
    ("metadata recorded on a refused add", "if (!tryAdd())\n            {\n                return false;\n            }\n            book.Record(id, reason, origin);", "book.Record(id, reason, origin);\n            if (!tryAdd())\n            {\n                return false;\n            }"),
    ("absorb never records", "book.Record(id, reason, origin);\n            return true;", "return true;"),
    ("order newest first", "return eligible.OrderBy(p => book.OrderKey(idOf(p))).ToList();", "return eligible.OrderByDescending(p => book.OrderKey(idOf(p))).ToList();"),
    ("order unstable", "return eligible.OrderBy(p => book.OrderKey(idOf(p))).ToList();", "return eligible.OrderBy(p => book.OrderKey(idOf(p))).Reverse().ToList();"),
    ("handover of a null", "if (p == null || !removeFromPool(p))", "if (!removeFromPool(p))"),
    ("handover forgets before the destination", "taken = destination(p);", "book.Forget(id);\n                taken = destination(p);"),
    ("handover refusal does not restore", "if (!taken)\n            {\n                Restore(book, p, id, putBack, onLost);\n                return false;\n            }", "if (!taken)\n            {\n                return false;\n            }"),
    ("handover exception does not restore", "catch\n            {\n                Restore(book, p, id, putBack, onLost);\n                throw;\n            }", "catch\n            {\n                throw;\n            }"),
    ("handover exception swallowed", "Restore(book, p, id, putBack, onLost);\n                throw;", "Restore(book, p, id, putBack, onLost);\n                return false;"),
    ("handover keeps metadata on success", "book.Forget(id);\n            return true;", "return true;"),
    ("restore failure not reported", "book.Forget(id);\n                onLost?.Invoke(p);", "book.Forget(id);"),
    ("restore failure keeps metadata", "book.Forget(id);\n                onLost?.Invoke(p);", "onLost?.Invoke(p);"),
    ("draw takes one too many", "for (int i = 0; i < orderedCandidates.Count && moved < count; i++)", "for (int i = 0; i < orderedCandidates.Count && moved <= count; i++)"),
    ("draw stops at the first refusal", "if (!HandOver(book, orderedCandidates[i], idOf(orderedCandidates[i]), removeFromPool, putBack, destination, onLost))\n                {\n                    continue;\n                }", "if (!HandOver(book, orderedCandidates[i], idOf(orderedCandidates[i]), removeFromPool, putBack, destination, onLost))\n                {\n                    break;\n                }"),
    ("draw counts refusals", "{\n                    continue;\n                }\n                arrived?.Add", "{\n                    moved++;\n                    continue;\n                }\n                arrived?.Add"),
    ("draw any takes the last", "for (int i = 0; i < orderedCandidates.Count; i++)\n            {\n                if (HandOver(book, orderedCandidates[i]", "for (int i = orderedCandidates.Count - 1; i >= 0; i--)\n            {\n                if (HandOver(book, orderedCandidates[i]"),
    ("roster move loses a refused person", "else if (!returnToRoster(p))\n                {\n                    onLost?.Invoke(p);\n                }", "else\n                {\n                    returnToRoster(p);\n                }"),
    ("roster move ignores the skip", "if (p == null || skip(p) || !removeFromRoster(p))", "if (p == null || !removeFromRoster(p))"),
    ("roster move counts the refused", "if (absorb(p))\n                {\n                    moved++;\n                }", "moved++;\n                if (absorb(p))\n                {\n                }"),
    ("recall skips the roster", "if (returnToRoster(p))\n            {\n                return RecallOutcome.Roster;\n            }", ""),
    ("recall loses the person", "return absorb(p) ? RecallOutcome.Placeless : RecallOutcome.LeftToWorld;", "absorb(p);\n            return RecallOutcome.Placeless;"),
    ("wanted keeps null kinds", "if (kinds[i] == null) continue;", ""),
    ("wanted trims the front", "wanted.RemoveRange(size, wanted.Count - size);", "wanted.RemoveRange(0, wanted.Count - size);"),
    ("wanted ignores the size", "if (size > 0 && wanted.Count > size)", "if (false)"),
    ("wanted size zero trims all", "if (size > 0 && wanted.Count > size)", "if (wanted.Count > size)"),
    ("wanted drops the last role", "for (int j = 0; j < rolledCounts[i]; j++)", "for (int j = 0; j < rolledCounts[i] - 1; j++)"),
    ("generate count negative", "return Math.Max(0, wantedCount - fromPool);", "return wantedCount - fromPool;"),
    ("generate count ignores the pool", "return Math.Max(0, wantedCount - fromPool);", "return wantedCount;"),
    ("character index past the cast", "return nextCharacter >= 0 && nextCharacter < characterCount ? nextCharacter : -1;", "return nextCharacter >= 0 && nextCharacter <= characterCount ? nextCharacter : -1;"),
    ("character index negative", "return nextCharacter >= 0 && nextCharacter < characterCount ? nextCharacter : -1;", "return nextCharacter < characterCount ? nextCharacter : -1;"),
]

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rc = run_mutations("src/RimMandrake/Inhabited/Source/InhabitedFateKernel.cs", "selftest_inhabited_fuzz.py", FATE, only)
    rc2 = run_mutations("src/RimMandrake/Inhabited/Source/InhabitedCustodyKernel.cs", "selftest_inhabited_fuzz.py", CUSTODY, only)
    sys.exit(rc or rc2)
