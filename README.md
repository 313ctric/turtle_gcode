# Turtle G-Code

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

## Basic Use

The module is designed to be pretty much a drop in replacement for the normal
turtle library.

If (for example) you had this python code
```python
import turtle

turtle.pendown()
turtle.forward(50)
turtle.circle(20)
```

you could convert it into G-Code by changing it to

```python
import turtle_gcode as turtle

turtle.pendown()
turtle.forward(50)
turtle.circle(20)

turtle.write_gcode(100, 100)
```

## More options

The turtle stores an internal buffer of all the moves made that would write to the output.
They can then be output to a string.

There are two functions defined
```python
write_gcode()
```
Writes the current move buffer as G-Code to the output. The drawing is automatically scaled
to be as large as possible within the specified bounds. If `allow_rotation` is `True` then the
drawing may also be rotated if that would allow it to be larger.

All parameters:
- `width` -- the width of the usable area of the plotter
- `height` -- the height of the usable area of the plotter
- `x` -- the x coordinate of the bottom left corner of the usable area of the plotter (default 0)
- `y` -- the y coordinate of the bottom left corner of the usable area of the plotter (default 0)
- `allow_rotation` -- if the drawing should be automatically rotated by 90deg if that will allow it to be drawn bigger in the supplied area (default False)
- `circle_mode` -- either 'radius' or 'centre', which circle drawing method the G-Code should use (default 'centre')
- `penup_command` -- the G-Code command to send the the plotter to move the pen up, by default no command is sent and the pen is assumed to always be down
- `pendown_command` -- the G-Code command to send the the plotter to move the pen down, by default no command is sent and the pen is assumed to always be down

```python
clear_gcode()
```
Clears all the moves from the G-Code buffer.

## License

Like the original turtle code this is under a zlib license.

A small part of the original turtle code is used, again under the original zlib license.

