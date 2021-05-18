<!-- {{{1

    File        : README.md
    Maintainer  : Felix C. Stegerman <flx@obfusk.net>
    Date        : 2021-05-18

    Copyright   : Copyright (C) 2021  Felix C. Stegerman
    Version     : v0.2.1
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

## Miscellaneous

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
