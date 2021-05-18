#!/usr/bin/python3
# encoding: utf-8

# --                                                            ; {{{1
#
# File        : kanjidraw/gui.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2021-05-18
#
# Copyright   : Copyright (C) 2021  Felix C. Stegerman
# Version     : v0.2.1
# License     : AGPLv3+
#
# --                                                            ; }}}1

                                                                # {{{1
r"""

Handwritten kanji recognition: tkinter GUI.

"""                                                             # }}}1

import os, sys

import tkinter as tk
import tkinter.font

from .lib import kanji_data, matches

NAME, TITLE = "kanjidraw", "Kanji Draw"
HEIGHT = WIDTH = 400
BACKGROUND, GRIDCOLOUR = "#ccc", "#aaa"
COLS, LINEWIDTH, FONTSIZE = 5, 5, 35
FONTS = ("Noto Sans CJK JP", "Noto Sans CJK SC", "Noto Sans CJK TC",
         "IPAexGothic", "IPAGothic")

def gui():                                                      # {{{1
  """Tkinter GUI."""

  nogrid = os.environ.get("KANJIDRAW_NOGRID") in ("1", "true", "yes")
  gridcolour = BACKGROUND if nogrid else GRIDCOLOUR

  win = tk.Tk()
  win.title(TITLE)
  win.columnconfigure(0, weight = 1)
  win.rowconfigure(0, weight = 1)

  fonts = set(tkinter.font.families())
  kanji_font = tk.font.Font(size = FONTSIZE)

  for f in FONTS:
    if f in fonts:
      kanji_font = tk.font.Font(family = f, size = FONTSIZE)
      break

  max_strokes = max(kanji_data().keys())
  drawing, x, y, strokes, lines = False, 0, 0, [], []

  def on_mousedown(event):
    nonlocal drawing, x, y
    if len(strokes) < max_strokes:
      drawing, x, y = True, event.x, event.y
      strokes.append([x * 255.0 / WIDTH, y * 255.0 / HEIGHT])
      lines.append([])
      enable_buttons()

  def on_mousemove(event):
    if drawing: draw_line(event.x, event.y)

  def on_mouseup(event):
    nonlocal drawing
    if drawing:
      draw_line(event.x, event.y)
      drawing = False
      strokes[-1] += [x * 255.0 / WIDTH, y * 255.0 / HEIGHT]
      update_strokes()

  def on_undo():
    if strokes:
      strokes.pop()
      for l in lines.pop(): canvas.delete(l)
      update_strokes()
      if not strokes: disable_buttons()

  def on_clear():
    strokes.clear(); lines.clear()
    canvas.delete("all"); draw_grid()
    update_strokes(); disable_buttons()

  def on_done():
    res_frame = tk.Frame(win)
    res_btns  = tk.Frame(res_frame)
    btn_back  = tk.Button(res_btns, text = "Go Back", command = on_back(res_frame))
    lbl_info  = tk.Label(res_btns, text = "Click to copy to clipboard")
    res_grid  = tk.Frame(res_frame)

    ms = matches(strokes, fuzzy = var_fuzzy.get(), offby1 = var_ob1.get())
    for i, (_, kanji) in enumerate(ms):
      col, row = i % COLS, i // COLS
      res_grid.columnconfigure(col, weight = 1)
      res_grid.rowconfigure(row, weight = 1)
      btn = tk.Button(res_grid, text = kanji, font = kanji_font,
                      command = on_select_kanji(res_frame, kanji))
      btn.grid(column = col, row = row, sticky = "nsew")

    btn_back.pack(side = tk.LEFT, padx = 5, pady = 5)
    lbl_info.pack(side = tk.LEFT, padx = 5, pady = 5)
    res_btns.pack(); res_grid.pack()
    res_frame.grid(row = 0, column = 0, sticky = "nsew")
    win.bind("<Escape>", on_back(res_frame))

  def on_back(res_frame):
    def f(event = None):
      win.unbind("<Escape>")
      res_frame.destroy()
    return f

  def on_select_kanji(res_frame, kanji):
    def f():
      copy_to_clipboard(kanji)
      res_frame.destroy()
      on_clear()
    return f

  def draw_line(x2, y2):
    nonlocal x, y
    l = canvas.create_line(x, y, x2, y2, width = LINEWIDTH, capstyle = tk.ROUND)
    lines[-1].append(l)
    x, y = x2, y2

  def draw_grid():
    for x in (WIDTH // 3, 2 * WIDTH // 3):
      canvas.create_line(x, 0, x, HEIGHT, fill = gridcolour)
    for y in (HEIGHT // 3, 2 * HEIGHT // 3):
      canvas.create_line(0, y, WIDTH, y, fill = gridcolour)

  def disable_buttons():
    for w in [btn_undo, btn_clear, btn_done]: w.config(state = tk.DISABLED)

  def enable_buttons():
    for w in [btn_undo, btn_clear, btn_done]: w.config(state = tk.NORMAL)

  def update_strokes():
    lbl_strokes.config(text = "Strokes: {}".format(len(strokes)))

  def copy_to_clipboard(text):
    win.clipboard_clear()
    win.clipboard_append(text)

  draw_frame  = tk.Frame(win)
  btns        = tk.Frame(draw_frame)
  btn_undo    = tk.Button(btns, text = "Undo", command = on_undo)
  btn_clear   = tk.Button(btns, text = "Clear", command = on_clear)
  lbl_strokes = tk.Label(btns, text = "Strokes: 0")
  btn_done    = tk.Button(btns, text = "Done", command = on_done)
  checks      = tk.Frame(draw_frame)
  var_fuzzy   = tk.IntVar()
  var_ob1     = tk.IntVar()
  check_fuzzy = tk.Checkbutton(checks, variable = var_fuzzy,
                               text = "Ignore stroke order & direction")
  check_ob1   = tk.Checkbutton(checks, variable = var_ob1, text = "± 1 stroke")

  canvas = tk.Canvas(draw_frame, height = HEIGHT, width = WIDTH,
                     bg = BACKGROUND)
  canvas.bind("<ButtonPress-1>", on_mousedown)
  canvas.bind("<B1-Motion>", on_mousemove)
  canvas.bind("<ButtonRelease-1>", on_mouseup)

  draw_grid(); disable_buttons()
  for w in [btn_undo, btn_clear, lbl_strokes, btn_done, check_fuzzy, check_ob1]:
    w.pack(side = tk.LEFT, padx = 5, pady = 5)
  btns.pack(); checks.pack(); canvas.pack()
  draw_frame.grid(row = 0, column = 0, sticky = "nsew")
  win.mainloop()
                                                                # }}}1

def main():
  if "--version" in sys.argv:
    from .lib import __version__
    print("{} v{}".format(NAME, __version__))
  else:
    gui()

if __name__ == "__main__":
  if "--doctest" in sys.argv:
    verbose = "--verbose" in sys.argv
    import doctest
    if doctest.testmod(verbose = verbose)[0]: sys.exit(1)
  else:
    main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
