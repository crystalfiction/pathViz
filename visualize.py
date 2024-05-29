import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import itertools
import math
from sklearn.cluster import KMeans
from parse import parse_keys
import typer

col_pal = px.colors.qualitative.Plotly
seq_col_pal = px.colors.sequential.Viridis
seq_col_pal_r = px.colors.sequential.Viridis_r
col_pal_iter = itertools.cycle(col_pal)


GOAL_KEY = {}


def get_kmeans(data):
    """
    Returns the cluster coordinates from snapshots kmeans
    """

    # prepare data
    data_prep = data[["x", "y", "z"]]

    kmeans = KMeans(n_clusters=1, n_init="auto")
    data_k = kmeans.fit(data_prep)
    cluster = data_k.cluster_centers_

    # returns the cluster coordinates from snapshots kmeans
    return cluster


def create_visuals(df, g, c, limit, orient):
    print("Creating visuals...")

    GOAL_KEY = parse_keys()

    # define plotly fig
    fig = go.Figure()

    # get unique snapshots
    uniques = df["snapshot"].unique()

    # of --limit passed
    if limit > 0:
        # if orient top
        if orient == "top":
            # slice the first n=limit snapshots
            uniques = uniques[:limit]
        else:
            # otherwise, orient bottom (default)
            uniques = uniques[-limit : len(uniques)]

    # get unique path_goals
    unique_goals = df["path_goal"].unique()
    # generate goal colors
    # plotly color palettes aren't long enough
    goal_colors = {}
    for i, u_goal in enumerate(unique_goals):
        if i < 10:
            goal_colors[u_goal] = col_pal[i]
        else:
            goal_colors[u_goal] = col_pal[i - 10]

    # for each snapshot
    traces = []
    for s in uniques:
        # cycle through trace_color iterator
        trace_color = next(col_pal_iter)

        # filter df by current grouping
        filtered = df[df["snapshot"] == s]

        # get unique path_id's from current grouping
        pid_uniques = filtered["path_id"].unique()

        # if 'c' cluster flag passed
        if c:
            # get kmeans for snapshot
            kmeans = get_kmeans(filtered)
            # create cluster trace
            trace = go.Scatter3d(
                x=[kmeans[0, 0]],
                y=[kmeans[0, 1]],
                z=[kmeans[0, 2]],
                name=str(s) + "_cluster",
                mode="markers",
                marker=dict(size=12, opacity=0.8, color=trace_color),
                legendgroup=str(s),
                legendgrouptitle_text=str(s),
            )
            traces.append(trace)

        # for each unique path_id
        for p in pid_uniques:
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
                marker=dict(
                    size=6,
                    opacity=0.5,
                    color=trace_color if not g else goal_colors[goal],
                ),
                line=dict(width=1, color=trace_color if not g else goal_colors[goal]),
                legendgroup=str(s),
                legendgrouptitle_text=str(s),
            )
            traces.append(trace)

    # add main path traces
    fig.add_traces(traces)

    camera = dict(up=dict(x=0.0, y=0.0, z=1), eye=dict(x=0.0, y=0.1, z=2))
    fig.update_layout(
        # scene_camera=dict(eye=dict(x=0.0, y=0.0, z=2.5)),
        template="plotly_dark",
        scene_camera=camera,
        scene=dict(
            xaxis=dict(nticks=6, autorange="reversed"),
            yaxis=dict(nticks=6),
            zaxis=dict(nticks=4),
        ),
    )

    # returns the plotly figure created from snapshots
    return fig


def visualize(g, c, limit, orient):
    # make sure snapshots exist
    if os.path.exists("snapshots.csv"):

        # read snapshots from snapshots.csv
        snapshots = pd.read_csv("snapshots.csv", index_col=False)

        # create visuals from snapshots
        fig = create_visuals(snapshots, g, c, limit, orient)

        # return the plotly fig
        print("Visualizing data...")
        return fig
