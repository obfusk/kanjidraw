<!-- {{{1

    File        : README.md
    Maintainer  : Felix C. Stegerman <flx@obfusk.net>
    Date        : 2021-05-19

    Copyright   : Copyright (C) 2021  Felix C. Stegerman
    Version     : v0.2.2
    License     : AGPLv3+

}}}1 -->

[![GitHub Release](https://img.shields.io/github/release/obfusk/kanjidraw.svg?logo=github)](https://github.com/obfusk/kanjidraw/releases)
[![PyPI Version](https://img.shields.io/pypi/v/kanjidraw.svg)](https://pypi.python.org/pypi/kanjidraw)
[![Python Versions](https://img.shields.io/pypi/pyversions/kanjidraw.svg)](https://pypi.python.org/pypi/kanjidraw)
[![CI](https://github.com/obfusk/kanjidraw/workflows/CI/badge.svg)](https://github.com/obfusk/kanjidraw/actions?query=workflow%3ACI)
[![AGPLv3+](https://img.shields.io/badge/license-AGPLv3+-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Sponsor](https://img.shields.io/badge/%E2%99%A5-support-violet.svg)](https://ko-fi.com/obfusk)

## kanjidraw - handwritten kanji recognition

`kanjidraw` is a simple Python library + GUI for matching (the strokes
of a) handwritten kanji against its database.

You can use the GUI to draw and subsequently select a kanji from the
list of probable matches, which will then be copied to the clipboard.

The database is based on KanjiVG and the algorithms are based on the
[Kanji draw](https://github.com/onitake/kanjirecog) Android app.

## Demo

[Jiten Japanese Dictionary](https://jiten.obfusk.dev)
uses `kanjidraw` with a
[JavaScript frontend](https://github.com/obfusk/jiten/blob/master/jiten/static/kanjidraw.js).

## Requirements

* Python >= 3.5 (w/ Tk support for the GUI).

### Debian/Ubuntu

```bash
$ apt install python3-tk
```

## Installing

### Using pip

```bash
$ pip install kanjidraw
```

NB: depending on your system you may need to use e.g. `pip3 --user`
instead of just `pip`.

### From git

NB: this installs the latest development version, not the latest
release.

```bash
$ git clone https://github.com/obfusk/kanjidraw.git
$ cd kanjidraw
$ pip install -e .
```

NB: you may need to add e.g. `~/.local/bin` to your `$PATH` in order
to run `kanjidraw`.

To update to the latest development version:

```bash
$ cd kanjidraw
$ git pull --rebase
```

## Examples

### Kanji Input on Linux

#### kanjidraw-paste

Opens `kanjidraw` to select one (`--oneshot`) or multiple
(`--multiple`) kanji, and afterwards pastes the selected kanji in the
active window.  Requires `xclip` and `xdotool`.

```bash
#!/bin/bash
set -e
pid="$( xdotool getactivewindow getwindowpid )"
pids() { xdotool search --classname "$1" getwindowpid %@; }
if pids urxvt | grep -q "^$pid$"; then
  key=ctrl+alt+v
elif pids terminal | grep -q "^$pid$"; then
  key=ctrl+shift+v
else
  key=ctrl+v
fi
kanjidraw -s "$@" | tr -d '\n' | xclip -i -selection clipboard
xdotool key --delay 250 "$key"
```

#### i3 config

Keybindings for i3.  Creating custom keybindings for `kanjidraw-paste
--oneshot` and/or `kanjidraw-paste --multiple` should work similarly
with other window managers and desktop environments.

```
for_window [title="Kanji Draw"] floating enable
bindsym $mod+Control+k exec --no-startup-id kanjidraw-paste --oneshot
bindsym $mod+Control+m exec --no-startup-id kanjidraw-paste --multiple
```

## Miscellaneous

### GUI Options

```bash
$ kanjidraw --help
usage: kanjidraw [-h] [-s] [-o | -m] [-d] [--version]

optional arguments:
  -h, --help      show this help message and exit
  -s, --stdout    print kanji to stdout instead of copying to clipboard
  -o, --oneshot   quit after one kanji
  -m, --multiple  queue kanji and copy/print after pressing 'c' or quitting
  -d, --dark      use dark theme
  --version       show program's version number and exit
```

Additional keybindings: `q` to quit, `<esc>` to go back.

### Enabling Dark Mode

```bash
$ export KANJIDRAW_DARK=1
```

### Disabling the Grid

```bash
$ export KANJIDRAW_NOGRID=1
```

## License

### Code

© Felix C. Stegerman

[![AGPLv3+](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.html)

### KanjiVG (stroke data)

© Ulrich Apel

[![CC-BY-SA](https://licensebuttons.net/l/by-sa/3.0/88x31.png)](https://github.com/KanjiVG/kanjivg/blob/master/COPYING)

<!-- vim: set tw=70 sw=2 sts=2 et fdm=marker : -->
