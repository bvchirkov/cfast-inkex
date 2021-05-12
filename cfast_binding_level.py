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

LINK = 'link'
UNLINK = 'unlink'
'''
Приявязка уровней
Первый выделенный - базовый
Второй выделенный - смещаемый

Запись производится в атрибуты родительского элемента "смещаемого" уровня
'''
class CfastLinkingLevels(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--tab")
        pars.add_argument("--linking", type=str, dest="linking")

    def effect(self):
        opt = self.options

        selected_elems = list(self.svg.get_selected())
        selected_elem_1 = selected_elems[0]
        selected_elem_2 = selected_elems[1]
        attr_name = 'cfast:link_id'

        if isinstance(selected_elem_1, inkex.Circle) and isinstance(selected_elem_2, inkex.Circle):
            level_parent = selected_elem_2.getparent().getparent()
            if opt.linking == LINK:
                level_parent.set(attr_name, '{},{}'.format(selected_elem_1.get_id(), selected_elem_2.get_id()))
            elif opt.linking == UNLINK:
                level_parent.pop(attr_name)

if __name__ == '__main__':
    CfastLinkingLevels().run()