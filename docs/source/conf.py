from sphinxawesome_theme import ThemeOptions
from sphinxawesome_theme.postprocess import Icons
from sphinx.application import Sphinx
from typing import Dict, Any
import sys, os


sys.path.insert(0, os.path.abspath(".."))

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
	# "sphinx_sitemap",
	"sphinx.ext.autosectionlabel",
	"sphinx_design",
	"sphinx_copybutton",
]

autosummary_generate = True  # Turn on sphinx.ext.autosummary
templates_path = ['_templates']

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
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

templates_path = ["_templates"]
exclude_patterns = []


pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ["_static"]
html_js_files = ["pypi-icon.js"]
html_theme = "pydata_sphinx_theme"
html_permalinks_icon = Icons.permalinks_icon
html_static_path = ["_static"]
html_context = {
    "github_user": "HRSAndrabi",
    "github_repo": "pykp",
    "github_version": "main",
    "doc_path": "docs/source",
}


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
        "**/*": ["page-toc", "edit-this-page"],
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

def setup_to_main(
    app: Sphinx, pagename: str, templatename: str, context, doctree
) -> None:
    """
    Add a function that jinja can access for returning an "edit this page" link
    pointing to `main`.
    """

    def to_main(link: str) -> str:
        """
        Transform "edit on github" links and make sure they always point to the
        main branch.

        Args:
            link: the link to the github edit interface

        Returns:
            the link to the tip of the main branch for the same file
        """
        links = link.split("/")
        idx = links.index("edit")
        return "/".join(links[: idx + 1]) + "/main/" + "/".join(links[idx + 2 :])

    context["to_main"] = to_main


def setup(app: Sphinx) -> Dict[str, Any]:
    """Add custom configuration to sphinx app.

    Args:
        app: the Sphinx application
    Returns:
        the 2 parallel parameters set to ``True``.
    """
    app.connect("html-page-context", setup_to_main)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }