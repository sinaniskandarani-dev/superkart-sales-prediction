import joblib                       # load the serialized model pipeline
import pandas as pd                 # build model input DataFrames
from flask import Flask, request, jsonify

# Initialise the Flask app
superkart_api = Flask("SuperKart")

# Load the trained pipeline (preprocessing + tuned Random Forest) once at start-up
model = joblib.load("superkart_model.joblib")

# Features the model expects, in training order
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type",
    "Product_Id_char", "Store_Age_Years", "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    """Health check / welcome route."""
    return "Welcome to the SuperKart Sales Prediction API"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Online inference: predict sales for one product-store record sent as JSON."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Keep only the model features, as a one-row DataFrame
    input_df = pd.DataFrame([{f: data[f] for f in FEATURES}])
    prediction = float(model.predict(input_df)[0])
    return jsonify({"Sales": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Batch inference: predict sales for every row of an uploaded CSV file."""
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file under the form field 'file'"}), 400

    input_df = pd.read_csv(request.files["file"])
    missing = [f for f in FEATURES if f not in input_df.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    # Return the input rows together with their predicted sales
    output = input_df.copy()
    output["Predicted_Sales"] = model.predict(input_df[FEATURES]).round(2)
    return jsonify(output.to_dict(orient="records"))


# Local run for debugging; in the container the app is served by Gunicorn
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
