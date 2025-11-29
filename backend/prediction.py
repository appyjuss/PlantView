import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
from torchvision.models import ResNet50_Weights
import torchvision.transforms as transforms
from PIL import Image
import os
import json
from io import BytesIO

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "resnet50_model.pth")
MAPPING_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "labels_mapping.json")

with open(MAPPING_PATH, 'r') as f:
    idx_to_class = json.load(f)

NUM_CLASSES = len(idx_to_class)


def load_model():
    model = models.resnet50(weights=ResNet50_Weights.DEFAULT)
    
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    
    state_dict = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
    model.load_state_dict(state_dict)
    
    model.eval()
    return model


model = load_model()


def predict_disease(image_path):
    
    transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                         std=[0.229, 0.224, 0.225]),
])
    
    image = Image.open(image_path).convert('RGB')
    img_tensor = transform(image).unsqueeze(0)  # Add batch dimension
    
    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = F.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
    
    class_id = predicted.item()
    confidence_score = float(confidence.item())
    class_name = idx_to_class[str(class_id)]
        
    return {
        "class_id": class_id,
        "confidence": round(confidence_score, 4),
        "class_name": class_name
    }


def predict_disease_from_bytes(image_bytes):
    """
    Accept raw image bytes and run the same preprocessing + model inference.
    Returns the same dict structure as `predict_disease`.
    """
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225]),
    ])
    img_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = F.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    class_id = predicted.item()
    confidence_score = float(confidence.item())
    class_name = idx_to_class.get(str(class_id))
    return {
        "class_id": class_id,
        "confidence": round(confidence_score, 4),
        "class_name": class_name
    }

