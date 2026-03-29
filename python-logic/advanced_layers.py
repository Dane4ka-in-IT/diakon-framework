import numpy as np
from engine import Layer

class Dropout(Layer):
    def __init__(self, rate=0.5):
        self.rate = rate
        self.mask = None
        self.training = True

    def forward(self, x):
        if not self.training:
            return x
        self.mask = np.random.binomial(1, 1 - self.rate, size=x.shape) / (1 - self.rate)
        return x * self.mask

    def backward(self, grad_output):
        if not self.training:
            return grad_output
        return grad_output * self.mask

class BatchNorm1d(Layer):
    def __init__(self, dim, eps=1e-5, momentum=0.9):
        self.eps = eps
        self.momentum = momentum
        self.training = True
        self.gamma = np.ones((1, dim))
        self.beta = np.zeros((1, dim))
        self.running_mean = np.zeros((1, dim))
        self.running_var = np.ones((1, dim))
        self.grad_gamma = None
        self.grad_beta = None

    def forward(self, x):
        if self.training:
            mean = np.mean(x, axis=0, keepdims=True)
            var = np.var(x, axis=0, keepdims=True)
            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * mean
            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * var
            self.x_centered = x - mean
            self.std = np.sqrt(var + self.eps)
            self.x_norm = self.x_centered / self.std
            return self.gamma * self.x_norm + self.beta
        else:
            x_norm = (x - self.running_mean) / np.sqrt(self.running_var + self.eps)
            return self.gamma * x_norm + self.beta

    def backward(self, grad_output):
        if not self.training: 
            return grad_output
        N = grad_output.shape[0]
        self.grad_gamma = np.sum(grad_output * self.x_norm, axis=0, keepdims=True)
        self.grad_beta = np.sum(grad_output, axis=0, keepdims=True)
        dx_norm = grad_output * self.gamma
        dvar = np.sum(dx_norm * self.x_centered, axis=0, keepdims=True) * -0.5 * (self.std ** -3)
        dmean = np.sum(dx_norm * -1.0 / self.std, axis=0, keepdims=True) + dvar * np.mean(-2.0 * self.x_centered, axis=0)
        return (dx_norm / self.std) + (dvar * 2.0 * self.x_centered / N) + (dmean / N)