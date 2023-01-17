import base64
import glob
from random import shuffle

import dash
from dash import html
from dash.dependencies import Input, Output

from recordingiterator import RecordingIterator

recording_paths = glob.glob("recordings/*")
recordings = [path.split("/")[1].removesuffix(".mp3") for path in recording_paths]
shuffle(recordings)


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

app.layout = html.Div(
    children=[
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
    style=dict(marginTop="200px", marginLeft="500px"),
)


@app.callback(
    Output("text", "children"),
    Input("prev", "n_clicks"),
    Input("next", "n_clicks"),
)
def show_next(prev_clicks: int, next_clicks: int) -> str:
    recit = RecordingIterator(recordings)
    if prev_clicks:
        for _ in range(prev_clicks):
            recit.forward()
    if next_clicks:
        for _ in range(next_clicks):
            recit.backward()
    return recit.get_rec()


@app.callback(Output("audio", "children"), Input("text", "children"))
def show_next(text: str) -> html.Audio:
    encoded_sound = base64.b64encode(open(f"recordings/{text}.mp3", "rb").read())
    src = f"data:audio/mpeg;base64,{encoded_sound.decode()}"
    return html.Audio(src=src, controls=True, autoPlay=True)


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
