"""Offline smoke tests: no AWS account, no model calls, no network. Run from assistant/:  python -m pytest tests"""

import pathlib
import re
import sys

import pytest
import yaml

HERE = pathlib.Path(__file__).resolve().parent.parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

import core  # noqa: E402

PRESETS = sorted(p.stem for p in (HERE / "presets").glob("*.yaml"))


def test_default_config_loads():
    cfg = core.load_config()
    for section in ("assistant", "user", "model", "tools", "agency"):
        assert section in cfg


@pytest.mark.parametrize("preset", PRESETS)
def test_preset_merges_and_builds_a_prompt(preset):
    cfg = core.load_config(preset)
    prompt = core.system_prompt(cfg)
    assert cfg["assistant"]["name"] in prompt
    extra = (yaml.safe_load((HERE / "presets" / f"{preset}.yaml").read_text()).get("assistant") or {}).get("extra_instructions")
    if extra:
        assert extra.strip().splitlines()[0].strip() in prompt


@pytest.mark.parametrize("preset", PRESETS)
def test_preset_business_folder_exists(preset):
    files = (core.load_config(preset).get("mcp_servers") or {}).get("files") or {}
    if files.get("enabled"):
        assert (HERE / files["root"]).is_dir(), f"{preset}: files root {files['root']} is not a folder"


def test_set_override_creates_and_changes_values():
    cfg = core.load_config(overrides=["assistant.personality=a pirate", "memory.enabled=false", "mcp_servers.time.enabled=true"])
    assert cfg["assistant"]["personality"] == "a pirate"
    assert cfg["memory"]["enabled"] is False
    assert cfg["mcp_servers"]["time"]["enabled"] is True


def test_every_configured_tool_group_has_documented_tools():
    cfg = core.load_config()
    for name in cfg["tools"]:
        if name in (cfg.get("gateway") or {}).get("tools", []) and not (HERE / "tools" / f"{name}.py").exists():
            continue
        for t in core.python_tools(cfg, name):
            spec = getattr(t, "tool_spec", None)
            if spec:  # the model reads this text to decide when to call the tool
                assert len(spec["description"].strip()) > 15, f"{name}.{spec['name']}: write a clearer docstring"


def test_agency_roster_loads():
    cfg = core.load_config()
    roster = core.active_agents(cfg)
    assert roster and all({"name", "role"} <= set(a) for a in roster)


def test_rehearsal_scenes_use_real_presets():
    import rehearse

    for name, _what, args, *_ in rehearse.SCENES:
        if args and "--preset" in args:
            assert args[args.index("--preset") + 1] in PRESETS, name


def test_rehearsal_scene_names_and_scripted_answers():
    import rehearse

    names = [scene[0] for scene in rehearse.SCENES]
    assert len(names) == len(set(names))
    assert {"approval", "fleet"} <= set(names)
    assert set(rehearse.STDIN) <= set(names)
    assert rehearse.STDIN["approval"] == "n\n"  # the rehearsal must never approve a delete
    assert dict((n, a) for n, _w, a, *_ in rehearse.SCENES)["fleet"] == ["--mode", "fleet"]


def test_cloud_scene_runs_without_agentcore_cli(monkeypatch):
    import rehearse

    monkeypatch.setattr(rehearse.shutil, "which", lambda _: None)
    monkeypatch.setattr(rehearse, "invoke_runtime_directly", lambda q: "direct: " + q)
    assert rehearse.needs("cloud", {}) is None
    assert rehearse.run(None, "hi", {}) == "direct: hi"


def test_documents_referenced_by_presets_exist():
    for preset in PRESETS:
        text = (HERE / "presets" / f"{preset}.yaml").read_text()
        for ref in re.findall(r"my_documents/([\w.*-]+)", text):
            if "*" not in ref:
                assert (HERE / "my_documents" / ref).exists(), f"{preset}: missing my_documents/{ref}"


def test_markdown_links_point_to_files_that_exist():
    broken = []
    for md in [REPO / "README.md", *sorted((REPO / "docs").glob("*.md"))]:
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", md.read_text()):
            if re.match(r"^[a-z]+:", target):
                continue
            if not (md.parent / target).exists():
                broken.append(f"{md.relative_to(REPO)} -> {target}")
    assert not broken, "\n".join(broken)


# ── luna.py --check ──────────────────────────────────────────

import check  # noqa: E402


@pytest.mark.parametrize("preset", PRESETS)
def test_shipped_presets_pass_the_checker(preset):
    errors = [m for level, m in check.problems(preset) if level == "error"]
    assert not errors, errors


@pytest.fixture
def bad_preset():
    path = HERE / "presets" / "zz-bad-test.yaml"
    path.write_text(
        "assistant: {personalty: calm}\n"
        "tools: [weather, hammer]\n"
        "mcp_servers: {files: {enabled: true, root: business/nope}}\n"
        "agency: {agents: [{name: chef, role: cooks, tools: [spoon], mcp: [pantry]}]}\n"
    )
    yield "zz-bad-test"
    path.unlink()


def test_checker_finds_the_usual_mistakes(bad_preset):
    messages = " | ".join(m for level, m in check.problems(bad_preset) if level == "error")
    assert "personalty" in messages and "did you mean 'assistant.personality'" in messages
    assert "hammer" in messages
    assert "business/nope" in messages
    assert "spoon" in messages and "pantry" in messages


def test_checker_suggests_the_closest_preset_name():
    messages = [m for _level, m in check.problems("clinc")]
    assert any("did you mean clinic" in m for m in messages)


# ── setup/new_preset.py ──────────────────────────────────────


def test_new_preset_scaffold_passes_the_checker():
    import shutil
    import subprocess

    slug = "zz-scaffold-test"
    try:
        out = subprocess.run([sys.executable, str(HERE / "setup" / "new_preset.py"), slug, "--business", "Test Shop"], capture_output=True, text=True, cwd=HERE)
        assert out.returncode == 0, out.stdout + out.stderr
        assert (HERE / "presets" / f"{slug}.yaml").exists() and (HERE / "business" / slug / "data.csv").exists()
        assert not [m for level, m in check.problems(slug) if level == "error"]
        again = subprocess.run([sys.executable, str(HERE / "setup" / "new_preset.py"), slug], capture_output=True, text=True, cwd=HERE)
        assert again.returncode == 1 and "already exists" in again.stdout
    finally:
        (HERE / "presets" / f"{slug}.yaml").unlink(missing_ok=True)
        shutil.rmtree(HERE / "business" / slug, ignore_errors=True)


def test_new_preset_rejects_bad_names():
    import subprocess

    out = subprocess.run([sys.executable, str(HERE / "setup" / "new_preset.py"), "Bad Name"], capture_output=True, text=True, cwd=HERE)
    assert out.returncode == 1


# ── tools/tables.py ──────────────────────────────────────────


def test_tables_tool_counts_and_sums_exactly(tmp_path):
    from tools import tables

    folder = HERE / "business" / "zz-tables-test"
    folder.mkdir()
    try:
        (folder / "d.csv").write_text("status,amount\nunconfirmed,10\nconfirmed,5.5\nUnconfirmed,2,000\n".replace("2,000", "2"))
        cfg = {"mcp_servers": {"files": {"enabled": True, "root": "business/zz-tables-test"}}}
        count_rows, sum_column = tables.tools(cfg)
        assert count_rows(file="d.csv", column="status", equals="unconfirmed")["count"] == 2
        assert count_rows(file="d.csv")["count"] == 3
        assert sum_column(file="d.csv", column="amount")["total"] == 17.5
        assert sum_column(file="d.csv", column="amount", filter_column="status", equals="confirmed")["total"] == 5.5
        with pytest.raises(ValueError):
            count_rows(file="../../config.yaml")
        with pytest.raises(ValueError):
            count_rows(file="d.csv", column="nope", equals="x")
    finally:
        import shutil

        shutil.rmtree(folder)


def test_tables_tool_is_off_without_the_files_server():
    from tools import tables

    assert tables.tools({"mcp_servers": {"files": {"enabled": False}}}) == []
