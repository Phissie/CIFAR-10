# -*- coding: utf-8 -*-
"""Lab3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13oQgETdzDPr0vCTFrJwkKLDvUu9dH56J

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rpi-techfundamentals/fall2018-materials/blob/master/10-deep-learning/04-pytorch-mnist.ipynb)
"""

!pip install torch torchvision

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split
from PIL import Image
import os

batch_size_train = 64
batch_size_test = 1000
learning_rate = 0.01
num_epochs = 2

# CIFAR-10 dataset with normalization
transform = transforms.Compose([transforms.ToTensor(),
                                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

dataset = datasets.CIFAR10(root='./data', train=True, transform=transform, download=True)
train_size = int(0.8 * len(dataset))
validate_size = int(0.1 * len(dataset))
test_size = len(dataset) - train_size - validate_size
train_dataset, validate_dataset, test_dataset = random_split(dataset, [train_size, validate_size, test_size])

train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size_train, shuffle=True)
validate_loader = DataLoader(dataset=validate_dataset, batch_size=batch_size_test, shuffle=False)
test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size_test, shuffle=False)

class CnnNet(nn.Module):
    def __init__(self):
        super(CnnNet, self).__init__()

        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)

        self.fc1 = nn.Linear(128 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, 10)

    def forward(self, x):

        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))

        x = x.view(-1, 128 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)

        return F.log_softmax(x, dim=1)


model = CnnNet()
optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.5)

best_model = None
best_accuracy = 0

def train(epoch):
    model.train()
    total_loss = 0
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

        if (batch_idx + 1) % 100 == 0:
            print(f'Epoch {epoch}, Batch {batch_idx + 1}: Current Loss = {total_loss / (batch_idx + 1):.4f}')

    average_loss = total_loss / len(train_loader)
    print(f'Epoch {epoch} Training Loss: {average_loss:.4f}')

def validate(epoch):
    global best_model, best_accuracy
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for data, target in validate_loader:
            output = model(data)
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)

    accuracy = 100. * correct / total
    print(f'Epoch {epoch} Validation Accuracy: {accuracy:.2f}%')

    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = model.state_dict()
        # Save the best model
        torch.save(best_model, 'best_cnn_model.pth')
        print("Best model saved with accuracy: {:.2f}%".format(best_accuracy))

def test():
    # Load the best model for testing
    model.load_state_dict(torch.load('best_cnn_model.pth'))
    model.eval()
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    accuracy = 100. * correct / len(test_loader.dataset)
    print(f'Test Accuracy: {accuracy:.2f}%')

for epoch in range(1, num_epochs + 1):
    train(epoch)
    validate(epoch)
    print('\n')

test()

from google.colab import files
from PIL import Image as PILImage

# Function to predict an uploaded image
def predict_uploaded_image(image_path):
    # Transform for the uploaded image
    transform = transforms.Compose([
        transforms.Resize((32, 32)),  # Resize to the same dimensions as CIFAR-10 images.
        transforms.ToTensor(),  # Convert the image to a tensor.
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))  # Normalize like CIFAR-10 images.
    ])

    # Load the image
    # image = Image.open(image_path)
    image = PILImage.open(image_path).convert('RGB')  # Convert image to RGB
    image = transform(image).unsqueeze(0)  # Add a batch dimension

    # Load the best model
    model.load_state_dict(torch.load('best_cnn_model.pth'))
    model.eval()  # Set the model to evaluation mode

    # Make a prediction
    with torch.no_grad():
        output = model(image)
        _, predicted = torch.max(output, 1)

    # Convert the predicted index to the corresponding class
    classes = ['plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
    predicted_class = classes[predicted.item()]

    return predicted_class

# Step 1: Upload an image file
uploaded = files.upload()

# Assuming the user will upload only one image file
image_path = next(iter(uploaded.keys()))
print(f"Uploaded file: {image_path}")

# Step 2: Predict the class of the uploaded image
predicted_class = predict_uploaded_image(image_path)
print(f"The uploaded image is predicted to be: {predicted_class}")

"""More product-oriented"""