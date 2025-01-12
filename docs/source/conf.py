import math  # noqa: D100
import os
import sys
from typing import Any, Dict
from unittest.mock import MagicMock

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.sphinxext.plot_directive
from sphinx.application import Sphinx

# -----------------------------------------------------------------------------
# General configuration
# -----------------------------------------------------------------------------

MOCK_MODULES = [
    "pandas",
    "networkx",
    "nest_asyncio",
    "minizinc",
]
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = MagicMock()

sys.path.insert(0, os.path.abspath("../.."))

project = "PyKP"
copyright = "2025, Hassan Andrabi"
author = "Hassan Andrabi"

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "sphinx.ext.autosectionlabel",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_favicon",
    "matplotlib.sphinxext.plot_directive",
]

# Turn on sphinx.ext.autosummary
autosummary_generate = True

# Group entries by type
autodoc_member_order = "groupwise"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Apply the .. plot:: directive to examples
numpydoc_use_plots = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -----------------------------------------------------------------------------
# Napoleon configuration
# -----------------------------------------------------------------------------
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -----------------------------------------------------------------------------
# Matplotlib plot_directive options
# -----------------------------------------------------------------------------
plot_include_source = True
plot_formats = [("png", 96)]
plot_html_show_formats = False
plot_html_show_source_link = False

phi = (math.sqrt(5) + 1) / 2

font_size = 13 * 72 / 96.0  # 13 px

plot_rcparams = {
    "font.size": font_size,
    "axes.titlesize": font_size,
    "axes.labelsize": font_size,
    "xtick.labelsize": font_size,
    "ytick.labelsize": font_size,
    "legend.fontsize": font_size,
    "figure.figsize": (3 * phi, 3),
    "figure.subplot.bottom": 0.2,
    "figure.subplot.left": 0.2,
    "figure.subplot.right": 0.9,
    "figure.subplot.top": 0.85,
    "figure.subplot.wspace": 0.4,
    "text.usetex": False,
}

# Do some matplotlib config in case users have a matplotlibrc that will break
# things
matplotlib.use("agg")
plt.ioff()


# -----------------------------------------------------------------------------
# HTML output
# -----------------------------------------------------------------------------
html_static_path = ["_static"]
html_favicon = "_static/logo.svg"
html_js_files = ["pypi-icon.js"]
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_context = {
    "github_user": "HRSAndrabi",
    "github_repo": "pykp",
    "github_version": "main",
    "doc_path": "docs/source",
}

# see https://sphinx-favicon.readthedocs.io for more information about the
# sphinx-favicon extension
favicons = [
    # generic icons compatible with most browsers
    "favicon-32x32.png",
    "favicon-16x16.png",
    {"rel": "shortcut icon", "sizes": "any", "href": "favicon.ico"},
    # chrome specific
    "android-chrome-192x192.png",
    # apple icons
    {"rel": "mask-icon", "color": "#459db9", "href": "safari-pinned-tab.svg"},
    {"rel": "apple-touch-icon", "href": "apple-touch-icon.png"},
    # msapplications
    {"name": "msapplication-TileColor", "content": "#459db9"},
    {"name": "theme-color", "content": "#ffffff"},
    {"name": "msapplication-TileImage", "content": "mstile-150x150.png"},
]

html_sidebars = {
    "index.html": [],
    "about/*": [],
    "quick-start/*": [],
    # "reference/*": [],
    "contributing/*": [],
}

html_theme_options = {
    "header_links_before_dropdown": 4,
    # "github_url": "https://github.com/HRSAndrabi/pykp",
    "footer_start": ["copyright"],
    "footer_end": [],
    "use_edit_page_button": True,
    "secondary_sidebar_items": {
        "about/*": ["page-toc", "edit-this-page"],
        "contributing/*": ["page-toc", "edit-this-page"],
        "installation/*": ["page-toc", "edit-this-page"],
        "quick-start/*": ["page-toc", "edit-this-page"],
        "reference/*": ["page-toc", "edit-this-page"],
        "**/generated/*": ["page-toc"],
    },
    "logo": {
        "image_light": "_static/logo-light.svg",
        "image_dark": "_static/logo-dark.svg",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/HRSAndrabi/pykp",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/pykp",
            "icon": "fa-custom fa-pypi",
        },
    ],
}


# Set up the "Edit on GitHub" link
def setup_to_main(
    app: Sphinx, pagename: str, templatename: str, context, doctree
) -> None:
    """Ensure that the "edit this page" link points to the main branch.

    Add a function that jinja can access for returning an "edit this page" link
    pointing to `main`.
    """

    def to_main(link: str) -> str:
        """Ensure that the "edit this page" link points to the main branch.

        Transform "edit on github" links and make sure they always point to the
        main branch.

        Parameters
        ----------
        link : str
            the link to the github edit interface.

        Returns
        -------
        str
            The link to the tip of the main branch for the same file.
        """
        links = link.split("/")
        idx = links.index("edit")
        return (
            "/".join(links[: idx + 1]) + "/main/" + "/".join(links[idx + 2 :])
        )

    context["to_main"] = to_main


def setup(app: Sphinx) -> Dict[str, Any]:
    """Add custom configuration to sphinx app.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application.

    Returns
    -------
    Dict
        The 2 parallel parameters set to ``True``.
    """
    app.connect("html-page-context", setup_to_main)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
