# qrftp

A QR code based FounTain encoded File Transfer Protocol.

## Overview

qrftp splits a file to a bunch of chunks, and encodes them to QR code images, then combines the images to an animated GIF. After that, the original file can be decoded by continously scanning the GIF image.

qrftp uses [Fountain code](https://en.wikipedia.org/wiki/Fountain_code) (namely [Luby transform code](https://en.wikipedia.org/wiki/Luby_transform_code)) to increase the efficiency of decoding process.

The concept of qrftp is inspired by [txqr](https://github.com/divan/txqr).

## Encode

An encoder is implemented in Python in `qrftp-encoder`.

**Usage**:

```
python qrftp-encode.py [-h] [-s CHUNK_SIZE] [--ltencode | --no-ltencode] [-r REDUNDANCY] [-d DELTA] [-c C] [-f FPS] [-o OUTPUT] input_file

positional arguments:
  input_file            The input file

options:
  -h, --help            show this help message and exit
  -s CHUNK_SIZE, --chunk_size CHUNK_SIZE
                        The chunk size, default 256
  --ltencode, --no-ltencode
                        Whether to use Luby-Tranform encoding, default True
  -r REDUNDANCY, --redundancy REDUNDANCY
                        The redundancy factor of Luby-Tranform encoding, default 2
  -d DELTA, --delta DELTA
                        The parameter `delta` of robust soliton distribution used by Luby-Tranform encoding, default 0.5
  -c C, --c C           The parameter `c` of robust soliton distribution used by Luby-Tranform encoding, default 0.1
  -p PROCESSES, --processes PROCESSES
                        The number of parallel processes used during QR code generation, default 1
  -f FPS, --fps FPS     The FPS of the generated GIF, default 10
  -o OUTPUT, --output OUTPUT
                        The output path, default the same as the input file
```

## Decode

A decoder is implemented in Javascript in `qrftp-decoder-web`.
