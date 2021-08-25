#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2021 - bvchirkov
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import inkex

class CfastBindingGeom(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--tab")
        pars.add_argument("--width",    type=float,          dest="width")
        pars.add_argument("--depth",    type=float,          dest="depth")

    def effect(self):
        opt = self.options

        selected_elem = list(self.svg.selection.filter(inkex.Rectangle).values())[0]
        level_parent = selected_elem.getparent().getparent()
        level_parent.set("cfast:k_width", opt.width/selected_elem.width)
        level_parent.set("cfast:k_height", opt.depth/selected_elem.height)

if __name__ == '__main__':
    CfastBindingGeom().run()