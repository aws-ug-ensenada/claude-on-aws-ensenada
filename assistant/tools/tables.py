"""Count and add up rows in the business's CSV files, so the model doesn't have to do arithmetic in its head.

Active only when the files server is switched on (the business presets do): it reads the same one folder, `mcp_servers.files.root`.
A language model can miscount rows when it reads a CSV; a function can't. Use these for any number that matters.
"""

import csv
import pathlib

from strands import tool

HERE = pathlib.Path(__file__).resolve().parent.parent
MAX_ROWS = 25


def _read(root: pathlib.Path, file: str) -> list[dict]:
    path = (root / file).resolve()
    if root.resolve() not in path.parents or path.suffix.lower() != ".csv":
        raise ValueError(f"{file}: only .csv files inside the business folder can be read")
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _matching(rows: list[dict], column: str, equals: str) -> list[dict]:
    if not column:
        return rows
    if rows and column not in rows[0]:
        raise ValueError(f"no column '{column}'; columns are: {', '.join(rows[0])}")
    return [r for r in rows if (r.get(column) or "").strip().lower() == equals.strip().lower()]


def tools(cfg: dict) -> list:
    files = (cfg.get("mcp_servers") or {}).get("files") or {}
    if not (files.get("enabled") and files.get("root")):
        return []
    root = HERE / files["root"]

    @tool
    def count_rows(file: str, column: str = "", equals: str = "") -> dict:
        """Count the rows of a CSV file in the business folder, optionally only those where a column equals a value.
        Use this instead of counting rows yourself. Returns the exact count and the matching rows (up to 25).

        Args:
            file: The CSV file name, e.g. "appointments.csv".
            column: Optional column to filter on, e.g. "status".
            equals: The value that column must equal (case-insensitive), e.g. "unconfirmed".
        """
        rows = _matching(_read(root, file), column, equals)
        return {"count": len(rows), "rows": rows[:MAX_ROWS], "truncated": len(rows) > MAX_ROWS}

    @tool
    def sum_column(file: str, column: str, filter_column: str = "", equals: str = "") -> dict:
        """Add up a numeric column of a CSV file in the business folder, optionally only for rows where another column equals a value.
        Use this instead of adding numbers yourself.

        Args:
            file: The CSV file name, e.g. "sales.csv".
            column: The numeric column to add up, e.g. "revenue_mxn".
            filter_column: Optional column to filter on, e.g. "day".
            equals: The value that column must equal, e.g. "Sat".
        """
        rows = _matching(_read(root, file), filter_column, equals)
        total = 0.0
        for r in rows:
            try:
                total += float((r.get(column) or "0").replace(",", ""))
            except ValueError:
                raise ValueError(f"column '{column}' has a value that is not a number: {r.get(column)!r}") from None
        return {"rows": len(rows), "total": round(total, 2)}

    return [count_rows, sum_column]
