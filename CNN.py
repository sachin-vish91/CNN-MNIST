# Author : Sachin Vishwkarma

# Imports the important libraries 
import torch
import torchvision
import torch.nn.functional as F 
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torch import optim 
from torch import nn 
from torch.utils.data import DataLoader 
from tqdm import tqdm 

# CNN implementation 
class CNN(nn.Module):
    def __init__(self, in_channels=1, num_classes=10):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(
            in_channels = in_channels,
            out_channels = 8,
            kernel_size = (3, 3), # kernel size
            stride=(1, 1), # stride
            padding=(1, 1), # padding
        )
        self.pool = nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2)) #  apply max pooling
        self.conv2 = nn.Conv2d(
            in_channels=8,
            out_channels=16,
            kernel_size=(3, 3),
            stride=(1, 1),
            padding=(1, 1),
        )
        self.fc1 = nn.Linear(16 * 7 * 7, num_classes) # final layer for the prediction of the class
    
    # below is the code for the forward pass
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = x.reshape(x.shape[0], -1)
        x = self.fc1(x)
        
        return x


# Set device based in the available GPU or CPU machine
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Set the hyperparameter 
in_channels = 1
num_classes = 10
learning_rate = 0.001
batch_size = 64
num_epochs = 3

# Load MNIST data to perform the trainig here we can change the data based on our need
train_dataset = datasets.MNIST(root="dataset/", train=True, transform=transforms.ToTensor(), download=True)
test_dataset = datasets.MNIST(root="dataset/", train=False, transform=transforms.ToTensor(), download=True)
train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=True)

# Initialize network which is defined earlier
model = CNN(in_channels = in_channels, num_classes = num_classes).to(device)

# define loss (CrossEntropy) and optimizer (Adam)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr = learning_rate)

# Once we have done the setup of the model, its time to start training.
# To train the model we need to run the model based on the number of epoch 

for epoch in range(num_epochs):
    for batch_idx, (data, targets) in enumerate(tqdm(train_loader)):
        # set devise
        data = data.to(device=device)
        targets = targets.to(device=device)

        # forward pass
        scores = model(data)
        loss = criterion(scores, targets)

        # backward pass
        optimizer.zero_grad() # set the gradient to zero to avaoid accumulation of the gradient from previous epoch
        loss.backward() # back propogate the loss 

        # Optimization
        optimizer.step()

# Check the model performance
def check_accuracy(loader, model):
    num_correct = 0
    num_samples = 0
    model.eval()
    
    # set no_grad as in testing we do not need to calculate the gradient
    with torch.no_grad(): 
        for x, y in loader:
            x = x.to(device=device)
            y = y.to(device=device)

            scores = model(x)
            _, predictions = scores.max(1)
            num_correct += (predictions == y).sum()
            num_samples += predictions.size(0)


    model.train()
    return num_correct/num_samples

###################### Accuracy on trainig set. ##############
print(f"Accuracy: {check_accuracy(train_loader, model)*100:.2f}")

###################### Accuracy on test set. ##############
print(f"Accuracy: {check_accuracy(test_loader, model)*100:.2f}")
