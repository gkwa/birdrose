import argparse
import logging
import sys
import xml.etree.ElementTree as ET

from birdrose import __version__

__author__ = "Taylor Monacelli"
__copyright__ = "Taylor Monacelli"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


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


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
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

    parser.add_argument(
        "--version",
        action="version",
        version="birdrose {ver}".format(ver=__version__),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    args = parse_args(args)

    original_presets_path = args.original_presets_path
    addon_presets_path = args.addon_presets_path
    merged_presets_path = args.original_presets_path
    sentinel = args.sentinel
    check_fn = args.sentinel_check_fcn

    setup_logging(args.loglevel)
    _logger.debug("Starting script...")

    tree1 = ET.parse(original_presets_path)

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

    _logger.info("Script ends here")


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
