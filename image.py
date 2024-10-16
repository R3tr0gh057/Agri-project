# Import necessary libraries
import warnings
from huggingface_hub import hf_hub_download
from transformers import AutoModelForImageClassification, AutoFeatureExtractor
import torch
from torchvision import transforms
from PIL import Image

# Suppress specific UserWarnings regarding shape mismatches
warnings.filterwarnings(
    "ignore",
    message="Some weights of .* were not initialized from the model checkpoint",
    category=UserWarning,
    module="transformers"
)

# Step 1: Download and load the model from Hugging Face Hub
def load_model():
    # Download the model weights file from Hugging Face
    model_path = hf_hub_download(repo_id="someoneskilled/kheeramodel_v1", filename="plant_disease_classifier (1).pth")
    
    # Load the pre-trained ResNet model with custom weights
    model = AutoModelForImageClassification.from_pretrained(
        'microsoft/resnet-50', num_labels=4, ignore_mismatched_sizes=True
    )
    
    # Load the saved weights into the model, setting weights_only=True for safety
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=True))
    
    # Set the model to evaluation mode
    model.eval()
    return model

# Step 2: Define image transformations that match the model's training process
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Step 3: Load and preprocess the image
def preprocess_image(image_path):
    # Load the image from the specified path
    img = Image.open(image_path).convert("RGB")  # Ensure 3-channel image (RGB)
    # Apply transformations
    img_tensor = transform(img).unsqueeze(0)  # Add a batch dimension
    return img_tensor

# Step 4: Make a prediction
def predict(model, img_tensor):
    # Run inference without tracking gradients
    with torch.no_grad():
        output = model(img_tensor)
    
    # Get the index of the highest score
    _, predicted = torch.max(output.logits, 1)
    return predicted.item()

# Main execution code
if __name__ == "__main__":
    # Load the model
    model = load_model()
    
    # Define the path to your image
    image_path = input("Path to your image: ")

    # Preprocess the image
    img_tensor = preprocess_image(image_path)

    # Make a prediction
    predicted_class = predict(model, img_tensor)
    # print(f'Predicted class index: {predicted_class}')
    
    predictions = {
        0: 'Potassium defficiency',
        1: 'Healthy',
        2: 'Potassium and Nitrogen defficiency',
        3: 'Nitrogen defficiency'
    }

    # Print the predicted class label
    print(f'Predicted class: {predictions[predicted_class]}')
