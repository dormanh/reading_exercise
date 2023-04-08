import base64
import glob
from random import sample

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from typing import Optional

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


app.layout = dcc.Tabs(
    children=[
        dcc.Tab(
            label="beszédgyakorlat",
            children=html.Div(
                children=[
                    dcc.RadioItems(
                        id="cat_select",
                        options=[c for c in categories if (c != "for_typing")],
                        value=categories[1],
                        labelStyle=dict(display="block"),
                        inputStyle={"margin-right": "20px"},
                        style=dict(
                            fontSize=20,
                            width="1000px",
                            marginLeft="-100px",
                            marginBottom="100px",
                        ),
                    ),
                    html.H1(id="text", style=dict(fontSize=40, marginBottom="50px")),
                    html.Div(id="audio", style=dict(marginBottom="50px")),
                    html.Div(
                        children=[
                            html.Button("← előző", id="prev"),
                            html.Button(
                                "következő →",
                                id="next",
                                style=dict(marginLeft="50px"),
                            ),
                        ],
                        style=dict(fontSize=20),
                    ),
                ],
                style=dict(marginTop="100px", marginLeft="500px"),
            ),
        ),
        dcc.Tab(
            label="gépelés gyakorlat",
            children=html.Div(
                children=[
                    html.Audio(
                        id="audio_typing",
                        controls=True,
                        autoPlay=True,
                        style=dict(marginBottom="50px"),
                    ),
                    html.H3(
                        "Ide írd a megoldást:",
                        style=dict(
                            fontSize=30,
                            marginTop="20px",
                            marginLeft="-100px",
                        ),
                    ),
                    html.Div(
                        children=[
                            dcc.Input(
                                id="typed",
                                style=dict(
                                    width="500px",
                                    fontSize=30,
                                    marginRight="20px",
                                    marginLeft="-100px",
                                ),
                            ),
                            html.Button(
                                "ellenőrzés",
                                id="check_typed",
                                style=dict(fontSize=20),
                            ),
                            html.H3(
                                id="feedback",
                                style=dict(
                                    fontSize=30,
                                    marginLeft="-100px",
                                    marginTop="20px",
                                ),
                            ),
                        ],
                        style=dict(marginBottom="100px"),
                    ),
                    html.Div(
                        children=[
                            html.Button("← előző", id="prev_typing"),
                            html.Button(
                                "következő →",
                                id="next_typing",
                                style=dict(marginLeft="50px"),
                            ),
                        ],
                        style=dict(fontSize=20),
                    ),
                ],
                style=dict(marginTop="100px", marginLeft="500px"),
            ),
        ),
    ],
    style=dict(fontSize=20),
)


@app.callback(
    Output("text", "children"),
    Input("prev", "n_clicks"),
    Input("next", "n_clicks"),
    Input("cat_select", "value"),
    State("cat_select", "value"),
)
def show_next_text(
    prev_clicks: int,
    next_clicks: int,
    _: str,
    current_cat: str,
) -> str:
    recit = RecordingIterator(recording_dict[current_cat])
    if prev_clicks:
        for _ in range(prev_clicks):
            recit.forward()
    if next_clicks:
        for _ in range(next_clicks):
            recit.backward()
    return recit.get_rec()


@app.callback(
    Output("audio", "children"),
    Input("text", "children"),
    State("cat_select", "value"),
)
def show_next_audio(text: str, category: str) -> html.Audio:
    encoded_sound = base64.b64encode(
        open(f"recordings/{category}/{text}.mp3", "rb").read()
    )
    src = f"data:audio/mpeg;base64,{encoded_sound.decode()}"
    return html.Audio(src=src, controls=True, autoPlay=True)


@app.callback(
    Output("audio_typing", "src"),
    Output("audio_typing", "title"),
    Output("typed", "value"),
    Output("check_typed", "n_clicks"),
    Input("prev_typing", "n_clicks"),
    Input("next_typing", "n_clicks"),
)
def show_next_typing(prev_clicks: int, next_clicks: int) -> tuple:
    recit = RecordingIterator(recording_dict["for_typing"])
    if prev_clicks:
        for _ in range(prev_clicks):
            recit.forward()
    if next_clicks:
        for _ in range(next_clicks):
            recit.backward()
    recording = recit.get_rec()
    encoded_sound = base64.b64encode(
        open(f"recordings/for_typing/{recording}.mp3", "rb").read()
    )
    src = f"data:audio/mpeg;base64,{encoded_sound.decode()}"
    return src, recording, "", 0


@app.callback(
    Output("feedback", "children"),
    Input("check_typed", "n_clicks"),
    State("typed", "value"),
    State("audio_typing", "title"),
)
def show_result(n_clicks: int, typed: str, correct: str) -> Optional[str]:
    if n_clicks:
        return (
            "Írj be valamit!"
            if not typed
            else "Helyes megoldás!"
            if (typed.lower() == correct.lower())
            else "Próbáld újra!"
        )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
