from setuptools import setup

setup(
    name='RasterSurfaceVectorize',
    version='1.0',
    py_modules=['surfacevectorize, runner'],
    install_requires=[
        'Click',
        'numpy',
        'fiona',
        'rasterio',
        'shapely',
        'skimage',
        'json'
    ],
    entry_points='''
        [console_scripts]
        surfacevectorize=surfacevectorize:cli
    ''',    
)