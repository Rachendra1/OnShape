"""Shared mesh helpers for Onshape STL exports."""
import networkx as nx
import numpy as np
import trimesh


def load(path):
    """Load an Onshape STL, merge duplicate vertices and close its small flat seam holes."""
    m = trimesh.load(path, force="mesh")
    m.merge_vertices(digits_vertex=5)
    m = patch_flat_holes(m)
    assert m.is_watertight, f"{path}: still has holes after patching"
    return m


def patch_flat_holes(m):
    """Onshape's divider STL has one small flat hole (a missing patch of the channel
    ceiling where the mirrored halves meet). Close any planar boundary loop with a fan."""
    edges = m.edges_sorted[trimesh.grouping.group_rows(m.edges_sorted, require_count=1)]
    if len(edges) == 0:
        return m
    faces = [m.faces]
    verts = [m.vertices]
    n = len(m.vertices)
    for cycle in nx.cycle_basis(nx.from_edgelist(edges)):
        pts = m.vertices[cycle]
        assert np.ptp(pts, axis=0).min() < 1e-3, "hole is not flat; won't guess how to fill it"
        verts.append(pts.mean(0, keepdims=True))
        faces.append([[cycle[i], cycle[(i + 1) % len(cycle)], n] for i in range(len(cycle))])
        n += 1
    out = trimesh.Trimesh(np.vstack(verts), np.vstack(faces), process=True)
    trimesh.repair.fix_normals(out)
    return out
