"""T17: MLP pequeña en CPU; transformaciones aprendidas solo con train."""

import numpy as np
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.preprocessing import StandardScaler
import torch
from torch import nn

from delivery_ml.baseline import validated_xy
from delivery_ml.model_data import FEATURE_COLUMNS


MAX_EPOCHS = 30
BATCH_SIZE = 2048
LEARNING_RATE = 0.001
SEED = 42


class SmallMLPRegressor:
    """4 → 16 ReLU → 8 ReLU → 1 lineal: 225 parámetros, regresión sin recorte."""

    def fit(self, train, epochs: int = MAX_EPOCHS, validation=None):
        if not isinstance(epochs, int) or epochs < 1:
            raise ValueError("epochs debe ser un entero positivo")
        x, y = validated_xy(train)
        if validation is not None:
            _, validation_y = validated_xy(validation)
        self.feature_scaler = StandardScaler().fit(x)
        self.target_scaler = StandardScaler().fit(y.to_numpy().reshape(-1, 1))
        features = torch.tensor(self.feature_scaler.transform(x), dtype=torch.float32)
        target = torch.tensor(self.target_scaler.transform(y.to_numpy().reshape(-1, 1)), dtype=torch.float32)
        torch.set_num_threads(2)
        torch.use_deterministic_algorithms(True)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(SEED)
            self.network = nn.Sequential(nn.Linear(4, 16), nn.ReLU(), nn.Linear(16, 8),
                                         nn.ReLU(), nn.Linear(8, 1))
        optimizer = torch.optim.Adam(self.network.parameters(), lr=LEARNING_RATE)
        loss_fn = nn.MSELoss()
        generator = torch.Generator().manual_seed(SEED)
        self.history = []
        for epoch in range(1, epochs + 1):
            self.network.train()
            permutation = torch.randperm(len(x), generator=generator)
            total_loss = 0.0
            for start in range(0, len(x), BATCH_SIZE):
                indices = permutation[start:start + BATCH_SIZE]
                optimizer.zero_grad()
                loss = loss_fn(self.network(features[indices]), target[indices])
                if not torch.isfinite(loss):
                    raise ValueError("Pérdida MLP no finita")
                loss.backward()
                optimizer.step()
                total_loss += float(loss.detach()) * len(indices)
            item = {"epoch": epoch, "training_mse_scaled": total_loss / len(x)}
            if validation is not None:
                prediction = self.predict(validation)
                item.update({"validation_mae_minutes": float(mean_absolute_error(validation_y, prediction)),
                             "validation_rmse_minutes": float(root_mean_squared_error(validation_y, prediction))})
            self.history.append(item)
        return self

    def predict(self, features):
        """Solo necesita predictores, sin IDs, eventos ni target."""
        values = self.feature_scaler.transform(features[FEATURE_COLUMNS])
        if not np.isfinite(values).all():
            raise ValueError("Predictores no finitos")
        self.network.eval()
        with torch.no_grad():
            scaled = self.network(torch.tensor(values, dtype=torch.float32)).numpy()
        return self.target_scaler.inverse_transform(scaled).ravel()
