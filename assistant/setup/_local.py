"""Read/write config.local.yaml — your account-specific IDs. Git-ignored, never committed."""

import pathlib

import yaml

FILE = pathlib.Path(__file__).parent.parent / "config.local.yaml"
REGION = yaml.safe_load((FILE.parent / "config.yaml").read_text())["model"]["region"]


def read() -> dict:
    return (yaml.safe_load(FILE.read_text()) or {}) if FILE.exists() else {}


def write(data: dict) -> None:
    FILE.write_text("# Written by setup/ scripts. Your account-specific IDs — do not commit.\n" + yaml.safe_dump(data, sort_keys=False))
