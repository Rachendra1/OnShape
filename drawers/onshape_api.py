"""Tiny Onshape REST helper. Auth comes from the cloud proxy (no key in code).

    from onshape_api import api
    api("GET", "/documents/d/<did>/workspaces")
    api("POST", "/partstudios/d/<did>/w/<wid>/e/<eid>/features", {"feature": {...}})
"""
import json
import subprocess
import time

BASE = "https://cad.onshape.com/api/v10"
DOC = "c1f3594b6f062bbce36ab673"             # ModularDrawers - Claude
MAIN = "2d7ff63b0b4fd88af2740cb5"
BRANCH = "6dcc85354eb72817400f9cdc"           # claude-fixes
SAFETY_VERSION = "1506cc77d0bcc2af5bb77e0f"   # "Before Claude edits"


class OnshapeError(RuntimeError):
    pass


def api(method, path, body=None, raw=False, tries=8):
    url = path if path.startswith("http") else BASE + path
    cmd = ["curl", "-sS", "-X", method, "-H", "Accept: application/json", "-w", "\n%{http_code}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "--data-binary", "@-"]
    for attempt in range(tries):
        out = subprocess.run(cmd + [url], input=json.dumps(body) if body is not None else None,
                             capture_output=True, text=True)
        text, _, code = out.stdout.rpartition("\n")
        if code == "429" or code.startswith("5"):
            time.sleep(5 * (attempt + 1))
            continue
        if not code.startswith("2"):
            raise OnshapeError(f"{method} {path} -> HTTP {code}: {text[:800]}")
        return text if raw else (json.loads(text) if text.strip() else None)
    raise OnshapeError(f"{method} {path}: gave up after {tries} tries (HTTP {code})")


# ---- feature builders ------------------------------------------------------
def element_microversion(eid, wid=BRANCH):
    for e in api("GET", f"/documents/d/{DOC}/w/{wid}/elements"):
        if e["id"] == eid:
            return e["microversionId"]
    raise OnshapeError(f"element {eid} not found")


def q(query_string):
    return {"btType": "BTMParameterQueryList-148", "parameterId": None,
            "queries": [{"btType": "BTMIndividualQuery-138", "queryString": query_string}]}


def qty(pid, expression):
    return {"btType": "BTMParameterQuantity-147", "parameterId": pid, "expression": expression, "isInteger": False}


def derive(source_eid, name, config=None):
    """importDerived feature: all parts of another Part Studio in this document, at the origin."""
    part_q = q("query = qBodyType(qEverything(EntityType.BODY), BodyType.SOLID);")  # solids only
    part_q["parameterId"] = "partQuery"
    ref = {"btType": "BTMParameterReferencePartStudio-3302", "parameterId": "partStudio",
           "namespace": f"e{source_eid}::m{element_microversion(source_eid)}",
           "partQuery": part_q,
           "configuration": [qty(k, v) for k, v in (config or {}).items()]}
    return {"btType": "BTMFeature-134", "featureType": "importDerived", "name": name,
            "parameters": [ref,
                           {"btType": "BTMParameterEnum-145", "parameterId": "placement", "value": "AT_ORIGIN",
                            "enumName": "DerivedPlacementType"},
                           {"btType": "BTMParameterBoolean-144", "parameterId": "includeMateConnectors", "value": False}]}


def custom(feature_type, fs_eid, name, params):
    """A feature from our own Feature Studio. params: {id: BTMParameter dict}."""
    plist = []
    for pid, p in params.items():
        p = dict(p); p["parameterId"] = pid; plist.append(p)
    return {"btType": "BTMFeature-134", "featureType": feature_type, "name": name,
            "namespace": f"e{fs_eid}::m{element_microversion(fs_eid)}", "parameters": plist}


def add_feature(eid, feature, wid=BRANCH):
    r = api("POST", f"/partstudios/d/{DOC}/w/{wid}/e/{eid}/features", {"feature": feature})
    return r["feature"]["featureId"], r.get("featureState", {}).get("featureStatus"), r


def update_feature(eid, feature, wid=BRANCH):
    r = api("POST", f"/partstudios/d/{DOC}/w/{wid}/e/{eid}/features/featureid/{feature['featureId']}",
            {"feature": feature})
    return r.get("featureState", {}).get("featureStatus"), r


def statuses(eid, wid=BRANCH):
    d = api("GET", f"/partstudios/d/{DOC}/w/{wid}/e/{eid}/features")
    return [(f["name"], d["featureStates"].get(f["featureId"], {}).get("featureStatus")) for f in d["features"]]
