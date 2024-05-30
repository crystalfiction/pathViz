import os
import pandas as pd
from pandas import DataFrame
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import itertools

from utils import parse_keys, get_kmeans, get_density

col_pal = px.colors.qualitative.Plotly
seq_col_pal = px.colors.sequential.Viridis
seq_col_pal_r = px.colors.sequential.Viridis_r
col_pal_iter = itertools.cycle(col_pal)


GOAL_KEY = {}


def visualize(g: bool, c: bool, heat: bool, limit: int, orient: str):
    """
    Reads snapshot data and creates visuals depending on
    passed options.

    Returns fig as type plotly Figure
    """
    # make sure snapshots exist
    if os.path.exists("snapshots.csv"):

        # read snapshots from snapshots.csv
        snapshots = pd.read_csv("snapshots.csv", index_col=False).drop(
            columns=["Unnamed: 0"]
        )

        # null fig for flagging
        fig = None
        # if --limit 1 was passed, return error
        if limit == 1:
            return print("Limiting does not currently support --limit=1")

        # if --c was passed, return error
        # check if heat option passed
        if heat:
            if c:
                return print("Heatmap does not support clustering.")
            # if heat create heatmap visual from snapshots
            fig = create_heatmap(snapshots, g, limit, orient)
        else:
            # create scatter visual from snapshots
            fig = create_scatter(snapshots, g, c, limit, orient)

        # return the plotly fig
        return fig


def create_scatter(df: DataFrame, g: bool, c: bool, limit: int, orient: str):
    """
    Processes passed df data and options & creates plotly visual

    Returns fig as type plotly Figure
    """
    print("Creating visuals...")

    # parse the path_goals defined in goals_key.xml
    GOAL_KEY = parse_keys()

    # define plotly fig
    fig = go.Figure()

    # get unique snapshot names
    uniques = df["snapshot"].unique()

    # if --limit passed...
    if limit > 0:
        # TODO: account for limit=1

        # check if --orient option passed...
        # defaults to "btm"
        if orient == "top":
            # if option passed
            # slice the first n=limit snapshots
            uniques = uniques[:limit]
        elif orient == "btm":
            # else slice the last n=limit snapshots
            uniques = uniques[-limit : len(uniques)]

    # get unique path_goals
    unique_goals = df["path_goal"].unique()

    # TODO: remap goal color palette according to goal priority
    # since plotly color palettes length = 10,
    # we reindex the goals using only goals in this snapshot,
    # but preserve the unique 'gid' specified by DF data structures

    # create a goal_colors dict for use with --g option
    goal_colors = {}
    # for each unique goal in snapshot collection...
    for i, gid in enumerate(unique_goals):
        # if index < 10 (plotly color palette length)
        if i < 10:
            # add entry to goal_colors where
            # key: gid (goal id)
            # value: color hex code at index i of col_pal
            goal_colors[gid] = col_pal[i]
        else:
            # if gid out of col_pal index range...
            # 'reset' i to 0 and add entry
            goal_colors[gid] = col_pal[i - 10]

    # to be used as final traces list
    traces = []
    # for each snapshot id in uniques
    for sid in uniques:
        # cycle through trace_color iterator
        trace_color = next(col_pal_iter)

        # filter df by current sid
        filtered = df[df["snapshot"] == sid]

        # get unique path_id's from snapshot
        pid_uniques = filtered["path_id"].unique()

        # if 'c' cluster flag passed...
        # process the cluster in the snapshot loop,
        # 1 cluster trace per snapshot
        if c:
            # get kmeans for snapshot
            cluster_center, inertia = get_kmeans(filtered)
            # rename x,y,z coordinates
            kmeans_x = cluster_center[0, 0]
            kmeans_y = cluster_center[0, 1]
            kmeans_z = cluster_center[0, 2]

            # create cluster trace
            trace = go.Scatter3d(
                x=[kmeans_x],
                y=[kmeans_y],
                z=[kmeans_z],
                name=str(sid) + "_cluster",
                mode="markers",
                marker=dict(
                    size=12,
                    opacity=1,
                    color=trace_color,
                ),
                legendgroup=str(sid),
                legendgrouptitle_text=str(sid),
            )
            # append to traces list
            traces.append(trace)

        # for each unique pid in snapshot...
        for pid in pid_uniques:
            # filter df for current pid
            vectors = filtered[filtered["path_id"] == pid]
            # get the common goal for this path
            goal = vectors["path_goal"].mode()[0]
            # create the path trace
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
                legendgroup=str(sid),
                legendgrouptitle_text=str(sid),
            )
            # append to traces list
            traces.append(trace)

    # add all traces in traces list to fig
    fig.add_traces(traces)

    # adjust the camera perspective
    camera = dict(up=dict(x=0.0, y=0.0, z=1), eye=dict(x=0.0, y=0.1, z=2))

    # make final layout updates
    fig.update_layout(
        template="plotly_dark",
        scene_camera=camera,
        scene=dict(
            xaxis=dict(nticks=6, autorange="reversed"),
            yaxis=dict(nticks=6),
            zaxis=dict(nticks=4),
        ),
    )

    # return the figure
    return fig


def create_heatmap(df: DataFrame, g: bool, limit: int, orient: str):
    """ """
    print("Creating visuals...")

    # parse the path_goals defined in goals_key.xml
    GOAL_KEY = parse_keys()

    # define plotly fig
    fig = go.Figure()

    # perform kneighbors on df
    heat_df = get_density(df)
    if heat_df is None:
        return

    # get unique path_id's
    uniques = heat_df["path_id"].unique()

    # if --limit passed...
    if limit > 0:
        # TODO: account for limit=1

        # check if --orient option passed...
        # defaults to "btm"
        if orient == "top":
            # if option passed
            # slice the first n=limit snapshots
            uniques = uniques[:limit]
        elif orient == "btm":
            # else slice the last n=limit snapshots
            uniques = uniques[-limit : len(uniques)]

    # get unique path_goals
    unique_goals = heat_df["path_goal"].unique()

    # TODO: remap goal color palette according to goal priority
    # since plotly color palettes length = 10,
    # we reindex the goals using only goals in this snapshot,
    # but preserve the unique 'gid' specified by DF data structures

    # create a goal_colors dict for use with --g option
    goal_colors = {}
    # for each unique goal in snapshot collection...
    for i, gid in enumerate(unique_goals):
        # if index < 10 (plotly color palette length)
        if i < 10:
            # add entry to goal_colors where
            # key: gid (goal id)
            # value: color hex code at index i of col_pal
            goal_colors[gid] = col_pal[i]
        else:
            # if gid out of col_pal index range...
            # 'reset' i to 0 and add entry
            goal_colors[gid] = col_pal[i - 10]

    # to be used as final traces list
    traces = []
    # for unique path_ids
    for pid in uniques:
        # filter df by current pid
        vectors = heat_df[heat_df["path_id"] == pid]
        # get the common goal for this path
        goal = vectors["path_goal"].mode()[0]
        # create the path trace
        trace = go.Scatter3d(
            x=vectors["x"],
            y=vectors["y"],
            z=vectors["z"],
            name=str(GOAL_KEY[goal]),
            mode="markers+lines",
            legendgroup=str(pid),
            legendgrouptitle_text=str(pid),
        )
        # append to traces list
        traces.append(trace)

    # add all traces in traces list to fig
    fig.add_traces(traces)
    fig.update_traces(
        overwrite=True,
        marker=dict(
            size=6, opacity=0.5, color=heat_df["n_density"], colorscale="Inferno_r"
        ),
        line=dict(width=1, color=heat_df["n_density"], colorscale="Inferno_r"),
    )

    # adjust the camera perspective
    camera = dict(up=dict(x=0.0, y=0.0, z=1), eye=dict(x=0.0, y=0.1, z=2))

    # make final layout updates
    fig.update_layout(
        template="plotly_dark",
        scene_camera=camera,
        scene=dict(
            xaxis=dict(nticks=6, autorange="reversed"),
            yaxis=dict(nticks=6),
            zaxis=dict(nticks=4),
        ),
    )

    # return the figure
    return fig
