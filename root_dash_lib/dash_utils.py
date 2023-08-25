'''General-purpose functions for the dashboard.
Most functions should be useful for most datasets.
'''
import copy
import numpy as np
import os
import pandas as pd
import streamlit as st
import yaml

import matplotlib
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import seaborn as sns

################################################################################

"""
This code is a bit of a mess, but it's a good starting point for more-sophisticated utilities.
def add_panel(
        preprocessed_df,
        config,
        global_data_kw,
        global_categorical_filter_defaults,
        global_plot_kw,
        header=None,
    ):
    '''Add a generic panel to a dashboard.
    There is room to make this more flexible, but at the cost of less readability.
    If made more flexible, should likely go with a class structure to avoid passing around too many arguments.
    '''

    if header is not None:
        st.header( 'header' )

    figure_tab, data_settings_tab, figure_settings_tab = st.tabs([ 'Figure', 'Data Settings', 'Figure Settings' ])

    # Data settings tab
    with data_settings_tab:

        # Create two columns
        general_st_col, filter_st_col = st.columns( 2 )

        # Column for general settings
        with general_st_col:
            st.markdown( '#### General Settings' )

            data_kw = setup_data_axes(
                st,
                config,
            )
            recat_data_kw = setup_data_settings(
                st,
                include=[ 'recategorize', 'combine_single_categories' ],
                defaults={
                    'recategorize': True, 'combine_single_categories': True
                },
            )
            data_kw.update( recat_data_kw )
            data_kw.update( global_data_kw )

            # Then change categories if requested.
            # The new categories avoid double counting.
            recategorized_df = st.cache_data( data_utils.recategorize_data )( preprocessed_df, config['new_categories'], data_kw['recategorize'], data_kw['combine_single_categories'] )

        # Column for filters
        with filter_st_col:
            st.markdown( '#### Filter Settings' )

            categorical_filter_defaults = {}
            if data_kw['recategorize']:
                categorical_filter_defaults.update( global_categorical_filter_defaults )

            # Set up the filters
            search_str, search_col, categorical_filters, numerical_filters = dash_utils.setup_filters(
                st,
                recategorized_df,
                config,
                include_search=False,
                categorical_filter_defaults = categorical_filter_defaults,
            )

            # Apply the filters
            selected_df = st.cache_data( dash_utils.filter_data )( recategorized_df, search_str, search_col, categorical_filters, numerical_filters )

            # Retrieve counts or sums
            aggregated_df, total = st.cache_data( time_series_utils.aggregate )(
                selected_df,
                data_kw['time_bin_column'],
                data_kw['y_column'],
                data_kw['groupby_column'],
                data_kw['count_or_sum'],
            )

    with figure_settings_tab:

        lineplot_st_col, stackplot_st_col = st.columns( 2 )

        with lineplot_st_col:
            st.markdown( '#### Lineplot Settings' )

            # Settings for the lineplot
            if data_kw['cumulative']:
                default_ymax = total.sum().max() * 1.05
            else:
                default_ymax = total.values.max() * 1.05
            plot_kw = time_series_utils.setup_lineplot_settings(
                st,
                default_ymax,
                default_x_label = 'Year',
                default_y_label = 'Count of Unique Investigators',
            )
            plot_kw['category_colors'] = {
                category: global_plot_kw['color_palette'][i] for i, category in enumerate( aggregated_df.columns )
            }
            # Pull in the other dictionaries
            plot_kw.update( global_plot_kw )
            plot_kw.update( data_kw )

        with stackplot_st_col:
            st.markdown( '#### Stackplot Settings' )

            # Settings for the stackplot
            stackplot_kw = time_series_utils.setup_stackplot_settings(
                st,
                default_x_label = 'Year',
                default_y_label = 'Fraction of Unique Investigators',
            )
            stackplot_kw['category_colors'] = {
                category: global_plot_kw['color_palette'][i] for i, category in enumerate( aggregated_df.columns )
            }
            # Pull in the other dictionaries
            stackplot_kw.update( global_plot_kw )
            stackplot_kw.update( data_kw )

    with figure_tab:

        view = st.radio( 'How do you want to view the data?', [ 'lineplot', 'stackplot', 'data' ], horizontal=True )

        download_kw = st.cache_data( time_series_utils.view_time_series )(
            view,
            preprocessed_df,
            selected_df,
            aggregated_df,
            total,
            data_kw,
            plot_kw,
            stackplot_kw,
        )

        st.download_button( **download_kw )
"""