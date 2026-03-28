import numpy as np

class Callback:
    def on_epoch_end(self, epoch, logs):
        pass

class EarlyStopping(Callback):
    def __init__(self, patience=5, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = np.inf
        self.wait = 0
        self.stop_training = False

    def on_epoch_end(self, epoch, logs):
        current_loss = logs.get('loss')
        if current_loss is None:
            return

        if current_loss < self.best_loss - self.min_delta:
            self.best_loss = current_loss
            self.wait = 0
        else:
            self.wait += 1
            if self.wait >= self.patience:
                print(f"Early stopping at epoch {epoch}")
                self.stop_training = True

class LRScheduler(Callback):
    def __init__(self, optimizer, factor=0.5, patience=3):
        self.opt = optimizer
        self.factor = factor
        self.patience = patience
        self.best_loss = np.inf
        self.wait = 0

    def on_epoch_end(self, epoch, logs):
        current_loss = logs.get('loss')
        if current_loss < self.best_loss:
            self.best_loss = current_loss
            self.wait = 0
        else:
            self.wait += 1
            if self.wait >= self.patience:
                self.opt.lr *= self.factor
                print(f"Reducing learning rate to {self.opt.lr}")
                self.wait = 0