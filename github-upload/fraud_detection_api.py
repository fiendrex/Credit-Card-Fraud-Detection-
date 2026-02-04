"""
Fraud Detection API - For programmatic model access
Can be used standalone or integrated with REST frameworks (Flask, FastAPI)
"""

import pickle
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Union
from dataclasses import dataclass

@dataclass
class PredictionResult:
    """Structured prediction result"""
    transaction_id: str
    lr_prediction: int
    lr_probability: float
    rf_prediction: int
    rf_probability: float
    consensus_prediction: int
    consensus_score: float
    timestamp: str = ""

class FraudDetectionAPI:
    """
    Main API class for fraud detection
    Handles model loading, prediction, and result formatting
    """
    
    def __init__(self, models_dir: str = "fraud_detection_models"):
        """
        Initialize API with model path
        
        Args:
            models_dir: Directory containing pickle files
        """
        self.models_dir = Path(models_dir)
        self.lr_model = None
        self.rf_model = None
        self.scaler = None
        self.metadata = None
        self.feature_names = None
        
        self.load_models()
    
    def load_models(self) -> bool:
        """
        Load all required model files
        
        Returns:
            bool: True if all models loaded successfully
        """
        try:
            # Load models
            with open(self.models_dir / "logistic_regression_model.pkl", "rb") as f:
                self.lr_model = pickle.load(f)
            
            with open(self.models_dir / "random_forest_model.pkl", "rb") as f:
                self.rf_model = pickle.load(f)
            
            # Load scaler
            with open(self.models_dir / "scaler.pkl", "rb") as f:
                self.scaler = pickle.load(f)
            
            # Load metadata
            with open(self.models_dir / "model_metadata.pkl", "rb") as f:
                self.metadata = pickle.load(f)
            
            # Load feature names
            with open(self.models_dir / "feature_names.pkl", "rb") as f:
                self.feature_names = pickle.load(f)
            
            print("✅ All models loaded successfully")
            return True
        
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            return False
    
    def predict_single(self, features: np.ndarray, 
                      transaction_id: str = "TX001") -> PredictionResult:
        """
        Predict fraud for a single transaction
        
        Args:
            features: 1D array of transaction features (30 features)
            transaction_id: Unique transaction identifier
        
        Returns:
            PredictionResult: Structured prediction result
        """
        if self.lr_model is None or self.rf_model is None:
            raise ValueError("Models not loaded. Call load_models() first.")
        
        # Ensure correct shape
        features = np.array(features).reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Logistic Regression predictions
        lr_pred = self.lr_model.predict(features_scaled)[0]
        lr_proba = self.lr_model.predict_proba(features_scaled)[0][1]
        
        # Random Forest predictions
        rf_pred = self.rf_model.predict(features_scaled)[0]
        rf_proba = self.rf_model.predict_proba(features_scaled)[0][1]
        
        # Consensus prediction (average of probabilities)
        consensus_score = (lr_proba + rf_proba) / 2
        consensus_pred = 1 if consensus_score > 0.5 else 0
        
        return PredictionResult(
            transaction_id=transaction_id,
            lr_prediction=int(lr_pred),
            lr_probability=float(lr_proba),
            rf_prediction=int(rf_pred),
            rf_probability=float(rf_proba),
            consensus_prediction=int(consensus_pred),
            consensus_score=float(consensus_score)
        )
    
    def predict_batch(self, features_list: List[List[float]], 
                     transaction_ids: List[str] = None) -> List[PredictionResult]:
        """
        Predict fraud for multiple transactions
        
        Args:
            features_list: List of feature arrays
            transaction_ids: Optional list of transaction IDs
        
        Returns:
            List of PredictionResult objects
        """
        results = []
        
        for idx, features in enumerate(features_list):
            tx_id = transaction_ids[idx] if transaction_ids else f"TX{idx+1:05d}"
            result = self.predict_single(features, tx_id)
            results.append(result)
        
        return results
    
    def predict_from_dict(self, transaction_dict: Dict[str, float], 
                         transaction_id: str = "TX001") -> PredictionResult:
        """
        Predict fraud from transaction dictionary
        
        Args:
            transaction_dict: Dict with feature names as keys
            transaction_id: Transaction identifier
        
        Returns:
            PredictionResult object
        """
        # Extract features in correct order
        features = []
        for feature_name in self.feature_names:
            features.append(transaction_dict.get(feature_name, 0.0))
        
        return self.predict_single(np.array(features), transaction_id)
    
    def get_model_info(self) -> Dict:
        """
        Get model metadata and performance metrics
        
        Returns:
            Dict containing model information
        """
        return {
            "lr_auc": self.metadata.get("lr_auc"),
            "rf_auc": self.metadata.get("rf_auc"),
            "lr_f1": self.metadata.get("lr_f1"),
            "rf_f1": self.metadata.get("rf_f1"),
            "train_samples": self.metadata.get("train_samples"),
            "test_samples": self.metadata.get("test_samples"),
            "num_features": self.metadata.get("num_features"),
            "fraud_rate": self.metadata.get("train_fraud_rate")
        }
    
    def result_to_dict(self, result: PredictionResult) -> Dict:
        """
        Convert PredictionResult to dictionary
        
        Args:
            result: PredictionResult object
        
        Returns:
            Dictionary representation
        """
        return {
            "transaction_id": result.transaction_id,
            "lr_prediction": result.lr_prediction,
            "lr_probability": result.lr_probability,
            "rf_prediction": result.rf_prediction,
            "rf_probability": result.rf_probability,
            "consensus_prediction": result.consensus_prediction,
            "consensus_score": result.consensus_score,
            "is_fraud": result.consensus_prediction == 1
        }
    
    def result_to_json(self, result: PredictionResult) -> str:
        """
        Convert PredictionResult to JSON string
        
        Args:
            result: PredictionResult object
        
        Returns:
            JSON string
        """
        return json.dumps(self.result_to_dict(result), indent=2)


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    print("🔒 Fraud Detection API - Example Usage\n")
    
    # Initialize API
    api = FraudDetectionAPI("models")
    
    # Get model info
    print("📊 Model Information:")
    info = api.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 1: Single prediction with array
    print("Example 1: Single Transaction Prediction")
    sample_features = np.random.randn(30)
    result = api.predict_single(sample_features, "TX12345")
    print(api.result_to_json(result))
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Batch prediction
    print("Example 2: Batch Prediction (5 transactions)")
    batch_features = [np.random.randn(30) for _ in range(5)]
    batch_results = api.predict_batch(
        batch_features,
        transaction_ids=[f"TX{i}" for i in range(1, 6)]
    )
    
    fraud_count = sum(1 for r in batch_results if r.consensus_prediction == 1)
    print(f"Processed: {len(batch_results)} transactions")
    print(f"Fraudulent: {fraud_count} ({fraud_count/len(batch_results)*100:.1f}%)")
    
    for result in batch_results:
        print(f"  {result.transaction_id}: {result.consensus_score:.2%} fraud probability")
    
    print("\n✅ API Examples completed!")
