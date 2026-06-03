"""Red tests — the runnable CLI entry point (wraps the tool surface)."""
import json

from chain_signer.cli import main


def test_cli_list_prints_all_tools(capsys):
    rc = main(["list"])
    data = json.loads(capsys.readouterr().out)
    assert {t["name"] for t in data} == {"create_wallet", "get_balance", "send", "call_contract", "swap", "bridge",
                                         "preflight", "inspect_signature"}
    assert rc == 0


def test_cli_call_create_wallet_prints_an_address(capsys):
    rc = main(["call", "create_wallet", '{"chain":"evm"}'])
    data = json.loads(capsys.readouterr().out)
    assert data["address"].startswith("0x") and len(data["address"]) == 42, f"bad address: {data.get('address')}"
    assert rc == 0


def test_cli_unknown_command_returns_nonzero():
    assert main(["frobnicate"]) != 0, "unknown command should return a non-zero exit code"
