import os
# Force TensorFlow to bypass the Windows CUDA drivers to prevent silent crashes
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image

class VisualExtractor:
    def __init__(self):
        print("Initializing ResNet50 on CPU (Intel i7)...")
        # Load ResNet50 as a feature extractor (include_top=False)
        self.model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
        print("ResNet50 loaded successfully!")

    def extract_embedding(self, img_path):
        """Processes a single image and returns its feature embedding."""
        try:
            # ResNet50 requires exact 224x224 input
            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            
            # Keras expects batches, so expand dimensions to (1, 224, 224, 3)
            img_array = np.expand_dims(img_array, axis=0)
            
            # Apply ImageNet specific normalization
            img_array = preprocess_input(img_array)
            
            # Extract features and return as a flat Python list for ChromaDB ingestion
            features = self.model.predict(img_array, verbose=0)
            return features[0].tolist()
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            return None