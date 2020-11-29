import jwt
import datetime
import json
import geopy
import facebook
import requests
import phonenumbers
import boto3
from SQLite import DatabaseSQLite
from math import sin, cos, sqrt, atan2, radians


# Interceptor is in charge of the security. From token to sanitize inputs
class Interceptor:
    def __init__(self, key):
        self.key = key

    def create_personal_token(self, user_id, email, name, last_name, apelhido, rank):
        payload = {
            'user_id': user_id,
            'email': email,
            'name': name,
            'lastName': last_name,
            'apelhido': apelhido,
            'rank': rank
            }
        return jwt.encode(payload, self.key).decode('utf-8')

    def create_validation_token(self, user_id, email, name, last_name, apelhido, rank):
        payload = {
            'user_id': user_id,
            'email': email,
            'name': name,
            'lastName': last_name,
            'apelhido': apelhido,
            'rank': rank,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)
            }
        return jwt.encode(payload, self.key).decode('utf-8')

    def check_for_token(self, message, librarian):
        if 'token' not in message.keys():
            return 2
        try:
            user_data = jwt.decode(message['token'], self.key)
            return 1 if librarian.check_token_info(user_data) else 4
        except jwt.InvalidTokenError:
            return 3


# Elephant has all the constants of the project and is the interface with AWS S3
class Elephant:
    def __init__(self):
        # APP constants
        self.APP_ROUTE = 'https://7394e12b510b.ngrok.io'
        # Mail Constants
        self.ADMIN_MAIL = 'appoeira.onethousandprojects@gmail.com'
        # Snoopy constants
        self.FACEBOOK_TOKEN = 'EAAEd3h8ryTIBAIysNjY7gfk2E0dGnvnAfspf3FHNSIeAl8xQc2Awq3LLDc2cPeWke3lffIsN2FvtJSpHd6cF9LxDIYvGvvLgI1qRLfhQNL55bilVt4AxjJKZAYUpOZBqLxIZBiuHTwdDUuWtkh612108PaTOj7V4d7KUMmInUji0fPxu7mBgbewolJ1NVox2S4jDRaKQgZDZD'
        self.GOOGLE_MAPS_KEY = 'AIzaSyATucbLXuXUMgYmynDqjy9qiY1Egz1Dh-o'
        self.INSTAGRAM_TOKEN = 'IGQVJXVVNjbDZALYjZAtYlpyaDA5VS1vSXVLSUFFdVc5VWlieDFadl9UdW9yUFI2TWlOcUpDYm1DMjQ2YmVmSko2SlpWSllCaGZAxSUxuUGptNWxKYkRuZAHVQSGNSVnRrbXViblpUcWV3dGVBbUtsdFdYQgZDZD'
        self.CITIES_PATH = "./Source/worldcities.csv"
        # DB constants
        self.DB_PATH = "./DB/database.db"
        self.RELATION_DISTANCE = 0.009009009
        self.DEFAULT_GROUP_IMAGE = 'https://appoeira.s3.eu-west-2.amazonaws.com/group_avatar_default.jpg'
        self.DEFAULT_RODA_IMAGE = 'https://appoeira.s3.eu-west-2.amazonaws.com/event_avatar_default.jpg'
        self.DEFAULT_EVENT_IMAGE = 'https://appoeira.s3.eu-west-2.amazonaws.com/event_avatar_default.jpg'
        self.DEFAULT_ONLINE_IMAGE = 'https://appoeira.s3.eu-west-2.amazonaws.com/event_avatar_default.jpg'
        self.DEFAULT_USER_IMAGE = 'https://appoeira.s3.eu-west-2.amazonaws.com/user_avatar_default.jpg'
        # AWS configuration
        self.AWS_GENERAL_KEY_ID = 'AKIAJFUZL44WQT476OTQ'
        self.AWS_GENERAL_KEY_SECRET = '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'
        # AWS S3 configuration
        self.REGION_NAME = 'eu-west-2'
        self.BUCKET_NAME = 'appoeira'
        self.AWS_ACCESS_KEY_ID = 'AKIASYPYF2Y4TIF5W6WE'
        self.AWS_ACCESS_KEY_SECRET = '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'
        self.s3_instance = boto3.resource("s3",
                                          aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                                          aws_secret_access_key=self.AWS_ACCESS_KEY_SECRET)

    def upload_object(self, file, object_id=0):
        file_name = file.filename
        if object_id != 0:
            occurrences = [i for i, a in enumerate(file_name) if a == "_"]
            file_name = file.filename[:occurrences[1]+1] + str(object_id) + file.filename[occurrences[2]:]
        occurrences = [i for i, a in enumerate(file_name) if a == "_"]
        file_to_upload = file.read()
        old_objects = self.s3_instance.Bucket(self.BUCKET_NAME).objects.filter(Prefix=file_name[:occurrences[2]])
        for old in old_objects:
            old.delete()
        obj = self.s3_instance.Bucket(self.BUCKET_NAME).put_object(Key='{}.jpg'.format(file_name),
                                                                   Body=file_to_upload,
                                                                   ACL='public-read')
        return "https://{}.s3.{}.amazonaws.com/{}".format(obj.bucket_name, self.REGION_NAME, obj.key), obj is not None, obj.key


# Sailor is in charge of handling all the geographical methods
class Sailor:
    def __init__(self):
        self.locator = geopy.geocoders.Nominatim(user_agent='Sailor')
        self.earth_radius = 6373.0

    def country_from_latlng(self, latitude, longitude):
        return self.locator.reverse(str(latitude) + ',' + str(longitude), language='en').raw['address']['country']

    def city_from_latlng(self, latitude, longitude):
        address = self.locator.reverse(str(latitude) + ',' + str(longitude), language='en').raw['address']
        if 'city' in address.keys():
            return address['city']
        elif 'town' in address.keys():
            return address['town']
        elif 'county' in address.keys():
            return address['county']
        else:
            return ''

    def full_address_from_latlng(self, latitude, longitude):
        return ', '.join(self.locator.reverse(str(latitude) + ',' + str(longitude), language='en').address.split(',')[0:2])

    def geodesic_distance(self, lat1, lng1, lat2, lng2):
        lat1 = radians(lat1)
        lng1 = radians(lng1)
        lat2 = radians(lat2)
        lng2 = radians(lng2)

        d_lng = lng2 - lng1
        d_lat = lat2 - lat1

        a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return self.earth_radius * c


# Postman handles all the mail that is implemented in the application
class Postman:
    def __init__(self):
        self.mode = 0
        self.settings = {
            "MAIL_SERVER": 'smtp.gmail.com',
            "MAIL_PORT": 465,
            "MAIL_USE_TLS": False,
            "MAIL_USE_SSL": True,
            "MAIL_USERNAME": 'appoeira.onethousandprojects@gmail.com',
            "MAIL_PASSWORD": 'uhjltusxkzycmrji'
        }
        self.VERIFICATION_BODY = 'Hi! How are you? Here is the link you wanted.\n{}/email-verification?token={}'
        self.NEW_OWNER_BODY = 'El usuario con id {} se ha unido al grupo con id {}'
        with open('./Templates/email_verification.html', 'r') as template:
            self.VERIFICATION_HTML = template.read()
        with open('./Templates/email_verified.html', 'r') as template:
            self.VERIFICATION_OK_HTML = template.read()
        with open('./Templates/email_not_verified.html', 'r') as template:
            self.VERIFICATION_NOK_HTML = template.read()
        with open('./Templates/email_invalid_token.html', 'r') as template:
            self.VERIFICATION_BAD_HTML = template.read()

    def html_email_verification(self, mode):
        self.mode = mode
        if self.mode == 1:
            return self.VERIFICATION_OK_HTML
        elif self.mode == 2:
            return self.VERIFICATION_NOK_HTML
        elif self.mode == 3:
            return self.VERIFICATION_BAD_HTML

    def verification_mail(self, token, route):
        return self.VERIFICATION_BODY.format(route, token), self.VERIFICATION_HTML.format(route, token)

    def new_owner_mail(self, new_owner_id, group_id):
        return self.NEW_OWNER_BODY.format(new_owner_id, group_id)


# Snoopy is the one that gets the data from the cloud
class Snoopy:
    def __init__(self, facebook_token, google_maps_key, elephant):
        super(Snoopy, self).__init__()
        self.facebookSnoopy = facebook.GraphAPI(access_token=facebook_token)
        self.googleMapsKey = google_maps_key
        self.geoCoder = geopy.geocoders.Nominatim(user_agent='snoopy')
        self.database = DatabaseSQLite(elephant.DB_PATH, elephant.RELATION_DISTANCE, elephant.DEFAULT_GROUP_IMAGE, elephant.DEFAULT_USER_IMAGE, Sailor())  # Database()

    def get_city_from_lat_lng(self, latitude, longitude):
        # Function that returns the address from a lat long.
        address = self.geoCoder.reverse(str(latitude) + ',' + str(longitude))
        return address.raw['address']

    def get_fb_nearby(self, latitude, longitude, distance, limit, query):
        # Function that gets all the places on facebook given lat long and radius
        return self.facebookSnoopy.search(type='place',
                                          center=str(latitude) + ',' + str(longitude),
                                          distance=str(distance),
                                          limit=str(limit),
                                          q=query,
                                          fields='name,location,website,phone,description,about')

    def get_fb_events(self, latitude, longitude, distance, limit, query):
        # Function that gets all the places on facebook given lat long and radius
        return self.facebookSnoopy.search(type='place',
                                          center=str(latitude) + ',' + str(longitude),
                                          distance=str(distance),
                                          limit=str(limit),
                                          q=query,
                                          fields='name,location,website,phone,description,about')

    def get_go_nearby(self, latitude, longitude, distance, query):
        # Function that gets all the places on google given lat long and radius
        result = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword={}&location={},{}&radius={}&key={}'.format(query, latitude, longitude, distance, self.googleMapsKey))
        my_json = json.loads(result.content.decode('utf8').replace("\n", ''))
        while 'next_page_token' in my_json:
            result = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={}&key={}'.format(my_json['next_page_token'], self.googleMapsKey))
            json_aux = json.loads(result.content.decode('utf8').replace("\n", ''))
            if 'next_page_token' in json_aux:
                my_json['next_page_token'] = json_aux['next_page_token']
            else:
                del my_json['next_page_token']
            for item in json_aux['results']:
                my_json['results'].append(item)
        return my_json

    def get_pic_go(self, reference):
        # Function that returns the url of a google picture to load on the phone
        result = requests.get('https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={}&key={}'.format(reference, self.googleMapsKey))
        return result.url

    def make_google_pretty(self, body):
        # Function that constructs the dictionary standard for working together between google and facebook
        detail = requests.get("https://maps.googleapis.com/maps/api/place/details/json?place_id={}&fields=website,international_phone_number&key={}".format(body['place_id'], self.googleMapsKey))
        detail = json.loads(detail.content.decode('utf8').replace("\n", ''))
        address = self.geoCoder.reverse(str(body['geometry']['location']['lat']) + ', ' + str(body['geometry']['location']['lng']))
        return {'name': body['name'],
                'pic_url': self.get_pic_go(body['photos'][0]['photo_reference']) if 'photos' in body.keys() else None,
                'location': {'city': address.raw['address']['city'] if 'city' in address.raw['address'] else None,
                             'country': address.raw['address']['country'] if 'country' in address.raw['address'] else None,
                             'latitude': address.latitude,
                             'longitude': address.longitude,
                             'street': body['vicinity'],
                             'zip': address.raw['address']['postcode'] if 'postcode' in address.raw['address'] else None
                             },
                'website': detail['result']['website'] if 'result' in detail.keys() and 'website' in detail['result'].keys() else None,
                'phone': detail['result']['international_phone_number'] if 'result' in detail.keys() and 'international_phone_number' in detail['result'].keys() else None,
                'about': None,
                'id': body['place_id']
                }

    def make_facebook_pretty(self, body, city):
        # Function that constructs the dictionary standard for working together between google and facebook
        if 'phone' in body.keys():
            phones = phonenumbers.PhoneNumberMatcher(body['phone'], city[5])
            for phone in phones:
                body['phone'] = phonenumbers.format_number(phone.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                break
        else:
            body['phone'] = None
        if 'about' in body.keys():
            if 'description' in body.keys():
                body['about'] += body['description']
                del body['description']
        elif 'description' in body.keys():
            body['about'] = body['description']
        else:
            body['about'] = None
        address = self.geoCoder.reverse(str(body['location']['latitude']) + ', ' + str(body['location']['longitude']))
        return {'name': body['name'],
                'pic_url': None,
                'location': {'city': address.raw['address']['city'] if 'city' in address.raw['address'] else None,
                             'country': address.raw['address']['country'] if 'country' in address.raw['address'] else None,
                             'latitude': address.latitude,
                             'longitude': address.longitude,
                             'street': body['street'] if 'street' in body.keys() else None,
                             'zip': address.raw['address']['postcode'] if 'postcode' in address.raw['address'] else None
                             },
                'website': body['website'] if 'website' in body.keys() else None,
                'phone': body['phone'],
                'about': body['about'],
                'id': body['id']
                }
