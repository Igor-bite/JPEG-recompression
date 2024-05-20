from io import BufferedReader
import math
import contextlib
import sys
from pathlib import Path
from compress import compress, print_stats, rle
from arithmeticcoding import BitInputStream, BitOutputStream
from io import BytesIO
import mtf as mtf_coder
from adaptive_arithmetic_compress import compress as aac_compress
from adaptive_arithmetic_decompress import decompress as aac_decompress
import arithmeticcoding
import new_bwt

MODEL_ORDER = 3


def main(args):
    files = sorted(["airplane", "arctichare", "baboon", "cat", "fruits", "frymire", "girl",
                    "monarch", "peppers", "pool", "sails", "serrano", "tulips", "watch"])

    # files = ["serrano", "monarch", "peppers", "pool", "sails", "tulips", "watch"]

    # Chunked BWT - RLE - MTF - AdaptiveAriphmCoding

    q = 30
    before = 0
    after = 0
    for file in files:
        input = f"dataset/jpeg{q}/{file}{q}.jpg"
        output = f"dataset/jpeg{q}/compressed/{file}{q}.jpg.ppm"
        decoded = f"dataset/jpeg{q}/decompressed/{file}{q}.jpg"
        compress(input, output)
        input_size = Path(input).stat().st_size
        output_size = Path(output).stat().st_size
        print(f"After AriphmCoding: {output_size}")
        decompress(output, decoded)
        decoded_size = Path(decoded).stat().st_size
        print(f"input_size = {input_size}")
        print(f"decoded_size = {decoded_size}")
        # assert input_size == decoded_size
        print()

        before += input_size
        after += output_size

    print()
    print(f"Before: {before}")
    print(f"After:  {after}")
    print()
    percent = 100 - (after / before) * 100
    print(f"Percent: {round(percent, 1)}")


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


def decompress(input, output):
    return
    with open(input, "rb") as inp, open(output, "wb") as out:
        bitin = arithmeticcoding.BitInputStream(inp)
        output_data = BytesIO()
        aac_decompress(bitin, output_data)
        output_data = output_data.getvalue()
        print(f"============  {input} -> {output} ============")
        for preprocessor in preprocessors.__reversed__():
            output_data = preprocessor(output_data, False)
        out.write(bytearray(output_data))


def bwt(data: bytes, isEncode: bool) -> bytes:
    chunk_size = 65000
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
        else:
            index = int.from_bytes(chunk[-2:], 'big')
            after_bwt = new_bwt.bw_restore(index, chunk[0:-2])
        result += bytearray(after_bwt)
    print(f"After BWT: {len(result)}")
    return result


def zigzag(data: bytes, isEncode: bool) -> bytes:
    size = int(len(data) / 1000)
    result = []
    for i in range(size):
        start = i * 1000
        end = (i + 1) * 1000
        if len(data) >= end:
            result.append(data[start:end])
        else:
            result.append(data[start:])
    final = []
    for i in range(len(result)):
        final += result[i]
    return final


def rle(data: bytes, isEncode: bool) -> bytes:
    if isEncode:
        result = rle_encode.encode(data)
    else:
        result = data
    print(f"After RLE: {len(result)}")
    return result


def mtf(data: bytes, isEncode: bool) -> bytes:
    all = list(range(257))
    if isEncode:
        result = mtf_coder.encode(data, all)
    else:
        result = mtf_coder.decode(data, all)
    return result


preprocessors = [zigzag, bwt, mtf]
# preprocessors = [bwt, mtf]


if __name__ == "__main__":
    main(sys.argv[1:])
