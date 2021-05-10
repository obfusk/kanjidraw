#!/usr/bin/python3
# encoding: utf-8

# --                                                            ; {{{1
#
# File        : kanjidraw/gui.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2021-05-10
#
# Copyright   : Copyright (C) 2021  Felix C. Stegerman
# Version     : v0.0.1
# License     : AGPLv3+
#
# --                                                            ; }}}1

                                                                # {{{1
r"""

Handwritten kanji recognition: tkinter GUI.

"""                                                             # }}}1

import sys

import tkinter as tk
import tkinter.font as tk_font
from tkinter import Tk, Button, Canvas, Frame, Label

from .lib import kanji_data, matches

NAME, TITLE = "kanjidraw", "Kanji Draw"
HEIGHT, WIDTH, BACKGROUND = 400, 400, "#ccc"
ROWS, LINEWIDTH, FONTSIZE = 5, 5, 35

def gui():                                                      # {{{1
  """Tkinter GUI."""

  win = Tk()
  win.title(TITLE)
  win.columnconfigure(0, weight = 1)
  win.rowconfigure(0, weight = 1)

  font = tk_font.Font(size = FONTSIZE)
  max_strokes = max(kanji_data().keys())
  drawing, x, y, strokes, lines = False, 0, 0, [], []

  def on_mousedown(event):
    nonlocal drawing, x, y
    if len(strokes) < max_strokes:
      drawing, x, y = True, event.x, event.y
      strokes.append([x * 255.0 / HEIGHT, y * 255.0 / WIDTH])
      lines.append([])
      enable_buttons()

  def on_mousemove(event):
    if drawing: draw_line(event.x, event.y)

  def on_mouseup(event):
    nonlocal drawing
    if drawing:
      draw_line(event.x, event.y)
      drawing = False
      strokes[-1] += [x * 255.0 / HEIGHT, y * 255.0 / WIDTH]
      update_strokes()

  def on_undo():
    if strokes:
      strokes.pop()
      for l in lines.pop(): canvas.delete(l)
      update_strokes()
      if not strokes: disable_buttons()

  def on_clear():
    strokes.clear()
    canvas.delete("all")
    update_strokes()
    disable_buttons()

  def on_done():
    res_frame = Frame(win)
    res_btns  = Frame(res_frame)
    btn_back  = Button(res_btns, text = "Go Back", command = on_back(res_frame))
    lbl_info  = Label(res_btns, text = "Click to copy to clipboard")
    res_grid  = Frame(res_frame)
    for i, (_, kanji) in enumerate(matches(strokes)):
      col, row = i % ROWS, i // ROWS
      res_grid.columnconfigure(col, weight = 1)
      res_grid.rowconfigure(row, weight = 1)
      btn = Button(res_grid, text = kanji, font = font,
                   command = on_select_kanji(res_frame, kanji))
      btn.grid(column = col, row = row, sticky = "nsew")
    btn_back.pack(side = tk.LEFT, padx = 5, pady = 5)
    lbl_info.pack(side = tk.LEFT, padx = 5, pady = 5)
    res_btns.pack()
    res_grid.pack()
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

  def disable_buttons():
    for w in [btn_undo, btn_clear, btn_done]: w.config(state = tk.DISABLED)

  def enable_buttons():
    for w in [btn_undo, btn_clear, btn_done]: w.config(state = tk.NORMAL)

  def update_strokes():
    lbl_strokes.config(text = "Strokes: {}".format(len(strokes)))

  def copy_to_clipboard(text):
    win.clipboard_clear()
    win.clipboard_append(text)

  draw_frame  = Frame(win)
  btns        = Frame(draw_frame)
  btn_undo    = Button(btns, text = "Undo", command = on_undo)
  btn_clear   = Button(btns, text = "Clear", command = on_clear)
  lbl_strokes = Label(btns, text = "Strokes: 0")
  btn_done    = Button(btns, text = "Done", command = on_done)
  disable_buttons()

  canvas = Canvas(draw_frame, height = HEIGHT, width = WIDTH, bg = BACKGROUND)
  canvas.bind("<ButtonPress-1>", on_mousedown)
  canvas.bind("<B1-Motion>", on_mousemove)
  canvas.bind("<ButtonRelease-1>", on_mouseup)

  for w in [btn_undo, btn_clear, lbl_strokes, btn_done]:
    w.pack(side = tk.LEFT, padx = 5, pady = 5)
  btns.pack()
  canvas.pack()
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
