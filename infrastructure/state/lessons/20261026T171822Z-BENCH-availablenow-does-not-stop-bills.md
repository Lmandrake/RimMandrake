Hiding a recipe through RecipeDef.AvailableNow only filters the add-bill list (ITab_Bills, health card). WorkGiver_DoBill asks Bill.ShouldDoNow, so bills made before a settings switch went off keep running. A mod setting that turns a recipe off must also postfix Bill_Production.ShouldDoNow (cold storage did both from c8fc7fac4e).
home: rimworld-modding
