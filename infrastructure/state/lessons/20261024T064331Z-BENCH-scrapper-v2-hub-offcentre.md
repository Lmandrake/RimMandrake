compose_scrapper_v2 resized the hub/boss to 44 px but build_pipe_atlas placed it with HUB=36, so the v2 lone stub, tees and cross drew 4 px south-east of centre (the RM_PipeSeatMath LoneStubScrapperPx=4 hack). A composer that resizes a fitting must set the placement constant to the new size; v3 sets B.HUB=88.
home: src/RimMandrake/FlowWorks/art_source/pipe
