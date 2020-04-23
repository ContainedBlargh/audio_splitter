# Audio Splitter

A python script that splits a large audio file into individual `.mp3` tracks, using the excellent `pydub` module.
Requires that FFMPEG installed and in your `$PATH` variable.

## Usage:

```
Usage of this program:
python audio_splitter.py <trackinfo csv file> <audio file> <album name>
```

The trackinfo file needs to be a csv-file with the following header:

```
artist, track, start
```

The `start` column should contain the timestamp for when the track start, in the following format:

```
hh:mm:ss
```

For a concrete example, check [the example file](./example_trackinfo.csv).

## Remarks:

I'm starring `pydub` and you should too.
