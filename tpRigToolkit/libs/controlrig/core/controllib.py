#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains functions related with ControlLib
"""

from __future__ import print_function, division, absolute_import

import os
from copy import copy

from Qt.QtGui import *

import tpDcc as tp
from tpDcc.libs.python import jsonio, yamlio, python

import tpRigToolkit
from tpRigToolkit.libs.controlrig.core import controldata, controlutils

# TODO: When storing controls that are a hierarchy of shapes, we MUST respect that hierarchy

if tp.is_maya():
    import tpDcc.dccs.maya as maya
    from tpDcc.dccs.maya.core import transform as xform_utils, shape as shape_utils, name as name_utils

CONTROLS_NAMES_TO_SKIP = ['front', 'persp', 'side', 'top']
CONTROLS_PREFIXES = ['ctrl_', 'CON_', 'Ctrl_', 'control_']
CONTROLS_PREFIXES_TO_SKIP = ['xform_', 'driver_', 'root_', 'auto_', 'follow_', 'offset_']
CONTROLS_SUFFIXES = ['_ctrl', '_CON', '_Ctrl', '_control']
CONTROLS_SUFFIXES_TO_SKIP = ['_xform', '_driver', '_root', '_auto', '_follow', '_offset']
CONTROLS_ATTRIBUTES = ['control']
CONTROLS_ATTRIBUTES_TO_SKIP = ['POSE']


class ControlLib(object):

    DEFAULT_DATA = {
        'controls': {
            'circle': [{"cvs": [(0.0, 0.7, -0.7), (0.0, 0.0, -1.0), (0.0, -0.7, -0.7), (0.0, -1.0, 0.0),
                                (0.0, -0.7, 0.7), (0.0, 0.0, 1.0), (0.0, 0.7, 0.7), (0.0, 1.0, 0.0)],
                        "degree": 3,
                        "periodic": 1}],
            'cross': [{"cvs": [(0.0, 0.5, -0.5), (0.0, 1.0, -0.5), (0.0, 1.0, 0.5), (0.0, 0.5, 0.5),
                               (0.0, 0.5, 1.0), (0.0, -0.5, 1.0), (0.0, -0.5, 0.5), (0.0, -1.0, 0.5),
                               (0.0, -1.0, -0.5), (0.0, -0.5, -0.5), (0.0, -0.5, -1.0), (0.0, 0.5, -1.0),
                               (0.0, 0.5, -0.5)],
                       "degree": 1,
                       "periodic": 1}],
            'cube': [{"cvs": [(-1.0, -1.0, 1.0), (-1.0, 1.0, 1.0), (-1.0, 1.0, -1.0), (-1.0, -1.0, -1.0),
                              (-1.0, -1.0, 1.0), (1.0, -1.0, 1.0), (1.0, -1.0, -1.0), (1.0, 1.0, -1.0),
                              (1.0, 1.0, 1.0), (1.0, -1.0, 1.0), (1.0, 1.0, 1.0), (-1.0, 1.0, 1.0),
                              (-1.0, 1.0, -1.0), (1.0, 1.0, -1.0), (1.0, -1.0, -1.0), (-1.0, -1.0, -1.0)],
                      "degree": 1,
                      "periodic": 1}]
        },
        'categories': []
    }

    def __init__(self):
        self._controls_file = None
        self._parser_format = 'json'

    @property
    def controls_file(self):
        return self._controls_file

    @controls_file.setter
    def controls_file(self, controls_file_path):
        self._controls_file = controls_file_path
        self.load_control_data()

    def has_valid_controls_file(self):
        """
        Returns whether controls file is valid or not
        :return: bool
        """

        return self._controls_file and os.path.isfile(self._controls_file)

    def load_control_data(self):
        """
        Function that initializes controls data file
        """

        controls = controldata.ControlPool()

        new_controls_file = False
        if not self._controls_file:
            controls_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            self._controls_file = '{}.yml'.format(
                controls_file) if self._parser_format == 'yaml' else '{}.json'.format(controls_file)
        if not self.has_valid_controls_file():
            try:
                f = open(self._controls_file, 'w')
                f.close()
            except Exception:
                pass

        if not self.has_valid_controls_file():
            tpRigToolkit.logger.warning(
                'Impossible to initialize controls data because controls file "{}" does not exists!'.format(
                    self._controls_file))
            return None

        if self._parser_format == 'yaml':
            data = yamlio.read_file(self._controls_file)
        else:
            data = jsonio.read_file(self._controls_file)
        if not data:
            data = self.DEFAULT_DATA
            if self._parser_format == 'yaml':
                yamlio.write_to_file(data, self._controls_file)
            else:
                jsonio.write_to_file(data, self._controls_file)
            new_controls_file = True

        data_controls = data.get('controls')
        if not data_controls:
            tpRigToolkit.logger.warning('No controsl found in current controls data!')
            return None

        for ctrl in data_controls:
            new_ctrl = controldata.ControlData(name=ctrl, ctrl_data=data_controls[ctrl])
            controls.add(new_ctrl)

        if new_controls_file:
            self.save_control_data(control_pool=controls)

        return controls

    def save_control_data(self, control_pool):
        """
        Stores the controls data to the controls data file (overwriting existing data)
        """

        control_data_dict = dict()

        if self._parser_format == 'yaml':
            current_data = yamlio.read_file(self._controls_file)
        else:
            current_data = jsonio.read_file(self._controls_file)

        control_data_dict['controls'] = control_pool()
        control_data_dict['categories'] = current_data['categories'] if current_data is not None else list()
        if self._parser_format == 'yaml':
            yamlio.write_to_file(control_data_dict, self._controls_file)
        else:
            jsonio.write_to_file(control_data_dict, self._controls_file)

    def get_controls(self):
        """
        Returns all available controls
        :return: list
        """

        return self.load_control_data()

    def add_control(self, control_name, curve_info):
        """
        Adds a new control to the list of controls
        :param control_name: str, name of the control we want to add
        :param curve_info: dict, dictionary with proper data curve
        :return:
        """

        control_pool = self.load_control_data()
        if control_name in control_pool:
            tpRigToolkit.logger.warning(
                'Control "{}" already exists in Control File. Aborting adding control operation ...')
            return

        new_ctrl = controldata.ControlData(
            name=control_name,
            ctrl_data=curve_info
        )
        if not new_ctrl:
            tpRigToolkit.logger.error(
                'Control Data for "{}" curve was not created properly! Aborting control add operation ...'.format(
                    control_name))
            return

        control_pool.add(new_ctrl)
        self.save_control_data(control_pool)

        return new_ctrl

    def rename_control(self, old_name, new_name):
        """
        Renames control with given new wame
        :param old_name: str, name of the control we want to rename
        :param new_name: str, new name of the control
        """

        control_pool = self.load_control_data()
        if old_name not in control_pool:
            tpRigToolkit.logger.warning(
                'Control "{}" is not stored in Control File. Aborting renaming control operation ...'.format(old_name))
            return False

        if new_name in control_pool:
            tpRigToolkit.logger.warning(
                'New Control name "{}" is already stored in Control File. '
                'Aborting renaming control operation ...'.format(new_name))
            return False

        control_pool[old_name].name = new_name
        self.save_control_data(control_pool)

        return True

    def delete_control(self, control_name):
        """
        Removes control with given control_name from the controls data file
        :param control_name:
        :return:
        """

        control_pool = self.load_control_data()
        if control_name not in control_pool:
            tpRigToolkit.logger.warning(
                'Control "{}" is not stored in Control File. Aborting deleting control operation ...')
            return

        control_pool.remove(control_name)
        self.save_control_data(control_pool)

    @staticmethod
    def create_control(shape_data, target_object=None, name='new_ctrl', size=1.0, offset=(0, 0, 0), ori=(1, 1, 1),
                       axis_order='XYZ', mirror=None, shape_parent=False, parent=None, color=None, buffer_groups=0):
        """
        Creates a new control
        :param shape_data: str, shape name from the dictionary
        :param target_object: str, object(s) on which we will create the control
        :param name: str, name of the curve
        :param size: float, global size of the control
        :param offset: tuple<float>, X, Y or Z offset around the object
        :param ori: tuple<float>, X, Y or Z multiply of the shape
        :param axis_order: str, 'XYZ' will take X as main axis, etc
        :param axis mirror: str, axis of mirror or None if no wanted mirror
        :param shape_parent, bool, True will parent the shape to the target object
        :param parent
        :param color
        :param buffer_groups
        :return: parent: str, parent of the curve
        """

        target_object = [target_object] if not isinstance(target_object, list) else target_object
        controls = list()
        orient = controldata.ControlV(ori)

        def create(name, offset=(0, 0, 0), shape_data=None):
            """
            Creates a curve an apply the appropiate transform to the shape
            :param shape_data: ControlShape, shape object of the curve
            :param name: str, name of the curve
            :param offset: tuple<float>, X, Y or Z offset around the object
            :return:
            """

            cvs = [controldata.ControlV(pt) for pt in copy(shape_data['cvs'])]
            points, degree, periodic = copy(cvs), shape_data['degree'], shape_data['periodic']
            order = [controldata.axis_eq[x] for x in axis_order]

            for i, point in enumerate(points):
                point *= size * orient.reorder(order)
                point += offset.reorder(order)
                point *= controldata.ControlV.mirror_vector()[mirror]
                points[i] = point.reorder(order)

            # Create a unique name for the controller
            i, n = 2, name
            try:
                while tp.Dcc.get_attribute_value(n, 't'):
                    n = '%s_%02d' % (name, i)
                    i += 1
            except ValueError:
                name = n

            # Make curve periodic if necessary
            if periodic and points[0] != points[-degree]:
                points.extend(points[0:degree])

            # Create the curve
            knots = [i for i in range(-degree + 1, len(points))]

            return tp.Dcc.create_curve(name=name, degree=degree, points=points, knots=knots, periodic=periodic)

        def create_name(obj_name):
            compo_name = [name if len(name) else obj_name]
            return '_'.join(compo_name)

        if len(target_object) != 0 and target_object[0]:
            for obj in target_object:
                ctrls = list()
                ro = tp.Dcc.get_attribute_value(obj, 'ro')
                ctrl_name = create_name(obj)
                for shp in shape_data:
                    try:
                        children_joint = None
                        children_joints = tp.Dcc.list_children(obj, children_type='joint')
                        if children_joints:
                            children_joint = children_joints[0]
                        if children_joint:
                            offset_perc = [tp.Dcc.get_attribute_value(obj, x) * offset[i] for i, x in enumerate('xyz')]
                        else:
                            offset_perc = offset
                    except (ValueError, TypeError):
                        offset_perc = offset
                    finally:
                        ctrl = create(shape_data=shp, name=ctrl_name, offset=controldata.ControlV(offset_perc))

                    # Realign controller and set rotation order
                    tp.Dcc.set_attribute_value(ctrl, 't', controlutils.getpos(obj))
                    controlutils.snap(obj, ctrl, t=False)
                    tp.Dcc.set_attribute_value(ctrl, 'ro', ro)

                    ctrls.append(ctrl)
                controls.append(ctrls)
        else:
            controls.append(
                [create(shape_data=shp, name=create_name(name), offset=controldata.ControlV(offset)) for shp in
                 shape_data])

        # The apply last transforms
        replace_controls = list()
        for i, ctrls in enumerate(controls):
            ctrl = ctrls[0]
            controls_to_color = ctrls

            for obj in controls_to_color:

                # Update shape color
                shapes = maya.cmds.listRelatives(obj, s=True, ni=True, f=True)
                for shp in shapes:
                    if maya.cmds.attributeQuery('overrideEnabled', node=shp, exists=True):
                        maya.cmds.setAttr(shp + '.overrideEnabled', True)
                    if color is not None:
                        if maya.cmds.attributeQuery('overrideRGBColors', node=shp, exists=True) and type(color) != int:
                            maya.cmds.setAttr(shp + '.overrideRGBColors', True)
                            if type(color) in [list, tuple]:
                                maya.cmds.setAttr(shp + '.overrideColorRGB', color[0], color[1], color[2])
                            elif isinstance(color, QColor):
                                maya.cmds.setAttr(shp + '.overrideColorRGB', *color.toTuple())
                        elif maya.cmds.attributeQuery('overrideColor', node=shp, exists=True):
                            if type(color) == int and -1 < color < 32:
                                maya.cmds.setAttr(shp + '.overrideColor', color)
                    else:
                        if name.startswith('l_') or name.endswith('_l') or '_l_' in name:
                            maya.cmds.setAttr(shp + '.overrideColor', 6)
                        elif name.startswith('r_') or name.endswith('_r') or '_r_' in name:
                            maya.cmds.setAttr(shp + '.overrideColor', 13)
                        else:
                            maya.cmds.setAttr(shp + '.overrideColor', 22)

            # Combine shapes
            if len(ctrls) > 1:
                for obj in ctrls[1:]:
                    shapes = maya.cmds.listRelatives(obj, s=True, ni=True, f=True)
                    maya.cmds.parent(shapes, ctrl, s=True, add=True)
                    # maya.cmds.delete(obj)
                maya.cmds.delete(ctrls[1:])

            if parent:
                tp.Dcc.set_parent(ctrl, parent)
            elif shape_parent and len(target_object) != 0:
                replaced_shapes = ControlLib.shape_to_transforms(ctrl, target_object[i])
                ctrls[0] = replaced_shapes[0]
            elif buffer_groups:
                ControlLib.create_buffer_groups(ctrl, buffer_groups)

            if len(ctrls) > 1:
                if replace_controls:
                    return [replace_controls[0][1]]
                else:
                    return [ctrl]

        return controls

    def create_control_by_name(
            self, ctrl_name, name='new_ctrl', size=1, offset=(0, 0, 0), ori=(1, 1, 1), axis_order='XYZ',
            mirror=None, shape_parent=False, target_object=None, parent=None, color=None):
        """
        Creates a new control given its name in the library
        :param ctrl_name: str, name of the control we want to create from the library
        :return: list<str>
        """

        controls = self.get_controls() or list()
        if not controls:
            tpRigToolkit.logger.warning('No controls found!')
            return

        for control in controls:
            if control.name == ctrl_name:
                return self.create_control(
                    control.shapes, name=name, size=size, offset=offset, ori=ori, axis_order=axis_order,
                    mirror=mirror, shape_parent=shape_parent, parent=parent, color=color, target_object=target_object)

        tpRigToolkit.logger.warning(
            'No control found with name: {}. Returning first control in library: {}'.format(
                ctrl_name, controls[0].name))

        # If the given control is not valid we create the first one of the list of controls
        return self.create_control(controls[0].shapes)

    def control_exists(self, ctrl_name):
        """
        Returns whether or not given control exists
        :param ctrl_name: str
        :return: bool
        """

        controls = list(self.get_controls()) or list()
        if not controls:
            tpRigToolkit.logger.warning('No controls found!')
            return

        for control in controls:
            if control.name == ctrl_name:
                return True

        return False

    def get_control_data_by_name(self, ctrl_name):
        """
        Returns data of the given control
        :param ctrl_name: str
        :return:
        """

        controls = list(self.get_controls()) or list()
        if not controls:
            tpRigToolkit.logger.warning('No controls found!')
            return

        for control in controls:
            if control.name == ctrl_name:
                return control

        tpRigToolkit.logger.warning(
            'No control found with name: {}. Returning first control in library: {}'.format(
                ctrl_name, controls[0].name))

        # If the given control is not valid we create the first one of the list of controls
        return controls[0]

    @staticmethod
    def validate_curve(crv):
        """
        Returns whether the given name corresponds to a valid NURBS curve
        :param crv: str, name of the curve we want to check
        :return: bool
        """

        if not tp.is_maya():
            return False

        if crv is None or not tp.Dcc.object_exists(crv):
            return False

        crv_shapes = list()
        if tp.Dcc.node_type(crv) == 'transform':
            curve_shapes = maya.cmds.listRelatives(crv, c=True, s=True)
            if curve_shapes:
                if maya.cmds.nodeType(curve_shapes[0]) == 'nurbsCurve':
                    crv_shapes = maya.cmds.listRelatives(crv, c=True, s=True)
            crv_shapes = maya.cmds.listRelatives(crv, c=True, s=True)
        elif maya.cmds.nodeType(crv) == 'nurbsCurve':
            crv_shapes = maya.cmds.listRelatives(maya.cmds.listRelatives(crv, p=True)[0], c=True, s=True)
        else:
            tpRigToolkit.logger.error('The object "{}" being validated is not a curve!'.format(crv))

        return crv_shapes

    @classmethod
    def get_curve_info(cls, crv, absolute_position=True, absolute_rotation=True, degree=None, periodic=False):
        """
        Returns dictionary that contains all information for rebuilding given NURBS curve
        :param crv: str, name of the curve to get info from
        :return: list<dict>
        """

        if not tp.is_maya():
            return False

        new_crv = maya.cmds.duplicate(crv, n='duplicates', renameChildren=True)

        shapes = list()
        mx = -1

        # In the first loop we get the global bounds of the selection so we can
        # normalize the CV coordinates later
        for obj in new_crv:
            if maya.cmds.listRelatives(obj, p=True, fullPath=True):
                maya.cmds.parent(obj, w=True)
            if absolute_position or absolute_rotation:
                maya.cmds.makeIdentity(
                    obj, apply=True, t=absolute_position, r=absolute_rotation, s=True, n=False, pn=True)

            curve_shapes = cls.validate_curve(obj)
            for crv in curve_shapes:
                for i in range(maya.cmds.getAttr('{}.degree'.format(crv)) + maya.cmds.getAttr('{}.spans'.format(crv))):
                    for p in maya.cmds.xform('{}.cv[{}]'.format(crv, i), query=True, t=True, os=True):
                        if mx < abs(p):
                            mx = abs(p)

        # In this second loop, we store the normalized data of the shapes
        for obj in new_crv:
            curve_shapes = cls.validate_curve(obj)
            for crv_shape in curve_shapes:

                cvs = list()
                degs = maya.cmds.getAttr('{}.degree'.format(crv_shape))
                spans = maya.cmds.getAttr('{}.spans'.format(crv_shape))
                c = maya.cmds.getAttr('{}.f'.format(crv_shape))
                for i in range(spans + (0 if periodic else degs)):
                    cvs.append(maya.cmds.xform('{}.cv[{}]'.format(crv_shape, i), query=True, t=True, os=True))
                cvs = [[p / mx for p in pt] for pt in cvs]

                crv_shape_dict = {
                    'cvs': cvs,
                    'form': maya.cmds.getAttr('{}.form'.format(crv_shape)),
                    'degree': degree or degs,
                    'periodic': c or periodic,
                    'color': maya.cmds.getAttr('{}.overrideColor'.format(crv_shape))
                }
                shapes.append(crv_shape_dict)

        maya.cmds.delete(new_crv)

        return shapes

    @classmethod
    def set_shape(cls, crv, crv_shape_list, size=None, select_new_shape=False, keep_color=False):
        """
        Creates a new shape on the given curve
        :param crv:
        :param crv_shape_list:
        :param size:
        :param select_new_shape: bool
        :param keep_color: bool
        """

        if not tp.is_maya():
            return False

        crv_shapes = cls.validate_curve(crv)

        orig_size = None
        orig_color = None
        if crv_shapes:
            bbox = xform_utils.BoundingBox(crv).get_shapes_bounding_box()
            orig_size = bbox.get_size()

            # If there are multiple shapes, we only take into account the color of the first shape
            orig_color = tp.Dcc.node_color(crv_shapes[0])

        if crv_shapes:
            maya.cmds.delete(crv_shapes)

        for i, c in enumerate(crv_shape_list):
            new_shape = maya.cmds.listRelatives(c, s=True, f=True)[0]
            new_shape = maya.cmds.rename(new_shape, tp.Dcc.node_short_name(crv) + 'Shape' + str(i + 1).zfill(2))
            maya.cmds.setAttr(new_shape + '.overrideEnabled', True)
            if orig_color is not None and keep_color:
                tp.Dcc.set_node_color(new_shape, orig_color)
            maya.cmds.parent(new_shape, crv, r=True, s=True)
            maya.cmds.delete(c)

        bbox = xform_utils.BoundingBox(crv).get_shapes_bounding_box()
        new_size = bbox.get_size()

        if orig_size and new_size:
            scale_size = orig_size / new_size
            shape_utils.scale_shapes(crv, scale_size, relative=False)

        if size:
            shape_utils.scale_shapes(crv, size, relative=True)

        if select_new_shape:
            maya.cmds.select(crv)

        return crv

    @staticmethod
    def shape_to_transforms(shapes=None, transforms=None):
        """
        Parent given shapes directly intro the given transforms
        :param shapes: list(str)
        :param transforms: list(str)
        """

        replaced_shapes = list()

        shapes = python.force_list(shapes)
        transforms = python.force_list(transforms)
        if len(shapes) != len(transforms):
            return False

        for shape, transform in zip(shapes, transforms):
            shapes = maya.cmds.listRelatives(shape, children=True, shapes=True, ni=True, fullPath=True)
            combined_shape = maya.cmds.parent(shapes, transform, shape=True, add=True)[0]
            combined_transform = maya.cmds.listRelatives(combined_shape, parent=True)[0]
            if len(shapes) == 1:
                maya.cmds.rename(shapes, '{}Shape'.format(shape))
            else:
                for i, shp in enumerate(shapes):
                    maya.cmds.rename(shp, '%sShape%02d' % (transform, i))
            # delete old transform
            maya.cmds.delete(shape)
            replaced_shapes.append(combined_transform)

        return replaced_shapes

    @staticmethod
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
            rotate_order = tp.Dcc.get_attribute_value(tgt, 'rotateOrder')
            for i in range(depth):
                obj_parent = maya.cmds.listRelatives(tgt, parent=True, fullPath=True)
                empty_group_name = 'buffer' if i == 0 else 'buffer{}'.format(i)
                empty_group = maya.cmds.group(empty=True, n=empty_group_name, world=True)
                tp.Dcc.set_attribute_value(empty_group, 'rotateOrder', rotate_order)
                if obj_parent:
                    maya.cmds.parent(empty_group, obj_parent)
                obj_transform = [tp.Dcc.get_attribute_value(tgt, xform) for xform in 'trs']
                maya.cmds.parent(tgt, empty_group)
                for j, xform in enumerate('tsr'):
                    maya.cmds.setAttr('{}.{}'.format(empty_group, xform), *obj_transform[j], type='double3')
                    reset_xform = (0, 0, 0) if i != 1 else (1, 1, 1)
                    maya.cmds.setAttr('{}.{}'.format(tgt, xform), *reset_xform, type='double3')
                result.append(empty_group)

        return result


@tp.Dcc.undo_decorator()
def create_text_control(text, font='Times New Roman'):
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


def is_control(transform_node, only_tagged=False, **kwargs):
    """
    Returns whether or not given transform is a rig control
    :param transform: str
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
    names_to_skip.extend(CONTROLS_NAMES_TO_SKIP)
    prefixes_to_check.extend(CONTROLS_PREFIXES)
    prefixes_to_skip.extend(CONTROLS_PREFIXES_TO_SKIP)
    suffixes_to_check.extend(CONTROLS_SUFFIXES)
    suffixes_to_skip.extend(CONTROLS_SUFFIXES_TO_SKIP)
    attributes_to_check.extend(CONTROLS_ATTRIBUTES)
    attributes_to_skip.extend(CONTROLS_ATTRIBUTES_TO_SKIP)
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
        if tp.Dcc.attribute_exists(transform, 'tag'):
            value = tp.Dcc.get_attribute_value(transform, 'tag')
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
            if tp.Dcc.attribute_exists(transform, attr_to_skip):
                return False
        for attr_to_check in attributes_to_check:
            if tp.Dcc.attribute_exists(transform, attr_to_check):
                return True
        if tp.Dcc.attribute_exists(transform, 'tag'):
            value = tp.Dcc.get_attribute_value(transform, 'tag')
            if value:
                maybe_control = True
        if tp.Dcc.attribute_exists(transform, 'curveType'):
            if maybe_control:
                if not shape_utils.has_shape_of_type(transform, 'nurbsCurve'):
                    return False
                return True

        if maybe_control:
            if shape_utils.has_shape_of_type(
                    transform, 'nurbsCurve') or shape_utils.has_shape_of_type(transform, 'nurbsSurface'):
                return True

    return False


def get_controls(namespace='', **kwargs):
    """
    Returns all controls in current scene
    Checks for the following info:
        - Check if the controls start with a control prefx or ends with a control suffix
        - Check if the controls have a specific control attribute
        - Check if a transform has an attribute called tag (with value) and the transform has a nurbsCurve at least
    :param namespace: str, only controls with the given namespace will be search.
    :return: list(str), list of control names
    """

    name = '{}:*'.format(namespace) if namespace else '*'

    transforms = tp.Dcc.list_nodes(name, node_type='transform', full_path=False)
    joints = tp.Dcc.list_nodes(name, node_type='joint', full_path=False)
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


@tp.Dcc.undo_decorator()
def select_controls(namespace='', **kwargs):
    """
    Select all controls in current scene
    :param namespace: str
    """

    all_controls = get_controls(namespace=namespace, **kwargs)
    if not all_controls:
        return

    tp.Dcc.select_node(all_controls)


@tp.Dcc.undo_decorator()
def key_controls(namespace='', **kwargs):
    """
    Sets a keyframe in all controls in current scene
    :param namespace: str
    :param kwargs:
    """

    all_controls = get_controls(namespace=namespace, **kwargs)
    if not all_controls:
        return

    maya.cmds.setKeyframe(all_controls, shape=0, controlPoints=0, hierarchy='none', breakdown=0)


@tp.Dcc.undo_decorator()
def mirror_control(control):
    """
    Find the right side control of a left side control and mirrors the control following next rules:
        - Mirror only will be applied if corresponding right side name exists
        - Replace left prefix and suffixes checking for validity
    :param control: str
    :return: str, mirrored control
    """

    if not control:
        return


@tp.Dcc.undo_decorator()
def mirror_controls(**kwargs):
    """
    Mirrors the CV positions of all controls in the current scene
    """

    mirrored_controls = list()

    all_controls = get_controls(**kwargs)
    if not all_controls:
        return mirrored_controls

    for control in all_controls:
        if control in mirror_controls:
            continue
        mirrored_control = mirror_control(control)
        mirrored_controls.append(mirror_control)

    return mirrored_controls


@tp.Dcc.undo_decorator()
def scale_controls(value, namespace='', **kwargs):
    all_controls = get_controls(namespace=namespace, **kwargs) or list()
    for control in all_controls:
        shapes = shape_utils.get_shapes(control)
        components = shape_utils.get_components_from_shapes(shapes)
        if not components:
            return
        pivot = maya.cmds.xform(control, query=True, rp=True, ws=True)
        maya.cmds.scale(value, value, value, components, p=pivot, r=True)
