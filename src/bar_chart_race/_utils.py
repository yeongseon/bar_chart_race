from pathlib import Path

import polars as pl
import pandas as pd
from matplotlib import image as mimage


def load_dataset(name='covid19'):
    '''
    Return a pandas DataFrame suitable for immediate use in `bar_chart_race`.
    Must be connected to the internet

    Parameters
    ----------
    name : str, default 'covid19'
        Name of dataset to load from the bar_chart_race github repository.
        Choices include:
        * 'covid19'
        * 'covid19_tutorial'
        * 'urban_pop'
        * 'baseball'

    Returns
    -------
    pandas DataFrame
    '''
    url = f'https://raw.githubusercontent.com/dexplo/bar_chart_race/master/data/{name}.csv'

    index_dict = {'covid19_tutorial': 'date',
                  'covid19': 'date',
                  'urban_pop': 'year',
                  'baseball': None}
    index_col = index_dict[name]
    parse_dates = [index_col] if index_col else None
    return pd.read_csv(url, index_col=index_col, parse_dates=parse_dates)

def prepare_wide_data(df: pd.DataFrame, orientation='h', sort='desc', n_bars=None,
                      interpolate_period=False, steps_per_period=10, compute_ranks=True):
    '''
    Prepares 'wide' data for bar chart animation using polars internally.
    Returns interpolated values and optionally ranks, as pandas DataFrames.

    Parameters
    ----------
    df : pandas DataFrame
        Input wide-format DataFrame (index: time, columns: categories, values)

    orientation : 'h' or 'v'
        Direction of animation bars (horizontal/vertical)

    sort : 'desc' or 'asc'
        Order of bars to appear

    n_bars : int or None
        Max number of bars to show at once

    interpolate_period : bool
        Whether to interpolate between time steps

    steps_per_period : int
        Number of interpolation steps between each period

    compute_ranks : bool
        If True, also return the rank DataFrame

    Returns
    -------
    (values_df, ranks_df) or values_df : Tuple of pandas DataFrames or just one
    '''
    if n_bars is None:
        n_bars = df.shape[1]

    # Step 1: Flatten index and convert to polars
    df_reset = df.reset_index()
    index_col = df_reset.columns[0]  # e.g., 'date' or 'year'
    df_pl = pl.from_pandas(df_reset)

    # Step 2: Expand index for interpolation (ex: 5 periods * 10 steps = 41 total)
    orig_len = df_pl.height
    new_len = (orig_len - 1) * steps_per_period + 1
    step_index = pl.Series(name="__step__", values=range(new_len))
    df_pl = df_pl.with_columns(step_index)

    # Step 3: Interpolate index values (time or numeric)
    if interpolate_period:
        # Date interpolation (e.g., 2020-01-01 to 2020-01-02 over 4 steps)
        if pd.api.types.is_datetime64_any_dtype(df[index_col]):
            dr = pd.date_range(df.index[0], df.index[-1], periods=new_len)
            df_pl = df_pl.with_columns(pl.Series(name=index_col, values=dr))
        else:
            # Numeric interpolation
            interpolated_index = pd.Series(df.index).interpolate(limit_direction='both')
            steps = pd.Series(
                np.linspace(interpolated_index.iloc[0], interpolated_index.iloc[-1], new_len)
            )
            df_pl = df_pl.with_columns(pl.Series(name=index_col, values=steps))
    else:
        # No interpolation: use forward fill to maintain constant time/index
        df_pl = df_pl.with_columns(
            pl.col(index_col).fill_null(strategy="forward")
        )

    # Step 4: Remove helper step index and set time index
    df_pl = df_pl.drop("__step__")

    # Step 5: Interpolate all columns linearly (category values)
    value_cols = [col for col in df_pl.columns if col != index_col]
    df_vals = df_pl.select([
        pl.col(index_col)
    ] + [
        pl.col(col).interpolate() for col in value_cols
    ])

    # Step 6: Compute ranks if needed
    if compute_ranks:
        ranks = df_vals.drop(index_col).rank(method="first", reverse=True)
        ranks = ranks.select([
            pl.col(col).clip_max(n_bars + 1) for col in ranks.columns
        ])

        # Flip rank (1 = top) depending on sort/orientation
        if (sort == 'desc' and orientation == 'h') or (sort == 'asc' and orientation == 'v'):
            ranks = ranks.select([
                (n_bars + 1 - pl.col(col)).alias(col) for col in ranks.columns
            ])

        # Combine ranks with index column
        df_ranks = pl.concat([df_vals.select(index_col), ranks], how="horizontal")

        # Return both values and ranks as pandas
        return df_vals.to_pandas().set_index(index_col), df_ranks.to_pandas().set_index(index_col)

    # Only return interpolated values
    return df_vals.to_pandas().set_index(index_col)


def prepare_long_data(df, index, columns, values, aggfunc='sum', orientation='h', 
                      sort='desc', n_bars=None, interpolate_period=False, 
                      steps_per_period=10, compute_ranks=True):
    '''
    Prepares 'long' data for bar chart animation. 
    Returns two DataFrames - the interpolated values and the interpolated ranks
    
    You (currently) cannot pass long data to `bar_chart_race` directly. Use this function
    to create your wide data first before passing it to `bar_chart_race`.

    Parameters
    ----------
    df : pandas DataFrame
        Must be a 'long' pandas DataFrame where one column contains 
        the period, another the categories, and the third the values 
        of each category for each period. 
        
        This DataFrame will be passed to the `pivot_table` method to turn 
        it into a wide DataFrame. It will then be passed to the 
        `prepare_wide_data` function.

    index : str
        Name of column used for the time period. It will be placed in the index

    columns : str
        Name of column containing the categories for each time period. This column
        will get pivoted so that each unique value is a column.

    values : str
        Name of column holding the values for each time period of each category.
        This column will become the values of the resulting DataFrame

    aggfunc : str or aggregation function, default 'sum'
        String name of aggregation function ('sum', 'min', 'mean', 'max, etc...) 
        or actual function (np.sum, np.min, etc...). 
        Categories that have multiple values for the same time period must be 
        aggregated for the animation to work.

    orientation : 'h' or 'v', default 'h'
        Bar orientation - horizontal or vertical

    sort : 'desc' or 'asc', default 'desc'
        Choose how to sort the bars. Use 'desc' to put largest bars on 
        top and 'asc' to place largest bars on bottom.

    n_bars : int, default None
        Choose the maximum number of bars to display on the graph.
        By default, use all bars. New bars entering the race will 
        appear from the bottom or top.

    interpolate_period : bool, default `False`
        Whether to interpolate the period. Only valid for datetime or
        numeric indexes. When set to `True`, for example, 
        the two consecutive periods 2020-03-29 and 2020-03-30 with 
        `steps_per_period` set to 4 would yield a new index of
        2020-03-29 00:00:00
        2020-03-29 06:00:00
        2020-03-29 12:00:00
        2020-03-29 18:00:00
        2020-03-30 00:00:00

    steps_per_period : int, default 10
        The number of steps to go from one time period to the next. 
        The bars will grow linearly between each period.

    compute_ranks : bool, default True
        When `True` return both the interpolated values and ranks DataFrames
        Otherwise just return the values

    Returns
    -------
    A tuple of DataFrames. The first is the interpolated values and the second
    is the interpolated ranks.

    Examples
    --------
    df_values, df_ranks = bcr.prepare_long_data(df)
    bcr.bar_chart_race(df_values, steps_per_period=1, period_length=50)
    '''
    df_wide = df.pivot_table(index=index, columns=columns, values=values, 
                             aggfunc=aggfunc).fillna(method='ffill')
    return prepare_wide_data(df_wide, orientation, sort, n_bars, interpolate_period,
                             steps_per_period, compute_ranks)


def read_images(filename, columns):
    image_dict = {}
    code_path = Path(__file__).resolve().parent / "_codes"
    code_value_path = code_path / 'code_value.csv'
    data_path = code_path / f'{filename}.csv'
    url_path = pd.read_csv(code_value_path).query('code == @filename')['value'].values[0]
    codes = pd.read_csv(data_path, index_col='code')['value'].to_dict()

    for col in columns:
        code = codes[col.lower()]
        if url_path == 'self':
            final_url = code
        else:
            final_url = url_path.format(code=code)
        image_dict[col] = mimage.imread(final_url)
    return image_dict