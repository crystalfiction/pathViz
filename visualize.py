import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import itertools
import math
from sklearn.cluster import KMeans
from parse import parse_keys

col_pal = px.colors.qualitative.Plotly
col_pal_iter = itertools.cycle(col_pal)


GOAL_KEY = {}


def get_kmeans(data):
    print("Evaluating snapshots...")

    # prepare data
    data_prep = data[["x", "y", "z"]]

    kmeans = KMeans(n_clusters=1, n_init="auto")
    data_k = kmeans.fit(data_prep)
    cluster = data_k.cluster_centers_

    # returns the cluster coordinates from snapshots kmeans
    return cluster


def create_visuals(df):
    print("Creating visuals...")

    GOAL_KEY = parse_keys()

    # define plotly fig
    fig = go.Figure()

    # get unique snapshots
    uniques = df["snapshot"].unique()

    # generate kmeans for plotting
    kmeans = get_kmeans(df)

    # for each snapshot
    traces = []
    for s in uniques:
        snapshot_color = next(col_pal_iter)

        # filter df by current snapshot
        filtered = df[df["snapshot"] == s]

        # get unique path_id's from current snapshot
        pid_uniques = filtered["path_id"].unique()

        # for each unique path_id
        for i, p in enumerate(pid_uniques):
            # filter df for current path
            vectors = filtered[filtered["path_id"] == p]
            # get common goal for path
            goal = vectors["path_goal"].mode()[0]
            trace = go.Scatter3d(
                x=vectors["x"],
                y=vectors["y"],
                z=vectors["z"],
                name=str(GOAL_KEY[goal]),
                mode="markers+lines",
                marker=dict(size=6, opacity=0.5, color=snapshot_color),
                line=dict(width=1, color=snapshot_color),
                legendgroup=str(s),
                legendgrouptitle_text=str(s),
            )

            traces.append(trace)

    # add main path traces
    fig.add_traces(traces)

    fig.update_layout(
        # scene_camera=dict(eye=dict(x=0.0, y=0.0, z=2.5)),
        template="plotly_dark",
        scene=dict(
            xaxis=dict(nticks=8),
            yaxis=dict(nticks=8, autorange="reversed"),
            zaxis=dict(nticks=4),
        ),
    )

    # returns the plotly figure created from snapshots
    return fig


def make_visuals():
    # make sure snapshots exist
    if os.path.exists("snapshots.csv"):

        # read snapshots from snapshots.csv
        snapshots = pd.read_csv("snapshots.csv", index_col=False)

        # create visuals from snapshots
        fig = create_visuals(snapshots)

        # return the plotly fig
        print("Visualizing data...")
        return fig
