from Methods import Snoopy, Elephant

# Scan to fill databases
FACEBOOK_TOKEN = 'EAAEd3h8ryTIBAIysNjY7gfk2E0dGnvnAfspf3FHNSIeAl8xQc2Awq3LLDc2cPeWke3lffIsN2FvtJSpHd6cF9LxDIYvGvvLgI1qRLfhQNL55bilVt4AxjJKZAYUpOZBqLxIZBiuHTwdDUuWtkh612108PaTOj7V4d7KUMmInUji0fPxu7mBgbewolJ1NVox2S4jDRaKQgZDZD'
GOOGLE_MAPS_KEY = 'AIzaSyDIDDkCDEoBHyF-sS2mjuhq0o_0UU59Fuc'
INSTAGRAM_TOKEN = 'IGQVJXVVNjbDZALYjZAtYlpyaDA5VS1vSXVLSUFFdVc5VWlieDFadl9UdW9yUFI2TWlOcUpDYm1DMjQ2YmVmSko2SlpWSllCaGZAxSUxuUGptNWxKYkRuZAHVQSGNSVnRrbXViblpUcWV3dGVBbUtsdFdYQgZDZD'


def data_eater_groups():
    # We look on google places
    reader = open("./Source/worldcities.csv").read().split('\n')
    reader.pop(0)
    reader = reader[4715:]
    for city in reader:
        print(city)
        city = city.replace('"', '').split(',')
        city_id = snoopy.database.city_check(city[1])
        country_id = snoopy.database.country_check(city[4])
        go = snoopy.get_go_nearby(latitude=float(city[2]), longitude=float(city[3]), distance=50000, query='capoeira')['results']
        for group in go:
            group = snoopy.make_google_pretty(group)
            snoopy.database.group_check_google(group, city_id, country_id)
        #fb = snoopy.get_fb_nearby(latitude=float(city[2]), longitude=float(city[3]), distance=50000, limit=100, query='capoeira')['data']
        #for group in fb:
        #    snoopy.make_facebook_pretty(group, city)
        #    snoopy.database.group_compare_fb_go(group, city_id, country_id)


def cagada_del_gilipollas():
    import requests
    import json
    snoopy.database.open_connection()
    snoopy.database.cursor.execute("SELECT group_picture_url, group_google_id FROM groups")
    x = list(snoopy.database.cursor.fetchall())
    for i, f in enumerate(x):
        detail = requests.get(
            "https://maps.googleapis.com/maps/api/place/details/json?place_id={}&fields=photo&key={}".format(
                list(f)[1], GOOGLE_MAPS_KEY)) if f[1] is not None else None
        if detail is not None and 'result' in json.loads(detail.content.decode('utf8').replace("\n", '')).keys():
            detail = json.loads(detail.content.decode('utf8').replace("\n", ''))['result']
            d = snoopy.get_pic_go(detail['photos'][0]['photo_reference']) if 'photos' in detail.keys() else None
            if d is not None:
                snoopy.database.cursor.execute("UPDATE groups SET group_picture_url = ? WHERE group_google_id = ?;", (d, f[1]))
                print(i)
                snoopy.database.connection.commit()
    snoopy.database.close_connection()


def better_location():
    snoopy.database.open_connection()
    snoopy.database.cursor.execute("SELECT group_id, group_location FROM groups;")
    locations_string = snoopy.database.cursor.fetchall()
    for location in locations_string:
        latitude = float(list(location)[1].split(' ')[0])
        longitude = float(list(location)[1].split(' ')[1])
        snoopy.database.cursor.execute("UPDATE groups SET group_latitude = ?, group_longitude = ? WHERE group_id = ?;", (latitude, longitude, list(location)[0]))
        snoopy.database.connection.commit()


# We instantiate the Snoopy
elephant = Elephant()
snoopy = Snoopy(FACEBOOK_TOKEN, GOOGLE_MAPS_KEY, elephant)

data_eater_groups()
snoopy.database.group_compare_all()



