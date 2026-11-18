import os
import pandas as pd
import chromadb
from core.feature_extractor import VisualExtractor

class VectorManager:
    def __init__(self):
        # Initialize ChromaDB to store data locally in a 'vector_db' directory
        self.client = chromadb.PersistentClient(path="./vector_db")
        
        # Create a collection using cosine similarity for the image matching
        self.collection = self.client.get_or_create_collection(
            name="fashion_products",
            metadata={"hnsw:space": "cosine"} 
        )
        self.extractor = VisualExtractor()

    def populate_db(self, csv_path="dataset/styles.csv", img_dir="dataset/images/"):
        print("\nLoading dataset metadata...")
        # Load CSV and skip any malformed rows inherent to the Kaggle dataset
        try:
            df = pd.read_csv(csv_path, on_bad_lines='skip') 
        except FileNotFoundError:
            print(f"ERROR: Could not find {csv_path}. Make sure it is extracted.")
            return

        # Limit to the first 2000 images for rapid prototyping
        df = df.head(2000) 
        
        embeddings = []
        metadatas = []
        ids = []
        
        print(f"Extracting features for {len(df)} images on CPU...")
        
        for index, row in df.iterrows():
            img_id = str(row['id'])
            img_path = os.path.join(img_dir, f"{img_id}.jpg")
            
            if not os.path.exists(img_path):
                continue
                
            # Extract the 2048-dimensional vector
            embedding = self.extractor.extract_embedding(img_path)
            
            if embedding is not None:
                embeddings.append(embedding)
                # Store categories so we can filter recommendations later
                metadatas.append({
                    "gender": str(row.get('gender', '')),
                    "masterCategory": str(row.get('masterCategory', '')),
                    "subCategory": str(row.get('subCategory', '')),
                    "articleType": str(row.get('articleType', ''))
                })
                ids.append(img_id)
                
            # Batch insert every 100 items for optimal memory management
            if len(embeddings) >= 100:
                self.collection.add(
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"Inserted batch up to index {index} into ChromaDB...")
                embeddings, metadatas, ids = [], [], []

        # Insert any remaining vectors
        if embeddings:
            self.collection.add(
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
        print("\nVector database population complete! You can now query similar items.")

if __name__ == "__main__":
    manager = VectorManager()
    manager.populate_db()