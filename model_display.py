import streamlit as st
import os
import pandas as pd
from datetime import datetime
from PIL import Image
import json
import matplotlib.pyplot as plt
import streamlit as st
import budget_allocate

def run_model_display():
    st.write("This is the model display page")
    # Set the root directory where the plots are stored
    root_dir = "./mars-pne_uk"

    # Title for the app
    st.title("Robyn Model Output Charts Viewer")

    # Initialize session state attributes if not already set
    if 'allocation_params' not in st.session_state:
        st.session_state.allocation_params = None
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None
    if 'view_allocation' not in st.session_state:
        st.session_state.view_allocation = False

    # Initialize sorted_folders to avoid undefined errors
    sorted_folders = []

    # Function to display budget allocation results
    def display_budget_allocation_results():
        st.write("---")
        st.title("Budget Allocation Results")
        allocation_params = st.session_state.allocation_params
        csv_path = os.path.join(root_dir, allocation_params['model'], "5_228_6_max_response_reallocated.csv")
        if os.path.exists(csv_path):
            results_df = pd.read_csv(csv_path)
            st.dataframe(results_df)
        else:
            st.error(f"The results file '{csv_path}' does not exist.")

        # Clear allocation parameters if needed
        if st.button("Back to Chart Selection"):
            st.session_state.view_allocation = False
            st.session_state.selected_model = None
    

    # Check if we need to display allocation results
    if st.session_state.view_allocation and st.session_state.allocation_params:
        display_budget_allocation_results()
    else:
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
                selected_label = st.selectbox("Select Model Folder (Latest First)", sorted_folders, index=0)
                selected_folder = folder_mapping[selected_label]
                st.session_state.selected_folder = selected_folder

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
                        try:
                            file_path = os.path.join(folder_path, selected_chart)
                            image = Image.open(file_path)
                            st.image(image, caption=f"{selected_chart}", use_column_width=True)
                        except Exception as e:
                            st.error(f"Error loading image {selected_chart}: {str(e)}")

                # Allow user to select a model run, default to the oldest one
                if model_run_files:
                    selected_model_run = st.selectbox("Select a Model Run to View", model_run_files, index=0)
                    if selected_model_run:
                        try:
                            file_path = os.path.join(folder_path, selected_model_run)
                            image = Image.open(file_path)
                            st.image(image, caption=f"{selected_model_run}", use_column_width=True)
                        except Exception as e:
                            st.error(f"Error loading model run image {selected_model_run}: {str(e)}")

                        # Add a checkbox to apply the selected model
                        if st.session_state.selected_model is None:
                            apply_model = st.checkbox("Select this model to apply", key='apply_model')
                            if apply_model:
                                st.session_state.selected_model = selected_model_run.replace('.png', '')
                                st.write(f"Model {st.session_state.selected_model} selected.")

                        # Directly show budget allocation parameters if model is selected
                        if st.session_state.selected_model == selected_model_run.replace('.png', ''):
                            st.header("Budget Allocator using selected Model")
                            st.subheader("Channel Constraints")
                            channel_constraints = {}
                            channels = [
                                "dsp_recruit_cost", "dsp_conversion_cost", "dsp_awareness_cost",
                                "sd_recruit_cost", "sp_auto_cost", "sb_defend_cost",
                                "sp_recruit_cost", "sp_attack_cost", "sp_defend_cost",
                                "sb_recruit_cost", "sd_defend_cost", "sb_attack_cost",
                                "sd_attack_cost"
                            ]

                            for channel in channels:
                                col1, col2 = st.columns(2)
                                with col1:
                                    low_value = st.selectbox(f"{channel} - Lower Bound", [0.5, 1.0, 1.2, 1.5, 1.8], key=f"{channel}_low")
                                with col2:
                                    up_value = st.selectbox(f"{channel} - Upper Bound", [1.5, 2.0, 2.5, 2.8, 3.0], key=f"{channel}_up")
                                channel_constraints[channel] = {"lower_bound": low_value, "upper_bound": up_value}

                            # Other parameters
                            total_budget = st.number_input("Total Budget", value=7000000, step=100000)
                            date_range = st.date_input("Date Range", [datetime(2024, 1, 1), datetime(2024, 3, 31)])
                            plot_folder = st.text_input("Plot Folder Path", "./plots")
                            export = st.checkbox("Export Results", value=True)

                            if st.button("Confirm and Run Budget Allocator"):
                            
                                    parameters = {
                                        "model": st.session_state.selected_model,
                                        "date_range": [d.strftime("%Y-%m-%d") for d in date_range],
                                        "total_budget": total_budget,
                                        "channel_constraints": channel_constraints,
                                        "export": export
                                    }


                                    # Export parameters to a JSON file
                                    json_file_path = os.path.join("allocation_params.json")
                                    with open(json_file_path, 'w') as json_file:
                                        json.dump(parameters, json_file, indent=4)
                                    st.success(f"Parameters exported to {json_file_path}")
                                    budget_allocate.run_budget_allocate()

                                    # Display the results immediately after exporting
                                    
