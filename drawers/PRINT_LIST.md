# Bethany's drawer: print list

Everything is in `print/`. The number to print is in each file name (`_x6` = print 6).
All parts are exported from **ModularDrawers - Claude**, Main workspace, 2026-11-19, already
standing the right way up (open side down, as drawn in Onshape).

**84 pieces, about 1 kg of PLA.** Assembled frame: 474.4 x 453.4 mm outside.

## Print a fit test first
1 x `BorderCornerConnector`, 1 x `BorderTConnector`, 1 x `TConnector`,
1 x `BorderDivider_028mm`, 1 x `Divider_028mm`. Snap them together; if the fit is good, print the rest.

## Dividers (50)
| File | Print | Where |
|---|---|---|
| BorderDivider_028mm_x3 | 3 | walls |
| BorderDivider_035mm_x4 | 4 | walls |
| BorderDivider_042mm_x6 | 6 | walls |
| BorderDivider_049mm_x1 | 1 | wall |
| BorderDivider_063mm_x1 | 1 | wall |
| BorderDivider_126mm_x1 | 1 | wall |
| BorderDivider_168mm_x1 | 1 | wall |
| BorderDivider_196mm_x1 | 1 | wall |
| BorderDivider_224mm_x1 | 1 | wall |
| BorderDivider_252mm_x1 | 1 | wall (longest piece; fits a 256 mm bed) |
| Divider_021mm_x1 | 1 | |
| Divider_028mm_x3 | 3 | |
| Divider_035mm_x4 | 4 | |
| Divider_042mm_x6 | 6 | |
| Divider_056mm_x1 | 1 | |
| Divider_077mm_x1 | 1 | |
| Divider_154mm_x2 | 2 | |
| Divider_168mm_x3 | 3 | |
| Divider_196mm_x7 | 7 | the long run from the south wall |
| **Divider_196mm_BENT_x1** | 1 | the spoon divider: 7 mm S-jog over the middle 49 mm |

## Connectors (34)
| File | Print |
|---|---|
| BorderCornerConnector_x4 | 4 |
| BorderTConnector_x16 | 16 |
| TConnector_x12 | 12 |
| **Custom_DoubleT_x1** | 1 (the "TT" spot) |
| **Custom_Step_x1** | 1 (the "T L T" spot) |

## How the three new pieces were made
- **Bent 196**: the Onshape 196 divider, sliced across its middle 49 mm and each slice slid
  sideways along a smooth S-curve (`make_bent_divider.py`). Both ends, including the plug
  sockets, are untouched (checked: 0.000 mm difference). The steepest part of the jog is 12.6°,
  so the walls there are 2.4 % thinner. Jog size and position are arguments if it needs tuning:
  `--offset 7 --transition 49 --center 0`.
- **Double T**: two of your TConnectors fused end to end, 14 mm apart, stems opposite.
- **Step**: TConnector + CornerConnector + TConnector fused, with a block of connector body
  filling the 7 mm gap (`make_custom_connectors.py`).
  In both, the plugs that would face each other are buried inside the neighbouring body;
  only the four plugs that meet real dividers stick out.

## Rebuilding
```
python3 export_print_set.py print          # standard parts from Onshape (needs the API key)
python make_bent_divider.py print/_sources/Divider_196mm.stl print/Divider_196mm_BENT_x1.stl
python make_custom_connectors.py print/_sources/TConnector.stl print/_sources/CornerConnector.stl print/_sources/StraightConnector.stl print
```
The last two need `pip install trimesh manifold3d networkx shapely scipy`.
