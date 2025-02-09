# pyspectrogram

Play around with audio streams

## Examples

Show colorized output for the music that is currently playing between 80 ad 500HZ with gain 30 drawing a response every 20ms:

    pyspectrogram spectrogram -r 80 500 -g 30 -b 20

Show the audio stream showing the intensity of an FFT between two frequencies (see code):

    pyspectrogram audio-frames
