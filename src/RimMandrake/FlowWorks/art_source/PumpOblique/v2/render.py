"""Render one liquid pump look from the 3D blockout: render.py <Look> <blockout.png> <out.png> [extra sentence]
Image 1 = blockout (camera + geometry), image 2 = the look's tank (material + light), image 3 = installed pump (parts)."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.normpath(os.path.join(HERE, "../../../Textures/RimMandrake/FlowWorks"))
MAT = {
 "Scrapper": "Rusty scavenged steel casing in worn brown-grey, mismatched riveted repair plates with one faded green and one faded red patch, copper-orange flanges and hub wheel, worn fasteners, pitting and oily seams.",
 "Industrial": "Dark gunmetal cast steel, machined flange edges that catch the light, practical bolted plates, a short black-and-yellow hazard band on the curved front wall, restrained oxidation and oily recesses.",
 "Modern": "Contemporary blue municipal water pump hardware you could buy today: smooth sky-blue enamelled cast metal casing and pipes, darker blue flanges, black rubber gasket seams, bright stainless bolts and hub wheel, clean with light wear.",
 "Futuristic": "Clean white panelled casing and white pipes, pale silver couplings and fasteners, graphite seals, thin cyan glowing lines around the dome seat, along the casing wall and around each coupling.",
}
PROMPT = """RimWorld liquid-pump building sprite, 1024x1024, real alpha, fully transparent background.

Image 1 is a 3D model render and is the exact camera, silhouette, proportions, position on the canvas and occlusion. Paint over that model: every edge, ellipse, flange, bolt and pipe end stays exactly where Image 1 puts it. Image 2 is the material family, palette, light and painted finish. Image 3 only names the machine's parts and colours.

Before painting, think about which faces this camera can see: it is orthographic, looking north from 34 degrees up. The domed lid is a raised curved surface with a hub wheel standing on it. The curved front wall is in view and darker. The north pipe runs away behind the casing and shows its upper barrel and the inner, bolted side of its flange. The south pipe comes level through the wall toward the viewer and ends in a solid bolted metal flange face, upright, seen at a slant. East and west pipes run level, shaded as round barrels bright on top and dark below, with edge-on flanges. Bolts sit on their own surfaces with visible thickness.

{MATERIAL}

Painterly detailed RimWorld machine, light from above front-left, crisp and readable when small, the same artist as Image 2. The whole machine stays inside the canvas and stands alone on transparency.{EXTRA}"""


def main():
    look, block, out = sys.argv[1:4]
    extra = " " + sys.argv[4] if len(sys.argv) > 4 else ""
    prompt = PROMPT.replace("{MATERIAL}", MAT[look]).replace("{EXTRA}", extra)
    open(os.path.splitext(out)[0] + ".prompt.txt", "w").write(prompt)
    tank = os.path.join(TEX, "Tank", look, "RM_LiquidTank.png")
    old = os.path.join(HERE, "..", "plan", look + ".png")
    r = subprocess.run([sys.executable, os.path.expanduser("~/dev/MandrakeWorkflows/skills/generating-images/scripts/codex_image.py"),
        "edit", "--image", block, "--image", tank, "--image", old, "--prompt", prompt, "--out", out, "--force", "--timeout", "240"])
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
