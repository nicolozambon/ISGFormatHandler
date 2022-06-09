import csv
import math
import re
import struct
from datetime import date
import rasterio
import numpy as np


def deg_to_dms_dict(dd):
    is_positive = dd >= 0
    dd = abs(dd)
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees if is_positive else -degrees
    return [int(degrees), int(minutes), int(seconds)]


def string_dms_to_dict(string_dms):
    if '°' in string_dms:
        degrees, minutes, seconds = [int(i) for i in re.split('[°\'"]', string_dms[:-1])]
    elif '\'' in string_dms:
        degrees = 0
        minutes, seconds = [int(i) for i in re.split('[\'"]', string_dms[:-1])]
    else:
        degrees = 0
        minutes = 0
        seconds = [int(i) for i in re.split('["]', string_dms[:-1])][0]
    return [int(degrees), int(minutes), int(seconds)]


def fillSpaces(string, length, align='left', right_space=False) -> str:
    while len(string) < length:
        if align == 'left':
            string = string + ' '
        if align == 'right':
            string = ' ' + string
    if right_space:
        string = string + ' '
    return string


def listToString(array, item_format, item_space, right_space=False) -> str:
    string = ''
    for item in array:
        string = string + fillSpaces(('{' + item_format + '}').format(item), item_space, 'right', right_space)
    return string


class FileFormat:

    def __init__(self, model, saved_file):
        self.model = model
        self.saved_file = saved_file

    def convertToISG(self, version='1.01'):
        # Set requested version as model version
        self.model.head['isg_format']['value'] = version

        # Grid shift
        if version == '1.01':
            self.model.head['lat_min']['value'] = float(self.model.dd_bounds['lat_min']) - float(
                self.model.dd_bounds['delta_lat']) / 2
            self.model.head['lat_max']['value'] = float(self.model.dd_bounds['lat_max']) + float(
                self.model.dd_bounds['delta_lat']) / 2
            self.model.head['lon_min']['value'] = float(self.model.dd_bounds['lon_min']) - float(self.model.dd_bounds['delta_lon']) / 2
            self.model.head['lon_max']['value'] = float(self.model.dd_bounds['lon_max']) + float(self.model.dd_bounds['delta_lon']) / 2

        # Find delimiter position
        version_structure = self.model.getStructureByVersion(version)
        delimiter_position = 1
        for key, value in version_structure.items():
            if len(value['keyword']) > delimiter_position:
                delimiter_position = len(value['keyword'])

        with open(self.saved_file, 'w') as file:

            file.writelines(self.model.comment_section)
            file.write('Created by ISGFormatHandler v1.0\n\n')
            file.write('begin_of_head ================================================\n')

            coord_units = None
            for slug, item in self.model.head.items():
                if slug == 'coord_units':
                    coord_units = item['value']
                    break
            if coord_units is None:
                coord_units = 'deg'

            for slug, item in self.model.getStructureByVersion(version).items():

                if slug in self.model.head:

                    if slug == 'model_name' and self.model.is_subset:
                        self.model.head[slug]['value'] += ' subset'

                    if self.model.head[slug]['type'] == 'numeric':
                        delimiter = ' = '
                        destination_format = item['format']

                        if isinstance(destination_format, dict) and coord_units in destination_format:
                            destination_format = destination_format[coord_units]
                            if coord_units == 'dms':

                                string = '{' + destination_format['d'] + '}°{' + destination_format['m'] + '}\'{' + \
                                         destination_format['s'] + '}"'

                                if type(self.model.head[slug]['value']) == str:
                                    dms = string_dms_to_dict(self.model.head[slug]['value'])
                                else:
                                    dms = deg_to_dms_dict(self.model.head[slug]['value'])

                                string = string.format(dms[0], dms[1], dms[2])[1:]

                            else:
                                string = '{' + destination_format + '}'
                                string = string.format(float(self.model.head[slug]['value']))

                        else:
                            if slug == 'creation_date':
                                if self.model.is_subset:
                                    string = ' ' + date.today().strftime('%d/%m/%Y')
                                else:
                                    string = ' ' + self.model.head[slug]['value']
                            else:
                                string = '{' + destination_format + '}'
                                try:
                                    if 'f' in string:
                                        if slug in self.model.dd_bounds:
                                            string = string.format(self.model.dd_bounds[slug])
                                        else:
                                            string = string.format(float(self.model.head[slug]['value']))
                                    else:
                                        string = string.format(int(self.model.head[slug]['value']))
                                except:
                                    string = string.format(self.model.head[slug]['value'])
                    else:
                        delimiter = ' : '
                        string = self.model.head[slug]['value']
                    file.write(
                        fillSpaces(version_structure[slug]['keyword'], delimiter_position) +
                        delimiter +
                        string +
                        '\n'
                    )
                else:
                    if slug == 'creation_date':
                        string = ' ' + date.today().strftime('%d/%m/%Y')
                    elif slug == 'data_format':
                        string = 'grid'
                    elif slug == 'data_ordering':
                        string = 'N-to-S, W-to-E'
                    elif slug == 'coord_type':
                        string = 'geodetic'
                    elif slug == 'coord_units':
                        string = 'deg'
                    else:
                        string = '---'
                    if item['type'] == 'numeric':
                        delimiter = ' = '
                    else:
                        delimiter = ' : '
                    file.write(
                        fillSpaces(item['keyword'], delimiter_position) + delimiter + string + '\n'
                    )
            file.write('end_of_head ==================================================\n')

            for list_row in self.model.data:
                row = listToString(list_row, ':10.4f', 10, True) + '\n'
                file.write(row)

    def convertToCSV(self):
        with open(self.saved_file, 'w', newline='') as file:
            file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['LAT', 'LON', 'N'])
            row = 0
            col = 0
            while row < self.model.getRowsNumber():
                while col < self.model.getColsNumber():
                    value = self.model.getValueAtPoint(row, col)
                    if value > -9000:
                        coord = self.model.getCoordAtPoint(row, col)
                        file_writer.writerow([
                            "{:.8f}".format(coord['lat']),
                            "{:.8f}".format(coord['lon']),
                            "{:.4f}".format(value)
                        ])
                    col += 1
                row += 1
                col = 0

    def convertToGSF(self):
        with open(self.saved_file, 'w') as f:
            f.write(str(self.model.dd_bounds['lat_min']) + '\n')
            lon_min = self.model.dd_bounds['lon_min']
            if lon_min < 0:
                lon_min = 360 + lon_min
            f.write(str(lon_min) + '\n')
            f.write(str(self.model.dd_bounds['lat_max']) + '\n')
            lon_max = self.model.dd_bounds['lon_max']
            if lon_max < 0:
                lon_max = 360 + lon_max
            f.write(str(lon_max) + '\n')
            f.write(str(self.model.head['ncols']['value']) + '\n')
            f.write(str(self.model.head['nrows']['value']) + '\n')
            row = 0
            col = 0
            while row < self.model.getRowsNumber():
                while col < self.model.getColsNumber():
                    f.write(str(self.model.getValueAtPoint(row, col)) + '\n')
                    col += 1
                row += 1
                col = 0

    def convertToTIF(self):
        data = np.matrix(self.model.data)
        delta_lon = (self.model.dd_bounds['lon_max'] - self.model.dd_bounds['lon_min']) / (data.shape[1] - 1)
        delta_lat = (self.model.dd_bounds['lat_max'] - self.model.dd_bounds['lat_min']) / (data.shape[0] - 1)
        Z = np.where(data < -9000, np.nan, data)
        transform = rasterio.transform.Affine.translation(self.model.dd_bounds['lon_min'] - delta_lon / 2, self.model.dd_bounds['lat_max'] + delta_lat / 2) * rasterio.transform.Affine.scale(delta_lon, -delta_lat)
        with rasterio.open(
                self.saved_file,
                'w',
                driver='GTiff',
                height=Z.shape[0],
                width=Z.shape[1],
                count=1,
                dtype=Z.dtype,
                crs='epsg:4326',
                transform=transform
        ) as dst:
            dst.write(Z, 1)

    def convertToGEM(self):
        model_name = self.model.head['model_name']['value']

        lat_min = self.model.dd_bounds['lat_min']
        lat_max = self.model.dd_bounds['lat_max']
        lon_min = self.model.dd_bounds['lon_min']
        lon_max = self.model.dd_bounds['lon_max']
        delta_lat = self.model.dd_bounds['delta_lat']
        delta_lon = self.model.dd_bounds['delta_lon']

        values_number, values_number_for_avg = 0, 0
        values_sum = 0
        for row in self.model.data:
            for value in row:
                values_number += 1
                if value > -9000:
                    values_number_for_avg += 1
                    values_sum += value
        average = values_sum / values_number_for_avg

        ncols = int(self.model.head['ncols']['value'])

        with open(self.saved_file, 'wb') as gem:
            deg_to_radians_coeff = math.pi / 180

            header = str.encode(model_name)
            magic = 0
            fsiz = 0
            unk64 = 0
            unk011 = 0

            a = 0
            f1 = 0
            unk012 = 0

            miny = lat_min * deg_to_radians_coeff
            minx = lon_min * deg_to_radians_coeff
            maxy = lat_max * deg_to_radians_coeff
            maxx = lon_max * deg_to_radians_coeff
            dy = delta_lat * deg_to_radians_coeff
            dx = delta_lon * deg_to_radians_coeff

            ave = average
            ncol = ncols
            nvals = values_number

            gem.write(struct.pack('<9shIbb', header, magic, fsiz, unk64, unk011))

            gem.seek(18 + 53, 1)

            gem.write(struct.pack('<ddddddddbfII', a, f1, miny, minx, maxy, maxx, dx, dy, unk012, ave, ncol, nvals))

            nrow = nvals / ncol

            row, col = 0, 0
            while row < self.model.getRowsNumber():
                while col < self.model.getColsNumber():
                    undulation = self.model.getValueAtPoint(row, col)
                    if undulation > -9000:
                        val = int((undulation - ave) * 1000)

                        gem.write(struct.pack('h', val))
                    col += 1
                row += 1
                col = 0

            '''
            for i in range(0, int(nrow * ncol)):
                undulation = self.model.data[nrow][ncol]
                val = int((undulation - ave) * 1000)
                gem.write(struct.pack('h', val))
            '''

    def convertToGRI(self):
        with open(self.saved_file, 'w') as f:
            number_format = ':10.4f'
            first_row = str(('{' + number_format + '}').format(self.model.dd_bounds['lat_min'])) + "\t\t"
            first_row += str(('{' + number_format + '}').format(self.model.dd_bounds['lat_max'])) + "\t\t"
            first_row += str(('{' + number_format + '}').format(self.model.dd_bounds['lon_min'])) + "\t\t"
            first_row += str(('{' + number_format + '}').format(self.model.dd_bounds['lon_max'])) + "\t\t"
            first_row += str(('{' + number_format + '}').format(self.model.dd_bounds['delta_lat'])) + "\t\t"
            first_row += str(('{' + number_format + '}').format(self.model.dd_bounds['delta_lon']))
            f.write(first_row + '\n')

            for list_row in self.model.data:
                row = listToString(list_row, number_format, 10) + '\n'
                f.write(row)
