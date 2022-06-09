import re


def dms_to_deg(dms):
    if '°' in dms:
        degrees, minutes, seconds = [int(i) for i in re.split('[°\'"]', dms[:-1])]
    elif '\'' in dms:
        degrees = 0
        minutes, seconds = [int(i) for i in re.split('[\'"]', dms[:-1])]
    else:
        degrees = 0
        minutes = 0
        seconds = [int(i) for i in re.split('["]', dms[:-1])][0]
    decimal_degrees = degrees + minutes / 60 + seconds / 3600
    return round(decimal_degrees, 6)
