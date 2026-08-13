# -*- coding: utf-8 -*-
"""v5. From v4: shorter lines built from longer words, apostrophes restored,
less breathy h, glosses trimmed. Jokes unchanged except where trimming helped."""

INSULT = [
("Mob un loo? N'ekka.","How much for you? Nothing. Counted twice. Still nothing."),
("Sh'akka sh'akku: kroo.","Priced you twice. Twice scrap."),
("B'ooba ta bahnoo bahnau!","Your motivator bad! Bad when you come!"),
("Heeka heeku! Mi gah!","You stink! I am Jawa! Think on that!"),
("Utinni? Noo. N'ekka utinni ta.","A find? No. Nobody ever shout that over you."),
("Omu'sata, kroo shaatu!","Shut mouth, unsellable heap!"),
("Zaaha zaahu, n'ekka boota.","You drink our water. You give back opinions."),
("Bom'loo ta? Hah! Hah hah!","Trade with you? Hah! I say hah! Mean it!"),
("Togo togu! Mombay m'bwa!","Hands off! Mine! Everyone know!"),
("Gah boota mi, gah noo ta.","Sand take me one day. Sand not bother you."),
("Ta boo n'ekka, mi sh'akka!","You were free. Still I overpaid."),
("Sh'akka gah: ibana. Ta: n'ekka.","Price sand: get number. Price you: get nothing."),
("Heek ta zaah shaatu!","You turn good water at fifty paces."),
("Mi kroo boota, mi noo boota ta!","I sell worse than you. I never sell you."),
("Boota n'ekka ta... mi tellah ma.","Poor find. I say so then. Say so now."),
("Gaha gahu, t'aah ma!","Even sand go around you. Sand has nowhere to be!"),
("Booka booku boota, ta noo!","Every crate here got more inside than you."),
("Mi tellah tellu boota!","I tell everyone. Everyone! Even small ones."),
("B'ooba n'ekka, t'aah ibana!","No motivator. No water. Still so much mouth!"),
("Ta bahnoo, ta noo bom'loo.","You not bargain. You just lose. Slow. Loud."),
("Heeka heeku, m'aahnoo m'aahnau!","You smell! Worse: you have opinions on it!"),
("Mob un loo gah? Mob un loo ta?","Sand has price. You? No price."),
("Ashuna! Kroo shaatu ma!","Go! Walking inventory error!"),
("Noo sh'akka ta. Noo sh'akka n'ekka.","I not price you. Nobody price nothing."),
("Kroo boota! Kroo bootoo!","Parts! You are parts! Loose parts in bag!"),
("Gah zaah bom'loo mi, ta shaatu!","I sell sand to drowning man. Not sell you."),
("T'aah ta boota? Hooda ta boota!","Best part of you is hood. Bad hood."),
("B'ooba ma? B'ooba kroo, boo!","It work? Never work. Not even new."),
("Sh'akka kroo, t'aah ibana!","Priced. Faulty. Still talking!"),
("Mi heek ta, gah heek ta, zaah heek ta!","I smell you. Sand smell you. Water complain."),
]

SLIGHT = [
("N'ekka... n'ekka noo.","Nothing. Nothing at all, really."),
("Sh'akka sh'akku... hmph.","Priced twice. Same both times."),
("Heeka... heeku.","Oh. Is you. I smell from here."),
("B'ooba ma bahnoo.","Something in that one installed backwards."),
("Mob un loo? Hah.","Imagine paying for that."),
("Kroo shaatoh shaatu.","Unsellable. Truly unsellable."),
("Bom'loo gah, noo bom'loo ma.","I trade for sand. Not for that."),
("Gaha gahu.","Even sand go around."),
("Ta zaah, ta noo boota...","Drink like colonist. Work like rock."),
("Utinni... noo. Hmph.","I get excited one moment. My mistake."),
("Nootiba nootibu... ma?","Put you in manifest... under what?"),
("M'aahnoo m'aahnau.","Opinions. So many opinions. All free."),
("Nubba bahnoo...","Those hands never hold anything heavy."),
("Heeka ma, mambay.","Smells. Fine. All have something."),
("Tellah boota ma...","Everyone know already. I make sure."),
("Sh'akka n'ekka, bom'loo n'ekka...","No value. No leverage. No thank you."),
("Ma b'ooba? Ma noo b'ooba.","It work? It not work."),
("Zaah noo boota ma...","Not worth water to raise it."),
("Kroo boo, kroo bootoo.","Was scrap when come. Settling in nice."),
("T'aah, t'aaha, t'aahu...","Talk. Talk. Talk."),
]

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import jawafit
    jawafit.score(INSULT + SLIGHT, "v5 all")
