"""Download every standard part for Bethany's drawer from Onshape as STL.

Lengths and counts come from bethany_layout.py. Files are named
<part>_<length>mm_x<count>.stl so the count to print is in the name.
Includes the bent divider and the two custom connectors, which live on the
claude-fixes branch as real Onshape parts (BentDivider, DoubleTConnector, StepConnector).

Needs the Onshape key on cad.onshape.com (the cloud proxy injects it).
Usage: python3 export_print_set.py outdir              # standard layout
       python3 export_print_set.py outdir --lowered    # layout_lowered (complete set)
"""
import os
import subprocess
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
import bethany_layout as lay  # noqa: E402

API = "https://cad.onshape.com/api/v10"
DOC = "c1f3594b6f062bbce36ab673"   # ModularDrawers - Claude
WS = "6dcc85354eb72817400f9cdc"    # branch claude-fixes (Main: 2d7ff63b0b4fd88af2740cb5)
TABS = {
    "Divider": "4f8fb15c91ad1c175b9a5d84",
    "BorderDivider": "df79b83aac218b3a10e96317",
    "TConnector": "a8474ca3e67789cb00965b7d",
    "BorderTConnector": "697cf5ef5a60aa0becf678a4",
    "BorderCornerConnector": "f993513148cf6725747ac8d5",
    "CornerConnector": "2c99d26bfc8c518fb3d7cbd9",
    "StraightConnector": "9f42ed33e5dc6d6a6e44d5e7",
    "BentDivider": "1fa7ccd71f83e697f9a02a0e",
    "DoubleTConnector": "1b210cf58b1f393817727634",
    "StepConnector": "3e814082c43d9d01d0c8205f",
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


if __name__ == "__main__" and "--lowered" not in sys.argv:
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
    jobs_named = [("BentDivider", "Divider_196mm_BENT_x1.stl"), ("DoubleTConnector", "Custom_DoubleT_x1.stl"),
                  ("StepConnector", "Custom_Step_x1.stl")]
    for tab, L, n in jobs:
        name = f"{tab}_{L:03d}mm_x{n}.stl" if L else f"{tab}_x{n}.stl"
        stl(tab, os.path.join(outdir, name), L)
        print("  ", name)
    for tab, name in jobs_named:
        stl(tab, os.path.join(outdir, name))
        print("  ", name)


def export_from_plan(outdir, lowered):
    """Export a complete print set straight from the assembly placement plan."""
    import build_assembly_onshape as plan
    from collections import Counter
    names = {plan.DIVIDER[0]: "Divider", plan.BORDER_DIVIDER[0]: "BorderDivider",
             plan.TCONN[0]: "TConnector", plan.BORDER_T[0]: "BorderTConnector",
             plan.BORDER_CORNER[0]: "BorderCornerConnector", plan.BENT: "Divider_196mm_BENT",
             plan.DOUBLE_T: "Custom_DoubleT", plan.STEP: "Custom_Step",
             plan.LOWERED: "LoweredDivider", plan.LOWERED_BENT: "LoweredDivider_196mm_BENT"}
    TABS.update({"LoweredDivider": plan.LOWERED, "LoweredDivider_196mm_BENT": plan.LOWERED_BENT,
                 "Divider_196mm_BENT": plan.BENT, "Custom_DoubleT": plan.DOUBLE_T, "Custom_Step": plan.STEP})
    os.makedirs(outdir, exist_ok=True)
    counts = Counter((p[0], p[2]) for p in plan.placements(lowered))
    for (el, cfg), n in sorted(counts.items(), key=lambda kv: (names[kv[0][0]], kv[0][1])):
        tab = names[el]
        L = int(cfg.split("=")[1].split()[0]) if cfg else None
        name = f"{tab}_{L:03d}mm_x{n}.stl" if L else f"{tab}_x{n}.stl"
        stl(tab, os.path.join(outdir, name), L)
        print("  ", name)
    return sum(counts.values())


if __name__ == "__main__" and "--lowered" in sys.argv:
    print("pieces:", export_from_plan(sys.argv[1], lowered=True))
