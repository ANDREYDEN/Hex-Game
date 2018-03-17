"""Mechanics of the game"""

from math import sqrt, hypot
from collections import deque, namedtuple

import consts

Point = namedtuple('Point', 'x y')

def point(*args: 'tuple or pair of args') -> namedtuple('Point', 'x y'):
    """Make an int named pair (Point) if the args are float but close to int"""
    halfInt = lambda n: int(n) if abs(int(n)-n) < consts.EPS else n
    if len(args) == 1:
        x, y = args[0]
    else:
        x, y = args
    return Point(halfInt(x), halfInt(y))

def dist(p_A: point, p_B: point):
    return hypot(p_A.x-p_B.x, p_A.y-p_B.y)

def triangleS(p_A: point, p_B: point, p_C: point):
    """retrun the surface of a triangle"""
    a = dist(p_C, p_B)
    b = dist(p_A, p_C)
    c = dist(p_A, p_B)
    p = (a+b+c)/2
    return sqrt(p*(p-a)*(p-b)*(p-c))

def inHex(pos: (int, int), x, y, a):
    """checks if a point is in a hexagon with the side a"""
    pos = point(pos)
    points = [(x+a, y), (x+a/2, y+a*sqrt(3)/2),
              (x-a/2, y+a*sqrt(3)/2), (x-a, y),
              (x-a/2, y-a*sqrt(3)/2), (x+a/2, y-a*sqrt(3)/2)]
    points = list(map(point, points))
    sum_s = 0
    for i in range(-1, 5):
        sum_s += triangleS(points[i], points[i+1], pos)
    S = a*a*3*sqrt(3)/2
    return abs(S-sum_s) < consts.EPS

def inRect(pos: (int, int), x, y, w, h):
    """checks if a point is in a rectangle"""
    return (pos.x > x and pos.x < x + w and\
           pos.y > y and pos.y < y + h)

def inBounds(v: point, w, h):
    return (v.x >= 0 and v.x < h and\
            v.y >= 0 and v.y < w)

def DFS(start: (int, int), grid: [[int]],
        exit_: 'function', player: int) -> bool:
    """Launches Depth First Search algorithm on grid beginning at start.
    Ends if exit_(cur) returns True.  Traverses only between players points.
    """
    w = len(grid[0])
    h = len(grid)
    Q = deque()
    Q.append(point(start))
    used = [[False for _ in range(w)] for __ in range(h)]
    MOVES = list(map(point, [(1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0)]))
    while len(Q):
        cur = Q[-1]
        if exit_(cur):
            return True
        used[cur.x][cur.y] = True
        flag = False
        for m in MOVES:
            other = Point(cur.x + m.x, cur.y + m.y)
            if (inBounds(other, w, h) and not used[other.x][other.y])\
                and grid[other.x][other.y] == player:
                Q.append(other)
                flag = True
                break
        if not flag:
            Q.pop()
    return False
