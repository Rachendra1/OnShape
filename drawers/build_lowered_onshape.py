"""Create LoweredDivider and LoweredBentDivider on the claude-fixes branch.

Both: Derive (Divider at #DividerLength, or BentDivider) -> Lower middle -> Name by length.
Configuration: LowerDrop (6 mm = 30% of the 20 mm height), LowFraction (0.4: the flat bottom of
the dip is the middle 40%), RampFraction (0.1: each ramp is 10% of the length).
"""
from onshape_api import *

FS = "58af070e0f8fa80c5afd624e"          # Drawer Features
DIVIDER = "4f8fb15c91ad1c175b9a5d84"
BENT = "1fa7ccd71f83e697f9a02a0e"


def qparam(pid, default, lo, hi, units="millimeter", qtype="LENGTH"):
    return {"btType": "BTMConfigurationParameterQuantity-1826", "parameterId": pid, "parameterName": pid,
            "quantityType": qtype,
            "rangeAndDefault": {"btType": "BTQuantityRange-181", "defaultValue": default,
                                "minValue": lo, "maxValue": hi, "units": units}}


def configure(eid, params):
    cfg = api("GET", f"/elements/d/{DOC}/w/{BRANCH}/e/{eid}/configuration")
    api("POST", f"/elements/d/{DOC}/w/{BRANCH}/e/{eid}/configuration", {
        "btType": "BTConfigurationUpdateCall-2933", "configurationParameters": params,
        "serializationVersion": cfg["serializationVersion"], "sourceMicroversion": cfg["sourceMicroversion"],
        "rejectMicroversionSkew": False})


def build(name, source, source_config, length_expr, prefix, with_length_input):
    eid = api("POST", f"/partstudios/d/{DOC}/w/{BRANCH}", {"name": name})["id"]
    params = [qparam("LowerDrop", 6, 0, 15),
              qparam("LowFraction", 0.4, 0.05, 0.8, units="", qtype="REAL"),
              qparam("RampFraction", 0.1, 0.01, 0.3, units="", qtype="REAL")]
    if with_length_input:
        params.insert(0, qparam("DividerLength", 196, 56, 256))
    configure(eid, params)
    fid, st, _ = add_feature(eid, derive(source, "Divider", source_config))
    assert st == "OK", st
    body = q(f'query = qBodyType(qCreatedBy(makeId("{fid}"), EntityType.BODY), BodyType.SOLID);')
    _, st, _ = add_feature(eid, custom("lowerMiddle", FS, "Lower middle", {
        "divider": body, "drop": qty(None, "#LowerDrop"),
        "lowLength": qty(None, f"#LowFraction * {length_expr}"),
        "ramp": qty(None, f"#RampFraction * {length_expr}")}))
    assert st == "OK", ("lower", st)
    _, st, _ = add_feature(eid, custom("nameByLength", FS, "Name by length", {
        "parts": q("query = qAllModifiableSolidBodies();"),
        "prefix": {"btType": "BTMParameterString-149", "value": prefix},
        "length": qty(None, length_expr)}))
    assert st == "OK", ("name", st)
    return eid


if __name__ == "__main__":
    ld = build("LoweredDivider", DIVIDER, {"DividerLength": "#DividerLength"}, "#DividerLength",
               "Lowered divider", True)
    lb = build("LoweredBentDivider", BENT, None, "196 mm", "Lowered bent divider", False)
    print("LoweredDivider", ld, "LoweredBentDivider", lb)
