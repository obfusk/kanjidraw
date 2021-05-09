#!/usr/bin/python3
# encoding: utf-8

# --                                                            ; {{{1
#
# File        : kanjidraw/gui.py
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

import sys

from . import load_json, matches

def tkinter_main():                                             # {{{1
  import tkinter as tk
  import tkinter.font as tk_font
  from tkinter import Tk, Button, Canvas, Frame, Label

  win = Tk()
  win.title("Kanji Draw")
  win.columnconfigure(0, weight = 1)
  win.rowconfigure(0, weight = 1)

  height, width, bg, rows = 400, 400, "#ccc", 5
  font = tk_font.Font(size = 35)

  data = load_json()
  max_strokes = max(data.keys())
  drawing, x, y, strokes, lines = False, 0, 0, [], []

  def on_mousedown(event):
    if len(strokes) < max_strokes:
      nonlocal drawing, x, y
      drawing, x, y = True, event.x, event.y
      strokes.append([x * 255.0 / height, y * 255.0 / width])
      lines.append([])
      enable_buttons()

  def on_mousemove(event):
    nonlocal x, y
    if drawing:
      draw_line(x, y, event.x, event.y)
      x, y = event.x, event.y

  def on_mouseup(event):
    nonlocal drawing, x, y
    if drawing:
      draw_line(x, y, event.x, event.y)
      drawing, x, y = False, event.x, event.y
      strokes[-1] += [x * 255.0 / height, y * 255.0 / width]
      update_strokes()

  def on_undo():
    if strokes:
      strokes.pop()
      for l in lines.pop():
        canvas.delete(l)
      update_strokes()
      if not strokes:
        disable_buttons()

  def on_clear():
    strokes.clear()
    canvas.delete("all")
    update_strokes()
    disable_buttons()

  def on_done():
    results_frame = Frame(win)
    for i, (_, kanji) in enumerate(matches(strokes, data)):
      results_frame.columnconfigure(i % rows, weight = 1)
      results_frame.rowconfigure(i // rows, weight = 1)
      btn = Button(results_frame, text = kanji, font = font,
                   command = on_select_kanji(results_frame, kanji))
      btn.grid(column = i % rows, row = i // rows, sticky = "nsew")
    results_frame.grid(row = 0, column = 0, sticky = "nsew")

  def on_select_kanji(results_frame, kanji):
    def handler():
      copy_to_clipboard(kanji)
      results_frame.destroy()
      on_clear()
    return handler

  def draw_line(x1, y1, x2, y2):
    l = canvas.create_line(x1, y1, x2, y2, width = 5, capstyle = tk.ROUND)
    lines[-1].append(l)

  def disable_buttons():
    for w in [btn_undo, btn_clear, btn_done]:
      w.config(state = tk.DISABLED)

  def enable_buttons():
    for w in [btn_undo, btn_clear, btn_done]:
      w.config(state = tk.NORMAL)

  def update_strokes():
    lbl_strokes.config(text = "Strokes: {}".format(len(strokes)))

  def copy_to_clipboard(text):
    win.clipboard_clear()
    win.clipboard_append(text)

  draw_frame = Frame(win)
  btns = Frame(draw_frame)
  btn_undo = Button(btns, text = "Undo", command = on_undo)
  btn_clear = Button(btns, text = "Clear", command = on_clear)
  lbl_strokes = Label(btns, text = "Strokes: 0")
  btn_done = Button(btns, text = "Done", command = on_done)
  disable_buttons()

  canvas = Canvas(draw_frame, height = height, width = width, bg = bg)
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

if __name__ == "__main__":
  if "--doctest" in sys.argv:
    verbose = "--verbose" in sys.argv
    import doctest
    if doctest.testmod(verbose = verbose)[0]: sys.exit(1)
  else:
    tkinter_main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
