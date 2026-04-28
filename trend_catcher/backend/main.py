from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend working"}

@app.get("/api/trends")
def trends():
    return {
        "trends": [
            {
                "hashtag": "#AITrend",
                "views": 120000,
                "prediction": "📈 Predicted: 312,000 views"
            },
            {
                "hashtag": "#TechNews",
                "views": 95000,
                "prediction": "📈 Predicted: 247,000 views"
            },
            {
                "hashtag": "#FoodTok",
                "views": 87000,
                "prediction": "📈 Predicted: 226,000 views"
            }
        ]
    }