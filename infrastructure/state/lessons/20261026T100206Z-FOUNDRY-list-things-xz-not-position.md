jawa/list_things rows carry x and z, not 'position'. prove_middenshell compared r.get('position') before vs after, so None==None and 'moved' was always False. Match rows by id and compare (x, z).
home: rimbridge
