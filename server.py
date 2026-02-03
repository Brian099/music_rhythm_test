import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import export_rhythm_data  # Import your existing module

app = FastAPI()

# Configuration
MUSIC_DIR = "music"

class GenerateRequest(BaseModel):
    filename: str
    min_beat_duration: float

@app.post("/api/generate")
async def generate_rhythm(request: GenerateRequest):
    music_path = os.path.join(MUSIC_DIR, request.filename)
    
    # Security check
    if not os.path.abspath(music_path).startswith(os.path.abspath(MUSIC_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(music_path):
        raise HTTPException(status_code=404, detail="File not found")

    print(f"Generating rhythm for {request.filename} with min_beat_duration={request.min_beat_duration}")
    
    # Use the existing analysis logic
    beats, bpm = export_rhythm_data.analyze_song(music_path, request.min_beat_duration)
    
    # Save the JSON file (logic adapted from export_rhythm_data.py main function)
    base_name = os.path.splitext(request.filename)[0]
    json_filename = f"{base_name}.json"
    json_path = os.path.join(MUSIC_DIR, json_filename)
    
    song_data = {
        "audio_src": f"{MUSIC_DIR}/{request.filename}".replace("\\", "/"),
        "beats": beats,
        "bpm": bpm
    }
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(song_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {
        "status": "success",
        "message": f"Generated {len(beats)} beats",
        "data_src": f"{MUSIC_DIR}/{json_filename}".replace("\\", "/")
    }

# Mount music directory to serve audio and json files
app.mount("/music", StaticFiles(directory="music"), name="music")

# Serve index.html at root
@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/playlist.json")
async def get_playlist():
    songs = []
    # Supported audio extensions
    audio_extensions = ('.mp3', '.wav', '.ogg', '.flac')
    
    if os.path.exists(MUSIC_DIR):
        # Sort to ensure consistent order
        for filename in sorted(os.listdir(MUSIC_DIR)):
            if filename.lower().endswith(audio_extensions):
                base_name = os.path.splitext(filename)[0]
                json_filename = f"{base_name}.json"
                
                songs.append({
                    "name": base_name, 
                    "data_src": f"music/{json_filename}",
                    "audio_file": filename
                })
    
    return {"songs": songs}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
