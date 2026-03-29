import numpy as np

class Loss:
    def forward(self, y_pred, y_true):
        pass

    def backward(self, y_pred, y_true):
        pass

class MSE(Loss):
    def forward(self, y_pred, y_true):
        return np.mean(np.power(y_true - y_pred, 2))
    
    def backward(self, y_pred, y_true):
        m = y_true.shape[0]
        return 2 * (y_pred - y_true) / m

class CrossEntropy(Loss):
    def forward(self, y_pred, y_true):
        y_pred = np.clip(y_pred, 1e-7, 1 - 1e-7)
        return -np.sum(y_true * np.log(y_pred)) / y_pred.shape[0]

    def backward(self, y_pred, y_true):
        y_pred = np.clip(y_pred, 1e-7, 1 - 1e-7)
        return -(y_true / y_pred) / y_pred.shape[0]