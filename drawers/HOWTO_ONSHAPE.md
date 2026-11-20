# How to build a drawer layout (and its parts list) in Onshape

Worked example: **Bethany's Drawer - full layout** on the `claude-fixes` branch of
*ModularDrawers - Claude*. Open it, then open its BOM tab: that table is the print list.

## The idea in one line
Make every piece a **configured part**, put each one in an **assembly** at the length it needs,
and let the **BOM** count them. Your paper tally is exactly what the BOM does for free.

## 1. Configured parts (you already had this)
`Divider` and `BorderDivider` each have a `DividerLength` configuration input. That's the key move:
one Part Studio makes every length.

Two small additions on the branch make the BOM readable:
- **Name by length** (a custom feature at the bottom of Divider, BorderDivider and BentDivider)
  writes "Divider 196 mm" into the part's *Description* for whatever length is chosen. Without it,
  every row in the BOM just says "Divider".
  (It writes Description, not Name, because a name you've typed by hand always wins.)
- **BorderTConnector** was two separate solids (the wall piece and a "StraightHalf" stem), so the BOM
  would have counted 32 parts for 16 border Ts. A Boolean union at the end makes it one part.

## 2. Put the pieces in an assembly
**Insert** (the + icon) → pick the Part Studio → set the configuration (e.g. DividerLength 196 mm) →
click to drop it in. Insert the same length several times by clicking repeatedly.

Then position them. Two ways:

**a. Snap them together with mates (the "real" way, best for designing).**
Your connectors and dividers have no mate connectors yet, which is why the old assembly had 18
parts and 1 mate. Fix that once, in each Part Studio:
1. In TConnector, BorderTConnector, BorderCornerConnector, etc., add a **Mate connector** at the
   base of each plug, Z up, X pointing out along the plug.
2. In Divider / BorderDivider, add a mate connector at the centre of each end face (Z up, X pointing
   out of the end). Use `#DividerLength/2` for its position so it follows the length.
3. In the assembly, a **Fastened mate** between a plug's connector and a divider end's connector
   snaps the divider onto the plug, like Lego. Build outward from one fixed corner.
With that, changing a length in the assembly moves everything after it automatically.

**b. Place them by coordinates (what I did, quickest from a finished sketch).**
I worked out every connector's centre from your drawing (X along the 35B-28B wall, Y along
the wall with 252B, 14 mm per connector) and moved each part there. That's
`build_assembly_onshape.py` + `bethany_layout.py` in the repo. Parts placed this way aren't mated,
so if you drag one it moves; select all → right-click → **Fix** to lock them.

## 3. The BOM is your parts list
Open the **BOM** tab of the assembly. Identical part + length rows are grouped and counted, and the
Description column shows the length. For this drawer it reads 10 border lengths, 11 interior lengths
(including the bent one), 4 corners, 16 border Ts, 12 Ts and the 2 custom connectors: **84 pieces**,
matching your tally.

To print: right-click a Part Studio tab → *Export* with the configuration set to the length you need,
or right-click the part in the assembly → *Export*. (The repo script `export_print_set.py` does all of
them in one go.)

## 4. The bend, double T and step, as features
These live in the **Drawer Features** Feature Studio (FeatureScript; the source is also in
`featurescript/drawer_features.fs`):
- **S-bend divider**: takes a straight divider, keeps both ends exactly, replaces the middle with a
  sweep of the divider's own cross-section along two tangent arcs. *BentDivider* = Derive(Divider at
  `#DividerLength`) → S-bend(`#JogOffset`, `#JogLength`, `#JogCenter`). Change the configuration to
  make any bent divider; it errors (red) if the jog would hit the plug sockets.
- **Place body**: rotate about Z, then move, optionally a copy and optionally trimmed. *DoubleTConnector*
  and *StepConnector* are Derive → Place body → Boolean union, nothing else.
- **Name by length**: described above.

## 5. Reviewing and merging the branch
Everything is on the branch **claude-fixes**. Main is untouched, and there's a version
**"Before Claude edits"** of how Main looked before.
1. Open the document → version graph (clock icon, bottom-left) → double-click **claude-fixes**.
2. Look around: new tabs *BentDivider*, *DoubleTConnector*, *StepConnector*, *Drawer Features*,
   *Bethany's Drawer - full layout*. Changed tabs: *Divider*, *BorderDivider* (Name by length added),
   *BorderTConnector* (fused).
3. Delete the tab **"UNUSED - delete me"** (a failed first try; my key can't delete).
4. Happy? Switch to Main, then in the version graph right-click **claude-fixes** → *Merge into
   current workspace*. Not happy? Just ignore or delete the branch; Main never changed.

## Next time, faster
Sketch the layout on the 7 mm grid as **centre lines**, mark each junction (BL, BT, T, X, L), and
remember: **divider length = centre-to-centre distance − 14 mm**. Then either type the layout into
`bethany_layout.py` (positions + which junctions connect) and run the two scripts, or build it with
mates as in 2a.
