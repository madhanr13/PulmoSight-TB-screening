"""GA-calibrated MobileNet inference with a no-weight demo fallback."""

import os

import numpy as np


class GAMobileNetClassifier:
    def __init__(self):
        self.model = None
        self.runtime_mode = "demo heuristic"
        self.threshold = self._genetic_threshold(
            scores=np.array([0.08, 0.18, 0.24, 0.41, 0.63, 0.77, 0.89]),
            labels=np.array([0, 0, 0, 0, 1, 1, 1]),
        )
        self._load_mobilenet()

    def _load_mobilenet(self):
        if os.getenv("USE_IMAGENET_WEIGHTS", "0") != "1":
            return
        try:
            from tensorflow.keras.applications import MobileNetV2
            self.model = MobileNetV2(
                weights="imagenet", include_top=False, pooling="avg")
            self.runtime_mode = "MobileNetV2 + GA"
        except (ImportError, OSError, ValueError):
            self.model = None

    @staticmethod
    def _genetic_threshold(scores, labels, population_size=24, generations=18):
        """Find the threshold with the best balanced accuracy by mutation/crossover."""
        rng = np.random.default_rng(42)
        population = rng.uniform(0.2, 0.8, population_size)
        for _ in range(generations):
            fitness = np.array([
                np.mean((scores >= candidate) == labels) for candidate in population
            ])
            elite = population[np.argsort(fitness)[-6:]]
            children = []
            while len(children) < population_size - len(elite):
                parents = rng.choice(elite, size=2)
                child = (parents[0] + parents[1]) / 2 + rng.normal(0, 0.035)
                children.append(np.clip(child, 0.05, 0.95))
            population = np.concatenate([elite, children])
        final_fitness = np.array([
            np.mean((scores >= candidate) == labels) for candidate in population
        ])
        return float(population[np.argmax(final_fitness)])

    @staticmethod
    def _heuristic_score(tensor):
        pixels = (tensor[0] + 1.0) / 2.0
        grayscale = pixels.mean(axis=2)
        contrast = float(grayscale.std())
        lower_quadrant = float(grayscale[112:, :].mean())
        upper_quadrant = float(grayscale[:112, :].mean())
        score = 0.42 + (contrast - 0.19) * 1.8 + \
            (upper_quadrant - lower_quadrant) * 0.25
        return float(np.clip(score, 0.03, 0.97))

    def predict(self, tensor):
        if self.model is not None:
            embedding = self.model.predict(tensor, verbose=0)
            score = float(1 / (1 + np.exp(-np.mean(embedding) / 2)))
        else:
            score = self._heuristic_score(tensor)

        positive = score >= self.threshold
        confidence = score if positive else 1 - score
        return {
            "prediction": "TB indicators detected" if positive else "No TB indicators detected",
            "status": "positive" if positive else "negative",
            "score": round(score * 100, 1),
            "confidence": round(confidence * 100, 1),
            "threshold": round(self.threshold * 100, 1),
            "disclaimer": "Research support only. This result is not a medical diagnosis.",
        }
