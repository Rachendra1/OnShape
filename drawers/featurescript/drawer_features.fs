FeatureScript 3083;
import(path : "onshape/std/common.fs", version : "3083.0");

// Drawer Features: custom features for Trevor's modular drawer dividers.
// Source of truth: drawers/featurescript/drawer_features.fs in the OnShape notes repo.

const JOG_OFFSET_BOUNDS =
{
    (meter) : [-0.2, 0.007, 0.2],
    (millimeter) : 7,
    (inch) : 0.25
} as LengthBoundSpec;

const JOG_LENGTH_BOUNDS =
{
    (meter) : [0.002, 0.049, 1],
    (millimeter) : 49,
    (inch) : 2
} as LengthBoundSpec;

const PLACE_BOUNDS =
{
    (meter) : [-1, 0, 1],
    (millimeter) : 0,
    (inch) : 0
} as LengthBoundSpec;

const CLIP_BOUNDS =
{
    (meter) : [0, 0, 1],
    (millimeter) : 0,
    (inch) : 0
} as LengthBoundSpec;

/**
 * S-bend divider.
 * Takes a straight divider that runs along Y, centred on the origin, open side down
 * (exactly how the Divider Part Studio builds it). Keeps both ends, plug sockets included,
 * and replaces the middle with a sweep of the divider's own cross-section along two
 * tangent arcs, so the far end ends up shifted sideways by the jog offset.
 */
annotation { "Feature Type Name" : "S-bend divider",
             "Feature Type Description" : "Puts a sideways S-jog in a straight divider. Ends and plug sockets stay exactly as they were." }
export const sBendDivider = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Straight divider", "Filter" : EntityType.BODY && BodyType.SOLID, "MaxNumberOfPicks" : 1 }
        definition.divider is Query;

        annotation { "Name" : "Jog offset (sideways, + is toward +X)" }
        isLength(definition.offset, JOG_OFFSET_BOUNDS);

        annotation { "Name" : "Jog length (along the divider)" }
        isLength(definition.jogLength, JOG_LENGTH_BOUNDS);

        annotation { "Name" : "Jog centre (from the middle, + is toward +Y)" }
        isLength(definition.center, PLACE_BOUNDS);
    }
    {
        const d = definition.offset;
        const L = definition.jogLength;
        if (abs(d) < 1e-6 * meter)
            return; // nothing to bend

        const bb = evBox3d(context, { "topology" : definition.divider, "tight" : true });  // ("box" is reserved)
        const y0 = definition.center - L / 2;
        const y1 = definition.center + L / 2;
        if (y0 < bb.minCorner[1] + 10 * millimeter || y1 > bb.maxCorner[1] - 10 * millimeter)
            throw regenError("Keep the jog at least 10 mm from both ends (that's where the plug sockets are).",
                             ["jogLength", "center"]);

        // 1. Cut the divider at both ends of the jog.
        opPlane(context, id + "plane0", { "plane" : plane(vector(0 * meter, y0, 0 * meter), vector(0, 1, 0)) });
        opPlane(context, id + "plane1", { "plane" : plane(vector(0 * meter, y1, 0 * meter), vector(0, 1, 0)) });
        opSplitPart(context, id + "split0", {
                    "targets" : definition.divider,
                    "tool" : qCreatedBy(id + "plane0", EntityType.FACE) });
        const afterFirst = qBodyType(qUnion([definition.divider, qCreatedBy(id + "split0", EntityType.BODY)]), BodyType.SOLID);
        opSplitPart(context, id + "split1", {
                    "targets" : afterFirst,
                    "tool" : qCreatedBy(id + "plane1", EntityType.FACE) });
        const allPieces = qBodyType(qUnion([afterFirst, qCreatedBy(id + "split1", EntityType.BODY)]), BodyType.SOLID);

        var south;
        var north;
        var middle = [];
        for (var piece in evaluateQuery(context, allPieces))
        {
            const b = evBox3d(context, { "topology" : piece, "tight" : true });
            const cy = (b.minCorner[1] + b.maxCorner[1]) / 2;
            if (cy < y0)
                south = piece;
            else if (cy > y1)
                north = piece;
            else
                middle = append(middle, piece);
        }
        if (south == undefined || north == undefined || size(middle) == 0)
            throw regenError("Couldn't cut the divider into three pieces. Is it a straight divider along Y, centred on the origin?");

        // 2. The cross-section to sweep is the south piece's cut face.
        const profile = qCoincidesWithPlane(qOwnedByBody(south, EntityType.FACE),
                                            plane(vector(0 * meter, y0, 0 * meter), vector(0, 1, 0)));
        opDeleteBodies(context, id + "dropMiddle", { "entities" : qUnion(middle) });

        // 3. Path: two tangent arcs forming an S from (0, y0) to (d, y1), on the floor (Z = 0).
        const s = d > 0 * meter ? 1 : -1;
        const ad = abs(d);
        const R = (L * L + ad * ad) / (4 * ad);
        const theta = asin(L / (2 * R));
        const yc = (y0 + y1) / 2;
        // arc 1 starts at (0, y0) heading +Y; arc 2 is arc 1 turned 180 degrees about the S's midpoint
        const p0 = vector(0 * meter, y0);
        const pm1 = vector(s * (R - R * cos(theta / 2)), y0 + R * sin(theta / 2));
        const pc = vector(s * (R - R * cos(theta)), y0 + R * sin(theta));
        const pm2 = vector(s * ad - pm1[0], 2 * yc - pm1[1]);
        const p1 = vector(s * ad, y1);

        const sketch = newSketchOnPlane(context, id + "path", {
                    "sketchPlane" : plane(vector(0, 0, 0) * meter, vector(0, 0, 1), vector(1, 0, 0)) });
        skArc(sketch, "arc1", { "start" : p0, "mid" : pm1, "end" : pc });
        skArc(sketch, "arc2", { "start" : pc, "mid" : pm2, "end" : p1 });
        skSolve(sketch);

        // 4. Sweep the cross-section along the S.
        opSweep(context, id + "sweep", {
                    "profiles" : profile,
                    "path" : qCreatedBy(id + "path", EntityType.EDGE) });

        // 5. Slide the north end over and fuse everything into one part.
        opTransform(context, id + "moveNorth", { "bodies" : north, "transform" : transform(vector(d, 0 * meter, 0 * meter)) });
        opBoolean(context, id + "fuse", {
                    "tools" : qUnion([south, qCreatedBy(id + "sweep", EntityType.BODY), north]),
                    "operationType" : BooleanOperationType.UNION });

        // 6. Tidy up construction geometry.
        opDeleteBodies(context, id + "cleanup", { "entities" : qUnion([
                            qCreatedBy(id + "plane0", EntityType.BODY),
                            qCreatedBy(id + "plane1", EntityType.BODY),
                            qCreatedBy(id + "path", EntityType.BODY)]) });
    });

/**
 * Place body: rotate a body about the Z axis through the origin, then move it in X/Y.
 * "Place a copy" leaves the original alone, so one Derive can be used twice.
 * Optional trim keeps only the part within +/- trim of the origin along Y (before rotating),
 * which turns a connector into a plug-free block of connector body.
 */
annotation { "Feature Type Name" : "Place body",
             "Feature Type Description" : "Rotate about Z, then move in X/Y. Optionally trim to +/- a distance along Y first." }
export const placeBody = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Bodies", "Filter" : EntityType.BODY && BodyType.SOLID }
        definition.bodies is Query;

        annotation { "Name" : "Rotate about Z" }
        isAngle(definition.angle, ANGLE_360_ZERO_DEFAULT_BOUNDS);

        annotation { "Name" : "Move X" }
        isLength(definition.x, PLACE_BOUNDS);

        annotation { "Name" : "Move Y" }
        isLength(definition.y, PLACE_BOUNDS);

        annotation { "Name" : "Trim to +/- along Y (0 = no trim)" }
        isLength(definition.trim, CLIP_BOUNDS);

        annotation { "Name" : "Place a copy (keep the original where it is)" }
        definition.copy is boolean;
    }
    {
        var bodies = definition.bodies;
        if (definition.copy)
        {
            opPattern(context, id + "copy", { "entities" : bodies, "transforms" : [identityTransform()], "instanceNames" : ["1"] });
            bodies = qCreatedBy(id + "copy", EntityType.BODY);
        }
        if (definition.trim > 0 * meter)
        {
            // Cut away everything beyond +/- trim along Y (subtracting keeps the body's identity).
            fCuboid(context, id + "cutSouth", {
                        "corner1" : vector(-1, -1, -1) * meter,
                        "corner2" : vector(1 * meter, -definition.trim, 1 * meter) });
            fCuboid(context, id + "cutNorth", {
                        "corner1" : vector(-1 * meter, definition.trim, -1 * meter),
                        "corner2" : vector(1, 1, 1) * meter });
            opBoolean(context, id + "trim", {
                        "tools" : qUnion([qCreatedBy(id + "cutSouth", EntityType.BODY), qCreatedBy(id + "cutNorth", EntityType.BODY)]),
                        "targets" : bodies,
                        "operationType" : BooleanOperationType.SUBTRACTION });
        }
        const zAxis = line(vector(0, 0, 0) * meter, vector(0, 0, 1));
        opTransform(context, id + "place", {
                    "bodies" : bodies,
                    "transform" : transform(vector(definition.x, definition.y, 0 * meter)) * rotationAround(zAxis, definition.angle) });
    });

/**
 * Name by length: sets the part Description to "<prefix> <length> mm" on every regeneration,
 * so each configuration of a divider describes its own length and the BOM shows it.
 * (Description, not Name: a name typed in by hand always wins over one set by a feature.)
 */
annotation { "Feature Type Name" : "Name by length",
             "Feature Type Description" : "Sets the part Description to \"<prefix> <length> mm\" so the BOM shows each length." }
export const nameByLength = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Parts", "Filter" : EntityType.BODY && BodyType.SOLID }
        definition.parts is Query;

        annotation { "Name" : "Name prefix", "Default" : "Divider" }
        definition.prefix is string;

        annotation { "Name" : "Length" }
        isLength(definition.length, NONNEGATIVE_LENGTH_BOUNDS);
    }
    {
        const mm = round(definition.length / millimeter);
        setProperty(context, {
                    "entities" : definition.parts,
                    "propertyType" : PropertyType.DESCRIPTION,
                    "value" : definition.prefix ~ " " ~ toString(mm) ~ " mm" });
    });

const DROP_BOUNDS =
{
    (meter) : [0, 0.006, 0.1],
    (millimeter) : 6,
    (inch) : 0.25
} as LengthBoundSpec;

const LOW_LENGTH_BOUNDS =
{
    (meter) : [0.001, 0.078, 1],
    (millimeter) : 78,
    (inch) : 3
} as LengthBoundSpec;

const RAMP_BOUNDS =
{
    (meter) : [0.001, 0.02, 1],
    (millimeter) : 20,
    (inch) : 0.75
} as LengthBoundSpec;

/**
 * Lower middle: dips the top of a divider in the middle so things are easier to reach.
 * Works on a divider along Y, open side down (straight or S-bent). Cuts it across at the
 * ends of the ramps and of the low stretch, sinks the low stretch by the drop, rebuilds each
 * ramp by sliding the divider's own cross-section down a slope, fuses everything and trims
 * off whatever went below the floor. The ends (with the plug sockets) are untouched, the
 * walls keep their thickness, and the top keeps its rounded shape. Ramps must be straight
 * (outside any S-bend).
 */
annotation { "Feature Type Name" : "Lower middle",
             "Feature Type Description" : "Dips the middle of a divider down by a set amount, with sloped ramps either side." }
export const lowerMiddle = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Divider", "Filter" : EntityType.BODY && BodyType.SOLID, "MaxNumberOfPicks" : 1 }
        definition.divider is Query;

        annotation { "Name" : "Drop (how much lower)" }
        isLength(definition.drop, DROP_BOUNDS);

        annotation { "Name" : "Low stretch (flat bottom of the dip)" }
        isLength(definition.lowLength, LOW_LENGTH_BOUNDS);

        annotation { "Name" : "Ramp length (each side)" }
        isLength(definition.ramp, RAMP_BOUNDS);
    }
    {
        const drop = definition.drop;
        if (drop > 1e-6 * meter)
        {
            const bb = evBox3d(context, { "topology" : definition.divider, "tight" : true });
            const yMid = (bb.minCorner[1] + bb.maxCorner[1]) / 2;
            const y1 = definition.lowLength / 2;
            const y2 = y1 + definition.ramp;
            if (yMid - y2 < bb.minCorner[1] + 10 * millimeter || yMid + y2 > bb.maxCorner[1] - 10 * millimeter)
                throw regenError("The dip plus its ramps must stay at least 10 mm from both ends (plug sockets).",
                                 ["lowLength", "ramp"]);
            if (drop >= bb.maxCorner[2] - bb.minCorner[2])
                throw regenError("The drop must be less than the divider's height.", ["drop"]);

            // 1. Cut across at four places: ramp start, low start, low end, ramp end.
            const ys = [yMid - y2, yMid - y1, yMid + y1, yMid + y2];
            var pieces = definition.divider;
            for (var i = 0; i < 4; i += 1)
            {
                opPlane(context, id + ("plane" ~ i), { "plane" : plane(vector(0 * meter, ys[i], 0 * meter), vector(0, 1, 0)) });
                opSplitPart(context, id + ("split" ~ i), {
                            "targets" : pieces,
                            "tool" : qCreatedBy(id + ("plane" ~ i), EntityType.FACE) });
                pieces = qBodyType(qUnion([pieces, qCreatedBy(id + ("split" ~ i), EntityType.BODY)]), BodyType.SOLID);
            }

            var southEnd;
            var southRamp;
            var low;
            var northRamp;
            var northEnd;
            for (var piece in evaluateQuery(context, pieces))
            {
                const pb = evBox3d(context, { "topology" : piece, "tight" : true });
                const cy = (pb.minCorner[1] + pb.maxCorner[1]) / 2;
                if (cy < ys[0])
                    southEnd = piece;
                else if (cy < ys[1])
                    southRamp = piece;
                else if (cy < ys[2])
                    low = piece;
                else if (cy < ys[3])
                    northRamp = piece;
                else
                    northEnd = piece;
            }
            if (southEnd == undefined || southRamp == undefined || low == undefined || northRamp == undefined || northEnd == undefined)
                throw regenError("Couldn't cut the divider into five pieces. Is it a divider along Y?");

            // 2. Cross-sections the ramps start from: the cut faces of the two end pieces.
            const southFace = qCoincidesWithPlane(qOwnedByBody(southEnd, EntityType.FACE),
                                                  plane(vector(0 * meter, ys[0], 0 * meter), vector(0, 1, 0)));
            const northFace = qCoincidesWithPlane(qOwnedByBody(northEnd, EntityType.FACE),
                                                  plane(vector(0 * meter, ys[3], 0 * meter), vector(0, 1, 0)));
            opDeleteBodies(context, id + "dropRamps", { "entities" : qUnion([southRamp, northRamp]) });

            // 3. Sink the low stretch.
            opTransform(context, id + "sink", { "bodies" : low, "transform" : transform(vector(0 * meter, 0 * meter, -drop)) });

            // 4. Ramps: slide each end's cross-section along the slope down to the sunk piece.
            const slope = drop / definition.ramp;
            const rampDepth = sqrt(definition.ramp * definition.ramp + drop * drop);
            opExtrude(context, id + "rampSouth", {
                        "entities" : southFace,
                        "direction" : normalize(vector(0, 1, -slope)),
                        "endBound" : BoundingType.BLIND,
                        "endDepth" : rampDepth });
            opExtrude(context, id + "rampNorth", {
                        "entities" : northFace,
                        "direction" : normalize(vector(0, -1, -slope)),
                        "endBound" : BoundingType.BLIND,
                        "endDepth" : rampDepth });

            // 5. Fuse, then trim off anything below the floor (Z = 0).
            const all = qUnion([southEnd, qCreatedBy(id + "rampSouth", EntityType.BODY), low,
                                qCreatedBy(id + "rampNorth", EntityType.BODY), northEnd]);
            opBoolean(context, id + "fuse", { "tools" : all, "operationType" : BooleanOperationType.UNION });
            fCuboid(context, id + "belowFloor", {
                        "corner1" : vector(-1, -1, -1) * meter,
                        "corner2" : vector(1 * meter, 1 * meter, bb.minCorner[2]) });
            opBoolean(context, id + "floor", {
                        "tools" : qCreatedBy(id + "belowFloor", EntityType.BODY),
                        "targets" : qBodyType(all, BodyType.SOLID),
                        "operationType" : BooleanOperationType.SUBTRACTION });

            // 6. Tidy up.
            opDeleteBodies(context, id + "cleanup", { "entities" : qUnion([
                                qCreatedBy(id + "plane0", EntityType.BODY), qCreatedBy(id + "plane1", EntityType.BODY),
                                qCreatedBy(id + "plane2", EntityType.BODY), qCreatedBy(id + "plane3", EntityType.BODY)]) });
        }
    });
