#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains constants definitions used by tpRigToolkit-libs-controlrig
"""

from __future__ import print_function, division, absolute_import


CONTROLS_NAMES_TO_SKIP = ['front', 'persp', 'side', 'top']
CONTROLS_PREFIXES = ['ctrl_', 'CON_', 'Ctrl_', 'control_']
CONTROLS_PREFIXES_TO_SKIP = ['xform_', 'driver_', 'root_', 'auto_', 'follow_', 'offset_']
CONTROLS_SUFFIXES = ['_ctrl', '_CON', '_Ctrl', '_control']
CONTROLS_SUFFIXES_TO_SKIP = ['_xform', '_driver', '_root', '_auto', '_follow', '_offset']
CONTROLS_ATTRIBUTES = ['control']
CONTROLS_ATTRIBUTES_TO_SKIP = ['POSE']

TEMP_BREAK_CONTROL_ATTR = 'tempBreakTrack'
TRACKER_CONTROL_TYPE_ATTR_NAME = 'controlTypeTrack'
TRACKER_CONTROL_TYPE_DEFAULT_ATTR_NAME = 'controlTypeTrackDefault'
ALL_CONTROL_TYPE_TRACKER_ATTRIBUTE_NAMES = [TRACKER_CONTROL_TYPE_ATTR_NAME, TRACKER_CONTROL_TYPE_DEFAULT_ATTR_NAME]
