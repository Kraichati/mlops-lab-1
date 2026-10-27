

import os
import io
from contextlib import asynccontextmanager

import mlflow
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

@asynccontextmanager
async def lifespan(app: FastAPI):
    mlflow.set_tracking_uri(
        os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    )

    app.state.model = mlflow.pyfunc.load_model(
        "models:/food11@champion"
    )

    print("Model loaded successfully!")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


CLASS_NAMES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]


transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])


@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)):

    # 1. Read the uploaded image
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )

    # 2. Apply the same preprocessing as training
    image_tensor = transform(image).unsqueeze(0)

    # 3. Predict using our registered MLflow model
    outputs = request.app.state.model.predict(
        image_tensor.numpy()
    )

    # 4. Convert model scores into probabilities
    probabilities = torch.softmax(
        torch.as_tensor(outputs[0]), dim=0
    )

    # 5. Find the predicted food category
    predicted_index = int(probabilities.argmax().item())

    # 6. Return the prediction
    return {
        "category": CLASS_NAMES[predicted_index],
        "confidence": float(probabilities[predicted_index].item())
    }
