import pytest
from itsdangerous import BadSignature

from notifications_utils.clients.encryption.encryption_client import Encryption


@pytest.fixture()
def encryption_client(app):
    client = Encryption()

    app.config['SECRET_KEY'] = 'test-notify-secret-key'
    app.config['DANGEROUS_SALT'] = 'test-notify-salt'

    client.init_app(app)

    return client


def test_should_encrypt_content(encryption_client):
    encrypted = encryption_client.encrypt("this".encode())
    assert encrypted != "this"


def test_encryption_is_nondeterministic(encryption_client):
    first_run = encryption_client.encrypt("this".encode())
    second_run = encryption_client.encrypt("this".encode())
    assert first_run != second_run


def test_should_decrypt_content(encryption_client):
    encrypted = encryption_client.encrypt("this".encode())
    assert encryption_client.decrypt(encrypted) == b"this"


def test_should_decrypt_previous_value(encryption_client):
    # encrypted was created in a previous run.
    # This will need to be replaced if the SECRET_KEY or DANGEROUS_SALT in the fixture ever change,
    # or any details about the key derivation within encryption_client.py
    encrypted = b'gAAAAABjkNhyDVLPwRXu94SSCK3bZW5syG6ovPcdIKICkgdsBnAz1F1QqYPd_kaiJdcllXENwn_wN3GV7EgfQtQpEbm52qTrLQ=='
    assert encryption_client.decrypt(encrypted).decode() == "this"


def test_should_sign_content(encryption_client):
    signed = encryption_client.sign("this")
    assert signed != "this"


def test_should_verify_content(encryption_client):
    signed = encryption_client.sign("this")
    assert encryption_client.verify_signature(signed) == "this"


def test_should_verify_signature(encryption_client):
    signed = encryption_client.sign("this")
    try:
        encryption_client.verify_signature(signed, salt="different-salt")
        raise AssertionError
    except BadSignature:
        pass


def test_should_sign_and_serialize_json(encryption_client):
    signed = encryption_client.sign({"this": "that"})
    assert encryption_client.verify_signature(signed) == {"this": "that"}
