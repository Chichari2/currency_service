import subprocess

def test_cli_help():
    result = subprocess.run(
        ["poetry", "run", "currency_service", "--help"],
        capture_output=True,
        text=True
    )
    assert "usage" in result.stdout.lower()
