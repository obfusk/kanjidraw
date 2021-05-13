#!/usr/bin/python3
# encoding: utf-8

# --                                                            ; {{{1
#
# File        : kanjidraw/lib.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2021-05-13
#
# Copyright   : Copyright (C) 2021  Felix C. Stegerman
# Version     : v0.2.0
# License     : AGPLv3+
#
# --                                                            ; }}}1

                                                                # {{{1
r"""

Handwritten kanji recognition: library.

>>> strokes = [[125.5875, 28.6875, 48.45, 196.35], [104.55, 93.7125, 195.7125, 223.125]]
>>> for s, k in matches(strokes): print(int(s), k)
99 人
96 九
96 乂
93 八
93 入
90 儿
89 勹
88 乃
87 又
87 几
87 冂
85 匕
82 亻
81 卜
78 亠
75 冖

>>> strokes = [[17.85, 102.0, 83.5125, 51.0], [45.9, 26.775, 49.0875, 210.375], [33.7875, 152.3625, 61.8375, 133.875], [103.9125, 54.825, 211.0125, 58.65], [139.6125, 31.2375, 142.8, 64.3875], [178.5, 42.075, 179.1375, 66.3], [108.375, 121.125, 106.4625, 182.325], [113.475, 114.1125, 205.275, 189.975], [163.2, 116.025, 164.475, 181.05], [126.225, 148.5375, 198.2625, 158.7375], [109.0125, 200.8125, 205.9125, 191.25]]
>>> for s, k in matches(strokes): print(int(s), k)
91 描
89 猫
86 桷
85 淌
84 猟
83 掩
83 培
82 猛
82 控
82 清
82 捨
81 陪
81 措
81 袷
81 掠
81 淹
80 桶
80 掘
80 舳
80 猪
80 掃
79 情
79 捺
79 陷
79 探

"""                                                             # }}}1

import gzip, functools, itertools, json, os, re, sys
import xml.etree.ElementTree as ET

from collections import namedtuple
from enum import Enum

__version__ = "0.2.0"

DATAFILE = os.path.join(os.path.dirname(__file__), "data.json")

ARGS_RX = re.compile(r"(-?(?:\d*\.)?\d+)[\s,]*")
PATH_RX = re.compile(r"([MZCS])\s*((?:(?:-?(?:\d*\.)?\d+)[\s,]*)*)", re.I)

DIRECTION_THRESHOLD     = 51
DIAGONAL_THRESHOLD      = 77

STROKE_DIRECTION_WEIGHT = 1.0
MOVE_DIRECTION_WEIGHT   = 0.8
STROKE_LOCATION_WEIGHT  = 0.6
CLOSE_WEIGHT            = 0.7

MAX_RESULTS             = 25
CUTOFF                  = 0.75

SEDM = namedtuple("SEDM", "starts ends dirs moves".split())

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
    return cls.of_line(tuple(l1[2:] + l2[:2]), threshold)

  def isclose(a, b):
    return (a == a.X or b == a.X or a == b) or \
           (a.value == ((b.value+1)%8) or ((a.value+1)%8) == b.value)
                                                                # }}}1

@functools.total_ordering
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
    return abs(a.value[0] - b.value[0]) <= 1 and \
           abs(a.value[1] - b.value[1]) <= 1

  def __lt__(a, b):
    return a.value < b.value

  def __eq__(a, b):
    return a.value == b.value
                                                                # }}}1

def strict_match(a, b):                                         # {{{1
  """Strict comparison; returns a percentage score as a float."""
  if len(a) != len(b): raise ValueError("must have same length")
  dal_a = _directions_and_locations(a)
  dal_b = _directions_and_locations(b)
  score, l = 0.0, len(a)
  for i in range(l):
    if dal_a.dirs[i] == dal_b.dirs[i]:
      score += STROKE_DIRECTION_WEIGHT
    elif dal_a.dirs[i].isclose(dal_b.dirs[i]):
      score += STROKE_DIRECTION_WEIGHT * CLOSE_WEIGHT
    if i > 0:
      if dal_a.moves[i-1] == dal_b.moves[i-1]:
        score += MOVE_DIRECTION_WEIGHT
      elif dal_a.moves[i-1].isclose(dal_b.moves[i-1]):
        score += MOVE_DIRECTION_WEIGHT * CLOSE_WEIGHT
    if dal_a.starts[i] == dal_b.starts[i]:
      score += STROKE_LOCATION_WEIGHT
    elif dal_a.starts[i].isclose(dal_b.starts[i]):
      score += STROKE_LOCATION_WEIGHT * CLOSE_WEIGHT
    if dal_a.ends[i] == dal_b.ends[i]:
      score += STROKE_LOCATION_WEIGHT
    elif dal_a.ends[i].isclose(dal_b.ends[i]):
      score += STROKE_LOCATION_WEIGHT * CLOSE_WEIGHT
  m = l * (STROKE_DIRECTION_WEIGHT + 2 * STROKE_LOCATION_WEIGHT) \
    + (l-1) * MOVE_DIRECTION_WEIGHT
  return 100 * score / m
                                                                # }}}1

def fuzzy_match(a, b):
  """Fuzzy comparison; ignores order and direction of strokes."""
  if len(a) != len(b): raise ValueError("must have same length")
  return strict_match(_fuzzy_sort(a), _fuzzy_sort(b))

def match_offby1(match):
  """Comparison ± 1 stroke."""
  def f (a, b):
    if abs(len(a) - len(b)) != 1: raise ValueError("length difference must be 1")
    if len(a) > len(b): a, b = b, a
    return max( match(a, b[:i] + b[i+1:]) for i in range(len(b)) )
  return f

def _fuzzy_sort(lines):                                         # {{{1
  result = []
  for line in lines:
    start_p, end_p = line[:2], line[2:]
    start_l, end_l = Location.of_point(*start_p), Location.of_point(*end_p)
    if start_l > end_l:
      start_p, end_p = end_p, start_p
      start_l, end_l = end_l, start_l
    result.append((start_l, end_l, start_p + end_p))
  return tuple( x[2] for x in sorted(result) )
                                                                # }}}1

def _directions_and_locations(lines):
  return SEDM(
    tuple( Location.of_point(*l[:2]) for l in lines ),
    tuple( Location.of_point(*l[2:]) for l in lines ),
    tuple(map(Direction.of_line, lines)),
    tuple(map(Direction.of_move, lines[1:], lines[:-1]))
  )

def matches(lines, data = None, fuzzy = False, offby1 = False,
            max_results = MAX_RESULTS, cutoff = CUTOFF):
  """
  Find best matches; yields a (score, kanji) pair for the first
  max_results matches that have a score >= max_score * cutoff.
  """
  match = fuzzy_match if fuzzy else strict_match
  data_items = _data_items_offby1 if offby1 else _data_items
  if offby1: match = match_offby1(match)
  return _matches(lines, data, max_results, cutoff, match, data_items)

def strict_matches(*a, **kw):
  """Find strict matches."""
  return matches(*a, **kw)

def fuzzy_matches(*a, **kw):
  """Find fuzzy matches."""
  return matches(*a, fuzzy = True, **kw)

def strict_matches_offby1(*a, **kw):
  """Find strict matches ِِ± 1 stroke."""
  return matches(*a, offby1 = True, **kw)

def fuzzy_matches_offby1(*a, **kw):
  """Find fuzzy matches ِِ± 1 stroke."""
  return matches(*a, fuzzy = True, offby1 = True, **kw)

def _data_items(lines, data):
  return data[len(lines)].items()

def _data_items_offby1(lines, data):
  for n in [len(lines)-1, len(lines)+1]:
    if n in data: yield from data[n].items()

def _matches(lines, data, max_results, cutoff, match, data_items):
  it = data_items(lines, data or kanji_data())
  ms = sorted(( (match(lines, l), k) for k, l in it ), reverse = True)
  mm = ms[0][0] * cutoff
  return itertools.takewhile(lambda m: m[0] >= mm, ms[:max_results])

def kanji_data():
  if kanji_data._data is None: kanji_data._data = _load_json()
  return kanji_data._data
kanji_data._data = None

# FIXME: better kanji unicode ranges?
def _parse_kanjivg(file):                                       # {{{1
  data = {}
  with gzip.open(file) as f:
    for e in ET.parse(f).getroot():
      if e.tag != "kanji": continue
      code  = int(e.get("id").replace("kvg:kanji_", ""), 16)
      char  = chr(code)
      paths = tuple( _path_to_line(p.get("d")) for p in e.findall(".//path") )
      if not (0x4e00 <= code <= 0x9fff): continue
      kanji = data.setdefault(len(paths), {})
      assert char not in kanji
      kanji[char] = paths
  return data
                                                                # }}}1

# https://www.w3.org/TR/SVG/paths.html
def _path_to_line(path):                                        # {{{1
  assert path[0] in "Mm"
  last = 0
  for i, m in enumerate(PATH_RX.finditer(path)):
    assert m.start() == last
    last = m.end()
    cmd, args = m.group(1), tuple(map(float, ARGS_RX.findall(m.group(2))))
    if cmd in "Mm":   # moveto
      assert i == 0
      x1, y1 = x2, y2 = args
    elif cmd in "Zz": # closepath
      assert len(args) == 0
      assert last == len(path)
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
  assert last == len(path)
  assert all( 0 <= v < 109 for v in [x1, y1, x2, y2] )
  return tuple( int(v * 255 / 109) for v in [x1, y1, x2, y2] )
                                                                # }}}1

def _load_json(file = DATAFILE):
  """Load data from JSON file."""
  with open(file) as fh:
    return { int(k): v for k, v in json.load(fh).items() }

def _save_json(file, data):
  """Save data to JSON file."""
  with open(file, "w") as fh:
    json.dump(data, fh, sort_keys = True)

if __name__ == "__main__":
  if "--doctest" in sys.argv:
    verbose = "--verbose" in sys.argv
    import doctest
    if doctest.testmod(verbose = verbose)[0]: sys.exit(1)

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
