import streamlit as st
import os
import json

# Title for the Budget Allocator app
st.title("MetaRobynMMM - Budget Allocation")

# Check if model selection exists in session state
if 'selected_model' not in st.session_state:
    st.write("No model selected. Please go back to the chart dropdown viewer and select a model.")
    if st.button("Go to Chart Dropdown Viewer"):
        st.session_state['navigate_to_viewer'] = True
else:
    # Full-width input fields for optimization settings
    st.subheader("Optimization Settings")
    st.markdown("---")
    col_optimization, col_budget, col_date, col_plot = st.columns([1, 1, 1, 1])

    with col_optimization:
        st.write("**Optimization Goal**")
        optimization_goal = st.selectbox("", ["Maximize ROAS", "Maximize Conversions", "Minimize Cost"], key="optimization_goal")

    with col_budget:
        st.write("**Total Budget**")
        total_budget = st.number_input("", value=7000000, step=100000, key="total_budget")

    with col_date:
        st.write("**Date Range**")
        date_range = st.date_input("", [datetime(2024, 1, 1), datetime(2024, 3, 31)], key="date_range")

    with col_plot:
        st.write("**Plot Folder Path**")
        plot_folder = st.text_input("", "./plots", key="plot_folder")

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
            low_value = st.selectbox(f"{channel} - Lower Bound", [0.5, 1.0, 1.2, 1.5, 1.8], key=f"{channel}_low")
            channel_constraints[channel] = {"lower_bound": low_value}

    with col_right:
        st.subheader("Upper Bounds")
        for channel in channels:
            up_value = st.selectbox(f"{channel} - Upper Bound", [1.5, 2.0, 2.5, 2.8, 3.0], key=f"{channel}_up")
            channel_constraints[channel]["upper_bound"] = up_value

    # Export option
    export = st.checkbox("Export Results", value=True, key="export_results")

    # Collect parameters for robyn_allocator
    if st.button("Run Budget Allocator", key="run_budget_allocator_final"):
        st.write("Budget Allocator started...")
        # Generate budget_params.csv and run budget_alloc.py
        with open('budget_params.csv', 'w') as f:
            f.write('model,date_range,total_budget,channel_constraints,export,plot_folder\n')
            f.write(f"{st.session_state['selected_model']},{date_range},{total_budget},{json.dumps(channel_constraints)},{export},{plot_folder}\n")
        st.write("Generating budget_params.csv...")
        os.system('python budget_alloc.py')
        st.write("Running budget_alloc.py...")

    # View results option
    if export and st.button("View Results", key="view_results_final"):
        st.write("Displaying allocation results...")