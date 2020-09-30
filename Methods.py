import jwt
import datetime
import json
import geopy
import facebook
import requests
import phonenumbers
from SQLite import DatabaseSQLite


class Interceptor:
    def __init__(self, key):
        self.key = key

    # Create personal token
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


class Sailor:
    def __init__(self):
        self.locator = geopy.geocoders.Nominatim(user_agent='Sailor')

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


class Postman:
    def __init__(self):
        self.mode = 0
        self.settings = {
            "MAIL_SERVER": 'smtp.gmail.com',
            "MAIL_PORT": 465,
            "MAIL_USE_TLS": False,
            "MAIL_USE_SSL": True,
            "MAIL_USERNAME": 'ficcionyciencia.contact@gmail.com',
            "MAIL_PASSWORD": 'yqvhskrqgxqzknuf'
        }


    def html_email_verification(self, mode):
        self.mode = mode
        if self.mode == 1:
            return '''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>APPoeira: Email no verificado</title>
                </head>
                    <body>
                        <h1>Hola, {}</h1>
                        <p>¡¡Tu email ha sido verificado!!</p>
                    </body>
                </html>
                '''
        elif self.mode == 2:
            return '''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>APPoeira: Email no verificado</title>
                </head>
                    <body>
                        <h1>Hola, {}.</h1>
                        <p>Hubo un error en la verificación de tu email.</p> 
                        <p>Puedes solicitar de nuevo que te enviemos el email de verificaición entrando en APPoeira</p>
                    </body>
                </html>
                '''
        elif self.mode == 3:
            return '''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>APPoeira: Email no verificado</title>
                </head>
                    <body>
                        <h1>Hola</h1>
                        <p>El link no era correcto.</p> 
                        <p>Puedes solicitar de nuevo que te enviemos el email de verificaición entrando en APPoeira</p>
                    </body>
                </html>
                '''


# TODO estudiar la nueva versión 8 del graph de facebook, que no entiendo nada
class Snoopy:
    def __init__(self, facebook_token, google_maps_key):
        super(Snoopy, self).__init__()
        self.facebookSnoopy = facebook.GraphAPI(access_token=facebook_token)
        self.googleMapsKey = google_maps_key
        self.geoCoder = geopy.geocoders.Nominatim(user_agent='snoopy')
        self.database = DatabaseSQLite('./DB/database.db')  # Database()

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
                'website': detail['result']['website'] if 'website' in detail['result'].keys() else None,
                'phone': detail['result']['international_phone_number'] if 'international_phone_number' in detail['result'].keys() else None,
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
                'pic_url': None,  # TODO enterarse de como coger url de imagen en facebook
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
