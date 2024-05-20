from operator import itemgetter
import math


def bw_transform(s):
    n = len(s)
    m = sorted([s[i:n]+s[0:i] for i in range(n)])
    I = m.index(s)
    L = [q[-1] for q in m]
    return (I, L)


def bw_restore(I, L):
    n = len(L)
    X = sorted([(i, x) for i, x in enumerate(L)], key=itemgetter(1))

    T = [None for i in range(n)]
    for i, y in enumerate(X):
        j, _ = y
        T[j] = i

    Tx = [I]
    for i in range(1, n):
        Tx.append(T[Tx[i-1]])

    S = [L[i] for i in Tx]
    S.reverse()
    return S


if __name__ == "__main__":
    data = list("banana".encode())
    print(data)
    index, encoded = bw_transform(data)
    # print(encoded)
    decoded = bw_restore(index, encoded)
    # print(decoded)
    print(data == decoded)
    print()
    print()
    print()

    chunk_size = 50000
    q = 30
    name = "serrano"
    input = f"dataset/jpeg{q}/{name}{q}.jpg"
    decoded = f"dataset/jpeg{q}/decompressed/{name}{q}.jpg"
    file = open(input, mode="rb")
    input_data = file.read()
    file.close()
    print(f"input_data len = {len(input_data)}")
    chunks_count = math.ceil(len(input_data) / chunk_size)
    print(f"chunks = {chunks_count}")
    result_after_bwt = bytes()
    for i in range(chunks_count):
        data = bytes()
        if i == chunks_count - 1:
            data = input_data[i * chunk_size:]
        else:
            data = input_data[i * chunk_size:(i + 1) * chunk_size]
        print(f"Before {len(data)}")
        index, after_bwt = bw_transform(data)
        print(f"After {len(after_bwt)}")
        print(f"index = {index}, {index.to_bytes(2, 'big')} bytes")
        after_bwt += index.to_bytes(2, 'big')
        result_after_bwt += bytearray(after_bwt)
    print(len(result_after_bwt))

    chunk_size += 2
    decoded = bytes()
    for i in range(chunks_count):
        data = bytes()
        if i == chunks_count - 1:
            data = result_after_bwt[i * chunk_size:]
        else:
            data = result_after_bwt[i * chunk_size:(i + 1) * chunk_size]
        index = int.from_bytes(data[-2:], 'big')
        print(f"index = {index}")
        after_bwt = bw_restore(index, data[0:-2])
        decoded += bytearray(after_bwt)
    print(input_data == decoded)
    print(len(decoded))
    with open(decoded, mode="wb") as out:
        out.write(bytearray(decoded))
