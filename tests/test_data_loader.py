import pandas as pd

from src.data_loader import (
    load_jodi_files,
    MISSING_VALUE_CODES,
)


def test_missing_value_codes():
    assert MISSING_VALUE_CODES["-"] == "not_reported"
    assert MISSING_VALUE_CODES[".."] == "conversion_factor_unavailable"
    assert MISSING_VALUE_CODES["x"] == "unit_not_applicable"


def test_load_jodi_files(tmp_path):

    sample = pd.DataFrame(
        {
            "REF_AREA": ["BD", "BD", "BD"],
            "TIME_PERIOD": ["2026-01", "2026-01", "2026-01"],
            "ENERGY_PRODUCT": ["CRUDEOIL"] * 3,
            "FLOW_BREAKDOWN": ["INDPROD"] * 3,
            "UNIT_MEASURE": ["KBD", "KBBL", "CONVBBL"],
            "OBS_VALUE": ["150.5", "-", "7.2"],
            "ASSESSMENT_CODE": ["1", "2", "3"],
        }
    )

    sample.to_csv(
        tmp_path / "primaryyear2026.csv",
        index=False,
    )

    result = load_jodi_files(tmp_path)

    assert len(result) == 3

    assert result.iloc[0]["OBS_VALUE_NUMERIC"] == 150.5

    assert pd.isna(result.iloc[1]["OBS_VALUE_NUMERIC"])

    assert result.iloc[1]["OBS_VALUE_STATUS"] == "not_reported"

    assert result.iloc[0]["OBSERVATION_DATE"] == pd.Timestamp("2026-01-01")

    assert "SOURCE_FILE" in result.columns
