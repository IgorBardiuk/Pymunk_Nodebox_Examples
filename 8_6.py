#encoding: utf-8
from __future__ import division
from nodebox.graphics import *
import pymunk
import pymunk.pyglet_util
import random, math
import numpy as np

space = pymunk.Space()

def createBody(x, y, shape, *shapeArgs):
    body = pymunk.Body()
    body.position = x, y
    s = shape(body, *shapeArgs)
    s.mass = 1
    s.friction = 1
    space.add(body, s)
    return s  # повертає форму тіла

s0 = createBody(300, 300, pymunk.Poly, ((-20, -5), (-20, 5), (20, 15), (20, -15)))
s0.score = 0
s3 = createBody(200, 300, pymunk.Poly, ((-20, -5), (-20, 5), (20, 15), (20, -15)))
s3.color = (0, 255, 0, 255)
s3.score = 0
s3.body.Q = [[0, 0], [0, 0], [0, 0], [0, 0]]  # Додано новий стан для state=3
s3.body.action = 0  # 0 - залишати, 1 - змінювати напрямок
s1 = createBody(300, 200, pymunk.Circle, 10, (0, 0))
S2 = []
for i in range(1):
    s2 = createBody(350, 250, pymunk.Circle, 10, (0, 0))
    s2.color = (255, 0, 0, 255)
    S2.append(s2)

def getAngle(x, y, x1, y1):
    return math.atan2(y1 - y, x1 - x)

def getDist(x, y, x1, y1):
    return ((x - x1)**2 + (y - y1)**2)**0.5

def inCircle(x, y, cx, cy, R):
    return (x - cx)**2 + (y - cy)**2 < R**2

def inSector(x, y, cx, cy, R, a):
    angle = getAngle(cx, cy, x, y)
    a = a % (2 * math.pi)
    angle = angle % (2 * math.pi)
    return inCircle(x, y, cx, cy, R) and (a - 0.5 < angle < a + 0.5)

def strategy2(b=s3.body):
    """Оновлена стратегія робота з використанням Q-learning та новим станом."""
    v = 100
    a = b.angle
    b.velocity = v * math.cos(a), v * math.sin(a)
    x, y = b.position
    R = getDist(x, y, 350, 250)
    ellipse(x, y, 200, 200, stroke=Color(0.5))
    line(x, y, x + 100 * math.cos(a + 0.5), y + 100 * math.sin(a + 0.5), stroke=Color(0.5))
    line(x, y, x + 100 * math.cos(a - 0.5), y + 100 * math.sin(a - 0.5), stroke=Color(0.5))

    if canvas.frame % 10 == 0:  # кожні n кадрів
        inS = inSector(s1.body.position[0], s1.body.position[1], x, y, 100, a)
        inS2 = inSector(S2[0].body.position[0], S2[0].body.position[1], x, y, 100, a)

        # Установлюємо стан і винагороду
        if inS:
            state = 1
            reward = 1 if b.action == 0 else -1
        elif inS2:
            state = 2
            reward = -1 if b.action == 0 else 1
        else:
            # Новий стан, коли немає об'єктів у полі зору
            state = 3
            reward = -0.5  # Негативна винагорода для заохочення дослідження

        # Оновлення Q-таблиці
        b.Q[state][b.action] += reward
        print("State: {}, Action: {}, Q-Values: {}".format(state, b.action, b.Q))

        # Вибір дії
        act = b.Q[state][b.action]
        if random.random() < abs(1.0 / (act + 0.1)):  # випадкова дія з ймовірністю, залежною від Q-значення
            b.action = random.choice([0, 1])  # випадкова дія
        else:
            b.action = np.argmax(b.Q[state])  # оптимальна дія

        # Виконання дії
        if b.action:  # Якщо обрана дія — змінити напрямок
            if state == 3:
                b.angle += random.uniform(-0.5, 0.5)  # Невелика випадкова зміна кута для дослідження
            else:
                b.angle = 2 * math.pi * random.random()

        # Запобігання виїзду за межі кола
        if R > 180:
            b.angle = getAngle(x, y, 350, 250)

def scr(s, s0, s3, p=1):
    bx, by = s.body.position
    s0x, s0y = s0.body.position
    s3x, s3y = s3.body.position
    if not inCircle(bx, by, 350, 250, 180):
        if getDist(bx, by, s0x, s0y) < getDist(bx, by, s3x, s3y):
            s0.score = s0.score + p
        else:
            s3.score = s3.score + p
        s.body.position = random.randint(200, 400), random.randint(200, 300)

def score():
    """визначає переможця"""
    scr(s1, s0, s3)
    for s in S2:
        scr(s, s0, s3, p=-1)

def manualControl():
    """Керування роботом з мишки або клавіатури"""
    v = 10  # швидкість
    b = s0.body
    a = b.angle
    x, y = b.position
    vx, vy = b.velocity
    if canvas.keys.char == "a":
        b.angle -= 0.1
    if canvas.keys.char == "d":
        b.angle += 0.1
    if canvas.keys.char == "w":
        b.velocity = vx + v * math.cos(a), vy + v * math.sin(a)
    if canvas.mouse.button == LEFT:
        b.angle = getAngle(x, y, *canvas.mouse.xy)
        b.velocity = vx + v * math.cos(a), vy + v * math.sin(a)

def simFriction():
    for s in [s0, s1, s3] + S2:
        s.body.velocity = s.body.velocity[0] * 0.9, s.body.velocity[1] * 0.9
        s.body.angular_velocity = s.body.angular_velocity * 0.9

draw_options = pymunk.pyglet_util.DrawOptions()

def draw(canvas):
    canvas.clear()
    fill(0, 0, 0, 1)
    text("%i %i" % (s0.score, s3.score), 20, 20)
    nofill()
    ellipse(350, 250, 350, 350, stroke=Color(0))
    manualControl()
    strategy2()
    score()
    simFriction()
    space.step(0.02)
    space.debug_draw(draw_options)

canvas.size = 700, 500
canvas.run(draw)

