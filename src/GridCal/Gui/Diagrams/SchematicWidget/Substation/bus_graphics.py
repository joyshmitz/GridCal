# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations
import numpy as np
from typing import Union, TYPE_CHECKING, List, Dict
import webbrowser
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QRectF, QRect, QPointF
from PySide6.QtGui import QPen, QCursor, QIcon, QPixmap, QBrush, QColor
from PySide6.QtWidgets import QMenu, QGraphicsSceneMouseEvent

from GridCal.Gui.Diagrams.SchematicWidget.Injections.injections_template_graphics import InjectionTemplateGraphicItem
from GridCal.Gui.messages import yes_no_question, warning_msg
from GridCal.Gui.gui_functions import add_menu_entry
from GridCal.Gui.Diagrams.generic_graphics import (GenericDiagramWidget, ACTIVE, DEACTIVATED,
                                                   FONT_SCALE, EMERGENCY, TRANSPARENT)
from GridCal.Gui.Diagrams.SchematicWidget.terminal_item import BarTerminalItem, HandleItem
from GridCal.Gui.Diagrams.SchematicWidget.Injections.load_graphics import LoadGraphicItem, Load
from GridCal.Gui.Diagrams.SchematicWidget.Injections.generator_graphics import GeneratorGraphicItem, Generator
from GridCal.Gui.Diagrams.SchematicWidget.Injections.static_generator_graphics import (StaticGeneratorGraphicItem,
                                                                                       StaticGenerator)
from GridCal.Gui.Diagrams.SchematicWidget.Injections.battery_graphics import (BatteryGraphicItem, Battery)
from GridCal.Gui.Diagrams.SchematicWidget.Injections.shunt_graphics import (ShuntGraphicItem, Shunt)
from GridCal.Gui.Diagrams.SchematicWidget.Injections.external_grid_graphics import (ExternalGridGraphicItem,
                                                                                    ExternalGrid)
from GridCal.Gui.Diagrams.SchematicWidget.Injections.current_injection_graphics import (
    CurrentInjectionGraphicItem,
    CurrentInjection)
from GridCal.Gui.Diagrams.SchematicWidget.Injections.controllable_shunt_graphics import (
    ControllableShuntGraphicItem,
    ControllableShunt)

from GridCalEngine.enumerations import DeviceType, FaultType
from GridCalEngine.Devices.types import INJECTION_DEVICE_TYPES
from GridCalEngine.Devices.Substation import Bus

if TYPE_CHECKING:  # Only imports the below statements during type checking
    from GridCal.Gui.Diagrams.SchematicWidget.schematic_widget import SchematicWidget

SHUNT_GRAPHICS = Union[
    BatteryGraphicItem,
    ShuntGraphicItem,
    ExternalGridGraphicItem,
    ControllableShuntGraphicItem,
    LoadGraphicItem,
    GeneratorGraphicItem,
    StaticGeneratorGraphicItem,
    CurrentInjectionGraphicItem
]


class ShortCircuitFlags:
    """
    Short circuit flags
    """

    def __init__(self, sc_3p: bool = False, sc_lg: bool = False, sc_ll: bool = False, sc_llg: bool = False):
        self.sc_3p = sc_3p
        self.sc_lg = sc_lg
        self.sc_ll = sc_ll
        self.sc_llg = sc_llg

    def disable_all(self):
        """

        :return:
        """
        self.sc_3p = False
        self.sc_lg = False
        self.sc_ll = False
        self.sc_llg = False


class BusGraphicItem(GenericDiagramWidget, QtWidgets.QGraphicsRectItem):
    """
      Represents a block in the diagram
      Has an x and y and width and height
      width and height can only be adjusted with a tip in the lower right corner.

      - in and output ports
      - parameters
      - description
    """

    def __init__(self,
                 parent=None,
                 index=0,
                 editor: SchematicWidget = None,
                 bus: Bus = None,
                 h: int = 40,
                 w: int = 80,
                 x: float = 0,
                 y: float = 0,
                 draw_labels: bool = True,
                 r: float = 0):
        """

        :param parent:
        :param index:
        :param editor:
        :param bus:
        :param h:
        :param w:
        :param x:
        :param y:
        """
        GenericDiagramWidget.__init__(self, parent=parent, api_object=bus, editor=editor, draw_labels=draw_labels)
        QtWidgets.QGraphicsRectItem.__init__(self, parent)

        self.min_w = 180.0
        self.min_h = 40.0
        self.offset = 20
        self.h = h if h >= self.min_h else self.min_h
        self.w = w if w >= self.min_w else self.min_w
        self.r = r

        # loads, shunts, generators, etc...
        self._child_graphics: List[SHUNT_GRAPHICS] = list()

        # Enabled for short circuit
        self.sc_enabled = [False, False, False, False]
        self.sc_type = FaultType.ph3
        self.pen_width = 4

        # index
        self.index = index

        # Label:
        self.label = QtWidgets.QGraphicsTextItem(self.api_object.name if self.api_object is not None else "", self)
        self.label.setDefaultTextColor(ACTIVE['text'])
        self.label.setScale(FONT_SCALE)

        # square
        self.tile = QtWidgets.QGraphicsRectItem(0, 0, 20, 20, self)
        self.tile.setOpacity(0.7)

        # connection terminals the block
        self._terminal = BarTerminalItem('s', parent=self, editor=self._editor)  # , h=self.h))
        self._terminal.setPen(QPen(TRANSPARENT, self.pen_width, self.style,
                                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        # Create corner for resize:
        self.sizer = HandleItem(self._terminal, callback=self.change_size)
        self.sizer.setPos(self.w, self.h)
        self.sizer.setFlag(self.GraphicsItemFlag.ItemIsMovable)

        self.big_marker = None

        self.set_tile_color(self.color)

        self.setPen(QPen(TRANSPARENT, self.pen_width, self.style))
        self.setBrush(TRANSPARENT)
        self.setFlags(self.GraphicsItemFlag.ItemIsSelectable | self.GraphicsItemFlag.ItemIsMovable)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Update size:
        self.change_size(w=self.w)

        self.set_position(x, y)

    @property
    def api_object(self) -> Bus:
        return self._api_object

    @property
    def editor(self) -> SchematicWidget:
        return self._editor

    def get_associated_branch_graphics(self) -> List[GenericDiagramWidget]:
        """
        Get a list of all associated branch graphics
        :return:
        """
        conn: List[GenericDiagramWidget | SHUNT_GRAPHICS] = self._terminal.get_hosted_graphics()

        return conn

    def get_associated_widgets(self) -> List[GenericDiagramWidget | SHUNT_GRAPHICS]:
        """
        Get a list of all associated graphics
        :return:
        """
        conn: List[GenericDiagramWidget | SHUNT_GRAPHICS] = self.get_associated_branch_graphics()

        for graphics in self._child_graphics:
            conn.append(graphics)

        return conn

    def get_nexus_point(self) -> QPointF:
        """
        Get the connection point for the children nexus line
        :return: QPointF
        """
        return QPointF(self.x() + self.rect().width() / 2.0,
                       self.y() + self.rect().height() + self._terminal.h / 2.0)

    def recolour_mode(self) -> None:
        """
        Change the colour according to the system theme
        """
        super().recolour_mode()

        self.label.setDefaultTextColor(ACTIVE['text'])
        self.set_tile_color(self.color)

        for e in self._child_graphics:
            if e is not None:
                e.recolour_mode()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        """
        On mouse move of this object...
        Args:
            event: QGraphicsSceneMouseEvent inherited
        """
        super().mouseMoveEvent(event)
        self._editor.update_diagram_element(device=self.api_object,
                                            x=self.pos().x(),
                                            y=self.pos().y(),
                                            w=self.w,
                                            h=self.h,
                                            r=self.rotation(),
                                            draw_labels=self.draw_labels,
                                            graphic_object=self)

    def add_big_marker(self, color: Union[None, QColor] = QColor(255, 0, 0, 255), tool_tip_text: str = ""):
        """
        Add a big marker to the bus
        :param color: Qt Color ot the marker
        :param tool_tip_text: tool tip text to display
        """
        if color is not None:
            if self.big_marker is None:
                self.big_marker = QtWidgets.QGraphicsEllipseItem(0, 0, 180, 180, parent=self)

            self.big_marker.setBrush(color)
            self.big_marker.setOpacity(0.5)
            self.big_marker.setToolTip(tool_tip_text)

    def delete_big_marker(self) -> None:
        """
        Delete the big marker
        """
        if self.big_marker is not None:
            self._editor._remove_from_scene(self.big_marker)
            self.big_marker = None

    def set_position(self, x: float, y: float) -> None:
        """
        Set the bus x, y position
        :param x: x in pixels
        :param y: y in pixels
        """
        if np.isnan(x):
            x = 0.0
        if np.isnan(y):
            y = 0.0
        self.setPos(QPointF(x, y))

    def set_tile_color(self, brush: QBrush) -> None:
        """
        Set the color of the title
        Args:
            brush:  Qt Color
        """
        self.tile.setBrush(brush)
        self._terminal.setBrush(brush)

    def merge(self, other_bus_graphic: "BusGraphicItem") -> None:
        """
        Merge another BusGraphicItem into this
        :param other_bus_graphic: BusGraphicItem
        """
        self._child_graphics += other_bus_graphic._child_graphics

    def update(self, rect: Union[QRectF, QRect] = ...):
        """
        Update the object
        :return:
        """
        self.change_size(w=self.w)

    def set_height(self, h: int):
        """
        Set the height of the
        :param h:
        :return:
        """
        self.setRect(0.0, 0.0, self.w, h)
        self.h = h

    def change_size(self, w: int, dummy: float = 0.0):
        """
        Resize block function
        :param w:
        :param dummy:
        :return:
        """
        # Limit the block size to the minimum size:
        self.w = w if w > self.min_w else self.min_w
        self.setRect(0.0, 0.0, self.w, self.min_h)
        y0 = self.offset
        x0 = 0

        # center label:
        self.label.setPos(self.w + 5, -20)

        # lower
        self._terminal.setPos(x0, y0)
        self._terminal.setRect(0, 20, self.w, 10)

        # rearrange children
        self.arrange_children()

        # update editor diagram position
        self._editor.update_diagram_element(device=self.api_object,
                                            x=self.pos().x(),
                                            y=self.pos().y(),
                                            w=self.w,
                                            h=int(self.min_h),
                                            r=self.rotation(),
                                            draw_labels=self.draw_labels,
                                            graphic_object=self)

        return self.w, self.min_h

    def arrange_children(self) -> None:
        """
        This function sorts the load and generators icons
        Returns:
            Nothing
        """
        y0 = self.h + 40
        n = len(self._child_graphics)
        inc_x = self.w / (n + 1)
        x = inc_x
        for elm in self._child_graphics:
            elm.setPos(x - elm.w / 2, y0)
            x += inc_x

        # Arrange line positions
        self._terminal.process_callbacks(self.pos() + self._terminal.pos())

    def create_children_widgets(self, injections_by_tpe: Dict[DeviceType, List[INJECTION_DEVICE_TYPES]]):
        """
        Create the icons of the elements that are attached to the API bus object
        Returns: Nothing
        """

        for tpe, dev_list in injections_by_tpe.items():

            if tpe == DeviceType.LoadDevice:
                for elm in dev_list:
                    self.add_load(elm)

            elif tpe == DeviceType.StaticGeneratorDevice:
                for elm in dev_list:
                    self.add_static_generator(elm)

            elif tpe == DeviceType.GeneratorDevice:
                for elm in dev_list:
                    self.add_generator(elm)

            elif tpe == DeviceType.ShuntDevice:
                for elm in dev_list:
                    self.add_shunt(elm)

            elif tpe == DeviceType.BatteryDevice:
                for elm in dev_list:
                    self.add_battery(elm)

            elif tpe == DeviceType.ExternalGridDevice:
                for elm in dev_list:
                    self.add_external_grid(elm)

            elif tpe == DeviceType.CurrentInjectionDevice:
                for elm in dev_list:
                    self.add_current_injection(elm)

            elif tpe == DeviceType.ControllableShuntDevice:
                for elm in dev_list:
                    self.add_controllable_shunt(elm)

            else:
                raise Exception("Unknown device type:" + str(tpe))

        self.arrange_children()

    def contextMenuEvent(self, event: QtWidgets.QGraphicsSceneContextMenuEvent):
        """
        Display context menu
        @param event:
        @return:
        """
        menu = QMenu()
        menu.addSection("Bus")

        add_menu_entry(menu=menu,
                       text="Active",
                       icon_path="",
                       function_ptr=self.enable_disable_toggle,
                       checkeable=True,
                       checked_value=self.api_object.active)

        add_menu_entry(menu=menu,
                       text="Draw labels",
                       icon_path="",
                       function_ptr=self.enable_disable_label_drawing,
                       checkeable=True,
                       checked_value=self.draw_labels)

        sc = menu.addMenu('Short circuit')
        sc_icon = QIcon()
        sc_icon.addPixmap(QPixmap(":/Icons/icons/short_circuit.svg"))
        sc.setIcon(sc_icon)

        sc_3p = sc.addAction('3-phase')
        sc_3p_icon = QIcon()
        sc_3p_icon.addPixmap(QPixmap(":/Icons/icons/short_circuit.svg"))
        sc_3p.setIcon(sc_3p_icon)
        sc_3p.setCheckable(True)
        sc_3p.setChecked(self.sc_enabled[0])
        sc_3p.triggered.connect(self.enable_disable_sc_3p)

        sc_lg = sc.addAction('Line-Ground')
        sc_lg_icon = QIcon()
        sc_lg_icon.addPixmap(QPixmap(":/Icons/icons/short_circuit.svg"))
        sc_lg.setIcon(sc_lg_icon)
        sc_lg.setCheckable(True)
        sc_lg.setChecked(self.sc_enabled[1])
        sc_lg.triggered.connect(self.enable_disable_sc_lg)

        sc_ll = sc.addAction('Line-Line')
        sc_ll_icon = QIcon()
        sc_ll_icon.addPixmap(QPixmap(":/Icons/icons/short_circuit.svg"))
        sc_ll.setIcon(sc_ll_icon)
        sc_ll.setCheckable(True)
        sc_ll.setChecked(self.sc_enabled[2])
        sc_ll.triggered.connect(self.enable_disable_sc_ll)

        sc_llg = sc.addAction('Line-Line-Ground')
        sc_llg_icon = QIcon()
        sc_llg_icon.addPixmap(QPixmap(":/Icons/icons/short_circuit.svg"))
        sc_llg.setIcon(sc_llg_icon)
        sc_llg.setCheckable(True)
        sc_llg.setChecked(self.sc_enabled[3])
        sc_llg.triggered.connect(self.enable_disable_sc_llg)

        sc_no = sc.addAction('Disable')
        sc_no.triggered.connect(self.disable_sc)

        # types
        # ph3 = '3x'
        # LG = 'LG'
        # LL = 'LL'
        # LLG = 'LLG'

        add_menu_entry(menu=menu,
                       text="Is a DC bus",
                       icon_path=":/Icons/icons/dc.svg",
                       function_ptr=self.enable_disable_dc,
                       checkeable=True,
                       checked_value=self.api_object.is_dc)

        add_menu_entry(menu=menu,
                       text="Plot profiles",
                       icon_path=":/Icons/icons/plot.svg",
                       function_ptr=self.plot_profiles)

        add_menu_entry(menu,
                       text='Arrange',
                       icon_path=":/Icons/icons/automatic_layout.svg",
                       function_ptr=self.arrange_children)

        # add_menu_entry(menu,
        #                text='Rotate',
        #                # icon_path=":/Icons/icons/automatic_layout.svg",
        #                function_ptr=self.rotate)

        add_menu_entry(menu,
                       text='Assign active state to profile',
                       icon_path=":/Icons/icons/assign_to_profile.svg",
                       function_ptr=self.assign_status_to_profile)

        add_menu_entry(menu, text='Delete',
                       icon_path=":/Icons/icons/delete_schematic.svg",
                       function_ptr=self.delete)

        add_menu_entry(menu, text='Expand schematic',
                       icon_path=":/Icons/icons/grid_icon.svg",
                       function_ptr=self.expand_diagram_from_bus)

        add_menu_entry(menu, text='Vicinity diagram from here',
                       icon_path=":/Icons/icons/grid_icon.svg",
                       function_ptr=self.new_vicinity_diagram_from_here)

        add_menu_entry(menu=menu,
                       text="Open in street view",
                       icon_path=":/Icons/icons/map.svg",
                       function_ptr=self.open_street_view)

        menu.addSection("Add")

        # Actions under the "Add" section
        add_menu_entry(menu, text='Load',
                       icon_path=":/Icons/icons/add_load.svg",
                       function_ptr=self.add_load)

        add_menu_entry(menu, text='Current injection',
                       icon_path=":/Icons/icons/add_load.svg",
                       function_ptr=self.add_current_injection)

        add_menu_entry(menu, text='Shunt',
                       icon_path=":/Icons/icons/add_shunt.svg",
                       function_ptr=self.add_shunt)

        add_menu_entry(menu,
                       text='Controllable shunt',
                       icon_path=":/Icons/icons/add_shunt.svg",
                       function_ptr=self.add_controllable_shunt)

        add_menu_entry(menu, text='Generator',
                       icon_path=":/Icons/icons/add_gen.svg",
                       function_ptr=self.add_generator)

        add_menu_entry(menu, text='Static generator',
                       icon_path=":/Icons/icons/add_stagen.svg",
                       function_ptr=self.add_static_generator)

        add_menu_entry(menu, text='Battery',
                       icon_path=":/Icons/icons/add_batt.svg",
                       function_ptr=self.add_battery)

        add_menu_entry(menu,
                       text='External grid',
                       icon_path=":/Icons/icons/add_external_grid.svg",
                       function_ptr=self.add_external_grid)

        menu.exec_(event.screenPos())

    def assign_status_to_profile(self):
        """
        Assign the snapshot rate to the profile
        """
        self._editor.set_active_status_to_profile(self.api_object)

    # def delete_all_connections(self, delete_from_db: bool) -> None:
    #     """
    #     Delete all bus connections
    #     """
    #     self._terminal.remove_all_connections(delete_from_db=delete_from_db)

    def delete(self) -> None:
        """
        Remove this element
        @return:
        """
        deleted, delete_from_db_final = self.editor.delete_with_dialogue(selected=[self], delete_from_db=False)
        if deleted:
            self._terminal.clear()

    def delete_child(self, obj: SHUNT_GRAPHICS | InjectionTemplateGraphicItem):
        """
        Delete a child object
        :param obj:
        """
        self._child_graphics.remove(obj)

    def update_color(self):
        """
        Update the colour
        """
        if self.api_object.active:
            self.set_tile_color(QBrush(ACTIVE['color']))
        else:
            self.set_tile_color(QBrush(DEACTIVATED['color']))

    def expand_diagram_from_bus(self) -> None:
        """
        Expands the diagram from this bus
        """
        self._editor.expand_diagram_from_bus(root_bus=self.api_object)

    def new_vicinity_diagram_from_here(self):
        """
        Create new vicinity diagram
        :return:
        """
        if self.api_object is not None:
            self.editor.gui.new_bus_branch_diagram_from_bus(root_bus=self.api_object)
        else:
            warning_msg("The api object is none :(")

    def enable_disable_toggle(self):
        """
        Toggle bus element state
        @return:
        """
        if self.api_object is not None:

            # change the bus state (snapshot)
            self.api_object.active = not self.api_object.active

            # change the Branches state (snapshot)
            for host in self._terminal.hosting_connections:
                if host.api_object is not None:
                    host.set_enable(val=self.api_object.active)

            self.update_color()

            if self._editor.circuit.has_time_series:
                ok = yes_no_question('Do you want to update the time series active status accordingly?',
                                     'Update time series active status')

                if ok:
                    # change the bus state (time series)
                    self._editor.set_active_status_to_profile(self.api_object, override_question=True)

                    # change the Branches state (time series)
                    for host in self._terminal.hosting_connections:
                        if host.api_object is not None:
                            self._editor.set_active_status_to_profile(host.api_object, override_question=True)

    def any_short_circuit(self) -> bool:
        """
        Determine if there are short circuits enabled
        :return:
        """
        for t in self.sc_enabled:
            if t:
                return True
        return False

    def enable_sc(self) -> None:
        """
        Enable the short circuit
        """
        self.tile.setPen(QPen(QColor(EMERGENCY['color']), self.pen_width))

    def disable_sc(self):
        """
        Disable short circuit
        """
        self.tile.setPen(QPen(TRANSPARENT, self.pen_width))
        self.sc_enabled = [False, False, False, False]

    def enable_disable_sc_3p(self):
        """
        Enable 3-phase short circuit
        """
        self.sc_enabled = [True, False, False, False]
        self.sc_type = FaultType.ph3
        self.enable_sc()

    def enable_disable_sc_lg(self):
        """
        Enable line ground short circuit
        """
        self.sc_enabled = [False, True, False, False]
        self.sc_type = FaultType.LG
        self.enable_sc()

    def enable_disable_sc_ll(self):
        """
        Enable line-line short circuit
        """
        self.sc_enabled = [False, False, True, False]
        self.sc_type = FaultType.LL
        self.enable_sc()

    def enable_disable_sc_llg(self):
        """
        Enable line-line-ground short circuit
        """
        self.sc_enabled = [False, False, False, True]
        self.sc_type = FaultType.LLG
        self.enable_sc()

    def enable_disable_dc(self):
        """
        Activates or deactivates the bus as a DC bus
        """
        if self._api_object.is_dc:
            self._api_object.is_dc = False
        else:
            self._api_object.is_dc = True

    def rotate(self):
        """

        :return:
        """
        self.r += 90
        self.setRotation(self.r)
        self._editor.update_diagram_element(device=self._api_object,
                                            x=self.pos().x(),
                                            y=self.pos().y(),
                                            w=self.w,
                                            h=self.h,
                                            r=self.r,
                                            draw_labels=self.draw_labels,
                                            graphic_object=self)

    def plot_profiles(self) -> None:
        """
        Plot profiles
        """
        # get the index of this object
        i = self._editor.circuit.get_buses().index(self._api_object)
        self._editor.plot_bus(i, self._api_object)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        """
        mouse press: display the editor
        :param event: QGraphicsSceneMouseEvent
        """

        if self._api_object.device_type == DeviceType.BusDevice:
            self._editor.set_editor_model(api_object=self._api_object)

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        """
        Mouse double click
        :param event: event object
        """
        title = self._api_object.name if self._api_object is not None else ""
        msg = ""
        self.label.setHtml(f'<html><head/><body><p><span style=" font-size:10pt;">{title}<br/></span>'
                           f'<span style=" font-size:6pt;">{msg}</span></p></body></html>')

        self.setToolTip(msg)

    def get_terminal(self) -> BarTerminalItem:
        """
        Get the hosting terminal of this bus object
        :return: TerminalItem
        """
        return self._terminal

    def add_object(self, api_obj: Union[None, INJECTION_DEVICE_TYPES] = None):
        """
        Add any recognized object
        :param api_obj: EditableDevice
        """

        if api_obj.device_type == DeviceType.GeneratorDevice:
            self.add_generator(api_obj=api_obj)

        elif api_obj.device_type == DeviceType.LoadDevice:
            self.add_load(api_obj=api_obj)

        elif api_obj.device_type == DeviceType.StaticGeneratorDevice:
            self.add_static_generator(api_obj=api_obj)

        elif api_obj.device_type == DeviceType.ShuntDevice:
            self.add_shunt(api_obj=api_obj)

        elif api_obj.device_type == DeviceType.BatteryDevice:
            self.add_battery(api_obj=api_obj)

        elif api_obj.device_type == DeviceType.ExternalGridDevice:
            self.add_external_grid(api_obj=api_obj)

        elif api_obj.device_type == DeviceType.CurrentInjectionDevice:
            self.add_current_injection(api_obj=api_obj)

        elif api_obj.device_type == DeviceType.ControllableShuntDevice:
            self.add_controllable_shunt(api_obj=api_obj)

        else:
            raise Exception("Cannot add device of type {}".format(api_obj.device_type.value))

    def add_load(self, api_obj: Union[Load, None] = None):
        """
        Add load object to bus
        :param api_obj:
        :return:
        """
        if api_obj is None or type(api_obj) is bool:
            api_obj = self._editor.circuit.add_load(bus=self._api_object)

        _grph = LoadGraphicItem(parent=self, api_obj=api_obj, editor=self._editor)
        self._child_graphics.append(_grph)
        self.arrange_children()
        return _grph

    def add_shunt(self, api_obj: Union[Shunt, None] = None):
        """
        Add shunt device
        :param api_obj: If None, a new shunt is created
        """
        if api_obj is None or type(api_obj) is bool:
            api_obj = self._editor.circuit.add_shunt(bus=self._api_object)

        _grph = ShuntGraphicItem(parent=self, api_obj=api_obj, editor=self._editor)
        self._child_graphics.append(_grph)
        self.arrange_children()
        return _grph

    def add_generator(self, api_obj: Union[Generator, None] = None):
        """
        Add generator
        :param api_obj: if None, a new generator is created
        """
        if api_obj is None or type(api_obj) is bool:
            api_obj = self._editor.circuit.add_generator(bus=self._api_object)

        _grph = GeneratorGraphicItem(parent=self, api_obj=api_obj, editor=self._editor)
        self._child_graphics.append(_grph)
        self.arrange_children()
        return _grph

    def add_static_generator(self, api_obj: Union[StaticGenerator, None] = None):
        """
        Add static generator
        :param api_obj: If none, a new static generator is created
        :return:
        """
        if api_obj is None or type(api_obj) is bool:
            api_obj = self._editor.circuit.add_static_generator(bus=self._api_object)

        _grph = StaticGeneratorGraphicItem(parent=self, api_obj=api_obj, editor=self._editor)
        self._child_graphics.append(_grph)
        self.arrange_children()

        return _grph

    def add_battery(self, api_obj: Union[Battery, None] = None):
        """

        :param api_obj:
        :return:
        """
        if api_obj is None or type(api_obj) is bool:
            api_obj = self._editor.circuit.add_battery(bus=self._api_object)

        _grph = BatteryGraphicItem(parent=self, api_obj=api_obj, editor=self._editor)
        self._child_graphics.append(_grph)
        self.arrange_children()

        return _grph

    def add_external_grid(self, api_obj: Union[ExternalGrid, None] = None):
        """

        :param api_obj:
        :return:
        """
        if api_obj is None or type(api_obj) is bool:
            api_obj = self._editor.circuit.add_external_grid(bus=self._api_object)

        _grph = ExternalGridGraphicItem(parent=self, api_obj=api_obj, editor=self._editor)
        self._child_graphics.append(_grph)
        self.arrange_children()

        return _grph

    def add_current_injection(self, api_obj: Union[CurrentInjection, None] = None):
        """

        :param api_obj:
        :return:
        """
        if api_obj is None or type(api_obj) is bool:
            api_obj = self._editor.circuit.add_current_injection(bus=self._api_object)

        _grph = CurrentInjectionGraphicItem(parent=self, api_obj=api_obj, editor=self._editor)
        self._child_graphics.append(_grph)
        self.arrange_children()

        return _grph

    def add_controllable_shunt(self, api_obj: Union[ControllableShunt, None] = None):
        """

        :param api_obj:
        :return:
        """
        if api_obj is None or type(api_obj) is bool:
            api_obj = self._editor.circuit.add_controllable_shunt(bus=self._api_object)

        _grph = ControllableShuntGraphicItem(parent=self, api_obj=api_obj, editor=self._editor)
        self._child_graphics.append(_grph)
        self.arrange_children()

        return _grph

    def set_values(self, i: int, Vm: float, Va: float, P: float, Q: float, tpe: str, format_str="{:10.2f}"):
        """

        :param i:
        :param Vm:
        :param Va:
        :param P:
        :param Q:
        :param tpe:
        :param format_str:
        :return:
        """
        if self.draw_labels:
            vm = format_str.format(Vm)
            vm_kv = format_str.format(Vm * self._api_object.Vnom)
            va = format_str.format(Va)
            msg = f"Bus {i}"
            if tpe is not None:
                msg += f" [{tpe}]"
            msg += "<br>"
            msg += f"v={vm}&lt;{va}º pu<br>"
            msg += f"V={vm_kv} KV<br>"
            if P is not None:
                p = format_str.format(P)
                q = format_str.format(Q)
                msg += f"P={p} MW<br>Q={q} MVAr"
        else:
            msg = ""

        title = self._api_object.name if self._api_object is not None else ""
        self.label.setHtml(f'<html><head/><body><p><span style=" font-size:10pt;">{title}<br/></span>'
                           f'<span style=" font-size:6pt;">{msg}</span></p></body></html>')

        self.setToolTip(msg)

    def open_street_view(self):
        """
        Call open street maps
        :return:
        """
        # https://maps.google.com/?q=<lat>,<lng>
        if self._api_object is not None:
            url = f"https://www.google.com/maps/?q={self._api_object.latitude},{self._api_object.longitude}"
            webbrowser.open(url)
        else:
            warning_msg(f"No API object available :(")

    def __str__(self):

        if self._api_object is None:
            return f"Bus graphics {hex(id(self))}"
        else:
            return f"Graphics of {self._api_object.name} [{hex(id(self))}]"

    def __repr__(self):
        return str(self)
