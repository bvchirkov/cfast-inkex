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
