#!/usr/bin/env python3
from flask import Flask, url_for

from flask_saml2.sp import ServiceProvider
from tests.idp.base import CERTIFICATE as IDP_CERTIFICATE
from tests.sp.base2 import CERTIFICATE, PRIVATE_KEY


class ExampleServiceProvider(ServiceProvider):
    def get_logout_return_url(self):
        return url_for('index', _external=True)

    def get_default_login_return_url(self):
        return url_for('index', _external=True)


sp = ExampleServiceProvider()

app = Flask(__name__)
app.debug = True
app.secret_key = 'not a secret'

app.config['SERVER_NAME'] = '192.168.109.142:9000'
#app.config['SERVER_NAME'] = 'localhost:9000'
app.config['SAML2_SP'] = {
    'certificate': CERTIFICATE,
    'private_key': PRIVATE_KEY,
}

app.config['SAML2_IDENTITY_PROVIDERS'] = [
    {
        'CLASS': 'flask_saml2.sp.idphandler.IdPHandler',
        'OPTIONS': {
            'display_name': 'My Identity Provider',
            'entity_id': 'http://192.168.109.142:8000/saml/metadata.xml',
            'sso_url': 'http://192.168.109.142:8000/saml/login/',
            'slo_url': 'http://192.168.109.142:8000/saml/logout/',
            #'entity_id': 'http://localhost:8000/saml/metadata.xml',
            #'sso_url': 'http://localhost:8000/saml/login/',
            #'slo_url': 'http://localhost:8000/saml/logout/',
            'certificate': IDP_CERTIFICATE,
        },
    },
]


@app.route('/')
def index():
    print("FOOOOOOO! index")
    print(sp.is_user_logged_in())
    if sp.is_user_logged_in():
        auth_data = sp.get_auth_data_in_session()
        

        message = f'''
        <p>You are logged in as <strong>{auth_data.nameid}</strong>.
        The IdP sent back the following attributes:<p>
        '''


        if auth_data.nameid == 'luke@example.com':
            message = message + f'''
            <p>May the Force be with you</p>
            '''

        attrs = '<dl>{}</dl>'.format(''.join(
            f'<dt>{attr}</dt><dd>{value}</dd>'
            for attr, value in auth_data.attributes.items()))

        logout_url = url_for('flask_saml2_sp.logout')
        logout = f'<form action="{logout_url}" method="POST"><input type="submit" value="Log out"></form>'

        return message + attrs + logout
    else:
        message = '<p>You are logged out.</p>'

        login_url = url_for('flask_saml2_sp.login')
        link = f'<p><a href="{login_url}">Log in to continue</a></p>'

        return message + link


app.register_blueprint(sp.create_blueprint(), url_prefix='/saml/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
