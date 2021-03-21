#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpRigToolkit-libs-controllib function implementations for 3ds Max
"""

from __future__ import print_function, division, absolute_import

from tpDcc.libs.curves.core import curveslib


def create_control_curve(
        control_name='new_ctrl', control_type='circle', controls_path=None, control_size=1.0,
        translate_offset=(0.0, 0.0, 0.0), rotate_offset=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0), axis_order='XYZ',
        mirror=None, color=None, line_width=-1, create_buffers=False, buffers_depth=0,
        match_translate=False, match_rotate=False, match_scale=False, parent=None):
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

    new_curve = curveslib.create_curve(
        control_type, curves_path=controls_path, curve_size=control_size, translate_offset=translate_offset,
        scale=scale, axis_order=axis_order, mirror=mirror, color=color, parent=parent)

    return new_curve
