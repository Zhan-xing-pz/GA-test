"""Small bridge from GenericAgent code_run to the CRAG mock API tools.

This file is meant to be imported by GA-generated Python snippets during CRAG
benchmark evaluation. It deliberately exposes one stable function:

    call_crag_tool(tool_name, arguments, search_results_file=None)

The actual CRAG tool implementations live in crag-eval/test/src/tools.py.
Set CRAG_EVAL_TEST_DIR to that directory, or run from inside it.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional


DEFAULT_REMOTE_TEST_DIR = "/mnt/data/kw/mwy/pz/crag-eval/test"


def _candidate_test_dirs() -> list[Path]:
    dirs: list[Path] = []
    env_dir = os.environ.get("CRAG_EVAL_TEST_DIR")
    if env_dir:
        dirs.append(Path(env_dir))

    cwd = Path.cwd()
    dirs.extend([
        cwd,
        cwd / "test",
        Path(DEFAULT_REMOTE_TEST_DIR),
    ])
    return dirs


def _resolve_test_dir() -> Path:
    for d in _candidate_test_dirs():
        if (d / "src" / "tools.py").is_file():
            return d.resolve()
    tried = "\n".join(str(p) for p in _candidate_test_dirs())
    raise RuntimeError(
        "Cannot locate crag-eval/test. Set CRAG_EVAL_TEST_DIR to the directory "
        "that contains src/tools.py. Tried:\n" + tried
    )


def _ensure_crag_import_path() -> Path:
    test_dir = _resolve_test_dir()
    test_dir_str = str(test_dir)
    if test_dir_str not in sys.path:
        sys.path.insert(0, test_dir_str)
    return test_dir


def _load_search_results(search_results_file: Optional[str]) -> Optional[list[dict]]:
    search_results_file = search_results_file or os.environ.get("CRAG_SEARCH_RESULTS_FILE")
    if not search_results_file:
        return None
    path = Path(search_results_file)
    if not path.is_file():
        raise FileNotFoundError(f"search_results_file not found: {search_results_file}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "search_results" in data:
        data = data["search_results"]
    if not isinstance(data, list):
        raise ValueError("search_results_file must contain a list or {'search_results': list}")
    return data


def call_crag_tool(
    tool_name: str,
    arguments: dict[str, Any],
    search_results_file: Optional[str] = None,
    mock_api_url: Optional[str] = None,
) -> str:
    """Execute one CRAG tool call and return a JSON string.

    Args:
        tool_name: Exact CRAG tool name, e.g. "finance_get_ticker_by_name".
        arguments: Tool arguments as a dict.
        search_results_file: Optional JSON file for the sample's search results.
        mock_api_url: Optional mock API base URL. Defaults to CRAG_MOCK_API_URL
            or http://localhost:8000.
    """

    if not isinstance(arguments, dict):
        return json.dumps({
            "ok": False,
            "tool_name": tool_name,
            "arguments": arguments,
            "error": "arguments must be a dict",
        }, ensure_ascii=False)

    try:
        _ensure_crag_import_path()
        from src.tools import ToolExecutor  # type: ignore

        search_results = _load_search_results(search_results_file)
        executor = ToolExecutor(mock_api_url or os.environ.get("CRAG_MOCK_API_URL", "http://localhost:8000"))
        observation = executor.execute(tool_name, arguments, search_results=search_results)
        return json.dumps({
            "ok": True,
            "tool_name": tool_name,
            "arguments": arguments,
            "observation": observation,
        }, ensure_ascii=False, default=str)
    except Exception as exc:
        return json.dumps({
            "ok": False,
            "tool_name": tool_name,
            "arguments": arguments,
            "error": f"{type(exc).__name__}: {exc}",
        }, ensure_ascii=False, default=str)


def list_crag_tools(domain: Optional[str] = None) -> str:
    """Return CRAG tool names and schemas as JSON for debugging or skill setup."""

    try:
        _ensure_crag_import_path()
        from src.tools import get_all_tools, get_tools_for_domain  # type: ignore

        tools = get_tools_for_domain(domain) if domain else get_all_tools()
        compact = [
            {
                "name": t.get("function", {}).get("name"),
                "description": t.get("function", {}).get("description"),
                "parameters": t.get("function", {}).get("parameters", {}),
            }
            for t in tools
        ]
        return json.dumps({"ok": True, "domain": domain, "tools": compact}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("tool_name")
    parser.add_argument("arguments_json")
    parser.add_argument("--search-results-file")
    parser.add_argument("--mock-api-url")
    args = parser.parse_args()

    print(call_crag_tool(
        args.tool_name,
        json.loads(args.arguments_json),
        search_results_file=args.search_results_file,
        mock_api_url=args.mock_api_url,
    ))

