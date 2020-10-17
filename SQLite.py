import geopy
import sqlite3
import hashlib
from sqlite3 import Error
from datetime import datetime
from geopy.distance import distance, lonlat


class DatabaseSQLite:
    def __init__(self, db_file, relation_distance, default_group_img, default_user_img):
        super(DatabaseSQLite, self).__init__()
        self.db_file = db_file
        self.connection = None
        self.cursor = None
        self.open_connection()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.close_connection()
        self.relationDistance = relation_distance
        self.default_group_image = default_group_img
        self.default_user_image = default_user_img

    # DATA EATER FUNCTIONS #
    ########################

    # Data Eater Function: Check if a group already exists on the DB
    def group_check_google(self, body, city_fk, country_fk):
        self.open_connection()
        self.cursor.execute("SELECT group_id FROM groups WHERE group_google_id = ?;", (body['id'],))
        group_id = self.cursor.fetchone()
        if group_id is None:
            # If it doesn't exists, we check if it is the same place of other already on the DB
            self.cursor.execute("SELECT * FROM groups WHERE group_city_id = ?;", (city_fk,))
            city_groups = self.cursor.fetchall()
            existed = False
            for group in city_groups:
                group = list(group)
                lat_diff = body['location']['latitude'] - group[16]
                lng_diff = body['location']['longitude'] - group[17]
                # If the group is within around 35m from other on the DB, we consider it is the same,
                # and we merge the info from both of them
                if abs(lat_diff) < 0.00035 and abs(lng_diff) < 0.00035:
                    existed = True
                    self.cursor.execute("SELECT * FROM groups WHERE group_id = ?;", (group[0],))
                    group_1 = list(self.cursor.fetchone())
                    group_1[1] = body['name'] if group_1[1] is None and 'name' in body.keys() else group_1[1]
                    group_1[2] = body['pic_url'] if group_1[2] is None and 'pic_url' in body.keys() else group_1[2]
                    group_1[3] = body['website'] if group_1[3] is None and 'website' in body.keys() else group_1[3]
                    group_1[4] = body['phone'] if group_1[4] is None and 'phone' in body.keys() else group_1[4]
                    group_1[10] = body['street'] if group_1[10] is None and 'street' in body.keys() else group_1[10]
                    self.cursor.execute("UPDATE groups SET "
                                        "group_name = ?,"
                                        "group_picture_url = ?,"
                                        "group_url = ?,"
                                        "group_phone = ?,"
                                        "group_verified = ?,"
                                        "group_opening_hours = ?,"
                                        "group_google_id = ?,"
                                        "group_description = ?,"
                                        "group_address = ?,"
                                        "group_location = ?,"
                                        "group_city_id = ?,"
                                        "group_country_id = ?,"
                                        "group_owner_id = ?,"
                                        "group_school_id = ?,"
                                        "group_latitude = ?,"
                                        "group_longitude = ?"
                                        "WHERE group_id = ?;",
                                        (group_1[1], group_1[2] if group_1[
                                                                       2] is None else self.default_group_image,
                                         group_1[3], group_1[4], group_1[5], group_1[6],
                                         group_1[8], group_1[9],
                                         group_1[10], group_1[11], group_1[12],
                                         group_1[13], group_1[14], group_1[15],
                                         group_1[16], group_1[17],
                                         group_1[0]))
                    print('Updated Google: {}'.format(group_1[1]))
                    self.connection.commit()
            if not existed:
                self.cursor.execute("INSERT INTO groups ("
                                    "group_name,"
                                    "group_picture_url,"
                                    "group_url,"
                                    "group_phone,"
                                    "group_verified,"
                                    "group_google_id,"
                                    "group_description,"
                                    "group_address,"
                                    "group_location,"
                                    "group_city_id,"
                                    "group_country_id,"
                                    "group_latitude,"
                                    "group_longitude"
                                    ")"
                                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);",
                                    (body['name'],
                                     body['pic_url'] if 'pic_url' in body.keys() else None,
                                     body['website'] if 'website' in body.keys() else None,
                                     body['phone'] if 'phone' in body.keys() else None,
                                     False,
                                     body['id'],
                                     body['about'] if 'about' in body.keys() else None,
                                     body['location']['street'] if 'street' in body['location'].keys() else None,
                                     str(body['location']['latitude']) + " " + str(body['location']['longitude']),
                                     city_fk,
                                     country_fk,
                                     body['location']['latitude'],
                                     body['location']['longitude']))
                print('Inserted Google: {}'.format(body['name']))
                self.connection.commit()
                self.cursor.execute("SELECT group_id FROM groups WHERE group_name = ?;", (body['name'],))
        self.close_connection()

    # Data Eater Function: Checks all groups to see if they are the same
    def group_compare_all(self):
        self.open_connection()
        self.cursor.execute("SELECT city_id FROM cities;")
        cities = self.cursor.fetchall()
        for city in cities:
            self.cursor.execute("SELECT * FROM groups WHERE group_city_id = ?;", (city[0],))
            groups = list(self.cursor.fetchall())
            for group in groups:
                group = list(group)
                no_check = []
                if groups is None:
                    self.cursor.execute("SELECT * FROM groups WHERE group_city_id = ?;", (group[12],))
                    groups = list(self.cursor.fetchall())
                for group_to_check in groups:
                    if group[0] != group_to_check[0] and group[0] not in no_check:
                        group_to_check = list(group_to_check)
                        lat_diff = group[16] - group_to_check[16]
                        lng_diff = group[17] - group_to_check[17]
                        if abs(lat_diff) < 0.00035 and abs(lng_diff) < 0.00035:
                            no_check.append(group_to_check[0])
                            self.cursor.execute("SELECT * FROM groups WHERE group_id = ?;", (group[0],))
                            group_1 = list(self.cursor.fetchone())
                            self.cursor.execute("SELECT * FROM groups WHERE group_id = ?;", (group_to_check[0],))
                            group_2 = list(self.cursor.fetchone())
                            for i in range(1, len(group_1)):
                                group_1[i] = group_2[i] if group_1[i] is None and group_2[i] is not None else group_1[i]
                            self.cursor.execute("UPDATE groups SET "
                                                "group_name = ?,"
                                                "group_picture_url = ?,"
                                                "group_url = ?,"
                                                "group_phone = ?,"
                                                "group_verified = ?,"
                                                "group_opening_hours = ?,"
                                                "group_facebook_id = ?,"
                                                "group_google_id = ?,"
                                                "group_description = ?,"
                                                "group_address = ?,"
                                                "group_location = ?,"
                                                "group_city_id = ?,"
                                                "group_country_id = ?,"
                                                "group_owner_id = ?,"
                                                "group_school_id = ?,"
                                                "group_latitude = ?,"
                                                "group_longitude = ?"
                                                "WHERE group_id = ?;",
                                                (group_1[1], group_1[2], group_1[3],
                                                 group_1[4], group_1[5], group_1[6],
                                                 group_1[7], group_1[8], group_1[9],
                                                 group_1[10], group_1[11], group_1[12],
                                                 group_1[13], group_1[14], group_1[15],
                                                 group_1[16], group_1[17], group_1[0]))
                            self.cursor.execute("DELETE FROM groups WHERE group_id = ?;", (group_2[0],))
                            self.connection.commit()
        self.close_connection()

    # Data Eater Function: Checks a FB group to see if it's already in the database = if exists in Google
    def group_compare_fb_go(self, body, city_fk, country_fk):
        self.open_connection()
        self.cursor.execute("SELECT group_id FROM groups WHERE group_facebook_id = ?;", (body['id'],))
        group_id = self.cursor.fetchone()
        if group_id is None:
            # If it doesn't exist
            self.cursor.execute("SELECT * FROM groups WHERE group_city_id = ?;", (city_fk,))
            city_groups = self.cursor.fetchall()
            existed = False
            for group in city_groups:
                group = list(group)
                lat_diff = body['location']['latitude'] - group[16]
                lng_diff = body['location']['longitude'] - group[17]
                # If the group is within around 35m from other on the DB, we consider it is the same,
                # and we merge the info from both of them
                if abs(lat_diff) < 0.00035 and abs(lng_diff) < 0.00035:
                    existed = True
                    self.cursor.execute("SELECT * FROM groups WHERE group_id = ?;", (group[0],))
                    group_1 = list(self.cursor.fetchone())
                    group_1[1] = body['name'] if group_1[1] is None and 'name' in body.keys() else group_1[1]
                    group_1[2] = body['pic_url'] if group_1[2] is None and 'pic_url' in body.keys() else group_1[2]
                    group_1[3] = body['website'] if group_1[3] is None and 'website' in body.keys() else group_1[3]
                    group_1[4] = body['phone'] if group_1[4] is None and 'phone' in body.keys() else group_1[4]
                    group_1[7] = body['id']
                    group_1[10] = body['street'] if group_1[10] is None and 'street' in body.keys() else group_1[10]
                    self.cursor.execute("UPDATE groups SET "
                                        "group_name = ?,"
                                        "group_picture_url = ?,"
                                        "group_url = ?,"
                                        "group_phone = ?,"
                                        "group_verified = ?,"
                                        "group_opening_hours = ?,"
                                        "group_facebook_id = ?,"
                                        "group_description = ?,"
                                        "group_address = ?,"
                                        "group_location = ?,"
                                        "group_city_id = ?,"
                                        "group_country_id = ?,"
                                        "group_owner_id = ?,"
                                        "group_school_id = ?,"
                                        "group_latitude = ?,"
                                        "group_longitude = ?"
                                        "WHERE group_id = ?;",
                                        (group_1[1], group_1[2], group_1[3],
                                         group_1[4], group_1[5], group_1[6],
                                         group_1[7], group_1[9],
                                         group_1[10], group_1[11], group_1[12],
                                         group_1[13], group_1[14], group_1[15],
                                         group_1[16], group_1[17], group_1[0]))
                    print('Updated Facebook: {}'.format(group_1[1]))
                    self.connection.commit()
            if not existed:
                self.cursor.execute("INSERT INTO groups ("
                                    "group_name,"
                                    "group_picture_url,"
                                    "group_url,"
                                    "group_phone,"
                                    "group_verified,"
                                    "group_facebook_id,"
                                    "group_description,"
                                    "group_address,"
                                    "group_location,"
                                    "group_city_id,"
                                    "group_country_id,"
                                    "group_latitude,"
                                    "group_longitude"
                                    ")"
                                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);",
                                    (body['name'],
                                     body['pic_url'] if 'pic_url' in body.keys() else None,
                                     body['website'] if 'website' in body.keys() else None,
                                     body['phone'] if 'phone' in body.keys() else None,
                                     False,
                                     body['id'],
                                     body['about'] if 'about' in body.keys() else None,
                                     body['location']['street'] if 'street' in body['location'].keys() else None,
                                     str(body['location']['latitude']) + " " + str(
                                         body['location']['longitude']),
                                     city_fk,
                                     country_fk,
                                     body['location']['latitude'],
                                     body['location']['longitude']))
                print('Inserted Facebook: {}'.format(body['name']))
                self.connection.commit()
                self.cursor.execute("SELECT group_id FROM groups WHERE group_name = ?;", (body['name'],))
        self.close_connection()

    # Data Eater Function: Checks if a city is already on the DB
    def city_check(self, city):
        self.open_connection()
        self.cursor.execute("SELECT city_id FROM cities WHERE city_name = ?;", (city,))
        city_id = self.cursor.fetchone()
        if city_id is not None:
            self.close_connection()
        else:
            self.cursor.execute("INSERT INTO cities (city_name) VALUES (?);", (city,))
            self.connection.commit()
            self.cursor.execute("SELECT city_id FROM cities WHERE city_name = ?;", (city,))
            city_id = self.cursor.fetchone()
            self.close_connection()
        return city_id[0]

    # Data Eater Function: Checks if a country is already on the DB
    def country_check(self, country):
        self.open_connection()
        self.cursor.execute("SELECT country_id FROM countries WHERE country_name = ?;", (country,))
        country_id = self.cursor.fetchone()
        if country_id is not None:
            self.close_connection()
        else:
            self.cursor.execute("INSERT INTO countries (country_name) VALUES (?);", (country,))
            self.connection.commit()
            self.cursor.execute("SELECT country_id FROM countries WHERE country_name = ?;", (country,))
            country_id = self.cursor.fetchone()
            self.close_connection()
        return country_id[0]

    # APPOEIRA FUNCTIONS #
    ########################

    # APPoeira Function: Returns all groups within a distance. Function called when /location-group invoked
    def group_get_based_on_location(self, latitude, longitude, distance_):
        offset = distance_ * self.relationDistance
        self.open_connection()
        self.cursor.execute("SELECT "
                            "group_id, "
                            "group_name, "
                            "group_picture_url, "
                            "group_phone, "
                            "group_verified, "
                            "group_latitude, "
                            "group_longitude "
                            "FROM groups "
                            "WHERE group_latitude BETWEEN ? AND ? "
                            "AND group_longitude BETWEEN ? AND ?;",
                            (latitude - offset, latitude + offset,
                             longitude - offset, longitude + offset,))
        results = self.cursor.fetchall()
        if results is not None:
            import statistics
            results = list(results)
            groups = []
            for result in results:
                ratings = None
                if list(result)[4] == 1:
                    self.cursor.execute("SELECT u_r_g_rating FROM user_rating_group WHERE u_r_g_group_id = ?",
                                        (list(result)[0],))
                    ratings = list(self.cursor.fetchall())
                    ratings = [rating[0] for rating in ratings] if ratings != [] else None
                dictionary = {"id": list(result)[0],
                              "name": list(result)[1],
                              "picUrl": list(result)[2],
                              "phone": list(result)[3],
                              "verified": False if list(result)[4] == 0 else True,
                              "rating": statistics.mean(ratings) if ratings is not None else 0.0,
                              "votes": len(ratings) if ratings is not None else 0,
                              'latitude': list(result)[5],
                              'longitude': list(result)[6],
                              "distance": float('%.1f' % geopy.distance.distance(lonlat(*[latitude, longitude]),
                                                                                 (lonlat(list(result)[5],
                                                                                         list(result)[6]))).km)
                              }
                groups.append(dictionary)
            self.close_connection()
            groups.sort(key=lambda s: (-s['rating'], s["distance"]))
            return groups
        self.close_connection()
        return None

    # APPoeira Function: Returns all rodas within a distance. Function called when /location-roda invoked
    def roda_get_based_on_location(self, latitude, longitude, distance_):
        offset = distance_ * self.relationDistance
        self.open_connection()
        self.cursor.execute("SELECT "
                            "roda_id, "
                            "roda_name, "
                            "roda_date, "
                            "roda_pic_url, "
                            "roda_verified, "
                            "roda_latitude, "
                            "roda_longitude "
                            "FROM rodas "
                            "WHERE roda_latitude BETWEEN ? AND ? "
                            "AND roda_longitude BETWEEN ? AND ?;",
                            (latitude - offset, latitude + offset,
                             longitude - offset, longitude + offset,))
        rodas = self.cursor.fetchall()
        if rodas is not None:
            import statistics
            result = []
            rodas = list(rodas)
            for roda in rodas:
                ratings = None
                if list(roda)[4] == 1:
                    self.cursor.execute("SELECT u_r_r_rating FROM user_rating_roda WHERE u_r_r_roda_id = ?",
                                        (list(roda)[0],))
                    ratings = list(self.cursor.fetchall())
                    ratings = [rating[0] for rating in ratings] if ratings != [] else None
                self.cursor.execute("SELECT "
                                    "user_id, "
                                    "user_apelhido, "
                                    "rank_name "
                                    "FROM users "
                                    "INNER JOIN ranks ON user_rank_id = rank_id "
                                    "INNER JOIN user_roda ON u_r_user_id = user_id AND u_r_role_id = 1 "
                                    "INNER JOIN rodas ON roda_id = ?;",
                                    (list(roda)[0],))
                owner = self.cursor.fetchone()
                result.append({"id": list(roda)[0],
                               "name": list(roda)[1],
                               "date": list(roda)[2].split('-')[0] + '-' +
                                       list(roda)[2].split('-')[1] + '-' +
                                       list(roda)[2].split('-')[2] + ' ' +
                                       list(roda)[2].split('-')[3] + ':' +
                                       list(roda)[2].split('-')[4],
                               "picUrl": list(roda)[3],
                               "verified": False if list(roda)[4] == 0 else True,
                               'latitude': list(roda)[5],
                               'longitude': list(roda)[6],
                               "distance": float('%.1f' % geopy.distance.distance(lonlat(*[latitude, longitude]),
                                                                                  (lonlat(list(roda)[5],
                                                                                          list(roda)[6]))).km),
                               'ownerApelhido': list(owner)[1],
                               'ownerRank': list(owner)[2],
                               'rating': statistics.mean(ratings) if ratings is not None else 0.0
                               })
            result.sort(key=lambda s: (-s['rating'], s["distance"]))
            return result
        return [{"id": None,
                 "name": None,
                 "date": None,
                 "picUrl": None,
                 "verified": False,
                 'latitude': None,
                 'longitude': None,
                 "distance": None,
                 'ownerApelhido': None,
                 'ownerRank': None,
                 'rating': None
                 }]

    # APPoeira Function: Inserts a new Roda on the DB. Function called when /roda-created invoked
    def roda_create(self, owners, name, description, date, invited, latitude, longitude, city, country, phone, elephant, image):
        self.open_connection()
        self.cursor.execute("SELECT city_id FROM cities WHERE city_name = ?;", (city,))
        city_id = self.cursor.fetchone()
        self.cursor.execute("SELECT country_id FROM countries WHERE country_name = ?;", (country,))
        country_id = self.cursor.fetchone()
        response = self.cursor.execute("INSERT INTO rodas ("
                                       "roda_name, "
                                       "roda_date, "
                                       "roda_description, "
                                       "roda_verified, "
                                       "roda_latitude, "
                                       "roda_longitude, "
                                       "roda_city_id, "
                                       "roda_country_id, "
                                       "roda_phone "
                                       ") "
                                       "VALUES (?,?,?,?,?,?,?,?,?);",
                                       (name, date, description, True, latitude, longitude, city_id[0],
                                        country_id[0], phone))
        if response.rowcount > 0:
            self.cursor.execute("SELECT roda_id "
                                "FROM rodas "
                                "WHERE roda_latitude = ?"
                                "AND roda_longitude = ?",
                                (latitude, longitude))
            roda_id = self.cursor.fetchone()
            if roda_id is not None:
                url, ok, pic_name = elephant.upload_object(image, roda_id[0])
                self.cursor.execute("UPDATE rodas SET "
                                    "roda_pic_url = ? "
                                    "WHERE roda_id = ?;",
                                    (url if url != "" else self.default_group_image, roda_id[0]))
                self.cursor.execute("INSERT INTO user_roda ("
                                    "u_r_user_id, "
                                    "u_r_roda_id, "
                                    "u_r_role_id, "
                                    "u_r_accepted, "
                                    "u_r_date "
                                    ") "
                                    "VALUES (?,?,?,?,?)",
                                    (owners[0], roda_id[0], 1, True, datetime.utcnow()))
                inviteds = [(user_invited, roda_id[0], 2, datetime.utcnow(), False) for user_invited in invited]
                self.cursor.executemany("INSERT INTO user_roda ("
                                        "u_r_user_id, "
                                        "u_r_roda_id, "
                                        "u_r_role_id, "
                                        "u_r_date, "
                                        "u_r_accepted"
                                        ") "
                                        "VALUES (?,?,?,?,?)",
                                        (inviteds))
                self.close_connection()
                return {"id": roda_id[0],
                        }
        self.close_connection()
        return {"id": None,
                }

    # APPoeira Function: Returns roda detail. Function called when /roda-detail invoked
    def roda_detail(self, roda_id, user_id):
        import Methods
        sailor = Methods.Sailor()
        self.open_connection()
        self.cursor.execute("SELECT roda_id, "
                            "roda_name, "
                            "roda_pic_url, "
                            "roda_description, "
                            "roda_phone, "
                            "roda_verified, "
                            "city_name, "
                            "country_name, "
                            "roda_latitude, "
                            "roda_longitude "
                            "FROM rodas JOIN cities JOIN countries "
                            "ON rodas.roda_city_id = cities.city_id AND "
                            "rodas.roda_country_id = countries.country_id "
                            "WHERE roda_id = ?;",
                            (roda_id,))
        roda = self.cursor.fetchone()
        if roda is not None:
            import statistics
            roda = list(roda)
            ratings = None
            if list(roda)[5] == 1:
                self.cursor.execute("SELECT u_r_r_rating FROM user_rating_roda WHERE u_r_r_roda_id = ?",
                                    (list(roda)[0],))
                ratings = list(self.cursor.fetchall())
                ratings = [rating[0] for rating in ratings] if ratings != [] else None
            self.cursor.execute("SELECT roda_id "
                                "FROM rodas "
                                "INNER JOIN user_roda ON roda_id = u_r_roda_id "
                                "INNER JOIN users ON u_r_user_id = user_id "
                                "WHERE user_id = ? "
                                "AND roda_id = ?;",
                                (user_id, roda_id))
            member = self.cursor.fetchall()
            self.cursor.execute("SELECT u_r_r_rating "
                                "FROM user_rating_roda "
                                "INNER JOIN rodas ON roda_id = u_r_r_roda_id "
                                "INNER JOIN users ON u_r_r_user_id = user_id "
                                "WHERE user_id = ?"
                                "AND roda_id = ?;",
                                (user_id, roda_id))
            vote = self.cursor.fetchall()
            self.cursor.execute("SELECT roda_id "
                                "FROM rodas "
                                "INNER JOIN user_roda ON roda_id = u_r_roda_id "
                                "INNER JOIN users ON u_r_user_id = user_id AND u_r_role_id = 1 "
                                "WHERE user_id = ? "
                                "AND roda_id = ?;",
                                (user_id, roda_id))
            owner = self.cursor.fetchall()
            self.close_connection()
            return {"error": '',
                    "id": list(roda)[0],
                    "name": list(roda)[1],
                    "picUrl": list(roda)[2],
                    "description": list(roda)[3],
                    "phone": list(roda)[4],
                    "verified": False if list(roda)[5] == 0 else True,
                    "rating": statistics.mean(ratings) if ratings is not None else 0.0,
                    "votes": len(ratings) if ratings is not None else 0,
                    "address": sailor.full_address_from_latlng(list(roda)[8], list(roda)[9]),
                    "city": list(roda)[6],
                    "country": list(roda)[7],
                    "latitude": list(roda)[8],
                    "longitude": list(roda)[9],
                    "isMember": True if member != [] else False,
                    "hasVoted": vote[0][0] if vote != [] else 0,
                    "isOwner": True if owner != [] else False,
                    }
        self.close_connection()
        return {"error": 'Wrong User',
                "id": None,
                "name": None,
                "picUrl": None,
                "description": None,
                "phone": None,
                "verified": None,
                "rating": None,
                "votes": None,
                "address": None,
                "city": None,
                "country": None,
                "latitude": None,
                "longitude": None,
                "isMember": None,
                "hasVoted": None,
                "isOwner": None
                }

    # APPoeira Function: Returns all events within a distance. Function called when /location-event invoked
    def event_get_based_on_location(self, latitude, longitude, distance_):
        offset = distance_ * self.relationDistance
        self.open_connection()
        self.cursor.execute("SELECT "
                            "event_id, "
                            "event_name, "
                            "event_date, "
                            "event_pic_url, "
                            "event_verified, "
                            "event_latitude, "
                            "event_longitude "
                            "FROM events "
                            "WHERE event_latitude BETWEEN ? AND ? "
                            "AND event_longitude BETWEEN ? AND ?;",
                            (latitude - offset, latitude + offset,
                             longitude - offset, longitude + offset,))
        presential_events = self.cursor.fetchall()
        self.cursor.execute("SELECT "
                            "event_id, "
                            "event_name, "
                            "event_date, "
                            "event_pic_url, "
                            "event_verified, "
                            "event_latitude, "
                            "event_longitude "
                            "FROM events "
                            "WHERE event_latitude isnull "
                            "AND event_longitude isnull;")
        online_events = self.cursor.fetchall()
        if presential_events is not None and online_events is not None:
            events = presential_events + online_events
        elif presential_events is not None and online_events is None:
            events = presential_events
        elif presential_events is None and online_events is not None:
            events = online_events
        else:
            events = None
        if events is not None:
            import statistics
            result = []
            events = list(events)
            for event in events:
                ratings = None
                if list(event)[4] == 1:
                    self.cursor.execute("SELECT u_r_e_rating FROM user_rating_event WHERE u_r_e_event_id = ?",
                                        (list(event)[0],))
                    ratings = list(self.cursor.fetchall())
                    ratings = [rating[0] for rating in ratings] if ratings != [] else None
                self.cursor.execute("SELECT "
                                    "user_id, "
                                    "user_apelhido, "
                                    "rank_name "
                                    "FROM users "
                                    "INNER JOIN ranks ON user_rank_id = rank_id "
                                    "INNER JOIN user_event ON u_e_user_id = user_id AND u_e_role_id = 1 "
                                    "INNER JOIN events ON event_id = ?;",
                                    (list(event)[0],))
                owner = self.cursor.fetchone()
                self.cursor.execute("SELECT "
                                    "e_p_platform_id, "
                                    "e_p_key "
                                    "FROM event_platform "
                                    "INNER JOIN events ON e_p_event_id = event_id "
                                    "AND event_id = ?;",
                                    (list(event)[0],))
                platform = self.cursor.fetchone()
                result.append({"id": list(event)[0],
                               "name": list(event)[1],
                               "date": list(event)[2].split('-')[0] + '-' +
                                       list(event)[2].split('-')[1] + '-' +
                                       list(event)[2].split('-')[2] + ' ' +
                                       list(event)[2].split('-')[3] + ':' +
                                       list(event)[2].split('-')[4],
                               "picUrl": list(event)[3],
                               "verified": False if list(event)[4] == 0 else True,
                               'latitude': list(event)[5],
                               'longitude': list(event)[6],
                               "distance": float('%.1f' % geopy.distance.distance(lonlat(*[latitude, longitude]),
                                                                                  (lonlat(list(event)[5],
                                                                                          list(event)[6]))).km),
                               'ownerApelhido': list(owner)[1],
                               'ownerRank': list(owner)[2],
                               'platform': list(platform)[0],
                               'key': list(platform)[1],
                               "rating": statistics.mean(ratings) if ratings is not None else 0.0
                               })
            result.sort(key=lambda s: (-s['rating'], s["distance"]))
            return result
        return [{"id": None,
                 "name": None,
                 "date": None,
                 "picUrl": None,
                 "verified": False,
                 'latitude': None,
                 'longitude': None,
                 "distance": None,
                 'ownerApelhido': None,
                 'ownerRank': None,
                 'platform': 0,
                 'key': None,
                 'rating': None
                 }]

    # APPoeira Function: Returns event detail. Function called when /event-detail invoked
    def event_detail(self, event_id, user_id):
        import Methods
        sailor = Methods.Sailor()
        self.open_connection()
        self.cursor.execute("SELECT event_latitude FROM events WHERE event_id = ?", (event_id,))
        aux_event = list(self.cursor.fetchone())
        if aux_event[0] is None:
            presential = False
            self.cursor.execute("SELECT event_id, "
                                "event_name, "
                                "event_pic_url, "
                                "event_description, "
                                "event_phone, "
                                "event_verified, "
                                "platform_name "
                                "FROM events "
                                "INNER JOIN event_platform ON event_id = e_p_event_id "
                                "INNER JOIN platforms ON platform_id = e_p_platform_id "
                                "WHERE event_id = ?;",
                                (event_id,))
        else:
            presential = True
            self.cursor.execute("SELECT event_id, "
                                "event_name, "
                                "event_pic_url, "
                                "event_description, "
                                "event_phone, "
                                "event_verified, "
                                "city_name, "
                                "country_name, "
                                "event_latitude, "
                                "event_longitude "
                                "FROM events JOIN cities JOIN countries "
                                "ON events.event_city_id = cities.city_id AND "
                                "events.event_country_id = countries.country_id "
                                "WHERE event_id = ?;",
                                (event_id,))
        event = self.cursor.fetchone()
        if event is not None:
            import statistics
            event = list(event)
            ratings = None
            if list(event)[5] == 1:
                self.cursor.execute("SELECT u_r_e_rating FROM user_rating_event WHERE u_r_e_event_id = ?",
                                    (list(event)[0],))
                ratings = list(self.cursor.fetchall())
                ratings = [rating[0] for rating in ratings] if ratings != [] else None
            self.cursor.execute("SELECT user_id "
                                "FROM users "
                                "INNER JOIN user_event ON user_id = u_e_user_id "
                                "INNER JOIN events ON u_e_event_id = event_id "
                                "WHERE user_id = ? "
                                "AND event_id = ?;",
                                (user_id, event_id))
            member = self.cursor.fetchall()
            self.cursor.execute("SELECT u_r_e_rating "
                                "FROM user_rating_event "
                                "INNER JOIN events ON event_id = u_r_e_event_id "
                                "INNER JOIN users ON u_r_e_user_id = user_id "
                                "WHERE user_id = ?"
                                "AND event_id = ?;",
                                (user_id, event_id))
            vote = self.cursor.fetchall()
            self.cursor.execute("SELECT user_id "
                                "FROM users "
                                "INNER JOIN user_event ON user_id = u_e_user_id "
                                "INNER JOIN events ON u_e_event_id = event_id AND u_e_role_id = 1 "
                                "WHERE user_id = ? "
                                "AND event_id = ?;",
                                (user_id, event_id))
            owner = self.cursor.fetchall()
            self.close_connection()
            return {"error": '',
                    "id": list(event)[0],
                    "name": list(event)[1],
                    "picUrl": list(event)[2],
                    "description": list(event)[3],
                    "phone": list(event)[4],
                    "verified": False if list(event)[5] == 0 else True,
                    "rating": statistics.mean(ratings) if ratings is not None else 0.0,
                    "votes": len(ratings) if ratings is not None else 0,
                    "address": sailor.full_address_from_latlng(list(event)[8], list(event)[9]) if presential else "",
                    "city": list(event)[6] if presential else "",
                    "country": list(event)[7] if presential else "",
                    "latitude": list(event)[8] if presential else 0.0,
                    "longitude": list(event)[9] if presential else 0.0,
                    "platform": list(event)[6] if not presential else "",
                    "isMember": True if member != [] else False,
                    "hasVoted": vote[0][0] if vote != [] else 0,
                    "isOwner": True if owner != [] else False,
                    }
        self.close_connection()
        return {"error": 'Wrong User',
                "id": None,
                "name": None,
                "picUrl": None,
                "description": None,
                "phone": None,
                "verified": None,
                "rating": None,
                "votes": None,
                "address": None,
                "city": None,
                "country": None,
                "latitude": None,
                "longitude": None,
                "platform": None,
                "isMember": None,
                "hasVoted": None,
                "isOwner": None
                }

    # APPoeira Function: Inserts a new Event on the DB. Function called when /event-created invoked
    def event_create(self, owners, name, description, date, invited, platform, latitude, longitude, city,
                     country, phone, convided, key, elephant, image):
        self.open_connection()
        if platform == 6:
            self.cursor.execute("SELECT city_id FROM cities WHERE city_name = ?;", (city,))
            city_id = self.cursor.fetchone()
            self.cursor.execute("SELECT country_id FROM countries WHERE country_name = ?;", (country,))
            country_id = self.cursor.fetchone()
            response = self.cursor.execute("INSERT INTO events ("
                                           "event_name, "
                                           "event_date, "
                                           "event_description, "
                                           "event_verified, "
                                           "event_latitude, "
                                           "event_longitude, "
                                           "event_city_id, "
                                           "event_country_id, "
                                           "event_phone"
                                           ") "
                                           "VALUES (?,?,?,?,?,?,?,?,?);",
                                           (name, date,description, True, latitude, longitude, city_id[0],
                                            country_id[0], phone))
        else:
            response = self.cursor.execute("INSERT INTO events ("
                                           "event_name, "
                                           "event_date, "
                                           "event_description, "
                                           "event_verified, "
                                           "event_phone"
                                           ") "
                                           "VALUES (?,?,?,?,?);",
                                           (name, date, description, True, phone))
        if response.rowcount > 0:
            self.cursor.execute("SELECT event_id "
                                "FROM events "
                                "WHERE event_name = ?"
                                "AND event_date = ?",
                                (name, date))
            event_id = self.cursor.fetchone()
            if event_id is not None:
                url, ok, pic_name = elephant.upload_object(image, event_id[0])
                self.cursor.execute("UPDATE events SET "
                                    "event_pic_url = ? "
                                    "WHERE event_id = ?;",
                                    (url if url != "" else self.default_group_image, event_id[0]))
                self.cursor.execute("INSERT INTO event_platform ("
                                    "e_p_event_id, "
                                    "e_p_platform_id, "
                                    "e_p_key"
                                    ") "
                                    "VALUES (?,?,?)",
                                    (event_id[0], platform, key))
                self.cursor.execute("INSERT INTO user_event ("
                                    "u_e_user_id, "
                                    "u_e_event_id, "
                                    "u_e_role_id, "
                                    "u_e_date, "
                                    "u_e_accepted"
                                    ") "
                                    "VALUES (?,?,?,?,?)",
                                    (owners[0], event_id[0], 1, datetime.utcnow(), True))
                inviteds = [(user_invited, event_id[0], 2, datetime.utcnow(), False) for user_invited in invited]
                self.cursor.executemany("INSERT INTO user_event ("
                                        "u_e_user_id, "
                                        "u_e_event_id, "
                                        "u_e_role_id, "
                                        "u_e_date, "
                                        "u_e_accepted"
                                        ") "
                                        "VALUES (?,?,?,?,?)",
                                        (inviteds))
                convideds = [(user_convided, event_id[0], 3, datetime.utcnow(), False) for user_convided in convided]
                self.cursor.executemany("INSERT INTO user_event ("
                                        "u_e_user_id, "
                                        "u_e_event_id, "
                                        "u_e_role_id, "
                                        "u_e_date, "
                                        "u_e_accepted"
                                        ") "
                                        "VALUES (?,?,?,?,?)",
                                        (convideds))
                self.close_connection()
                return {"id": event_id[0],
                        }
        self.close_connection()
        return {"id": None,
                }

    # APPoeira Function: Inserts a new Online on the DB. Function called when /online-created invoked
    def online_create(self, owners, name, description, date, invited, platform, phone, key, elephant, image):
        self.open_connection()
        response = self.cursor.execute("INSERT INTO onlines ("
                                       "online_name, "
                                       "online_date, "
                                       "online_description, "
                                       "online_verified, "
                                       "online_phone "
                                       ") "
                                       "VALUES (?,?,?,?,?);",
                                       (name, date, description, True, phone))
        if response.rowcount > 0:
            self.cursor.execute("SELECT online_id "
                                "FROM onlines "
                                "WHERE online_name = ?"
                                "AND online_date = ?",
                                (name, date))
            online_id = self.cursor.fetchone()
            if online_id is not None:
                url, ok, pic_name = elephant.upload_object(image, online_id[0])
                self.cursor.execute("UPDATE onlines SET "
                                    "online_pic_url = ? "
                                    "WHERE online_id = ?;",
                                    (url if url != "" else self.default_group_image, online_id[0]))
                self.cursor.execute("INSERT INTO online_platform ("
                                    "o_p_online_id, "
                                    "o_p_platform_id, "
                                    "o_p_key"
                                    ") "
                                    "VALUES (?,?,?)",
                                    (online_id[0], platform, key))
                self.cursor.execute("INSERT INTO user_online ("
                                    "u_o_user_id, "
                                    "u_o_online_id, "
                                    "u_o_role_id, "
                                    "u_o_date, "
                                    "u_o_accepted"
                                    ") "
                                    "VALUES (?,?,?,?,?)",
                                    (owners[0], online_id[0], 1, datetime.utcnow(), True))
                inviteds = [(user_invited, online_id[0], 2, datetime.utcnow(), False) for user_invited in invited]
                self.cursor.executemany("INSERT INTO user_online ("
                                        "u_o_user_id, "
                                        "u_o_online_id, "
                                        "u_o_role_id, "
                                        "u_o_date, "
                                        "u_o_accepted"
                                        ") "
                                        "VALUES (?,?,?,?,?)",
                                        (inviteds))
                self.close_connection()
                return {"id": online_id[0],
                        }
        self.close_connection()
        return {"id": None,
                }

    # APPoeira Function: Sign Up functionality. Called when /sign-up invoked
    def user_signup(self, first_name, last_name, apelhido, email, password, rank):
        self.open_connection()
        self.cursor.execute("SELECT user_id FROM users "
                            "WHERE user_email = ?;",
                            (email,))
        if self.cursor.fetchone() is None:
            crypt = hashlib.new('sha256')
            crypt.update(password.encode())
            self.cursor.execute("INSERT INTO users ("
                                "user_first_name,"
                                "user_last_name,"
                                "user_apelhido,"
                                "user_email,"
                                "user_date_join,"
                                "user_premium,"
                                "user_pic_url,"
                                "user_password,"
                                "user_rank_id,"
                                "user_school_id, "
                                "user_email_verified "
                                ") "
                                "VALUES (?,?,?,?,?,?,?,?,?,?,?);",
                                (first_name, last_name,
                                 apelhido, email,
                                 datetime.utcnow(), False,
                                 self.default_user_image,
                                 crypt.hexdigest(), rank, 1, False))
            self.connection.commit()
            self.cursor.execute("SELECT user_id, "
                                "user_apelhido, "
                                "user_pic_url, "
                                "user_rank_id, "
                                "user_first_name, "
                                "user_last_name, "
                                "user_email_verified, "
                                "user_email "
                                "FROM users "
                                "WHERE user_email = ?;", (email,))
            user = list(self.cursor.fetchone())
            self.close_connection()
            return {'token': '',
                    'id': user[0],
                    'rank': user[3],
                    'name': user[4],
                    'lastName': user[5],
                    'apelhido': user[1],
                    'email': user[7],
                    'picUrl': user[2],
                    'emailVerified': False,
                    }
        self.close_connection()
        return {'token': None,
                'id': None,
                'rank': None,
                'name': None,
                'lastName': None,
                'apelhido': None,
                'email': None,
                'picUrl': None,
                'emailVerified': False,
                }

    # APPoeira Function: Login functionality. Called when /login invoked
    def user_login(self, email, password):
        crypt = hashlib.new('sha256')
        crypt.update(password.encode())
        self.open_connection()
        self.cursor.execute("SELECT user_id, "
                            "user_apelhido, "
                            "user_pic_url, "
                            "user_rank_id, "
                            "user_first_name, "
                            "user_last_name, "
                            "user_email_verified, "
                            "user_email "
                            "FROM users "
                            "WHERE user_email = ? AND user_password = ?;",
                            (email, crypt.hexdigest()))
        user = self.cursor.fetchone()
        if user is not None:
            user = list(user)
            self.close_connection()
            return {'token': '',
                    'id': user[0],
                    'rank': user[3],
                    'name': user[4],
                    'lastName': user[5],
                    'apelhido': user[1],
                    'email': user[7],
                    'picUrl': user[2],
                    'emailVerified': True if user[6] == 1 else False,
                    }
        self.close_connection()
        return {'token': None,
                'id': None,
                'rank': None,
                'name': None,
                'lastName': None,
                'apelhido': None,
                'email': None,
                'picUrl': None,
                'emailVerified': False,
                }

    # APPoeira Function: Email verification
    def email_verification(self, user_id):
        self.open_connection()
        response = self.cursor.execute("UPDATE users "
                                       "SET user_email_verified = true "
                                       "WHERE user_id = ?;",
                                       (user_id,))
        self.close_connection()
        return True if response.rowcount > 0 else False

    # APPoeira Function: Returns all groups within a distance. Function called when /group-detail invoked
    def group_detail(self, group_id, user_id):
        self.open_connection()
        self.cursor.execute("SELECT group_id, "
                            "group_name, "
                            "group_picture_url, "
                            "group_url, "
                            "group_phone, "
                            "group_verified, "
                            "group_opening_hours, "
                            "group_facebook_id, "
                            "group_google_id, "
                            "group_description, "
                            "group_address, "
                            "city_name, "
                            "country_name, "
                            "group_latitude, "
                            "group_longitude "
                            "FROM groups JOIN cities JOIN countries "
                            "ON groups.group_city_id = cities.city_id AND "
                            "groups.group_country_id = countries.country_id "
                            "WHERE group_id = ?;",
                            (group_id,))
        group = self.cursor.fetchone()
        if group is not None:
            import statistics
            group = list(group)
            ratings = None
            if list(group)[5] == 1:
                self.cursor.execute("SELECT u_r_g_rating FROM user_rating_group WHERE u_r_g_group_id = ?",
                                    (list(group)[0],))
                ratings = list(self.cursor.fetchall())
                ratings = [rating[0] for rating in ratings] if ratings != [] else None
            self.cursor.execute("SELECT group_id "
                                "FROM groups "
                                "INNER JOIN user_group ON group_id = u_g_group_id "
                                "INNER JOIN users ON u_g_user_id = user_id "
                                "WHERE user_id = ? "
                                "AND group_id = ?;",
                                (user_id, group_id))
            member = self.cursor.fetchall()
            self.cursor.execute("SELECT u_r_g_rating "
                                "FROM user_rating_group "
                                "INNER JOIN groups ON group_id = u_r_g_group_id "
                                "INNER JOIN users ON u_r_g_user_id = user_id "
                                "WHERE user_id = ?"
                                "AND group_id = ?;",
                                (user_id, group_id))
            vote = self.cursor.fetchall()
            self.cursor.execute("SELECT u_c_g_comment "
                                "FROM user_comment_group "
                                "INNER JOIN groups ON group_id = u_c_g_group_id "
                                "INNER JOIN users ON u_c_g_user_id = user_id "
                                "WHERE user_id = ?"
                                "AND group_id = ?;",
                                (user_id, group_id))
            comment = self.cursor.fetchall()
            self.close_connection()
            return {"error": '',
                    "id": list(group)[0],
                    "name": list(group)[1],
                    "picUrl": list(group)[2],
                    "url": list(group)[3],
                    "phone": list(group)[4],
                    "verified": False if list(group)[5] == 0 else True,
                    "rating": statistics.mean(ratings) if ratings is not None else 0.0,
                    "votes": len(ratings) if ratings is not None else 0,
                    "opening": list(group)[6],
                    "facebook": list(group)[7],
                    "google": list(group)[8],
                    "about": list(group)[9],
                    "address": list(group)[10],
                    "city": list(group)[11],
                    "country": list(group)[12],
                    "latitude": list(group)[13],
                    "longitude": list(group)[14],
                    "isMember": True if member != [] else False,
                    "hasVoted": vote[0][0] if vote != [] else 0,
                    "comment": comment[0][0] if comment != [] else None
                    }
        self.close_connection()
        return {"error": 'Wrong User',
                "id": None,
                "name": None,
                "picUrl": None,
                "url": None,
                "phone": None,
                "verified": None,
                "rating": None,
                "votes": None,
                "opening": None,
                "facebook": None,
                "google": None,
                "about": None,
                "address": None,
                "city": None,
                "country": None,
                "latitude": None,
                "longitude": None,
                "isMember": None,
                "hasVoted": None,
                "comment": None
                }

    # APPoeira Function: Group detail information. Called when /group-detail-more invoked
    def group_detail_more(self, group_id):
        self.open_connection()
        self.cursor.execute("SELECT user_id, "
                            "user_apelhido, "
                            "user_pic_url, "
                            "user_premium, "
                            "rank_name, "
                            "group_role_name "
                            "FROM groups "
                            "INNER JOIN users INNER JOIN ranks ON user_rank_id = rank_id "
                            "INNER JOIN user_group ON u_g_user_id = user_id "
                            "INNER JOIN grouproles ON u_g_role_id = group_role_id "
                            "WHERE u_g_group_id = ? AND "
                            "group_id = ?;", (group_id, group_id))
        details = self.cursor.fetchall()
        if details is not None:
            details = list(details)
            self.close_connection()
            return [{'groupSchool': None,
                     'userId': list(detail)[0],
                     'userApelhido': list(detail)[1],
                     'userPicUrl': list(detail)[2],
                     'userPremium': False if list(detail)[3] == 0 else True,
                     'userRank': list(detail)[4],
                     'userGroupRole': list(detail)[5],
                     } for detail in details]
        self.close_connection()
        return None

    # APPoeira Function: Group detail information. Called when /group-comments invoked
    def group_comments(self, group_id):
        self.open_connection()
        self.cursor.execute("SELECT u_c_g_comment, "
                            "u_c_g_date, "
                            "u_c_g_user_id, "
                            "user_apelhido, "
                            "user_pic_url "
                            "FROM user_comment_group "
                            "INNER JOIN groups ON group_id = u_c_g_group_id "
                            "INNER JOIN users ON user_id = u_c_g_user_id "
                            "WHERE group_id = ?;",
                            (group_id,))
        comments = self.cursor.fetchall()
        if comments is not None:
            comments = list(comments)
            self.close_connection()
            return [{'userId': list(comment)[2],
                     'picUrl': list(comment)[4],
                     'userApelhido': list(comment)[3],
                     'comment': list(comment)[0],
                     'date': list(comment)[1],
                     } for comment in comments]
        self.close_connection()
        return None

    # APPoeira Function: new comment on a group. Called when /new-comment invoked
    def new_comment_group(self, group_id, user_id, comment):
        self.open_connection()
        response = self.cursor.execute("INSERT INTO user_comment_group ("
                                       "u_c_g_user_id, "
                                       "u_c_g_group_id, "
                                       "u_c_g_comment, "
                                       "u_c_g_date"
                                       ")"
                                       "VALUES (?,?,?,?);",
                                       (user_id, group_id, comment, datetime.utcnow()))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: follow user. Called when /user-follow invoked
    def user_follow(self, my_id, user_id):
        self.open_connection()
        response = self.cursor.execute("INSERT INTO user_follows_user ("
                                       "u_f_u_user_id, "
                                       "u_f_u_followed_id, "
                                       "u_f_u_date "
                                       ")"
                                       "VALUES (?,?,?);",
                                       (my_id, user_id, datetime.utcnow()))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: unfollow user. Called when /user-unfollow invoked
    def user_unfollow(self, my_id, user_id):
        self.open_connection()
        response = self.cursor.execute("DELETE FROM user_follows_user "
                                       "WHERE u_f_u_user_id = ? "
                                       "AND u_f_u_followed_id = ?;",
                                       (my_id, user_id))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: join group. Called when /join-group invoked
    def join_group(self, group_id, user_id, role_id):
        self.open_connection()
        response = self.cursor.execute("INSERT INTO user_group ("
                                       "u_g_user_id, "
                                       "u_g_group_id, "
                                       "u_g_role_id, "
                                       "u_g_date, "
                                       "u_g_accepted"
                                       ")"
                                       "VALUES (?,?,?,?,?);",
                                       (user_id, group_id, role_id, datetime.utcnow(), True))
        if response.rowcount > 0:
            self.cursor.execute("UPDATE groups SET "
                                "group_verified = 1 "
                                "WHERE group_id = ?;",
                                (group_id,))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: leave group. Called when /leave-group invoked
    def leave_group(self, group_id, user_id):
        self.open_connection()
        response = self.cursor.execute("DELETE FROM user_group "
                                       "WHERE u_g_user_id = ? "
                                       "AND u_g_group_id = ?;",
                                       (user_id, group_id))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: User detail information. Called when /user-detail invoked
    def user_detail(self, user_id):
        self.open_connection()
        self.cursor.execute("SELECT user_apelhido, "
                            "user_pic_url, "
                            "user_date_join, "
                            "user_premium, "
                            "rank_name, "
                            "school_name, "
                            "user_email, "
                            "user_first_name, "
                            "user_last_name "
                            "FROM users "
                            "INNER JOIN ranks ON user_rank_id = rank_id "
                            "INNER JOIN schools ON user_school_id = school_id "
                            "WHERE user_id = ?;",
                            (user_id,))
        user_info = self.cursor.fetchone()
        if user_info is not None:
            self.cursor.execute("SELECT group_id,"
                                "group_name,"
                                "group_picture_url, "
                                "group_role_name, "
                                "u_g_date, "
                                "u_g_accepted "
                                "FROM groups "
                                "INNER JOIN users ON u_g_user_id = ? "
                                "INNER JOIN user_group ON group_id = u_g_group_id "
                                "INNER JOIN grouproles ON u_g_role_id = group_role_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            groups = self.cursor.fetchall()
            self.cursor.execute("SELECT group_id, "
                                "group_name, "
                                "group_picture_url, "
                                "u_r_g_rating, "
                                "u_r_g_date "
                                "FROM groups "
                                "INNER JOIN users ON u_r_g_user_id = ? "
                                "INNER JOIN user_rating_group ON group_id = u_r_g_group_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            group_votes = self.cursor.fetchall()
            self.cursor.execute("SELECT group_id, "
                                "group_name, "
                                "group_picture_url, "
                                "u_c_g_comment, "
                                "u_c_g_date "
                                "FROM groups "
                                "INNER JOIN users ON u_c_g_user_id = ? "
                                "INNER JOIN user_comment_group ON group_id = u_c_g_group_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            group_comments = self.cursor.fetchall()
            self.cursor.execute("SELECT roda_id,"
                                "roda_name,"
                                "roda_pic_url, "
                                "roda_role_name, "
                                "u_r_date, "
                                "u_r_accepted "
                                "FROM rodas "
                                "INNER JOIN users ON u_r_user_id = ? "
                                "INNER JOIN user_roda ON roda_id = u_r_roda_id "
                                "INNER JOIN rodaroles ON u_r_role_id = roda_role_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            rodas = self.cursor.fetchall()
            self.cursor.execute("SELECT roda_id, "
                                "roda_name, "
                                "roda_pic_url, "
                                "u_r_r_rating, "
                                "u_r_r_date "
                                "FROM rodas "
                                "INNER JOIN users ON u_r_r_user_id = ? "
                                "INNER JOIN user_rating_roda ON roda_id = u_r_r_roda_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            roda_votes = self.cursor.fetchall()
            self.cursor.execute("SELECT roda_id, "
                                "roda_name, "
                                "roda_pic_url, "
                                "u_c_r_comment, "
                                "u_c_r_date "
                                "FROM rodas "
                                "INNER JOIN users ON u_c_r_user_id = ? "
                                "INNER JOIN user_comment_roda ON roda_id = u_c_r_roda_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            roda_comments = self.cursor.fetchall()
            self.cursor.execute("SELECT event_id,"
                                "event_name,"
                                "event_pic_url, "
                                "event_role_name, "
                                "u_e_date, "
                                "u_e_accepted "
                                "FROM events "
                                "INNER JOIN users ON u_e_user_id = ? "
                                "INNER JOIN user_event ON event_id = u_e_event_id "
                                "INNER JOIN eventroles ON u_e_role_id = event_role_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            events = self.cursor.fetchall()
            self.cursor.execute("SELECT event_id, "
                                "event_name, "
                                "event_pic_url, "
                                "u_r_e_rating, "
                                "u_r_e_date "
                                "FROM events "
                                "INNER JOIN users ON u_r_e_user_id = ? "
                                "INNER JOIN user_rating_event ON event_id = u_r_e_event_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            event_votes = self.cursor.fetchall()
            self.cursor.execute("SELECT event_id, "
                                "event_name, "
                                "event_pic_url, "
                                "u_c_e_comment, "
                                "u_c_e_date "
                                "FROM events "
                                "INNER JOIN users ON u_c_e_user_id = ? "
                                "INNER JOIN user_comment_event ON event_id = u_c_e_event_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            event_comments = self.cursor.fetchall()
            self.cursor.execute("SELECT online_id,"
                                "online_name,"
                                "online_pic_url, "
                                "online_role_name, "
                                "u_o_date, "
                                "u_o_accepted "
                                "FROM onlines "
                                "INNER JOIN users ON u_o_user_id = ? "
                                "INNER JOIN user_online ON online_id = u_o_online_id "
                                "INNER JOIN onlineroles ON u_o_role_id = online_role_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            onlines = self.cursor.fetchall()
            self.cursor.execute("SELECT online_id, "
                                "online_name, "
                                "online_pic_url, "
                                "u_r_o_rating, "
                                "u_r_o_date "
                                "FROM onlines "
                                "INNER JOIN users ON u_r_o_user_id = ? "
                                "INNER JOIN user_rating_online ON online_id = u_r_o_online_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            online_votes = self.cursor.fetchall()
            self.cursor.execute("SELECT online_id, "
                                "online_name, "
                                "online_pic_url, "
                                "u_c_o_comment, "
                                "u_c_o_date "
                                "FROM onlines "
                                "INNER JOIN users ON u_c_o_user_id = ? "
                                "INNER JOIN user_comment_online ON online_id = u_c_o_online_id "
                                "WHERE user_id = ?;",
                                (user_id, user_id))
            online_comments = self.cursor.fetchall()
            self.cursor.execute("SELECT user_id, "
                                "user_apelhido, "
                                "user_pic_url, "
                                "u_f_u_date "
                                "FROM users "
                                "INNER JOIN user_follows_user ON u_f_u_user_id = user_id "
                                "WHERE u_f_u_followed_id = ?;",
                                (user_id,))
            followers = self.cursor.fetchall()
            self.cursor.execute("SELECT user_id, "
                                "user_apelhido, "
                                "user_pic_url, "
                                "u_f_u_date "
                                "FROM users "
                                "INNER JOIN user_follows_user ON u_f_u_followed_id = user_id "
                                "WHERE u_f_u_user_id = ?;",
                                (user_id,))
            followeds = self.cursor.fetchall()
            self.close_connection()
            return {'apelhido': list(user_info)[0],
                    'email': list(user_info)[6],
                    'name': list(user_info)[7],
                    'lastName': list(user_info)[8],
                    'picUrl': list(user_info)[1],
                    'joined': list(user_info)[2],
                    'premium': True if list(user_info)[3] == 1 else False,
                    'rank': list(user_info)[4],
                    'school': list(user_info)[5],
                    'followers': [{
                        'userId': list(follower)[0],
                        'userApelhido': list(follower)[1],
                        'userPicUrl': list(follower)[2],
                        'userDate': list(follower)[3].split(' ')[0] if list(follower)[3] is not None else "",
                    } for follower in followers] if followers != [] else [{
                        'userId': None,
                        'userApelhido': None,
                        'userPicUrl': None,
                        'userDate': None
                    }],
                    'followed': [{
                        'userId': list(followed)[0],
                        'userApelhido': list(followed)[1],
                        'userPicUrl': list(followed)[2],
                        'userDate': list(followed)[3].split(' ')[0] if list(followed)[3] is not None else "",
                    } for followed in followeds] if followeds != [] else [{
                        'userId': None,
                        'userApelhido': None,
                        'userPicUrl': None,
                        'userDate': None
                    }],
                    'groups': [{
                        'groupId': list(group)[0],
                        'groupName': list(group)[1],
                        'groupPicUrl': list(group)[2],
                        'groupRole': list(group)[3],
                        'groupDate': list(group)[4].split(' ')[0] if list(group)[4] is not None else "",
                        'groupAccepted': list(group)[5]
                    } for group in groups] if groups != [] else [{
                        'groupId': None,
                        'groupName': None,
                        'groupPicUrl': None,
                        'groupRole': None,
                        'groupDate': None
                    }],
                    'groupVotes': [{
                        'groupId': list(group_vote)[0],
                        'groupName': list(group_vote)[1],
                        'groupPicUrl': list(group_vote)[2],
                        'groupRating': list(group_vote)[3],
                        'groupDate': list(group_vote)[4].split(' ')[0] if list(group_vote)[4] is not None else ""
                    } for group_vote in group_votes] if group_votes != [] else [{
                        'groupId': None,
                        'groupName': None,
                        'groupPicUrl': None,
                        'groupRating': None,
                        'groupDate': None
                    }],
                    'groupComments': [{
                        'groupId': list(group_comment)[0],
                        'groupName': list(group_comment)[1],
                        'groupPicUrl': list(group_comment)[2],
                        'groupComment': list(group_comment)[3],
                        'groupDate': list(group_comment)[4].split(' ')[0] if list(group_comment)[4] is not None else ""
                    } for group_comment in group_comments] if group_comments != [] else [{
                        'groupId': None,
                        'groupName': None,
                        'groupPicUrl': None,
                        'groupComment': None,
                        'groupDate': None
                    }],
                    'events': [{
                        'eventId': list(event)[0],
                        'eventName': list(event)[1],
                        'eventPicUrl': list(event)[2],
                        'eventRole': list(event)[3],
                        'eventDate': list(event)[4].split(' ')[0] if list(event)[4] is not None else "",
                        'eventAccepted': list(event)[5]
                    } for event in events] if events != [] else [{
                        'eventId': None,
                        'eventName': None,
                        'eventPicUrl': None,
                        'eventRole': None,
                        'eventDate': None
                    }],
                    'eventVotes': [{
                        'eventId': list(event_vote)[0],
                        'eventName': list(event_vote)[1],
                        'eventPicUrl': list(event_vote)[2],
                        'eventRating': list(event_vote)[3],
                        'eventDate': list(event_vote)[4].split(' ')[0] if list(event_vote)[4] is not None else ""
                    } for event_vote in event_votes] if event_votes != [] else [{
                        'eventId': None,
                        'eventName': None,
                        'eventPicUrl': None,
                        'eventRating': None,
                        'eventDate': None
                    }],
                    'eventComments': [{
                        'eventId': list(event_comment)[0],
                        'eventName': list(event_comment)[1],
                        'eventPicUrl': list(event_comment)[2],
                        'eventComment': list(event_comment)[3],
                        'eventDate': list(event_comment)[4].split(' ')[0] if list(event_comment)[4] is not None else ""
                    } for event_comment in event_comments] if event_comments != [] else [{
                        'eventId': None,
                        'eventName': None,
                        'eventPicUrl': None,
                        'eventComment': None,
                        'eventDate': None
                    }],
                    'rodas': [{
                        'rodaId': list(roda)[0],
                        'rodaName': list(roda)[1],
                        'rodaPicUrl': list(roda)[2],
                        'rodaRole': list(roda)[3],
                        'rodaDate': list(roda)[4].split(' ')[0] if list(roda)[4] is not None else "",
                        'rodaAccepted': list(roda)[5]
                    } for roda in rodas] if rodas != [] else [{
                        'rodaId': None,
                        'rodaName': None,
                        'rodaPicUrl': None,
                        'rodaRole': None,
                        'rodaDate': None
                    }],
                    'rodaVotes': [{
                        'rodaId': list(roda_vote)[0],
                        'rodaName': list(roda_vote)[1],
                        'rodaPicUrl': list(roda_vote)[2],
                        'rodaVote': list(roda_vote)[3],
                        'rodaDate': list(roda_vote)[4].split(' ')[0] if list(roda_vote)[4] is not None else ""
                    } for roda_vote in roda_votes] if roda_votes != [] else [{
                        'rodaId': None,
                        'rodaName': None,
                        'rodaPicUrl': None,
                        'rodaVote': None,
                        'rodaDate': None
                    }],
                    'rodaComments': [{
                        'rodaId': list(roda_comment)[0],
                        'rodaName': list(roda_comment)[1],
                        'rodaPicUrl': list(roda_comment)[2],
                        'rodaComment': list(roda_comment)[3],
                        'rodaDate': list(roda_comment)[4].split(' ')[0] if list(roda_comment)[4] is not None else ""
                    } for roda_comment in roda_comments] if roda_comments != [] else [{
                        'rodaId': None,
                        'rodaName': None,
                        'rodaPicUrl': None,
                        'rodaComment': None,
                        'rodaDate': None
                    }],
                    'onlines': [{
                        'onlineId': list(online)[0],
                        'onlineName': list(online)[1],
                        'onlinePicUrl': list(online)[2],
                        'onlineRole': list(online)[3],
                        'onlineDate': list(online)[4].split(' ')[0] if list(online)[4] is not None else "",
                        'onlineAccepted': list(online)[5]
                    } for online in onlines] if onlines != [] else [{
                        'onlineId': None,
                        'onlineName': None,
                        'onlinePicUrl': None,
                        'onlineRole': None,
                        'onlineDate': None
                    }],
                    'onlineVotes': [{
                        'onlineId': list(online_vote)[0],
                        'onlineName': list(online_vote)[1],
                        'onlinePicUrl': list(online_vote)[2],
                        'onlineVote': list(online_vote)[3],
                        'onlineDate': list(online_vote)[4].split(' ')[0] if list(online_vote)[4] is not None else ""
                    } for online_vote in online_votes] if online_votes != [] else [{
                        'onlineId': None,
                        'onlineName': None,
                        'onlinePicUrl': None,
                        'onlineVote': None,
                        'onlineDate': None
                    }],
                    'onlineComments': [{
                        'onlineId': list(online_comment)[0],
                        'onlineName': list(online_comment)[1],
                        'onlinePicUrl': list(online_comment)[2],
                        'onlineComment': list(online_comment)[3],
                        'onlineDate': list(online_comment)[4].split(' ')[0] if list(online_comment)[4] is not None else ""
                    } for online_comment in online_comments] if online_comments != [] else [{
                        'onlineId': None,
                        'onlineName': None,
                        'onlinePicUrl': None,
                        'onlineComment': None,
                        'onlineDate': None
                    }]
                    }
        self.close_connection()
        return {'apelhido': None,
                'email': None,
                'name': None,
                'lastName': None,
                'picUrl': None,
                'joined': None,
                'premium': False,
                'rank': None,
                'school': None,
                'followers': [{
                    'userId': None,
                    'userApelhido': None,
                    'userPicUrl': None,
                    'userDate': None
                }],
                'followed': [{
                    'userId': None,
                    'userApelhido': None,
                    'userPicUrl': None,
                    'userDate': None
                }],
                'groups': [{
                    'groupId': None,
                    'groupName': None,
                    'groupPicUrl': None,
                    'groupRole': None,
                    'groupDate': None,
                    'groupeAccepted': None
                }],
                'groupVotes': [{
                    'groupId': None,
                    'groupName': None,
                    'groupPicUrl': None,
                    'groupRating': None,
                    'groupDate': None
                }],
                'groupComments': [{
                    'groupId': None,
                    'groupName': None,
                    'groupPicUrl': None,
                    'groupComment': None,
                    'groupDate': None
                }],
                'events': [{
                    'eventId': None,
                    'eventName': None,
                    'eventPicUrl': None,
                    'eventRole': None,
                    'eventDate': None,
                    'eventAccepted': None
                }],
                'eventVotes': [{
                    'eventId': None,
                    'eventName': None,
                    'eventPicUrl': None,
                    'eventRating': None,
                    'eventDate': None
                }],
                'eventComments': [{
                    'eventId': None,
                    'eventName': None,
                    'eventPicUrl': None,
                    'eventComment': None,
                    'eventDate': None
                }],
                'rodas': [{
                    'rodaId': None,
                    'rodaName': None,
                    'rodaPicUrl': None,
                    'rodaRole': None,
                    'rodaDate': None,
                    'rodaAccepted': None
                }],
                'rodaVotes': [{
                    'rodaId': None,
                    'rodaName': None,
                    'rodaPicUrl': None,
                    'rodaVote': None,
                    'rodaDate': None
                }],
                'rodaComments': [{
                    'rodaId': None,
                    'rodaName': None,
                    'rodaPicUrl': None,
                    'rodaComment': None,
                    'rodaDate': None
                }],
                'onlines': [{
                    'onlineId': None,
                    'onlineName': None,
                    'onlinePicUrl': None,
                    'onlineRole': None,
                    'onlineDate': None,
                    'onlineAccepted': None
                }],
                'onlineVotes': [{
                    'onlineId': None,
                    'onlineName': None,
                    'onlinePicUrl': None,
                    'onlineVote': None,
                    'onlineDate': None
                }],
                'onlineComments': [{
                    'onlineId': None,
                    'onlineName': None,
                    'onlinePicUrl': None,
                    'onlineComment': None,
                    'onlineDate': None
                }]
                }

    # APPoeira Function: News check. Called when /are-there-news invoked
    def are_there_news(self, user_id):
        self.open_connection()
        self.cursor.execute("select u_g_user_id, 2 "
                            "from user_group "
                            "where u_g_user_id = ? and u_g_accepted = 0 "
                            "UNION ALL "
                            "select u_r_user_id, 3 "
                            "from user_roda "
                            "where u_r_user_id = ? and u_r_accepted = 0 "
                            "UNION ALL "
                            "select u_e_user_id, 4 "
                            "from user_event "
                            "where u_e_user_id = ? and u_e_accepted = 0 "
                            "UNION ALL "
                            "select u_o_user_id, 5 "
                            "from user_online "
                            "where u_o_user_id = ? and u_o_accepted = 0",
                            (user_id, user_id, user_id, user_id,))
        result = self.cursor.fetchall()
        return {'response': result != []}

    # APPoeira Function: Search on the database. Called when /search invoked
    def search(self, search, mode):
        users = []
        groups = []
        events = []
        rodas = []
        onlines = []
        if mode[0] == "1":
            self.open_connection()
            self.cursor.execute("SELECT user_id, "
                                "user_apelhido, "
                                "user_pic_url, "
                                "user_premium, "
                                "rank_name "
                                "FROM users "
                                "INNER JOIN ranks ON user_rank_id = rank_id "
                                "WHERE user_apelhido LIKE '%{}%';".format(search))
            result = self.cursor.fetchall()
            users = [{'id': list(user)[0],
                      'apelhido': list(user)[1],
                      'picUrl': list(user)[2],
                      'premium': True if list(user)[3] == 1 else False,
                      'rank': list(user)[4]
                      } for user in result]
            self.close_connection()
        if mode[1] == "1":
            self.open_connection()
            self.cursor.execute("SELECT "
                                "group_id, "
                                "group_name, "
                                "group_picture_url, "
                                "group_verified "
                                "FROM groups "
                                "WHERE group_name LIKE '%{}%';".format(search))
            results = self.cursor.fetchall()
            if results is not None:
                import statistics
                results = list(results)
                groups = []
                for result in results:
                    ratings = None
                    if list(result)[3] == 1:
                        self.cursor.execute("SELECT u_r_g_rating FROM user_rating_group WHERE u_r_g_group_id = ?",
                                            (list(result)[0],))
                        ratings = list(self.cursor.fetchall())
                        ratings = [rating[0] for rating in ratings] if ratings != [] else None
                    groups.append({"id": list(result)[0],
                                   "name": list(result)[1],
                                   "picUrl": list(result)[2],
                                   "verified": False if list(result)[3] == 0 else True,
                                   "rating": statistics.mean(ratings) if ratings is not None else 0.0,
                                  })
            self.close_connection()
        if mode[2] == "1":
            self.open_connection()
            self.cursor.execute("SELECT roda_id, "
                                "roda_name, "
                                "roda_pic_url, "
                                "roda_verified "
                                "FROM rodas "
                                "WHERE roda_name LIKE '%{}%';".format(search))
            result = self.cursor.fetchall()
            if result is not None:
                rodas = []
                result = list(result)
                for roda in result:
                    self.cursor.execute("SELECT "
                                        "user_apelhido, "
                                        "rank_name "
                                        "FROM users "
                                        "INNER JOIN ranks ON user_rank_id = rank_id "
                                        "INNER JOIN user_roda ON u_r_user_id = user_id AND u_r_role_id = 1 "
                                        "INNER JOIN rodas ON roda_id = ?;",
                                        (list(roda)[0],))
                    owner = self.cursor.fetchone()
                    rodas.append({"id": list(roda)[0],
                                   "name": list(roda)[1],
                                   "picUrl": list(roda)[2],
                                   "verified": False if list(roda)[3] == 0 else True,
                                   'owner': list(owner)[0],
                                   'ownerRank': list(owner)[1],
                                   })
            self.close_connection()
        if mode[3] == "1":
            self.open_connection()
            self.cursor.execute("SELECT "
                                "event_id, "
                                "event_name, "
                                "event_pic_url, "
                                "event_verified "
                                "FROM events "
                                "WHERE event_name LIKE '%{}%';".format(search))
            result = self.cursor.fetchall()
            if result is not None:
                events = []
                result = list(result)
                for event in result:
                    self.cursor.execute("SELECT "
                                        "user_apelhido, "
                                        "rank_name "
                                        "FROM users "
                                        "INNER JOIN ranks ON user_rank_id = rank_id "
                                        "INNER JOIN user_event ON u_e_user_id = user_id AND u_e_role_id = 1 "
                                        "INNER JOIN events ON event_id = ?;",
                                        (list(event)[0],))
                    owner = self.cursor.fetchone()
                    events.append({"id": list(event)[0],
                                   "name": list(event)[1],
                                   "picUrl": list(event)[2],
                                   "verified": False if list(event)[3] == 0 else True,
                                   'owner': list(owner)[0],
                                   'ownerRank': list(owner)[1]
                                   })
            self.close_connection()
        if mode[4] == "1":
            self.open_connection()
            self.cursor.execute("SELECT "
                                "online_id, "
                                "online_name, "
                                "online_pic_url, "
                                "online_verified "
                                "FROM onlines "
                                "WHERE online_name LIKE '%{}%';".format(search))
            result = self.cursor.fetchall()
            if result is not None:
                onlines = []
                result = list(result)
                for online in result:
                    self.cursor.execute("SELECT "
                                        "user_apelhido, "
                                        "rank_name "
                                        "FROM users "
                                        "INNER JOIN ranks ON user_rank_id = rank_id "
                                        "INNER JOIN user_online ON u_o_user_id = user_id AND u_o_role_id = 1 "
                                        "INNER JOIN onlines ON online_id = ?;",
                                        (list(online)[0],))
                    owner = self.cursor.fetchone()
                    onlines.append({"id": list(online)[0],
                                    "name": list(online)[1],
                                    "picUrl": list(online)[2],
                                    "verified": False if list(online)[3] == 0 else True,
                                    'owner': list(owner)[0],
                                    'ownerRank': list(owner)[1]
                                   })
            self.close_connection()
        return {"num": 0,
                "userResponses": users,
                "groupResponses": groups,
                "rodaResponses": rodas,
                "eventResponses": events,
                "onlineResponses": onlines
                }

    # APPoeira Function: User rated a group. Called when /user-rated-group invoked
    def user_rated_group(self, user_id, group_id, stars):
        self.open_connection()
        self.cursor.execute("SELECT u_r_g_rating "
                            "FROM user_rating_group "
                            "WHERE u_r_g_user_id = ? "
                            "AND u_r_g_group_id = ?",
                            (user_id, group_id))
        rating = self.cursor.fetchone()
        if rating is None:
            import statistics
            self.cursor.execute("INSERT INTO user_rating_group ("
                                "u_r_g_user_id, "
                                "u_r_g_group_id, "
                                "u_r_g_rating, "
                                "u_r_g_date"
                                ")"
                                "VALUES (?,?,?,?);",
                                (user_id, group_id, stars, datetime.utcnow()))
            self.connection.commit()
            self.cursor.execute("UPDATE groups SET "
                                "group_verified = 1 "
                                "WHERE group_id = ?;",
                                (group_id,))
            self.connection.commit()
            self.cursor.execute("SELECT u_r_g_rating FROM user_rating_group WHERE u_r_g_group_id = ?",
                                (group_id,))
            ratings = list(self.cursor.fetchall())
            ratings = [rating[0] for rating in ratings] if ratings != [] else None
            self.close_connection()
            return {'ok': True,
                    'stars': stars,
                    'ratings': statistics.mean(ratings) if ratings is not None else 0.0
                    }
        else:
            self.close_connection()
            return {'ok': False,
                    'stars': rating[0],
                    'ratings': 0
                    }

    # APPoeira Function: Profile updated. Called when /user-profile-updated
    def user_update_profile(self, user_id, name, last_name, apelhido, email, password, new_password, rank):
        crypt = hashlib.new('sha256')
        crypt.update(password.encode())
        self.open_connection()
        self.cursor.execute("SELECT user_pic_url, "
                            "user_apelhido, "
                            "user_first_name, "
                            "user_last_name, "
                            "user_password, "
                            "user_id, "
                            "user_email, "
                            "user_rank_id "
                            "FROM users "
                            "WHERE user_id = ?;",
                            (user_id,))
        user = self.cursor.fetchone()
        error = 0b1111111111
        if user is not None:
            user = list(user)
            error = error - 0b0000000001 if name == user[2] or name == '' else error
            error = error - 0b0000000010 if last_name == user[3] or last_name == '' else error
            error = error - 0b0000000100 if apelhido == user[1] or apelhido == '' else error
            error = error - 0b0000001000 if email == user[6] or email == '' else error
            error = error - 0b0000010000 if password == '' else error
            error = error - 0b0000100000 if new_password == '' else error
            error = error - 0b0001000000 if rank == 0 or rank == user[7] else error
            if crypt.hexdigest() == user[4]:
                crypt = hashlib.new('sha256')
                crypt.update(new_password.encode())
                self.cursor.execute("UPDATE users SET "
                                    "user_password = ?, "
                                    "user_email = ?, "
                                    "user_first_name = ?, "
                                    "user_last_name = ?, "
                                    "user_apelhido = ?, "
                                    "user_rank_id = ? "
                                    "WHERE user_id = ?",
                                    (crypt.hexdigest(),
                                     email if email != user[6] and email != '' else user[6],
                                     name if name != user[2] and name != '' else user[2],
                                     last_name if last_name != user[3] and last_name != '' else user[3],
                                     apelhido if apelhido != user[1] and apelhido != '' else user[1],
                                     rank if rank != user[7] and rank > 0 else user[7], user[5]))
                self.close_connection()
                return {
                        'apelhido': apelhido if apelhido != user[1] and apelhido != '' else user[1],
                        'email': email if email != user[6] and email != '' else user[6],
                        'token': '',
                        'name': name if name != user[2] and name != '' else user[2],
                        'lastName': last_name if last_name != user[3] and last_name != '' else user[3],
                        'rank': rank if rank != user[7] and rank > 0 else user[7],
                        'error': error
                        }
            else:
                error = error - 0b0100000000
                self.cursor.execute("UPDATE users SET "
                                    "user_email = ?, "
                                    "user_first_name = ?, "
                                    "user_last_name = ?, "
                                    "user_apelhido = ?, "
                                    "user_rank_id = ? "
                                    "WHERE user_id = ?",
                                    (email if email != user[6] and email != '' else user[6],
                                     name if name != user[2] and name != '' else user[2],
                                     last_name if last_name != user[3] and last_name != '' else user[3],
                                     apelhido if apelhido != user[1] and apelhido != '' else user[1],
                                     rank if rank != user[7] and rank > 0 else user[7], user[5]))
                self.close_connection()
                return {
                        'apelhido': apelhido if apelhido != user[1] and apelhido != '' else user[1],
                        'email': email if email != user[6] and email != '' else user[6],
                        'token': '',
                        'name': name if name != user[2] and name != '' else user[2],
                        'lastName': last_name if last_name != user[3] and last_name != '' else user[3],
                        'rank': rank if rank != user[7] and rank > 0 else user[7],
                        'error': error
                        }
        error = error - 0b1000000000
        self.close_connection()
        return {
                'apelhido': None,
                'email': None,
                'token': '',
                'name': None,
                'lastName': None,
                'rank': None,
                'error': error
                }

    # APPoeira Function: Picture updated. Called when /upload-picture
    def upload_picture(self, url, ok, key):
        occurrences = [i for i, a in enumerate(key) if a == "_"]
        object_type = key[:occurrences[0]]
        object_subtype = key[occurrences[0] + 1:occurrences[1]]
        type_id = key[occurrences[1] + 1:occurrences[2]]
        subtype_id = key[occurrences[2] + 1:occurrences[3]]
        self.open_connection()
        response = self.cursor.execute("UPDATE {}s SET "
                                       "{}_pic_url = ? "
                                       "WHERE {}_id = ?;".format(object_type, object_type, object_type),
                                       (url, type_id))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 and ok else False,
                'picUrl': url}

    # APPoeira Function: Roda detail information. Called when /roda-detail-more invoked
    def roda_detail_more(self, roda_id):
        self.open_connection()
        self.cursor.execute("SELECT user_id, "
                            "user_apelhido, "
                            "user_pic_url, "
                            "user_premium, "
                            "rank_name, "
                            "roda_role_name "
                            "FROM rodas "
                            "INNER JOIN users INNER JOIN ranks ON user_rank_id = rank_id "
                            "INNER JOIN user_roda ON u_r_user_id = user_id "
                            "INNER JOIN rodaroles ON u_r_role_id = roda_role_id "
                            "WHERE u_r_roda_id = ? AND "
                            "roda_id = ?;", (roda_id, roda_id))
        details = self.cursor.fetchall()
        if details is not None:
            details = list(details)
            self.close_connection()
            return [{'groupSchool': None,
                     'userId': list(detail)[0],
                     'userApelhido': list(detail)[1],
                     'userPicUrl': list(detail)[2],
                     'userPremium': False if list(detail)[3] == 0 else True,
                     'userRank': list(detail)[4],
                     'userGroupRole': list(detail)[5],
                     } for detail in details]
        self.close_connection()
        return None

    # APPoeira Function: Roda detail information. Called when /roda-comments invoked
    def roda_comments(self, roda_id):
        self.open_connection()
        self.cursor.execute("SELECT u_c_r_comment, "
                            "u_c_r_date, "
                            "u_c_r_user_id, "
                            "user_apelhido, "
                            "user_pic_url "
                            "FROM user_comment_roda "
                            "INNER JOIN rodas ON roda_id = u_c_r_roda_id "
                            "INNER JOIN users ON user_id = u_c_r_user_id "
                            "WHERE roda_id = ?;",
                            (roda_id,))
        comments = self.cursor.fetchall()
        if comments is not None:
            comments = list(comments)
            self.close_connection()
            return [{'userId': list(comment)[2],
                     'picUrl': list(comment)[4],
                     'userApelhido': list(comment)[3],
                     'comment': list(comment)[0],
                     'date': list(comment)[1],
                     } for comment in comments]
        self.close_connection()
        return None

    # APPoeira Function: new comment on a roda. Called when /new-comment invoked
    def new_comment_roda(self, roda_id, user_id, comment):
        self.open_connection()
        response = self.cursor.execute("INSERT INTO user_comment_roda ("
                                       "u_c_r_user_id, "
                                       "u_c_r_roda_id, "
                                       "u_c_r_comment, "
                                       "u_c_r_date"
                                       ")"
                                       "VALUES (?,?,?,?);",
                                       (user_id, roda_id, comment, datetime.utcnow()))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: User rated a roda. Called when /user-rated-roda invoked
    def user_rated_roda(self, user_id, roda_id, stars):
        self.open_connection()
        self.cursor.execute("SELECT u_r_r_rating "
                            "FROM user_rating_roda "
                            "WHERE u_r_r_user_id = ? "
                            "AND u_r_r_roda_id = ?",
                            (user_id, roda_id))
        rating = self.cursor.fetchone()
        if rating is None:
            self.cursor.execute("INSERT INTO user_rating_roda ("
                                "u_r_r_user_id, "
                                "u_r_r_roda_id, "
                                "u_r_r_rating, "
                                "u_r_r_date"
                                ")"
                                "VALUES (?,?,?,?);",
                                (user_id, roda_id, stars, datetime.utcnow()))
            self.connection.commit()
            self.cursor.execute("UPDATE rodas SET "
                                "roda_verified = 1 "
                                "WHERE roda_id = ?;",
                                (roda_id,))
            self.connection.commit()
            self.close_connection()
            return {'ok': True,
                    'stars': stars
                    }
        else:
            self.close_connection()
            return {'ok': False,
                    'stars': rating[0]
                    }

    # APPoeira Function: join roda. Called when /join-roda invoked
    def join_roda(self, roda_id, user_id, role_id):
        self.open_connection()
        response = self.cursor.execute("INSERT INTO user_roda ("
                                       "u_r_user_id, "
                                       "u_r_roda_id, "
                                       "u_r_role_id, "
                                       "u_r_date, "
                                       "u_r_accepted"
                                       ")"
                                       "VALUES (?,?,?,?,?);",
                                       (user_id, roda_id, role_id, datetime.utcnow(), True))
        if response.rowcount > 0:
            self.cursor.execute("UPDATE rodas SET "
                                "roda_verified = 1 "
                                "WHERE roda_id = ?;",
                                (roda_id,))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: leave roda. Called when /leave-roda invoked
    def leave_roda(self, roda_id, user_id):
        self.open_connection()
        response = self.cursor.execute("DELETE FROM user_roda "
                                       "WHERE u_r_user_id = ? "
                                       "AND u_r_roda_id = ?;",
                                       (user_id, roda_id))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: Event detail information. Called when /event-detail-more invoked
    def event_detail_more(self, event_id):
        self.open_connection()
        self.cursor.execute("SELECT user_id, "
                            "user_apelhido, "
                            "user_pic_url, "
                            "user_premium, "
                            "rank_name, "
                            "event_role_name "
                            "FROM events "
                            "INNER JOIN users INNER JOIN ranks ON user_rank_id = rank_id "
                            "INNER JOIN user_event ON u_e_user_id = user_id "
                            "INNER JOIN eventroles ON u_e_role_id = event_role_id "
                            "WHERE u_e_event_id = ? AND "
                            "event_id = ?;", (event_id, event_id))
        details = self.cursor.fetchall()
        if details is not None:
            details = list(details)
            self.close_connection()
            return [{'eventSchool': None,
                     'userId': list(detail)[0],
                     'userApelhido': list(detail)[1],
                     'userPicUrl': list(detail)[2],
                     'userPremium': False if list(detail)[3] == 0 else True,
                     'userRank': list(detail)[4],
                     'userGroupRole': list(detail)[5],
                     } for detail in details]
        self.close_connection()
        return None

    # APPoeira Function: Event detail information. Called when /event-comments invoked
    def event_comments(self, event_id):
        self.open_connection()
        self.cursor.execute("SELECT u_c_e_comment, "
                            "u_c_e_date, "
                            "u_c_e_user_id, "
                            "user_apelhido, "
                            "user_pic_url "
                            "FROM user_comment_event "
                            "INNER JOIN events ON event_id = u_c_e_event_id "
                            "INNER JOIN users ON user_id = u_c_e_user_id "
                            "WHERE event_id = ?;",
                            (event_id,))
        comments = self.cursor.fetchall()
        if comments is not None:
            comments = list(comments)
            self.close_connection()
            return [{'userId': list(comment)[2],
                     'picUrl': list(comment)[4],
                     'userApelhido': list(comment)[3],
                     'comment': list(comment)[0],
                     'date': list(comment)[1],
                     } for comment in comments]
        self.close_connection()
        return None

    # APPoeira Function: new comment on a event. Called when /new-comment invoked
    def new_comment_event(self, event_id, user_id, comment):
        self.open_connection()
        response = self.cursor.execute("INSERT INTO user_comment_event ("
                                       "u_c_e_user_id, "
                                       "u_c_e_event_id, "
                                       "u_c_e_comment, "
                                       "u_c_e_date"
                                       ")"
                                       "VALUES (?,?,?,?);",
                                       (user_id, event_id, comment, datetime.utcnow()))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: User rated a event. Called when /user-rated-event invoked
    def user_rated_event(self, user_id, event_id, stars):
        self.open_connection()
        self.cursor.execute("SELECT u_r_e_rating "
                            "FROM user_rating_event "
                            "WHERE u_r_e_user_id = ? "
                            "AND u_r_e_event_id = ?",
                            (user_id, event_id))
        rating = self.cursor.fetchone()
        if rating is None:
            self.cursor.execute("INSERT INTO user_rating_event ("
                                "u_r_e_user_id, "
                                "u_r_e_event_id, "
                                "u_r_e_rating, "
                                "u_r_e_date"
                                ")"
                                "VALUES (?,?,?,?);",
                                (user_id, event_id, stars, datetime.utcnow()))
            self.connection.commit()
            self.cursor.execute("UPDATE events SET "
                                "event_verified = 1 "
                                "WHERE event_id = ?;",
                                (event_id,))
            self.connection.commit()
            self.close_connection()
            return {'ok': True,
                    'stars': stars
                    }
        else:
            self.close_connection()
            return {'ok': False,
                    'stars': rating[0]
                    }

    # APPoeira Function: join event. Called when /join-event invoked
    def join_event(self, event_id, user_id, role_id):
        self.open_connection()
        response = self.cursor.execute("INSERT INTO user_event ("
                                       "u_e_user_id, "
                                       "u_e_event_id, "
                                       "u_e_role_id, "
                                       "u_e_date, "
                                       "u_e_accepted"
                                       ")"
                                       "VALUES (?,?,?,?,?);",
                                       (user_id, event_id, role_id, datetime.utcnow(), True))
        if response.rowcount > 0:
            self.cursor.execute("UPDATE events SET "
                                "event_verified = 1 "
                                "WHERE event_id = ?;",
                                (event_id,))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: leave event. Called when /leave-event invoked
    def leave_event(self, event_id, user_id):
        self.open_connection()
        response = self.cursor.execute("DELETE FROM user_event "
                                       "WHERE u_e_user_id = ? "
                                       "AND u_e_event_id = ?;",
                                       (user_id, event_id))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: Returns all onlines within a distance. Function called when /location-online invoked
    def online_get_based_on_location(self):
        self.open_connection()
        self.cursor.execute("SELECT "
                            "online_id, "
                            "online_name, "
                            "online_date, "
                            "online_pic_url, "
                            "online_verified "
                            "FROM onlines;")
        onlines = self.cursor.fetchall()
        if onlines is not None:
            import statistics
            result = []
            onlines = list(onlines)
            for online in onlines:
                ratings = None
                if list(online)[4] == 1:
                    self.cursor.execute("SELECT u_r_r_rating FROM user_rating_roda WHERE u_r_r_roda_id = ?",
                                        (list(online)[0],))
                    ratings = list(self.cursor.fetchall())
                    ratings = [rating[0] for rating in ratings] if ratings != [] else None
                self.cursor.execute("SELECT "
                                    "user_id, "
                                    "user_apelhido, "
                                    "rank_name "
                                    "FROM users "
                                    "INNER JOIN ranks ON user_rank_id = rank_id "
                                    "INNER JOIN user_online ON u_o_user_id = user_id AND u_o_role_id = 1 "
                                    "INNER JOIN onlines ON online_id = ?;",
                                    (list(online)[0],))
                owner = self.cursor.fetchone()
                self.cursor.execute("SELECT "
                                    "o_p_platform_id, "
                                    "o_p_key "
                                    "FROM online_platform "
                                    "INNER JOIN onlines ON o_p_online_id = online_id "
                                    "AND online_id = ?;",
                                    (list(online)[0],))
                platform = self.cursor.fetchone()
                result.append({"id": list(online)[0],
                               "name": list(online)[1],
                               "date": list(online)[2].split('-')[0] + '-' +
                                       list(online)[2].split('-')[1] + '-' +
                                       list(online)[2].split('-')[2] + ' ' +
                                       list(online)[2].split('-')[3] + ':' +
                                       list(online)[2].split('-')[4],
                               "picUrl": list(online)[3],
                               "verified": False if list(online)[4] == 0 else True,
                               'ownerApelhido': list(owner)[1],
                               'ownerRank': list(owner)[2],
                               'platform': list(platform)[0],
                               'key': list(platform)[1],
                               'rating': statistics.mean(ratings) if ratings is not None else 0.0
                               })
            result.sort(key=lambda s: -s['rating'])
            return result
        return [{"id": None,
                 "name": None,
                 "date": None,
                 "picUrl": None,
                 "verified": False,
                 'ownerApelhido': None,
                 'ownerRank': None,
                 'platform': 0,
                 'key': None,
                 'rating': None
                 }]

    # APPoeira Function: Returns online detail. Function called when /online-detail invoked
    def online_detail(self, online_id, user_id):
        self.open_connection()
        self.cursor.execute("SELECT online_id, "
                            "online_name, "
                            "online_pic_url, "
                            "online_description, "
                            "online_phone, "
                            "online_verified, "
                            "platform_name "
                            "FROM onlines "
                            "INNER JOIN online_platform ON online_id = o_p_online_id "
                            "INNER JOIN platforms ON platform_id = o_p_platform_id "
                            "WHERE online_id = ?;",
                            (online_id,))
        online = self.cursor.fetchone()
        if online is not None:
            import statistics
            online = list(online)
            ratings = None
            if list(online)[5] == 1:
                self.cursor.execute("SELECT u_r_o_rating FROM user_rating_online WHERE u_r_o_online_id = ?",
                                    (list(online)[0],))
                ratings = list(self.cursor.fetchall())
                ratings = [rating[0] for rating in ratings] if ratings != [] else None
            self.cursor.execute("SELECT user_id "
                                "FROM users "
                                "INNER JOIN user_online ON user_id = u_o_user_id "
                                "INNER JOIN onlines ON u_o_online_id = online_id "
                                "WHERE user_id = ? "
                                "AND online_id = ?;",
                                (user_id, online_id))
            member = self.cursor.fetchall()
            self.cursor.execute("SELECT u_r_o_rating "
                                "FROM user_rating_online "
                                "INNER JOIN onlines ON online_id = u_r_o_online_id "
                                "INNER JOIN users ON u_r_o_user_id = user_id "
                                "WHERE user_id = ?"
                                "AND online_id = ?;",
                                (user_id, online_id))
            vote = self.cursor.fetchall()
            self.cursor.execute("SELECT user_id "
                                "FROM users "
                                "INNER JOIN user_online ON user_id = u_o_user_id "
                                "INNER JOIN onlines ON u_o_online_id = online_id AND u_o_role_id = 1 "
                                "WHERE user_id = ? "
                                "AND online_id = ?;",
                                (user_id, online_id))
            owner = self.cursor.fetchall()
            self.close_connection()
            return {"error": '',
                    "id": list(online)[0],
                    "name": list(online)[1],
                    "picUrl": list(online)[2],
                    "description": list(online)[3],
                    "phone": list(online)[4],
                    "verified": False if list(online)[5] == 0 else True,
                    "rating": statistics.mean(ratings) if ratings is not None else 0.0,
                    "votes": len(ratings) if ratings is not None else 0,
                    "platform": list(online)[6],
                    "isMember": True if member != [] else False,
                    "hasVoted": vote[0][0] if vote != [] else 0,
                    "isOwner": True if owner != [] else False,
                    }
        self.close_connection()
        return {"error": 'Wrong User',
                "id": None,
                "name": None,
                "picUrl": None,
                "description": None,
                "phone": None,
                "verified": None,
                "rating": None,
                "votes": None,
                "platform": None,
                "isMember": None,
                "hasVoted": None,
                "isOwner": None
                }

    # APPoeira Function: Event detail information. Called when /online-detail-more invoked
    def online_detail_more(self, online_id):
        self.open_connection()
        self.cursor.execute("SELECT user_id, "
                            "user_apelhido, "
                            "user_pic_url, "
                            "user_premium, "
                            "rank_name, "
                            "online_role_name "
                            "FROM onlines "
                            "INNER JOIN users INNER JOIN ranks ON user_rank_id = rank_id "
                            "INNER JOIN user_online ON u_o_user_id = user_id "
                            "INNER JOIN onlineroles ON u_o_role_id = online_role_id "
                            "WHERE u_o_online_id = ? AND "
                            "online_id = ?;", (online_id, online_id))
        details = self.cursor.fetchall()
        if details is not None:
            details = list(details)
            self.close_connection()
            return [{'onlineSchool': None,
                     'userId': list(detail)[0],
                     'userApelhido': list(detail)[1],
                     'userPicUrl': list(detail)[2],
                     'userPremium': False if list(detail)[3] == 0 else True,
                     'userRank': list(detail)[4],
                     'userGroupRole': list(detail)[5],
                     } for detail in details]
        self.close_connection()
        return None

    # APPoeira Function: Event detail information. Called when /online-comments invoked
    def online_comments(self, online_id):
        self.open_connection()
        self.cursor.execute("SELECT u_c_o_comment, "
                            "u_c_o_date, "
                            "u_c_o_user_id, "
                            "user_apelhido, "
                            "user_pic_url "
                            "FROM user_comment_online "
                            "INNER JOIN onlines ON online_id = u_c_o_online_id "
                            "INNER JOIN users ON user_id = u_c_o_user_id "
                            "WHERE online_id = ?;",
                            (online_id,))
        comments = self.cursor.fetchall()
        if comments is not None:
            comments = list(comments)
            self.close_connection()
            return [{'userId': list(comment)[2],
                     'picUrl': list(comment)[4],
                     'userApelhido': list(comment)[3],
                     'comment': list(comment)[0],
                     'date': list(comment)[1],
                     } for comment in comments]
        self.close_connection()
        return None

    # APPoeira Function: new comment on a online. Called when /new-comment invoked
    def new_comment_online(self, online_id, user_id, comment):
        self.open_connection()
        response = self.cursor.execute("INSERT INTO user_comment_online ("
                                       "u_c_o_user_id, "
                                       "u_c_o_online_id, "
                                       "u_c_o_comment, "
                                       "u_c_o_date"
                                       ")"
                                       "VALUES (?,?,?,?);",
                                       (user_id, online_id, comment, datetime.utcnow()))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: User rated a online. Called when /user-rated-online invoked
    def user_rated_online(self, user_id, online_id, stars):
        self.open_connection()
        self.cursor.execute("SELECT u_r_o_rating "
                            "FROM user_rating_online "
                            "WHERE u_r_o_user_id = ? "
                            "AND u_r_o_online_id = ?",
                            (user_id, online_id))
        rating = self.cursor.fetchone()
        if rating is None:
            self.cursor.execute("INSERT INTO user_rating_online ("
                                "u_r_o_user_id, "
                                "u_r_o_online_id, "
                                "u_r_o_rating, "
                                "u_r_o_date"
                                ")"
                                "VALUES (?,?,?,?);",
                                (user_id, online_id, stars, datetime.utcnow()))
            self.connection.commit()
            self.cursor.execute("UPDATE onlines SET "
                                "online_verified = 1 "
                                "WHERE online_id = ?;",
                                (online_id,))
            self.connection.commit()
            self.close_connection()
            return {'ok': True,
                    'stars': stars
                    }
        else:
            self.close_connection()
            return {'ok': False,
                    'stars': rating[0]
                    }

    # APPoeira Function: join online. Called when /join-online invoked
    def join_online(self, online_id, user_id, role_id):
        self.open_connection()
        response = self.cursor.execute("INSERT INTO user_online ("
                                       "u_o_user_id, "
                                       "u_o_online_id, "
                                       "u_o_role_id, "
                                       "u_o_date, "
                                       "u_o_accepted"
                                       ")"
                                       "VALUES (?,?,?,?,?);",
                                       (user_id, online_id, role_id, datetime.utcnow(), True))
        if response.rowcount > 0:
            self.cursor.execute("UPDATE onlines SET "
                                "online_verified = 1 "
                                "WHERE online_id = ?;",
                                (online_id,))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # APPoeira Function: leave online. Called when /leave-online invoked
    def leave_online(self, online_id, user_id):
        self.open_connection()
        response = self.cursor.execute("DELETE FROM user_online "
                                       "WHERE u_o_user_id = ? "
                                       "AND u_o_online_id = ?;",
                                       (user_id, online_id))
        self.close_connection()
        return {'ok': True if response.rowcount > 0 else False}

    # COMMON FUNCTIONS #
    ########################

    # Common Function: Check token information once the token is valid
    def check_token_info(self, user_data):
        self.open_connection()
        self.cursor.execute("SELECT user_id "
                            "FROM users "
                            "WHERE user_first_name = ? "
                            "AND user_last_name = ? "
                            "AND user_apelhido = ? "
                            "AND user_rank_id = ? "
                            "AND user_email = ?;",
                            (user_data['name'],
                             user_data['lastName'],
                             user_data['apelhido'],
                             user_data['rank'],
                             user_data['email']))
        user_id = self.cursor.fetchone()
        self.close_connection()
        return True if user_id[0] == user_data['user_id'] else False

    # Common Function: Unverify user email when user changes it in the profile modification
    def unverify_user_email(self, user_id):
        self.open_connection()
        self.cursor.execute("UPDATE users "
                            "SET user_email_verified = false "
                            "WHERE user_id = ?;",
                            (user_id,))
        self.close_connection()

    # Common Function: Opens a DB connection
    def open_connection(self):
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.cursor = self.connection.cursor()
        except Error as e:
            print(e)

    # Common Function: Closes a DB connection
    def close_connection(self):
        self.connection.commit()
        self.connection.close()
