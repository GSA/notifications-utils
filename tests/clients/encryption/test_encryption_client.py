import pytest

from notifications_utils.clients.encryption.encryption_client import (
    Encryption,
    EncryptionError,
)


@pytest.fixture()
def encryption_client(app):
    client = Encryption()

    app.config['SECRET_KEY'] = 'test-notify-secret-key'
    app.config['DANGEROUS_SALT'] = 'test-notify-salt'

    client.init_app(app)

    return client


def test_should_ensure_shared_salt_security(app):
    client = Encryption()
    app.config['SECRET_KEY'] = 'test-notify-secret-key'
    app.config['DANGEROUS_SALT'] = 'too-short'
    with pytest.raises(EncryptionError):
        client.init_app(app)


def test_should_ensure_custom_salt_security(encryption_client):
    with pytest.raises(EncryptionError):
        encryption_client.encrypt("this", salt='too-short')


def test_should_encrypt_strings(encryption_client):
    encrypted = encryption_client.encrypt("this")
    assert encrypted != "this"
    assert isinstance(encrypted, str)


def test_should_encrypt_dicts(encryption_client):
    to_encrypt = {"hello": "world"}
    encrypted = encryption_client.encrypt(to_encrypt)
    assert encrypted != to_encrypt
    assert encryption_client.decrypt(encrypted) == to_encrypt


def test_encryption_is_nondeterministic(encryption_client):
    first_run = encryption_client.encrypt("this")
    second_run = encryption_client.encrypt("this")
    assert first_run != second_run


def test_should_decrypt_content(encryption_client):
    encrypted = encryption_client.encrypt("this")
    assert encryption_client.decrypt(encrypted) == "this"


def test_should_decrypt_content_with_custom_salt(encryption_client):
    salt = "different-salt-value"
    encrypted = encryption_client.encrypt("this", salt=salt)
    assert encryption_client.decrypt(encrypted, salt=salt) == "this"


def test_should_verify_decryption(encryption_client):
    encrypted = encryption_client.encrypt("this")
    with pytest.raises(EncryptionError):
        encryption_client.decrypt(encrypted, salt="different-salt-value")


def test_should_decrypt_previous_values(encryption_client):
    # encrypted was created in a previous run.
    # This will need to be replaced if the SECRET_KEY or DANGEROUS_SALT in the fixture ever change,
    # or any details about the key derivation within encryption_client.py
    encrypted_bytes = b'gAAAAABjkQjAc7IJbMc6sUpHkI0BxKWwgH4i5fMQIPJ2lV1NPSNXPa_vIsUdTjCbwba5SzrlCpYs2LXTPWxKttCeWYTcQ7EjTQ=='  # noqa
    assert encryption_client.decrypt(encrypted_bytes) == "this"
    encrypted_str = 'gAAAAABjk2d_N7ojFjrREFpU2ImgNT17nebSjAVIuJRBQoll2KbPJ2s5jFX3gPRwusRnsgmag-QpdEFKZsFrE3v-f42tWjVfyA=='  # noqa
    assert encryption_client.decrypt(encrypted_str) == "this"


def test_should_sign_content(encryption_client):
    signed = encryption_client.sign("this")
    assert signed != "this"


def test_should_verify_content(encryption_client):
    signed = encryption_client.sign("this")
    assert encryption_client.verify_signature(signed) == "this"


def test_should_verify_signature(encryption_client):
    signed = encryption_client.sign("this")
    with pytest.raises(EncryptionError):
        encryption_client.verify_signature(signed, salt="different-salt-value")


def test_should_sign_and_serialize_json(encryption_client):
    signed = encryption_client.sign({"this": "that"})
    assert encryption_client.verify_signature(signed) == {"this": "that"}
