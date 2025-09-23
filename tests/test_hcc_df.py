"""
This unit test tests that the df_profile() which take dataframe as input and
run hccpy in parallel can achieve the same result as profile() which calculate
risk score and hcc_list bene by bene.
"""

import pytest
import pandas as pd
from hccpy.hcc import HCCEngine


@pytest.fixture
def df():
    data = {
        0: [
            ["L988", "Z96653", "L97429", "B351", "L97419", "M109"],
            80,
            "F",
            "CNA",
            1,
            False,
        ],
        1: [
            ["L84", "B351", "M109", "M2041", "D8687", "E083211"],
            72,
            "M",
            "INS",
            0,
            False,
        ],
        2: [["D122", "M25473", "D6859", "F13181"], 65, "M", "CPD", 0, True],
        3: [["D591"], 60, "M", "CPD", 0, True],
        4: [["G111"], 55, "F", "CPA", 0, False],
    }
    dataframe = pd.DataFrame.from_dict(
        data,
        orient="index",
        columns=["dx_lst", "age", "sex", "elig", "orec", "medicaid"],
    )
    return dataframe


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


@pytest.fixture
def he_updated_mapping():
    return HCCEngine("28", dx2cc_year="2024_FY21FY22")


def test_run_hcc(he_28, df):
    """
    This function tests that the df_profile() which take dataframe as input and
    run hccpy in parallel can achieve the same result as profile() which calculate
    risk score and hcc_list bene by bene.
    """
    df1 = df.apply(lambda row: calc_hccpy(row, he_28), axis=1)
    df2 = he_28.profile(df)
    assert len(df1) == len(df2), "the output row number mismatch"
    assert np.all(
        np.isclose(df1["risk_score"], df2["risk_score"], atol=1e-10, rtol=0)
    ), "the risk score is not equal"
    assert all(
        set(a) == set(b) for a, b in zip(df1["hcc_lst"], df2["hcc_lst"])
    ), "the generated hcc_lst is not the same"


def test_updated_mapping(he_28, he_updated_mapping, df):
    """
    This function tests that the updated mapping file could handle deprecated
    deleted code properly and map to expected HCC accordingly
    """
    df1 = he_28.profile(df)
    assert len(df1.iloc[3]["hcc_lst"]) == 0, "Dx code D591 is not a deleted code"
    assert len(df1.iloc[4]["hcc_lst"]) == 0, "Dx code G111 is not a deleted code"
    df2 = he_updated_mapping.profile(df)
    assert (
        "HCC109" in df2.iloc[3]["hcc_lst"]
    ), "Deleted dx code D591 is not handled properly"
    assert (
        "HCC200" in df2.iloc[4]["hcc_lst"]
    ), "Deleted dx code G111 is not handled properly"


def test_missing_demo_features(he_28, df):
    """
    This function tests that the hccpy function would raise TypeError if miss any demo features
    or contain Null value in the dataframe
    """
    with pytest.raises(TypeError):
        he_28.profile(dx_lst=["L988", "Z96653"])
    df_copy = df.copy()
    df_copy.at[1, "elig"] = None
    with pytest.raises(AssertionError):
        he_28.profile(df_copy)
