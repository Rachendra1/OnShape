# Onshape model work: agent briefing

This repo holds notes for finishing and cleaning up Trevor's Onshape CAD models.
The models live in Onshape, not here. Read `INVENTORY.md` first: it lists every
document, what is in it, and the cleanup recommendations.

## Talking to Onshape

- An Onshape API key (Basic auth) is saved as a network secret on this cloud environment for
  `cad.onshape.com`. The proxy injects it automatically. Do **not** add an Authorization header yourself;
  plain `curl` works:
  ```bash
  curl -sS -H "Accept: application/json" "https://cad.onshape.com/api/v10/users/sessioninfo"
  ```
  401 `invalid_token` means the secret is wrong or was saved as Bearer instead of Basic.
- Since 2026-11-20 the key can **read and write, but not delete** (Trevor's choice). DELETE calls return 403.
- Make changes on a **branch**, never directly in Main, and save a Version of Main first.
  The drawer work is on branch `claude-fixes` (see `MODULAR_DRAWERS.md`). Trevor reviews and merges.
- Never delete, merge or overwrite anything in Onshape without Trevor's explicit OK.
- STL exports redirect to `cad-usw2.onshape.com`, which the proxy blocks: re-request the same
  `/modelexport?...` path on `cad.onshape.com`. `drawers/onshape_api.py` has a small helper (with 429 backoff).
- Exports have a **daily cap** separate from normal API calls: after ~150 STL exports in a day,
  Onshape answers 429 with `Retry-After` of ~20 h while reads still work. Don't re-export what you
  already have; identical parts can be copied between print sets.
- FeatureScript: `box` is a reserved word (`const box = ...` won't compile), and the API never returns
  compile errors: an empty `/featurespecs` list means it didn't compile. Use
  `POST /partstudios/.../featurescript` with try/catch to debug runtime errors.
- Gulbasaurus (and anything else of Enna's) is off-limits: no changes or cleanup suggestions.

## Useful endpoints (base `https://cad.onshape.com/api/v10`)

| What | Endpoint |
|---|---|
| List documents (max `limit=20`, follow `next`) | `/documents?filter=0&limit=20` |
| Document info | `/documents/{did}` |
| Branches (workspaces) | `/documents/d/{did}/workspaces` |
| Versions | `/documents/d/{did}/versions` |
| Tabs (elements) | `/documents/d/{did}/w/{wid}/elements` |
| Parts in a document | `/parts/d/{did}/w/{wid}` |
| Feature tree of a Part Studio | `/partstudios/d/{did}/w/{wid}/e/{eid}/features` |
| Mass properties | `/partstudios/d/{did}/w/{wid}/e/{eid}/massproperties` |
| Bounding box | `/partstudios/d/{did}/w/{wid}/e/{eid}/boundingboxes` |
| Variables | `/variables/d/{did}/w/{wid}/e/{eid}/variables` |
| STL export | `/partstudios/d/{did}/w/{wid}/e/{eid}/stl?units=millimeter` (follow redirect with `-L`) |

Use `v/{vid}` instead of `w/{wid}` to read a specific saved version.
Document IDs are in `INVENTORY.md`; get workspace and element IDs from the endpoints above.

## Onshape versioning in one paragraph (for explaining to Trevor)

One project = one document, with Part Studios, Assemblies and Drawings as tabs.
The **Main** workspace is live and auto-saved. A **Version** is a permanent named
snapshot (use it instead of "copy the document as a backup"). A **Branch** is a
separate workspace for experiments that can be merged back into Main. The version
graph (clock icon, bottom-left) shows all of it. Duplicating documents is the
habit to break.
