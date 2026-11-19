"""Download every standard part for Bethany's drawer from Onshape as STL.

Lengths and counts come from bethany_layout.py. Files are named
<part>_<length>mm_x<count>.stl so the count to print is in the name.
The bent divider and the two custom connectors are made afterwards by
make_bent_divider.py and make_custom_connectors.py (see PRINT_LIST.md).

Needs the Onshape key on cad.onshape.com (the cloud proxy injects it).
Usage: python3 export_print_set.py outdir
"""
import os
import subprocess
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
import bethany_layout as lay  # noqa: E402

API = "https://cad.onshape.com/api/v10"
DOC, WS = "c1f3594b6f062bbce36ab673", "2d7ff63b0b4fd88af2740cb5"   # ModularDrawers - Claude, Main
TABS = {
    "Divider": "4f8fb15c91ad1c175b9a5d84",
    "BorderDivider": "df79b83aac218b3a10e96317",
    "TConnector": "a8474ca3e67789cb00965b7d",
    "BorderTConnector": "697cf5ef5a60aa0becf678a4",
    "BorderCornerConnector": "f993513148cf6725747ac8d5",
    "CornerConnector": "2c99d26bfc8c518fb3d7cbd9",
    "StraightConnector": "9f42ed33e5dc6d6a6e44d5e7",
}


def stl(tab, out, length=None):
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return out   # already downloaded
    for attempt in range(8):
        try:
            return _stl(tab, out, length)
        except (StopIteration, subprocess.CalledProcessError, AssertionError):
            time.sleep(15 * (attempt + 1))   # Onshape rate limit (429): back off and retry
    raise RuntimeError(f"could not export {out}")


def _stl(tab, out, length=None):
    time.sleep(2)
    url = f"{API}/partstudios/d/{DOC}/w/{WS}/e/{TABS[tab]}/stl?units=millimeter&mode=binary"
    if length is not None:
        url += f"&configuration=DividerLength%3D{length}%2Bmm"
    # The export redirects to a regional host the proxy blocks; ask cad.onshape.com for the same path.
    head = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-D", "-", url],
                          capture_output=True, text=True, check=True).stdout
    loc = next(l.split(" ", 1)[1].strip() for l in head.splitlines() if l.lower().startswith("location:"))
    loc = "https://cad.onshape.com/" + loc.split("/", 3)[3]
    subprocess.run(["curl", "-sS", "-f", "-o", out, loc], check=True)
    size = os.path.getsize(out)
    assert size > 1000, f"{out}: suspiciously small ({size} bytes)"
    return out


if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    border, inner = lay.report()
    inner = Counter(inner)
    inner[196] -= 1   # the bent one is made separately
    kinds = Counter(k for *_, k in lay.N.values())
    jobs = [("BorderDivider", L, n) for L, n in sorted(border.items())]
    jobs += [("Divider", L, n) for L, n in sorted(inner.items()) if n]
    jobs += [("BorderCornerConnector", None, kinds["BL"]), ("BorderTConnector", None, kinds["BT"]),
             ("TConnector", None, kinds["T"])]
    for tab, L, n in jobs:
        name = f"{tab}_{L:03d}mm_x{n}.stl" if L else f"{tab}_x{n}.stl"
        stl(tab, os.path.join(outdir, name), L)
        print("  ", name)
    # sources for the custom pieces
    src = os.path.join(outdir, "_sources")
    os.makedirs(src, exist_ok=True)
    stl("Divider", os.path.join(src, "Divider_196mm.stl"), 196)
    for tab in ("TConnector", "CornerConnector", "StraightConnector"):
        stl(tab, os.path.join(src, f"{tab}.stl"))
