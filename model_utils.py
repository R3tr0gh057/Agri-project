# model_utils.py

import warnings
from huggingface_hub import hf_hub_download
from transformers import AutoModelForImageClassification
import torch
from torchvision import transforms
from PIL import Image

# Suppress specific UserWarnings
warnings.filterwarnings(
    "ignore",
    message="Some weights of .* were not initialized from the model checkpoint",
    category=UserWarning,
    module="transformers"
)

# Load the model with custom weights
def load_model():
    model_path = hf_hub_download(repo_id="someoneskilled/kheeramodel_v1", filename="plant_disease_classifier (1).pth")
    model = AutoModelForImageClassification.from_pretrained(
        'microsoft/resnet-50', num_labels=4, ignore_mismatched_sizes=True
    )
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=True))
    model.eval()
    return model

# Initialize model once
model = load_model()

# Image transformations
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Prediction function
def predict_image(image: Image.Image):
    img_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(img_tensor)
    _, predicted = torch.max(output.logits, 1)
    return predicted.item()
