"""Scaffold a preset and a data folder for a new business, then check it. Takes seconds, so it works on stage.

  python setup/new_preset.py bakery --business "Panadería Sol" --about "Owns a small bakery in Ensenada; busiest on weekends"

Creates presets/bakery.yaml, business/bakery/ (a data.csv to fill in and reports/), and runs the checker.
Then add rows to business/bakery/data.csv (or copy in your exports) and run:  python luna.py --preset bakery
"""

import argparse
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

PRESET = """# {business}. Try: python luna.py --preset {slug}
# Data lives in business/{slug}/; reports Luna saves go to business/{slug}/reports/.
# Policies, price lists and other reference text go in my_documents/ (then: python setup/create_knowledge_base.py --sync).
assistant:
  name: Luna
  personality: practical and brief
  answer_length: short
  extra_instructions: |
    You help run {business}.
    The business files (data.csv, reports/) are in the folder your file tools can open.
    Policies and prices are in the user's documents: search them before answering.
    When you save a report, write Markdown to reports/ and name it with the date.
user:
  about: {about}
mcp_servers:
  time: {{enabled: true}}
  fetch: {{enabled: true}}
  files: {{enabled: true, root: business/{slug}}}
"""

DATA = "date,item,quantity,notes\n2026-11-16,example item,10,replace these rows with your own data\n"


def main() -> int:
    """Write presets/<slug>.yaml and business/<slug>/, then run the preset checker; returns its exit code."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slug", help="short name, e.g. bakery (lowercase letters, digits, hyphens)")
    parser.add_argument("--business", help="the business's name, e.g. 'Panadería Sol' (default: the slug)")
    parser.add_argument("--about", default="Owns the business.", help="one sentence about the owner and what matters to them")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.slug):
        print("The name may only have lowercase letters, digits and hyphens.")
        return 1
    preset, folder = HERE / "presets" / f"{args.slug}.yaml", HERE / "business" / args.slug
    if preset.exists() or folder.exists():
        print(f"{args.slug} already exists; choose another name or delete presets/{args.slug}.yaml and business/{args.slug}/.")
        return 1
    preset.write_text(PRESET.format(slug=args.slug, business=args.business or args.slug, about=args.about))
    (folder / "reports").mkdir(parents=True)
    (folder / "reports" / ".gitkeep").touch()
    (folder / "data.csv").write_text(DATA)
    print(f"✅ presets/{args.slug}.yaml and business/{args.slug}/ created\n")
    import check

    code = check.run(args.slug)
    print(f"\nNext: put your data in business/{args.slug}/ and run  python luna.py --preset {args.slug}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
