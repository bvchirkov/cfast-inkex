#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2021 bvchirkov
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
