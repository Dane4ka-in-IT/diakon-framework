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
        
class Softmax(Layer):
    def forward(self, x):
        exps = np.exp(x - np.max(x, axis=1, keepdims=True))
        self.out = exps / np.sum(exps, axis=1, keepdims=True)
        return self.out

    def backward(self, grad_output):
        return grad_output * self.out * (1 - self.out)

class Flatten(Layer):
    def forward(self, x):
        self.input_shape = x.shape
        return x.reshape(x.shape[0], -1)

    def backward(self, grad_output):
        return grad_output.reshape(self.input_shape)

class Conv2D(Layer):
    def __init__(self, in_channels, out_channels, kernel_size):
        self.k = kernel_size
        self.in_c = in_channels
        self.out_c = out_channels
        self.w = np.random.randn(out_channels, in_channels, kernel_size, kernel_size) * 0.1
        self.b = np.zeros((out_channels, 1))
        self.grad_w = np.zeros_like(self.w)
        self.grad_b = np.zeros_like(self.b)

    def forward(self, x):
        self.x = x
        batch_size, in_c, h, w = x.shape
        out_h = h - self.k + 1
        out_w = w - self.k + 1
        out = np.zeros((batch_size, self.out_c, out_h, out_w))
        
        for b in range(batch_size):
            for c_out in range(self.out_c):
                for i in range(out_h):
                    for j in range(out_w):
                        x_slice = self.x[b, :, i:i+self.k, j:j+self.k]
                        out[b, c_out, i, j] = np.sum(x_slice * self.w[c_out]) + self.b[c_out, 0]
        return out

    def backward(self, grad_output):
        batch_size, _, out_h, out_w = grad_output.shape
        grad_in = np.zeros_like(self.x)
        self.grad_w.fill(0)
        self.grad_b.fill(0)

        for b in range(batch_size):
            for c_out in range(self.out_c):
                for i in range(out_h):
                    for j in range(out_w):
                        x_slice = self.x[b, :, i:i+self.k, j:j+self.k]
                        g = grad_output[b, c_out, i, j]
                        self.grad_w[c_out] += x_slice * g
                        self.grad_b[c_out, 0] += g
                        grad_in[b, :, i:i+self.k, j:j+self.k] += self.w[c_out] * g
                        
        return grad_in