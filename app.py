import base64
import glob
from random import sample

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

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


app.layout = html.Div(
    children=[
        dcc.RadioItems(
            id="cat_select",
            options=categories,
            value=categories[0],
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
)


@app.callback(
    Output("text", "children"),
    Input("prev", "n_clicks"),
    Input("next", "n_clicks"),
    Input("cat_select", "value"),
    State("cat_select", "value"),
)
def show_next(
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
def show_next(text: str, category: str) -> html.Audio:
    encoded_sound = base64.b64encode(
        open(f"recordings/{category}/{text}.mp3", "rb").read()
    )
    src = f"data:audio/mpeg;base64,{encoded_sound.decode()}"
    return html.Audio(src=src, controls=True, autoPlay=True)


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
