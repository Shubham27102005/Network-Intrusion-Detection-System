import os
import joblib
import streamlit as st
from tensorflow.keras.models import load_model


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="NIDS | Network Intrusion Detection",
    page_icon="🛡️",
    layout="wide"
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")


# --------------------------------------------------
# Load Models
# --------------------------------------------------

@st.cache_resource
def load_models():

    models = {}

    models["Logistic Regression"] = joblib.load(
        os.path.join(MODEL_DIR, "logistic_regression.pkl")
    )

    models["Balanced Logistic Regression"] = joblib.load(
        os.path.join(MODEL_DIR, "balanced_logistic_regression.pkl")
    )

    models["ANN"] = load_model(
        os.path.join(MODEL_DIR, "ann_model.keras")
    )

    models["Random Forest"] = joblib.load(
        os.path.join(MODEL_DIR, "nids_random_forest.pkl")
    )

    scaler = joblib.load(
        os.path.join(MODEL_DIR, "standard_scaler.pkl")
    )

    return models, scaler


models, scaler = load_models()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🛡️ Network Intrusion Detection System")

st.markdown(
    """
    ### AI-Based Network Traffic Security

    An intelligent intrusion detection system using
    **Machine Learning and Artificial Neural Networks**
    to classify network traffic as **Normal** or **Attack**.
    """
)

st.divider()


# --------------------------------------------------
# Model Statistics
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Models", "4")

with col2:
    st.metric("RF Accuracy", "98.40%")

with col3:
    st.metric("ANN Accuracy", "96.02%")

with col4:
    st.metric("Dataset", "NF-UNSW-NB15")


st.divider()


# --------------------------------------------------
# Model Selection
# --------------------------------------------------

st.header("🤖 Detection Model")

selected_model = st.selectbox(
    "Choose a model for intrusion detection:",
    list(models.keys())
)

st.success(f"Selected Model: **{selected_model}**")


# --------------------------------------------------
# Tabs
# --------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "🔍 Prediction",
        "📊 Model Comparison",
        "ℹ️ Project Information"
    ]
)


# --------------------------------------------------
# Prediction Tab
# --------------------------------------------------
with tab1:

    st.subheader("🔍 Network Traffic Analysis")

    st.write(
        "Enter the network traffic features below and select "
        "a trained model to detect potential intrusion."
    )

    # --------------------------------------------------
    # Input Features
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        l4_src_port = st.number_input(
            "Source Port",
            min_value=0,
            max_value=65535,
            value=443,
            step=1
        )

        l4_dst_port = st.number_input(
            "Destination Port",
            min_value=0,
            max_value=65535,
            value=80,
            step=1
        )

        protocol = st.number_input(
            "Protocol",
            min_value=0,
            value=6,
            step=1
        )

        l7_proto = st.number_input(
            "L7 Protocol",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

        in_bytes = st.number_input(
            "Input Bytes",
            min_value=0,
            value=1000,
            step=100
        )

    with col2:
        out_bytes = st.number_input(
            "Output Bytes",
            min_value=0,
            value=1000,
            step=100
        )

        in_pkts = st.number_input(
            "Input Packets",
            min_value=0,
            value=10,
            step=1
        )

        out_pkts = st.number_input(
            "Output Packets",
            min_value=0,
            value=10,
            step=1
        )

        tcp_flags = st.number_input(
            "TCP Flags",
            min_value=0,
            value=0,
            step=1
        )

        flow_duration = st.number_input(
            "Flow Duration (milliseconds)",
            min_value=0,
            value=1000,
            step=100
        )

    # --------------------------------------------------
    # Create Input DataFrame
    # --------------------------------------------------

    input_data = pd.DataFrame([{
        "L4_SRC_PORT": l4_src_port,
        "L4_DST_PORT": l4_dst_port,
        "PROTOCOL": protocol,
        "L7_PROTO": l7_proto,
        "IN_BYTES": in_bytes,
        "OUT_BYTES": out_bytes,
        "IN_PKTS": in_pkts,
        "OUT_PKTS": out_pkts,
        "TCP_FLAGS": tcp_flags,
        "FLOW_DURATION_MILLISECONDS": flow_duration
    }])

    st.write("### Input Traffic")
    st.dataframe(input_data, use_container_width=True)

    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    if st.button(
        "🚨 Analyze Traffic",
        use_container_width=True
    ):

        selected_model_object = models[selected_model]

        # Random Forest was trained on unscaled features.
        # LR, Balanced LR and ANN use StandardScaler.
        if selected_model == "Random Forest":

            model_input = input_data.values

        else:

            model_input = scaler.transform(input_data)

        # --------------------------------------------------
        # Model Prediction
        # --------------------------------------------------

        if selected_model == "ANN":

            probability = float(
                selected_model_object.predict(
                    model_input,
                    verbose=0
                )[0][0]
            )

            prediction = int(probability >= 0.5)

        else:

            prediction = int(
                selected_model_object.predict(model_input)[0]
            )

            probability = float(
                selected_model_object.predict_proba(
                    model_input
                )[0][1]
            )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        st.divider()

        if prediction == 1:

            st.error("🔴 ATTACK DETECTED")

        else:

            st.success("🟢 NORMAL TRAFFIC")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Selected Model",
                selected_model
            )

        with col2:
            st.metric(
                "Attack Probability",
                f"{probability * 100:.2f}%"
            )

        st.progress(probability)

# --------------------------------------------------
# Model Comparison Tab
# --------------------------------------------------

with tab2:

    st.subheader("Model Performance")

    comparison_data = {
        "Model": [
            "Logistic Regression",
            "Balanced Logistic Regression",
            "ANN",
            "Random Forest"
        ],
        "Accuracy": [
            "94.03%",
            "—",
            "96.02%",
            "98.40%"
        ],
        "Precision": [
            "75.00%",
            "—",
            "62.93%",
            "83.69%"
        ],
        "Recall": [
            "15.00%",
            "—",
            "97.32%",
            "94.16%"
        ],
        "F1 Score": [
            "25.00%",
            "—",
            "76.44%",
            "88.61%"
        ]
    }

    st.table(comparison_data)


# --------------------------------------------------
# Project Information Tab
# --------------------------------------------------

with tab3:

    st.subheader("About the Project")

    st.write(
        """
        This Network Intrusion Detection System is based on the
        NF-UNSW-NB15 dataset and uses multiple machine learning
        approaches to identify potentially malicious network traffic.
        """
    )

    st.write("**Models:**")
    st.write(
        """
        - Logistic Regression
        - Balanced Logistic Regression
        - Artificial Neural Network
        - Random Forest
        """
    )

    st.write(
        "**Dataset:** NF-UNSW-NB15 — University of Queensland, Australia"
    )

    st.success(
        "✅ All trained models and preprocessing artifacts loaded successfully."
    )