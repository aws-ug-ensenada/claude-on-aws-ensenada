"""Slide the winery's sample data to the current calendar, so "this weekend" and "last weekend" have data.

  python setup/refresh_sample_dates.py            # shift, in whole weeks (weekdays stay the same)
  python setup/refresh_sample_dates.py --dry-run  # show what would change
  git checkout -- business/winery                 # put the original dates back

The sample sales end on a Sunday and the sample reservations start on a Thursday. This moves sales so the last day is
the most recent Sunday, and reservations so they start on the coming Thursday (today counts). The coffee shop and the
clinic don't need it: their questions don't depend on the date. Don't commit the shifted files.
"""

import argparse
import csv
import datetime
import pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
FOLDER = HERE / "business" / "winery"


def last_sunday_before(today: datetime.date) -> datetime.date:
    return today - datetime.timedelta(days=(today.weekday() + 1) % 7 or 7)


def next_thursday_from(today: datetime.date) -> datetime.date:
    return today + datetime.timedelta(days=(3 - today.weekday()) % 7)


def shift(path: pathlib.Path, rows: list[dict], target: datetime.date, anchor: str) -> tuple[int, list[dict]]:
    dates = [datetime.date.fromisoformat(r["date"]) for r in rows]
    current = max(dates) if anchor == "last" else min(dates)
    days = (target - current).days
    if days % 7:
        raise SystemExit(f"{path.name}: its {'last' if anchor == 'last' else 'first'} day is a {current:%A} but the target is a {target:%A}")
    return days, [{**r, "date": (d + datetime.timedelta(days=days)).isoformat()} for r, d in zip(rows, dates)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    today = datetime.date.today()
    plan = [("sales.csv", last_sunday_before(today), "last"), ("reservations.csv", next_thursday_from(today), "first")]
    for name, target, anchor in plan:
        path = FOLDER / name
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fields, rows = reader.fieldnames, list(reader)
        days, new_rows = shift(path, rows, target, anchor)
        first, last = new_rows[0]["date"], new_rows[-1]["date"]
        print(f"{name}: {days:+d} days -> {first} to {last}" + ("  (dry run)" if args.dry_run else ""))
        if not args.dry_run and days:
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
                writer.writerows(new_rows)


if __name__ == "__main__":
    main()
