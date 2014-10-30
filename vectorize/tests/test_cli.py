import json

from click.testing import CliRunner

from rastersurface.scripts.surfacevectorize import cli


def test_cli_shapes():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
