import os
import json
import librosa
import numpy as np

def get_files(directory, extensions):
    return [f for f in os.listdir(directory) if f.lower().endswith(extensions)]

def analyze_song(music_path, min_beat_duration=0.1):
    print(f"Processing music: {music_path}")
    
    # Analyze Audio
    try:
        y, sr = librosa.load(music_path)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        # Handle tempo type compatibility
        if isinstance(tempo, np.ndarray):
            tempo = tempo.item()
            
        # Filter beats (Anti-flashing)
        filtered_beat_times = [0.0]
        for t in beat_times:
            if t - filtered_beat_times[-1] >= min_beat_duration:
                filtered_beat_times.append(float(t))
                
        print(f"  -> Extracted {len(filtered_beat_times)} beat points. BPM: {tempo:.2f}")
        return filtered_beat_times, tempo
    except Exception as e:
        print(f"  -> Error processing {music_path}: {e}")
        return [], 0

def main():
    # Configuration
    MUSIC_DIR = "music"
    PLAYLIST_FILE = "playlist.json"
    MIN_BEAT_DURATION = 0.1  # Set to 0.1 as requested for higher sensitivity
    
    # 1. Find Music
    music_files = get_files(MUSIC_DIR, ('.mp3', '.wav', '.flac'))
    if not music_files:
        print("Error: No music files found.")
        return

    playlist = {
        "songs": []
    }

    # 3. Process Each Song
    for music_filename in music_files:
        music_path = os.path.join(MUSIC_DIR, music_filename)
        # Generate JSON filename: music/song.mp3 -> music/song.json
        base_name = os.path.splitext(music_filename)[0]
        json_filename = f"{base_name}.json"
        json_path = os.path.join(MUSIC_DIR, json_filename)
        
        # Analyze
        beats, bpm = analyze_song(music_path, MIN_BEAT_DURATION)
        
        if beats:
            # Save individual song data
            song_data = {
                "audio_src": f"{MUSIC_DIR}/{music_filename}".replace("\\", "/"),
                "beats": beats,
                "bpm": bpm
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(song_data, f, ensure_ascii=False, indent=2)
            
            # Add to playlist
            playlist["songs"].append({
                "name": base_name,
                "data_src": f"{MUSIC_DIR}/{json_filename}".replace("\\", "/")
            })
            
            print(f"  -> Saved rhythm data to {json_path}")

    # 4. Export Playlist
    with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(playlist, f, ensure_ascii=False, indent=2)
        
    print(f"\nAll done! Playlist saved to {PLAYLIST_FILE}")

if __name__ == "__main__":
    main()
