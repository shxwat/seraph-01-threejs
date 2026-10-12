"""Procedural, asset-free PBR surfaces. Compatible with Blender 4.3+."""
import bpy


def metal(name, color, roughness, bump=0.08):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    bs = n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = 1
    bs.inputs['Roughness'].default_value = roughness
    tex = n.new('ShaderNodeTexNoise'); tex.name = 'Microscopic forging irregularities'
    tex.inputs['Scale'].default_value = 145
    tex.inputs['Detail'].default_value = 2
    coord = n.new('ShaderNodeTexCoord')
    mapping = n.new('ShaderNodeVectorMath'); mapping.operation = 'MULTIPLY'
    mapping.inputs[1].default_value = (1, 1, 18)
    l.new(coord.outputs['Generated'], mapping.inputs[0])
    l.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (roughness * .65,) * 3 + (1,)
    ramp.color_ramp.elements[1].color = (min(.7, roughness * 1.35),) * 3 + (1,)
    l.new(tex.outputs['Fac'], ramp.inputs[0]); l.new(ramp.outputs['Color'], bs.inputs['Roughness'])
    bn = n.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = bump
    bn.inputs['Distance'].default_value = .003
    l.new(tex.outputs['Fac'], bn.inputs['Height']); l.new(bn.outputs['Normal'], bs.inputs['Normal'])
    return m


def emission(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = m.node_tree.nodes; n.clear()
    e = n.new('ShaderNodeEmission'); e.name = 'Animated radiance'
    e.inputs['Color'].default_value = (*color, 1)
    e.inputs['Strength'].default_value = strength
    o = n.new('ShaderNodeOutputMaterial'); m.node_tree.links.new(e.outputs[0], o.inputs['Surface'])
    return m


def create_materials():
    return {
        'gold': metal('01 · Divine gold | brushed electrum', (.69, .43, .15), .26),
        'pale': metal('02 · Pale gold | polished armor edges', (.83, .68, .38), .20, .035),
        'black': metal('03 · Black titanium | ceramic-coated alloy', (.035, .045, .055), .27),
        'silver': metal('04 · Silver machinery | machined platinum', (.58, .66, .72), .23),
        'groove': metal('05 · Recessed inscriptions | oxidized bronze', (.11, .065, .022), .46),
        'pupil': metal('06 · Iris aperture | black optical metal', (.006, .009, .012), .13, .012),
        'energy': emission('07 · Artificial star | amber-white', (1, .68, .28), 12),
        'hot': emission('08 · Containment filaments | white-hot', (1, .88, .60), 8),
        'blue': emission('09 · Cryogenic circuitry | blue-white', (.2, .65, 1), 4),
        'dim': emission('10 · Orbital inscriptions | old gold', (1, .44, .1), 2),
    }
