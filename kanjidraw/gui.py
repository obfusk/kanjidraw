#!/usr/bin/python3
# encoding: utf-8

# --                                                            ; {{{1
#
# File        : kanjidraw/gui.py
# Maintainer  : FC Stegerman <flx@obfusk.net>
# Date        : 2022-07-26
#
# Copyright   : Copyright (C) 2022  FC Stegerman
# Version     : v0.2.3
# License     : AGPLv3+
#
# --                                                            ; }}}1

                                                                # {{{1
r"""

Handwritten kanji recognition: tkinter GUI.

"""                                                             # }}}1

import argparse, os, sys

import tkinter as tk
import tkinter.font

from tkinter import ttk

from .lib import kanji_data, matches, __version__

NAME, TITLE = "kanjidraw", "Kanji Draw"
HEIGHT = WIDTH = 400
COLS, LINEWIDTH, FONTSIZE = 5, 5, 35
FONTS = ("Noto Sans CJK JP", "Noto Sans CJK SC", "Noto Sans CJK TC",
         "IPAexGothic", "IPAGothic")

LIGHT_THEME = dict(
  bg = "#fff", bg_active = "#eee", fg = "#000", btn_fg = "#fff",
  btn_bg = "#375a7f", btn_bg_active = "#1a252f",
  btn_bg_disabled = "#7c93ab", btn_fg_disabled = "#fff",
  canvas_fg = "#000", grid = "#999"
)
DARK_THEME = dict(
  bg = "#333", bg_active = "#222", fg = "#fff", btn_fg = "#fff",
  btn_bg = "#375a7f", btn_bg_active = "#28415b",
  btn_bg_disabled = "#344b63", btn_fg_disabled = "#b7b7b7",
  canvas_fg = "#ddd", grid = "#999"
)

def frame_button(master, size, **kw):
  frame = ttk.Frame(master, width = size, height = size)
  frame.columnconfigure(0, weight = 1)
  frame.rowconfigure(0, weight = 1)
  frame.grid_propagate(False)
  btn = ttk.Button(frame, **kw)
  btn.grid(column = 0, row = 0, sticky = "nsew")
  return frame, btn

def gui(stdout = False, oneshot = False, multiple = False,      # {{{1
        dark = False):
  """Tkinter GUI."""

  nogrid = os.environ.get("KANJIDRAW_NOGRID") in ("1", "true", "yes")
  if os.environ.get("KANJIDRAW_DARK") in ("1", "true", "yes"):
    dark = True

  win = tk.Tk()
  win.title(TITLE)
  win.columnconfigure(0, weight = 1)
  win.rowconfigure(0, weight = 1)

  theme = DARK_THEME if dark else LIGHT_THEME
  fonts = set(tkinter.font.families())
  kanji_font = tk.font.Font()

  for f in FONTS:
    if f in fonts:
      kanji_font.config(family = f)
      break

  kanji_btn_font = kanji_font.copy()
  kanji_btn_font.config(size = FONTSIZE)

  s = ttk.Style()
  s.configure(".", background = theme["bg"], foreground = theme["fg"])
  s.configure("TButton", background = theme["btn_bg"],
                         foreground = theme["btn_fg"])
  s.map(".", background = [("active", theme["bg_active"]),
                           ("disabled", theme["bg"])])
  s.map("TButton", background = [("active", theme["btn_bg_active"]),
                                 ("disabled", theme["btn_bg_disabled"])],
                   foreground = [("active", theme["btn_fg"]),
                                 ("disabled", theme["btn_fg_disabled"])])
  s.configure("Kanji.TButton", font = kanji_btn_font)
  s.configure("Kanji.TLabel", font = kanji_font)

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
    res_frame = ttk.Frame(win)
    res_btns  = ttk.Frame(res_frame)
    btn_back  = ttk.Button(res_btns, text = "Go Back", command = on_back(res_frame))
    lbl_info  = ttk.Label(res_btns, text = info_txt)
    res_grid  = ttk.Frame(res_frame)

    ms = matches(strokes, fuzzy = var_fuzzy.get(), offby1 = var_ob1.get())
    for i, (_, kanji) in enumerate(ms):
      col, row = i % COLS, i // COLS
      res_grid.columnconfigure(col, weight = 1)
      res_grid.rowconfigure(row, weight = 1)
      frame, btn = frame_button(res_grid, WIDTH // COLS,
                                text = kanji, style = "Kanji.TButton",
                                command = on_select_kanji(res_frame, kanji))
      frame.grid(column = col, row = row, sticky = "nsew")

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
      nonlocal drawn_kanji
      if multiple:
        drawn_kanji += kanji
        kanji_lbl.config(text = drawn_kanji)
      else:
        (print if stdout else copy_to_clipboard)(kanji)
        if oneshot: win.quit()
      res_frame.destroy()
      on_clear()
    return f

  def draw_line(x2, y2):
    nonlocal x, y
    l = canvas.create_line(x, y, x2, y2, width = LINEWIDTH,
                           capstyle = tk.ROUND, fill = theme["canvas_fg"])
    lines[-1].append(l)
    x, y = x2, y2

  def draw_grid():
    if not nogrid:
      for x in (WIDTH // 3, 2 * WIDTH // 3):
        canvas.create_line(x, 0, x, HEIGHT, fill = theme["grid"])
      for y in (HEIGHT // 3, 2 * HEIGHT // 3):
        canvas.create_line(0, y, WIDTH, y, fill = theme["grid"])

  def disable_buttons():
    for w in [btn_undo, btn_clear, btn_done]: w.config(state = tk.DISABLED)

  def enable_buttons():
    for w in [btn_undo, btn_clear, btn_done]: w.config(state = tk.NORMAL)

  def update_strokes():
    lbl_strokes.config(text = "Strokes: {}".format(len(strokes)))

  def copy_to_clipboard(text):
    win.clipboard_clear()
    win.clipboard_append(text)

  draw_frame  = ttk.Frame(win)
  btns        = ttk.Frame(draw_frame)
  btn_undo    = ttk.Button(btns, text = "Undo", command = on_undo)
  btn_clear   = ttk.Button(btns, text = "Clear", command = on_clear)
  lbl_strokes = ttk.Label(btns, text = "Strokes: 0")
  btn_done    = ttk.Button(btns, text = "Done", command = on_done)
  checks      = ttk.Frame(draw_frame)
  var_fuzzy   = tk.IntVar()
  var_ob1     = tk.IntVar()
  check_fuzzy = ttk.Checkbutton(checks, variable = var_fuzzy,
                                text = "Ignore stroke order & direction")
  check_ob1   = ttk.Checkbutton(checks, variable = var_ob1, text = "± 1 stroke")

  canvas = tk.Canvas(draw_frame, height = HEIGHT, width = WIDTH,
                     background = theme["bg"], highlightthickness = 1,
                     highlightbackground = theme["canvas_fg"])
  canvas.bind("<ButtonPress-1>", on_mousedown)
  canvas.bind("<B1-Motion>", on_mousemove)
  canvas.bind("<ButtonRelease-1>", on_mouseup)

  draw_grid(); disable_buttons()
  for w in [btn_undo, btn_clear, lbl_strokes, btn_done, check_fuzzy, check_ob1]:
    w.pack(side = tk.LEFT, padx = 5, pady = 5)
  btns.pack(); checks.pack(); canvas.pack()
  draw_frame.grid(row = 0, column = 0, sticky = "nsew")

  if multiple:
    info_txt    = "Click to add to queue"                     #  FIXME
    drawn_kanji = ""
    kanji_lbl   = ttk.Label(draw_frame, style = "Kanji.TLabel")
    kanji_lbl.pack()

    def output():
      nonlocal drawn_kanji
      if drawn_kanji:
        (print if stdout else copy_to_clipboard)(drawn_kanji)
        drawn_kanji = ""
        kanji_lbl.config(text = "")

    def quit():
      output()
      win.quit()

    win.bind("c", lambda e: output())
    win.bind("q", lambda e: quit())
    win.protocol("WM_DELETE_WINDOW", quit)
  else:
    if stdout:
      info_txt = "Click to print to stdout"
    else:
      info_txt = "Click to copy to clipboard"
    win.bind("q", lambda e: win.quit())

  win.update()
  win.minsize(win.winfo_width(), win.winfo_height())
  win.maxsize(win.winfo_width(), win.winfo_height())
  win.mainloop()
                                                                # }}}1

def main():                                                     # {{{1
  p = argparse.ArgumentParser(prog = NAME)
  p.add_argument("-s", "--stdout", action = "store_true",
                 help = "print kanji to stdout instead of "
                        "copying to clipboard")
  g = p.add_mutually_exclusive_group()
  g.add_argument("-o", "--oneshot", action = "store_true",
                 help = "quit after one kanji")
  g.add_argument("-m", "--multiple", action = "store_true",
                 help = "queue kanji and copy/print after "
                        "pressing 'c' or quitting")
  p.add_argument("-d", "--dark", action = "store_true",
                 help = "use dark theme")
  p.add_argument("--version", action = "version",
                 version = "%(prog)s {}".format(__version__))
  gui(**vars(p.parse_args()))
                                                                # }}}1

if __name__ == "__main__":
  if "--doctest" in sys.argv:
    verbose = "--verbose" in sys.argv
    import doctest
    if doctest.testmod(verbose = verbose)[0]: sys.exit(1)
  else:
    main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
