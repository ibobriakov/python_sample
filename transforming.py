__author__ = 'IGOR'

from pandas import *
import glob
import datetime


# TODO: refactor these 2 functions
def lat_from_address(row):
    from pygeocoder import Geocoder
    lat, lon = Geocoder.geocode(row['Address']).coordinates
    return lat

def lon_from_address(row):
    from pygeocoder import Geocoder
    lat, lon = Geocoder.geocode(row['Address']).coordinates
    return lon


# y = 24*dayofweek + hour
def hour_from_code(row):
    day_of_week = int(row['DayOfWeek'])
    hour = int(row['HourFrom'])
    if day_of_week == 6:
        return hour
    else:
        return 24*(day_of_week+1) + hour

def hour_to_code(row):
    day_of_week = int(row['DayOfWeek'])
    hour = int(row['HourTo'])
    if day_of_week == 6:
        return hour
    else:
        return 24*(day_of_week+1) + hour
	


def get_amount_by_loc(DF, lat, lon, hour_start, hour_finish, margin = 0.02):
    qualified_points = DF[(DF['hour'] >= hour_start) & (DF['hour'] <= hour_finish )]

    qualified_points = qualified_points[ (qualified_points['lat1'] > lat - margin) 
                        & (qualified_points['lat1'] < lat + margin ) ] 
    qualified_points = qualified_points[ (qualified_points['lon1'] > lon - margin ) 
                        & (qualified_points['lon1'] < lon + margin ) ] 

    qualified_points.to_csv('log_filtered_by_event_3.csv')

    return qualified_points['amount'].sum()


def get_proper_test_set(foldername):
    import os

    # Set the directory you want to start from
    rootDir = '.'
    for dirName, subdirList, fileList in os.walk(rootDir):
        if foldername == dirName[-10:]:
            print "Found", foldername
            fname = os.path.join(dirName,'part-r-00000')
            result = read_table(fname , names=["id", "hour", "amount", "lat1",
                                            "lon1", "lat2", "lon2", "lat3", "lon3"])
            return result
	return -1

def get_amount(row):
    total = get_amount_by_loc(get_proper_test_set(row['Datetime'].strftime("%Y-%m-%d")), row['Lat'],
                             row['Lon'], row['HourFromCode'], int(row['HourToCode']), 0.01)
    print total
    return total

def get_amount_many(row, margin = 0.01):
    total_1 = get_amount_by_loc(get_proper_test_set(row['Datetime'].strftime("%Y-%m-%d")), row['Lat'],
                             row['Lon'], row['HourFromCode'], int(row['HourToCode']), margin)

    total = get_amount_by_loc(get_proper_test_set(row['Datetime'].strftime("%Y-%m-%d")), row['Lat'],
                             row['Lon'], row['HourFromCode'], int(row['HourToCode']), 0.01)

    print margin, total_1, total
    return total_1	

	
target_lat = 51.55661
target_lon = -0.279481

# hour code transformation

train_set = read_csv('train.csv')
train_set['HourFrom'] = train_set['Time From'].apply(lambda x: x[-5:-3] ) #[-5:]
train_set['HourTo'] = train_set['Time To'].apply(lambda x: x[-5:-3] ) #[-5:]

train_set['Datetime'] = train_set['Time From'].apply(lambda x: datetime.datetime.strptime(x, '%d.%m.%Y %H:%M')) #[-5:]
train_set['DayOfWeek'] = train_set['Datetime'].apply(lambda x: x.dayofweek)


train_set['Lat'] = train_set.apply(lat_from_address, axis=1)
train_set['Lon'] = train_set.apply(lon_from_address, axis=1)

train_set['HourFromCode'] = train_set.apply(hour_from_code, axis=1)
train_set['HourToCode'] = train_set.apply(hour_to_code, axis=1)

train_set.to_csv('train_calculated.csv')  