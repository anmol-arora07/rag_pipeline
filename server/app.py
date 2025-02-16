from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
from uuid import uuid4
from rag.server.kafka_producer import send_to_kafka

app = FastAPI()

# Add CORSMiddleware to allow cross-origin requests
origins = [
    "http://localhost:3002",  # Allow your frontend origin (React app)
    # You can also allow other origins by adding them to this list
    # "http://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins in the list
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)



@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    allowed_types = ["application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    file_id = str(uuid4())
    file_path = f"/Users/anmolarora/Desktop/Galaxy/projects/qna-app/backend/uploads/{file_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
     # Create a message to send to Kafka (file ID, file path, and file details)
    message = {
        "documentId": file_id,
        "filePath": file_path,
        "filename": file.filename,
        "fileType": file.content_type
    }


    send_to_kafka(topic='file-upload-topic', file_id=file_id, message=message)

    return {"documentId": file_id, "filePath": file_path}