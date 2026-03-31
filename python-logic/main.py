import numpy as np
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from engine import Dense, Relu, Sigmoid, Softmax
from losses import MSE, CrossEntropy
from optimizers import SGD, MomentumSGD, GradClipper
from sklearn.datasets import load_iris, load_digits
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import pickle

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

trained_models = {}

class TrainRequest(BaseModel):
    layers: List[int]
    optimizer: str
    epochs: int
    learning_rate: float
    dataset: str

class PredictRequest(BaseModel):
    features: List[float]
    dataset: str

class DataLoader:
    def __init__(self, X, y, batch_size=32, shuffle=True):
        self.X = X
        self.y = y
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.transform = None

    def map(self, transform_func):
        self.transform = transform_func
        return self

    def __iter__(self):
        m = self.X.shape[0]
        indices = np.arange(m)
        if self.shuffle:
            np.random.shuffle(indices)
        
        for i in range(0, m, self.batch_size):
            batch_idx = indices[i:i + self.batch_size]
            X_batch = self.X[batch_idx]
            y_batch = self.y[batch_idx]
            
            if self.transform:
                X_batch, y_batch = self.transform(X_batch, y_batch)
                
            yield X_batch, y_batch

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

    def fit(self, X, y, epochs=10, batch_size=32, callbacks=None):
        history = []
        loader = DataLoader(X, y, batch_size)
        callbacks = callbacks or []
        
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
                
            avg_loss = float(epoch_loss / batches)
            history.append(avg_loss)
            logs = {'loss': avg_loss}
            stop = False
            for cb in callbacks:
                cb.on_epoch_end(epoch, logs)
                if getattr(cb, 'stop_training', False):
                    stop = True
            if stop:
                break
        return history

    def set_training(self, mode=True):
        for layer in self.layers:
            if hasattr(layer, 'training'):
                layer.training = mode

    def save_weights(self, filepath):
        weights = []
        for layer in self.layers:
            layer_data = {}
            if hasattr(layer, 'w'): layer_data['w'] = layer.w
            if hasattr(layer, 'b'): layer_data['b'] = layer.b
            if hasattr(layer, 'gamma'): layer_data['gamma'] = layer.gamma
            if hasattr(layer, 'beta'): layer_data['beta'] = layer.beta
            if hasattr(layer, 'running_mean'): layer_data['running_mean'] = layer.running_mean
            if hasattr(layer, 'running_var'): layer_data['running_var'] = layer.running_var
            weights.append(layer_data)
        with open(filepath, 'wb') as f:
            pickle.dump(weights, f)

    def load_weights(self, filepath):
        with open(filepath, 'rb') as f:
            weights = pickle.load(f)
        for layer, layer_data in zip(self.layers, weights):
            if 'w' in layer_data: layer.w = layer_data['w']
            if 'b' in layer_data: layer.b = layer_data['b']
            if 'gamma' in layer_data: layer.gamma = layer_data['gamma']
            if 'beta' in layer_data: layer.beta = layer_data['beta']
            if 'running_mean' in layer_data: layer.running_mean = layer_data['running_mean']
            if 'running_var' in layer_data: layer.running_var = layer_data['running_var']

def get_real_data(dataset_name):
    encoder = OneHotEncoder(sparse_output=False)
    scaler = StandardScaler()
    
    if dataset_name == "mnist":
        data = load_digits()
        X = scaler.fit_transform(data.data)
        y = encoder.fit_transform(data.target.reshape(-1, 1))
        return X, y, scaler
    elif dataset_name == "iris":
        data = load_iris()
        X = scaler.fit_transform(data.data)
        y = encoder.fit_transform(data.target.reshape(-1, 1))
        return X, y, scaler
        
    X = np.random.randn(100, 10)
    y = np.random.randn(100, 2)
    return X, y, None

@app.post("/train")
def train_model(req: TrainRequest):
    X, y, scaler = get_real_data(req.dataset)
    model = NeuralNetwork()
    
    in_features = X.shape[1]
    for units in req.layers:
        model.add(Dense(in_features, units))
        model.add(Relu())
        in_features = units
        
    out_features = y.shape[1]
    model.add(Dense(in_features, out_features))
    
    if req.dataset in ["mnist", "iris"]:
        model.add(Softmax())
        loss = CrossEntropy()
    else:
        loss = MSE()

    if req.optimizer == "SGD":
        opt = SGD(req.learning_rate)
    elif req.optimizer == "Momentum":
        opt = MomentumSGD(req.learning_rate, momentum=0.9)
    elif req.optimizer == "Clipping":
        opt = GradClipper(SGD(req.learning_rate), clip_value=1.0)
    else:
        opt = SGD(req.learning_rate)

    model.compile(loss, opt)
    history = model.fit(X, y, epochs=req.epochs, batch_size=32)

    trained_models[req.dataset] = {"model": model, "scaler": scaler}
    
    return {
        "status": "success",
        "dataset": req.dataset,
        "history": history
    }

@app.post("/predict")
def predict(req: PredictRequest):
    if req.dataset not in trained_models:
        return {"error": "Модель для этого датасета ещё не обучена"}

    data = trained_models[req.dataset]
    model = data["model"]
    scaler = data["scaler"]

    X = np.array([req.features])
    if scaler:
        X = scaler.transform(X)

    model.set_training(False)
    out = model.forward(X)
    model.set_training(True)

    predicted_class = int(np.argmax(out, axis=1)[0])
    probabilities = out[0].tolist()

    names = {"iris": ["setosa", "versicolor", "virginica"],
             "mnist": [str(i) for i in range(10)]}
    class_name = names.get(req.dataset, [str(predicted_class)])[predicted_class]

    return {
        "predicted_class": predicted_class,
        "class_name": class_name,
        "probabilities": probabilities
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)