import math
import sys
from functools import partial

import click
from .audio import process_stream, audio_callback


@click.group()
def cli():
    pass


def get_terminal_cols():
    import shutil

    try:
        columns, _ = shutil.get_terminal_size()
    except AttributeError:
        columns = 80
    return columns


@cli.command()
@click.option("-l", "--list-devices", is_flag=True)
@click.option("-b", "--block-duration", default=35, help="Speed to draw in ms", show_default=True)
@click.option("-d", "--device", help="input device (numeric ID or substring)")
@click.option("-g", "--gain", default=20, help="Initial gain factor", show_default=True)
@click.option("-r", "--range", help="Frequency range", nargs=2, default=[80, 20000], show_default=True)
@click.option(
    "-c", "--columns", help="width of spectrogram", default=get_terminal_cols()
)
def spectrogram(list_devices, block_duration, device, gain, range, columns):
    import sounddevice as sd
    import numpy as np

    usage_line = " press <enter> to quit, +<enter> or -<enter> to change scaling "

    if list_devices:
        print(sd.query_devices())
        sys.exit()

    colors = 30, 34, 35, 91, 93, 97
    chars = " :%#\t#%:"
    gradient = []
    for bg, fg in zip(colors, colors[1:]):
        for char in chars:
            if char == "\t":
                bg, fg = fg, bg
            else:
                gradient.append(f"\x1b[{fg};{bg + 10}m{char}")

    low, high = range
    try:
        samplerate = sd.query_devices(device, "input")["default_samplerate"]

        delta_f = (high - low) / (columns - 1)
        fftsize = math.ceil(samplerate / delta_f)
        low_bin = math.floor(low / delta_f)

        def callback(indata, frames, time, status):
            if status:
                text = " " + str(status) + " "
                print("\x1b[34;40m", text.center(columns, "#"), "\x1b[0m", sep="")
            if any(indata):
                magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
                magnitude *= gain / fftsize
                line = (
                    gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                    for x in magnitude[low_bin : low_bin + columns]
                )
                print(*line, sep="", end="\x1b[0m\n")
            else:
                print("no input")

        with sd.InputStream(
            device=device,
            channels=1,
            callback=callback,
            blocksize=int(samplerate * block_duration / 1000),
            samplerate=samplerate,
        ):
            while True:
                response = input()
                if response in ("", "q", "Q"):
                    break
                for ch in response:
                    if ch == "+":
                        gain *= 2
                    elif ch == "-":
                        gain /= 2
                    else:
                        print(
                            "\x1b[31;40m",
                            usage_line.center(columns, "#"),
                            "\x1b[0m",
                            sep="",
                        )
                        break
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(type(e).__name__ + ": " + str(e))


@cli.command()
@click.option("--chunk-duration", default=3, type=int, help="In seconds", show_default=True)
@click.option("--sample-rate", default=44100, type=int, help="In Hz", show_default=True)
def audio_frames(chunk_duration, sample_rate):
    process_stream(
        chunk_duration,
        sample_rate,
        callback=partial(audio_callback, sample_rate=sample_rate),
    )
