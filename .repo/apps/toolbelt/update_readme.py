import logging

from toolbelt import README_FILE, TOOLS_JSON
from toolbelt import ReadmeTableManager, ToolsFileManager
from toolbelt import Tool


log = logging.getLogger(__name__)


def configure_logging(level: str = "INFO"):
    """Configure logging with appropriate format and level."""
    log_level = level.upper() if level else "INFO"
    log_fmt = (
        "%(asctime)s | [%(levelname)s] | %(filename)s:%(lineno)d :: %(message)s"
        if log_level == "DEBUG"
        else "%(asctime)s | [%(levelname)s] :: %(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=log_fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler()],
    )


def main(log_level: str = "INFO"):
    configure_logging(log_level)

    tools_manager: ToolsFileManager = ToolsFileManager(TOOLS_JSON)

    if not tools_manager.exists():
        raise FileNotFoundError(f"Could not find tools.json file at path: {TOOLS_JSON}")

    try:
        tools_manager.read()
    except Exception as e:
        log.error(f"Failed reading file '{TOOLS_JSON}': {e}")
        raise

    if len(tools_manager.data) == 0:
        log.warning("tools.json is empty. Nothing to update.")
        return

    log.info("Deduplicating tools...")
    tools_manager.dedupe()

    tools_manager.sort()

    log.info(f"Saving sorted and deduplicated tools back to {TOOLS_JSON}")
    try:
        tools_manager.save()
    except Exception as e:
        log.error(f"Failed saving file '{TOOLS_JSON}': {e}")
        raise

    readme_manager: ReadmeTableManager = ReadmeTableManager(README_FILE)

    log.info(f"Updating file '{README_FILE}'")
    try:
        readme_manager.update_readme_with_table(
            tools_manager.data,
            as_table=True,
            render_tags=False,
            render_notes=False,
        )
    except Exception as e:
        log.error(f"Failed updating README file: {e}")
        raise


if __name__ == "__main__":
    try:
        main()

        log.info(f"'{README_FILE}' updated successfully.")
    except Exception as exc:
        log.error(f"Failed to update repository README: {exc}")
        raise
