"""
Credit Card Fraud Detection Deployment App
A Streamlit-based web application for real-time fraud detection
"""

import streamlit as st
import pickle
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os

# Page configuration
st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI


st.markdown("""
<style>

/* === Metric Card Container === */
.metric-card {
    background-color: #0f172a;   /* dark card */
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.45);
    text-align: center;
}

/* === Card Title === */
.metric-card h3 {
    color: #e5e7eb;              /* light gray text */
    font-size: 16px;
    margin-bottom: 8px;
}

/* === Metric Value === */
.metric-card h2 {
    color: #22c55e;              /* bright green */
    font-size: 32px;
    font-weight: 700;
    margin: 0;
}

</style>
""", unsafe_allow_html=True)


# Load models and scaler
@st.cache_resource
def load_models():
    """Load pickled models and scaler"""
    try:
        models_dir = "fraud_detection_models"
        
        # Load models
        with open(f"{models_dir}/logistic_regression_model.pkl", "rb") as f:
            lr_model = pickle.load(f)
        
        with open(f"{models_dir}/random_forest_model.pkl", "rb") as f:
            rf_model = pickle.load(f)
        
        with open(f"{models_dir}/scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
        
        # Load metadata
        with open(f"{models_dir}/model_metadata.pkl", "rb") as f:
            metadata = pickle.load(f)
        
        # Load feature names
        with open(f"{models_dir}/feature_names.pkl", "rb") as f:
            feature_names = pickle.load(f)
        
        return lr_model, rf_model, scaler, metadata, feature_names
    
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        st.info("Please ensure pickle files are in the 'fraud_detection_models' directory")
        return None, None, None, None, None

# Load models
lr_model, rf_model, scaler, metadata, feature_names = load_models()

# Header
st.title("🔒 Credit Card Fraud Detection System")
st.markdown("---")

# Sidebar Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio(
    "Select Mode",
    ["🏠 Dashboard", "🔍 Single Transaction", "📊 Batch Prediction", "📈 Model Performance"],
    help="Choose between different operation modes"
)

if lr_model is None:
    st.error("Models not loaded. Please check the models directory.")
    st.stop()

# ==================== DASHBOARD PAGE ====================
if app_mode == "🏠 Dashboard":
    st.header("Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🤖 Logistic Regression AUC",
            f"{metadata['lr_auc']:.4f}",
            "ROC-AUC Score"
        )
    
    with col2:
        st.metric(
            "🌲 Random Forest AUC",
            f"{metadata['rf_auc']:.4f}",
            "ROC-AUC Score"
        )
    
    with col3:
        st.metric(
            "📊 LR F1-Score",
            f"{metadata['lr_f1']:.4f}",
            "Performance"
        )
    
    with col4:
        st.metric(
            "📊 RF F1-Score",
            f"{metadata['rf_f1']:.4f}",
            "Performance"
        )
    
    st.markdown("---")
    
    st.subheader("Model Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Logistic Regression Model**
        - Training Samples: {metadata['train_samples']:,}
        - Test Samples: {metadata['test_samples']:,}
        - Features: {metadata['num_features']}
        - Fraud Rate (Training): {metadata['train_fraud_rate']:.2f}%
        """)
    
    with col2:
        st.info(f"""
        **Random Forest Model**
        - Training Samples: {metadata['train_samples']:,}
        - Test Samples: {metadata['test_samples']:,}
        - Features: {metadata['num_features']}
        - Trees: 100
        - Model Size: Ensemble
        """)

# ==================== SINGLE TRANSACTION PAGE ====================
elif app_mode == "🔍 Single Transaction":
    st.header("Single Transaction Fraud Detection")
    
    st.markdown("""
    Enter transaction details below. The system will analyze the transaction 
    using both Logistic Regression and Random Forest models.
    """)
    
    st.markdown("---")
    
    # Create input columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        transaction_time = st.number_input(
            "Transaction Time (seconds)",
            min_value=0.0,
            max_value=172800.0,
            value=50000.0,
            help="Time of transaction in seconds"
        )
        
        amount = st.number_input(
            "Transaction Amount ($)",
            min_value=0.0,
            max_value=25000.0,
            value=100.0,
            step=0.01,
            help="Transaction amount in dollars"
        )
    
    with col2:
        st.write("**V Features (Part 1)**")
        v1 = st.slider("V1", -10.0, 10.0, 0.0)
        v2 = st.slider("V2", -10.0, 10.0, 0.0)
        v3 = st.slider("V3", -10.0, 10.0, 0.0)
        v4 = st.slider("V4", -10.0, 10.0, 0.0)
        v5 = st.slider("V5", -10.0, 10.0, 0.0)
    
    with col3:
        st.write("**V Features (Part 2)**")
        v10 = st.slider("V10", -10.0, 10.0, 0.0)
        v12 = st.slider("V12", -10.0, 10.0, 0.0)
        v14 = st.slider("V14", -10.0, 10.0, 0.0)
        v17 = st.slider("V17", -10.0, 10.0, 0.0)
        v21 = st.slider("V21", -10.0, 10.0, 0.0)
    
    # Prepare input data
    if st.button("🔍 Analyze Transaction", key="analyze_btn", use_container_width=True):
        
        # Create input array with all features
        input_data = np.zeros((1, metadata['num_features']))
        
        # Set Time and Amount
        input_data[0, 0] = transaction_time
        
        # Set V features (example mapping - adjust indices as needed)
        v_features = {
            1: v1, 2: v2, 3: v3, 4: v4, 5: v5,
            10: v10, 12: v12, 14: v14, 17: v17, 21: v21
        }
        
        for idx, val in v_features.items():
            if idx < metadata['num_features']:
                input_data[0, idx] = val
        
        # Scale the input
        input_scaled = scaler.transform(input_data)
        
        # Get predictions
        lr_pred_proba = lr_model.predict_proba(input_scaled)[0][1]
        rf_pred_proba = rf_model.predict_proba(input_scaled)[0][1]
        
        lr_pred = lr_model.predict(input_scaled)[0]
        rf_pred = rf_model.predict(input_scaled)[0]
        
        # Display results
        st.markdown("---")
        st.subheader("Prediction Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if lr_pred == 1:
                st.markdown("""
                <div class="fraud-alert">
                <h3>🚨 Logistic Regression: FRAUDULENT</h3>
                <p><strong>Fraud Probability:</strong> {:.2%}</p>
                </div>
                """.format(lr_pred_proba), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="safe-alert">
                <h3>✅ Logistic Regression: LEGITIMATE</h3>
                <p><strong>Legitimate Probability:</strong> {:.2%}</p>
                </div>
                """.format(1 - lr_pred_proba), unsafe_allow_html=True)
        
        with col2:
            if rf_pred == 1:
                st.markdown("""
                <div class="fraud-alert">
                <h3>🚨 Random Forest: FRAUDULENT</h3>
                <p><strong>Fraud Probability:</strong> {:.2%}</p>
                </div>
                """.format(rf_pred_proba), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="safe-alert">
                <h3>✅ Random Forest: LEGITIMATE</h3>
                <p><strong>Legitimate Probability:</strong> {:.2%}</p>
                </div>
                """.format(1 - rf_pred_proba), unsafe_allow_html=True)
        
        # Probability comparison chart
        st.markdown("---")
        
        fig = go.Figure(data=[
            go.Bar(name='Logistic Regression', x=['Fraud Probability'], y=[lr_pred_proba * 100]),
            go.Bar(name='Random Forest', x=['Fraud Probability'], y=[rf_pred_proba * 100])
        ])
        
        fig.update_layout(
            title="Fraud Probability Comparison",
            yaxis_title="Probability (%)",
            template="plotly_white",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Transaction summary
        st.markdown("---")
        st.subheader("Transaction Summary")
        
        summary_df = pd.DataFrame({
            "Parameter": ["Time", "Amount", "V1", "V2", "V3", "V4", "V5", "V10", "V12", "V14", "V17", "V21"],
            "Value": [transaction_time, f"${amount:.2f}", v1, v2, v3, v4, v5, v10, v12, v14, v17, v21]
        })
        
        st.dataframe(summary_df, use_container_width=True)

# ==================== BATCH PREDICTION PAGE ====================
elif app_mode == "📊 Batch Prediction":
    st.header("Batch Prediction")
    
    st.markdown("""
    Upload a CSV file with multiple transactions for batch prediction.
    The CSV should contain the same features as single transactions.
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read the CSV
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ Loaded {len(df)} transactions")
            
            # Prepare data for prediction
            df_numeric = df.select_dtypes(include=[np.number])
            
            if len(df_numeric.columns) >= metadata['num_features']:
                # Take only required features
                X_batch = df_numeric.iloc[:, :metadata['num_features']].values
                
                # Scale
                X_batch_scaled = scaler.transform(X_batch)
                
                # Predictions
                lr_preds = lr_model.predict(X_batch_scaled)
                rf_preds = rf_model.predict(X_batch_scaled)
                lr_proba = lr_model.predict_proba(X_batch_scaled)[:, 1]
                rf_proba = rf_model.predict_proba(X_batch_scaled)[:, 1]
                
                # Create results dataframe
                results = pd.DataFrame({
                    'LR_Prediction': lr_preds,
                    'LR_Fraud_Probability': lr_proba,
                    'RF_Prediction': rf_preds,
                    'RF_Fraud_Probability': rf_proba,
                    'Consensus': (lr_preds + rf_preds) / 2  # Average prediction
                })
                
                st.markdown("---")
                st.subheader("Prediction Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    lr_fraud_count = (lr_preds == 1).sum()
                    st.metric("LR Frauds Detected", lr_fraud_count, f"{lr_fraud_count/len(df)*100:.1f}%")
                
                with col2:
                    rf_fraud_count = (rf_preds == 1).sum()
                    st.metric("RF Frauds Detected", rf_fraud_count, f"{rf_fraud_count/len(df)*100:.1f}%")
                
                with col3:
                    consensus_fraud = (results['Consensus'] > 0.5).sum()
                    st.metric("Consensus Frauds", consensus_fraud, f"{consensus_fraud/len(df)*100:.1f}%")
                
                st.markdown("---")
                st.subheader("Detailed Predictions")
                st.dataframe(results, use_container_width=True)
                
                # Download results
                csv = results.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results",
                    data=csv,
                    file_name="fraud_predictions.csv",
                    mime="text/csv"
                )
            else:
                st.error(f"CSV must have at least {metadata['num_features']} numeric features")
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# ==================== MODEL PERFORMANCE PAGE ====================
elif app_mode == "📈 Model Performance":
    st.header("Model Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("LR Accuracy", f"{metadata.get('lr_accuracy', 0):.4f}")
    with col2:
        st.metric("LR Precision", f"{metadata.get('lr_precision', 0):.4f}")
    with col3:
        st.metric("LR Recall", f"{metadata.get('lr_recall', 0):.4f}")
    with col4:
        st.metric("LR F1-Score", f"{metadata['lr_f1']:.4f}")
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("RF Accuracy", f"{metadata.get('rf_accuracy', 0):.4f}")
    with col2:
        st.metric("RF Precision", f"{metadata.get('rf_precision', 0):.4f}")
    with col3:
        st.metric("RF Recall", f"{metadata.get('rf_recall', 0):.4f}")
    with col4:
        st.metric("RF F1-Score", f"{metadata['rf_f1']:.4f}")
    
    st.markdown("---")
    
    # AUC Comparison
    fig = go.Figure(data=[
        go.Bar(name='Logistic Regression', x=['ROC-AUC'], y=[metadata['lr_auc']]),
        go.Bar(name='Random Forest', x=['ROC-AUC'], y=[metadata['rf_auc']])
    ])
    
    fig.update_layout(
        title="Model Comparison: AUC Scores",
        template="plotly_white",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Model information
    st.markdown("---")
    st.subheader("Training Information")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.info(f"""
        **Dataset Statistics**
        - Total Samples: {metadata.get('total_samples', 'N/A')}
        - Training Samples: {metadata['train_samples']:,}
        - Test Samples: {metadata['test_samples']:,}
        - Number of Features: {metadata['num_features']}
        - Fraud Rate: {metadata['train_fraud_rate']:.2f}%
        """)
    
    with info_col2:
        st.success(f"""
        **Model Details**
        - Logistic Regression: Trained with max_iter=1000
        - Random Forest: 100 trees with random_state=42
        - Scaler: StandardScaler applied to all features
        - Test Size: 20%
        - Stratified Split: Yes
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; margin-top: 2rem;'>
<p>🔒 Credit Card Fraud Detection System v1.0</p>
<p>Powered by Logistic Regression & Random Forest</p>
</div>
""", unsafe_allow_html=True)
