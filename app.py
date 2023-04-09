import base64
import glob
from pathlib import Path
from random import sample

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from typing import Optional
from unidecode import unidecode

from recordingiterator import RecordingIterator


categories = [path.removeprefix("recordings/") for path in glob.glob("recordings/*")]
get_recordings = lambda category: glob.glob(f"recordings/{category}/*")
shuffle_list = lambda l: sample(l, len(l))
recording_dict = {
    category: shuffle_list(
        [path.split("/")[-1].removesuffix(".mp3") for path in get_recordings(category)]
    )
    for category in categories
}


def find_recording(category: str, prev_clicks: int, next_clicks: int) -> tuple:
    recit = RecordingIterator(recording_dict[category])
    if prev_clicks:
        for _ in range(prev_clicks):
            recit.forward()
    if next_clicks:
        for _ in range(next_clicks):
            recit.backward()
    rec_title = recit.get_rec()
    encoded_sound = base64.b64encode(
        Path(f"recordings/{category}/{rec_title}.mp3").read_bytes()
    )
    src = f"data:audio/mpeg;base64,{encoded_sound.decode()}"
    return rec_title, src


app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://codepen.io/chriddyp/pen/bWLwgP.css",
        "https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css",
    ],
    external_scripts=[
        "https://code.jquery.com/jquery-3.5.1.slim.min.js",
        "https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js",
    ],
    suppress_callback_exceptions=True,
)

default_margin = dict(marginBottom="50px")

default_text_component = lambda *args, **kwargs: html.H3(
    *args, style=dict(fontSize=20, **default_margin), **kwargs
)


category_selector = dcc.RadioItems(
    id="cat_select",
    options=[c for c in categories if (c != "for_typing")],
    value=categories[1],
    labelStyle=dict(display="block"),
    inputStyle={"margin-right": "20px"},
    style=dict(width="1000px", marginBottom="100px"),
)

audio_component = lambda exercise_type: html.Audio(
    id=f"audio_{exercise_type}",
    controls=True,
    autoPlay=True,
    style=default_margin,
)

paging_buttons = lambda exercise_type: html.Div(
    children=[
        html.Button("← előző", id=f"prev_{exercise_type}"),
        html.Button(
            "következő →",
            id=f"next_{exercise_type}",
            style=dict(marginLeft="50px"),
        ),
    ],
)

letter_tiles = html.Div(
    children=[
        default_text_component("Kattints a segítségért:"),
        *[
            html.Button(
                id=f"letter_{i}",
                style=dict(
                    marginRight="10px",
                    fontSize=20,
                ),
            )
            for i in range(10)
        ],
    ],
    style=default_margin,
)

typing_input = dcc.Input(
    id="typed",
    style=dict(
        width="500px",
        fontSize=30,
        **default_margin,
    ),
)

check_button = html.Button(
    "ellenőrzés",
    id="check_typed",
    style=dict(fontSize=20),
)

tab_style = dict(marginTop="100px", marginLeft="400px")

speech_exercise_tab = dcc.Tab(
    label="beszédgyakorlat",
    children=html.Div(
        children=[
            category_selector,
            default_text_component(id="text_speech"),
            audio_component("speech"),
            paging_buttons("speech"),
        ],
        style=tab_style,
    ),
)


typing_exercise_tab = dcc.Tab(
    label="gépelés gyakorlat",
    children=html.Div(
        children=[
            audio_component("typing"),
            letter_tiles,
            default_text_component("Ide írd a megoldást:"),
            typing_input,
            check_button,
            default_text_component(id="feedback"),
            paging_buttons("typing"),
        ],
        style=tab_style,
    ),
)


app.layout = dcc.Tabs(
    children=[speech_exercise_tab, typing_exercise_tab],
    style=dict(fontSize=20),
)


@app.callback(
    Output("text_speech", "children"),
    Output("audio_speech", "src"),
    Input("cat_select", "value"),
    Input("prev_speech", "n_clicks"),
    Input("next_speech", "n_clicks"),
)
def show_next_speech(
    selected_cat: str,
    prev_clicks: int,
    next_clicks: int,
) -> tuple:
    return find_recording(selected_cat, prev_clicks, next_clicks)


@app.callback(
    Output("audio_typing", "title"),
    Output("audio_typing", "src"),
    Output("typed", "value"),
    Output("check_typed", "n_clicks"),
    Input("prev_typing", "n_clicks"),
    Input("next_typing", "n_clicks"),
)
def show_next_typing(prev_clicks: int, next_clicks: int) -> tuple:
    return (*find_recording("for_typing", prev_clicks, next_clicks), "", 0)


@app.callback(
    Output("feedback", "children"),
    Input("check_typed", "n_clicks"),
    State("typed", "value"),
    State("audio_typing", "title"),
)
def check_typed(n_clicks: int, typed: str, correct: str) -> Optional[str]:
    if n_clicks:
        return (
            "Írj be valamit!"
            if not typed
            else "Helyes megoldás!"
            if (unidecode(typed.lower().strip()) == unidecode(correct.lower().strip()))
            else "Próbáld újra!"
        )


@app.callback(
    *[Output(f"letter_{i}", "hidden") for i in range(10)],
    *[Output(f"letter_{i}", "n_clicks") for i in range(10)],
    Input("audio_typing", "title"),
)
def show_letter_tiles(text: str) -> tuple:
    return [
        *[False for _ in text],
        *[True for _ in range(10 - len(text))],
        *[0 for _ in range(10)],
    ]


@app.callback(
    *[Output(f"letter_{i}", "children") for i in range(10)],
    *[Input(f"letter_{i}", "n_clicks") for i in range(10)],
    State("audio_typing", "title"),
)
def reveal_letter(*args) -> list:
    n_clicks_list = args[:10]
    text = args[-1]
    return [
        text[i] if n_clicks & (i < len(text)) else ""
        for i, n_clicks in enumerate(n_clicks_list)
    ]


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
