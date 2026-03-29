import numpy as np

class SGD:
    def __init__(self, learning_rate=0.01):
        self.lr = learning_rate

    def step(self, layers):
        for layer in layers:
            if hasattr(layer, 'w'):
                layer.w -= self.lr * layer.grad_w
                layer.b -= self.lr * layer.grad_b

class MomentumSGD:
    def __init__(self, learning_rate=0.01, momentum=0.9):
        self.lr = learning_rate
        self.m = momentum
        self.v_w = []
        self.v_b = []

    def step(self, layers):
        if not self.v_w:
            for layer in layers:
                if hasattr(layer, 'w'):
                    self.v_w.append(np.zeros_like(layer.w))
                    self.v_b.append(np.zeros_like(layer.b))
                else:
                    self.v_w.append(None)
                    self.v_b.append(None)

        for i, layer in enumerate(layers):
            if hasattr(layer, 'w'):
                self.v_w[i] = self.m * self.v_w[i] - self.lr * layer.grad_w
                self.v_b[i] = self.m * self.v_b[i] - self.lr * layer.grad_b
                layer.w += self.v_w[i]
                layer.b += self.v_b[i]

class GradClipper:
    def __init__(self, base_optimizer, clip_value=1.0):
        self.opt = base_optimizer
        self.clip = clip_value

    def step(self, layers):
        for layer in layers:
            if hasattr(layer, 'w'):
                np.clip(layer.grad_w, -self.clip, self.clip, out=layer.grad_w)
                np.clip(layer.grad_b, -self.clip, self.clip, out=layer.grad_b)
        self.opt.step(layers)