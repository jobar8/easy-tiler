import importlib.util
from pathlib import Path


def _load_demo_module():
    repo_root = Path(__file__).resolve().parents[1]
    demo_path = repo_root / 'examples' / 'demo.py'
    spec = importlib.util.spec_from_file_location('examples.demo', str(demo_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_demo_creates_outputs(tmp_path, monkeypatch):
    # run demo in isolated tmp directory
    monkeypatch.chdir(tmp_path)
    demo = _load_demo_module()
    demo.run_demo()

    png = tmp_path / 'demo.png'
    svg = tmp_path / 'demo.svg'

    assert png.exists(), 'demo.png was not created'
    assert svg.exists(), 'demo.svg was not created'
    assert png.stat().st_size > 0, 'demo.png is empty'
    assert svg.stat().st_size > 0, 'demo.svg is empty'
