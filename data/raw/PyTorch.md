---
id: PyTorch
aliases:
  - PyTorch
tags: []
---
# PyTorch

<!-- toc -->

- [What is PyTorch?](#what-is-pytorch)
- [***Tensors***](#tensors)
- [Implementating Classification problem using PyTorch](#implementating-classification-problem-using-pytorch)
    * [importing necessary libraries](#importing-necessary-libraries)
    * [Preparing data](#preparing-data)
    * [Defining Neural Network](#defining-neural-network)
    * [Definiing Loss Function, Optimiser, and Scheduler](#definiing-loss-function-optimiser-and-scheduler)
    * [Defining Function for Metrics calculation](#defining-function-for-metrics-calculation)
    * [Defining model, Loss, Optimiser, Weight Initialization](#defining-model-loss-optimiser-weight-initialization)
    * [Model Training and Evaluation](#model-training-and-evaluation)
- [Implementation in TensorFlow](#implementation-in-tensorflow)

<!-- tocstop -->

## What is PyTorch?

PyTorch is a Python-based scientific computing package serving two broad purposes:

  - A replacement for NumPy to use the power of GPUs and other accelerators.
  - An automatic differentiation library that is useful to implement neural networks.

From <https://docs.pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html>

## ***Tensors***

Tensors are a specialized data structure that are very similar to arrays and matrices. In PyTorch, we use tensors to encode the inputs and outputs of a model, as well as the model’s parameters.

Tensors are similar to NumPy’s ndarrays, except that tensors can run on GPUs or other hardware accelerators. In fact, tensors and NumPy arrays can often share the same underlying memory, eliminating the need to copy data (see Bridge with NumPy). Tensors are also optimized for automatic differentiation (we’ll see more about that later in the Autograd section). If you’re familiar with ndarrays, you’ll be right at home with the Tensor API. If not, follow along!


## Implementating Classification problem using PyTorch

### importing necessary libraries
```py
from torch.utils.data import TensorDataset, DataLoader
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import KFold
```
### Preparing data
```python
## Converting DataFrame / arrays to tensors
x_train_tensors = torch.tensor(data=x_train, dtype=torch.float32)
y_train_tensors = torch.tensor(data=y_train, dtype=torch.float32).unsqueeze(1)
x_test_tensors = torch.tensor(data=x_test,dtype=torch.float32)
y_test_tensors = torch.tensor(data=y_test,dtype=torch.float32).unsqueeze(1)

train_ds = TensorDataset(x_train_tensors,y_train_tensors)
test_ds = TensorDataset(x_test_tensors,y_test_tensors)
train_loader = DataLoader(train_ds, batch_size=512, shuffle=True)
test_loader  = DataLoader(test_ds, batch_size=512, shuffle=False)

```
### Defining Neural Network
```python
import torch.nn as nn
ANN_model = nn.Sequential(
    nn.Linear(22,64),
    nn.BatchNorm1d(64),
    nn.LeakyReLU(),
    nn.Dropout(0.2),
    nn.Linear(64,32),
    nn.BatchNorm1d(32),
    nn.LeakyReLU(),
    nn.Dropout(0.2),
    nn.Linear(32,1)
)
```
### Definiing Loss Function, Optimiser, and Scheduler
```python
criterion = nn.BCEWithLogitsLoss()
import torch.optim as optim
optimiser = optim.NAdam(ANN_model.parameters(),lr=0.005)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimiser, mode="min", patience=5, factor=0.5
)
```
### Defining Function for Metrics calculation

```python

# 
def evaluate(model, loader, criterion, threshold=0.5):
    """
     Defines a reusable evaluation function. 
     Takes model, data loader, loss function, 
     and classification threshold (default 0.5)
    """
    model.eval()  # Switches model to evaluation mode → disables Dropout & makes BatchNorm use running statistics instead of batch statistics

    # Initializes accumulators for total loss, predicted probabilities, and true labels
    running_loss = 0.0
    all_probs, all_targets = [], []

    with torch.no_grad(): #Disables gradient computation → saves memory & speeds up inference (no need to track gradients when not training)
        for x_batch, y_batch in loader:  #Iterates over mini-batches from the data loader
            outputs = model(x_batch) #FORWARD PASS → raw logits (unnormalized scores) flow through all layers
            loss = criterion(outputs, y_batch) #LOSS CALCULATION → computes BCE loss between predictions and true labels

            running_loss += loss.item() #adding or appending loss. .item() extract python float from tensor 
            probs = torch.sigmoid(outputs) # applying sigmoid function to sqash probabilities (0 to 1). Note: BCEWithLogitsLoss does this internally during training, but here we need explicit probabilities for metrics


            #.squeeze() removes dimensions of size 1 (e.g., shape [32,1] → [32])
            # .cpu() moves tensor from GPU to CPU
            #.numpy() converts to NumPy for sklearn metrics
            all_probs.extend(probs.squeeze().cpu().numpy())
            all_targets.extend(y_batch.squeeze().cpu().numpy())

    preds = [1 if p > threshold else 0 for p in all_probs] #Converts probabilities to binary predictions using threshold (0.5 by default)

    # Returns dictionary of all metrics computed by sklearn 
    return {
        "loss": running_loss / len(loader),
        "acc": accuracy_score(all_targets, preds),
        "Prec":precision_score(all_targets,preds),
        "Rec":recall_score(all_targets,preds),
        "f1": f1_score(all_targets, preds),
        "auc": roc_auc_score(all_targets, all_probs),
    }
```

### Defining model, Loss, Optimiser, Weight Initialization
```python

#Defining model
ANN_model_k = nn.Sequential( # Creates a feedforward neural network (ANN) where layers execute sequentially
    nn.Linear(22,64), #Fully connected layer: 22 input features → 64 neuronsWeight matrix W (64×22) and bias vector b (64)

    # It normalizes the output of the previous layer to have zero mean and unit variance for each mini‑batch.
    nn.BatchNorm1d(64), # Batch Normalization: normalizes activations across the batch
    nn.LeakyReLU(), # Activation function. Leaky fixes dying ReLU problem (negative value still get a smaller gradient)
    nn.Dropout(0.25), # Regularization: randomly zeros 25% of neurons during training. Prevents overfitting by forcing the network not to rely on specific neurons
                            
# hidden layer with activation + dropout
    nn.Linear(64,32),
    nn.LeakyReLU(),
    nn.Dropout(0.25),
    
    # output layer. No sigmoid here because BCEWithLogitsLoss applies it internally (numerically stable)
    nn.Linear(32,1)
)

# Defining Loss, optimiser, Scheduler
criterion = nn.BCEWithLogitsLoss() # Binary Cross-Entropy with Logits. #Combines sigmoid + BCE in one numerically stable operation
optimiser = optim.NAdam(ANN_model_k.parameters(),lr=0.005) #Nesterov (momentum) + Adam optimizer
# LEARNING RATE SCHEDULER
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimiser, mode="min", patience=5, factor=0.5
)

# Weight Initialization
def init_kaiming(m):
    if isinstance(m, nn.Linear):
        nn.init.kaiming_normal_(m.weight, mode="fan_in", nonlinearity="leaky_relu")
        if m.bias is not None:
            nn.init.zeros_(m.bias)

ANN_model_k.apply(init_kaiming)
```
### Model Training and Evaluation
```py
epochs = 50

train_losses = []
val_losses = []

for epoch in range(epochs):
    ANN_model_k.train() # Switches back to training mode → enables Dropout & batch statistics in BatchNorm
    running_loss = 0.0
    for x_batch, y_batch in train_loader: #Iterates over mini-batches of training data
        optimiser.zero_grad() #Clears gradients from previous batch. PyTorch accumulates gradients by default, so this must be called before each backward pass
        outputs = ANN_model_k(x_batch) #FORWARD PASS: data flows through all layers:
        loss = criterion(outputs, y_batch) #LOSS CALCULATION: measures how wrong the predictions are

        loss.backward() # BACKWARD PASS: computes gradients of loss w.r.t. every parameter using chain rule

        optimiser.step() #WEIGHT & BIAS UPDATE: updates all parameters using NAdam rule: Every nn.Linear weight matrix and bias vector gets updated here

        running_loss += loss.item() #Accumulates batch loss for monitoring

    avg_loss = running_loss / len(train_loader)
    train_metrics = evaluate(ANN_model_k, train_loader, criterion)
    val_metrics   = evaluate(ANN_model_k, test_loader, criterion)
    train_losses.append(train_metrics["loss"])
    val_losses.append(val_metrics["loss"])

    scheduler.step(val_metrics["loss"])

    print(
        f"Epoch {epoch+1:02d} | "
        f"TrainLoss {train_metrics['loss']:.4f} | "
        f"ValLoss {val_metrics['loss']:.4f} | "
        f"TrainAcc {train_metrics['acc']:.3f} | "
        f"ValAcc {val_metrics['acc']:.3f} | "
        f"TrainPre {train_metrics['Prec']:.3f} | "
        f"ValPre {val_metrics['Prec']:.3f} | "
        f"TrainRec {train_metrics['Rec']:.3f} | "
        f"ValRec {val_metrics['Rec']:.3f} | "
        f"TrainAUC {train_metrics['auc']:.3f} | "
        f"ValAUC {val_metrics['auc']:.3f}"
    )
```

## Implementation in TensorFlow

  - import tensorflow as tf
  - from tensorflow.keras.models import Sequential
  - from tensorflow.keras.layers import Dense
  - from tensorflow.keras.callbacks import EarlyStopping,TensorBoard
  - import datetime
  - from tensorflow.keras.callbacks import EarlyStopping,TensorBoard
  - from scikeras.wrappers import KerasClassifier




  - Sequential Network to do Forward and backward prop
  - Hidden Neuron (Dense)
  - Activation Function (Singmoid, Tanh, ReLU)
  - Optimiser (updates weights in the backward Prop)
  - Loss Function
  - Metrics 
  - Training Logs (Tensorboard)
















