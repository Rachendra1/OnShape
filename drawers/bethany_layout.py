"""Bethany's drawer: Trevor's hand-drawn layout as data.

Coordinates are connector centre points in mm, read off the sketch:
X runs along the south wall (the 35B-28B-28B-... wall), Y along the west
wall (the wavy-line wall with 252B and 168B). Origin = SW corner connector.

Every connector body reaches 6.99 mm from its centre, so a divider between
two connectors is (centre distance - 13.98 mm). Trevor works on a 7 mm grid and
uses 14 mm, which is what this file does.

Run:  python3 drawers/bethany_layout.py [out.png]
"""
import sys
from collections import Counter

NODE = 14          # mm of divider run taken up by one connector (2 x 7)
MIN_DIVIDER = 21   # plugs go 9.3 mm into each end, so ~19 mm is the floor
WALL_OFFSET = 2.72 # border pieces: centreline to the drawer wall
PLUG_BODY = 6.99   # connector body half-length, measured from STL

# ---- connectors: name -> (x, y, kind) ------------------------------------
N = {}
def node(name, x, y, kind): N[name] = (x, y, kind)

# corners
node("SW", 0, 0, "BL"); node("SE", 469, 0, "BL")
node("NW", 0, 448, "BL"); node("NE", 469, 448, "BL")
# south wall border-Ts
for i, x in enumerate([49, 91, 133, 182, 231, 287, 364, 413], 1):
    node(f"S{i}", x, 0, "BT")
# north wall border-Ts
for i, x in enumerate([140, 196, 252, 308, 364, 427], 1):
    node(f"N{i}", x, 448, "BT")
node("W1", 0, 266, "BT")
node("E1", 469, 210, "BT")
# row 1 (y=266) and row 2 (y=210)
for x in [49, 140, 196, 252]: node(f"R1_{x}", x, 266, "T")
for x in [49, 91, 133, 182, 238, 287]: node(f"R2_{x}", x, 210, "T")
node("R2_364", 364, 210, "T")
node("Y280_364", 364, 280, "T")
# the three spots that need special parts
node("STEP_T1", 287, 266, "T*")   # T / L / T step cluster
node("STEP_L", 287, 280, "L*")
node("STEP_T2", 308, 280, "T*")
node("TT_a", 413, 210, "T*")      # "TT": two Ts back to back
node("TT_b", 427, 210, "T*")

# ---- dividers: (a, b, border?, note) --------------------------------------
E = []
def run(names, border=False, note=""):
    for a, b in zip(names, names[1:]): E.append((a, b, border, note))

run(["SW", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "SE"], border=True)
run(["NW", "N1", "N2", "N3", "N4", "N5", "N6", "NE"], border=True)
run(["SW", "W1", "NW"], border=True)
run(["SE", "E1", "NE"], border=True)
# 196s from the south wall up to row 2 / the east junctions
for s, t in [("S1", "R2_49"), ("S2", "R2_91"), ("S3", "R2_133"), ("S4", "R2_182"),
             ("S6", "R2_287"), ("S7", "R2_364"), ("S8", "TT_a")]:
    run([s, t])
E.append(("S5", "R2_238", False, "bent '196 L?' (7 mm jog)"))
run(["R2_49", "R2_91", "R2_133", "R2_182", "R2_238", "R2_287"])
run(["R2_49", "R1_49"]); run(["R2_287", "STEP_T1"])
run(["W1", "R1_49", "R1_140", "R1_196", "R1_252", "STEP_T1"])
for n, r in [("N1", "R1_140"), ("N2", "R1_196"), ("N3", "R1_252")]: run([n, r])
run(["N4", "STEP_T2"]); run(["N5", "Y280_364"]); run(["N6", "TT_b"])
run(["STEP_T2", "Y280_364"]); run(["Y280_364", "R2_364"])
run(["R2_364", "TT_a"]); run(["TT_b", "E1"])
E.append(("STEP_T1", "STEP_L", False, "step: no room for a divider"))
E.append(("STEP_L", "STEP_T2", False, "step: no room for a divider"))
E.append(("TT_a", "TT_b", False, "TT: no room for a divider"))


def length(a, b):
    (x1, y1, _), (x2, y2, _) = N[a], N[b]
    return abs(x2 - x1) + abs(y2 - y1) - NODE   # all runs are axis-aligned (bent one: ~)


def report():
    border, inner, problems = Counter(), Counter(), []
    for a, b, is_border, note in E:
        L = length(a, b)
        if L < MIN_DIVIDER:
            problems.append(f"{a}-{b}: {L} mm ({note})")
            continue
        if note.startswith("bent"):
            L = abs(N[b][1] - N[a][1]) - NODE
            problems.append(f"{a}-{b}: {L} mm {note}")
        (border if is_border else inner)[L] += 1
    kinds = Counter(k for *_, k in N.values())
    w = max(x for x, _, _ in N.values()) + 2 * WALL_OFFSET
    d = max(y for _, y, _ in N.values()) + 2 * WALL_OFFSET
    print(f"Frame outside size: {w:.1f} x {d:.1f} mm (along south wall x along west wall)")
    print("Border dividers:", ", ".join(f"{k}B x{v}" for k, v in sorted(border.items())))
    print("Interior dividers:", ", ".join(f"{k} x{v}" for k, v in sorted(inner.items())))
    print("Connectors:", dict(kinds))
    print("Needs a decision:"); [print("  ", p) for p in problems]
    return border, inner


def draw(path):
    from PIL import Image, ImageDraw, ImageFont
    s, m = 2.0, 60
    W = int(469 * s + 2 * m); H = int(448 * s + 2 * m)
    im = Image.new("RGB", (W, H), "white"); g = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("DejaVuSans.ttf", 13); fb = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
    except OSError:
        f = fb = ImageFont.load_default()
    P = lambda x, y: (m + x * s, H - m - y * s)
    o = WALL_OFFSET
    g.rectangle([P(-o, 448 + o), P(469 + o, -o)], outline=(170, 170, 170), width=1)
    for a, b, is_border, note in E:
        (x1, y1, _), (x2, y2, _) = N[a], N[b]
        bad = length(a, b) < MIN_DIVIDER
        col = (210, 40, 40) if bad else (220, 120, 0) if note else (30, 90, 160) if is_border else (40, 40, 40)
        g.line([P(x1, y1), P(x2, y2)], fill=col, width=5 if is_border else 4)
        if not bad:
            L = abs(y2 - y1) - NODE if note.startswith("bent") else length(a, b)
            t = f"{L}B" if is_border else f"{L}"
            cx, cy = P((x1 + x2) / 2, (y1 + y2) / 2)
            vert = x1 == x2 or note.startswith("bent")
            g.text((cx + (6 if vert else -10), cy - (7 if vert else 18)), t, fill=col, font=f)
    colors = {"BL": (30, 90, 160), "BT": (30, 90, 160), "T": (40, 40, 40), "T*": (210, 40, 40), "L*": (210, 40, 40)}
    for name, (x, y, k) in N.items():
        cx, cy = P(x, y); r = 7 * s / 2
        g.rectangle([cx - r, cy - r, cx + r, cy + r], fill=colors[k])
    for (x, y), label in [((300, 273), "STEP"), ((420, 210), "TT"), ((234, 105), "bent?")]:
        cx, cy = P(x, y); g.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], outline=(210, 40, 40), width=3)
        g.text((cx + 30, cy - 46), label, fill=(210, 40, 40), font=fb)
    g.text((m, 12), "Bethany's drawer - Trevor's sketch as read (connector centres, mm). "
           "Blue = border, red = needs a decision.", fill="black", font=f)
    g.text((m - 50, H - m + 20), "south wall (BL 35B BT 28B ...)", fill=(90, 90, 90), font=f)
    g.text((6, m - 30), "west wall (wavy) ->", fill=(90, 90, 90), font=f)
    im.save(path)


if __name__ == "__main__":
    report()
    if len(sys.argv) > 1:
        draw(sys.argv[1])
