# -*- coding: utf-8 -*-
"""
$Id$

Copyright 2011 Lars Kruse <devel@sumpfralle.de>

This file is part of PyCAM.

PyCAM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyCAM is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyCAM.  If not, see <http://www.gnu.org/licenses/>.
"""


import pycam.Plugins
import pycam.Geometry.Point


class ToolpathGrid(pycam.Plugins.PluginBase):

    UI_FILE = "toolpath_grid.ui"
    DEPENDS = ["Toolpaths"]
    CATEGORIES = ["Toolpath"]

    def setup(self):
        if self.gui:
            self._frame = self.gui.get_object("ToolpathGridFrame")
            self.core.register_ui("toolpath_handling", "Clone grid",
                    self._frame, 30)
            for objname in ("GridYCount", "GridXCount"):
                self.gui.get_object(objname).set_value(1)
            for objname in ("GridYCount", "GridXCount", "GridYDistance",
                    "GridXDistance"):
                self.gui.get_object(objname).connect("value-changed",
                        self._update_widgets)
            self.gui.get_object("GridCreate").connect("clicked",
                    self.create_toolpath_grid)
            self.core.register_event("toolpath-selection-changed",
                    self._update_widgets)
            self._update_widgets()
        return True

    def teardown(self):
        if self.gui:
            self.core.unregister_ui("toolpath_handling", self._frame)
            self.core.unregister_event("toolpath-selection-changed",
                    self._update_widgets)
        pass

    def _get_toolpaths_dim(self, toolpaths):
        if toolpaths:
            maxx = max([tp.maxx for tp in toolpaths])
            minx = min([tp.minx for tp in toolpaths])
            maxy = max([tp.maxy for tp in toolpaths])
            miny = min([tp.miny for tp in toolpaths])
            return (maxx - minx), (maxy - miny)
        else:
            return None, None

    def _update_widgets(self, widget=None):
        toolpaths = self.core.get("toolpaths").get_selected()
        if toolpaths:
            x_dim, y_dim = self._get_toolpaths_dim(toolpaths)
            x_count = self.gui.get_object("GridXCount").get_value()
            x_space = self.gui.get_object("GridXDistance").get_value()
            y_count = self.gui.get_object("GridYCount").get_value()
            y_space = self.gui.get_object("GridYDistance").get_value()
            x_width = x_dim * x_count + x_space * (x_count - 1)
            y_width = y_dim * y_count + y_space * (y_count - 1)
            self.gui.get_object("LabelGridXWidth").set_label("%g%s" % \
                    (x_width, self.core.get("unit_string")))
            self.gui.get_object("LabelGridYWidth").set_label("%g%s" % \
                    (y_width, self.core.get("unit_string")))
            self._frame.show()
        else:
            self._frame.hide()

    def create_toolpath_grid(self, widget=None):
        toolpaths = self.core.get("toolpaths").get_selected()
        x_count = int(self.gui.get_object("GridXCount").get_value())
        y_count = int(self.gui.get_object("GridYCount").get_value())
        x_space = self.gui.get_object("GridXDistance").get_value()
        y_space = self.gui.get_object("GridYDistance").get_value()
        x_dim, y_dim = self._get_toolpaths_dim(toolpaths)
        for toolpath in toolpaths:
            new_paths = []
            for x in range(x_count):
                for y in range(y_count):
                    shift = pycam.Geometry.Point.Vector(x * (x_space + x_dim),
                            y * (y_space + y_dim), 0)
                    for path in toolpath.paths:
                        new_path = pycam.Geometry.Path.Path()
                        new_path.points = [shift.add(p) for p in path.points]
                        new_paths.append(new_path)
            if not self.gui.get_object("KeepOriginal").get_active():
                toolpath.paths = new_paths
                self.core.emit_event("toolpath-changed")
            else:
                new_toolpath = toolpath.copy()
                new_toolpath.paths = new_paths
                self.core.get("toolpaths").append(new_toolpath)
        self.core.get("toolpaths").select(toolpaths)
