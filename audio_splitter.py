from pydub import AudioSegment
import pandas as pd
from dataclasses import dataclass
import sys
from typing import List
import re
import multiprocessing
from threading import Thread
import os

@dataclass
class Track:
    artist: str
    title: str
    start: int
    end: int = None

def sanitize(s: str):
    return re.sub("[^\w ]", "", s.strip())

def parse_tracks(trackinfo_path):
    print("Parsing trackinfo...")
    tracks = []

    trackinfo = pd.read_csv(trackinfo_path, dtype=str)
    for entry in list(trackinfo.iterrows()):
        row = entry[1].tolist()
        artist = sanitize(row[0])
        track = sanitize(row[1])
        start = row[2].strip()
        t = list(map(int, start.split(':')))
        start_in_millis = 0
        for i in range(len(t)):
            start_in_millis += t[-(1 + i)]  * (60**i) * 1000
        tracks.append(Track(artist, track, start_in_millis))

    for i in range(len(tracks) - 1):
        track = tracks[i]
        next_track = tracks[i + 1]
        track.end = next_track.start
    
    print(f"Done, parsed {len(tracks)} tracks!")
    return tracks

def chunk_list(seq: List, num: int):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    
    return out

def track_exporter(tracks: List[Track], path: str, master: AudioSegment, album_name: str):
    def export_tracks():
            for track in tracks:
                segment = None
                if track.end == None:
                    segment = master[track.start:track.start + master.duration_seconds * 1000 - 100].fade_out(1000)
                else:
                    segment = master[track.start:track.end].fade_out(1000)
                tags = {
                    'artist': track.artist,
                    'album': album_name,
                    'title': track.title
                }
                filename = f"{path}/{track.artist} - {track.title}.mp3"
                segment.export(filename, tags=tags)
    return export_tracks

def split_audio(tracks: List[Track], audio_path, album_name):
    path = f"./{album_name}"
    if not os.path.exists(path):
        print(f"Creating album directory at '{path}'")
        os.mkdir(path)
    print("Loading audio...")
    master = AudioSegment.from_file(audio_path)
    print("Done!")
    thread_count = multiprocessing.cpu_count() * 2
    
    if len(tracks) < 3: #For so few tracks, let's not parallelize.
        single_exporter = track_exporter(tracks, path, master, album_name)
        single_exporter()
        return

    chunks = chunk_list(tracks, thread_count)
    threads = []
    print("Exporting tracks, this may take a while...")
    for i in range(thread_count):
        exporter = track_exporter(chunks[i], path, master, album_name)
        t = Thread(target=exporter)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    pass

def main(argv):
    if (len(argv) != 4):
        print("Usage of this program:\npython audio_splitter.py <trackinfo csv file> <audio file> <album name>")
        return
    trackinfo_path = argv[1]
    audio_path = argv[2]
    album_name = argv[3]
    tracks = parse_tracks(trackinfo_path)
    split_audio(tracks, audio_path, album_name)

if __name__ == "__main__":
    main(sys.argv)
    pass