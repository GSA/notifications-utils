from base64 import urlsafe_b64encode
from json import dumps, loads

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from itsdangerous import BadSignature, URLSafeSerializer


class EncryptionError(Exception):
    pass


class SaltLengthError(Exception):
    pass


class Encryption:
    def init_app(self, app):
        self._serializer = URLSafeSerializer(app.config.get('SECRET_KEY'))
        self._salt = app.config.get('DANGEROUS_SALT')
        self._password = app.config.get('SECRET_KEY').encode()

        try:
            self._shared_encryptor = Fernet(self._derive_key(self._salt))
        except SaltLengthError as reason:
            raise EncryptionError("DANGEROUS_SALT must be at least 16 bytes") from reason

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
            try:
                return Fernet(self._derive_key(salt))
            except SaltLengthError as reason:
                raise EncryptionError("Custom salt value must be at least 16 bytes") from reason
        else:
            return self._shared_encryptor

    def _derive_key(self, salt):
        salt_bytes = salt.encode()
        if len(salt_bytes) < 16:
            # For the salt to be secure, at least for the PBKDF2HMAC derivation function,
            # it must be 16 bytes or longer and randomly generated.
            # https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC:~:text=Secure%20values%201%20are%20128%2Dbits%20(16%20bytes)%20or%20longer%20and%20randomly%20generated.
            raise SaltLengthError
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=480_000
        )
        return urlsafe_b64encode(kdf.derive(self._password))
