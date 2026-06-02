"""Red tests — balance must fail with a CLEAR, actionable message, not a cryptic int() crash.

First-user reality: an agent dev calls get_balance without ETHERSCAN_API_KEY (or hits a rate limit).
Etherscan returns an error JSON ({"status":"0",...,"result":"Missing/Invalid API Key"}). The old code
did int(data["result"]) -> "invalid literal for int()", which tells the user nothing. These pin that
we surface the real cause and name the env var to set.
"""
import pytest

from chain_signer.balance import get_balance


def _err_fetch(result_msg):
    return lambda url: {"status": "0", "message": "NOTOK", "result": result_msg}


def test_missing_api_key_gives_actionable_error():
    with pytest.raises(ValueError) as e:
        get_balance("0x000000000000000000000000000000000000dEaD",
                    fetch=_err_fetch("Missing/Invalid API Key"))
    msg = str(e.value)
    assert "ETHERSCAN_API_KEY" in msg, f"error should name the env var to set: {msg}"


def test_rate_limit_error_is_surfaced_not_swallowed():
    with pytest.raises(ValueError) as e:
        get_balance("0x000000000000000000000000000000000000dEaD",
                    fetch=_err_fetch("Max rate limit reached"))
    assert "rate limit" in str(e.value).lower()


def test_success_path_still_returns_number():
    bal = get_balance("0x000000000000000000000000000000000000dEaD",
                      fetch=lambda url: {"status": "1", "message": "OK", "result": str(5 * 10**18)})
    assert bal == 5.0
