"""
This unit test tests that the df_profile() which take dataframe as input and
run hccpy in parallel can achieve the same result as profile() which calculate
risk score and hcc_list bene by bene.
"""

import pytest
import pandas as pd
from hccpy.hcc import HCCEngine

data = {
    0: [
        ["L988", "Z96653", "L97429", "B351", "L97419", "M109"],
        80,
        "F",
        "CNA",
        1,
        False,
    ],
    1: [["L84", "B351", "M109", "M2041", "D8687", "E083211"], 72, "M", "INS", 0, False],
    2: [["D122", "M25473", "D6859", "F13181"], 65, "M", "CPD", 0, True],
}

df = pd.DataFrame.from_dict(
    data, orient="index", columns=["dx_lst", "age", "sex", "elig", "orec", "medicaid"]
)


def calc_hccpy(
    profile: pd.Series,
    he: HCCEngine,
) -> dict:
    """Get the risk from a dictionary input or a 'row' of data from a DataFrame."""
    dx_list_cleaned = profile["dx_lst"]
    p = he.profile(
        dx_lst=dx_list_cleaned,
        age=profile["age"],
        sex=profile["sex"],
        elig=profile["elig"],
        orec=profile["orec"],
        medicaid=profile["medicaid"],
    )
    return pd.Series(p)


@pytest.fixture
def he_28():
    return HCCEngine("28")


def test_run_hcc(he_28):
    global df
    df1 = df.apply(lambda row: calc_hccpy(row, he_28), axis=1)
    df2 = he_28.profile(df)
    assert len(df1) == len(df2), "the output row number mismatch"
    assert (df1["risk_score"] == df2["risk_score"]).all(), "the risk score is not equal"
    assert all(
        set(a) == set(b) for a, b in zip(df1["hcc_lst"], df2["hcc_lst"])
    ), "the generated hcc_lst is not the same"
