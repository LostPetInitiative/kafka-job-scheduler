# Docstring required by flit.
"""Command line utility for downloading standards documents from the 3GPP download site."""

import os.path

# The VERSION file is located in the same directory as this __init__.py file.
here = os.path.abspath(os.path.dirname(__file__))
version_file_path = os.path.abspath(os.path.join(here, "VERSION"))

with open(version_file_path) as version_file:
    version = version_file.read().strip()

# Internally the code can consume the release id using the __version__ variable.
__version__ = version