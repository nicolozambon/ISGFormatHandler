ISG_FORMATS = {
    'head': [
        {
            'slug': 'model_name',
            'values': [
                {
                    'keyword': 'model name',
                    'type': 'textual',
                    'format': '',
                    'version': ['1.0', '1.01', '2.0']
                }
            ]
        },
        {
            'slug': 'model_year',
            'values': [
                {
                    'keyword': 'model year',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'model_type',
            'values': [
                {
                    'keyword': 'model type',
                    'type': 'textual',
                    'format': '',
                    'version': ['1.0', '1.01', '2.0']
                }
            ]
        },
        {
            'slug': 'data_type',
            'values': [
                {
                    'keyword': 'data type',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'data_units',
            'values': [
                {
                    'keyword': 'units',
                    'type': 'textual',
                    'format': '',
                    'version': ['1.0', '1.01']
                },
                {
                    'keyword': 'data units',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'data_format',
            'values': [
                {
                    'keyword': 'data format',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'data_ordering',
            'values': [
                {
                    'keyword': 'data ordering',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'ref_ellipsoid',
            'values': [
                {
                    'keyword': 'reference',
                    'type': 'textual',
                    'format': '',
                    'version': ['1.0', '1.01']
                },
                {
                    'keyword': 'ref ellipsoid',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'ref_frame',
            'values': [
                {
                    'keyword': 'ref frame',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'height_datum',
            'values': [
                {
                    'keyword': 'height datum',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'tide_system',
            'values': [
                {
                    'keyword': 'tide system',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'coord_type',
            'values': [
                {
                    'keyword': 'coord type',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'coord_units',
            'values': [
                {
                    'keyword': 'coord units',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'map_projection',
            'values': [
                {
                    'keyword': 'map projection',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'epsg_code',
            'values': [
                {
                    'keyword': 'EPSG code',
                    'type': 'textual',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'lat_min',
            'values': [
                {
                    'keyword': 'lat min',
                    'type': 'numeric',
                    'format': ':10.4f',
                    'version': ['1.0']
                },
                {
                    'keyword': 'lat min',
                    'type': 'numeric',
                    'format': ':18.12f',
                    'version': ['1.01']
                },
                {
                    'keyword': ['lat min', 'north min'],
                    'type': 'numeric',
                    'format': {
                        'dms': {'d': ':4', 'm': ':02', 's': ':02'},
                        'deg': ':11.6f',
                        'meters': ':11.3f',
                        'feet': ':11.3f'
                    },
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'lat_max',
            'values': [
                {
                    'keyword': 'lat max',
                    'type': 'numeric',
                    'format': ':10.4f',
                    'version': ['1.0']
                },
                {
                    'keyword': 'lat max',
                    'type': 'numeric',
                    'format': ':18.12f',
                    'version': ['1.01']
                },
                {
                    'keyword': ['lat max', 'north max'],
                    'type': 'numeric',
                    'format': {
                        'dms': {'d': ':4', 'm': ':02', 's': ':02'},
                        'deg': ':11.6f',
                        'meters': ':11.3f',
                        'feet': ':11.3f'
                    },
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'lon_min',
            'values': [
                {
                    'keyword': 'lon min',
                    'type': 'numeric',
                    'format': ':10.4f',
                    'version': ['1.0']
                },
                {
                    'keyword': 'lon min',
                    'type': 'numeric',
                    'format': ':18.12f',
                    'version': ['1.01']
                },
                {
                    'keyword': ['lon min', 'east min'],
                    'type': 'numeric',
                    'format': {
                        'dms': {'d': ':4', 'm': ':02', 's': ':02'},
                        'deg': ':11.6f',
                        'meters': ':11.3f',
                        'feet': ':11.3f'
                    },
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'lon_max',
            'values': [
                {
                    'keyword': 'lon max',
                    'type': 'numeric',
                    'format': ':10.4f',
                    'version': ['1.0']
                },
                {
                    'keyword': 'lon max',
                    'type': 'numeric',
                    'format': ':18.12f',
                    'version': ['1.01']
                },
                {
                    'keyword': ['lon max', 'east max'],
                    'type': 'numeric',
                    'format': {
                        'dms': {'d': ':4', 'm': ':02', 's': ':02'},
                        'deg': ':11.6f',
                        'meters': ':11.3f',
                        'feet': ':11.3f'
                    },
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'delta_lat',
            'values': [
                {
                    'keyword': 'delta lat',
                    'type': 'numeric',
                    'format': ':10.4f',
                    'version': ['1.0']
                },
                {
                    'keyword': 'delta lat',
                    'type': 'numeric',
                    'format': ':18.12f',
                    'version': ['1.01']
                },
                {
                    'keyword': ['delta lat', 'delta north'],
                    'type': 'numeric',
                    'format': {
                        'dms': {'d': ':4', 'm': ':02', 's': ':02'},
                        'deg': ':11.6f',
                        'meters': ':11.3f',
                        'feet': ':11.3f'
                    },
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'delta_lon',
            'values': [
                {
                    'keyword': 'delta lon',
                    'type': 'numeric',
                    'format': ':10.4f',
                    'version': ['1.0']
                },
                {
                    'keyword': 'delta lon',
                    'type': 'numeric',
                    'format': ':18.12f',
                    'version': ['1.01']
                },
                {
                    'keyword': ['delta lon', 'delta east'],
                    'type': 'numeric',
                    'format': {
                        'dms': {'d': ':4', 'm': ':02', 's': ':02'},
                        'deg': ':11.6f',
                        'meters': ':11.3f',
                        'feet': ':11.3f'
                    },
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'nrows',
            'values': [
                {
                    'keyword': 'nrows',
                    'type': 'numeric',
                    'format': ':10',
                    'version': ['1.0', '2.0']
                },
                {
                    'keyword': 'nrows',
                    'type': 'numeric',
                    'format': ':18',
                    'version': ['1.01']
                }
            ]
        },
        {
            'slug': 'ncols',
            'values': [
                {
                    'keyword': 'ncols',
                    'type': 'numeric',
                    'format': ':10',
                    'version': ['1.0', '2.0']
                },
                {
                    'keyword': 'ncols',
                    'type': 'numeric',
                    'format': ':18',
                    'version': ['1.01']
                }
            ]
        },
        {
            'slug': 'nodata',
            'values': [
                {
                    'keyword': 'nodata',
                    'type': 'numeric',
                    'format': ':10.4f',
                    'version': ['1.0', '2.0']
                },
                {
                    'keyword': 'nodata',
                    'type': 'numeric',
                    'format': ':18.4f',
                    'version': ['1.01']
                }
            ]
        },
        {
            'slug': 'creation_date',
            'values': [
                {
                    'keyword': 'creation date',
                    'type': 'numeric',
                    'format': '',
                    'version': ['2.0']
                }
            ]
        },
        {
            'slug': 'isg_format',
            'values': [
                {
                    'keyword': 'ISG format',
                    'type': 'numeric',
                    'format': ':10.1f',
                    'version': ['1.0', '2.0']
                },
                {
                    'keyword': 'ISG format',
                    'type': 'numeric',
                    'format': ':10.2f',
                    'version': ['1.01']
                }
            ]
        }
    ]
}