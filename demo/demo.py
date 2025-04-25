import bar_chart_race as bcr
import pandas as pd
import os

csv_path = os.path.join(os.path.dirname(__file__), "computer_science_schools.csv")
df = pd.read_csv(csv_path, index_col="Date", parse_dates=True)
df.fillna(0.0, inplace=True)

bcr.bar_chart_race(
    df=df,
    filename="demo/demo.mp4",
    img_label_folder="demo/computer_science_schools",
    img_label_size=200,
    fig_kwargs={
        'figsize': (26, 15),
        'dpi': 120,
        'facecolor': '#F8FAFF'
    },
    orientation="h",
    sort="desc",
    n_bars=10,
    steps_per_period=1,           # ✅ safest value
    interpolate_period=False,     # ✅ safest config (no interpolation math involved)
    period_length=1500,
    colors=[
        '#6ECBCE', '#FF2243', '#FFC33D', '#CE9673', '#FFA0FF', '#6501E5', '#F79522',
        '#699AF8', '#34718E', '#00DBCD', '#00A3FF', '#F8A737', '#56BD5B', '#D40CE5',
        '#6936F9', '#FF317B', '#0000F3', '#FFA0A0', '#31FF83', '#0556F3'
    ],
    title={
        'label': 'Programming Language Popularity 1990 - 2020',
        'size': 52,
        'weight': 'bold',
        'pad': 40
    },
    period_label={
        'x': .95,
        'y': .15,
        'ha': 'right',
        'va': 'center',
        'size': 72,
        'weight': 'semibold'
    },
    bar_label_font={'size': 27},
    tick_label_font={'size': 27},
    bar_kwargs={'alpha': .99, 'lw': 0},
    bar_texttemplate='{x:.2f}',
    period_template='{x:.0f}',
)
