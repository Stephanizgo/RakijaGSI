"""Find selected newer CPU instructions in AArch64 executable segments.

This is a presence check, not proof that an instruction executes on every
CPU. Missing matches do not establish compatibility with older devices.
"""

import os
import struct


# Masks follow LLVM's AArch64InstrFormats.td. Keep SIMD and scalar forms
# separate: their identical mnemonics can have different CPU requirements.
INSTRUCTION_PATTERNS = {}


def find_cpu_features(path):
    """Return feature names, or None for an unreadable/malformed ARM64 ELF."""
    try:
        with open(path, "rb") as file:
            size = os.fstat(file.fileno()).st_size
            header = file.read(64)
            if (
                header[:6] != b"\x7fELF\x02\x01"
                or len(header) < 20
                or struct.unpack_from("<H", header, 18)[0] != 183
            ):
                return set()
            if len(header) != 64:
                return None

            program_offset = struct.unpack_from("<Q", header, 32)[0]
            program_size = struct.unpack_from("<H", header, 54)[0]
            program_count = struct.unpack_from("<H", header, 56)[0]
            if (
                program_size < 56
                or program_offset > size
                or program_count == 0xFFFF
                or program_count > (size - program_offset) // program_size
            ):
                return None

            segments = []
            for index in range(program_count):
                file.seek(program_offset + index * program_size)
                segment = file.read(56)
                kind, flags = struct.unpack_from("<II", segment)
                if kind != 1 or not flags & 1:
                    continue
                offset = struct.unpack_from("<Q", segment, 8)[0]
                address = struct.unpack_from("<Q", segment, 16)[0]
                length = struct.unpack_from("<Q", segment, 32)[0]
                if offset > size or length > size - offset:
                    return None
                # Instructions are aligned by virtual address, not file offset.
                padding = -address % 4
                if length > padding:
                    segments.append((offset + padding, length - padding))

            features = set()
            for offset, length in segments:
                file.seek(offset)
                remaining = length - length % 4
                while remaining:
                    chunk_size = min(remaining, 1024 * 1024)
                    chunk = file.read(chunk_size)
                    if len(chunk) != chunk_size:
                        return None
                    for (word,) in struct.iter_unpack("<I", chunk):
                        for feature, patterns in INSTRUCTION_PATTERNS.items():
                            if feature not in features and any(
                                word & mask == value for mask, value in patterns
                            ):
                                features.add(feature)
                    remaining -= len(chunk)
            return features
    except (OSError, struct.error):
        return None
