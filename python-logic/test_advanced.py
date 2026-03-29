import numpy as np
from engine import Dense, Relu, Conv2D, Flatten
from advanced_layers import Dropout, BatchNorm1d
from optimizers import SGD
from main import NeuralNetwork
from losses import MSE

nn = NeuralNetwork()


X_img = np.random.randn(2, 1, 5, 5)
nn.add(Conv2D(in_channels=1, out_channels=3, kernel_size=3))
nn.add(Relu())


nn.add(Flatten())

nn.add(BatchNorm1d(dim=27)) 
nn.add(Dropout(rate=0.2))
nn.add(Dense(27, 2))

nn.compile(loss_func=MSE(), optimizer=SGD(0.01))

print("Начинаем обучение...")
history = nn.fit(X_img, np.array([[1, 0], [0, 1]]), epochs=2)
print("Обучение прошло успешно! История:", history)

nn.save_weights("my_model.pkl")
print("Веса сохранены в my_model.pkl!")

nn.set_training(False)
pred = nn.forward(X_img)
print("Предсказание (без дропаута):", pred.shape)