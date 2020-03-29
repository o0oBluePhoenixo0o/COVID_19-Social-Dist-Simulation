import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


TEMPLATE = "plotly_white"
_SUSCEPTIBLE_COLOR = "rgba(230,230,230,.4)"
_RECOVERED_COLOR = "rgba(180,200,180,.4)"

COLOR_MAP = {
    "default": "#262730",
    "pink": "#E22A5B",
    "purple": "#985FFF",
    "susceptible": _SUSCEPTIBLE_COLOR,
    "recovered": _RECOVERED_COLOR,} 

def _set_legends(fig):
    fig.layout.update(legend=dict(x=-0.1, y=1.2))
    fig.layout.update(legend_orientation="h")


def plot_historical_data(df):
    fig = px.line(
        df, x="Date", y="Number", color="Status", template=TEMPLATE
    )
    
    fig.layout.update(
        xaxis_title="Date",
        font=dict(family="Arial", size=12))
    
    _set_legends(fig)

    return fig


def num_beds_occupancy_comparison_chart(num_beds_available, max_num_beds_needed):
    """
    A horizontal bar chart comparing # of beds available compared to 
    max number number of beds needed
    """
    num_beds_available, max_num_beds_needed = (
        int(num_beds_available),
        int(max_num_beds_needed),
    )

    df = pd.DataFrame(
        {
            "Label": ["Total Beds ", "Peak Occupancy "],
            "Value": [num_beds_available, max_num_beds_needed],
            "Text": [f"{num_beds_available:,}  ", f"{max_num_beds_needed:,}  "],
            "Color": ["b", "r"],
        }
    )
    fig = px.bar(
        df,
        x="Value",
        y="Label",
        color="Color",
        text="Text",
        orientation="h",
        opacity=0.7,
        template=TEMPLATE,
        height=300,
    )

    fig.layout.update(
        showlegend=False,
        xaxis_title="",
        xaxis_showticklabels=False,
        yaxis_title="",
        yaxis_showticklabels=True,
        font=dict(family="Arial", size=15, color=COLOR_MAP["default"]),
    )
    fig.update_traces(textposition="outside", cliponaxis=False)

    return fig