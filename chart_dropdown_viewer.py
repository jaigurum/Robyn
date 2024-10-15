import streamlit as st
import os
from datetime import datetime
from PIL import Image

# Set the root directory where the plots are stored
root_dir = "./mars-pne_uk"

# Title for the app
st.title("Robyn Model Output Charts Viewer")

# Navigation state
if 'navigate_to_allocator' not in st.session_state:
    st.session_state['navigate_to_allocator'] = False

# Get all subdirectories and files in root directory
sub_dirs = [f for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))]

# Extract the datetime part from the folder names and sort by it
folders_with_dates = []
for folder in sub_dirs:
    try:
        timestamp_str = folder.split('_')[1]
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M")
        folders_with_dates.append((folder, timestamp))
    except ValueError:
        continue

folders_with_dates.sort(key=lambda x: x[1], reverse=True)
sorted_folders = [f"{folder} (Run on: {timestamp.strftime('%Y-%m-%d %H:%M')})" for folder, timestamp in folders_with_dates]
folder_mapping = {f"{folder} (Run on: {timestamp.strftime('%Y-%m-%d %H:%M')})": folder for folder, timestamp in folders_with_dates}

selected_label = st.selectbox("Select Model Folder (Latest First)", sorted_folders)
selected_folder = folder_mapping[selected_label]

if selected_folder:
    folder_path = os.path.join(root_dir, selected_folder)
    available_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))]
    chart_files = [f for f in available_files if "pareto_front" in f or "hypersampling" in f]  # Filtered files for selection

    if chart_files:
        selected_chart = st.selectbox("Select a Chart to View", chart_files)
        file_path = os.path.join(folder_path, selected_chart)
        image = Image.open(file_path)
        st.image(image, caption=f"{selected_chart}", use_column_width=True)

    model_run_files = [f for f in available_files if f not in chart_files and f.endswith('.png')]
    model = None
    if model_run_files:
        selected_model_run = st.selectbox("Select a Model Run to View", model_run_files, index=0)
        if selected_model_run:
            file_path = os.path.join(folder_path, selected_model_run)
            image = Image.open(file_path)
            st.image(image, caption=f"{selected_model_run}", use_column_width=True)

            apply_model = st.checkbox("Selected model to apply")
            if apply_model:
                model = selected_model_run.replace('.png', '')
                st.session_state['selected_model'] = model
                st.write(f"Model {model} selected. You can now navigate to the budget allocator.")

    if model and st.button("Go to Budget Allocator", key="go_budget_allocator"):
        st.session_state['navigate_to_allocator'] = True
        st.experimental_rerun()  # To update the state and navigate

if st.session_state['navigate_to_allocator']:
    st.markdown("### Please open the Budget Allocator app to continue.")
    st.stop()
