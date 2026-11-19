# Modular Drawers: how the system works and what's left

Reviewed 2026-11-19 from **ModularDrawers - Claude** (`c1f3594b6f062bbce36ab673`), Main workspace.
Nothing in Onshape was changed.

## The system (what already works)

Dividers are hollow A-frame walls, open at the bottom: **20 mm tall, 12 mm wide at the base, 5 mm rounded top**
(`height`, `width_bottom`, `width_top` in GlobalParams). Connectors are hubs with tapered plugs and a
snap bump; the plugs slide into the open ends of the dividers. "Border" pieces are the same shape cut off
flat on one side to sit against the drawer wall.

| Tab | Part | Use | Configurable |
|---|---|---|---|
| Divider | Divider | Interior wall | `DividerLength` (0–256 mm) |
| BorderDivider | BDDivider | Wall piece against the drawer side | `DividerLength` (0–256 mm) |
| XConnector | XConnector | 4-way interior crossing | no |
| TConnector | TConnector | 3-way interior junction | no |
| CornerConnector | CornerConnector | Interior L | no |
| StraightConnector | StraightConnector | Join two interior dividers in a line (long runs) | no |
| StraightHalfConnector | StraightHalf | Dead-end cap for a divider that stops mid-drawer | no |
| BorderCornerConnector | BDCorner | Drawer corner | no |
| BorderTConnector | BDTConnector | Interior divider meets the wall | no |
| BorderStraightConnector | BDStraightCon | Join two border dividers along a wall | no |

That is a complete set for any rectangular (straight-line) layout.

## Measured geometry (from STL exports)

Every connector is built around a node point:
- Connector body extends **6.99 mm** from the node along each arm; plugs reach 16.33 mm.
- Border pieces' flat back is **2.72 mm** from the divider centerline.

So, drawing the layout as centerlines:
- Outer loop of centerlines sits **2.72 mm inside** the drawer walls.
- **Divider length = node-to-node distance − 13.98 mm** (call it 14).
- A plain wall with only corners: border divider = interior wall length − 19.42 mm − clearance.
- Divider length is capped at 256 mm in the configuration (likely the print bed). Longer runs are
  split with a Straight / BorderStraight connector (which also costs 14 mm).

STL export works through the read-only API key at any `DividerLength`
(the export redirects to `cad-usw2.onshape.com`, which is blocked; re-request the same
`/modelexport?...` path on `cad.onshape.com` instead).

## Problems found

- **Bethany's Drawer is a pile of parts, not a layout**: 4 BDCorner + 14 BDDivider (28/35/42/252 mm),
  1 mate, no T or X connectors. It can't be checked for fit as-is.
- **Bend, Bend2, BendRight, BendRight Copy 1 don't produce a solid** (only a wire curve, or nothing).
  The curved/lowered divider idea is unfinished.
- Bend2's configuration labels don't match their variables (`StraightFactor` is labelled "Bend",
  `RaisedFactor1` "Lower", `Lower1Factor` "Lowered", `Lower2Factor` "Raise").
- GlobalParams `snap_height_factor` and CalculatedParams `bendlength` are blank, yet `snap_radius`
  uses `snap_height_factor`.
- Leftover/empty tabs: `Part Studio 1` (one sketch), `Part Studio 2` (one derive, no part), second
  `Divider` and `Divider2` (just a profile sketch), `Profile_Template`, `Profile2`, `BendRight Copy 1`,
  `TestAssembly`, `Assembly 1`.

## Recommendations

1. **Finish line = straight-line dividers only.** Make a Version now ("V3 – straight system print-ready").
   Move the Bend experiments to a branch; don't let them block the gift.
2. **Design → parts is a calculation, not a new model**: layout → list of nodes (corner, T, X, …) and
   segments → divider length = segment − 14 mm → export each STL at its length. This can be done
   from a dimensioned sketch of the design plus the drawer's inside measurements.
3. **Print a fit test first**: one BDCorner + one short BDDivider + one TConnector + one Divider.
   Check the snap (`gap` 0.15, `gap_top` 0.16) on the actual printer before printing everything.
4. **Leave clearance**: aim ~1–2 mm short per wall so the frame drops in.
5. **Later (the fun part)**: a Feature Studio custom feature that takes a layout sketch and generates
   every piece, or a Bethany's Drawer assembly that's actually mated as a visual check.

## Bethany's drawer: the hand-drawn layout (photos 2026-11-19)

Encoded in `drawers/bethany_layout.py` (run it for the parts list; `drawers/bethany_layout.png` is
the layout drawn back). Every count matches Trevor's tally on the sketch:

- Border: 28B x3, 35B x4, 42B x6, 49B, 63B, 126B, 168B, 196B, 224B, 252B (20 pieces)
- Interior: 21, 28 x3, 35 x4, 42 x6, 56, 77, 154 x2, 168 x3, 196 x8 (7 + the bent one), 224 (30 pieces)
- Connectors: BL x4, BT x16, T x12, plus the special spots below
- Assembled frame outside: **474.4 x 453.4 mm** (south wall x west wall). Nothing over 256 mm,
  so no straight joiners are needed.
- Material: about 820 cm3 of plastic, roughly **1 kg of PLA**.

Three spots the current parts can't build:

1. **"196 L?" bent divider** (from the 35B/42B border-T on the south wall): jogs 7 mm over its length.
   The Bend studios don't make a solid yet. Straightening it costs nothing: move that border T
   7 mm (swap the 35B and 42B on the south wall, or the 42 and 35 in the row above). Same parts list.
2. **"TT"** (where the 224 from the north wall meets the 196 from the south wall): two Ts 14 mm
   apart, so the divider between them would be 0 mm. Fix: one custom "double T" = two TConnectors
   fused end to end (a 10-minute Part Studio: derive TConnector twice, rotate one 180°, move 14 mm,
   union). Or move the 224 over 14 mm so it becomes a standard X (north wall 49B/28B -> 35B/42B,
   east-side 28 -> 42).
3. **"T L T" step** (end of the 21, under the two 154s): the lines are 21 mm apart one way and
   14 mm the other, leaving 0 mm and 7 mm gaps; dividers need at least ~19 mm (plugs go 9.3 mm in
   each end). Fix: one custom "step" connector (both Ts plus a short solid bar between them), or
   rework that corner of the layout.

## Needed from Trevor

- Pictures of the design, with compartment sizes (or which ones are equal).
- Drawer **inside** width, depth and height (dividers are 20 mm tall; is that right for this drawer?).
- Printer and bed size.
- Any curved or lowered dividers in her design?
