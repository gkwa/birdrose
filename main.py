import argparse
import sys
import xml.etree.ElementTree as ET


def loop_over_file_lines(file_path, sentinel):
    with open(file_path, "r") as presets_fh:
        for line in presets_fh:
            if line.lower().find(sentinel.lower()) >= 0:
                return True
    return False


def loop_over_preset_names(file_path, sentinel):
    root = ET.parse(file_path).getroot()

    preset_names = {
        preset.find("./Name").text.lower() for preset in root.findall("Preset")
    }

    return True if sentinel.lower() in preset_names else False


def sentinel_already_exists(file_path, sentinel, check_fn):
    return eval(check_fn)(file_path, sentinel)


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
    default="/tmp/addon.txt",
)
parser.add_argument(
    "sentinel",
    nargs="?",
    help="string to look for in order to prevent duplicates",
    default="SESSIONS-12Mbps 0.4s AAC-2 L~0.8s",
)
parser.add_argument(
    "sentinel_check_fcn",
    choices=["loop_over_file_lines", "loop_over_preset_names"],
    nargs="?",
    help="string to look for in order to prevent duplicates",
    default="loop_over_file_lines",
)
args = parser.parse_args()

original_presets_path = args.original_presets_path
addon_presets_path = args.addon_presets_path
merged_presets_path = args.original_presets_path
sentinel = args.sentinel
check_fn = args.sentinel_check_fcn


tree1 = ET.parse(original_presets_path)
root1 = tree1.getroot()

if sentinel_already_exists(original_presets_path, sentinel, check_fn):
    sys.exit(0)

tree2 = ET.parse(addon_presets_path)
root2 = tree2.getroot()

tree3 = ET.ElementTree()

new_root = ET.Element("Presets")
new_root.append(root2)
presets_list = tree1.findall("Preset")
new_root.extend(presets_list)
tree3._setroot(new_root)
tree3.write(merged_presets_path, encoding="utf-8", xml_declaration=True)
