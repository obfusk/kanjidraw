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

ARGS_RX = re.compile(r"(-?(?:\d*\.)?\d+)[\s,]*")
PATH_RX = re.compile(r"([MZCS])\s*((?:(?:-?(?:\d*\.)?\d+)[\s,]*)*)", re.I)

Line = namedtuple("Line", "x1 y1 x2 y2".split())

# ... TODO ...

def parse_kanjivg(file):                                        # {{{1
  data = {}
  with gzip.open(file) as f:
    for e in ET.parse(f).getroot():
      if e.tag != "kanji": continue
      code  = int(e.get("id").replace("kvg:kanji_", ""), 16)
      char  = chr(code)
      paths = tuple( _path_to_line(p.get("d"))
                     for p in e.findall(".//path") )
      if not (0x4e00 <= code <= 0x9fff): continue             #  FIXME
      assert char not in data
      data[char] = paths
  return data
                                                                # }}}1

# FIXME: handle errors
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
  return Line(x1, y1, x2, y2)
                                                                # }}}1

if __name__ == "__main__":
  if "--doctest" in sys.argv:
    verbose = "--verbose" in sys.argv
    import doctest
    if doctest.testmod(verbose = verbose)[0]: sys.exit(1)

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
