from mcp.server.fastmcp import FastMCP
import typing
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_REPO_PATH: Path | None = None

mcp = FastMCP("Repo Explorer")

def check_repo_path() -> bool:
    """Check whether path to current repo is set and valid"""
    if CURRENT_REPO_PATH is None:
        return False
    if not CURRENT_REPO_PATH.exists():
        return False
    if not CURRENT_REPO_PATH.is_dir():
        return False
    return True

@mcp.tool()
def list_projects() -> list[str]:
    """Return a list of folders under ~/Projects"""
    logging.info("list_projects: called")

    root = Path("~/Projects").expanduser()

    if not root.exists():
        logging.warning(f"list_projects: root directory does not exist: {root}")
        return []

    projects: list[str] = []

    for p in root.iterdir():
        if p.is_dir():
            projects.append(str(p.relative_to(root)))

    logging.info(f"list_projects: found {len(projects)} projects")
    return projects

@mcp.tool()
def set_repo(path: str) -> str:
    """Set the path to currently exploring repo

    If `path` is absolute, use it directly.
    If `path` is relative, search for it inside ~/Projects/<path>.

    Args:
        path (str): path to repo to explore.
    """
    logging.info(f"set_repo: called with path={path}")
    global CURRENT_REPO_PATH
    raw = Path(path).expanduser()
    if raw.is_absolute():
        repo = raw.resolve()
    else:
        fallback = Path("~/Projects").expanduser() / raw
        repo = fallback.resolve()

    if not repo.exists():
        logging.warning(f"set_repo failed: repo does not exist: {repo}")
        return f"Error: Path does not exist: {repo}"
    if not repo.is_dir():
        logging.warning("set_repo failed: repo path is not a directory.")
        return f"Error: Path is not a directory: {repo}"

    logging.info(f"set_repo success: repo path set to {repo}")
    CURRENT_REPO_PATH = repo
    return f"Active repository set to {repo}"

@mcp.tool()
def list_all_files() -> list[str]:
    """List the file paths (relative path to repo root directory) for all files in the repo

    Returns:
        list[str]: return a list of paths for all files in current repo
    """
    logging.info(f"list_all_files: called")
    if not check_repo_path():
        return ["Error: No valid active repository. Use set_repo(path) first."]

    files: list[str] = []

    for p in CURRENT_REPO_PATH.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(CURRENT_REPO_PATH)))

    logging.info(f"list_all_files: found {len(files)} files")
    return files

@mcp.tool()
def read_file(relative_path: str) -> str:
    """Return the content of file at the given relative path in current repository

    Args:
        relative_path (str): relative path from current repo to the file to read from

    Returns:
        str: content of the file at the relative path
    """
    logging.info(f"read_file: called to read file at {relative_path}")
    if not check_repo_path():
        return "Error: No valid active repository. Use set_repo(path) first."

    file_path = CURRENT_REPO_PATH / relative_path

    if not file_path.exists():
        return f"Error: File does not exist: {relative_path}"

    if not file_path.is_file():
        return f"Error: Not a file: {relative_path}"

    try:
        content = file_path.read_text()
    except Exception as e:
        logging.error(f"read_file: Error reading file: {e}")
        return f"Error reading file: {e}"

    logging.info(f"read_file: successfully read content from {relative_path}")
    return content

@mcp.tool()
def count_files() -> int:
    """Return the number of files in the current repository."""
    logging.info("count_files: called")
    if not check_repo_path():
        return -1  # or raise, or return 0 with an error message elsewhere

    count = 0
    for p in CURRENT_REPO_PATH.rglob("*"):
        if p.is_file():
            count += 1

    logging.info(f"count_files: found {count} files")
    return count

@mcp.tool()
def search_in_repo(query: str, max_results: int = 50) -> list[str]:
    """
    Search for a text string across all files in the repository.

    Returns lines in the form: "path:line: snippet".
    """
    logging.info(f"search_in_repo: called with query={query!r}, max_results={max_results}")

    if not check_repo_path():
        return ["Error: No valid active repository. Use set_repo(path) first."]

    matches: list[str] = []
    for p in CURRENT_REPO_PATH.rglob("*"):
        if len(matches) >= max_results:
            break
        if p.is_file():
            try:
                for i, line in enumerate(p.read_text(errors="ignore").splitlines(), start=1):
                    if query in line:
                        matches.append(f"{p.relative_to(CURRENT_REPO_PATH)}:{i}: {line.strip()}")
                        if len(matches) >= max_results:
                            break
            except Exception:
                continue

    logging.info(f"search_in_repo: found {len(matches)} matches")
    return matches

@mcp.tool()
def find_files(name_substring: str = "", extension: str | None = None, max_results: int = 50) -> list[str]:
    """
    Find files by name substring and/or extension.

    Example:
      - name_substring="auth", extension=".py"
      - name_substring="", extension=".sql"
    """
    logging.info(f"find_files: called with name_substring={name_substring!r}, extension={extension!r}")

    if not check_repo_path():
        return ["Error: No valid active repository. Use set_repo(path) first."]

    hits: list[str] = []
    for p in CURRENT_REPO_PATH.rglob("*"):
        if len(hits) >= max_results:
            break
        if p.is_file():
            filename = p.name
            if name_substring and name_substring not in filename:
                continue
            if extension and not filename.endswith(extension):
                continue
            hits.append(str(p.relative_to(CURRENT_REPO_PATH)))

    logging.info(f"find_files: found {len(hits)} files")
    return hits


def main():
    logging.info("Starting MCP Server")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()