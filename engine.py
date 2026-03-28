import numpy as np

class Layer:
    def forward(self, x):
        pass
    
    def backward(self, grad_output):
        pass

class Dense(Layer):
    def __init__(self, in_features, out_features):
        self.w = np.random.randn(in_features, out_features) * 0.01
        self.b = np.zeros((1, out_features))
        self.grad_w = None
        self.grad_b = None
        self.x = None

    def forward(self, x):
        self.x = x
        return np.dot(x, self.w) + self.b

    def backward(self, grad_output):
        self.grad_w = np.dot(self.x.T, grad_output)
        self.grad_b = np.sum(grad_output, axis=0, keepdims=True)
        return np.dot(grad_output, self.w.T)

class Relu(Layer):
    def forward(self, x):
        self.x = x
        return np.maximum(0, x)

    def backward(self, grad_output):
        res = grad_output.copy()
        res[self.x <= 0] = 0
        return res

class Sigmoid(Layer):
    def forward(self, x):
        self.out = 1 / (1 + np.exp(-x))
        return self.out

    def backward(self, grad_output):
        return grad_output * self.out * (1 - self.out)