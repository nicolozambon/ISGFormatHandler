import geopandas as gpd
import matplotlib.pyplot as plt


class Shapefile:

    def __init__(self):
        self.data = None

    def retrieveByPath(self, path):
        data = gpd.GeoDataFrame.from_file(path)
        data.crs = "EPSG:4326"
        self.data = data

    def plot(self):
        if self.data is not None:
            self.data.plot()
            plt.show()

    def convertToBounds(self):
        bounds = {}
        if self.data is not None:
            bounds['lat_min'] = float(self.data.bounds['miny'])
            bounds['lat_max'] = float(self.data.bounds['maxy'])
            bounds['lon_min'] = float(self.data.bounds['minx'])
            bounds['lon_max'] = float(self.data.bounds['maxx'])
            return bounds

    def getBounds(self):
        # 'IT': ('Italy', (6.7499552751, 36.619987291, 18.4802470232, 47.1153931748))
        if self.data is not None:
            return self.data.bounds

    def getBoundary(self):
        if self.data is not None:
            return self.data.boundary
