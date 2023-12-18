"""Sphinx configuration."""
project = "hca"
author = "Roger Caminal Armadans"
copyright = "2023, Roger Caminal Armadans"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
