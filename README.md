# ISGFormatHandler
ISGFormatHandler is a Python package that handles _International Service for the Geoid_ models files (.isg format). It has been developed as part of the Computer Engineering project at the _Politecnico di Milano_.

## Specifications
The package supports the reading of ISG files in format 1.00, 1.01 and 2.00. In the case of ISG 2.00, the package only supports grid models. Models represented with sparse data are excluded. For more information, refer to the documentation of the ISG 2.00 format.

The supported actions are the following ones:
1. Read (mandatory);
2. Plot;
4. Convert format;
3. Create and save a sub-model;

The conversion can be performed to theese formats:
- .isg - ISG 1.01 - _International Service for the Geoid format_
- .isg - ISG 2.00 - _International Service for the Geoid format_
- .csv - CSV - _Comma Separated Values_
- .gsf - GSF - _Carlson Geoid Separation File_
- .tif - GeoTIFF - _GeoTIFF Elevation_
- .gri - GEOCOL
- ~.gem - GEM - _Leica GEM_~: the implementation of the Leica GEM conversion algorithm has been suspended due to lack of format documentation. For possible future developments, a draft of the conversion algorithm is present in the code but, at the moment, it is not callable from Python.


## Requirements

- Python 3.9 or greater (operation is not guaranteed for lower versions);
- PIP (recommended);

## Installation
1. Create a new directory:
    ```
    mkdir project
    cd project
    ```
2. Clone the repository and move into the directory:
    ```
    git clone https://github.com/nicolozambon/ISGFormatHandler.git
    cd ISGFormatHandler
    ```
3. Create a virtual environment and install dependencies:
    ```
    python3 -m venv venv 
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4. Run example:
   1. Create a directory called `example`:
      ```
      mkdir example
      ```
   2. Manually move the ISG model of interest into this folder.
   3. Edit `example.py` in order to point to the ISG file.
   4. Run `example.py`:
      ```
      python example.py
      ```
   
## Usage examples

### Plot and convert a model
```python
import ISGFormatHandler as handler

isg_file_path = 'example/EGG97_20170702.isg'
output_path = 'example'

model = handler.Model()
model.retrieveByPath(isg_file_path)

# Plot the model
model.plot()

# The possible formats are 'isg1.01', 'isg2.00', 'csv', 'gsf', 'tif', 'gri'
model.convertTo(output_path, 'isg1.01')
```

### Create a sub-model from bounds
```python
import ISGFormatHandler as handler

isg_file_path = 'example/EGG97_20170702.isg'
output_path = 'example'
bounds = {
    'lat_min': 40,
    'lat_max': 45,
    'lon_min': 10,
    'lon_max': 15
}

model = handler.Model()
model.retrieveByPath(isg_file_path)

model.createSubmodel(
    directory=output_path,
    output_format='isg1.01',
    bounds=bounds
    interpolation=None,
    optimize_dimensions=True
)
```

### Create a sub-model from shapefile
```python
import ISGFormatHandler as handler

isg_file_path = 'example/EGG97_20170702.isg'
shp_file_path = 'example/ITA_adm.zip'
output_path = 'example'

model = handler.Model()
model.retrieveByPath(isg_file_path)

model.createSubmodel(
    directory=output_path,
    output_format='isg1.01',
    shapefile_path=shp_file_path,
    convert_shapefile_to_bounds=False
    interpolation=None,
    optimize_dimensions=True
)
```

### Create and interpolate a sub-model from shapefile
```python
import ISGFormatHandler as handler

isg_file_path = 'example/EGG97_20170702.isg'
shp_file_path = 'example/ITA_adm.zip'
output_path = 'example'

# The possible interpolation methods are 'nn' (2D nearest-neighbor), 'bl' (2D linear) and 'bc' (2D cubic)
interpolation = {
    'lat_deg': 0.1,
    'lon_deg': 0.1,
    'method': 'nn'
}

model = handler.Model()
model.retrieveByPath(isg_file_path)

model.createSubmodel(
    directory=output_path,
    output_format='isg1.01',
    shapefile_path=shp_file_path,
    convert_shapefile_to_bounds=False
    interpolation=interpolation,
    optimize_dimensions=True
)
```
