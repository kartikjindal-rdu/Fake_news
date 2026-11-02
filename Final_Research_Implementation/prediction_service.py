
import joblib

class VeriNewsPredictor:

    def __init__(self, model_path):
        self.package = joblib.load(model_path)
        self.vectorizer = self.package["vectorizer"]
        self.models = self.package["models"]

    def predict(self, text):

        if not isinstance(text, str) or not text.strip():
            raise ValueError("News text cannot be empty")

        features = self.vectorizer.transform([text])

        output = {}

        for name, model in self.models.items():
            prediction = int(model.predict(features)[0])
            output[name] = (
                "REAL" if prediction == 1 else "FAKE"
            )

        return output
