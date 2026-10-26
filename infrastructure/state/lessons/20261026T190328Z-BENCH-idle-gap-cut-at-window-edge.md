testing_metrics.py max idle gap is truncated at its window end: it reported 137.8 min at 18:00Z for a SteveDesktop gap that ran 15:43Z to 18:29Z (166 min, from testq done/ timestamps). A gap still open at the window edge is a lower bound; mark it so, or measure from job timestamps.
home: infrastructure/state/facts/instrument_traps.md
