import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms

from dataset import MultiImageDataset  # Assuming dataset.py is in the same directory

# Define the neural network architecture
class MultiLabelNet(nn.Module):
    def __init__(self, num_classes):
        super(MultiLabelNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, 1, 1)
        self.conv2 = nn.Conv2d(16, 32, 3, 1, 1)
        self.fc1 = nn.Linear(19520, 128)  # Adjusted the input features to 19520
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = nn.functional.relu(self.conv1(x))
        #print(x)
        x = nn.functional.max_pool2d(x, 2)
        x = nn.functional.relu(self.conv2(x))
        x = nn.functional.max_pool2d(x, 2)
        x = torch.flatten(x, 1)

        #print("Flattened size:", x.shape)  # Debugging line to check the size

        x = nn.functional.relu(self.fc1(x))
        x = torch.sigmoid(self.fc2(x))
        return x


# Load and preprocess the dataset
transform = transforms.Compose([
    transforms.Resize((42, 247)),
    transforms.ToTensor()
])

trainDataset = MultiImageDataset(r"C:\Users\ziggy\Documents\GitHub\bloxburg-fast-food-neural-net\backup\train", transform=transform)
TestDataset = MultiImageDataset(r"C:\Users\ziggy\Documents\GitHub\bloxburg-fast-food-neural-net\labledData\test", transform=transform)

train_loader = DataLoader(trainDataset, batch_size=32, shuffle=True)
train_loader2 = DataLoader(trainDataset, batch_size=1, shuffle=False)
test_loader = DataLoader(TestDataset, batch_size=1, shuffle=False)

#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#print(f"Using device: {device}")

# Initialize the model
model = MultiLabelNet(num_classes=30)  # Set the number of classes based on your label list
#model.to(device)
# Define the loss function and optimizer
criterion = nn.BCELoss()  # Suitable for multi-label classification
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Train the model
for epoch in range(100):  # loop over the dataset multiple times
    print("Epoch:", epoch)
    for i, (image, labels) in enumerate(train_loader, 0):
        #image, labels = image.to(device), labels.to(device)  # Move data to device
        optimizer.zero_grad()
        outputs = model(image)
        loss = criterion(outputs, labels.float())  # Labels need to be float type for BCELoss
        loss.backward()
        optimizer.step()

# Add your evaluation code here as needed
def accuracy(outputs, labels):
    with torch.no_grad():
        predictions = outputs > 0.5  # Threshold for multi-label classification
        correct = (predictions == labels).float()  # Convert to float for division
        accuracy = correct.sum() / correct.numel()
    return accuracy

model.eval()  # Set the model to evaluation mode
total_accuracy = 0
total_samples = 0

# Evaluate the model
for inputs, labels in test_loader:
    #inputs, labels = inputs.to(device), labels.to(device)  # Move data to device
    outputs = model(inputs)
    predictions = outputs > 0.5
    print(outputs)
    print(predictions)
    print(labels)
    if torch.equal(predictions, labels):

        print(True)
    else:
        print(False)

    print()

    acc = accuracy(outputs, labels)
    total_accuracy += acc.item() * inputs.size(0)
    total_samples += inputs.size(0)

# Calculate the average accuracy over all samples
average_accuracy = total_accuracy / total_samples
print(f'Average Accuracy: {average_accuracy:.4f}')