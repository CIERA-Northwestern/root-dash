'''Module for viewing data: Plotting, tables, etc.
'''
import copy
import re
import types
from typing import Tuple

import numpy as np
import pandas as pd
import streamlit as st

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.figure

import matplotlib.patheffects as patheffects
import seaborn as sns

from .data_handler import DataHandler
from .settings import Settings

class DataViewer:
    '''Class for viewing data.

    Args:
        config: The config dictionary.
        data_handler: The data handler containing the relevant data.
    '''

    def __init__(self, config: dict, settings: Settings):
        self.config = config
        self.settings = settings

    def write(self, data, data_key: str=None, st_loc=st, columns: list[str]=None):
        '''Show a specified dataframe.

        Args:
            data: Data dict containing the data frames.
            data_key: key to search the data handler for.
                Defaults to providing a widget.
            st_loc: Where to show the data.
            columns: Columns to show. Defaults to all.
        '''

        if data_key is None:
            data_key = st_loc.radio(
                'View what data?',
                options=data.keys(),
                horizontal=True,
            )

        if data_key not in data:
            st.write('{} not found in data'.format( data_key ))
            return

        shown_df = data[data_key]
        if columns is not None:
            shown_df = shown_df[columns]

        st.write(data[data_key])

    def lineplot(
            self,
            df: pd.DataFrame,
            totals: pd.Series = None,
            categories: list[str] = None,
            cumulative: bool = False,
            x_label: str = None,
            y_label: str = None,
            fig_width: float = plt.rcParams['figure.figsize'][0] * 2,
            fig_height: float = plt.rcParams['figure.figsize'][1],
            yscale: str = 'linear',
            x_lim: Tuple[float, float] = None,
            y_lim: Tuple[float, float] = None,
            xtick_spacing: float = None,
            ytick_spacing: float = None,
            font_scale: float = 1.,
            linewidth: float = 2.,
            marker_size: float = 30.,
            category_colors: dict[str,str] = None,
            seaborn_style: str = 'whitegrid',
            include_legend: bool = True,
            legend_x: float = 1.,
            legend_y: float = 1.,
            legend_loc: str = 'lower right',
            legend_scale: float = 1.,
            include_annotations: bool = False,
            annotations_ha: str = 'left',
            **kwargs
        ) -> matplotlib.figure.Figure:
        '''General-purpose matplotlib lineplot.
        This function provides solid defaults with a lot of customization.
        If you want more customization you should probably create your own
        situation-dependent function.

        Args:
            df: Dataframe to plot, formatted s.t. the x-values are the index,
                the y-values are the values in the dataframe,
                and each column is a different category to compare.
            total: Total values (across all categories) to plot, if given.
            categories: Categories to show. Defaults to all columns.
            cumulative: If True, show cumulative quantities, not instantaneous.
            x_label: Label for x axis. If not provided, not shown.
            y_label: Label for y axis. If not provided, not shown.
            fig_width: Figure width.
            fig_height: Figure height.
            yscale: Scale for axis, i.e. 'linear', 'log'.
            x_lim: x-axis limits.
            y_lim: y-axis limits.
            xtick_spacing: Distance (in data units) between x ticks.
            ytick_spacing: Distance (in data units) between y ticks.
            font_scale: Fonts are multiplied by this number (keeping relative size).
            linewidth: Line thickness.
            marker_size: Marker size.
            category_colors: Colors to use for the different categories.
                Defaults to using the seaborn color palette.
            seaborn_style: Seaborn style to use.
            include_legend: Whether to add a legend or not.
            legend_x: Legend x location (axis units).
            legend_y: Legend y location (axis units).
            legend_loc: Legend alignment.
            legend_scale: The legend size is multiplied by this number.
            include_annotations: Whether to annotate the individual lines
                with the category names.
            annotation_ha: Horizontal alignment for the annotations.

        Returns:
            fig: The figure containing the plot.
        '''

        # Modify data if cumulative
        if cumulative:
            df = df.cumsum( axis='rows' )
            if totals is not None:
                totals = totals.cumsum()

        # Set defaults
        xs = df.index
        if categories is None:
            categories = df.columns
        if category_colors is None:
            color_palette = sns.color_palette()
            category_colors = { key: color_palette[i] for i, key in enumerate( categories ) }

        sns.set(style=seaborn_style)
        plot_context = sns.plotting_context("notebook")

        fig = plt.figure(figsize=(fig_width, fig_height))
        ax = plt.gca()
        for j, category_j in enumerate( categories ):

            ys = df[category_j]

            ax.plot(
                xs,
                ys,
                linewidth = linewidth,
                alpha = 0.5,
                zorder = 2,
                color = category_colors[category_j],
            )
            ax.scatter(
                xs,
                ys,
                label = category_j,
                zorder = 2,
                color = category_colors[category_j],
                s = marker_size,
                )

            # Add labels
            if include_annotations:
                label_y = ys.iloc[-1]

                text = ax.annotate(
                    text = category_j,
                    xy = (1, label_y),
                    xycoords = matplotlib.transforms.blended_transform_factory( ax.transAxes, ax.transData ),
                    xytext = (-5 + 10 * ( annotations_ha == 'left'), 0),
                    va = 'center',
                    ha = annotations_ha,
                    textcoords = 'offset points',
                )
                text.set_path_effects([
                    patheffects.Stroke(linewidth=2.5, foreground='w'),
                    patheffects.Normal(),
                ])

        if totals is not None:
            ax.plot(
                xs,
                totals,
                linewidth = linewidth,
                alpha = 0.5,
                color = 'k',
                zorder = 1,
            )
            ax.scatter(
                xs,
                totals,
                label = 'Total',
                color = 'k',
                zorder = 1,
                s = marker_size,
            )

        ax.set_yscale(yscale)

        # Limits
        if x_lim is None:
            x_lim = ax.get_xlim()
        else:
            ax.set_xlim(x_lim)
        if y_lim is None:
            y_lim = ax.get_ylim()
        else:
            ax.set_ylim(y_lim)

        # Ticks
        if xtick_spacing is None:
            ax.set_xticks(xs.astype(int))
        else:
            count_ticks = np.arange(x_lim[0], x_lim[1], xtick_spacing)
            ax.set_xticks(count_ticks)
        if ytick_spacing is not None:
            count_ticks = np.arange(y_lim[0], y_lim[1], ytick_spacing)
            ax.set_yticks(count_ticks)

        if include_legend:
            l = ax.legend(
                bbox_to_anchor = (legend_x, legend_y),
                loc = legend_loc,
                framealpha = 1.,
                fontsize = plot_context['legend.fontsize'] * legend_scale,
                ncol = len( categories ) // 4 + 1
            )

        # Labels, inc. size
        if x_label is not None:
            ax.set_xlabel(x_label, fontsize=plot_context['axes.labelsize'] * font_scale)
        if y_label is not None:
            ax.set_ylabel(y_label, fontsize=plot_context['axes.labelsize'] * font_scale)
        ax.tick_params(labelsize=plot_context['xtick.labelsize'] * font_scale)

        # Show
        st.write(fig)

        # return facet_grid
        return fig


def get_tick_range_and_spacing( total, cumulative, ax_frac=0.1 ):
    '''Solid defaults for ymax and the tick_spacing.

    Args:
        total (pd.Series): The total counts or sums.
        cumulative (bool): Whether the data is cumulative.
        ax_frac (float): Fraction of axis between ticks.

    Returns:
        ymax (float): The maximum y value.
        tick_spacing (float): The spacing between ticks.
    '''

    # Settings for the lineplot
    if cumulative:
        ymax = total.sum().max() * 1.05
    else:
        ymax = total.values.max() * 1.05

    # Round the tick spacing to a nice number
    unrounded_tick_spacing = ax_frac * ymax
    tick_spacing = np.round( unrounded_tick_spacing, -np.floor(np.log10(unrounded_tick_spacing)).astype(int) )

    return ymax, tick_spacing
