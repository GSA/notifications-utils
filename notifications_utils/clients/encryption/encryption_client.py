from base64 import urlsafe_b64encode
from json import dumps, loads

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from itsdangerous import URLSafeSerializer


class Encryption:
    def init_app(self, app):
        self.serializer = URLSafeSerializer(app.config.get('SECRET_KEY'))
        self.salt = app.config.get('DANGEROUS_SALT')

        password = app.config.get('SECRET_KEY').encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt.encode(),
            iterations=480_000
        )
        key = urlsafe_b64encode(kdf.derive(password))
        self.encryptor = Fernet(key)

    def encrypt(self, thing_to_encrypt):
        return self.encryptor.encrypt(dumps(thing_to_encrypt).encode())

    def decrypt(self, thing_to_decrypt):
        return loads(self.encryptor.decrypt(thing_to_decrypt).decode())

    def sign(self, thing_to_sign, salt=None):
        return self.serializer.dumps(thing_to_sign, salt=(salt or self.salt))

    def verify_signature(self, thing_to_verify, salt=None):
        return self.serializer.loads(thing_to_verify, salt=(salt or self.salt))
