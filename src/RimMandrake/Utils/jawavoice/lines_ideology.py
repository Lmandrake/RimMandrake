# -*- coding: utf-8 -*-
"""Ideology v2, rebuilt on the v5 lexicon. Ordered dict: defName -> lines."""
import collections

D = collections.OrderedDict()

D["EnslaveAttempt"] = [
("Nootiba nootibu. Ta ma.","You on manifest now. Line eleven."),
("Mombay m'bwa! Nootiba mi.","You mine. Found, logged, mine."),
("Boota, noo kroo... ashuna!","All here work, or become parts. Choose today."),
("Ibana boo, ibana noo boo.","Say yes now: free. Say yes later: cost hand."),
]
D["ReduceWill"] = [
("N'ekka ashuna ta. N'ekka.","Nobody coming. Nobody even looking."),
("Gaha gahu boota ma.","Sand keep what sand take. Never give back."),
("Mob un loo ta? Hmph.","I ask your people your price. No answer yet."),
("Nootib n'ekka, zaah ibana.","Your name worth nothing here. Your water worth much."),
("Sabioto. Bahnoo bahnau ta.","Stop struggle. You wear out. You not new."),
("Mi noo kroo ta... boo.","Every day you whole, is day I not strip you."),
]
D["Suppress"] = [
("Togo togu! Togo togu ma!","Hands where I see! That is law here."),
("Boota mambay, bahnoo kroo.","Work, stay whole. Argue, become parts. Short list."),
("Nootiba nootibu, ma.","I count you every morning. I never miscount."),
("Noo t'aah, noo bom'loo. Boota!","No questions. No haggling. Only work."),
]
D["SparkSlaveRebellion"] = [
("Ashuna... ashunu, ta ne?","We go. Tonight. You and me."),
("Nootib bahnoo... utinni!","They count bad now. Is find. Finds belong to takers."),
("Mombay m'bwa! Zaah mi, gah mi.","I am mine. My water. My sand. My name."),
("Bom'loo n'ekka ta ne. Ashuna!","Never was going to be bargain. So stop waiting."),
]
D["ConvertIdeoAttempt"] = [
("Bom'loo boo mi, ta tellah?","Hear offer before you refuse. Is all anyone owed."),
("Gaha gahu. Mi ta ibana.","Sand take and take. What we keep, we keep together."),
("Kroo boota, ta boota!","All broken can be worth something again. Person too."),
]
D["Convert_Success"] = [
("Utinni! Bom'loo ibana!","A find! Deal struck! Deal good!"),
("Mambay. Nootiba ta, taa baa.","Good. You on manifest. Welcome."),
]
D["Convert_Failure"] = [
("Bom'loo noo... mambay. Sh'akka boo.","No deal today. Fine. Price only come down."),
("Mob un loo? Hmph. Ashuna.","I make fair offer. Walk away then."),
]
D["Counsel_Success"] = [
("Sabioto. Nootiba nootibu ma.","Sit. One piece at time, together, like salvage."),
("Bahnoo noo kroo, ta boota.","Cracked not worthless. I rebuild worse than you."),
("Zaah mi, zaah ta. Mambay.","Take my water. Take moment. Is all right."),
]
D["Counsel_Failure"] = [
("Noo... noo, mi t'aah bahnoo.","No. No, that come out wrong. Now worse."),
("Sabioto! Mi kroo ma boota.","Forget I speak. I take working thing. I break it."),
]
D["Reassure"] = [
("Ibana. Ibana, ta. Mambay.","Yes. You right to hold. Is all right."),
("Gaha gahu, ta noo. Boota!","Sand shift. You not shift. That worth something."),
]
D["PreachHealth"] = [
("Ta noo kroo! Boota, boota!","You not scrap yet. Get up. Get up."),
("Zaah, mambay, ibana ma.","Water. Rest. One reason. That is whole repair."),
("Booka ta boota ne!","Something here still need you. Get up."),
]
D["WorkDrive"] = [
("Utinni! Boota, boota, boota!","Work! Salvage in ground! Daylight going to waste!"),
("Ashuna! Gaha gahu noo bom'loo!","Move! Desert not negotiate! Dark not negotiate!"),
("Nootiba nootibu, booka ne!","Every hand today. Every crate tonight. All eat."),
]
D["Trial_Accuse"] = [
("Mombay m'bwa! Ta nubba ma!","That was mine! Was in this one hands!"),
("Mi nootib! Booka n'ekka!","I check manifest! Count short! Story short too!"),
("Bom'loo bahnoo ta ne!","This one bargain bad faith. Everyone here feel it."),
("Heeka heeku! Gah t'aah ma!","Smell story! Buried and dug up twice!"),
]
D["Trial_Defend"] = [
("Noo! Noo! Mi nootib ibana!","No! No! My count honest! I show again!"),
("Utinni noo kroo ta!","Finding thing not stealing thing! Ask any of you!"),
("Bom'loo mi! Bom'loo, bom'loo!","Let me make offer! Always is offer!"),
("Sabioto! Sh'akka mi, noo nootib!","This not trial! This is crowd deciding my price!"),
("Taa baa... mambay... mi n'ekka.","Please. Please. I have nothing left to trade."),
]

ALL = [ln for v in D.values() for ln in v]

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import jawafit
    print("TARGET     n=639  redup  38.8%  h 32.65%  apos 22.38%  vv 45.36%  "
          "wlen 4.75  jw 3.96  ratio 2.55\n")
    jawafit.score(ALL, "ideo v2")
    print("\n%d defs, %d lines -> %d rules" % (len(D), len(ALL), len(ALL) * 4))
