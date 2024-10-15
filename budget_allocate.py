
import streamlit as st
import os
import pandas as pd
from datetime import datetime
from PIL import Image
import json
import matplotlib.pyplot as plt


def run_budget_allocate():
 
    # Assuming the CSV file path is defined
    csv_path = os.path.join("5_228_6_max_response_reallocated.csv")

    if os.path.exists(csv_path):
        budget_results = pd.read_csv(csv_path)

        # Streamlit section to show charts
        st.write("---")
        st.title("Budget Allocation Results - Charts")

        # 1. Budget Allocation vs. Response Curve
        st.subheader("Budget Allocation vs. Response Curve for Channels")
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        for channel in budget_results['channels'].unique():
            channel_data = budget_results[budget_results['channels'] == channel]
            ax1.plot(channel_data['constr_low'], channel_data['optmResponseUnitUnbound'], label=channel)

        ax1.set_xlabel('Budget Allocation')
        ax1.set_ylabel('Response Curve')
        ax1.set_title('Budget Allocation vs. Response Curve for Channels')
        ax1.legend()
        ax1.grid()
        st.pyplot(fig1)

        # 2. Channel Contribution to Total Revenue (Decomposition)
        st.subheader("Channel Contribution to Total Revenue")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.bar(budget_results['channels'], budget_results['optmResponseUnitTotalUnbound'], color='skyblue')
        ax2.set_xlabel('Channels')
        ax2.set_ylabel('Total Response Contribution')
        ax2.set_title('Channel Contribution to Total Revenue')
        plt.xticks(rotation=45)
        ax2.grid(axis='y')
        st.pyplot(fig2)

        # 3. Media Efficiency Ratio (ROI by Channel)
        st.subheader("ROI by Channel")
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        ax3.bar(budget_results['channels'], budget_results['optmRoiUnitUnbound'], color='lightgreen')
        ax3.set_xlabel('Channels')
        ax3.set_ylabel('ROI (Return on Investment)')
        ax3.set_title('ROI by Channel')
        plt.xticks(rotation=45)
        ax3.grid(axis='y')
        st.pyplot(fig3)

        # 4. Incrementality Analysis by Channel
        st.subheader("Incrementality Analysis by Channel")
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        ax4.bar(budget_results['channels'], budget_results['optmResponseUnitLiftUnbound'], color='coral')
        ax4.set_xlabel('Channels')
        ax4.set_ylabel('Incremental Response')
        ax4.set_title('Incrementality Analysis by Channel')
        plt.xticks(rotation=45)
        ax4.grid(axis='y')
        st.pyplot(fig4)
    else:
        st.error(f"The results file '{csv_path}' does not exist.")
