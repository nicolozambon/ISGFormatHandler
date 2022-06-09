import math
import tempfile
import geopandas
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from scipy import interpolate
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, Polygon

from .config import ISG_FORMATS
from .values_conversion import dms_to_deg
from ..converter.file_format import FileFormat
from ..shapefile.shapefile import Shapefile


class Model:
    head_config_fields = ISG_FORMATS['head']

    def __init__(self):
        self.file_path = None
        self.isg_model_format = None
        self.comment_section = []
        self.head = {}
        self.data = []
        self.dd_bounds = {}
        self.is_subset = False
        self.is_dms_format = False

    def retrieveByPath(self, path) -> None:
        self.file_path = path
        with open(self.file_path, encoding='utf8') as f:
            lines = f.readlines()
        self.read(lines)
        self.standardizeModel()

    def getMainHeadValues(self):
        is_dms = self.isg_model_format == '2.0' and self.head['coord_units']['value'] == 'dms'
        array = {
            'model_name': self.head['model_name']['value'],
            'model_type': self.head['model_type']['value'],
            'lat_min': float(self.head['lat_min']['value']) if not is_dms else dms_to_deg(self.head['lat_min']['value']),
            'lat_max': float(self.head['lat_max']['value']) if not is_dms else dms_to_deg(self.head['lat_max']['value']),
            'lon_min': float(self.head['lon_min']['value']) if not is_dms else dms_to_deg(self.head['lon_min']['value']),
            'lon_max': float(self.head['lon_max']['value']) if not is_dms else dms_to_deg(self.head['lon_max']['value']),
            'delta_lat': float(self.head['delta_lat']['value']) if not is_dms else dms_to_deg(self.head['delta_lat']['value']),
            'delta_lon': float(self.head['delta_lon']['value']) if not is_dms else dms_to_deg(self.head['delta_lon']['value'])
        }
        return array

    def setBoundsManually(self, bounds) -> None:
        self.dd_bounds['lat_min'] = bounds['lat_min']
        self.dd_bounds['lat_max'] = bounds['lat_max']
        self.dd_bounds['lon_min'] = bounds['lon_min']
        self.dd_bounds['lon_max'] = bounds['lon_max']

    def standardizeModel(self) -> None:
        bound_slugs = ['lat_min', 'lat_max', 'lon_min', 'lon_max', 'delta_lat', 'delta_lon']
        for slug, item in self.head.items():
            if slug in bound_slugs:
                if self.isg_model_format == '2.0' and self.head['coord_units']['value'] == 'dms':
                    self.is_dms_format = True
                    self.dd_bounds[slug] = dms_to_deg(item['value'])
                else:
                    self.dd_bounds[slug] = float(item['value'])

        # Grid shift
        if self.isg_model_format in ['1.0', '1.01']:
            self.dd_bounds['lat_min'] = self.dd_bounds['lat_min'] + self.dd_bounds['delta_lat'] / 2
            self.dd_bounds['lat_max'] = self.dd_bounds['lat_max'] - self.dd_bounds['delta_lat'] / 2
            self.dd_bounds['lon_min'] = self.dd_bounds['lon_min'] + self.dd_bounds['delta_lon'] / 2
            self.dd_bounds['lon_max'] = self.dd_bounds['lon_max'] - self.dd_bounds['delta_lon'] / 2

        # Set N-to-S convention
        if self.isg_model_format == '2.0':
            if self.head['data_ordering']['value'] == 'S-to-N, W-to-E':
                matrix = []
                for row in self.data:
                    matrix_row = []
                    for col in row:
                        matrix_row.append(col)
                    matrix.insert(0, matrix_row)
                self.data = matrix
            elif self.head['data_ordering']['value'] == 'N-to-S, E-to-W':
                matrix = []
                for row in self.data:
                    matrix_row = []
                    for col in row:
                        matrix_row.insert(0, col)
                    matrix.append(matrix_row)
                self.data = matrix
            elif self.head['data_ordering']['value'] == 'S-to-N, E-to-W':
                matrix = []
                for row in self.data:
                    matrix_row = []
                    for col in row:
                        matrix_row.insert(0, col)
                    matrix.insert(0, matrix_row)
                self.data = matrix
            self.head['data_ordering']['value'] = 'N-to-S, W-to-E'

    def getStructureByVersion(self, version=None) -> dict:
        if not version:
            version = self.isg_model_format
        structure = {}
        for field in self.head_config_fields:
            for value in field['values']:
                if version in value['version']:
                    structure[field['slug']] = {
                        'keyword': value['keyword'],
                        'type': value['type'],
                        'format': value['format'],
                    }
        return structure

    def convertTo(self, path, extension) -> str:
        prefix = datetime.now().strftime("%Y%m%d_%H%M%S_")
        tmp = None
        if extension.lower() == 'csv':
            tmp = tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix='.csv', dir=path)
            converter = FileFormat(self, tmp.name)
            converter.convertToCSV()
        elif extension.lower() == 'isg1.01':
            tmp = tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix='.isg', dir=path)
            converter = FileFormat(self, tmp.name)
            converter.convertToISG(version='1.01')
        elif extension.lower() == 'isg2.00':
            tmp = tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix='.isg', dir=path)
            converter = FileFormat(self, tmp.name)
            converter.convertToISG(version='2.0')
        elif extension.lower() == 'gsf':
            tmp = tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix='.gsf', dir=path)
            converter = FileFormat(self, tmp.name)
            converter.convertToGSF()
        elif extension.lower() == 'tif':
            tmp = tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix='.tif', dir=path)
            converter = FileFormat(self, tmp.name)
            converter.convertToTIF()
        elif extension.lower() == 'gri':
            tmp = tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix='.gri', dir=path)
            converter = FileFormat(self, tmp.name)
            converter.convertToGRI()
        return tmp.name

    def read(self, lines) -> None:
        for line in lines:
            if 'ISG format' in line:
                self.isg_model_format = line[line.find('=') + 1:-1].strip()
                break
        if self.isg_model_format is None:
            print('Error')
            exit(1)
        structure = self.getStructureByVersion()
        in_comment_section = True
        in_header_section = False
        in_data_section = False
        matrix = []

        for line in lines:
            skip_line = False
            if 'begin_of_head' in line:
                in_comment_section = False
                in_header_section = True
                skip_line = True
            if 'end_of_head' in line:
                in_header_section = False
                in_data_section = True
                skip_line = True
            if not skip_line:
                if in_comment_section:
                    self.comment_section.append(line)
                elif in_header_section:
                    numeric = False
                    textual = False

                    separator_pos = line.find(':')
                    if separator_pos > 0:
                        textual = True
                    else:
                        numeric = True
                        separator_pos = line.find('=')

                    for slug, item in structure.items():
                        if isinstance(item['keyword'], list) and line[0:separator_pos].rstrip() in item['keyword']:
                            item['keyword'] = line[0:separator_pos].rstrip()
                        if line[0:separator_pos].rstrip() == item['keyword']:
                            if textual:
                                item['value'] = line[separator_pos + 1:-1].strip()
                            elif numeric:
                                item['value'] = line[separator_pos + 1:-1].strip()
                            break

                elif in_data_section:
                    array = []
                    for item in line.split():
                        try:
                            array.append(float(item))
                        except ValueError:
                            pass
                    matrix.append(array)

        self.head = structure
        self.data = matrix

    def DEBUG_getModelsContent(self):
        for item in self.head:
            print(item)
        for item in self.data:
            print(item)

    def getRowsNumber(self):
        for slug, item in self.head.items():
            if slug == 'nrows':
                return int(item['value'])

    def getColsNumber(self):
        for slug, item in self.head.items():
            if slug == 'ncols':
                return int(item['value'])

    def getCoordAtPoint(self, row, col):
        nrows = int(self.head['nrows']['value'])
        ncols = int(self.head['ncols']['value'])
        calculated_delta_lat = (self.dd_bounds['lat_max'] - self.dd_bounds['lat_min']) / (nrows - 1)
        calculated_delta_lon = (self.dd_bounds['lon_max'] - self.dd_bounds['lon_min']) / (ncols - 1)
        coord = {
            'lat': self.dd_bounds['lat_min'] + calculated_delta_lat * (nrows - 1 - row),
            'lon': self.dd_bounds['lon_max'] - calculated_delta_lon * (ncols - 1 - col),
        }
        return coord

    def getValueAtPoint(self, row, col):
        return self.data[row][col]

    def defineGrid(self):
        undulations = []
        coordinates = []

        calculated_delta_lat = (self.dd_bounds['lat_max'] - self.dd_bounds['lat_min']) / (int(self.head['nrows']['value']) - 1)
        calculated_delta_lon = (self.dd_bounds['lon_max'] - self.dd_bounds['lon_min']) / (int(self.head['ncols']['value']) - 1)

        for row_index, line in enumerate(self.data):
            for col_index, item in enumerate(line):
                lat = self.dd_bounds['lat_max'] - row_index * calculated_delta_lat
                lon = self.dd_bounds['lon_min'] + col_index * calculated_delta_lon
                if undulations != -9999.0000:
                    undulations.append(item)
                    coordinates.append(Point(lon, lat))
        return geopandas.GeoDataFrame(undulations, geometry=coordinates, crs="epsg:4326")

    def getSubset(self, bounds=None, shapefile=None):  # -> ISGGeoidHandler.geoid.model.Model
        if bounds is not None:
            polygon = Polygon([
                (bounds['lon_min'], bounds['lat_min']),
                (bounds['lon_min'], bounds['lat_max']),
                (bounds['lon_max'], bounds['lat_max']),
                (bounds['lon_max'], bounds['lat_min'])
            ])
            gdf_layer = geopandas.GeoDataFrame(index=[0], geometry=[polygon], crs="epsg:4326")
        elif shapefile is not None:
            gdf_layer = shapefile.data
        else:
            print('Error')
            return

        gdf = self.defineGrid()
        gdf_layer.to_crs(gdf.crs)
        subset_geoseries = gdf['geometry'].clip(gdf_layer['geometry'])
        values = []
        coord_list = []

        for index, value in subset_geoseries.items():
            coord_list.append(value)
            values.append(gdf[0][index])

        subset = geopandas.GeoDataFrame(values, geometry=coord_list)

        lon_min = min(subset['geometry'], key=lambda item: item.x).x
        lon_max = max(subset['geometry'], key=lambda item: item.x).x
        lat_min = min(subset['geometry'], key=lambda item: item.y).y
        lat_max = max(subset['geometry'], key=lambda item: item.y).y

        calculated_model_delta_lat = (self.dd_bounds['lat_max'] - self.dd_bounds['lat_min']) / (int(self.head['nrows']['value']) - 1)
        calculated_model_delta_lon = (self.dd_bounds['lon_max'] - self.dd_bounds['lon_min']) / (int(self.head['ncols']['value']) - 1)

        nrows = int((lat_max - lat_min) / calculated_model_delta_lat)
        ncols = int((lon_max - lon_min) / calculated_model_delta_lon)

        calculated_delta_lat = (lat_max - lat_min) / (nrows - 1)
        calculated_delta_lon = (lon_max - lon_min) / (ncols - 1)

        matrix = [[-9999.0000 for x in range(ncols)] for y in range(nrows)]

        model = None
        for index, point in enumerate(subset['geometry']):
            row = int((lat_max - point.y) / calculated_delta_lat)
            col = int((point.x - lon_min) / calculated_delta_lon)
            matrix[row][col] = subset[0][index]

            model = Model()

            model.dd_bounds['delta_lat'] = self.dd_bounds['delta_lat']
            model.dd_bounds['delta_lon'] = self.dd_bounds['delta_lon']
            model.dd_bounds['lat_min'] = lat_min
            model.dd_bounds['lat_max'] = lat_max
            model.dd_bounds['lon_min'] = lon_min
            model.dd_bounds['lon_max'] = lon_max

            model.data = matrix
            model.head = self.head.copy()

            model.head['delta_lat']['value'] = self.dd_bounds['delta_lat']
            model.head['delta_lon']['value'] = self.dd_bounds['delta_lon']
            model.head['lat_min']['value'] = lat_min
            model.head['lat_max']['value'] = lat_max
            model.head['lon_min']['value'] = lon_min
            model.head['lon_max']['value'] = lon_max
            model.head['nrows']['value'] = nrows
            model.head['ncols']['value'] = ncols
            model.is_subset = True

        return model

    def plot(self, path=None) -> None:
        data = np.matrix(self.data)
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot()

        m = Basemap(
            projection='cyl',
            resolution='i',
            ax=ax,
            llcrnrlat=self.dd_bounds['lat_min'],  # llcrnrlat: latitude of lower left hand corner of the desired map domain (degrees).
            urcrnrlat=self.dd_bounds['lat_max'],  # urcrnrlat 	latitude of upper right hand corner of the desired map domain (degrees).
            llcrnrlon=self.dd_bounds['lon_min'],  # llcrnrlon 	longitude of lower left hand corner of the desired map domain (degrees).
            urcrnrlon=self.dd_bounds['lon_max']   # urcrnrlon 	longitude of upper right hand corner of the desired map domain (degrees).
        )

        lat = np.linspace(self.dd_bounds['lat_max'], self.dd_bounds['lat_min'], data.shape[0])
        lon = np.linspace(self.dd_bounds['lon_min'], self.dd_bounds['lon_max'], data.shape[1])
        xs, ys = np.meshgrid(lon, lat)
        x, y = m(xs, ys)

        clevs = np.linspace(np.min(np.where(data < -9000, np.max(data), data)), np.max(data), 100)
        cs = m.contourf(x, y, np.where(data < -9000, np.nan, data), clevs, cmap=plt.cm.turbo)

        try:
            m.drawcoastlines()
        except ValueError:
            pass

        m.drawcountries()
        meridian_step = int((self.dd_bounds['lon_max'] - self.dd_bounds['lon_min']) / 8)
        parallel_step = int((self.dd_bounds['lat_max'] - self.dd_bounds['lat_min']) / 4)
        if meridian_step == 0:
            meridian_step = 1
        if parallel_step == 0:
            parallel_step = 1

        m.drawmeridians(range(-180, 180, meridian_step), labels=[False, False, True, True])
        m.drawparallels(range(-90, 90, parallel_step), labels=[True, False, False, False])

        cbar = m.colorbar(cs, location='right', pad="2%", ticks=np.linspace(np.min(np.where(data < -9000, np.max(data), data)), np.max(data), 5))
        cbar.set_label('Undulation N [m]')
        plt.xlabel('Longitude', labelpad=40)
        plt.ylabel('Latitude', labelpad=40)
        plt.title(self.head['model_name']['value'], pad=30)

        if path:
            if path is not None:
                path = path + '/'
            plt.savefig(path + 'plot.png')
        plt.show()

    def interpolate(self, lon_step, lat_step, method) -> None:
        row, col = 0, 0
        lat_list, lon_list, und_list = [], [], []
        while row < self.getRowsNumber():
            while col < self.getColsNumber():
                coord = self.getCoordAtPoint(row, col)
                undulation = self.getValueAtPoint(row, col)
                if undulation > -9000:
                    und_list.append(undulation)
                    lat_list.append(coord['lat'])
                    lon_list.append(coord['lon'])
                col += 1
            row += 1
            col = 0

        coord_list = list(zip(lon_list, lat_list))

        if method == 'nearest':
            interpolator = interpolate.NearestNDInterpolator(coord_list, und_list)
        elif method == 'linear':
            interpolator = interpolate.LinearNDInterpolator(coord_list, und_list)
        elif method == 'cubic':
            interpolator = interpolate.CloughTocher2DInterpolator(coord_list, und_list)
        else:
            print('Error')
            return

        self.data = []
        self.dd_bounds['delta_lat'] = lat_step
        self.dd_bounds['delta_lon'] = lon_step

        lat = self.dd_bounds['lat_max']
        while lat >= self.dd_bounds['lat_min']:
            lon = self.dd_bounds['lon_max']
            row = []
            while lon >= self.dd_bounds['lon_min']:
                value = interpolator(lon, lat)
                if math.isnan(value):
                    row.append(-9999.00)
                else:
                    row.append(float(value))
                lon -= lon_step
            self.data.append(row)
            lat -= lat_step

        self.head['nrows']['value'] = len(self.data)
        self.head['ncols']['value'] = len(self.data[0])

    def createSubmodel(self, directory, output_format, bounds=None, shapefile_path=None, interpolation=None, convert_shapefile_to_bounds=False, optimize_dimensions=True):
        model = self
        if not optimize_dimensions:
            if shapefile_path is not None or bounds is not None:
                if shapefile_path is not None:
                    shapefile = Shapefile()
                    shapefile.retrieveByPath(shapefile_path)
                    shapefile_bounds = shapefile.getBounds()
                    optimizing_bounds_dict = {
                        'lat_min': float(shapefile_bounds['miny'][0]),
                        'lat_max': float(shapefile_bounds['maxy'][0]),
                        'lon_min': float(shapefile_bounds['minx'][0]),
                        'lon_max': float(shapefile_bounds['maxx'][0])
                    }
                else:
                    optimizing_bounds_dict = bounds

                modified = False
                while model.dd_bounds['lat_min'] > optimizing_bounds_dict['lat_min']:
                    modified = True
                    row = []
                    for i in range(len(model.data[0])):
                        row.append(-9999)
                    model.data.append(row)
                    model.dd_bounds['lat_min'] -= model.dd_bounds['delta_lat']
                while model.dd_bounds['lat_max'] < optimizing_bounds_dict['lat_max']:
                    modified = True
                    row = []
                    for i in range(len(model.data[0])):
                        row.append(-9999)
                    model.data.insert(0, row)
                    model.dd_bounds['lat_max'] += model.dd_bounds['delta_lat']
                while model.dd_bounds['lon_min'] > optimizing_bounds_dict['lon_min']:
                    modified = True
                    for row in model.data:
                        row.insert(0, -9999)
                    model.dd_bounds['lon_min'] -= model.dd_bounds['delta_lon']
                while model.dd_bounds['lon_max'] < optimizing_bounds_dict['lon_max']:
                    modified = True
                    for row in model.data:
                        row.append(-9999)
                    model.dd_bounds['lon_max'] += model.dd_bounds['delta_lon']
                if modified:
                    model.head['lat_min']['value'] = model.dd_bounds['lat_min']
                    model.head['lat_max']['value'] = model.dd_bounds['lat_max']
                    model.head['lon_min']['value'] = model.dd_bounds['lon_min']
                    model.head['lon_max']['value'] = model.dd_bounds['lon_max']
                    model.head['nrows']['value'] = int((model.dd_bounds['lat_max'] - model.dd_bounds['lat_min']) / model.dd_bounds['delta_lat'] + 1)
                    model.head['ncols']['value'] = int((model.dd_bounds['lon_max'] - model.dd_bounds['lon_min']) / model.dd_bounds['delta_lon'] + 1)

        lon_step, lat_step, method = None, None, None
        if interpolation is not None:
            lon_step = interpolation['lat_deg']
            lat_step = interpolation['lon_deg']
            method = None
            if interpolation['method'] == 'nn':
                method = 'nearest'
            elif interpolation['method'] == 'bl':
                method = 'linear'
            elif interpolation['method'] == 'bc':
                method = 'cubic'

        if shapefile_path is not None:

            if convert_shapefile_to_bounds or interpolation is not None:
                shapefile = Shapefile()
                shapefile.retrieveByPath(shapefile_path)
                shapefile_bounds = shapefile.getBounds()
                shapefile_bounds_dict = {
                    'lat_min': float(shapefile_bounds['miny'][0]),
                    'lat_max': float(shapefile_bounds['maxy'][0]),
                    'lon_min': float(shapefile_bounds['minx'][0]),
                    'lon_max': float(shapefile_bounds['maxx'][0])
                }

                if interpolation is not None:
                    pseudo_lat_min = shapefile_bounds_dict['lat_min'] - 2 * model.dd_bounds['delta_lat']
                    pseudo_lat_max = shapefile_bounds_dict['lat_max'] + 2 * model.dd_bounds['delta_lat']
                    pseudo_lon_min = shapefile_bounds_dict['lon_min'] - 2 * model.dd_bounds['delta_lon']
                    pseudo_lon_max = shapefile_bounds_dict['lon_max'] + 2 * model.dd_bounds['delta_lon']
                    interpolation_cropped_area_bounds = {
                        'lat_min': pseudo_lat_min if pseudo_lat_min > model.dd_bounds['lat_min'] else model.dd_bounds['lat_min'],
                        'lat_max': pseudo_lat_max if pseudo_lat_max < model.dd_bounds['lat_max'] else model.dd_bounds['lat_max'],
                        'lon_min': pseudo_lon_min if pseudo_lon_min > model.dd_bounds['lon_min'] else model.dd_bounds['lon_min'],
                        'lon_max': pseudo_lon_max if pseudo_lon_max < model.dd_bounds['lon_max'] else model.dd_bounds['lon_max']
                    }
                    interpolation_cropped_area_model = model.getSubset(bounds=interpolation_cropped_area_bounds)
                    interpolation_cropped_area_model.interpolate(lon_step, lat_step, method)
                    model = interpolation_cropped_area_model

                if convert_shapefile_to_bounds:
                    subset = model.getSubset(bounds=shapefile_bounds_dict)
                else:
                    subset = model.getSubset(shapefile=shapefile)

            else:
                shapefile = Shapefile()
                shapefile.retrieveByPath(shapefile_path)
                subset = model.getSubset(shapefile=shapefile)
            model = subset

        elif bounds is not None:
            if interpolation is not None:
                pseudo_lat_min = bounds['lat_min'] - 2 * model.dd_bounds['delta_lat']
                pseudo_lat_max = bounds['lat_max'] + 2 * model.dd_bounds['delta_lat']
                pseudo_lon_min = bounds['lon_min'] - 2 * model.dd_bounds['delta_lon']
                pseudo_lon_max = bounds['lon_max'] + 2 * model.dd_bounds['delta_lon']
                interpolation_cropped_area_bounds = {
                    'lat_min': pseudo_lat_min if pseudo_lat_min > model.dd_bounds['lat_min'] else model.dd_bounds['lat_min'],
                    'lat_max': pseudo_lat_max if pseudo_lat_max < model.dd_bounds['lat_max'] else model.dd_bounds['lat_max'],
                    'lon_min': pseudo_lon_min if pseudo_lon_min > model.dd_bounds['lon_min'] else model.dd_bounds['lon_min'],
                    'lon_max': pseudo_lon_max if pseudo_lon_max < model.dd_bounds['lon_max'] else model.dd_bounds['lon_max']
                }
                interpolation_cropped_area_model = model.getSubset(bounds=interpolation_cropped_area_bounds)
                interpolation_cropped_area_model.interpolate(lon_step, lat_step, method)
                model = interpolation_cropped_area_model
            subset = model.getSubset(bounds=bounds)
            model = subset

        else:  # entire model
            if interpolation is not None:
                model.interpolate(lon_step, lat_step, method)
            pass

        print("Creating sub-model plot...")
        model.plot(path=directory)

        print("Converting sub-model...")
        if output_format == 'isg1.01':
            model.convertTo(directory, 'isg1.01')
        elif output_format == 'isg2.00':
            model.convertTo(directory, 'isg2.00')
        elif output_format == 'csv':
            model.convertTo(directory, 'csv')
        elif output_format == 'gsf':
            model.convertTo(directory, 'gsf')
        elif output_format == 'tif':
            model.convertTo(directory, 'tif')
        elif output_format == 'gri':
            model.convertTo(directory, 'gri')
        print("Sub-model created!")
