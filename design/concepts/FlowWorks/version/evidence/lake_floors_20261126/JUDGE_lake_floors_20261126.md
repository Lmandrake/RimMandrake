# Judge verdict: lake-floor variety (R11), 2026-11-26

Judge: delegated blind taste judge (did not make the work). One look at index.html (roughness table) and lake_1..lake_8.png.
Promise judged (owner, R11, 2026-10-17): "Vary it. Some lakes will be shallow and silted up. Others will be deep and
chasm-like. Depends on the biome. The more mountainous, the deeper in general. The more plains-like, the smoother/shallower.
They should also have some variation down there, not just a radial crater."

## Per lake
1. Plains pond (Flat, grassland), 3.0 m: KEEP. A flat silt pan at about 2.5 m inside the 1 m wadeable ring. It reads smooth and shallow, as "plains-like" asks.
2. Plains lake, silted up (Flat), 2.0 m: KEEP. A flat 2 m pan. It reads "shallow and silted up".
3. Plains lake, open (Flat, swamp), 2.0 m: KEEP. Shallow and smooth. The swamp nudge (roughness 0.00) is the only biome effect, and it is small.
4. Low hills (SmallHills), 3.5 m: KEEP. It is a little deeper than the plains lakes (mean 2.6 m against 1.9 m). The rings are concentric (0 % off-radial) and the deepest point is a one-square pit at the centre. This is the nearest of the eight to a "radial crater". At 3.5 m total depth, and next to plains, a smooth bowl stays inside "smoother/shallower", so I call it polish, not a flaw.
5. Hills (LargeHills), 12.5 m: KEEP. The deepest point is an irregular trench off the centre (6 % off-radial), with steep walls and a 9 m shelf. Clearly deeper than lake 4, and not a radial crater.
6. Hills, canyon country (RM_FloodedCanyon), 16.0 m: KEEP. The biome lifts it into the mountains band (0.75). It has a long gouge, scattered holes, 4 shelves and a broken bottom (41 % off-radial). "Depends on the biome" is visible: same hilliness as lake 5, and deeper and rougher.
7. Mountain (Mountainous), 27.0 m: KEEP. Near-vertical walls to about 15 m, then a stepped, uneven floor and a trench off the centre (65 % off-radial). It reads deep and craggy.
8. Chasm (Impassable), 46.0 m: KEEP. Cliff walls to about 30 m, then a lumpy floor with a curving rift along one side (81 % off-radial). It reads "deep and chasm-like".

## Overall: KEEP
Every sentence of R11 is kept across the eight lakes. Shallow and silted (2, 1). Deep and chasm-like (8, 7). The biome changes
the result (6 against 5; swamp in 3). Depth rises steadily from plains to chasm (mean 1.9 / 2.6 / 7.4 / 9.5 / 17.1 / 29.5 m). Plains
are smooth, and from hills upward the floor varies and is not a radial crater. The roughness table rises steadily by band in
every column (silted 45 % down to 5 %, shelves 10 % up to 50 %).

## Shallow-only lakes on flat and hill maps (the live run on 2026-10-18)
The generator is not at fault: it never touches wadeable squares. But the player's experience falls short of R11 on hill
maps. A drained lake on a LargeHills map that has only shallow water gives a 1 m floor, the same as on plains. So the
"hills" band (5 to 20 m, lakes 5 and 6) appears only where vanilla placed deep water. On the evidence of one live map per
type, the slope from plains to mountains shows only between hills and mountains, not between plains and hills. This is not a
REJECT of the generator. Whether hill-map lakes should get deep-water floors is a design and tuning question for the
Conductor. Also, the live mountain lake's floors (0.5 to 10 m) are well below this band's 8 to 35 m draw. A lake that is mostly
wadeable would explain that, but this evidence does not show it.

## Polish (blocks nothing)
- polish: Lake 4 (low hills) has 0 % off-radial floor: nested rings with a one-square pit at the centre. A little off-centre unevenness would help, even at 3.5 m.
- polish: Lakes 1 and 4 end in a single-square "needle" pit 0.5 m below the floor around it. When the lake is drained it looks like an artefact, not a basin.
- polish: Lakes 2 and 3 (silted and open plains) cannot be told apart in the pictures. On plains the silted and open draws give the same result.
- polish: The table's chasm row gives a draw range of "12 to 56 m" next to "never deeper 50 m". The cap cuts the range. Say so, or show 12 to 50 m.
- polish: The lake 2 cross-section runs along the lake's southern edge, because every square is equally deep, so the deepest-square pick is arbitrary. A line through the middle would show more.
- polish: The lake 6 caption title says "Hills lake", but its band is mountains. Add "(biome raises it to mountains)".
