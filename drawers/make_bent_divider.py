"""Make a bent ("S-jog") divider from a straight Divider STL exported from Onshape.

The straight divider is cut into thin slices along its length and each slice is
slid sideways by a smooth S-curve:  x += offset * (1 - cos(pi * t)) / 2,  t = 0..1
across the transition zone. The two ends stay perfectly straight and untouched,
so the plug sockets are exactly the Onshape ones.

Because slices slide rather than rotate, walls in the jog get very slightly thinner
(cos of the max slope; 7 mm over 49 mm is 2.4 % thinner), which is irrelevant for printing.

Usage:
  python make_bent_divider.py straight.stl out.stl --offset 7 --transition 49 [--center 0]
Coordinates: Y is the divider's length (centred on 0), +X is the side it jogs to as Y
increases, Z is up (open bottom at Z=0). --center moves the jog along the length.
"""
import argparse
import numpy as np
import trimesh
from meshfix import load


p = argparse.ArgumentParser()
p.add_argument("src"); p.add_argument("dst")
p.add_argument("--offset", type=float, default=7.0)
p.add_argument("--transition", type=float, default=49.0)
p.add_argument("--center", type=float, default=0.0)
p.add_argument("--step", type=float, default=2.0, help="slice spacing through the jog (mm); 2 mm keeps the curve within 0.004 mm")
a = p.parse_args()

m = load(a.src)
lo, hi = m.bounds
y0 = a.center - a.transition / 2
y1 = a.center + a.transition / 2
plug_room = 9.4   # plugs reach 9.33 mm into each end
assert y0 - lo[1] > plug_room and hi[1] - y1 > plug_room, "jog would overlap a plug socket"

# slice the mesh with planes across the transition so it can bend smoothly
for y in np.arange(y0, y1 + 1e-9, a.step):
    m = m.slice_plane([0, y, 0], [0, 1, 0], cap=False) + m.slice_plane([0, y, 0], [0, -1, 0], cap=False)
    m.merge_vertices(digits_vertex=5)

v = m.vertices.copy()
t = np.clip((v[:, 1] - y0) / a.transition, 0, 1)
v[:, 0] += a.offset * (1 - np.cos(np.pi * t)) / 2
m = trimesh.Trimesh(v, m.faces, process=True)
m.merge_vertices(digits_vertex=5)
trimesh.repair.fix_normals(m)
assert m.is_watertight, "bending opened a gap"

print(f"watertight volume={m.volume/1000:.2f} cm3 bounds={np.round(m.extents, 2)} tris={len(m.faces)}")
m.export(a.dst)
