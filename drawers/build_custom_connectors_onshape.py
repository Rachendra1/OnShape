"""Create the DoubleT and Step connector Part Studios on the claude-fixes branch.
Same recipe as make_custom_connectors.py, but as real Onshape features:
Derive (your connectors) -> Place body (custom feature) -> Boolean union."""
from onshape_api import *

FS = "58af070e0f8fa80c5afd624e"          # Drawer Features
TCONN, CORNER, STRAIGHT = "a8474ca3e67789cb00965b7d", "2c99d26bfc8c518fb3d7cbd9", "9f42ed33e5dc6d6a6e44d5e7"


def body_of(fid):
    return q(f'query = qBodyType(qCreatedBy(makeId("{fid}"), EntityType.BODY), BodyType.SOLID);')


def build(name, part_name, pieces):
    """pieces: [(source tab, derive label, [(placement label, angle, x, y, trim), ...])].
    Each source is derived once; every placement but the last places a copy."""
    eid = api("POST", f"/partstudios/d/{DOC}/w/{BRANCH}", {"name": name})["id"]
    for src, label, placements in pieces:
        fid, st, _ = add_feature(eid, derive(src, label))
        assert st == "OK", (label, st)
        for i, (plabel, angle, x, y, trim) in enumerate(placements):
            copy = i < len(placements) - 1
            _, st, _ = add_feature(eid, custom("placeBody", FS, f"Place {plabel}", {
                "bodies": body_of(fid), "angle": qty(None, f"{angle} deg"),
                "x": qty(None, f"{x} mm"), "y": qty(None, f"{y} mm"), "trim": qty(None, f"{trim} mm"),
                "copy": {"btType": "BTMParameterBoolean-144", "value": copy}}))
            assert st == "OK", ("place", plabel, st)
    union = {"btType": "BTMFeature-134", "featureType": "booleanBodies", "name": "Fuse",
             "parameters": [{"btType": "BTMParameterEnum-145", "parameterId": "operationType",
                             "value": "UNION", "enumName": "BooleanOperationType"},
                            dict(q("query = qAllModifiableSolidBodies();"), parameterId="tools")]}
    _, st, _ = add_feature(eid, union)
    assert st == "OK", ("union", st)
    parts = api("GET", f"/parts/d/{DOC}/w/{BRANCH}/e/{eid}")
    assert len(parts) == 1, parts
    md = api("GET", f"/metadata/d/{DOC}/w/{BRANCH}/e/{eid}/p/{parts[0]['partId']}")
    nprop = [p for p in md["properties"] if p["name"] == "Name"][0]["propertyId"]
    api("POST", f"/metadata/d/{DOC}/w/{BRANCH}/e/{eid}/p/{parts[0]['partId']}",
        {"properties": [{"propertyId": nprop, "value": part_name}]})
    return eid


if __name__ == "__main__":
    # TT spot: two Ts 14 mm apart, stems opposite (down to the 196, up to the 224)
    dt = build("DoubleTConnector", "Double T connector", [
        (TCONN, "TConnector", [("T east (stem north)", 90, 14, 0, 0), ("T west (stem south)", -90, 0, 0, 0)])])
    # T-L-T step: T (stem west), L (arms south+east), T (stem north), body block across the 7 mm gap
    st = build("StepConnector", "Step connector", [
        (TCONN, "TConnector", [("T far (stem north)", 90, 21, 14, 0), ("T (stem west)", 180, 0, 0, 0)]),
        (CORNER, "CornerConnector", [("L (arms south, east)", 0, 0, 14, 0)]),
        (STRAIGHT, "StraightConnector", [("filler block", 90, 10.5, 14, 5.5)])])
    print("DoubleTConnector", dt, "StepConnector", st)
