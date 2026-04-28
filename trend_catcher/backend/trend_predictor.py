import numpy as np
from sklearn.linear_model import LinearRegression

def predict_trend_growth(view_counts):
    days = np.array(range(1, len(view_counts)+1)).reshape(-1, 1)
    views = np.array(view_counts).reshape(-1, 1)

    model = LinearRegression()
    model.fit(days, views)

    prediction = model.predict([[21]])
    return int(prediction[0][0])