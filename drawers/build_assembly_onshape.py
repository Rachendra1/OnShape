"""Build "Bethany's Drawer - full layout" on the claude-fixes branch from bethany_layout.py.

Every piece is inserted (dividers with their DividerLength configuration) and moved to its
place, so the assembly's BOM tab is the parts list. Positions: X along the south wall,
Y along the west wall, origin = SW corner connector centre, Z up, all in mm.

Usage: python3 build_assembly_onshape.py <assembly element id>
"""
import math
import sys
from collections import OrderedDict

import bethany_layout as lay
from onshape_api import api, DOC, BRANCH

DIVIDER = ("4f8fb15c91ad1c175b9a5d84", "JOD")
BORDER_DIVIDER = ("df79b83aac218b3a10e96317", "JOD")
TCONN = ("a8474ca3e67789cb00965b7d", "RBBD")
BORDER_T = ("697cf5ef5a60aa0becf678a4", "JyD")
BORDER_CORNER = ("f993513148cf6725747ac8d5", "JmD")
BENT = "1fa7ccd71f83e697f9a02a0e"
DOUBLE_T = "1b210cf58b1f393817727634"
STEP = "3e814082c43d9d01d0c8205f"

W, D = 469, 448   # far walls' connector-centre lines


def only_part(eid):
    return api("GET", f"/parts/d/{DOC}/w/{BRANCH}/e/{eid}")[0]["partId"]


def wall_rotation(x, y):
    """Rotation that turns a border piece's flat back (+X as modelled) toward its wall."""
    if x == W: return 0
    if y == D: return 90
    if x == 0: return 180
    if y == 0: return -90
    raise ValueError((x, y))


def placements():
    out = []   # (element, part, configuration, x, y, rotation, label)
    for a, b, border, note in lay.E:
        (x1, y1, _), (x2, y2, _) = lay.N[a], lay.N[b]
        if note.startswith("bent"):
            # south end on (231, 0), north end on (238, 210): straight ends 7 mm apart in X
            out.append((BENT, only_part(BENT), "", x1, (y1 + y2) / 2, 0, "bent 196"))
            continue
        L = lay.length(a, b)
        if L < lay.MIN_DIVIDER:
            continue   # the special spots, covered by the double T and step connectors
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        horizontal = y1 == y2
        if border:
            el, part = BORDER_DIVIDER
            # flat back toward the wall: south -90, north 90, west 180, east 0
            rot = (-90 if my == 0 else 90) if horizontal else (180 if mx == 0 else 0)
        else:
            el, part = DIVIDER
            rot = 90 if horizontal else 0
        out.append((el, part, f"DividerLength={L} mm", mx, my, rot, f"{a}-{b}"))

    for name, (x, y, kind) in lay.N.items():
        if kind == "BL":
            rot = {(W, 0): 0, (W, D): 90, (0, D): 180, (0, 0): -90}[(x, y)]
            out.append((*BORDER_CORNER, "", x, y, rot, name))
        elif kind == "BT":
            out.append((*BORDER_T, "", x, y, wall_rotation(x, y), name))
        elif kind == "T":
            arms = []
            for a, b, _, _ in lay.E:
                if name in (a, b):
                    other = lay.N[b if a == name else a]
                    dx, dy = other[0] - x, other[1] - y      # snap to the main axis (the bent one is off by 7)
                    arms.append((int(math.copysign(1, dx)), 0) if abs(dx) > abs(dy) else (0, int(math.copysign(1, dy))))
            stem = [v for v in arms if (-v[0], -v[1]) not in arms]
            assert len(arms) == 3 and len(stem) == 1, (name, arms)
            rot = math.degrees(math.atan2(stem[0][1], stem[0][0]))
            out.append((*TCONN, "", x, y, rot, name))
    out.append((DOUBLE_T, only_part(DOUBLE_T), "", *lay.N["TT_a"][:2], 0, "double T"))
    out.append((STEP, only_part(STEP), "", *lay.N["STEP_T1"][:2], 0, "step"))
    return out


def transform(x, y, rot_deg):
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    return [c, -s, 0, x / 1000, s, c, 0, y / 1000, 0, 0, 1, 0, 0, 0, 0, 1]


def build(asm):
    base = f"/assemblies/d/{DOC}/w/{BRANCH}/e/{asm}"
    groups = OrderedDict()
    for p in placements():
        groups.setdefault(p[:3], []).append(p)
    seen = {i["id"] for i in api("GET", base)["rootAssembly"]["instances"]}
    placed = 0
    for (el, part, cfg), items in groups.items():
        for _ in items:
            api("POST", f"{base}/instances", {"documentId": DOC, "elementId": el, "partId": part,
                                              "isAssembly": False, "isWholePartStudio": False,
                                              "configuration": cfg})
        new = [i["id"] for i in api("GET", base)["rootAssembly"]["instances"] if i["id"] not in seen]
        assert len(new) == len(items), (el, cfg, len(new), len(items))
        for inst, (_, _, _, x, y, rot, label) in zip(new, items):
            api("POST", f"{base}/occurrencetransforms", {
                "occurrences": [{"path": [inst]}], "transform": transform(x, y, rot), "isRelative": False})
            placed += 1
        seen.update(new)
        print(f"  {len(items):2d} x {el[:6]}/{part} {cfg}")
    return placed


if __name__ == "__main__":
    n = build(sys.argv[1])
    print("placed", n)
