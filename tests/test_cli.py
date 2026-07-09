import importlib.util

from typer.testing import CliRunner

from nobots.cli import app

runner = CliRunner()


def test_score_missing_models_extra(tmp_path, monkeypatch):
    real_find_spec = importlib.util.find_spec

    def fake_find_spec(name, *a, **k):
        if name in ("torch", "transformers"):
            return None
        return real_find_spec(name, *a, **k)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    f = tmp_path / "in.md"
    f.write_text("hello world")
    result = runner.invoke(app, ["score", str(f)])
    assert result.exit_code == 1
    assert "needs the models extra" in result.output


def test_humanize_missing_humanize_extra(tmp_path, monkeypatch):
    import nobots.humanize.agent as agent

    def fake_build(*a, **k):
        raise ModuleNotFoundError("no module named pydantic_ai")

    monkeypatch.setattr(agent, "build_default_model", fake_build)
    f = tmp_path / "in.md"
    f.write_text("hello world")
    result = runner.invoke(app, ["humanize", str(f)])
    assert result.exit_code == 1
    assert "needs the humanize extra" in result.output


def test_humanize_runtime_error_stays_clean_message(tmp_path, monkeypatch):
    import nobots.humanize.agent as agent

    def fake_build(*a, **k):
        raise RuntimeError("Ollama unreachable at http://localhost:11434")

    monkeypatch.setattr(agent, "build_default_model", fake_build)
    f = tmp_path / "in.md"
    f.write_text("hello world")
    result = runner.invoke(app, ["humanize", str(f)])
    assert result.exit_code == 1
    assert "Ollama unreachable" in result.output
    assert "needs the humanize extra" not in result.output
