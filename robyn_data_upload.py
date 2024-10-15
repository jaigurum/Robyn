import streamlit as st
import os
import pandas as pd
from datetime import datetime
from PIL import Image
import json

# Set the root directory where the plots are stored
root_dir = "./mars-pne_uk"

# Title for the app
st.title("Robyn Model Output Charts Viewer")

# Get all subdirectories and files in root directory
if not os.path.exists(root_dir):
    st.error(f"The directory '{root_dir}' does not exist. Please check the path.")
else:
    sub_dirs = [f for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))]

    # Extract the datetime part from the folder names and sort by it
    folders_with_dates = []
    for folder in sub_dirs:
        try:
            # Extract timestamp from the folder name
            timestamp_str = folder.split('_')[1]
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M")
            folders_with_dates.append((folder, timestamp))
        except ValueError:
            # Skip folders that do not match the expected format
            continue

    # Sort folders by datetime in descending order (latest first)
    folders_with_dates.sort(key=lambda x: x[1], reverse=True)

    # Create a displayable label with date and time
    sorted_folders = [f"{folder} (Run on: {timestamp.strftime('%Y-%m-%d %H:%M')})" for folder, timestamp in folders_with_dates]
    folder_mapping = {f"{folder} (Run on: {timestamp.strftime('%Y-%m-%d %H:%M')})": folder for folder, timestamp in folders_with_dates}

    # Allow user to select the folder (default to the latest one)
    if sorted_folders:
        selected_label = st.selectbox("Select Model Folder (Latest First)", sorted_folders)
        selected_folder = folder_mapping[selected_label]

        folder_path = os.path.join(root_dir, selected_folder)
        available_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))]

        # Filter only the relevant chart images
        chart_files = [
            "hypersampling.png",
            "pareto_front.png",
            "prophet_decomp.png",
            "ROAS_convergence1.png",
            "ROAS_convergence2.png",
            "ROAS_convergence3.png"
        ]

        # Intersect with available files to ensure the listed files are present
        chart_files = [f for f in chart_files if f in available_files]

        # Filter model run images (files that match the format *_*_* and end with .png)
        model_run_files = [f for f in available_files if f not in chart_files and f.count('_') == 2 and f.endswith('.png')]

        # Sort model run files by modified time in ascending order (oldest first)
        model_run_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))

        # Allow user to select a chart, default to pareto_front if available
        if chart_files:
            default_chart = "pareto_front.png" if "pareto_front.png" in chart_files else chart_files[0]
            selected_chart = st.selectbox("Select a Chart to View", chart_files, index=chart_files.index(default_chart))
            if selected_chart:
                # Display the selected chart with full name in caption
                file_path = os.path.join(folder_path, selected_chart)
                image = Image.open(file_path)
                st.image(image, caption=f"{selected_chart}", use_column_width=True)

        # Allow user to select a model run, default to the oldest one
        if model_run_files:
            selected_model_run = st.selectbox("Select a Model Run to View", model_run_files, index=0)
            if selected_model_run:
                file_path = os.path.join(folder_path, selected_model_run)
                image = Image.open(file_path)
                st.image(image, caption=f"{selected_model_run}", use_column_width=True)

                # Add a checkbox to apply the selected model
                apply_model = st.checkbox("Select this model to apply")
                if apply_model:
                    model = selected_model_run.replace('.png', '')
                    st.write(f"Model {model} selected.")

                # Navigation options
                if st.button("Go to Budget Allocator"):
                    st.session_state.clear()
                    st.title("MetaRobynMMM - Budget Allocation")
                    # Full-width input fields for optimization settings
                    st.subheader("Optimization Settings")
                    st.markdown("---")
                    col_optimization, col_budget, col_date, col_plot = st.columns([1, 1, 1, 1])

                    with col_optimization:
                        st.write("**Optimization Goal**")
                        optimization_goal = st.selectbox("", ["Maximize ROAS", "Maximize Conversions", "Minimize Cost"])

                    with col_budget:
                        st.write("**Total Budget**")
                        total_budget = st.number_input("", value=7000000, step=100000)

                    with col_date:
                        st.write("**Date Range**")
                        date_range = st.date_input("", [datetime(2024, 1, 1), datetime(2024, 3, 31)])

                    with col_plot:
                        st.write("**Plot Folder Path**")
                        plot_folder = st.text_input("", "./plots")

                    # Channel Constraints
                    st.subheader("Channel Constraints")
                    st.markdown("---")
                    col_mid, col_right = st.columns([1, 1])
                    channel_constraints = {}
                    channels = [
                        "dsp_recruit_cost",
                        "dsp_conversion_cost",
                        "dsp_awareness_cost",
                        "sd_recruit_cost",
                        "sp_auto_cost",
                        "sb_defend_cost",
                        "sp_recruit_cost",
                        "sp_attack_cost",
                        "sp_defend_cost",
                        "sb_recruit_cost",
                        "sd_defend_cost",
                        "sb_attack_cost",
                        "sd_attack_cost"
                    ]

                    with col_mid:
                        st.subheader("Lower Bounds")
                        for channel in channels:
                            low_value = st.selectbox(f"{channel} - Lower Bound", [0.5, 1.0, 1.2, 1.5, 1.8])
                            channel_constraints[channel] = {"lower_bound": low_value}

                    with col_right:
                        st.subheader("Upper Bounds")
                        for channel in channels:
                            up_value = st.selectbox(f"{channel} - Upper Bound", [1.5, 2.0, 2.5, 2.8, 3.0])
                            channel_constraints[channel]["upper_bound"] = up_value

                    # Export option
                    export = st.checkbox("Export Results", value=True)

                    # Collect parameters for robyn_allocator
                    if st.button("Run Budget Allocator"):
                        st.write("Budget Allocator started...")
                        parameters = {
                            "model": model,
                            "date_range": date_range,
                            "total_budget": total_budget,
                            "channel_constraints": channel_constraints,
                            "export": export,
                            "plot_folder": plot_folder
                        }
                        st.write(f"Running robyn_allocator with the following parameters:")
                        st.json(parameters)
                        # Here you would typically run the budget allocator script
                        # os.system('python budget_alloc.py')
    else:
        st.warning("No valid folders found in the specified directory.")