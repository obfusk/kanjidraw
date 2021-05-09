from pathlib import Path
import setuptools

from kanjidraw import __version__

info = Path(__file__).with_name("README.md").read_text(encoding = "utf8")

setuptools.setup(
  name              = "kanjidraw",
  url               = "https://github.com/obfusk/kanjidraw",
  description       = "handwritten kanji recognition",
  long_description  = info,
  long_description_content_type = "text/markdown",
  version           = __version__,
  author            = "Felix C. Stegerman",
  author_email      = "flx@obfusk.net",
  license           = "AGPLv3+",
  classifiers       = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    "Natural Language :: Japanese",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
  # "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: Implementation :: CPython",
  # "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Text Processing",
    "Topic :: Utilities",
  ],
  keywords          = "japanese kanji draw handwriting",
  packages          = setuptools.find_packages(),
  package_data      = dict(kanjidraw = ["data.json"]),
  entry_points      = dict(
    console_scripts = ["kanjidraw = kanjidraw.gui:main"]
  ),
  python_requires   = ">=3.5",
)
