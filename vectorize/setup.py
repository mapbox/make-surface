from codecs import open  # To use a consistent encoding
from setuptools import setup

# Get the long description from the relevant file
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='rastersurface',
    version='0.1',
    description='Vectorization of raster surfaces',
    long_description=long_description,
    packages=[''],
    install_requires=[
        'click', 'fiona', 'numpy', 'rasterio', 'shapely', 'scikit-image'],
    extras_require = {
        'test': ['pytest'],
    },
    entry_points='''
        [console_scripts]
        surfacevectorize=scripts.surfacevectorize:cli
    ''',
)
