# TODO GENERAL:
#  General
#       -> Hacerse con imágenes genéricas e iconos custom y con un logo                         ALBERTO
#       -> Estudiar las animaciones de Android                                                  INVESTIGAR
#       -> Hacer el script de actualización de grupos (ver como cojones hacer lo de facebook)   INVESTIGAR
#       -> Añadir auth para todas las activities que lo necesitan                               PUEDO
#       -> Añadir poder subir fotos de la librería o hacerlas en el momento                     INVESTIGAR
#       -> Salir de grupos, rodas, etc                                                          PENSARLO
#       -> Sanitizar inputs                                                                     INVESTIGAR
#       -> Cuando aparece el teclado se lleva el bottombar                                      INVESTIGAR
#  GroupListViewv
#       -> Hacer que aparezca la imagen en la etiqueta del marcador                             INVESTIGAR
#  GroupDetailView                                                                              OK
#  GroupDetailMoreView
#       -> Misma opción de Google o Fb.                                                         PUEDO
#       -> Al decir que eres jefe de grupo, enviarle un mail pidiendo los datos del grupo o alguna acreditación que de
#          alguna manera acredite a esa persona. Se le pedirá el teléfono y se enviará un mail con este teléfono a los
#          demás instructores de la ciudad. Este mail habrá dos botones uno con el sí y el otro con el no que, o bien
#          me llegará a mí, o bien se validará de forma automática. Informarle con un Popup     PENSARLO
#  GroupModificationView
#       -> No implementada                                                                      PUEDO
#       -> Sólo el creador podrá implementarla, o las personas a las que él habilite            PUEDO
#       -> Añadir descripción con texto enriquecido                                             INVESTIGAR
#       -> Invitar a gente (solo el dueño del grupo) y las invitacinoes tienen que aceptarse    PUEDO
#  RodaListView
#       -> Hacer que aparezca la imagen en la etiqueta del marcador                             INVESTIGAR
#  RodaDetailView                                                                               OK
#  RodaDetailMoreView
#       -> Ver qué pasa con la información que se envía al servidor y la que se muestra         PUEDO
#  RodaModificationView
#       -> La imagen por defecto no carga                                                       INVESTIGAR
#  EventListView                                                                                OK
#  EventDetailView                                                                              OK
#  EventDetailMoreView
#       -> No implementada                                                                      PUEDO
#       -> Hacer lo mismo que con los grupos                                                    PUEDO
#  EventModificationView
#       -> La imagen por defecto no carga                                                       INVESTIGAR
#       -> No guarda bien los convidados                                                        INVESTIGAR
#  OnlineListView
#       -> No implementada                                                                      PUEDO
#       -> Añadir un botón de crear Online                                                      PUEDO
#  OnlineDetailView
#       -> No implementada                                                                      PUEDO
#       -> Hacer lo mismo que con los grupos                                                    PUEDO
#  OnlineDetailMoreView
#       -> No implementada                                                                      PUEDO
#       -> Hacer lo mismo que con los grupos                                                    PUEDO
#  OnlineModificationView
#       -> La imagen por defecto no carga                                                       INVESTIGAR
#  LoginView
#       -> Añadir logo                                                                          ALBERTO
#  SignUpView
#       -> Añadir logo                                                                          ALBERTO
#  NewsView
#       -> No implementada                                                                      PUEDO
#       -> Una lista que te llevará al perfil de la persona que ha hecho la acción              PUEDO
#  SearchView
#       -> No implementada                                                                      PUEDO
#       -> Quiero que busque de manera dinámica en la base de datos. Ya sea de forma global o con un filtro de grupos,
#          usuarios, etc.                                                                       PUEDO
#  HelpView
#       -> No implementada                                                                      PUEDO
#       -> Estaría guapo meter vídeos tutoriales, pero igual es una puta flipada                INVESTIGAR
#  TopNavigationMenu
#       -> Que al desconectarse elimine la foto de perfil del topNavigation                     VER QUÉ PASA
#       -> Añadir logo                                                                          ALBERTO
#       -> Añadir notificaciones de invitaciones a grupos o cualquier otra cosa                 PENSARLO
#  UserDetailView
#       -> Añadir la funcionalidad de postear cosas en tu propio perfil (fotos, etc)            INVESTIGAR
#       -> Poner bonica la actividad                                                            PUEDO
#  ProfileModificationView                                                                      OK
#  BottomNavigationMenu                                                                         OK
#  ------
#  Para el futuro
#       -> Meter un código de error en cada requete para comunicar al cliente qué es lo que
#          ha salido mal (email ya existe, etc)
#       -> Anidar qweries aunque lo que me devuelva esté feo
#       -> Estudiar el control de activities abiertas

import jwt
import json
import secrets
from SQLite import DatabaseSQLite
from flask import Flask, request, make_response
from flask_mail import Mail, Message
import Methods

# TODO guardar esta clave en el environment y antes de crearla checkear si existe
SECRET_KEY = secrets.token_bytes(256)
SECRET_KEY = b'\xfa\x9f\xa2\x80\xcf\xa4\x91\xca\x81\r\xf9\x10\x02\tQ\x07o\x13u\xc3\x8b\xf8uj#\x8f\xf5\xae\xe9\x94\x0buD\x8b\'8d\xc7\xfc0\x05B\x89\x01x\x96N\x9d\xd4\x811\xf9\xa5\x87?\x8b\xbc\xfd&\x9fH+K\x98\x11\x07\xf2\xd9\xdf\xc9\xc4>6\xe1%\xb9\xac\xf5\x1d\xb6[\xbcSm\xb3\xb78\xb3T5\xcc%So8,0\x86\xadazj\xfb\xb0\x01\xe1\x9a(q,\xc1\x0b\x08\xbd\xad\xc3,1\xf4W\xff\\E\x03H\xf3\xb1\x18\n\xf8\x04\x99\x08\xb02\x86r\x04\xd4\xc2|\xddX<\xb6\x0f^\x19\x93\x9f\x8c\xc0\x06\xedj11\'\x1e-&\xb6\xbb\xaf\xfb\xb5\x1eK\x01/O\xb5h\xe2\xc9\xdf\\\x17\xf9\x1d!\xa9k\xfe\x9ax@g\xa6m\xecX@\xbbN\x9e\xbeE\xc1a\xa9\xcc\xacO]?D}E\xd1i\xceZ|a/\x8b,\x9e\xe1\xd4\xbb\x91S\xd6\xa0\xfc.n\x8c\xab\xb3\xe8\xc4\xb8\xa3\x18\xd4\xdb\x17(\xcb\x9fgs\xeaIN\xe4~\\\x9e")`\xf3'
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'ficcionyciencia.contact@gmail.com',
    "MAIL_PASSWORD": 'yqvhskrqgxqzknuf'
}

# Server initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config.update(mail_settings)
mail = Mail(app)

##########
# Routes #
##########

# Groups #
##########
@app.route('/location-group', methods=["POST"])
def location_group():
    groups = librarian.group_get_based_on_location(float(request.__getattr__('json')['latitude']),
                                                   float(request.__getattr__('json')['longitude']),
                                                   float(request.__getattr__('json')['distance']))
    if groups is not None:
        return make_response(json.dumps(groups), 200)
    return make_response(json.dumps(groups), 200)


@app.route('/group-detail', methods=["POST"])
def group_detail():
    if interceptor.check_for_token(request.__getattr__('json'), librarian) == 1:
        detail = librarian.group_detail(request.__getattr__('json')['groupId'],
                                        request.__getattr__('json')['userId'])
        if detail['id'] is not None:
            return make_response(json.dumps(detail), 200)
    elif interceptor.check_for_token(request.__getattr__('json'), librarian) == 2:
        return make_response(json.dumps({'error': "Missing Token"}), 200)
    elif interceptor.check_for_token(request.__getattr__('json'), librarian) == 3:
        return make_response(json.dumps({'error': "Invalid Token"}), 200)

# Token
@app.route('/group-comments', methods=["POST"])
def group_comments():
    groups = librarian.group_comments(request.__getattr__('json')['groupId'])
    if groups is not None:
        return make_response(json.dumps(groups), 200)
    return make_response(json.dumps(groups), 200)

# Token
@app.route('/group-join', methods=["POST"])
def group_join():
    ok = librarian.join_group(request.__getattr__('json')['groupId'],
                              request.__getattr__('json')['userId'],
                              request.__getattr__('json')['roleId'])
    return make_response(json.dumps(ok), 200)

# Token
@app.route('/group-detail-more', methods=["POST"])
def group_detail_more():
    details = librarian.group_detail_more(request.__getattr__('json')['groupId'])
    if details is not None:
        return make_response(json.dumps(details), 200)
    return make_response(json.dumps(details), 200)

# Token
@app.route('/new-comment-group', methods=["POST"])
def new_comment_group():
    ok = librarian.new_comment_group(request.__getattr__('json')['groupId'],
                                     request.__getattr__('json')['userId'],
                                     request.__getattr__('json')['comment'])
    return make_response(json.dumps(ok), 200)

# Token
@app.route('/user-rated-group', methods=["POST"])
def user_rated_group():
    stars = librarian.user_rated_group(request.__getattr__('json')['UserId'],
                                       request.__getattr__('json')['GroupId'],
                                       request.__getattr__('json')['Rating'])
    return make_response(json.dumps(stars), 200)


# Rodas #
#########
@app.route('/location-roda', methods=["POST"])
def location_roda():
    rodas = librarian.roda_get_based_on_location(float(request.__getattr__('json')['latitude']),
                                                 float(request.__getattr__('json')['longitude']),
                                                 float(request.__getattr__('json')['distance']))
    if rodas is not None:
        return make_response(json.dumps(rodas), 200)
    return make_response(json.dumps(rodas), 200)


@app.route('/roda-detail', methods=["POST"])
def roda_detail():
    if interceptor.check_for_token(request.__getattr__('json'), librarian) == 1:
        detail = librarian.roda_detail(request.__getattr__('json')['rodaId'],
                                       request.__getattr__('json')['userId'])
        if detail['id'] is not None:
            return make_response(json.dumps(detail), 200)
    elif interceptor.check_for_token(request.__getattr__('json'), librarian) == 2:
        return make_response(json.dumps({'error': "Missing Token"}), 200)
    elif interceptor.check_for_token(request.__getattr__('json'), librarian) == 3:
        return make_response(json.dumps({'error': "Invalid Token"}), 200)

# Token
@app.route('/roda-create', methods=["POST"])
def roda_create():
    roda = librarian.roda_create(request.__getattr__('json')['owners'],
                                 request.__getattr__('json')['name'],
                                 request.__getattr__('json')['description'],
                                 request.__getattr__('json')['date'],
                                 request.__getattr__('json')['picUrl'],
                                 request.__getattr__('json')['invited'],
                                 float(request.__getattr__('json')['latitude']),
                                 float(request.__getattr__('json')['longitude']),
                                 sailor.city_from_latlng(float(request.__getattr__('json')['latitude']),
                                                         float(request.__getattr__('json')['longitude'])),
                                 sailor.country_from_latlng(float(request.__getattr__('json')['latitude']),
                                                            float(request.__getattr__('json')['longitude'])),

                                 request.__getattr__('json')['phone'])
    if roda is not None:
        return make_response(json.dumps(roda), 200)
    return make_response(json.dumps(roda), 200)

# Token
@app.route('/roda-comments', methods=["POST"])
def roda_comments():
    rodas = librarian.roda_comments(request.__getattr__('json')['groupId'])
    if rodas is not None:
        return make_response(json.dumps(rodas), 200)
    return make_response(json.dumps(rodas), 200)

# Token
@app.route('/roda-join', methods=["POST"])
def roda_join():
    ok = librarian.join_roda(request.__getattr__('json')['groupId'],
                             request.__getattr__('json')['userId'],
                             request.__getattr__('json')['roleId'])
    return make_response(json.dumps(ok), 200)

# Token
@app.route('/roda-detail-more', methods=["POST"])
def roda_detail_more():
    details = librarian.roda_detail_more(request.__getattr__('json')['groupId'])
    if details is not None:
        return make_response(json.dumps(details), 200)
    return make_response(json.dumps(details), 200)

# Token
@app.route('/new-comment-roda', methods=["POST"])
def new_comment_roda():
    ok = librarian.new_comment_roda(request.__getattr__('json')['groupId'],
                                    request.__getattr__('json')['userId'],
                                    request.__getattr__('json')['comment'])
    return make_response(json.dumps(ok), 200)

# Token
@app.route('/user-rated-roda', methods=["POST"])
def user_rated_roda():
    stars = librarian.user_rated_roda(request.__getattr__('json')['UserId'],
                                      request.__getattr__('json')['GroupId'],
                                      request.__getattr__('json')['Rating'])
    return make_response(json.dumps(stars), 200)


# Events #
#########
@app.route('/location-event', methods=["POST"])
def location_event():
    event = librarian.event_get_based_on_location(float(request.__getattr__('json')['latitude']),
                                                  float(request.__getattr__('json')['longitude']),
                                                  float(request.__getattr__('json')['distance']))
    if event is not None:
        return make_response(json.dumps(event), 200)
    return make_response(json.dumps(event), 200)


@app.route('/event-detail', methods=["POST"])
def event_detail():
    if interceptor.check_for_token(request.__getattr__('json'), librarian) == 1:
        detail = librarian.event_detail(request.__getattr__('json')['eventId'],
                                        request.__getattr__('json')['userId'])
        if detail['id'] is not None:
            return make_response(json.dumps(detail), 200)
    elif interceptor.check_for_token(request.__getattr__('json'), librarian) == 2:
        return make_response(json.dumps({'error': "Missing Token"}), 200)
    elif interceptor.check_for_token(request.__getattr__('json'), librarian) == 3:
        return make_response(json.dumps({'error': "Invalid Token"}), 200)
    return make_response(json.dumps(None), 200)

# Token
@app.route('/event-create', methods=["POST"])
def event_create():
    event = librarian.event_create(request.__getattr__('json')['owners'],
                                   request.__getattr__('json')['name'],
                                   request.__getattr__('json')['description'],
                                   request.__getattr__('json')['date'],
                                   request.__getattr__('json')['picUrl'],
                                   request.__getattr__('json')['invited'],
                                   int(request.__getattr__('json')['platform']),
                                   float(request.__getattr__('json')['latitude']) if 'latitude' in request.__getattr__('json') else 0.0,
                                   float(request.__getattr__('json')['longitude']) if 'longitude' in request.__getattr__('json') else 0.0,
                                   sailor.city_from_latlng(float(request.__getattr__('json')['latitude']),
                                                           float(request.__getattr__('json')['longitude'])) if 'latitude' in request.__getattr__('json') else '',
                                   sailor.country_from_latlng(float(request.__getattr__('json')['latitude']),
                                                              float(request.__getattr__('json')['longitude']))if 'latitude' in request.__getattr__('json') else '',
                                   request.__getattr__('json')['phone'],
                                   request.__getattr__('json')['convided'],
                                   request.__getattr__('json')['key'])
    if event is not None:
        return make_response(json.dumps(event), 200)
    return make_response(json.dumps(event), 200)

# Onlines #
###########
# Token
@app.route('/online-create', methods=["POST"])
def online_create():
    online = librarian.online_create(request.__getattr__('json')['owners'],
                                     request.__getattr__('json')['name'],
                                     request.__getattr__('json')['description'],
                                     request.__getattr__('json')['date'],
                                     request.__getattr__('json')['picUrl'],
                                     request.__getattr__('json')['invited'],
                                     int(request.__getattr__('json')['platform']),
                                     request.__getattr__('json')['phone'],
                                     request.__getattr__('json')['key'])
    if online is not None:
        return make_response(json.dumps(online), 200)
    return make_response(json.dumps(online), 200)


# Users #
#########
@app.route('/sign-up', methods=["POST"])
def signup_user():
    user = librarian.user_signup(request.__getattr__('json')['firstName'],
                                 request.__getattr__('json')['lastName'],
                                 request.__getattr__('json')['apelhido'],
                                 request.__getattr__('json')['email'],
                                 request.__getattr__('json')['password'],
                                 request.__getattr__('json')['rank'])
    if user['id'] is not None:
        send_verification_mail(interceptor.create_validation_token(user['id'],
                                                                   user['email'],
                                                                   user['name'],
                                                                   user['lastName'],
                                                                   user['apelhido'],
                                                                   user['rank']), user['email'])
    return make_response(json.dumps(user), 200)


@app.route('/login', methods=["POST"])
def login_user():
    user = librarian.user_login(request.__getattr__('json')['email'],
                                request.__getattr__('json')['password'])
    if user['id'] is not None:
        user['token'] = interceptor.create_personal_token(user['id'],
                                                          user['email'],
                                                          user['name'],
                                                          user['lastName'],
                                                          user['apelhido'],
                                                          user['rank'])
    return make_response(json.dumps(user), 200)

# Token
@app.route('/user-follow', methods=["POST"])
def user_follow():
    ok = librarian.user_follow(request.__getattr__('json')['myId'],
                               request.__getattr__('json')['userId'])
    return make_response(json.dumps(ok), 200)

# Token
@app.route('/user-unfollow', methods=["POST"])
def user_unfollow():
    ok = librarian.user_unfollow(request.__getattr__('json')['myId'],
                                 request.__getattr__('json')['userId'])
    return make_response(json.dumps(ok), 200)

# Token
@app.route('/user-detail', methods=["POST"])
def user_detail():
    user = librarian.user_detail(request.__getattr__('json')['userId'])
    return make_response(json.dumps(user), 200)

# Token
@app.route('/user-search', methods=["POST"])
def user_search():
    users = librarian.user_search(request.__getattr__('json')['search'])
    return make_response(json.dumps(users), 200)

# Token
@app.route('/profile-update', methods=["POST"])
def user_profile_update():
    user = librarian.user_update_profile(request.__getattr__('json')['userId'],
                                         request.__getattr__('json')['firstName'],
                                         request.__getattr__('json')['lastName'],
                                         request.__getattr__('json')['apelhido'],
                                         request.__getattr__('json')['email'],
                                         request.__getattr__('json')['password'],
                                         request.__getattr__('json')['newPassword'],
                                         request.__getattr__('json')['rank'],
                                         request.__getattr__('json')['picUrl'])
    if "{0:b}".format(user['error'])[6] == '1':
        librarian.unverify_user_email(request.__getattr__('json')['userId'])
        send_verification_mail(interceptor.create_validation_token(request.__getattr__('json')['userId'],
                                                                   user['email'],
                                                                   user['name'],
                                                                   user['lastName'],
                                                                   user['apelhido'],
                                                                   user['rank']), user['email'])
    else:
        user['token'] = interceptor.create_personal_token(request.__getattr__('json')['userId'],
                                                          user['email'],
                                                          user['name'],
                                                          user['lastName'],
                                                          user['apelhido'],
                                                          user['rank'])
    return make_response(json.dumps(user), 200)

# TODO hasta aquí de puta madre. Ahora, hay que ver cómo hacer el direccionamiento a la aplicación o algo de
#  alguna manera para, o bien hacer login, o bien algo así
@app.route('/email-verification')
def email_verification():
    try:
        user_data = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
        verified = librarian.email_verification(user_data['user_id']) if librarian.check_token_info(user_data) else False
        return make_response(postman.html_email_verification(1 if verified else 2).format(user_data['apelhido']))
    except jwt.ExpiredSignatureError or jwt.DecodeError or jwt.InvalidTokenError or jwt.InvalidSignatureError:
        return make_response(postman.html_email_verification(3))


def send_verification_mail(token, email):
    with app.app_context():
        text = """
            <p>Hi!<br>
                How are you?<br>
                Here is the <a href="https://f394e381119b.ngrok.io /email-verification?token={}">link</a> you wanted.
            </p>
            """.format(token)
        msg = Message(subject="Hello",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[email],
                      body=text)
        mail.send(msg)


if __name__ == "__main__":
    # Initialising the Librarian
    librarian = DatabaseSQLite('./DB/database.db')
    # Initialising the Interceptor
    interceptor = Methods.Interceptor(app.config['SECRET_KEY'])
    # Initialising the Postman
    postman = Methods.Postman()
    # Initialising the Sailor
    sailor = Methods.Sailor()
    # Calling the server
    app.run(port=5000, debug=False)
