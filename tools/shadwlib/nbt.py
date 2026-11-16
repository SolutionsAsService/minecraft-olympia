"""A small NBT reader and writer (gzip, big-endian), enough for Minecraft structure files. Stdlib only.

Values are (type_id, value) pairs:
  1 byte, 3 int, 6 double, 8 string, 9 list = (element_type_id, [values]), 10 compound = {name: (type_id, value)}, 11 int array.
"""

import gzip
import struct

END, BYTE, INT, DOUBLE, STRING, LIST, COMPOUND, INT_ARRAY = 0, 1, 3, 6, 8, 9, 10, 11


def _str(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def _payload(t, v):
    if t == BYTE:
        return struct.pack(">b", v)
    if t == INT:
        return struct.pack(">i", v)
    if t == DOUBLE:
        return struct.pack(">d", v)
    if t == STRING:
        return _str(v)
    if t == LIST:
        et, items = v
        return struct.pack(">bi", et, len(items)) + b"".join(_payload(et, x) for x in items)
    if t == COMPOUND:
        out = b""
        for name, (tt, vv) in v.items():
            out += struct.pack(">b", tt) + _str(name) + _payload(tt, vv)
        return out + b"\x00"
    if t == INT_ARRAY:
        return struct.pack(">i", len(v)) + b"".join(struct.pack(">i", x) for x in v)
    raise ValueError(f"unsupported NBT type {t}")


def dumps(root, name=""):
    """Gzip-compressed bytes of a root compound (a dict of name -> (type, value))."""
    return gzip.compress(struct.pack(">b", COMPOUND) + _str(name) + _payload(COMPOUND, root), 9)


class _Reader:
    def __init__(self, data):
        self.d, self.i = data, 0

    def take(self, n):
        b = self.d[self.i:self.i + n]
        self.i += n
        return b

    def string(self):
        (n,) = struct.unpack(">H", self.take(2))
        return self.take(n).decode("utf-8")

    def payload(self, t):
        if t == BYTE:
            return struct.unpack(">b", self.take(1))[0]
        if t == 2:
            return struct.unpack(">h", self.take(2))[0]
        if t == INT:
            return struct.unpack(">i", self.take(4))[0]
        if t == 4:
            return struct.unpack(">q", self.take(8))[0]
        if t == 5:
            return struct.unpack(">f", self.take(4))[0]
        if t == 6:
            return struct.unpack(">d", self.take(8))[0]
        if t == STRING:
            return self.string()
        if t == LIST:
            et = struct.unpack(">b", self.take(1))[0]
            (n,) = struct.unpack(">i", self.take(4))
            return (et, [self.payload(et) for _ in range(n)])
        if t == COMPOUND:
            out = {}
            while True:
                tt = struct.unpack(">b", self.take(1))[0]
                if tt == END:
                    return out
                name = self.string()
                out[name] = (tt, self.payload(tt))
        if t == INT_ARRAY:
            (n,) = struct.unpack(">i", self.take(4))
            return [struct.unpack(">i", self.take(4))[0] for _ in range(n)]
        raise ValueError(f"unsupported NBT type {t}")


def loads(blob):
    """Read gzip NBT bytes; returns the root compound as {name: (type, value)}."""
    r = _Reader(gzip.decompress(blob))
    t = struct.unpack(">b", r.take(1))[0]
    assert t == COMPOUND, "root must be a compound"
    r.string()
    return r.payload(COMPOUND)
