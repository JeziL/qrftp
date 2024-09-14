import os
import sys
import random
import qrcode
import RSDSampler
from tqdm import tqdm
from MT19937Random import MT19937Random
from tqdm.contrib.concurrent import process_map
from argparse import ArgumentParser, BooleanOptionalAction


def split_binary_data(data, chunk_size):
    return [data[i:i+ chunk_size] for i in range(0, len(data), chunk_size)]

def generate_chunks(data_parts, chunk_size, ext):
    chunks = []
    for i in range(len(data_parts)):
        data = data_parts[i]
        header = f"{ext}|".encode() + len(data).to_bytes(2)
        chunk = header + data
        if len(data) < chunk_size:
            chunk += b'\xFF' * (chunk_size - len(data))
        chunks.append(chunk)
    return chunks

def generate_LT_blocks(chunks, ltencode, redundancy_factor, delta, c):
    blocks = []
    n_chunks = len(chunks)

    if ltencode:
        n_blocks = int(n_chunks * redundancy_factor)
    else:
        n_blocks = n_chunks
    
    prng = RSDSampler.PRNG(params=(n_chunks, delta, c))
    prng.set_seed(random.randint(0, 2 ** 32 - 1))
    for i in tqdm(range(n_blocks), desc=("Encoding LT blocks" if ltencode else "Generating blocks")):
        degree = prng._sample_d() if ltencode else 1
        seed = random.randint(0, 2 ** 32 - 1) if ltencode else i
        r = MT19937Random(c_seed=seed)
        selected_indices = r.sample(n_chunks, degree) if ltencode else [i]
        block = chunks[selected_indices[0]]
        for idx in selected_indices[1:]:
            block = bytes([b1 ^ b2 for b1, b2 in zip(block, chunks[idx])])
        
        block = ltencode.to_bytes(1) + n_chunks.to_bytes(4) + seed.to_bytes(4) + len(selected_indices).to_bytes(4) + block
        blocks.append(block)
    return blocks

def create_qr_code(block):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(block)
    qr.make(fit=True)
    return qr

def create_qr_code_parallel(blocks, num_proc):
    return process_map(create_qr_code, blocks, max_workers=num_proc, chunksize=1, desc="Generating QR codes")

def save_gif(qrs, fps, output_path):
    imgs = [qr.make_image(fill_color='black', back_color='white') for qr in qrs]
    if len(imgs) > 1:
        imgs[0].save(output_path, save_all=True, append_images=imgs[1:], duration=int(1000/float(fps)), loop=0)
    else:
        imgs[0].save(output_path)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="qrftp-encode" if getattr(sys, "frozen", False) else "python qrftp-encode.py",
        description="Read file and encode to animated QR codes.",
    )
    parser.add_argument("input_file", help="The input file")

    parser.add_argument("-s", "--chunk_size", help="The chunk size, default 256", default=256)

    parser.add_argument('--ltencode', action=BooleanOptionalAction, help="Whether to use Luby-Tranform encoding, default True", default=True)
    parser.add_argument("-r", "--redundancy", help="The redundancy factor of Luby-Tranform encoding, default 2", default=2)
    parser.add_argument("-d", "--delta", help="The parameter `delta` of robust soliton distribution used by Luby-Tranform encoding, default 0.5", default=0.5)
    parser.add_argument("-c", "--c", help="The parameter `c` of robust soliton distribution used by Luby-Tranform encoding, default 0.1", default=0.1)

    parser.add_argument("-f", "--fps", help="The FPS of the generated GIF, default 10", default=10)
    parser.add_argument("-o", "--output", help="The output path, default the same as the input file")
    args = parser.parse_args()
    
    # Read in the input file
    basename, old_ext = os.path.splitext(args.input_file)
    if args.output is None:
        args.output = basename + ".gif"
    if len(old_ext) == 0:
        old_ext = ".bin"
    
    with open(args.input_file, 'rb') as file:
        content = file.read()

    # Split file content  
    parts = split_binary_data(content, int(args.chunk_size))

    # Generate data chunks
    print("Generating data chunks...")
    chunks = generate_chunks(parts, int(args.chunk_size), old_ext)

    # LT encode
    blocks = generate_LT_blocks(chunks, args.ltencode, float(args.redundancy), float(args.delta), float(args.c))
    
    # Generate QR codes
    qrs = create_qr_code_parallel(blocks, 12)
    
    print("Combining QR codes to GIF...")
    save_gif(qrs, args.fps, args.output)
    print("Done.")
