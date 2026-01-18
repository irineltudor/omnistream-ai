# Processor package

# Fix PIL.Image.ANTIALIAS deprecation for moviepy compatibility with Pillow 10+
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
