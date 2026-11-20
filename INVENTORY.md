# Onshape inventory and cleanup recommendations

Pulled 2026-11-19 via the API. 19 documents, all owned by Trevor, **all set to public**.
Doc URL pattern: `https://cad.onshape.com/documents/{id}`

These recommendations are proposals only; nothing has been changed in Onshape.

## Project families (where the duplicates are)

### 1. Modular Drawers: 3 documents, one project
| Doc | ID | Created | Last edit | Versions | Notes |
|---|---|---|---|---|---|
| **ModularDrawers - Claude** | `c1f3594b6f062bbce36ab673` | 2026-07-26 | 2026-08-09 | Start, V2 (08-09) | Newest. A copy of the ChatGPT doc (created the day that doc was last edited), plus Profile2, Bend2, Part Studio 2, GlobalParams |
| ModularDrawersChatGPT | `93c066e8868e2324be9971fd` | 2025-10-20 | 2026-07-26 | Start, V2, V2 (duplicate name), V3, V4 | Older line of the same design |
| ModularDrawers | `9503c2c8a1eb860fdb39e29c` | 2025-10-19 | 2025-10-20 | Start, V1 | First attempt; different approach (Feature Studio, "_old" tabs) |

**Recommendation:** Treat **ModularDrawers - Claude** as the master; rename it to "Modular Drawers".
Confirm nothing in the ChatGPT doc's Main is missing from it, then archive the other two
(move them to an "Archive" folder; no need to delete). The "Claude" doc also has
cleanup inside: two tabs called `Divider`, plus `Divider2`, `BendRight Copy 1`, `Part Studio 1/2`,
and `TestAssembly` vs `Assembly 1` vs `Bethany's Drawer`.

### 2. Ryobi battery holder: 5 documents, one project
| Doc | ID | Last edit | Notes |
|---|---|---|---|
| **RyobiUpdatedTemplate** | `6d989bab59da353669ec293c` | 2026-09-08 | Most recent and most complete: BatteryWithBase, BatteryHolder and Battery2 assemblies, NEWBATTERY.obj |
| Test | `052f6f67c2bea7fa94c813b7` | 2025-09-22 | Earlier copy of the same imported STLs (Template Plate (1)(2)(3)) |
| Trevor Test | `18764068bbc3b70b7affd8c6` | 2025-09-19 | Earlier copy |
| Ryobi_Single_Holder_Flat.stl | `1289a66f2e552a25ac638832` | 2025-09-19 | Raw STL import |
| Template Plate.stl | `fd3bc68c5cfbe4059752ed08` | 2025-09-19 | Raw STL import |

**Recommendation:** Keep **RyobiUpdatedTemplate** and rename it to "Ryobi Battery Holder". Archive the other four.
Inside it: delete the duplicate `Template Plate (1)/(2)` tabs once confirmed unused, and rename
`Part Studio 1` and `Assembly 1`. Note that the work is mesh imports (STL/OBJ); for a properly
editable model these parts may need to be remodeled as native features.

### 3. Kitchen / room layout: 2 related documents
| Doc | ID | Last edit | Notes |
|---|---|---|---|
| Cabinets | `3e1ef31fbbad4a6a0d49fbc1` | 2025-11-25 | Full room: 26 named parts (cabinets, appliances, counters, lights) |
| Wall | `049dd78c6cfd4b5a1234e1e8` | 2025-12-06 | Wall, Shelving, CounterTop, Cabinet studios; variables |

**Recommendation:** Ask Trevor whether these are the same room. If so, merge into one doc.
Otherwise keep both and rename them clearly.

## Standalone projects (no duplicates)
| Doc | ID | Last edit | Versions | Notes |
|---|---|---|---|---|
| Template - Drills | `5701b1312b7fbdbe4e0193b5` | 2026-01-12 | Start, V1, V2, V3 | ⚠️ **Branch `B1` (edited 01-12) is newer than `Main` (01-09).** Work may be stranded on B1; review and merge into Main. Contents are drawer and door handles/knobs, so the name doesn't fit; consider renaming |
| MakaylasPresent | `74ad69d9b4bf0ff703752d44` | 2025-12-19 | Start, V3, V4 | 1 part, 2 drawings, variables. Looks finished |
| Kuggis Shelf | `42847d9d152b50fb60843d72` | 2026-11-20 | Start, V1, V1.1, V2 | Small and Large inserts. Made print-ready 2026-11-20; see `KUGGIS.md` |
| Boomer phone stand - Copy | `bf1bd8d19d5b57a5b086aaaf` | 2025-12-19 | Start | Copy of someone else's public doc (original isn't Trevor's); rename it to drop "- Copy" |

## Throwaway / empty: archive or delete
| Doc | ID | Notes |
|---|---|---|
| Assembly_BellSilverware | `fdec9fd523912a313be13a59` | 0 parts. Empty; ask whether it was meant to be something |
| Untitled document | `f84e4146cdb7197e2349caaa` | 0 parts |
| Gulbasaurus | `849157e8704ec732ffe045c3` | 1 part, never versioned; ask |
| experiment number one | `de20480606050eab5f5f0151` | Learning exercise |
| try one | `2c83dc0b9a53e80407df857b` | Learning exercise |

## General recommendations
1. **Stop copying documents.** Make a Version instead ("V3 – thicker walls"), or a Branch to experiment.
2. **Version names:** ModularDrawersChatGPT has two versions both called "V2". Give versions descriptive names.
3. **Privacy:** every document is public. Switch personal ones (e.g. MakaylasPresent, the kitchen) to private if that wasn't intended.
4. **Folders:** create `Active`, `Archive` and `Learning` folders in the Onshape documents page.
5. **Tab names:** rename `Part Studio 1` / `Assembly 1` / `Part 1` to what they actually are.

## Open questions for Trevor
- Which models are top priority to finish, and what does "done" mean for each (print, drawing, fit check)?
- Are Cabinets and Wall the same room?
- What is on the `B1` branch of Template - Drills that isn't in Main?
- Gulbasaurus and Assembly_BellSilverware: keep or drop?
