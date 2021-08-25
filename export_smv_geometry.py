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

"""
Export a Smokeview geometry file (.smv)
"""

import inkex
from inkex import ShapeElement
from export_cfast_geometry import CfastFace, CfastProcessing, CfastComparament, CfastPoint

LR = '\n'

class SmvFile():
    ZONE = "ZONE \n {}\n PRESSURE\n P\n Pa\n Layer Height\n zlay\n m\n TEMPERATURE\n TEMP\n C\n TEMPERATURE\n TEMP\n C"
    ROOM = "ROOM"
    HVENTPOS = "HVENTPOS"
    
    # comparaments - array of class CfastComparament
    # wallvents - array of class CfastWallvents
    def __init__(self, comparaments:list, wallvents:list, ink_self) -> None:
        self.comparaments = comparaments
        self.wallvents = wallvents
        self.ink_self = ink_self
    
    def to_string(self) -> str:
        content = self.ZONE.format(self.ink_self.svg.name.replace('smv', 'svg')) + LR
        
        r = lambda item: round(item, 4)
        
        comps_dict = dict()
        for i, comp in enumerate(self.comparaments):
            content += self.ROOM + LR
            content += '  {}  {}  {}'.format(comp.width, comp.depth, comp.height) + LR
            content += '  {}  {}  {}'.format(comp.origin[0], comp.origin[1], comp.origin[2]) + LR
            comps_dict[comp.id] = (i+1, comp)
        
        for wallvent in self.wallvents:
            content += self.HVENTPOS + LR
            wv_cidx  = wallvent.comp_ids
            from_obj = comps_dict[wv_cidx[0]]
            from_idx:int = from_obj[0]
            to_idx:int   = 0
            if len(wv_cidx) == 1:
                to_idx = len(comps_dict)
            else:
                to_idx = comps_dict[wv_cidx[1]][0]

            comp:CfastComparament = from_obj[1]
            face = wallvent.face
            offset = wallvent.offset
            p1:CfastPoint = None
            p2:CfastPoint = None
            if face == CfastFace.FRONT:
                p1 = CfastPoint(offset,                 0, wallvent.bottom)
                p2 = CfastPoint(p1.x + wallvent.width,  0, wallvent.top)
            elif face == CfastFace.REAR:
                p1 = CfastPoint(comp.width - offset,    comp.depth, wallvent.bottom)
                p2 = CfastPoint(p1.x - wallvent.width,  p1.y,       wallvent.top)
            elif face == CfastFace.LEFT:
                p1 = CfastPoint(0, comp.depth - offset,     wallvent.bottom)
                p2 = CfastPoint(0, p1.y - wallvent.width,   wallvent.top)
            elif face == CfastFace.RIGHT:
                p1 = CfastPoint(comp.width, offset,                 wallvent.bottom)
                p2 = CfastPoint(p1.x,       p1.y + wallvent.width,  wallvent.top)

            content += '  {}  {}  {}  {}  {}  {}  {}  {}'.format(from_idx, to_idx,
                                                                 r(p1.x), r(p2.x), 
                                                                 r(p1.y), r(p2.y),
                                                                 r(p1.z), r(p2.z)
                                                                 ) + LR

        return content

class ExportCfastGeometry(inkex.OutputExtension):
    select_all = (ShapeElement,)

    def save(self, stream):
        comps, w_vents = CfastProcessing().mapping(self.svg.selection.filter(ShapeElement).values())

        smv_content = SmvFile(comps, w_vents, self).to_string()
        stream.write("{}\n".format(smv_content).encode('utf-8'))

        self.msg('Экспорт данных успешно произведен')
        self.msg('=================================')
        self.msg('Количество помещений: {}'.format(len(comps)))
        self.msg('Количество проемов: {}'.format(len(w_vents)))
        self.msg('---------------------------------')
        self.msg(smv_content)
    

if __name__ == '__main__':
    ExportCfastGeometry().run()
