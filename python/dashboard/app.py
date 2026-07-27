import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import requests

app = dash.Dash(__name__)
API = "http://localhost:8000"

app.layout = html.Div([
    html.H1("COVID-19 Data Platform"),
    dcc.Dropdown(id="country", options=[
        {"label": c, "value": c} for c in ["Lithuania", "Germany", "United States", "Sweden", "Poland"]
    ], value="Lithuania"),
    dcc.Graph(id="cases-graph"),
    dcc.Graph(id="deaths-graph"),
    dcc.Graph(id="forecast-graph"),
    html.H3("Add annotation"),
    dcc.Textarea(id="comment-box", placeholder="Add a note about this country's trend..."),
    html.Button("Save", id="save-btn"),
    html.Div(id="save-status"),
    html.Div(id="annotations-list")
])

@app.callback(Output("cases-graph", "figure"), Output("deaths-graph", "figure"), Output("forecast-graph", "figure"), Output("annotations-list", "children"),
    Input("country", "value"),
)
def update_graphs(country):
    data = requests.get(f"{API}/metrics", params={"country": country}).json()
    fig1 = px.line(data, x="DATE", y="cases_per_100k", title=f"Cases per 100k — {country}")
    fig2 = px.line(data, x="DATE", y="deaths_per_100k", title=f"Deaths per 100k — {country}")
    forecast_data = requests.get(f"{API}/forecast", params={"country": country}).json()
    fig3 = px.line(forecast_data, x="ds", y="yhat", title=f"30-Day Case Forecast — {country}")
    annos = requests.get(f"{API}/annotations", params={"country": country}).json()
    anno_list = html.Ul([html.Li(a.get("comment", "")) for a in annos]) if annos else html.P("No annotations yet.")

    return fig1, fig2, fig3, anno_list

@app.callback(Output("save-status", "children"), Input("save-btn", "n_clicks"), State("comment-box", "value"), State("country", "value"),
    prevent_initial_call=True,
)
def save_comment(n, comment, country):
    requests.post(f"{API}/annotations", json={"country_region": country, "comment": comment, "metric": "cases"})
    return "Saved!"

if __name__ == "__main__":
    app.run(debug=True, port=8050)