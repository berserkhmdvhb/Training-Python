import subprocess
import sys
import os

CLI_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cf_cli.py'))


def run_cli(args):
    result = subprocess.run(
        [sys.executable, CLI_SCRIPT] + args,
        capture_output=True,
        text=True,
        encoding="utf-8"  # <-- Force UTF-8 to handle all Unicode
    )
    return result.stdout, result.stderr, result.returncode



def test_cli_strict_match():
    out, err, code = run_cli(['-q', 'heart'])

    # Optional debug (can comment out once stable)
    print("\n----- STDOUT -----\n", out)
    print("\n----- STDERR -----\n", err)

    assert "WHITE HEART SUIT" in out
    assert code == 0



def test_cli_fuzzy_match():
    out, err, code = run_cli(['-q', 'grnning', '--fuzzy'])
    assert "GRINNING" in out
    assert code == 0


def test_cli_threshold_loose():
    out, err, code = run_cli(['-q', 'grnning', '--fuzzy', '--threshold', '0.5'])
    assert "GRINNING" in out
    assert code == 0


def test_cli_threshold_strict():
    out, err, code = run_cli(['-q', 'grnning', '--fuzzy', '--threshold', '0.95'])
    assert code == 0
    assert "GRINNING" not in out or out == ''


def test_cli_invalid_threshold():
    out, err, code = run_cli(['-q', 'heart', '--fuzzy', '--threshold', '1.5'])
    assert code != 0
    assert "Threshold must be between 0.0 and 1.0" in err


def test_cli_empty_query():
    out, err, code = run_cli(['-q', ''])
    assert code != 0
    assert "empty" in err.lower()


def test_cli_unknown_flag():
    out, err, code = run_cli(['--doesnotexist'])
    assert code != 0
    assert "usage" in err.lower()