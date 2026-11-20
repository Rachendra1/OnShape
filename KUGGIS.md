# Kuggis Shelf: stacked-print setup

Doc: https://cad.onshape.com/documents/42847d9d152b50fb60843d72

Goal: print many IKEA Kuggis box dividers in one unattended job on the Bambu A1 by
stacking them and alternating materials, so neighbouring dividers don't fuse.

## Changes made 2026-11-20 (via API)

Backup first: version **V1.1 - before print-ready changes** = the state before any of this.
Version **V2 - print-ready, 1.0 mm (Small x9, Large x11)** = these changes with Large at 11; Main now has Large at 16.

| Where | Was | Now | Why |
|---|---|---|---|
| Variable Studio `Depth` | 0.96 mm | 1.0 mm | 5 whole layers at the A1's default 0.20 mm (first layer 0.20 too), so every material change lands on a layer boundary |
| `Depth_Notch` | `#Depth/6` (0.16 mm) | 0.2 mm | One full layer per face, so the slicer actually prints it. Stacked gap = 0.4 mm |
| `Notch_Size` | 4 mm | 8 mm | Notch is a circle centred on the edge: now 8 mm wide x 4 mm in, which fits a small flat screwdriver |
| New `Small_Stack_Count` / `Large_Stack_Count` | – | 9 / 16 (Large was 11 in V2) | How many dividers in each print stack (1 = single divider) |
| Large, InsertPieceLarge: Extrude 1 depth | typed 0.96 mm | `#Depth` | Large now follows the variable like Small does |
| Small, Large: new **Print stack** feature | – | Linear pattern up the Z axis, spacing `#Depth`, count = stack count | Exactly stacked, separate parts, no gaps, no XY drift |

Result checked via API: Small = 9 parts, 158.75 x 114.3 x 9.000 mm; Large = 11 parts (now 16 parts, 16.000 mm tall),
244.48 x 158.75 x 11.000 mm; each part 1.000 mm thick.

Not changed (now redundant, delete when happy): `InsertPieceSmall`, `InsertPieceLarge`,
`StackedSmall`, `StackedLarge`, `Both Sizes` and their BOMs. The stacked assemblies had a
0.04 mm gap at the bottom and one Large insert rotated 180°; the pattern replaces them.

## Printing

1. Export the **Small** or **Large** Part Studio as STEP (right-click tab → Export).
2. Bambu Studio: import, and answer **Yes** to "load as a single object with multiple parts".
3. Objects panel: alternate filaments per part, **PLA / PETG / PLA / ...**. Two colours of the
   same plastic will fuse; PLA and PETG peel apart.
4. Profile: 0.20 mm Standard (initial layer 0.20). Textured PEI plate. Accept the bed-temp warning.
5. First run: set the stack count to 3 and check the corners don't curl up off the layer below.

No air gap between dividers: a gap smaller than a layer is ignored by the slicer, and a full-layer
gap leaves the next divider printing on air. The PLA/PETG pairing plus the 0.4 mm notch handle separation.
