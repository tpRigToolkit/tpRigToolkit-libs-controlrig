#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains functions related with ControlLib
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from tpDcc import dcc
from tpDcc.core import library, reroute
from tpDcc.libs.curves.core import curveslib

LIB_ID = 'tpRigToolkit-libs-controlrig'
LIB_ENV = LIB_ID.replace('-', '_').upper()
CONTROL_EXT = '.control'

LOGGER = logging.getLogger('tpRigToolkit-libs-controlrig')


class ControLlib(library.DccLibrary, object):
    def __init__(self, *args, **kwargs):
        super(ControLlib, self).__init__(*args, **kwargs)

    @classmethod
    def config_dict(cls, file_name=None):
        base_tool_config = library.DccLibrary.config_dict(file_name=file_name)
        tool_config = {
            'name': 'Control Rig',
            'id': LIB_ID,
            'supported_dccs': {'maya': ['2017', '2018', '2019', '2020']},
            'tooltip': 'Library to manage rig controls',
            'logger_dir': os.path.join(os.path.expanduser('~'), 'tpRigToolkit', 'logs', 'tools'),
            'logger_level': 'INFO',
        }
        base_tool_config.update(tool_config)

        return base_tool_config


# ============================================================================================================
# CREATE
# ============================================================================================================

def control_exists(control_name, controls_path=None):
    """
    Returns whether or not given control rig exists in controls library
    :param control_name: str
    :param controls_path: str
    :return: bool
    """

    curve_found = curveslib.find_curve_path_by_name(control_name, curves_path=controls_path)

    return bool(curve_found)


@reroute.reroute_factory(LIB_ID, 'controllib')
def create_control_curve(control_name='new_ctrl', control_type='circle', controls_path=None, **kwargs):
    """
    Creates a new curve based control
    :param control_name: str
    :param control_type: str
    :param controls_path: str
    :return:
    """

    raise NotImplementedError('Function create_text_control not implemented for current DCC!')


@reroute.reroute_factory(LIB_ID, 'controllib')
def create_text_control(text, font='Times New Roman'):
    """
    Creates a new text based control
    :param text: str, text control will contain
    :param font: str, font name text control will use
    """

    raise NotImplementedError('Function create_text_control not implemented for current DCC!')


# ============================================================================================================
# REPLACE
# ============================================================================================================

@reroute.reroute_factory(LIB_ID, 'controllib')
def replace_control_curves(control_names, control_type='circle', controls_path=None, keep_color=True, **kwargs):
    """

    :param control_names:
    :param control_type:
    :param controls_path:
    :param keep_color:
    :return:
    """

    raise NotImplementedError('Function set_shape not implemented for current DCC!')

# @reroute.reroute_factory(LIB_ID, 'controllib')
# def set_shape(crv, crv_shape_list, size=None, select_new_shape=False, keep_color=False):
#     """
#     Creates a new shape on the given curve
#     :param crv:
#     :param crv_shape_list:
#     :param size:
#     :param select_new_shape: bool
#     :param keep_color: bool
#     """
#
#     raise NotImplementedError('Function set_shape not implemented for current DCC!')
#


# ============================================================================================================
# COLOR
# ============================================================================================================

@reroute.reroute_factory(LIB_ID, 'controllib')
def get_control_color(control_name):
    """
    Returns the control of the control transform node
    :param control_name: str, control transform name
    :return: variant
    """

    raise NotImplementedError('Function get_control_color not implemented for current DCC!')


@reroute.reroute_factory(LIB_ID, 'controllib')
def set_control_color(control_name, new_color, linear=True):
    """
    Sets the control of the given control transform node
    :param control_name: str, control transform name
    :param new_color: list(float, float, float) or int, new color to apply to the control
    :param linear, bool, Whether or not color is set in linear space
    :return: bool, True if the color is applied successfully; False otherwise
    """

    raise NotImplementedError('Function get_control_color not implemented for current DCC!')


def set_controls_color(control_names, new_color, linear=True):
    """
    Sets the control of the given control transform node
    :param control_names: list(str), List of control names to set control of
    :param new_color: list(float, float, float) or int, new color to apply to the control
    :param linear, bool, Whether or not color is set in linear space
    :return: list(str), list of
    """

    colored_controls = list()
    for control_name in control_names:
        colored_control = set_control_color(control_name, new_color, linear=linear)
        if colored_control:
            colored_controls.append(colored_control)

    return colored_controls


# ============================================================================================================
# DUPLICATE
# ============================================================================================================

@reroute.reroute_factory(LIB_ID, 'controllib')
def duplicate_control(control_name, use_selected_name=False, copy_tracker=True, delete_node_shapes=False):
    """
    Duplicates the given control transform node to a new transform parented to the world
    :param control_name: str, name of the control to duplicate
    :param use_selected_name: bool, Whether or not
    :param copy_tracker:
    :param delete_node_shapes:
    :return:
    """

    raise NotImplementedError('Function get_control_color not implemented for current DCC!')


# ============================================================================================================
# MIRROR
# ============================================================================================================

@reroute.reroute_factory(LIB_ID, 'controllib')
def mirror_control(source_control, target_control=None, mirror_axis='X', mirror_mode=0, keep_color=True):
    """
    Find the right side control of a left side control and mirrors the control following next rules:
        - Mirror only will be applied if corresponding right side name exists
        - Replace left prefix and suffixes checking for validity
    :param source_control: str
    :return: str, mirrored control
    """

    raise NotImplementedError('Function select_controls not implemented for current DCC!')


@dcc.undo_decorator()
def mirror_controls(nodes=None, **kwargs):
    """
    Mirrors the CV positions of all controls in the current scene
    """

    mirrored_controls = list()

    all_controls = nodes if nodes else get_controls(**kwargs)
    if not all_controls:
        return mirrored_controls

    for control_to_mirror in all_controls:
        if control_to_mirror in mirrored_controls:
            continue
        mirrored_control = mirror_control(control_to_mirror, **kwargs)
        if not mirrored_control:
            continue
        mirrored_controls.append(mirrored_control)

    if mirrored_controls:
        dcc.select_node(mirrored_controls)

    return mirrored_controls


# ============================================================================================================
# TRACK
# ============================================================================================================

@reroute.reroute_factory(LIB_ID, 'controllib')
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

    raise NotImplementedError('Function add_control_tracker_attributes not implemented for current DCC!')


@reroute.reroute_factory(LIB_ID, 'controllib')
def break_track_control(control_name):

    raise NotImplementedError('Function break_track_control not implemented for current DCC!')


# ============================================================================================================
# TRANSFORM
# ============================================================================================================

@reroute.reroute_factory(LIB_ID, 'controllib')
def get_control_scale(control_name):
    """
    Returns the size of the given control by checking its tracker scale attribute or their shapes bounding box
    :param control_name: str, name of the control to get size of
    :return: float
    """

    raise NotImplementedError('Function get_control_scale not implemented for current DCC!')


# ============================================================================================================
# EXTRAS
# ============================================================================================================

@reroute.reroute_factory(LIB_ID, 'controllib')
def is_control(transform_node, only_tagged=False, **kwargs):
    """
    Returns whether or not given transform is a rig control
    :param transform_node: str
    :param only_tagged: bool
    :return: bool
    """

    raise NotImplementedError('Function is_control not implemented for current DCC!')


@reroute.reroute_factory(LIB_ID, 'controllib')
def get_controls(**kwargs):
    """
    Returns all controls in current scene
    Checks for the following info:
        - Check if the controls start with a control prefx or ends with a control suffix
        - Check if the controls have a specific control attribute
        - Check if a transform has an attribute called tag (with value) and the transform has a nurbsCurve at least
    :return: list(str), list of control names
    """

    raise NotImplementedError('Function get_controls not implemented for current DCC!')


@reroute.reroute_factory(LIB_ID, 'controllib')
def select_controls(**kwargs):
    """
    Select all controls in current scene
    """

    raise NotImplementedError('Function select_controls not implemented for current DCC!')


@reroute.reroute_factory(LIB_ID, 'controllib')
def key_controls(**kwargs):
    """
    Sets a keyframe in all controls in current scene
    :param kwargs:
    """

    raise NotImplementedError('Function select_controls not implemented for current DCC!')


@reroute.reroute_factory(LIB_ID, 'controllib')
def scale_controls(value, controls=None, **kwargs):
    """
    Scale current selected controls by given value
    """

    raise NotImplementedError('Function select_controls not implemented for current DCC!')


@reroute.reroute_factory(LIB_ID, 'controllib')
def add_control_tracker_attributes(control_name, control_type='circle'):
    """
    Adds color tracker attributes to the given node
    :param control_name: str, name of transform node of the control
    :param control_type: str, control library type
    """

    raise NotImplementedError('Function select_controls not implemented for current DCC!')
