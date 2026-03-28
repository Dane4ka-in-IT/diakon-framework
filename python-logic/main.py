import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from engine import Dense, Relu, Sigmoid
from losses import MSE, CrossEntropy
from optimizers import SGD, MomentumSGD, GradClipper

app = FastAPI()

class TrainRequest(BaseModel):
    layers: list[int]
    optimizer: str
    epochs: int
    learning_rate: float
    dataset: str

class DataLoader:
    def __init__(self, X, y, batch_size=32, shuffle=True):
        self.X = X
        self.y = y
        self.batch_size = batch_size
        self.shuffle = shuffle

    def __iter__(self):
        m = self.X.shape[0]
        indices = np.arange(m)
        if self.shuffle:
            np.random.shuffle(indices)
        
        for i in range(0, m, self.batch_size):
            batch_idx = indices[i:i + self.batch_size]
            yield self.X[batch_idx], self.y[batch_idx]

class NeuralNetwork:
    def __init__(self):
        self.layers = []
        self.loss_func = None

    def add(self, layer):
        self.layers.append(layer)

    def compile(self, loss_func, optimizer):
        self.loss_func = loss_func
        self.optimizer = optimizer

    def forward(self, X):
        out = X
        for layer in self.layers:
            out = layer.forward(out)
        return out

    def backward(self, grad_output):
        for layer in reversed(self.layers):
            grad_output = layer.backward(grad_output)

    def fit(self, X, y, epochs=10, batch_size=32):
        history = []
        loader = DataLoader(X, y, batch_size)
        
        for epoch in range(epochs):
            epoch_loss = 0
            batches = 0
            for X_batch, y_batch in loader:
                y_pred = self.forward(X_batch)
                loss = self.loss_func.forward(y_pred, y_batch)
                epoch_loss += loss
                
                grad = self.loss_func.backward(y_pred, y_batch)
                self.backward(grad)
                self.optimizer.step(self.layers)
                batches += 1
                
            history.append(float(epoch_loss / batches))
        return history

def get_dummy_data(dataset_name):
    if dataset_name == "mnist":
        X = np.random.randn(1000, 784)
        y = np.zeros((1000, 10))
        for i in range(1000):
            y[i, np.random.randint(0, 10)] = 1
        return X, y
    elif dataset_name == "iris":
        X = np.random.randn(150, 4)
        y = np.zeros((150, 3))
        for i in range(150):
            y[i, np.random.randint(0, 3)] = 1
        return X, y
    return np.random.randn(100, 10), np.random.randn(100, 2)

@app.post("/train")
def train_model(req: TrainRequest):
    X, y = get_dummy_data(req.dataset)
    
    model = NeuralNetwork()
    
    in_features = X.shape[1]
    for units in req.layers:
        model.add(Dense(in_features, units))
        model.add(Relu())
        in_features = units
        
    out_features = y.shape[1]
    model.add(Dense(in_features, out_features))
    
    if req.dataset == "mnist" or req.dataset == "iris":
        model.add(Sigmoid())
        loss = CrossEntropy()
    else:
        loss = MSE()

    if req.optimizer == "SGD":
        opt = SGD(req.learning_rate)
    elif req.optimizer == "Momentum":
        opt = MomentumSGD(req.learning_rate)
    elif req.optimizer == "Clipping":
        opt = GradClipper(SGD(req.learning_rate))
    else:
        opt = SGD(req.learning_rate)

    model.compile(loss, opt)
    history = model.fit(X, y, epochs=req.epochs, batch_size=32)
    
    return {
        "status": "success",
        "dataset": req.dataset,
        "history": history
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)