import json
import logging
from pathlib import Path
import argparse

log = logging.getLogger(__name__)

## Absolute path to this script's directory
THIS_DIR = Path(__file__).resolve().parent
## Path to repository root
REPO_ROOT = THIS_DIR.parent.parent
## Path to tools.json
TOOLS_JSON = REPO_ROOT / ".repo" / "tools.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sort the tools.json file in the .repo directory."
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without writing changes to the file.",
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    log_level = "DEBUG" if args.debug else "INFO"
    log_fmt = "%(asctime)s | [%(levelname)s] | %(filename)s:%(lineno)d :: %(message)s" if args.debug else "%(asctime)s | [%(levelname)s] :: %(message)s"
    
    logging.basicConfig(
        level=log_level,
        format=log_fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler()],
    )
    
    log.debug("DEBUG logging enabled")
    
    if not Path(TOOLS_JSON).exists():
        log.error(f"tools.json not found at {TOOLS_JSON}")
        return
    
    log.info(f"Reading tools from file: {TOOLS_JSON}")
    
    try:
        with open(TOOLS_JSON, "r", encoding="utf-8") as f:
            tools = json.load(f)
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse JSON: {e}")
        raise
    except Exception as e:
        log.error(f"Error reading file: {e}")
        raise
    
    log.debug(f"Tools ({type(tools)}):\n{tools}")
    
    if not isinstance(tools, list):
        log.error("tools.json does not contain a list of tools.")
        return
    
    if len(tools) == 0:
        log.warning("tools.json is empty. Nothing to sort.")
        return
    
    log.info(f"Sorting {len(tools)} tools by 'name' field.")
    
    try:
        sorted_tools = sorted(tools, key=lambda x: x.get("name", "").lower())
    except Exception as e:
        log.error(f"Error during sorting: {e}")
        raise
    
    log.debug(f"Tools (sorted):\n{sorted_tools}")
    
    if args.dry_run:
        log.info("Dry run enabled. No changes will be written to the file.")
        log.info("Sorted tools would be (first 10):\n" + json.dumps(sorted_tools[:10], indent=4))
        
        return
    
    log.info(f"Writing sorted tools back to file: {TOOLS_JSON}")
    try:
        with open(TOOLS_JSON, "w", encoding="utf-8") as f:
            json.dump(sorted_tools, f, indent=4)
            f.write("\n")
    except Exception as e:
        log.error(f"Error writing to file: {e}")
        raise
    

if __name__ == "__main__":
    try:
        main()
        log.info("tools.json sorted successfully.")
    except Exception as exc:
        log.error(f"An error occurred: {exc}")
        raise
