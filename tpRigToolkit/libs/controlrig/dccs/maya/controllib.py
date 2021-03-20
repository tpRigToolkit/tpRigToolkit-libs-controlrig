#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpRigToolkit-libs-controllib function implementations for Maya
"""

from __future__ import print_function, division, absolute_import

import maya.cmds

from tpDcc import dcc
from tpDcc.core import command
from tpDcc.libs.python import python

from tpDcc.dccs.maya.api import node as api_node
from tpDcc.dccs.maya.core import filtertypes, curve, name as name_utils, shape as shape_utils, node as node_utils
from tpDcc.dccs.maya.core import transform as xform_utils, color as color_utils

from tpRigToolkit.libs.controlrig.core import consts
from tpRigToolkit.libs.controlrig.dccs.maya import controlutils


# ============================================================================================================
# CREATE
# ============================================================================================================

def create_control_curve(
        control_name='new_ctrl', control_type='circle', controls_path=None, control_size=1.0,
        translate_offset=(0.0, 0.0, 0.0), rotate_offset=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0), axis_order='XYZ',
        mirror=None, color=None, line_width=-1,  create_buffers=False, buffers_depth=0,
        match_translate=False, match_rotate=False, match_scale=False, parent=None, **kwargs):
    """
    Creates a new curve based control
    :param control_name: str, name of the new control to create
    :param control_type: str, curve types used by the new control
    :param controls_path: str or None, path were control curve types can be located
    :param control_size: float, global size of the control
    :param translate_offset: tuple(float, float, float), XYZ translation offset to apply to the control curves
    :param rotate_offset: tuple(float, float, float), XYZ rotation offset to apply to the control curves
    :param scale: tuple(float, float, float), scale of the control.
    :param axis_order: str, axis order of the control. Default is XYZ.
    :param mirror: str or None, axis mirror to apply to the control curves (None, 'X', 'Y' or 'Z')
    :param color: list(float, float, float), RGB or index color to apply to the control
    :param line_width: str, If given, the new shapes will be parented to given node
    :param create_buffers: bool, Whether or not control buffer groups should be created.
    :param buffers_depth: int, Number of buffers groups to create.
    :param parent: str, If given, the new shapes will be parented to given node
    :param match_translate: bool, Whether or not new control root node should match the translate with the
        translation of the current DCC selected node
    :param match_translate: bool, Whether or not new control root node should match the rotate with the
        rotation of the current DCC selected node
    :param match_scale: bool, Whether or not new control root node should match the scale with the
        scale of the current DCC selected node
    :return:
    """

    current_selection = dcc.selected_nodes()

    parent_mobj = None
    if parent:
        parent_mobj = api_node.as_mobject(parent)

    runner = command.CommandRunner()

    control_data = kwargs.pop('control_data', None)
    if control_data:
        parent_mobj, shape_mobjs = runner.run(
            'tpDcc-libs-curves-dccs-maya-createCurveFromData', curve_data=control_data, curve_size=control_size,
            translate_offset=translate_offset, scale=scale, axis_order=axis_order, mirror=mirror, parent=parent_mobj)
    else:
        parent_mobj, shape_mobjs = runner.run(
            'tpDcc-libs-curves-dccs-maya-createCurveFromPath', curve_type=control_type, curves_path=controls_path,
            curve_size=control_size, translate_offset=translate_offset, scale=scale, axis_order=axis_order,
            mirror=mirror, parent=parent_mobj)

    if parent_mobj:
        for shape in shape_mobjs:
            api_node.rename_mobject(shape, control_name)
        curve_long_name_list = api_node.names_from_mobject_handles(shape_mobjs)
    else:
        api_node.rename_mobject(shape_mobjs[0], control_name)
        curve_long_name = api_node.names_from_mobject_handles(shape_mobjs)[0]
        curve_long_name_list = [curve_long_name]

    if rotate_offset != (0.0, 0.0, 0.0):
        shape_utils.rotate_node_shape_cvs(curve_long_name_list, rotate_offset)
    if line_width != -1:
        curve.set_curve_line_thickness(curve_long_name_list, line_width=line_width)

    # TODO: Support index based color
    if color is not None:
        if isinstance(color, int):
            node_utils.set_color(curve_long_name_list, color)
        else:
            node_utils.set_rgb_color(curve_long_name_list, color, linear=True, color_shapes=True)

    transforms = list()
    for curve_shape in curve_long_name_list:
        parent = dcc.node_parent(curve_shape)
        if parent:
            if parent not in transforms:
                transforms.append(parent)
        else:
            if curve_shape not in transforms:
                transforms.append(curve_shape)

    if not parent and transforms:
        if create_buffers and buffers_depth > 0:
            transforms = create_buffer_groups(transforms, buffers_depth)
        if current_selection:
            match_transform = current_selection[0]
            if match_transform and dcc.node_exists(match_transform):
                for transform in transforms:
                    if match_translate:
                        dcc.match_translation(match_transform, transform)
                    if match_rotate:
                        dcc.match_rotation(match_transform, transform)
                    if match_scale:
                        dcc.match_scale(match_transform, transform)

    return transforms


@dcc.undo_decorator()
def create_text_control(text, font='Times New Roman'):
    """
    Creates a new text based control
    :param text: str, text control will contain
    :param font: str, font name text control will use
    """

    created_text = maya.cmds.textCurves(f=font, t=text)
    children_list = maya.cmds.listRelatives(created_text[0], ad=True)
    texts_list = []
    for i in children_list:
        if 'curve' in i and 'Shape' not in i:
            texts_list.append(i)
    for i in range(len(texts_list)):
        maya.cmds.parent(texts_list[i], w=True)
        maya.cmds.makeIdentity(texts_list[i], apply=True, t=1, r=1, s=1, n=0)
        if i == 0:
            parent_guide = texts_list[0]
        else:
            shape = maya.cmds.listRelatives(texts_list[i], s=True)
            maya.cmds.move(0, 0, 0, (texts_list[i] + '.scalePivot'), (texts_list[i] + '.rotatePivot'))
            maya.cmds.parent(shape, parent_guide, add=True, s=True)
            maya.cmds.delete(texts_list[i])
    maya.cmds.delete(created_text[0])
    maya.cmds.xform(texts_list[0], cp=True)
    world_position = maya.cmds.xform(texts_list[0], q=True, piv=True, ws=True)
    maya.cmds.xform(texts_list[0], t=(-world_position[0], -world_position[1], -world_position[2]))
    maya.cmds.makeIdentity(texts_list[0], apply=True, t=1, r=1, s=1, n=0)
    maya.cmds.select(texts_list[0])


# ============================================================================================================
# REPLACE
# ============================================================================================================

def replace_control_curves(
        control_name, control_type='circle', controls_path=None, auto_scale=True,
        maintain_line_width=True, keep_color=True, **kwargs):
    """
    Replaces the given control with the given control type deleting the existing control curve shape nodes
    :param control_name:
    :param control_type:
    :param controls_path:
    :param auto_scale: bool
    :param maintain_line_width: bool
    :param keep_color: bool
    :return:
    """

    orig_sel = dcc.selected_nodes()

    line_width = -1
    orig_size = None
    orig_color = kwargs.pop('color', None)
    if auto_scale:
        orig_size = get_control_size(control_name)
    if maintain_line_width:
        line_width = curve.get_curve_line_thickness(control_name)
    if keep_color:
        orig_color = get_control_color(control_name)

    new_control = create_control_curve(
        control_name='new_ctrl', control_type=control_type, controls_path=controls_path, color=orig_color, **kwargs)[0]
    if auto_scale and orig_size is not None:
        new_scale = get_control_size(new_control)
        scale_factor = orig_size / new_scale
        dcc.scale_shapes(new_control, scale_factor, relative=False)

    # We need to make sure that transforms are reset in all scenarios
    # Previous implementation was failing if the target hierarchy had a mirror behaviour (group scaled negative in
    # one of the axises)
    # maya.cmds.matchTransform([new_control, target], pos=True, rot=True, scl=True, piv=True)
    target = dcc.list_nodes(control_name, node_type='transform')[0]
    dcc.delete_node(dcc.create_parent_constraint(new_control, target, maintain_offset=False))
    dcc.delete_node(dcc.create_scale_constraint(new_control, target, maintain_offset=False))
    target_parent = dcc.node_parent(target)
    if target_parent:
        new_control = dcc.set_parent(new_control, target_parent)
        for axis in 'XYZ':
            dcc.set_attribute_value(new_control, 'translate{}'.format(axis), 0.0)
            dcc.set_attribute_value(new_control, 'rotate{}'.format(axis), 0.0)
            dcc.set_attribute_value(new_control, 'scale{}'.format(axis), 1.0)
        new_control = dcc.set_parent_to_world(new_control)

    if target != new_control:
        xform_utils.parent_transforms_shapes(
            target, [new_control], delete_original=True, delete_shape_type='nurbsCurve')

    if maintain_line_width:
        curve.set_curve_line_thickness(target, line_width=line_width)

    dcc.select_node(orig_sel)

    return target


# ============================================================================================================
# COLOR
# ============================================================================================================

def get_control_color(control_name):
    """
    Returns the control of the control transform node
    :param control_name: str, control transform name
    :return: variant
    """

    shapes = dcc.list_shapes_of_type(control_name, shape_type='nurbsCurve')
    if not shapes:
        return (0.0, 0.0, 0.0)

    return dcc.node_rgb_color(shapes[0], linear=True)


def set_control_color(control_name, new_color, linear=True):
    """
    Sets the control of the given control transform node
    :param control_name: str, control transform name
    :param new_color: list(float, float, float) or int, new color to apply to the control
    :param linear, bool, Whether or not color is set in linear space
    :return: bool, True if the color is applied successfully; False otherwise
    """

    shapes = dcc.list_shapes_of_type(control_name, shape_type='nurbsCurve')
    if not shapes:
        return False

    # TODO: Add support for index based colors
    for shape in shapes:
        node_utils.set_rgb_color(shape, new_color, linear=linear)

    return True


# ============================================================================================================
# DUPLICATE
# ============================================================================================================

def duplicate_control(
        control_name, duplicate_name=None, use_selected_name=True, copy_tracker=True, delete_node_shapes=False):
    """
    Duplicates the given control transform node to a new transform parented to the world
    :param control_name: str, name of the control to duplicate
    :param duplicate_name: str, name of the duplicated control
    :param use_selected_name: bool, Whether or not
    :param copy_tracker:
    :param delete_node_shapes:
    :return:
    """

    if not duplicate_name and use_selected_name:
        duplicate_name = control_name
    duplicated_control = xform_utils.duplicate_transform_without_children(
        control_name, node_name=duplicate_name, delete_shapes=delete_node_shapes)

    if dcc.node_parent(duplicated_control):
        duplicated_control = dcc.set_parent_to_world(duplicated_control)

    if dcc.node_type(duplicated_control) == 'joint':
        pass

    return duplicated_control


# ============================================================================================================
# MIRROR
# ============================================================================================================

def mirror_control(
        source_control, target_control=None, mirror_axis='X', mirror_mode=0, mirror_color=None, mirror_replace=False,
        keep_color=True, from_name=None, to_name=None):
    """
    Find the right side control of a left side control and mirrors the control following next rules:
        - Mirror only will be applied if corresponding right side name exists
        - Replace left prefix and suffixes checking for validity
    :param mirror_axis: str
    :param mirror_mode: int or None
    :param mirror_color: int or list(float, float, float)
    :param mirror_replace: bool
    :param keep_color: bool
    :return: str, mirrored control
    """

    if keep_color:
        target_control_color = get_control_color(source_control)
    else:
        target_control_color = get_control_color(source_control) if not mirror_color and keep_color else mirror_color

    source_shapes = dcc.list_shapes_of_type(source_control, 'nurbsCurve')
    if not source_shapes:
        return None

    duplicated_control = duplicate_control(source_control)
    mirror_pivot_grp = dcc.create_empty_group(name='temp_mirrorPivot')
    duplicated_control = dcc.set_parent(duplicated_control, mirror_pivot_grp)

    dcc.set_attribute_value(mirror_pivot_grp, 'scale{}'.format(mirror_axis.upper()), -1)

    target_control = target_control or source_control.replace(from_name, to_name)

    # We force this conversion. This is something that we should remove in the future
    if target_control and not dcc.node_exists(target_control):
        target_control = target_control.replace('Left', 'Right')

    if target_control and not dcc.node_exists(target_control):
        target_control = dcc.node_short_name(target_control)

    if target_control and dcc.node_exists(target_control) and mirror_replace:
        if keep_color:
            target_control_color = get_control_color(target_control)
        mirrored_control = xform_utils.parent_transforms_shapes(
            target_control, duplicated_control, delete_original=True)
    else:
        mirrored_control = dcc.set_parent_to_world(duplicated_control)

    maya.cmds.delete(mirror_pivot_grp)

    if mirror_mode == 0:
        dcc.move_node(mirrored_control, 0, 0, 0, world_space=True)
    elif mirror_mode == 1:
        orig_pos = dcc.node_world_space_pivot(source_control)
        dcc.move_node(mirrored_control, orig_pos[0], orig_pos[1], orig_pos[2], world_space=True)

    if target_control_color:
        target_shapes = dcc.list_shapes_of_type(mirrored_control, shape_type='nurbsCurve')
        for target_shape in target_shapes:
            dcc.set_node_color(target_shape, target_control_color)

    if from_name and to_name and from_name != to_name:
        if from_name in mirrored_control:
            mirrored_control = dcc.rename_node(mirrored_control, source_control.replace(from_name, to_name))

    return mirrored_control


# ============================================================================================================
# TRACK
# ============================================================================================================

def add_control_tracker_attributes(
        control_name, control_type='circle', translate=(0.0, 0.0, 0.0), rotate=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0), color=None,):
    """
    Add control tracker attributes
    :param control_name: str, name of the control lwe want to track
    :param control_type: str, control type of the control
    :param translate: tuple(float, float, float), initial translation value
    :param rotate: tuple(float, float, float), initial rotation value
    :param scale: tuple(float, float, float), initial scale value
    :param color: list(float), initial color as linear color
    """

    xform_utils.add_transform_tracker_attributes(control_name, translate=translate, rotate=rotate, scale=scale)

    if not color:
        shapes = dcc.list_shapes_of_type(control_name, shape_type='nurbsCurve')
        if shapes:
            color = node_utils.get_rgb_color(shapes[0], linear=True)
    if not color:
        color = (0.0, 0.0, 0.0)
    color_utils.add_color_tracker_attributes(control_name, color)

    for i, attr_name in enumerate(consts.ALL_CONTROL_TYPE_TRACKER_ATTRIBUTE_NAMES):
        if not dcc.attribute_exists(control_name, attr_name):
            dcc.add_string_attribute(control_name, attr_name)

    dcc.set_attribute_value(control_name, consts.TRACKER_CONTROL_TYPE_ATTR_NAME, control_type)
    dcc.set_attribute_value(control_name, consts.TRACKER_CONTROL_TYPE_DEFAULT_ATTR_NAME, control_type)


# ============================================================================================================
# TRANSFORM
# ============================================================================================================

def get_control_size(control_name):
    """
    Returns the size of the given control by checking its bounding box size
    :param control_name: str, name of the control to get size of
    :return: float
    """

    return dcc.node_bounding_box_size(control_name)


# ============================================================================================================
# EXTRAS
# ============================================================================================================

def is_control(transform_node, only_tagged=False, **kwargs):
    """
    Returns whether or not given transform is a rig control
    :param transform_node: str
    :param only_tagged: bool
    :return: bool
    """

    maybe_control = False

    names_to_skip = python.force_list(kwargs.get('names_to_skip', list()))
    prefixes_to_check = python.force_list(kwargs.get('prefixes_to_check', list()))
    prefixes_to_skip = python.force_list(kwargs.get('prefixes_to_skip', list()))
    suffixes_to_check = python.force_list(kwargs.get('suffixes_to_check', list()))
    suffixes_to_skip = python.force_list(kwargs.get('suffixes_to_skip', list()))
    attributes_to_check = python.force_list(kwargs.get('attributes_to_check', list()))
    attributes_to_skip = python.force_list(kwargs.get('attributes_to_skip', list()))
    names_to_skip.extend(consts.CONTROLS_NAMES_TO_SKIP)
    prefixes_to_check.extend(consts.CONTROLS_PREFIXES)
    prefixes_to_skip.extend(consts.CONTROLS_PREFIXES_TO_SKIP)
    suffixes_to_check.extend(consts.CONTROLS_SUFFIXES)
    suffixes_to_skip.extend(consts.CONTROLS_SUFFIXES_TO_SKIP)
    attributes_to_check.extend(consts.CONTROLS_ATTRIBUTES)
    attributes_to_skip.extend(consts.CONTROLS_ATTRIBUTES_TO_SKIP)
    names_to_skip = tuple(set(names_to_skip))
    prefixes_to_check = tuple(set(prefixes_to_check))
    prefixes_to_skip = tuple(set(prefixes_to_skip))
    suffixes_to_check = tuple(set(suffixes_to_check))
    suffixes_to_skip = tuple(set(suffixes_to_skip))
    attributes_to_check = tuple(set(attributes_to_check))
    attributes_to_skip = tuple(set(attributes_to_skip))

    # TODO: We could use nomenclature to check control validity

    transform = name_utils.remove_namespace_from_string(transform_node)

    if only_tagged:
        if dcc.attribute_exists(transform, 'tag'):
            value = dcc.get_attribute_value(transform, 'tag')
            if value:
                return True
        return False
    else:
        # Check names
        if transform in names_to_skip:
            return False

        # Check prefix and suffix
        if transform.startswith(prefixes_to_skip) or transform.endswith(suffixes_to_skip):
            return False
        if transform.startswith(prefixes_to_check) or transform.endswith(suffixes_to_check):
            maybe_control = True

        # Check attributes
        for attr_to_skip in attributes_to_skip:
            if dcc.attribute_exists(transform, attr_to_skip):
                return False
        for attr_to_check in attributes_to_check:
            if dcc.attribute_exists(transform, attr_to_check):
                return True
        if dcc.attribute_exists(transform, 'tag'):
            value = dcc.get_attribute_value(transform, 'tag')
            if value:
                maybe_control = True
        if dcc.attribute_exists(transform, 'curveType') or dcc.attribute_exists(transform, 'type'):
            value = dcc.get_attribute_value(transform, 'curveType')
            if value:
                maybe_control = True
        if dcc.attribute_exists(transform, 'type'):
            value = dcc.get_attribute_value(transform, 'type')
            if value:
                maybe_control = True

        if maybe_control:
            if dcc.node_has_shape_of_type(
                    transform, 'nurbsCurve') or dcc.node_has_shape_of_type(transform, 'nurbsSurface'):
                return True

    return False


def get_controls(**kwargs):
    """
    Returns all controls in current scene
    Checks for the following info:
        - Check if the controls start with a control prefx or ends with a control suffix
        - Check if the controls have a specific control attribute
        - Check if a transform has an attribute called tag (with value) and the transform has a nurbsCurve at least
    :param namespace: str, only controls with the given namespace will be search.
    :return: list(str), list of control names
    """

    namespace = kwargs.get('namespace', '')
    name = '{}:*'.format(namespace) if namespace else '*'

    transforms = dcc.list_nodes(name, node_type='transform', full_path=False)
    joints = dcc.list_nodes(name, node_type='joint', full_path=False)
    if joints:
        transforms += joints

    found = list()
    found_with_value = list()

    for transform_node in transforms:
        if is_control(transform_node, only_tagged=True, **kwargs):
            found_with_value.append(transform_node)
        elif is_control(transform_node, only_tagged=False, **kwargs):
            found.append(transform_node)

    return found_with_value if found_with_value else found


@dcc.undo_decorator()
def select_controls(**kwargs):
    """
    Select all controls in current scene
    """

    namespace = kwargs.get('namespace', '')
    all_controls = get_controls(namespace=namespace, **kwargs)
    if not all_controls:
        return

    dcc.select_node(all_controls)


@dcc.undo_decorator()
def key_controls(**kwargs):
    """
    Sets a keyframe in all controls in current scene
    :param kwargs:
    """

    namespace = kwargs.get('namespace', '')
    all_controls = get_controls(namespace=namespace, **kwargs)
    if not all_controls:
        return

    dcc.set_keyframe(all_controls, shape=0, controlPoints=0, hierarchy='none', breakdown=0)


@dcc.undo_decorator()
def scale_controls(value, controls=None, **kwargs):
    """
    Scale current selected controls by given value
    """

    namespace = kwargs.get('namespace', '')
    all_controls = controls or get_controls(namespace=namespace, **kwargs) or list()
    for control in all_controls:
        dcc.scale_transform_shapes(control, value)


def get_control_transform_rgb_color(control_transform, linear=True):
    """
    Returns the RGB color of the given control, looking in the first shape node
    :param control_transform: str, name of the control transforms we want to retrieve color of
    :param linear: bool, Whether or not the RGB should be in linear space (matches viewport color)
    :return: tuple(float, float, float), new control color in float linear values (between 0.0 and 1.0)
    """

    control_shapes = filtertypes.filter_nodes_with_shapes(control_transform, shape_type='nurbsCurve')
    if not control_shapes:
        return 0.0, 0.0, 0.0

    return node_utils.get_rgb_color(control_shapes[0], linear=linear)


def set_shape(crv, crv_shape_list, size=None, select_new_shape=False, keep_color=False):
    """
    Creates a new shape on the given curve
    :param crv:
    :param crv_shape_list:
    :param size:
    :param select_new_shape: bool
    :param keep_color: bool
    """

    crv_shapes = controlutils.validate_curve(crv)

    orig_size = None
    orig_color = None
    if crv_shapes:
        orig_size = dcc.node_bounding_box_size(crv)

        # If there are multiple shapes, we only take into account the color of the first shape
        orig_color = dcc.node_color(crv_shapes[0])

    if crv_shapes:
        dcc.delete_node(crv_shapes)

    for i, c in enumerate(crv_shape_list):
        new_shape = dcc.list_shapes(c)[0]
        new_shape = dcc.rename_node(new_shape, dcc.node_short_name(crv) + 'Shape' + str(i + 1).zfill(2))
        dcc.enable_overrides(new_shape)
        if orig_color is not None and keep_color:
            dcc.set_node_color(new_shape, orig_color)
        dcc.combine_shapes(crv, new_shape, delete_after_combine=True)

    new_size = dcc.node_bounding_box_size(crv)

    if orig_size and new_size:
        scale_size = orig_size / new_size
        dcc.scale_shapes(crv, scale_size, relative=False)

    if size:
        dcc.scale_shapes(crv, size, relative=True)

    if select_new_shape:
        dcc.select_node(crv)

    return crv


def create_buffer_groups(target=None, depth=1):
    """
    Creates buffer groups for the given target
    :param target: str
    :param depth: int
    :return: list(str)
    """

    result = list()

    target = python.force_list(target)
    for tgt in target:
        rotate_order = dcc.get_attribute_value(tgt, 'rotateOrder')
        for i in range(depth):
            obj_parent = maya.cmds.listRelatives(tgt, parent=True, fullPath=True)
            empty_group_name = 'buffer' if i == 0 else 'buffer{}'.format(i)
            empty_group = maya.cmds.group(empty=True, n=empty_group_name, world=True)
            dcc.set_attribute_value(empty_group, 'rotateOrder', rotate_order)
            if obj_parent:
                maya.cmds.parent(empty_group, obj_parent)
            obj_transform = [dcc.get_attribute_value(tgt, xform) for xform in 'tsr']
            tgt = maya.cmds.parent(tgt, empty_group)[0]
            for j, xform in enumerate('tsr'):
                maya.cmds.setAttr('{}.{}'.format(empty_group, xform), *obj_transform[j], type='double3')
                reset_xform = (0, 0, 0) if j != 1 else (1, 1, 1)
                maya.cmds.setAttr('{}.{}'.format(tgt, xform), *reset_xform, type='double3')
            result.append(empty_group)

    return result
