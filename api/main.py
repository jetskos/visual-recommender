from pathlib import Path
from uuid import uuid4
import shutil

import chromadb
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.feature_extractor import VisualExtractor


PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = PROJECT_ROOT / "dataset" / "images"
UPLOAD_DIR = PROJECT_ROOT / "temp_uploads"
TEMPLATE_DIR = PROJECT_ROOT / "api" / "templates"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"

IMAGE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Visual Similarity Search")
app.mount("/dataset/images", StaticFiles(directory=IMAGE_DIR), name="images")
app.mount("/temp_uploads", StaticFiles(directory=UPLOAD_DIR), name="temp_uploads")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

print("Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
collection = chroma_client.get_collection(name="fashion_products")
extractor = VisualExtractor()


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.post("/search", response_class=HTMLResponse)
async def search_similar(
    request: Request,
    file: UploadFile = File(...),
    gender_filter: str = Form("All"),
):
    suffix = Path(file.filename or "").suffix.lower()
    upload_path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"

    try:
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        embedding = extractor.extract_embedding(str(upload_path))
        if embedding is None:
            return HTMLResponse(
                "<p class='text-red-600'>Error processing image.</p>",
                status_code=422,
            )

        query_args = {
            "query_embeddings": [embedding],
            "n_results": 5,
        }
        if gender_filter != "All":
            query_args["where"] = {"gender": gender_filter}

        results = collection.query(**query_args)
        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        matches = []

        for item_id, metadata, distance in zip(ids, metadatas, distances):
            matches.append(
                {
                    "id": item_id,
                    "path": f"/dataset/images/{item_id}.jpg",
                    "category": metadata.get("masterCategory", "Unknown"),
                    "subcategory": metadata.get("subCategory", "Unknown"),
                    "distance": round(distance, 4),
                }
            )

        return templates.TemplateResponse(
            request=request,
            name="results.html",
            context={
                "matches": matches,
                "uploaded_image": f"/temp_uploads/{upload_path.name}",
            },
        )
    finally:
        await file.close()