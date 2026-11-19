"""Build the two custom connectors for Bethany's drawer by fusing standard Onshape
connectors (exported as STL, default configuration) with a solid boolean union.

  double_t.stl : the "TT" spot. Two TConnectors back to back, 14 mm apart, stems
                 pointing opposite ways (one to the 196 from the south wall, one to
                 the 224 from the north wall).
  step.stl     : the "T L T" spot. T at (287,266) + CornerConnector at (287,280)
                 + T at (308,280), with a StraightConnector body filling the 7 mm gap
                 between the L and the second T.

The plugs that would point into a neighbouring connector end up buried inside that
connector's body, so only the plugs that meet real dividers stick out.
Coordinates match drawers/bethany_layout.py (X east, Y north, Z up, mm).

Usage: python make_custom_connectors.py T.stl Corner.stl Straight.stl outdir
"""
import os
import sys
import manifold3d as mf
import numpy as np
import trimesh
from meshfix import load


def to_manifold(m):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                               tri_verts=np.asarray(m.faces, np.uint32)))


def placed(m, x, y, rot_deg):
    """Rotate about Z (centre of the connector) then move its centre to (x, y)."""
    return to_manifold(m).rotate((0, 0, rot_deg)).translate((x, y, 0))


def body_slab(m, half_len):
    """Weld a connector's shells together and keep only the body within +/-half_len
    of its centre along Y (drops the plugs). Used as a solid filler block."""
    shells = [to_manifold(c) for c in m.split(only_watertight=True)]
    whole = mf.Manifold.batch_boolean(shells, mf.OpType.Add)
    box = mf.Manifold.cube((40, 2 * half_len, 40), center=True).translate((0, 0, 10))
    return whole ^ box


def to_trimesh(man):
    mesh = man.to_mesh()
    return trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts)


def check(name, man, parts):
    out = to_trimesh(man)
    pieces = len(out.split(only_watertight=False))
    print(f"{name}: watertight={out.is_watertight} pieces={pieces} volume={out.volume/1000:.2f} cm3 "
          f"(inputs {sum(p.volume() for p in parts)/1000:.2f}) size={np.round(out.extents, 1)}")
    assert out.is_watertight and pieces == 1
    return out


T, L, S, outdir = (load(sys.argv[1]), load(sys.argv[2]), load(sys.argv[3]), sys.argv[4])
# As exported: T runs along Y with its stem on +X; Corner has arms on +X and -Y;
# Straight runs along Y.
os.makedirs(outdir, exist_ok=True)

# "TT": local origin at the first T (413,210). Stem down (-Y) then stem up (+Y), 14 mm east.
tt_parts = [placed(T, 0, 0, -90), placed(T, 14, 0, 90)]
tt = check("double_t", mf.Manifold.batch_boolean(tt_parts, mf.OpType.Add), tt_parts)
tt.export(os.path.join(outdir, "double_t.stl"))

# Step: local origin at T1 (287,266).
#   T1 (0,0): arms W, S, N  -> stem on -X (rot 180)
#   L  (0,14): arms S, E    -> as exported
#   T2 (21,14): arms W, E, N -> stem on +Y (rot 90)
#   filler: 11 mm of Straight body (no plugs) along X across the 7 mm gap (L ends x=7, T2 starts x=14)
filler = body_slab(S, 5.5).rotate((0, 0, 90)).translate((10.5, 14, 0))  # spans x 5..16
step_parts = [placed(T, 0, 0, 180), placed(L, 0, 14, 0), placed(T, 21, 14, 90), filler]
step = check("step", mf.Manifold.batch_boolean(step_parts, mf.OpType.Add), step_parts)
step.export(os.path.join(outdir, "step.stl"))
