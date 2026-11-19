# Onshape model work: agent briefing

This repo holds notes for finishing and cleaning up Trevor's Onshape CAD models.
The models live in Onshape, not here. Read `INVENTORY.md` first: it lists every
document, what is in it, and the cleanup recommendations.

## Talking to Onshape

- An Onshape API key (read-only, Basic auth) is saved as a network secret on this
  cloud environment for `cad.onshape.com`. The proxy injects it automatically.
  Do **not** add an Authorization header yourself; plain `curl` works:
  ```bash
  curl -sS -H "Accept: application/json" "https://cad.onshape.com/api/v10/users/sessioninfo"
  ```
  401 `invalid_token` means the secret is wrong or was saved as Bearer instead of Basic.
- The key is **read-only**. Do not attempt writes; propose changes for Trevor to make
  in Onshape (or ask him for a write-enabled key).
- Never delete, merge or overwrite anything in Onshape without Trevor's explicit OK.
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
