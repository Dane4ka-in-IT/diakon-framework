import json
from main import train_model, predict, TrainRequest, PredictRequest

req = TrainRequest(layers=[10,5], optimizer='SGD', epochs=3, learning_rate=0.01, dataset='iris')
result = train_model(req)
print('TRAIN:', json.dumps(result, indent=2))

preq = PredictRequest(features=[5.1, 3.5, 1.4, 0.2], dataset='iris')
presult = predict(preq)
print('PREDICT:', json.dumps(presult, indent=2))
