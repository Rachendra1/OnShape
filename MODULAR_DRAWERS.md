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

## Needed from Trevor

- Pictures of the design, with compartment sizes (or which ones are equal).
- Drawer **inside** width, depth and height (dividers are 20 mm tall; is that right for this drawer?).
- Printer and bed size.
- Any curved or lowered dividers in her design?
