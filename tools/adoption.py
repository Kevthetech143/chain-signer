#!/usr/bin/env python3
"""Adoption instrumentation — read real PyPI install counts (free, no auth).

This is the win/kill signal for chain-signer's distribution test: are people actually
installing it? Uses pypistats.org's public 'recent' endpoint. Fetch is injectable for tests.
Run directly once the package is published:  python3 tools/adoption.py [package]
"""
import json
import sys
import urllib.request

API = "https://pypistats.org/api/packages/{pkg}/recent"


def _default_fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "chain-signer-adoption"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def install_counts(package="chain-signer", *, fetch=None):
    """Return {'day','week','month'} install counts for a PyPI package."""
    data = (fetch or _default_fetch)(API.format(pkg=package))["data"]
    return {"day": data["last_day"], "week": data["last_week"], "month": data["last_month"]}


if __name__ == "__main__":
    pkg = sys.argv[1] if len(sys.argv) > 1 else "chain-signer"
    try:
        c = install_counts(pkg)
        print(f"{pkg} installs — day {c['day']} | week {c['week']} | month {c['month']}")
    except Exception as e:
        print(f"no stats yet for {pkg} (not published, or no installs): {e}")
