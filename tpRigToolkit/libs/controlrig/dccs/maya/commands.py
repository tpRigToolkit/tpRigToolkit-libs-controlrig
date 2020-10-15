#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains commands for controls
"""

from __future__ import print_function, division, absolute_import

from tpDcc.core import command
import tpDcc.dccs.maya as maya


class CreateCurveFromLibrary(command.DccCommand, object):
    """
    Creates a new curve from the library of shapes
    """

    id = 'tpRigToolkit-libs-controlrig-commands-createCurveFromLib'
    is_undoable = True

    _new_parent = False

    def resolve_arguments(self, arguments):
        try:
            parent = arguments.parent
        except AttributeError:
            parent = None

        shape_name = arguments.shape_name or 'circle'

        if parent is not None:
            handle = maya.OpenMaya.MObjectHandle(parent)
            if not handle.isValid() or not handle.isAlive():
                self.cancel('Parent no longer exists in the current scene: {}'.format(parent))
            parent = handle
        else:
            self._new_parent = True
