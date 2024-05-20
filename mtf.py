def encode(s, st):
    return [[st.index(ch), st.insert(0, st.pop(st.index(ch)))][0] for ch in s]


def decode(sq, st):
    return [[st[i], st.insert(0, st.pop(i))][0] for i in sq]


if __name__ == "__main__":
    all = list(range(256))
    for s in ['broood', 'bananaaa', 'hiphophiphop']:
        input = list(s.encode())
        encode = encode(input, all[::])
        print('%14r encodes to %r' % (s, encode), end=', ')
        decode_bytes = decode(encode, all[::])
        decode = bytearray(decode_bytes)
        print('decodes back to %r' % decode)
