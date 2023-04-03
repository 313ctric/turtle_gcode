import turtle
import turtle_gcode as turtle


def A():
	turtle.pendown()
	turtle.goto(turtle.xcor() + 15, turtle.ycor()+50)
	turtle.goto(turtle.xcor() + 15, turtle.ycor()-50)
	turtle.penup()

	turtle.back(30)
	x = turtle.xcor()
	y = turtle.ycor()
	turtle.goto(x + 15/2, y+50/2)
	turtle.pendown()
	turtle.goto((x + 30 - 15/2, y+50/2))
	turtle.penup()
	turtle.goto(x, y)

	turtle.forward(40)

def M():
	turtle.pendown()

	turtle.left(90)
	turtle.forward(50)
	turtle.right(150)
	turtle.forward(30)
	turtle.left(120)
	turtle.forward(30)
	turtle.right(150)
	turtle.forward(50)

	turtle.left(90)
	turtle.penup()
	turtle.forward(10)

def T(): # width : 30
	turtle.forward(20)
	turtle.pendown()
	turtle.left(90)
	turtle.forward(50)
	turtle.left(90)
	turtle.forward(15)
	turtle.back(30)
	turtle.forward(15)
	turtle.right(90)
	turtle.back(50)
	turtle.right(90)
	turtle.penup()
	turtle.forward(30)

def U(): # width : 30
	turtle.left(90)
	turtle.forward(50)
	turtle.left(180)

	turtle.pendown()
	turtle.forward(35)
	turtle.circle(15, extent=180)
	turtle.forward(35)
	turtle.penup()
	
	turtle.back(50)
	turtle.right(90)
	turtle.forward(10)

def R(): # width : 30
	turtle.pendown()
	turtle.left(90)
	turtle.forward(50)
	turtle.right(90)
	turtle.circle(-15, extent=180)
	turtle.right(180)

	turtle.goto(turtle.xcor() + 20, turtle.ycor()-20)
	turtle.penup()
	turtle.forward(10)

def L(): # width : 30
	turtle.left(90)
	turtle.pendown()
	turtle.forward(50)
	turtle.back(50)
	turtle.right(90)
	turtle.forward(30)
	turtle.penup()
	turtle.forward(10)

def E(): # width : 30
	turtle.pendown()
	turtle.left(90)
	turtle.forward(50)
	turtle.right(90)
	
	turtle.forward(30)
	turtle.back(30)
	
	turtle.right(90)
	turtle.forward(25)
	turtle.left(90)

	turtle.forward(15)
	turtle.back(15)

	turtle.right(90)
	turtle.forward(25)
	turtle.left(90)

	turtle.forward(30)
	turtle.penup()
	turtle.forward(10)

def _(): # width : 30
	turtle.pendown()
	turtle.forward(30)
	turtle.penup()
	turtle.forward(10)

def G(): # width : 30
	turtle.forward(15)
	turtle.pendown()
	turtle.circle(15, extent=90)

	turtle.forward(5)
	turtle.left(90)
	turtle.forward(10)
	turtle.back(10)
	turtle.right(90)
	turtle.penup()
	turtle.forward(15)
	turtle.pendown()

	turtle.circle(15, extent=180)
	turtle.forward(20)
	turtle.circle(15, extent=90)
	turtle.penup()

	turtle.forward(15)
	turtle.forward(10)
def C(): # width : 30
	turtle.forward(15)
	turtle.pendown()
	turtle.circle(15, extent=90)

	turtle.penup()
	turtle.forward(20)
	turtle.pendown()

	turtle.circle(15, extent=180)
	turtle.forward(20)
	turtle.circle(15, extent=90)
	turtle.penup()

	turtle.forward(15)
	turtle.forward(10)
def O(): # width : 30
	turtle.forward(15)
	turtle.pendown()
	turtle.circle(15, extent=90)
	turtle.forward(20)
	turtle.circle(15, extent=180)
	turtle.forward(20)
	turtle.circle(15, extent=90)
	turtle.penup()

	turtle.forward(15)
	turtle.forward(10)
def D(): # width : 30 (actually 25)
	turtle.pendown()
	turtle.left(90)
	turtle.forward(50)
	turtle.right(90)

	turtle.circle(-25, extent=180)
	turtle.penup()

	turtle.right(180)

	turtle.forward(40)


# M()
# A()

turtle.speed(0)
turtle.penup()
turtle.back(470/2)

T()
U()
R()
T()
L()
E()
_()
G()
C()
O()
D()
E()

turtle.exitonclick()

print(turtle.write_gcode(470, 50, allow_rotation=True, circle_mode='centre'))