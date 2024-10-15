import streamlit as st
import numpy as np
import pandas as pd

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
                data = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                data = pd.read_excel(uploaded_file)

            # Display required fields and descriptions
            st.header("Required Fields and Field Descriptions")
            st.markdown("""
            - **Date Field**: `event_date_utc`  
              Format: YYYY-MM-DD. This field must be present and in a date format. It’s the timestamp for each record.
            - **Spend Fields** (must be numerical values):
              - `dsp_recruit_cost` (DSP Recruit)
              - ...
            """)

            # Data preview section
            st.subheader("Data Preview")
            st.write(data.head())

            # Field Mapping and Manual Overrides
            st.subheader("Field Mapping and Manual Overrides")
            with st.form("field_mapping"):
                col1, col2 = st.columns(2)
                event_date_col = col1.selectbox("Map event_date_utc", data.columns, key='event_date')
                dsp_recruit_col = col2.selectbox("Map dsp_recruit_cost", data.columns, key='dsp_recruit')
                submit_button = st.form_submit_button(label="Add Row")

            # Validation Button
            st.subheader("Submission Button")
            if st.button("Validate Data"):
                required_columns = [event_date_col, dsp_recruit_col]
                missing_columns = [col for col in required_columns if col not in data.columns]
                
                if len(missing_columns) == 0:
                    st.success("Data successfully validated!")
                else:
                    st.error(f"Missing columns: {', '.join(missing_columns)}")

            # Proceed to Hyperparameter Adjustment Page
            if st.button("Proceed to Hyperparameter Adjustment"):
                st.session_state['page'] = 'hyperparameter_adjustment'
                st.query_params(page=st.session_state['page'])

        except Exception as e:
            st.error(f"Error loading file: {e}")

    else:
        st.info("Please upload a file to continue.")

elif st.session_state['page'] == 'hyperparameter_adjustment':
    # Hyperparameter Adjustment Page
    st.title("MetaRobynMMM - Model Hyperparameter Configuration")

    # Dictionary to store hyperparameters for each ad type
    hyperparameters = {
        "DSP": {},
        "SP": {},
        "SB": {},
        "SD": {},
        "All Ad Types": {}
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
    def hyperparameter_adjustment(ad_type):
        st.subheader(f"{ad_type} Hyperparameter Range Settings")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            alpha_range = st.slider(f"{ad_type} Alpha Range (Decay Rate):", 0.1, 3.0, (0.5, 1.0), key=f"{ad_type}_alpha_range", help="Alpha controls how quickly the effect of media spend decays over time.")
            gamma_range = st.slider(f"{ad_type} Gamma Range (Saturation):", 0.0, 1.0, (0.2, 0.5), key=f"{ad_type}_gamma_range", help="Gamma controls the level of saturation in the media response curve.")
            scale_range = st.slider(f"{ad_type} Scale Range:", 0.0, 1.0, (0.2, 0.8), key=f"{ad_type}_scale_range", help="Scale modifies the overall strength of the adstock effect.")

        with col2:
            # Display Adstock Curve
            alpha_default = (alpha_range[0] + alpha_range[1]) / 2
            scale_default = (scale_range[0] + scale_range[1]) / 2
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
            "alpha_range": alpha_range,
            "gamma_range": gamma_range,
            "scale_range": scale_range
        }

    # Model Configuration Page
    st.header("Model Configuration")

    # Hyperparameter Adjustment for Each Channel
    for ad_type in hyperparameters.keys():
        hyperparameter_adjustment(ad_type)

    # Summary of Hyperparameter Ranges
    st.subheader("Summary of Hyperparameter Ranges")
    summary_df = pd.DataFrame.from_dict(hyperparameters, orient='index')
    st.dataframe(summary_df)

    # Iterations and Trials
    st.header("Model Iterations and Trials")
    iterations = st.slider("Iterations:", 2000, 10000, 1000, step=100, help="Number of iterations for the model optimization.")
    trials = st.slider("Trials:", 5, 30, 10, help="Number of trials for the hyperparameter tuning.")
    ts_validation = st.checkbox("Time Series Validation", value=False, help="Check if you want to use time series validation.")

    # Navigation Buttons
    if st.button("Back"):
        st.session_state['page'] = 'upload_page'
        st.query_params(page=st.session_state['page'])

    if st.button("Next"):
        st.session_state['page'] = 'model_run'
        st.query_params(page=st.session_state['page'])

    # Store hyperparameters and model configuration for future use
    st.session_state['hyperparameters'] = hyperparameters
    st.session_state['iterations'] = iterations
    st.session_state['trials'] = trials
    st.session_state['ts_validation'] = ts_validation

elif st.session_state['page'] == 'model_run':
    # Model Run Page
    st.title("MetaRobynMMM - Model Run")
    st.write("This page will contain the logic to run the model based on the configured hyperparameters and uploaded data.")

    # Navigation Buttons
    if st.button("Back"):
        st.session_state['page'] = 'hyperparameter_adjustment'
        st.query_params(page=st.session_state['page'])
