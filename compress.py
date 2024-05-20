from io import BufferedReader
import math
import contextlib
import sys
from pathlib import Path
from arithmeticcoding import BitOutputStream, BitInputStream
from io import BytesIO
import mtf as mtf_coder
from adaptive_arithmetic_compress import compress as aac_compress
import arithmeticcoding
import new_bwt

MODEL_ORDER = 3


def main(args):
    if len(args) != 2:
        sys.exit("Usage: python adaptive-arithmetic-compress.py InputFile OutputFile")
    input, output = args

    # Chunked ZIGZAG - BWT - MTF - AdaptiveAriphmCoding

    compress(input, output)


def compress(input, output):
    with open(input, "rb") as inp, \
            contextlib.closing(BitOutputStream(open(output, "wb"))) as bitout:
        input_data = inp.read()
        print(f"============  {input} -> {output} ============")
        print(f"Initial:  {len(input_data)}")
        for preprocessor in preprocessors:
            input_data = preprocessor(input_data, True)
        new_input = BytesIO(bytearray(input_data))
        aac_compress(new_input, bitout)


def bwt(data: bytes, isEncode: bool) -> bytes:
    chunk_size = 65000
    if not isEncode:
        chunk_size += 2
    chunks_count = math.ceil(len(data) / chunk_size)
    result = bytes()
    for i in range(chunks_count):
        chunk = bytes()
        if i == chunks_count - 1:
            chunk = data[i * chunk_size:]
        else: 
            chunk = data[i * chunk_size:(i + 1) * chunk_size]
        if isEncode:
            index, after_bwt = new_bwt.bw_transform(chunk)
            after_bwt += index.to_bytes(2, 'big')
            chunk_len = len(after_bwt)
        else:
            chunk_len = len(chunk)
            index_bytes = chunk[chunk_len - 2:]
            index = int.from_bytes(index_bytes, 'big')
            after_bwt = new_bwt.bw_restore(index, chunk[0:-2])
        result += bytearray(after_bwt)
    print(f"After BWT: {len(result)}")
    return result


def zigzag(data: bytes, isEncode: bool) -> bytes:
    repeated_length = 4
    max_number = 255 + repeated_length
    prev = -1
    last_repeated = 0
    result = bytes()
    for b in data:
      if b != prev:
        if last_repeated >= repeated_length:
          result += (last_repeated - repeated_length).to_bytes(1, 'big')
        last_repeated = 0
        prev = b
      
      last_repeated += 1 
      if last_repeated <= repeated_length:
        result += b.to_bytes(1, 'big')
      if last_repeated == max_number:
        result += (max_number - repeated_length).to_bytes(1, 'big')
        last_repeated = 0
    if last_repeated >= repeated_length:
      result += (last_repeated - repeated_length).to_bytes(1, 'big')
    return result


def mtf(data: bytes, isEncode: bool) -> bytes:
    all = list(range(257))
    if isEncode:
        result = mtf_coder.encode(data, all)
    else:
        result = mtf_coder.decode(data, all)
    return result


preprocessors = [zigzag, bwt, mtf]


if __name__ == "__main__":
    main(sys.argv[1:])
