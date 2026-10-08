import xml.etree.ElementTree as ET
p=r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml"
r=ET.parse(p).getroot()
a=[li.text for li in r.find("activeMods")]
print(len(a)); print(a); print("rut:",[x for x in a if "rut" in x.lower()])
