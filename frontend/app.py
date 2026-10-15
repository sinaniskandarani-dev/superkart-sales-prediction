import pandas as pd
import requests
import streamlit as st

# The backend container is reachable by its container name on the shared Docker network
BACKEND_URL = "http://backend:7860"

st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecast")
st.write("Predict the total sales of a product in a SuperKart store.")

# Fixed attributes of SuperKart's existing stores (store age = 2025 - establishment year)
STORES = {
    "OUT001 - Supermarket Type1, Tier 2": {"Store_Size": "High", "Store_Location_City_Type": "Tier 2", "Store_Type": "Supermarket Type1", "Store_Age_Years": 39},
    "OUT002 - Food Mart, Tier 3": {"Store_Size": "Small", "Store_Location_City_Type": "Tier 3", "Store_Type": "Food Mart", "Store_Age_Years": 28},
    "OUT003 - Departmental Store, Tier 1": {"Store_Size": "Medium", "Store_Location_City_Type": "Tier 1", "Store_Type": "Departmental Store", "Store_Age_Years": 27},
    "OUT004 - Supermarket Type2, Tier 2": {"Store_Size": "Medium", "Store_Location_City_Type": "Tier 2", "Store_Type": "Supermarket Type2", "Store_Age_Years": 17},
}

# Product type -> (Product_Id_char, Product_Type_Category), as engineered during training
PRODUCT_FAMILY = {
    "Fruits and Vegetables": ("FD", "Perishables"), "Snack Foods": ("FD", "Non Perishables"),
    "Frozen Foods": ("FD", "Non Perishables"), "Dairy": ("FD", "Perishables"),
    "Baking Goods": ("FD", "Non Perishables"), "Canned": ("FD", "Non Perishables"),
    "Meat": ("FD", "Perishables"), "Breads": ("FD", "Perishables"),
    "Starchy Foods": ("FD", "Non Perishables"), "Breakfast": ("FD", "Perishables"),
    "Seafood": ("FD", "Perishables"), "Soft Drinks": ("DR", "Non Perishables"),
    "Hard Drinks": ("DR", "Non Perishables"), "Household": ("NC", "Non Perishables"),
    "Health and Hygiene": ("NC", "Non Perishables"), "Others": ("NC", "Non Perishables"),
}

FEATURES = ["Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
            "Store_Size", "Store_Location_City_Type", "Store_Type",
            "Product_Id_char", "Store_Age_Years", "Product_Type_Category"]

single_tab, batch_tab = st.tabs(["Single prediction", "Batch prediction"])

# ---------------- Single prediction ----------------
with single_tab:
    st.subheader("Product details")
    col1, col2 = st.columns(2)
    with col1:
        product_type = st.selectbox("Product type", sorted(PRODUCT_FAMILY))
        sugar = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
        weight = st.number_input("Product weight", min_value=4.0, max_value=22.0, value=12.66, step=0.1)
    with col2:
        mrp = st.number_input("Product MRP", min_value=31.0, max_value=266.0, value=147.0, step=1.0)
        area = st.number_input("Allocated display area (ratio)", min_value=0.004, max_value=0.3,
                               value=0.068, step=0.001, format="%.3f")

    id_char, category = PRODUCT_FAMILY[product_type]
    st.caption(f"Product family: {id_char} | Category: {category}")

    st.subheader("Store details")
    store_choice = st.selectbox("Store", list(STORES) + ["Other / new store"])
    if store_choice in STORES:
        store = STORES[store_choice]
        st.caption(f"Size: {store['Store_Size']} | City: {store['Store_Location_City_Type']} | "
                   f"Type: {store['Store_Type']} | Age: {store['Store_Age_Years']} years")
    else:
        col3, col4 = st.columns(2)
        with col3:
            size = st.selectbox("Store size", ["Small", "Medium", "High"])
            tier = st.selectbox("City tier", ["Tier 1", "Tier 2", "Tier 3"])
        with col4:
            store_type = st.selectbox("Store type", ["Supermarket Type1", "Supermarket Type2",
                                                     "Departmental Store", "Food Mart"])
            age = st.number_input("Store age (years)", min_value=0, max_value=60, value=10)
        store = {"Store_Size": size, "Store_Location_City_Type": tier,
                 "Store_Type": store_type, "Store_Age_Years": int(age)}

    payload = {
        "Product_Weight": weight, "Product_Sugar_Content": sugar,
        "Product_Allocated_Area": area, "Product_MRP": mrp,
        "Product_Id_char": id_char, "Product_Type_Category": category, **store,
    }

    if st.button("Predict sales", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                st.success(f"Predicted Product Store Sales Total: {response.json()['Sales']:,.2f}")
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as err:
            st.error(f"Could not reach the prediction API: {err}")

# ---------------- Batch prediction ----------------
with batch_tab:
    st.write("Upload a CSV with these columns:")
    st.code(", ".join(FEATURES))
    uploaded_file = st.file_uploader("CSV file", type=["csv"])

    if uploaded_file is not None and st.button("Predict for batch", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predictbatch",
                                     files={"file": uploaded_file.getvalue()}, timeout=60)
            if response.status_code == 200:
                results = pd.DataFrame(response.json())
                st.success(f"Predictions completed for {len(results)} rows.")
                st.dataframe(results, use_container_width=True)
                st.download_button("Download predictions", results.to_csv(index=False),
                                   file_name="superkart_predictions.csv", mime="text/csv")
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as err:
            st.error(f"Could not reach the prediction API: {err}")
