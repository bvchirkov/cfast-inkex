#!/usr/bin/env python
# coding=utf-8
#
# Copyright (c) 2021 - bvchirkov
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
Export a cfast geometry file (.in)
"""

from typing import overload
import inkex
from inkex import ShapeElement, Layer, Rectangle, Circle, Ellipse

LR = '\n'
DEFAULT_HEIGHT_LEVEL = 3.0

class CfastFace:
    REAR  = 'REAR'
    FRONT = 'FRONT'
    LEFT  = 'LEFT'
    RIGHT = 'RIGHT'

class CfastPoint:
    def __init__(self, x:float, y:float, z:float):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return '({},{},{})'.format(round(self.x, 2), round(self.y, 2), round(self.z, 2))

class CfastPolygon(list):
    def __init__(self, *args, **kwargs):
        super(CfastPolygon, self).__init__(args)
    
class Segment:
    HORISONTAL = 0
    VERTICAL = 1

    def __init__(self, p1:CfastPoint, p2:CfastPoint):
        self.p1 = p1
        self.p2 = p2
    
    def __str__(self):
        return '[{},{}]'.format(self.p1, self.p2)

class CfastScale:
    def __init__(self, k_height:float, k_width:float):
        self.k_height = k_height
        self.k_width  = k_width
    
    def convert_width(self, value:float) -> float:
        return self.convert(value, self.k_width)
    
    def convert_depth(self, value:float) -> float:
        return self.convert(value, self.k_height)
    
    def convert(self, value:float, k:float) -> float:
        return round(value * k, 3)

class CfastFile:
    HEAD = "&HEAD VERSION = 7600, TITLE = 'CFAST Simulation' /"
    TAIL = "&TAIL /"
    TIME = "&TIME SIMULATION = 3600 PRINT = 60 SMOKEVIEW = 15 SPREADSHEET = 15 /"
    INIT = "&INIT PRESSURE = 101325 RELATIVE_HUMIDITY = 50 INTERIOR_TEMPERATURE = 20 EXTERIOR_TEMPERATURE = 20 /"   
    MISC = "&MISC LOWER_OXYGEN_LIMIT = 0.15 ADIABATIC = .TRUE. /"
    
    # comparaments - array of class CfastComparament
    # wallvents - array of class CfastWallvents
    def __init__(self, comparaments:list, wallvents:list):
        self.comparaments = comparaments
        self.wallvents = wallvents
    
    def to_string(self) -> str:
        content = self.HEAD + LR
        
        content += LR + "!! Scenario Configuration" + LR
        content += self.TIME + LR
        content += self.INIT + LR
        content += self.MISC + LR

        content += LR + "!! Compartments" + LR
        for comp in self.comparaments:
            content += str(comp) + LR
        
        content += LR + "!! Wall vents" + LR
        for wallvent in self.wallvents:
            content += str(wallvent) + LR

        content += LR + self.TAIL
        return content

class CfastComparament():
    def __init__(self, id:str, depth:float, width:float, height:float, origin:CfastPoint):
        self.id = id
        self.depth = depth
        self.width = width
        self.height = height
        self.origin = (origin.x, origin.y, origin.z)
    
    def __str__(self):
        return '&COMP ID = \'{id}\'\n'.format(id=self.id) + \
               '      DEPTH = {depth} HEIGHT = {height} WIDTH = {width}\n'.format(depth=self.depth, width=self.width, height=self.height) + \
               '      CEILING_MATL_ID = \'OFF\' WALL_MATL_ID = \'OFF\' FLOOR_MATL_ID = \'OFF\'\n' + \
               '      ORIGIN = {origin} GRID = 50, 50, 50 /'.format(origin=str(self.origin)[1:-1])

class CfastWallVent():
    OUTSIDE = 'OUTSIDE'

    def __init__(self, id:str, comp_ids:list, offset:float, width:float, top=float(2), bottom=float(0)):
        self.type = 'WALL'
        self.id:str = id
        self.comp_ids:list = comp_ids
        self.offset = offset
        self.width = width
        self.top = top
        self.bottom = bottom
        self.face = None
    
    def __str__(self):
        comp_ids:str = None
        if len(self.comp_ids) == 2:
            comp_ids = str(['\'{}\''.format(comp_id) for comp_id in self.comp_ids])[1:-1].replace('\"', '')
        elif len(self.comp_ids) == 1:
            comp_ids = '\'{}\', \'{}\''.format(str(self.comp_ids[0]), self.OUTSIDE)

        return '&VENT TYPE = \'{wall_type}\' ID = \'{id}\'\n'.format(wall_type=self.type, id=self.id) + \
               '      COMP_IDS = {comp_ids}\n'.format(comp_ids=comp_ids) + \
               '      BOTTOM = {bottom} HEIGHT = {height} WIDTH = {width}\n'.format(bottom=self.bottom, height=self.top, width=self.width) + \
               '      FACE = \'{face}\' OFFSET = {offset} /'.format(face=self.face, offset=self.offset)

class CfastRectangle():
    def __init__(self, rect:Rectangle, z:float, scale:CfastScale):
        self.rect:Rectangle = rect
        self.scale = scale
        self.x0 = self.scale.convert_width(rect.left)
        self.y0 = (-1)*self.scale.convert_depth(rect.bottom)
        self.z0 = z
        
        self.width  = scale.convert_width(rect.width)
        self.height = scale.convert_depth(rect.height)
        
        self.init_points_and_segments()

    def set_offset(self, dx:float, dy:float):
        self.x0 = round(self.x0 + dx, 4)
        self.y0 = round(self.y0 + dy, 4)
        self.init_points_and_segments()

    def init_points_and_segments(self):
        x1 = self.x0 + self.width
        y1 = self.y0 + self.height
        
        self.p0 = CfastPoint(self.x0, self.y0, self.z0)
        self.p1 = CfastPoint(x1, self.y0, self.z0)
        self.p2 = CfastPoint(x1, y1, self.z0)
        self.p3 = CfastPoint(self.x0, y1, self.z0)
    
        self.front = Segment(self.p3, self.p0)
        self.left  = Segment(self.p0, self.p1)
        self.rear  = Segment(self.p1, self.p2)
        self.right = Segment(self.p2, self.p3)

    def get_polygon(self) -> CfastPolygon:
        return CfastPolygon(self.p0, self.p1, self.p2, self.p3)
    
    def get_segments(self):
        return (self.left, self.rear, self.right, self.front)

class CfastProcessing:

    def mapping(self, elements) -> None:
        def is_visible(elem:ShapeElement) -> bool:
            style:list = elem.get('style').split(';')
            for style_attr in style:
                s = style_attr.split(':')
                if s[0] == 'stroke' and s[1] == 'none':
                    return False
            else:
                return True

        comps_raw = {}
        wallvents_raw = {}
        spots = {}
        scale:CfastScale = None
        origin_z = 0.0
        levels_links = {}
        num_of_levels = 0

        for elem in elements:
            if isinstance(elem, Layer):
                if 'level' in elem.label.lower():
                    origin_z = DEFAULT_HEIGHT_LEVEL * num_of_levels
                    scale = CfastScale(float(elem.get('cfast:k_width')), float(elem.get('cfast:k_height')))
                    link_id = elem.get('cfast:link_id')
                    if link_id is not None:
                        levels_links[origin_z] = link_id.split(',')
                    num_of_levels += 1
            elif isinstance(elem, Rectangle) and is_visible(elem):
                raw_rect = CfastRectangle(elem, origin_z, scale)
                parent_name = elem.getparent().label.lower()
                eid = elem.get_id()
                if 'room' in parent_name:
                    comps_raw[eid] = raw_rect
                elif 'door' in parent_name:
                    wallvents_raw[eid] = raw_rect
            elif isinstance(elem, Circle) or isinstance(elem, Ellipse):
                spots[elem.get_id()] = {'x':scale.convert_width(elem.center[0]),
                                        'y':-scale.convert_depth(elem.center[1])}

        for z in levels_links:
            bottom_spot_id:str = levels_links[z][0]
            top_spot_id:str = levels_links[z][1]
            bottom_spot = spots[bottom_spot_id]
            top_spot = spots[top_spot_id]
            d_x:float = bottom_spot['x'] - top_spot['x']
            d_y:float = bottom_spot['y'] - top_spot['y']
            spots[top_spot_id] = {'x': top_spot['x'] + d_x, 'y': top_spot['y'] + d_y}

            for comp_rect in comps_raw.values():
                if comp_rect.z0 == z:
                    comp_rect.set_offset(d_x, d_y)

        comparaments = {}
        wallvents = {}
        for comp_rect_id in comps_raw: # Обход по всем прямоугольникам типа Помещение
            comp_rect:CfastRectangle = comps_raw.get(comp_rect_id)
            comparaments[comp_rect_id] = CfastComparament(id=comp_rect_id, \
                                                        depth=comp_rect.height, height=DEFAULT_HEIGHT_LEVEL, width=comp_rect.width, \
                                                        origin=comp_rect.p0)
            for vent_rect_id in wallvents_raw: # Обход каждого прямоугольника типа Дверь
                wallvent_rect:CfastRectangle = wallvents_raw.get(vent_rect_id)
                # Если дверь и помещение на разных уровнях, то их отношение не рассматривается
                if comp_rect.p0.z != wallvent_rect.p0.z: continue
                
                for wallvent_point in wallvent_rect.get_polygon(): # Обход каждой точки двери
                    # Далее ищем какая дверь, какие помещения соединяет
                    # Заодно формируем информацию по двери
                    if self.point_in_ractangle(wallvent_point, comp_rect.get_polygon()):
                        if vent_rect_id not in wallvents:
                            wallvents[vent_rect_id] = CfastWallVent(vent_rect_id, [comp_rect_id], 0.0, 1.0)
                        else:
                            wallvent:CfastWallVent = wallvents.get(vent_rect_id)
                            if comp_rect_id not in wallvent.comp_ids:
                                wallvent.comp_ids.append(comp_rect_id)
                            wallvent.comp_ids.sort(key = lambda id: int(id[4:]))
                            
                            if wallvent.face is None:
                                wallvent_additional = self.process_wallvent(wallvents_raw.get(vent_rect_id), comps_raw.get(wallvent.comp_ids[0]).get_segments())
                                wallvent.face = wallvent_additional['face']
                                wallvent.width = wallvent_additional['width']
                                wallvent.offset = wallvent_additional['offset']

        # Сортировка элементов по возрастанию индекса
        # Без сортировкаи  CFAST говорит об ошибке, потому что, например, 
        # дверь может соединять только помещение с меньшим индесом с помещеним с большим индексом,
        # а за индекс принимается номер элемента в списке, а не id
        # Сортировка выполняется по каждому этажу
        item_id:int = lambda item: (item.origin[2] if hasattr(item, 'origin') else 0,
                                    int(item.id[4:]) if '-' not in item.id else int(item.id[4:].replace('-', '')))

        comps   = sorted(list(comparaments.values()), key=item_id)
        w_vents = sorted(list(wallvents.values()),    key=item_id)

        return comps, w_vents

    '''
    Проверка вхождения точки в прямоугольник

    Для этого произвоится треангуляция прямоугольника. В данном случае треангуляция осуществляется вручную,
    потому что нам известно, что каждое помещение представляет прямоугольником.
    После получения треугольников поподает ли точка в треугольник, для чего выполняется проверка 
    с какой стороны от стороны треугольника находится точка.
    '''
    def point_in_ractangle(self, point:CfastPoint, polygon:CfastPolygon) -> bool:
        triangles = ((polygon[0], polygon[1], polygon[2]), (polygon[2], polygon[3], polygon[0]))

        '''
        Проверка с какой стороны находится точка
        '''
        def where_point(a:CfastPoint, b:CfastPoint, p:CfastPoint) -> int:
            s = (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)
            if s > 0: return 1        # Точка слева от вектора AB
            elif s < 0: return -1     # Точка справа от вектора AB
            else: return 0            # Точка на векторе, прямо по вектору или сзади вектора

        '''
        Проверка попадания точки в треугольник
        '''
        def is_point_in_triangle(triangle:tuple, p:CfastPoint) -> bool:
            q1 = where_point(triangle[0], triangle[1], p)
            q2 = where_point(triangle[1], triangle[2], p)
            q3 = where_point(triangle[2], triangle[0], p)
            return q1 >= 0 and q2 >= 0 and q3 >= 0
        
        '''
        Проверяем в какие треугольники попадает точка
        '''
        for triangle in triangles:
            if is_point_in_triangle(triangle, point):
                break
        else: # В это условие попадаем, если прошли цикл
            return False
        
        return True

    '''
    Проверка на пересечение двух линий
    '''
    def intersect(self, l1:Segment, l2:Segment) -> bool:
        def area(a:CfastPoint, b:CfastPoint, c:CfastPoint) -> float:
            return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
        
        def swap(x:float, y:float) -> float:
            return y, x

        def intersect_1(a:float, b:float, c:float, d:float) -> bool:
            if a > b: a, b = swap(a, b)
            if c > d: c, d = swap(c, d)
            return max(a, c) <= min(b, d)

        return intersect_1(l1.p1.x, l1.p2.x, l2.p1.x, l2.p2.x) \
           and intersect_1(l1.p1.y, l1.p2.y, l2.p1.y, l2.p2.y) \
           and area(l1.p1, l1.p2, l2.p1) * area(l1.p1, l1.p2, l2.p2) <= 0 \
           and area(l2.p1, l2.p2, l1.p1) * area(l2.p1, l2.p2, l1.p2) <= 0

    '''
    Обработка двери
    1) Определение стороны
    2) Определение ширины
    3) Определение смещения
    '''
    def process_wallvent(self, wallvent_raw:CfastRectangle, comp_segments:tuple):
        def get_crosses_segments(ss_wv, ss_comp):
            '''
             Для каждой стороны двери определяем с какими сторонами помещения она пересекается
             
             s_wv, ss_wv[(i+2)%4] - грани двери, которые пересекаются с граню помещения \n
             s_c - грань помещения
            '''
            b:bool = False
            for i, s_wv in enumerate(ss_wv):
                for s_c in ss_comp:
                    b = self.intersect(s_wv, s_c)
                    if b: break
                if b: break
            return s_wv, ss_wv[(i+2)%4], s_c
        
        def get_orientation_segment(segment:Segment) -> int:
            if segment.p1.x == segment.p2.x:
                return Segment.VERTICAL
            elif segment.p1.y == segment.p2.y:
                return Segment.HORISONTAL
        
        s1, s2, s3 = get_crosses_segments(wallvent_raw.get_segments(), comp_segments)
        wallvent_orientation = Segment.VERTICAL \
                                    if get_orientation_segment(s1) == Segment.HORISONTAL \
                                    else Segment.HORISONTAL
        wallvent_width:float = wallvent_raw.width if wallvent_orientation == Segment.HORISONTAL else wallvent_raw.height
      
        comp_faces = [CfastFace.FRONT, CfastFace.RIGHT, CfastFace.REAR, CfastFace.LEFT]
        
        comp_p0:CfastPoint = None
        vent_p0:CfastPoint = None
        vent_offset:float = None
        face_id:int = comp_segments.index(s3)
        face:CfastFace = comp_faces[face_id]
        comp_segment_orientation:int = get_orientation_segment(s3)
        if comp_segment_orientation == Segment.HORISONTAL:
            if face == CfastFace.FRONT:
                comp_p0 = s3.p1 if s3.p1.x < s3.p2.x else s3.p2
                vent_p0 = s1.p1 if s1.p1.x < s2.p1.x else s2.p1
            elif face == CfastFace.REAR:
                comp_p0 = s3.p1 if s3.p1.x > s3.p2.x else s3.p2
                vent_p0 = s1.p1 if s1.p1.x > s2.p1.x else s2.p1
            vent_offset = abs(comp_p0.x - vent_p0.x)
        elif comp_segment_orientation == Segment.VERTICAL:
            if face == CfastFace.LEFT:
                comp_p0 = s3.p1 if s3.p1.y > s3.p2.y else s3.p2
                vent_p0 = s1.p1 if s1.p1.y > s2.p1.y else s2.p1
            elif face == CfastFace.RIGHT:
                comp_p0 = s3.p1 if s3.p1.y < s3.p2.y else s3.p2
                vent_p0 = s1.p1 if s1.p1.y < s2.p1.y else s2.p1
            vent_offset = abs(comp_p0.y - vent_p0.y)
        
        return {'face':face, 'width':round(wallvent_width, 3), 'offset':round(vent_offset, 3)}

class ExportCfastGeometry(inkex.OutputExtension):
    select_all = (ShapeElement,)

    def save(self, stream):
        comps, w_vents = CfastProcessing().mapping(self.svg.selection.filter(ShapeElement).values())
        cfast_content = CfastFile(comps, w_vents).to_string()
        stream.write("{}\n".format(cfast_content).encode('utf-8'))

        self.msg('Экспорт данных успешно произведен')
        self.msg('=================================')
        self.msg('Количество помещений: {}'.format(len(comps)))
        self.msg('Количество проемов: {}'.format(len(w_vents)))
        self.msg('---------------------------------')
        self.msg(cfast_content)
    

if __name__ == '__main__':
    ExportCfastGeometry().run()
