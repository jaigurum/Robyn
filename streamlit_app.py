import streamlit as st
import numpy as np
import pandas as pd
import csv
import model_display


# Customer Selection Dropdown
if 'cust' not in st.session_state:
    st.session_state['cust'] = ''

st.subheader("Select Customer Name")
cust_options = ["mars-pne", "unilever", "mars-wrigley", "colgate", "Add new customer name"]
cust_selected = st.selectbox("Customer Name", cust_options, key='cust_name')

if cust_selected == "Add new customer name":
    st.session_state['cust'] = st.text_input("Enter new customer name:")
else:
    st.session_state['cust'] = cust_selected

# Initialize session state for page navigation if it does not already exist
if 'page' not in st.session_state:
    st.session_state['page'] = 'upload_page'

# Page Navigation Logic
if st.session_state['page'] == 'upload_page':
    # Page title
    st.title("Robyn Model - Data Upload & Validation")

    # File upload section
    st.markdown("Upload your dataset in CSV or Excel format. Please ensure that all required fields are present and in the correct format before proceeding.")
    uploaded_file = st.file_uploader("Drag and drop files here", type=['csv', 'xlsx'], help="Accepted formats: csv, xlsx. Max file size: 100MB")

    if uploaded_file:
        try:
            # Load the uploaded file
            if uploaded_file.name.endswith('.csv'):
                robyn_df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                robyn_df = pd.read_excel(uploaded_file)

            # Display required fields and descriptions
            st.header("Required Fields and Field Descriptions")
            st.markdown("""
            - **Date Field**: `event_date_utc`  
              Format: YYYY-MM-DD. This field must be present and in a date format. It’s the timestamp for each record.
            - **Spend Fields** (must be numerical values):
              - `dsp_cost` (DSP)
              - ...
            """)

            # Data preview section
            st.subheader("Data Preview")
            st.write(robyn_df.head())

            # Select Country from Available Data
            st.subheader("Select Country")
            if 'country' in robyn_df.columns:
                available_countries = robyn_df['country'].unique()
                country_filtered = st.selectbox("Country", available_countries, key='country_select')
            else:
                country_filtered = 'Not specified'
                st.warning("Country column not found in the dataset.")

            # Field Mapping and Manual Overrides
            st.subheader("Field Mapping and Manual Overrides")
            with st.form("field_mapping"):
                col1, col2 = st.columns(2)
                event_date_col = col1.selectbox("Map event_date_utc", robyn_df.columns, key='event_date')
                dsp_recruit_col = col2.selectbox("Map dsp_recruit_cost", robyn_df.columns, key='dsp_recruit')
                submit_button = st.form_submit_button(label="Submit Field Mapping")

            # Validation Button
            st.subheader("Submission Button")
            if st.button("Validate Data"):
                required_columns = [
                    'dsp_recruit_cost',
                    'dsp_conversion_cost',
                    'dsp_awareness_cost',
                    'sd_recruit_cost',
                    'sp_auto_cost',
                    'sb_defend_cost',
                    'sp_recruit_cost',
                    'sp_attack_cost',
                    'sp_defend_cost',
                    'sb_recruit_cost',
                    'sd_defend_cost',
                    'sb_attack_cost',
                    'sd_attack_cost',
                    'dsp_recruit_impressions',
                    'dsp_conversion_impressions',
                    'dsp_awareness_impressions',
                    'sd_recruit_impressions',
                    'sp_auto_clicks',
                    'sb_defend_clicks',
                    'sp_recruit_clicks',
                    'sp_attack_clicks',
                    'sp_defend_clicks',
                    'sb_recruit_clicks',
                    'sd_defend_clicks',
                    'sb_attack_clicks',
                    'sd_attack_clicks',
                    'total_product_sales',
                    'country',
                    'date'
                ]
                missing_columns = [col for col in required_columns if col not in robyn_df.columns]

                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                else:
                    st.success("All required columns are present.")

            # Proceed to Hyperparameter Adjustment Page
            if st.button("Proceed to Hyperparameter Adjustment"):
                st.session_state['country_filtered'] = country_filtered
                st.session_state['page'] = 'hyperparameter_adjustment'
                st.experimental_set_query_params(page=st.session_state['page'])

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please upload a file to continue.")

elif st.session_state['page'] == 'hyperparameter_adjustment':
    # Hyperparameter Adjustment Page
    st.title("MetaRobynMMM - Model Hyperparameter Configuration")

    # Dictionary to store hyperparameters for each ad type
    hyperparameters = {
        "dsp_recruit": {
            "alphas": [1.0, 2.0],
            "gammas": [0.5, 0.7],
            "thetas": [0.2, 0.4]
        },
        "dsp_conversion": {
            "alphas": [0.5, 2.0],
            "gammas": [0.4, 0.5],
            "thetas": [0.1, 0.3]
        },
        "dsp_awareness": {
            "alphas": [0.5, 2.0],
            "gammas": [0.4, 0.5],
            "thetas": [0.1, 0.3]
        },
        "sd_recruit": {
            "alphas": [0.5, 1.0],
            "gammas": [0.2, 0.4],
            "thetas": [0.1, 0.3]
        },
        "sd_defend": {
            "alphas": [0.5, 1.0],
            "gammas": [0.2, 0.4],
            "thetas": [0.1, 0.3]
        },
        "sd_attack": {
            "alphas": [0.5, 1.0],
            "gammas": [0.2, 0.4],
            "thetas": [0.1, 0.3]
        },
        "sp_auto": {
            "alphas": [0.5, 3.0],
            "gammas": [0.6, 0.9],
            "thetas": [0.0, 0.3]
        },
        "sp_recruit": {
            "alphas": [0.5, 3.0],
            "gammas": [0.6, 0.9],
            "thetas": [0.0, 0.3]
        },
        "sp_attack": {
            "alphas": [0.5, 3.0],
            "gammas": [0.6, 0.9],
            "thetas": [0.0, 0.3]
        },
        "sp_defend": {
            "alphas": [0.5, 3.0],
            "gammas": [0.6, 0.9],
            "thetas": [0.0, 0.3]
        },
        "sb_defend": {
            "alphas": [1.1, 1.8],
            "gammas": [0.4, 0.5],
            "thetas": [0.0, 0.1]
        },
        "sb_recruit": {
            "alphas": [1.1, 1.8],
            "gammas": [0.4, 0.5],
            "thetas": [0.0, 0.1]
        },
        "sb_attack": {
            "alphas": [1.1, 1.8],
            "gammas": [0.4, 0.5],
            "thetas": [0.0, 0.1]
        }
    }

    # Function to calculate Adstock Curve
    def calculate_adstock_curve(alpha, scale, length=30):
        adstock_curve = [scale * (alpha ** i) for i in range(length)]
        return adstock_curve

    # Function to calculate Response Curve
    def calculate_response_curve(gamma, scale, length=30):
        x = np.arange(length)
        response_curve = scale * (1 - np.exp(-gamma * x))
        return response_curve

    # Function to display hyperparameter adjustment for each channel
    def hyperparameter_adjustment(ad_type, params):
        st.subheader(f"{ad_type} Hyperparameter Range Settings")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            alpha_range = st.slider(f"{ad_type} Alpha Range (Decay Rate):", 0.1, 3.0, tuple(params["alphas"]), key=f"{ad_type}_alpha_range", help="Alpha controls how quickly the effect of media spend decays over time.")
            gamma_range = st.slider(f"{ad_type} Gamma Range (Saturation):", 0.0, 1.0, tuple(params["gammas"]), key=f"{ad_type}_gamma_range", help="Gamma controls the level of saturation in the media response curve.")
            theta_range = st.slider(f"{ad_type} Theta Range:", 0.0, 1.0, tuple(params["thetas"]), key=f"{ad_type}_theta_range", help="Theta modifies the overall strength of the adstock effect.")

        with col2:
            # Display Adstock Curve
            alpha_default = (alpha_range[0] + alpha_range[1]) / 2
            scale_default = (theta_range[0] + theta_range[1]) / 2
            adstock_data = calculate_adstock_curve(alpha_default, scale_default)
            st.subheader("Adstock Curve")
            st.line_chart(pd.DataFrame(adstock_data, columns=["Adstock Effect"]))

        with col3:
            # Display Response Curve
            gamma_default = (gamma_range[0] + gamma_range[1]) / 2
            response_data = calculate_response_curve(gamma_default, scale_default)
            st.subheader("Response Curve")
            st.line_chart(pd.DataFrame(response_data, columns=["Media Response"]))

        # Save hyperparameters
        hyperparameters[ad_type] = {
            "alphas": list(alpha_range),
            "gammas": list(gamma_range),
            "thetas": list(theta_range)
        }

    # Hyperparameter Adjustment for Each Channel
    for ad_type, params in hyperparameters.items():
        hyperparameter_adjustment(ad_type, params)

    # Summary of Hyperparameter Ranges
    st.subheader("Summary of Hyperparameter Ranges")
    summary_df = pd.DataFrame.from_dict(hyperparameters, orient='index')
    st.dataframe(summary_df)

    # Iterations and Trials
    st.header("Model Iterations and Trials")
    iterations = st.slider("Iterations:", 2000, 10000, 1000, step=100, help="Number of iterations for the model optimization.")
    trials = st.slider("Trials:", 5, 30, 10, help="Number of trials for the hyperparameter tuning.")
    country_filtered = st.session_state['country_filtered']
    ts_validation = st.checkbox("Time Series Validation", value=False, help="Check if you want to use time series validation.")

    # Navigation Buttons
    if st.button("Back"):
        st.session_state['page'] = 'upload_page'
        st.experimental_set_query_params(page=st.session_state['page'])

    if st.button("Next"):
        st.session_state['page'] = 'model_run'
        st.experimental_set_query_params(page=st.session_state['page'])

    # Save Hyperparameters Button
    if st.button("Save Hyperparameters"):
        # Store hyperparameters and model configuration for future use
        st.session_state['hyperparameters'] = hyperparameters
        st.session_state['iterations'] = iterations
        st.session_state['trials'] = trials
        st.session_state['country_filtered'] = country_filtered
        st.session_state['cust'] = st.session_state['cust']

        # Store hyperparameters, iterations, and trials to a CSV file
        with open("/workspaces/Robyn/hyperparameter_config.csv", "w", newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Variable Name", "Min Value", "Max Value"])
            for ad_type, params in hyperparameters.items():
                for param, values in params.items():
                    csvwriter.writerow([f"{ad_type}_{param}", values[0], values[1]])
        st.success("Hyperparameters saved successfully as CSV.")

        # Save Iterations, Trials, Country, and Customer to a CSV file
        with open("/workspaces/Robyn/model_params.csv", "w", newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["parameter", "Value"])
            csvwriter.writerow(["iterations", iterations])
            csvwriter.writerow(["trials", trials])
            csvwriter.writerow(["ts_validation", ts_validation])
            csvwriter.writerow(["country", country_filtered])
            csvwriter.writerow(["cust", st.session_state['cust']])

elif st.session_state['page'] == 'model_run':
    # Model Run Page
    
    st.title("MetaRobynMMM - Model Run")
    
    model_display.run_model_display()  # Call the function from model_display.py

    # Navigation Buttons
    if st.button("Back"):
        st.session_state['page'] = 'hyperparameter_adjustment'
        st.experimental_set_query_params(page=st.session_state['page'])