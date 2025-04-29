# Bar Chart Race

Make animated bar and line chart races in Python with matplotlib or plotly.

Original Repo (without icons): [https://github.com/dexplo/bar_chart_race](https://github.com/dexplo/bar_chart_race)

Andres Berejnoi's Repo (with icons): [https://github.com/andresberejnoi/bar_chart_race](https://github.com/andresberejnoi/bar_chart_race)

---

## Top Computer Science Schools 2000 - 2020

![img](demo.gif)

---

## Installation

First, create a new virtual environment & activate it:

```bash
pip install virtualenv
virtualenv venv
.\venv\Scripts\activate
```

Install `bar_chart_race` using `pip`:

```bash
pip install git+https://github.com/programiz/bar_chart_race.git@master
```

---

## Additional Requirement: FFmpeg

By default, `bar_chart_race` saves animations as `.mp4` files.  
To do this, you must have **FFmpeg** installed on your system.

If FFmpeg is **not installed**, you will encounter an error like:

```
MovieWriter ffmpeg unavailable; using Pillow instead.
ValueError: unknown file extension: .mp4
```

Install FFmpeg:

- On Ubuntu / Debian:

  ```bash
  sudo apt-get update
  sudo apt-get install ffmpeg
  ```

- On macOS (with Homebrew):

  ```bash
  brew install ffmpeg
  ```

- Alternatively, download FFmpeg binaries from [here](https://github.com/BtbN/FFmpeg-Builds/releases/).

Verify installation:

```bash
ffmpeg -version
```

---

### Alternative: Save as GIF without FFmpeg

If you don't want to install FFmpeg, you can modify the output format to `.gif`, which can be saved using Pillow.

Edit your code to change the filename:

```python
bcr.bar_chart_race(
    filename="video.gif",  # Change extension from .mp4 to .gif
    ...
)
```

This allows you to create animations without requiring FFmpeg.

---

## Usage

Create a file and use the `bar_chart_race` library as shown below:

```python
import bar_chart_race as bcr
import pandas as pd

df = pd.read_csv("data.csv", index_col="Date")

# Replace empty values with 0
df.fillna(0.0, inplace=True)

# Using the bar_chart_race package
bcr.bar_chart_race(
    df=df,
    filename="video.mp4",
    img_label_folder="bar_image_labels",
    fig_kwargs={
        'figsize': (26, 15),
        'dpi': 120,
        'facecolor': '#F8FAFF'
    },
    orientation="h",
    sort="desc",
    n_bars=10,
    steps_per_period=45,
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
        'x': .95, 'y': .15,
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
```