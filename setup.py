from codecs import open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(name='makesurface',
      version='0.2.8',
      description="Create vector datasets from raster surfaces",
      long_description=long_description,
      classifiers=[],
      keywords='',
      author='Damon Burgett',
      author_email='damon@mapbox.com',
      url='https://github.com/mapbox/make-surface',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'click>=3.0', 'fiona', 'numpy', 'rasterio', 'shapely', 'scipy', 'mercantile', 'pyproj'
      ],
      extras_require={
          'test': ['pytest'],
      },
      entry_points="""
      [console_scripts]
      makesurface=makesurface.scripts.cli:cli
      """
      )
