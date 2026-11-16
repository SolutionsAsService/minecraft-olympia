"""shadwlib: the shared generators behind SHADW's Minecraft mods (Asgard, Khemet and whatever comes next).

Stdlib only. `shadw-mod lib-sync <mod>` copies this package into <mod>/tools/shadwlib so every mod repository stays
self-contained. In a mod's tool scripts:

    from shadwlib import nbt, png, pix, structure, skin

nbt        read and write gzip NBT (structure files)
png        write a PNG from RGBA tuples (no Pillow)
pix        16x16 sprite and block-texture helpers: Pix, tex, shade, h (deterministic noise)
structure  build a structure template block by block: state, Structure, chest, hole
skin       paint a humanoid (zombie-model) skin face by face on the standard 64x64 layout
"""
