#!/usr/bin/env python3
"""Install a PyPI wheel on a flaky connection by downloading it in small ranged chunks.

This machine drops long sustained downloads but handles small requests fine, so we pull the
wheel in 512KB pieces (with per-piece retries), verify the sha256, then pip-install the file.

Usage: python3 fetch_wheel.py <package> <version>
"""
import hashlib, json, subprocess, sys, time, urllib.request

CHUNK = 512 * 1024


def pick_wheel(pkg, ver):
    meta = json.load(urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/{ver}/json", timeout=30))
    plat = sys.platform  # 'darwin', 'linux', ...
    cands = [u for u in meta["urls"] if u["filename"].endswith(".whl")]
    def score(u):
        fn = u["filename"]
        if plat == "darwin" and "macosx" in fn: return 0
        if plat == "linux" and "manylinux" in fn: return 0
        if "py3-none-any" in fn or "-none-any" in fn: return 1
        return 9
    cands.sort(key=score)
    return cands[0]


def fetch(url, size, sha, out):
    buf = bytearray()
    while len(buf) < size:
        end = min(len(buf) + CHUNK, size) - 1
        for _ in range(8):
            try:
                req = urllib.request.Request(url, headers={"Range": f"bytes={len(buf)}-{end}", "User-Agent": "curl/8"})
                data = urllib.request.urlopen(req, timeout=30).read()
                if len(data) == end - len(buf) + 1:
                    buf.extend(data); break
            except Exception:
                time.sleep(2)
        else:
            raise SystemExit(f"failed at byte {len(buf)}")
    if hashlib.sha256(buf).hexdigest() != sha:
        raise SystemExit("sha256 mismatch")
    open(out, "wb").write(buf)


def main():
    pkg, ver = sys.argv[1], sys.argv[2]
    w = pick_wheel(pkg, ver)
    out = "/tmp/" + w["filename"]
    print(f"fetching {w['filename']} ({w['size']} bytes) in {CHUNK//1024}KB chunks")
    fetch(w["url"], w["size"], w["digests"]["sha256"], out)
    print("verified; pip installing")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", out])
    print("installed", pkg, ver)


if __name__ == "__main__":
    main()
