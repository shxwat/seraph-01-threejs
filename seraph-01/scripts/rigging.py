"""Object hierarchy, mechanical joints, deterministic animation primitives."""
import bpy
import bmesh
from mathutils import Vector

COLLECTION = None


def collection(name):
    global COLLECTION
    c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    COLLECTION = c
    return c


def link(obj):
    (COLLECTION or bpy.context.scene.collection).objects.link(obj)
    return obj


def empty(name, location=(0, 0, 0), parent=None):
    o = link(bpy.data.objects.new(name, None)); o.location = location; o.parent = parent
    o.empty_display_type = 'PLAIN_AXES'; o.empty_display_size = .18
    return o


def mesh_object(name, verts, faces, material, parent=None, bevel=0):
    me = bpy.data.meshes.new(name + ' · mesh'); me.from_pydata(verts, [], faces); me.update()
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o = link(bpy.data.objects.new(name, me)); o.parent = parent
    if material: me.materials.append(material)
    if bevel:
        mod = o.modifiers.new('Machined edge radii', 'BEVEL'); mod.width = bevel; mod.segments = 2
    return o


def linked(source, name, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1), parent=None):
    o = link(bpy.data.objects.new(name, source.data)); o.parent = parent
    o.location, o.rotation_euler, o.scale = location, rotation, scale
    return o


def key(obj, attr, frame, value):
    setattr(obj, attr, value); obj.keyframe_insert(data_path=attr, frame=frame)


def animate_assembly(obj, target, start, end, offset, initial_scale=.001):
    target = Vector(target)
    key(obj, 'location', 1, target + Vector(offset))
    key(obj, 'scale', 1, (initial_scale,) * 3)
    key(obj, 'scale', max(2, start - 16), (.4,) * 3)
    key(obj, 'location', start, target + Vector(offset))
    key(obj, 'location', end - 3, target + Vector(offset) * .025)
    key(obj, 'location', end, target)
    key(obj, 'scale', end, (1, 1, 1))


def polish_curves():
    # Blender 4.x legacy actions and Blender 5.x layered actions.
    for action in bpy.data.actions:
        curves = []
        if hasattr(action, 'fcurves'):
            curves.extend(action.fcurves)
        else:
            for layer in action.layers:
                for strip in layer.strips:
                    for slot in action.slots:
                        try: curves.extend(strip.channelbag(slot).fcurves)
                        except (AttributeError, RuntimeError): pass
        for f in curves:
            for p in f.keyframe_points:
                p.interpolation = 'BEZIER'
                p.handle_left_type = p.handle_right_type = 'AUTO_CLAMPED'
