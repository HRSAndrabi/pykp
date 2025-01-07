from sphinxawesome_theme import ThemeOptions
from sphinxawesome_theme.postprocess import Icons
import sys, os


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
html_theme = "pydata_sphinx_theme"
html_permalinks_icon = Icons.permalinks_icon
html_static_path = ["_static"]

html_sidebars = {
  "index.html": [],
  "about/*": [],
  "quick-start/*": [],
  "reference/*": [],
  "contributing/*": [],
}

html_theme_options = {
  "header_links_before_dropdown": 4,
  "github_url": "https://github.com/HRSAndrabi/pykp",
}

