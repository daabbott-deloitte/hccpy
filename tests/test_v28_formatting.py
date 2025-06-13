"""
    This unit test tests that the bugfix for formatting issues in the
    v28 mapping file has been fixed.
    See commit f2a1da3f1fb71c60cb8a6749986973afb48c71a8 for details.
"""

import pytest

from hccpy.hcc import HCCEngine

SEGMENTS = ["CNA", "CND", "CPA", "CPD", "CFA", "CFD", "INS", "NE"]
HCC191_DX = {
    "HCC180": "G8250",
    "HCC181": "G8220",
    "HCC182": "B0082",
    "HCC191": "G800",
    "HCC192": "G801",
    "HCC253": "G8100",
}
HCC192_DX = {
    "HCC180": "G8250",
    "HCC181": "G8220",
    "HCC182": "B0082",
    "HCC192": "G801",
    "HCC253": "G8100",
}
HCC221_DX = {
    "HCC221": "T8620",
    "HCC222": "I5084",
    "HCC223": "Z95811",
    "HCC224": "I5023",
    "HCC225": "I5021",
    "HCC226": "I501",
    "HCC227": "I514",
}
HCC222_DX = {
    "HCC222": "I5084",
    "HCC223": "Z95811",
    "HCC224": "I5023",
    "HCC225": "I5021",
    "HCC226": "I501",
    "HCC227": "I514",
}
HCC_DICT = {
    "HCC191": HCC191_DX,
    "HCC221": HCC221_DX,
    "HCC192": HCC192_DX,
    "HCC222": HCC222_DX,
}
AGE = 65
SEX = "M"


@pytest.fixture
def he_28():
    return HCCEngine("28")


def run_hier(he_28, hcc):
    d = HCC_DICT[hcc]
    for s in SEGMENTS:
        for hcc_, dx in d.items():
            if hcc_ == hcc:
                continue
            r = he_28.profile(
                dx_lst=[d[hcc], dx],
                age=AGE,
                sex=SEX,
                elig=s,
            )["hcc_lst"]
            assert hcc_ not in r and hcc in r, f"{hcc} hierarchy fails for {s}"


def test_hcc191(he_28):
    run_hier(he_28, "HCC191")


def test_hcc192(he_28):
    run_hier(he_28, "HCC192")


def test_hcc221(he_28):
    run_hier(he_28, "HCC221")


def test_hcc222(he_28):
    run_hier(he_28, "HCC222")
