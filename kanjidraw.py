#!/usr/bin/python3
# encoding: utf-8

# --                                                            ; {{{1
#
# File        : kanjidraw.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2021-05-09
#
# Copyright   : Copyright (C) 2021  Felix C. Stegerman
# Version     : v0.0.1
# License     : AGPLv3+
#
# --                                                            ; }}}1

                                                                # {{{1
r"""

...

"""                                                             # }}}1

import gzip, re
import xml.etree.ElementTree as ET

from collections import namedtuple
from enum import Enum

ARGS_RX = re.compile(r"(-?(?:\d*\.)?\d+)[\s,]*")
PATH_RX = re.compile(r"([MZCS])\s*((?:(?:-?(?:\d*\.)?\d+)[\s,]*)*)", re.I)

DIRECTION_THRESHOLD = 51
DIAGONAL_THRESHOLD  = 77

Line = namedtuple("Line", "x1 y1 x2 y2".split())

DirAndLoc = namedtuple("DirAndLoc", "starts ends dirs moves".split())

class Direction(Enum):                                          # {{{1
  X, N, NE, E, SE, S, SW, W, NW = range(-1, 8)

  @classmethod
  def of_line(cls, l, threshold = DIRECTION_THRESHOLD):
    x1, y1, x2, y2 = l
    dx, dy = x2 - x1, y2 - y1
    adx, ady = abs(dx), abs(dy)
    if adx < threshold and ady < threshold:
      return cls.X
    if adx > ady:
      diag = ady > DIAGONAL_THRESHOLD * adx // 256
      if dx > 0:
        return (cls.NE if dy < 0 else cls.SE) if diag else cls.E
      else:
        return (cls.NW if dy < 0 else cls.SW) if diag else cls.W
    else:
      diag = adx > DIAGONAL_THRESHOLD * ady // 256
      if dy > 0:
        return (cls.SW if dx < 0 else cls.SE) if diag else cls.S
      else:
        return (cls.NW if dx < 0 else cls.NE) if diag else cls.N

  @classmethod
  def of_move(cls, l1, l2, threshold = DIRECTION_THRESHOLD):
    return cls.of_line(Line(*(l1[2:] + l2[:2])), threshold)

  def isclose(a, b):
    return (a == cls.X or b == cls.X or a == b) or \
           (a == ((b+1)%8) or ((a+1)%8) == b)
                                                                # }}}1

class Location(Enum):                                           # {{{1
  N   = (1, 0)
  NE  = (2, 0)
  E   = (2, 1)
  SE  = (2, 2)
  S   = (1, 2)
  SW  = (0, 2)
  W   = (0, 1)
  NW  = (0, 0)
  MID = (1, 1)

  @classmethod
  def of_point(cls, x, y):
    if x < 85:
      return cls.NW if y < 85 else (cls.W if y < 170 else cls.SW)
    elif x < 170:
      return cls.N if y < 85 else (cls.MID if y < 170 else cls.S)
    else:
      return cls.NE if y < 85 else (cls.E if y < 170 else cls.SE)

  def isclose(a, b):
    return abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1
                                                                # }}}1

# ... TODO ...

# FIXME: better error messages
def compare_strict(a, b):                                       # {{{1
  if len(a) != len(b):
    raise ValueError("must have same length")                 #  FIXME
  ...
                                                                # }}}1

def _directions_and_locations(lines):
  return DirAndLoc(
    tuple( Location.of_point(*l[:2]) for l in lines ),
    tuple( Location.of_point(*l[2:]) for l in lines ),
    tuple(map(Direction.of_line, lines)),
    tuple(map(Direction.of_move, lines[1:], lines[:-1]))
  )

def parse_kanjivg(file):                                        # {{{1
  data = {}
  with gzip.open(file) as f:
    for e in ET.parse(f).getroot():
      if e.tag != "kanji": continue
      code  = int(e.get("id").replace("kvg:kanji_", ""), 16)
      char  = chr(code)
      paths = tuple( _path_to_line(p.get("d")) for p in e.findall(".//path") )
      if not (0x4e00 <= code <= 0x9fff): continue             #  FIXME
      assert char not in data
      data[char] = paths
  return data
                                                                # }}}1

# FIXME: handle errors; normalise?
# https://www.w3.org/TR/SVG/paths.html
def _path_to_line(path):                                        # {{{1
  assert path[0] in "Mm"                                      #  FIXME
  for i, m in enumerate(PATH_RX.finditer(path)):
    cmd, args = m.group(1), tuple(map(float, ARGS_RX.findall(m.group(2))))
    if cmd in "Mm":   # moveto
      assert i == 0
      x1, y1 = x2, y2 = args
    elif cmd in "Zz": # closepath
      assert len(args) == 0
      x2, y2 = x1, y1
    elif cmd in "Cc": # curveto
      while args:
        _x1, _y1, _x2, _y2, x, y, *args = args
        x2, y2 = (x, y) if cmd.isupper() else (x2 + x, y2 + y)
    elif cmd in "Ss": # shorthand/smooth curveto
      _x2, _y2, x, y = args
      x2, y2 = (x, y) if cmd.isupper() else (x2 + x, y2 + y)
    else:
      assert False
  assert all( 0 <= v < 109 for v in [x1, y1, x2, y2] )
  return Line(*( int(v * 255 / 109) for v in [x1, y1, x2, y2] ))
                                                                # }}}1

if __name__ == "__main__":
  if "--doctest" in sys.argv:
    verbose = "--verbose" in sys.argv
    import doctest
    if doctest.testmod(verbose = verbose)[0]: sys.exit(1)

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
