# zlib license
#   (A small part of this software is taken from the original turtle module, also
#       using the zlib license, it is marked below)

# Copyright (c) 2023 Electric
# 
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
# 
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
# 
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.



"""Turtle G-Code

A small library for converting python turtle commands into
G-Code for use with a pen-plotter.

Simply import this library instead of the default turtle one
and then add a call to turtle.write_gcode() at the end to
get the G-Code of the shapes you have drawn.


Things this library doesn't support:
 - Stamps
 - Writing Text
 - Different colours/thicknesses of pen
 - Undoing actions (undo functions throw an error if called)

Have fun :)
"""


import turtle
from dataclasses import dataclass
import tkinter as TK

import math

# we don't bother with stamps, or with the fancy shape stuff


Position = tuple[float, float]

@dataclass
class ScaleInfo():
    # scale factor, turtle_pos * scale = machine_pos
    scale: float
    # if the coordinates are rotated 90deg
    do_rotation: bool
    # offset in machine coordinates of the bottom let origin of the work area
    offset: Position
    # top of the drawing in turtle coordinates
    top: float
    # bottom of the drawing in turtle coordinates
    bottom: float

def position_gcode(pos: Position, info: ScaleInfo):
    if not info.do_rotation:
        return f"X{info.offset[0] + pos[0]*info.scale:.3f} Y{info.offset[1] + pos[1]*info.scale:.3f}"
    else:
        return f"X{info.offset[0] + (info.top-pos[1]+info.bottom)*info.scale:.3f} Y{info.offset[1] + pos[0]*info.scale:.3f}"

def coords_at_dist(start: Position, theta: float, distance: float) -> Position:
    """angle is in radians, taking 0 to be pointing along ht positive x-axis
    """
    return (
        start[0] + distance * math.cos(theta),
        start[1] + distance * math.sin(theta)
    )

def angle_between_points(start: Position, end: Position) -> float:
    vert = end[1]-start[1]
    horiz = end[0]-start[0]
    return math.atan2(vert, horiz)


@dataclass
class Extents():
    top: float
    bottom: float
    left: float
    right: float

@dataclass
class LinearMove():
    start: Position
    end: Position

    def extents(self) -> Extents:
        return Extents(
            max(self.start[1], self.end[1]),
            min(self.start[1], self.end[1]),
            min(self.start[0], self.end[0]),
            max(self.start[0], self.end[0]),
        )

    def write_gcode(self, info: ScaleInfo, circle_mode) -> str:
        return f"G1 {position_gcode(self.end, info)}"

@dataclass
class CircleMove():
    # circles that are regular polygons are inscribed within the circle of that radius, and always begin drawing
    # at a vertex

    # steps is the number of lines used to draw the whole extent, NOT the number of lines for the whole circle
    # (always ends at the vertex of an extent point)

    start: Position
    end: Position
    centre: Position
    radius: float
    # measured in radians
    extent: float
    steps: float | None
    
    def extents(self) -> Extents:
        # temporary code, not good enough
        rad = abs(self.radius)
        if self.extent >= math.tau:
            return Extents(
                top=self.centre[1]+rad,
                bottom=self.centre[1]-rad,
                left=self.centre[0]-rad,
                right=self.centre[0]+rad
            )

        start_angle = angle_between_points(self.centre, self.start)
        end_angle = angle_between_points(self.centre, self.end)

        def rotate_right(start_angle, rotate_by)->float:
            t = (start_angle-rotate_by)%math.tau
            if t > math.pi:
                return t-math.tau
            return t

        # right
        temp_start = rotate_right(start_angle, 0)
        temp_end = rotate_right(end_angle, 0)
        right_extent = rad*math.cos(min(abs(temp_start), abs(temp_end)))

        # top
        temp_start = rotate_right(start_angle, math.pi/2)
        temp_end = rotate_right(end_angle, math.pi/2)
        top_extent = rad*math.cos(min(abs(temp_start), abs(temp_end)))

        # left
        temp_start = rotate_right(start_angle, math.pi)
        temp_end = rotate_right(end_angle, math.pi)
        left_extent = rad*math.cos(min(abs(temp_start), abs(temp_end)))

        # bottom
        temp_start = rotate_right(start_angle, -math.pi/2)
        temp_end = rotate_right(end_angle, -math.pi/2)
        bottom_extent = rad*math.cos(min(abs(temp_start), abs(temp_end)))

        return Extents(
                top=self.centre[1]+top_extent,
                bottom=self.centre[1]-bottom_extent,
                left=self.centre[0]-left_extent,
                right=self.centre[0]+right_extent
            )

    def _write_gcode_steps(self, info: ScaleInfo) -> str:
        angle = angle_between_points(self.centre, self.start)
        end_command = ""

        step_size = self.extent/self.steps
        if self.radius < 0:
            # rotate clockwise instead
            step_size = -step_size
        
        for _ in range(self.steps):
            angle += step_size
            angle %= math.tau
            new_pos = coords_at_dist(self.centre, angle, abs(self.radius))
            end_command += f"G1 {position_gcode(new_pos, info)}\n"
        
        end_command = end_command.removesuffix("\n")
        return end_command

    def _write_gcode_circle_radius(self, info: ScaleInfo) -> str:
        """Writes with end point and radius
        """
        # we can move in steps of up to pi radians, but I had issues with one gcode simulator doing that
        # so instead we move in steps of pi/2 radians
        angle = angle_between_points(self.centre, self.start)
        extent = self.extent
        end_command = ""

        step_size = math.pi/2
        if self.radius < 0: step_size = -step_size

        start_code = "G3"
        if self.radius < 0: start_code = "G2"

        # loops around the circle
        while extent > abs(step_size):
            angle += step_size
            angle %= math.tau
            new_pos = coords_at_dist(self.centre, angle, abs(self.radius))
            end_command += f"{start_code} {position_gcode(new_pos, info)} R{abs(self.radius)*info.scale:.3f}\n"
            extent -= abs(step_size)


        if self.radius > 0:
            # anticlockwise - G3
            angle += extent
        else:
            # clockwise - G2
            angle -= extent
        
        angle %= math.tau
        new_pos = coords_at_dist(self.centre, angle, abs(self.radius))
        end_command += f"{start_code} {position_gcode(new_pos, info)} R{abs(self.radius)*info.scale:.3f}"

        return end_command

    def _write_gcode_circle_centre(self, info: ScaleInfo) -> str:
        """Writes with end point and centre
        """
        # we can move in steps of up to 2pi radians
        angle = angle_between_points(self.centre, self.start)
        extent = self.extent
        current_pos = self.start
        end_command = ""

        centre_relative = f"I{(self.centre[0]-current_pos[0])*info.scale:.3f} J{(self.centre[1]-current_pos[1])*info.scale:.3f}"
        step_size = math.tau
        start_code = "G3"
        if self.radius < 0: start_code = "G2"

        # loops around the circle
        while extent > step_size:
            # write a new arc
            end_command += f"{start_code} {position_gcode(current_pos, info)} {centre_relative}\n"
            extent -= step_size

        # final arc
        if self.radius > 0:
            # anticlockwise
            end_pos = coords_at_dist(self.centre, angle+extent, abs(self.radius))
        else:
            # clockwise
            end_pos = coords_at_dist(self.centre, angle-extent, abs(self.radius))
        
        end_command += f"{start_code} {position_gcode(end_pos, info)} {centre_relative}"
        
        return end_command

    def write_gcode(self, info: ScaleInfo, circle_mode: str):
        if self.radius == 0: return ''
        if self.steps == None:
            # actual circle
            if circle_mode == 'radius':
                return self._write_gcode_circle_radius(info)
            else:
                return self._write_gcode_circle_centre(info)
        else:
            # step circle
            return self._write_gcode_steps(info)

class Turtle(turtle.Turtle):

    # Default turtle methods that we override to add in the tracking logic

    def __init__(self, shape: str = "classic", undobuffersize: int = 0, visible: bool = True) -> None:
        super().__init__(shape, undobuffersize=0, visible=visible)
        self._gcode_moves = []

    def reset(self):
        super().reset()
        self._gcode_moves = []

    def clear(self):
        super().reset()
        self._gcode_moves = []

    def _gcode_wraplinear(func):
        def decorator(self: turtle.Turtle, *args, **kwargs):
            start_pos = self.pos()
            func(self, *args, **kwargs)
            end_pos = self.pos()
            if self.isdown():
                self._gcode_moves.append(LinearMove(start_pos, end_pos))
        return decorator

    @_gcode_wraplinear
    def forward(self, distance: float) -> None:
        return super().forward(distance)

    @_gcode_wraplinear
    def back(self, distance: float) -> None:
        return super().back(distance)

    @_gcode_wraplinear
    def goto(self, x, y=None):
        return super().goto(x, y)

    @_gcode_wraplinear
    def setx(self, x: float) -> None:
        return super().setx(x)

    @_gcode_wraplinear
    def sety(self, y: float) -> None:
        return super().sety(y)

    @_gcode_wraplinear
    def home(self) -> None:
        return super().home()
    
    # This becomes a move with 0 length
    @_gcode_wraplinear
    def dot(self, size=None, *color):
        return super().dot(size, *color)


    def circle(self, radius: float, extent: float | None = None, steps: int | None = None) -> None:
        start_pos = self.pos()

        # straight right is pi/2, straight up is o
        x, y = self._orient
        current_heading = math.atan2(y, x)
        centre_angle = current_heading + math.pi/2
        # (radius<0 just moves backwards, so this works)
        centre_pos = coords_at_dist(start_pos, centre_angle, radius)

        ret = super().circle(radius, extent, steps)

        end_extent = math.tau
        if extent != None:
            end_extent = (abs(extent)/self._fullcircle)*math.tau

        self._gcode_moves.append(CircleMove(start=start_pos, end=self.pos(), centre=centre_pos, radius=radius, extent=end_extent, steps=steps))
        return ret

    fd = forward
    bk = back
    backward = back
    setpos = goto
    setposition = goto

    # Various methods that aren't implemented, we override them because they are inconvenient
    # we could probably get away not doing this, but I want to for some reason

    def undo(self):	raise NotImplementedError("Undo is not supported by G-Code turtle")
    undobufferentries = undo
    def setundobuffer(self, size):	raise NotImplementedError("Undo is not supported by G-Code turtle")

    # Custom G-Code methods and the like

    def write_gcode(self, width: float, height: float, x: float = 0, y: float = 0, allow_rotation: bool = False, circle_mode: str = 'centre', penup_command: str = None, pendown_command: str = None) -> str:
        """Write the current G-Code buffer to a string

        Keyword arguments:
         - `width` -- the width of the usable area of the plotter
         - `height` -- the height of the usable area of the plotter
         - `x` -- the x coordinate of the bottom left corner of the usable area of the plotter (default 0)
         - `y` -- the y coordinate of the bottom left corner of the usable area of the plotter (default 0)
         - `allow_rotation` -- if the drawing should be automatically rotated by 90deg if that will allow it to be drawn bigger in the supplied area (default False)
         - `circle_mode` -- either 'radius' or 'centre', which circle drawing method the G-Code should use (default 'centre')
          - `penup_command` -- the G-Code command to send the the plotter to move the pen up, by default no command is sent and the pen is assumed to always be down
          - `pendown_command` -- the G-Code command to send the the plotter to move the pen down, by default no command is sent and the pen is assumed to always be down
        """
        width = float(width)
        if width <= 0: raise ValueError("Cannot write to a G-Code area with a negative or zero width")
        
        height = float(height)
        if height <= 0: raise ValueError("Cannot write to a G-Code area with a negative or zero height")
        
        x = float(x)
        y = float(y)
        allow_rotation = bool(allow_rotation)
        
        circle_mode = str(circle_mode).lower().strip()
        if circle_mode == 'centre':
            circle_mode = 'centre'
        if circle_mode != 'centre' and circle_mode != 'radius':
            raise ValueError("Unknown circle mode: must be 'centre' or 'radius")
        
        if penup_command != None:
            penup_command = penup_command.strip()
        if pendown_command != None:
            pendown_command = pendown_command.strip()

        if len(self._gcode_moves) == 0:
            return ''

        # print(self._gcode_moves)

        extents = self._gcode_moves[0].extents()
        top = extents.top
        bottom = extents.bottom
        left = extents.left
        right = extents.right

        for move in self._gcode_moves:
            extent = move.extents()
            if extent.top > top: top = extent.top
            if extent.bottom < bottom: bottom = extent.bottom
            if extent.left < left: left = extent.left
            if extent.right > right: right = extent.right

        turtle_width = right - left
        turtle_height = top - bottom

        do_rotation = False
        scale_width = width/turtle_width
        scale_height = height/turtle_height
        if ((turtle_width > turtle_height) != (width > height)) and allow_rotation:
            # should be rotated 90 degrees
            do_rotation = True
            scale_width = width/turtle_height
            scale_height = height/turtle_width

        scale_factor = min(scale_width, scale_height)

        offset_x = x - left*scale_factor
        offset_y = y - bottom*scale_factor
        if do_rotation:
            offset_x = x - bottom*scale_factor
            offset_y = y - left*scale_factor
        
        offset = (offset_x, offset_y)

        info = ScaleInfo(scale=scale_factor, do_rotation=do_rotation, offset=offset, top=top, bottom=bottom)

        gcode_str = f"G0 {position_gcode(self._gcode_moves[0].start, info)}\n"

        last_position = self._gcode_moves[0].start

        for move in self._gcode_moves:
            if move.start != last_position:
                # emit a penup move
                if penup_command != None:
                    gcode_str += penup_command + "\n"
                
                # move to correct place
                gcode_str += f"G0 {position_gcode(move.start, info)}\n"

                # emit a pendown move
                if pendown_command != None:
                    gcode_str += pendown_command + "\n"
            
            # write the actual move
            gcode_str += move.write_gcode(info, circle_mode) + "\n"
            last_position = move.end

        gcode_str = gcode_str.removesuffix("\n")


        return gcode_str

    def clear_gcode(self):
        """Clear the current list of G-Code moves"""
        self._gcode_moves = []

# exporting and the like


# taken from the main turtle library, it needs to be reproduced here so we reference the correct globals() and Turtle class
# 
# Copyright (C) 2006 - 2010  Gregor Lingl
# email: glingl@aon.at
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
def _make_global_funcs(functions, cls, obj, init, docrevise):
    for methodname in functions:
        method = getattr(cls, methodname)
        pl1, pl2 = turtle.getmethparlist(method)
        if pl1 == "":
            print(">>>>>>", pl1, pl2)
            continue
        defstr = turtle.__func_body.format(obj=obj, init=init, name=methodname,
                                    paramslist=pl1, argslist=pl2)
        exec(defstr, globals())
        globals()[methodname].__doc__ = docrevise(method.__doc__)


# _tg_classes (this is stupid but I don't care)
ScrolledCanvas = turtle.ScrolledCanvas
TurtleScreen = turtle.TurtleScreen
Screen = turtle.Screen
RawTurtle =turtle.RawTurtle
RawPen = turtle.RawPen
Pen = turtle.Pen
Shape = turtle.Shape
Vec2D = turtle.Vec2D
# _tg_screen_functions
_make_global_funcs(turtle._tg_screen_functions, turtle._Screen,
                   'Turtle._screen', 'Screen()', turtle._screen_docrevise)
# _tg_turtle_functions
_make_global_funcs(turtle._tg_turtle_functions + ["write_gcode"], Turtle,
                   'Turtle._pen', 'Turtle()', turtle._turtle_docrevise)

# _tg_utilities
write_docstringdict = turtle.write_docstringdict
done = turtle.done
# "Terminator"
Terminator = turtle.Terminator

__all__ = turtle.__all__

doc = """Turtle G-Code

A small library for converting python turtle commands into
G-Code for use with a pen-plotter.

Simply import this library instead of the default turtle one
and then add a call to turtle.write_gcode() at the end to
get the G-Code of the shapes you have drawn.


Things this library doesn't support:
 - Stamps
 - Writing Text
 - Different colours/thicknesses of pen
 - Undoing actions (undo functions throw an error if called)

Have fun :)
"""

if __name__ == "__main__":
    print(doc)