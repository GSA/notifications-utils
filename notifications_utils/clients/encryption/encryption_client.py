from base64 import urlsafe_b64encode
from json import dumps, loads

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from itsdangerous import BadSignature, URLSafeSerializer


class EncryptionError(Exception):
    pass


class Encryption:
    def init_app(self, app):
        self._serializer = URLSafeSerializer(app.config.get('SECRET_KEY'))
        self._salt = app.config.get('DANGEROUS_SALT')
        self._password = app.config.get('SECRET_KEY').encode()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt.encode(),
            iterations=480_000
        )
        key = urlsafe_b64encode(kdf.derive(self._password))
        self._shared_encryptor = Fernet(key)

    # thing_to_encrypt must be serializable as JSON
    # returns a UTF-8 string
    def encrypt(self, thing_to_encrypt, salt=None):
        return self._encryptor(salt).encrypt(dumps(thing_to_encrypt).encode()).decode()

    # thing_to_decrypt can be a UTF-8 string or bytes, and must be deserializable as JSON after decryption
    def decrypt(self, thing_to_decrypt, salt=None):
        try:
            return loads(self._encryptor(salt).decrypt(thing_to_decrypt))
        except InvalidToken as reason:
            raise EncryptionError from reason

    def sign(self, thing_to_sign, salt=None):
        return self._serializer.dumps(thing_to_sign, salt=(salt or self._salt))

    def verify_signature(self, thing_to_verify, salt=None):
        try:
            return self._serializer.loads(thing_to_verify, salt=(salt or self._salt))
        except BadSignature as reason:
            raise EncryptionError from reason

    def _encryptor(self, salt=None):
        if salt:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=480_000
            )
            key = urlsafe_b64encode(kdf.derive(self._password))
            return Fernet(key)
        else:
            return self._shared_encryptor
