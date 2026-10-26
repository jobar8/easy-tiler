"""Verify that every demo script in ``examples/`` renders its output files."""

import importlib.util
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / 'examples'

DEMO_FILES = sorted(EXAMPLES_DIR.glob('demo_*.py'))

OUTPUT_REPORT = re.compile(r'Wrote (?P<png>.+) and (?P<svg>.+)')


def _load_demo_module(demo_path: Path):
    module_name = f'examples.{demo_path.stem}'
    spec = importlib.util.spec_from_file_location(module_name, str(demo_path))
    if spec is None or spec.loader is None:
        raise ImportError(f'Could not load module from {demo_path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('demo_path', DEMO_FILES, ids=lambda path: path.stem)
def test_demo_creates_outputs(demo_path, tmp_path, monkeypatch, capsys):
    """Each demo should write a non-empty PNG and SVG when run."""
    demo = _load_demo_module(demo_path)

    # Redirect demo output away from the repository into an isolated directory.
    (tmp_path / 'images').mkdir()
    monkeypatch.setattr(demo, 'cwd', tmp_path)
    monkeypatch.chdir(tmp_path)

    demo.run_demo()

    match = OUTPUT_REPORT.search(capsys.readouterr().out)
    assert match is not None, f'{demo_path.name} did not report the files it wrote'

    png_path = Path(match.group('png'))
    svg_path = Path(match.group('svg'))

    for path, kind in ((png_path, 'png'), (svg_path, 'svg')):
        assert path.exists(), f'{kind} output {path} was not created'
        assert path.stat().st_size > 0, f'{kind} output {path} is empty'

    # Outputs must land inside the isolated directory, not the repository.
    assert tmp_path in png_path.parents
    assert tmp_path in svg_path.parents
