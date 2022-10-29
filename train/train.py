import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import torchvision
from torchvision import models, transforms
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score


input_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize((224,224)),
    #transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
])

def plt_data(data, index):
    LABELS = data.classes
    plt.title("No.{} , Class {}-{}".format(index, data[index][1], LABELS[data[index][1]]))
    plt.imshow(transforms.ToPILImage()(data[index][0]).convert('RGB'))
    

class ResNet(nn.Module):
    def __init__(self, out_features):
        super(ResNet, self).__init__()
        self.res = models.resnet50(weights='ResNet50_Weights.IMAGENET1K_V1')
        self.res.fc = nn.Linear(self.res.fc.in_features, out_features)
        self.softmax = nn.Softmax(dim = 1)
    def forward(self, x):
        output = self.res(x)
        return self.softmax(output)
    
    
if __name__ == "__main__":
    torch.manual_seed(59)
    data = torchvision.datasets.ImageFolder("datasets/", transform = input_transform)
    train_portion = int(len(data) * 0.7)
    test_portion = len(data) - train_portion
    train_data, test_data = torch.utils.data.random_split(data, [train_portion, test_portion])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ResNet(len(data.classes))
    model.to(device)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr = 0.001, momentum=0.9)
    batch_size = 32
    train_data_loader = torch.utils.data.DataLoader(train_data, batch_size = batch_size, shuffle = True)
    test_data_loader = torch.utils.data.DataLoader(test_data, batch_size = batch_size, shuffle = True)
    epochs = 5
    nBatch = len(train_data) // batch_size + 1
    model.train()
    for epoch in range(epochs):
        epoch_loss = 0
        epoch_accuracy = 0
        for iterations, (images, labels) in enumerate(train_data_loader):
            images = transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))(images).to(device)
            output = model(images)
            labels = labels.to(device)
            loss = loss_fn(output, labels).to(device)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            output_label = np.argmax(output.cpu().detach().numpy(), axis=1)
            accuracy = accuracy_score(output_label, labels.cpu().detach().numpy())
            epoch_accuracy += accuracy
            del images, output, labels, loss
        print("Epoch {} : [loss : {}, accuracy : {}]".format(epoch+1, epoch_loss / nBatch, epoch_accuracy / nBatch))
    del train_data_loader, train_data, optimizer
    torch.save({
        'epoch' : epoch + 1,
        'model_state_dict' : model.state_dict(),
        'loss' : epoch_loss,
        'accuracy' : epoch_accuracy
    }, "checkpoints/epoch_{}".format(epochs))  
    
    
    checkpoints = torch.load("checkpoints/epoch_{}".format(epochs), map_location='cpu')
    model = ResNet(len(data.classes))
    model.load_state_dict(checkpoints['model_state_dict'])
    print("Testing=======>")
    test_loss = 0
    test_accuracy = 0
    nTest = len(test_data) // batch_size + 1
    model.eval()
    for iterations, (images, labels) in enumerate(test_data_loader):
        images = transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))(images)
        output = model(images)
        
        loss = loss_fn(output, labels)
        test_loss += loss
        output_label = np.argmax(output.cpu().detach().numpy(), axis=1)
        accuracy = accuracy_score(output_label, labels.cpu().detach().numpy())
        test_accuracy += accuracy
    print("Testing results : [ loss : {}, accuracy : {} ]".format(test_loss / nTest, test_accuracy / nTest))
    
