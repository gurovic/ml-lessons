"""LaTeX → native PowerPoint Equation (OMML) через latex2mathml + MML2OMML.XSL."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from lxml import etree

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
A14_NS = "http://schemas.microsoft.com/office/drawing/2010/main"

XSL_BUNDLED = Path(__file__).parent / "assets" / "MML2OMML.XSL"
XSL_OFFICE_PATHS = [
    Path(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"),
    Path(r"C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL"),
    Path(r"C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL"),
]


def find_xsl_path() -> Path:
    if XSL_BUNDLED.exists():
        return XSL_BUNDLED
    for path in XSL_OFFICE_PATHS:
        if path.exists():
            return path
    raise FileNotFoundError(
        "MML2OMML.XSL не найден. Ожидается agents/assets/MML2OMML.XSL "
        "или установленный Microsoft Office."
    )


@lru_cache(maxsize=1)
def _xslt_transform():
    return etree.XSLT(etree.parse(str(find_xsl_path())))


def latex_to_omml_oMath(latex: str) -> etree._Element:
    """LaTeX → элемент m:oMath (MML2OMML.XSL требует MathML с namespace)."""
    import latex2mathml.converter

    mathml = latex2mathml.converter.convert(latex.strip())
    tree = etree.fromstring(mathml.encode("utf-8"))
    omml = _xslt_transform()(tree)
    root = omml.getroot()
    if root is None:
        raise ValueError(f"Не удалось сконвертировать формулу: {latex!r}")
    return root


def wrap_omml_for_powerpoint(omath: etree._Element) -> etree._Element:
    """Обёртка a14:m, требуемая PowerPoint для Equation в textbox."""
    wrapper = etree.Element(f"{{{A14_NS}}}m")
    wrapper.append(omath)
    return wrapper


def latex_to_pptx_element(latex: str) -> etree._Element:
    return wrap_omml_for_powerpoint(latex_to_omml_oMath(latex))
