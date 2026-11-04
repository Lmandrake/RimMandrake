Two helpers building on relentless in parallel both picked <store>/incidents.json for different records (capability signatures vs instrument incidents keyed by repair item); the merge would have had each one overwrite the other's. Before adding a store file, grep the store's p("...") names on origin/main, not just on your clone.
home: NONE
