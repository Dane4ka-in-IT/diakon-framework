import numpy as np
from engine import Dense, Relu
from optimizers import SGD
from main import NeuralNetwork, MSE

nn = NeuralNetwork()
nn.add(Dense(10, 5))
nn.add(Relu())
nn.add(Dense(5, 2))

opt = SGD(learning_rate=0.01)

nn.compile(MSE(), opt)

X = np.random.randn(1, 10)
y = np.random.randn(1, 2)
pred = nn.forward(X)
print("Forward pass complete, shape:", pred.shape)

history = nn.fit(X, y, epochs=2)
print("Training complete, loss history:", history)