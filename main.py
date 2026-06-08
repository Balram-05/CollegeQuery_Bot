import uvicorn
from fastapi import FastAPI, HTTPException, status
from src.schema.schema import UserAuthModel, ChatQueryModel
from src.pipelines.auth_pipeline import AuthPipeline
from src.pipelines.predict_pipeline import PredictPipeline

app = FastAPI(title="College Query Assistant Modular Backend API", version="1.0")

# Initialize Pipeline Interfaces
auth_pipeline = AuthPipeline()
predict_pipeline = PredictPipeline()

@app.get("/")
def read_root():
    return {"status": "Healthy", "message": "College Query Core Engine Online Engine"}

@app.post("/api/register")
def register(user: UserAuthModel):
    success = auth_pipeline.register_user(user.username, user.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Registration failed. Username might be unavailable."
        )
    return {"message": "User registration successful"}

@app.post("/api/login")
def login(user: UserAuthModel):
    authenticated = auth_pipeline.login_user(user.username, user.password)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid username or password credentials."
        )
    return {"message": "Authentication verified successfully"}

@app.post("/api/chat")
def chat(payload: ChatQueryModel):
    try:
        reply = predict_pipeline.generate_response(payload.question, payload.thread_id)
        return {"response": reply}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating a response: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
