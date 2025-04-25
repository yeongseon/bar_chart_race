import pandas as pd
from bar_chart_race._utils import prepare_long_data

def test_prepare_long_data_basic():
    # Step 1: Long format sample data
    data = pd.DataFrame({
        'year': [2020, 2020, 2021, 2021, 2021, 2022, 2022],
        'country': ['A', 'B', 'A', 'B', 'C', 'A', 'C'],
        'value': [10, 20, 30, 40, 50, 60, 70]
    })

    # Step 2: Run prepare_long_data with minimal settings
    df_values, df_ranks = prepare_long_data(
        df=data,
        index='year',
        columns='country',
        values='value',
        interpolate_period=False,
        steps_per_period=1
    )

    # Step 3: Verify shape
    assert df_values.shape[0] == 3  # years: 2020, 2021, 2022
    assert df_values.shape[1] == 3  # countries: A, B, C

    # Step 4: Verify contents
    assert df_values.loc[2020, 'A'] == 10
    assert df_values.loc[2021, 'B'] == 40
    assert df_values.loc[2022, 'C'] == 70
    assert df_ranks.loc[2022, 'A'] == 2  # Expected ranking order

    # Optional: check for no NaNs (after ffill)
    assert not df_values.isna().any().any()
