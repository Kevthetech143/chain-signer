"""Red tests — adoption instrumentation (free PyPI download stats).

The win/kill signal for the distribution test. Pure parse + fetch injected (no network).
Reads pypistats 'recent' downloads so we can measure real installs once published.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.adoption import install_counts


def _fake_fetch(payload):
    def fetch(url):
        fetch.url = url
        return payload
    return fetch


def test_install_counts_parses_day_week_month():
    fetch = _fake_fetch({"data": {"last_day": 3, "last_week": 21, "last_month": 88}})
    c = install_counts("chain-signer", fetch=fetch)
    assert c == {"day": 3, "week": 21, "month": 88}, f"bad parse: {c}"


def test_install_counts_hits_the_right_package_endpoint():
    fetch = _fake_fetch({"data": {"last_day": 0, "last_week": 0, "last_month": 0}})
    install_counts("chain-signer", fetch=fetch)
    assert "pypistats.org" in fetch.url and "chain-signer" in fetch.url


def test_install_counts_zero_before_anyone_installs():
    fetch = _fake_fetch({"data": {"last_day": 0, "last_week": 0, "last_month": 0}})
    assert install_counts("chain-signer", fetch=fetch) == {"day": 0, "week": 0, "month": 0}
