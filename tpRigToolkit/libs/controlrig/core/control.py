#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig control abstract implementation
"""


class AbstractRigControl(object):
    def __init__(self, name, *args, **kwargs):
        super(AbstractRigControl, self).__init__()

        self._control = name

    def get(self):
        """
        Returns the name of the control
        :return: str
        """

        return self._control
