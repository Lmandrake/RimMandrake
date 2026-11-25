The bridge drops a field whose value is null from a tool's reply (jawa/patch_switch list: offRefusal null is absent), so a Python caller that indexes an optional field raises KeyError exactly in the good case. Read optional reply fields with .get.
item: RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE
