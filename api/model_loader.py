# load model from /model directory or other pipeline 
import pathlib, joblib

class ModelLoader():

    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        self.is_loaded = False

    def load(self):
        self.model = joblib.load(self.model_path)
        self.is_loaded = True 
        print("Model Loaded.")

    def predict(self, text):
        label = self.model.predict(text)

        return {
            "label" : label,
        }

    
        