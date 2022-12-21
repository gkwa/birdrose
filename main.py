import argparse
import sys
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "original_presets_path",
    nargs="?",
    help="path to original presets file",
    default="/var/lib/avenir/conf/userpresets.xml",
)
parser.add_argument(
    "addon_presets_path",
    nargs="?",
    help="path to new addon presets file",
    default="./addon.txt",
)
parser.add_argument(
    "existing_preset_name",
    nargs="?",
    help="name of existing preset to look for in order to prevent duplicates",
    default="SESSIONS-12Mbps 0.4s AAC-2 L~0.8s",
)
args = parser.parse_args()

original_presets_path = args.original_presets_path
addon_presets_path = args.addon_presets_path
merged_presets_path = args.original_presets_path

tree1 = ET.parse(original_presets_path)
root1 = tree1.getroot()

tree2 = ET.parse(addon_presets_path)
root2 = tree2.getroot()

tree3 = ET.ElementTree()

preset_names = {
    preset.find("./Name").text.lower() for preset in root1.findall("Preset")
}

preset_exits_already = (
    True if args.existing_preset_name.lower() in preset_names else False
)

if preset_exits_already:
    sys.exit(0)

new_root = ET.Element("Presets")
new_root.append(root2)
for preset in tree1.findall("Preset"):
    new_root.append(preset)
tree3._setroot(new_root)
tree3.write(merged_presets_path)
