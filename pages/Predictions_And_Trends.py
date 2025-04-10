import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
import datetime
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

DB_PATH = "data/user_data.db"

def load_metrics():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT date, weight, fat_percent FROM body_metrics ORDER BY date", conn)
    conn.close()
    return df

def predict_future(df, target_days=30):
    if df.empty or df.shape[0] < 2:
        return None

    df['date'] = pd.to_datetime(df['date'])
    df['days_since_start'] = (df['date'] - df['date'].min()).dt.days

    X = df[['days_since_start']]
    preds = {}

    for col in ['weight', 'fat_percent']:
        if df[col].isnull().any():
            continue
        y = df[col]
        model = LinearRegression()
        model.fit(X, y)

        future_days = np.arange(df['days_since_start'].max() + 1,
                                df['days_since_start'].max() + target_days + 1).reshape(-1, 1)
        predictions = model.predict(future_days)

        future_dates = [df['date'].max() + datetime.timedelta(days=i) for i in range(1, target_days + 1)]
        preds[col] = pd.DataFrame({'date': future_dates, col: predictions})

    return preds

# -------- Streamlit UI --------
st.title("📊 Predictions & Trends")

metrics_df = load_metrics()

if metrics_df.empty:
    st.warning("No body metrics data found. Please log weight and fat% in the 'Body Metrics' tab first.")
    st.stop()

st.subheader("📈 Historical Trends")
st.line_chart(metrics_df.set_index("date")[['weight', 'fat_percent']])

st.subheader("🔮 Future Predictions")
days = st.slider("Predict for how many days ahead?", 7, 90, 30)

predictions = predict_future(metrics_df, days)

if predictions:
    for key, df in predictions.items():
        st.markdown(f"**Predicted {key.replace('_', ' ').title()}**")
        st.line_chart(df.set_index("date"))
else:
    st.info("Not enough data to predict. Please log more metrics over time.")

st.divider()
st.markdown("📌 In the next version: simulate the effect of adding/removing foods to see predicted body change!")
