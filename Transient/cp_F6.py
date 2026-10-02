import sys; sys.path.insert(0,"Transient")
from cp_lib import *
c = call("jawa/pawn_census", ids="Human963")["pawns"][0]; print("snappy job", J(c["job"],300), "food", c["needs"]["food"], "mental", c["mentalState"])
lin = call("jawa/thing_lineage", ids="Meat_Muffalo11429", includeEvents=False)["results"][0]; print(J(lin,600))
