import logging

import cryptography.hazmat.primitives
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from cryptography.hazmat.primitives import serialization

from .models import PrimaryLink

logger = logging.getLogger(__name__)


def get_public_key(public_key_pem: str) -> rsa.RSAPublicKey | bool:
    try:
        # Charger la clé publique au format PEM
        public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'), backend=default_backend())

        # Vérifier que la clé publique est au format RSA
        if not isinstance(public_key, rsa.RSAPublicKey):
            return False
        return public_key

    except Exception as e:
        logger.error(f"Erreur de validation get_public_key : {e}")
        raise e

# Validation of the pin code
class PinValidator(serializers.Serializer):
    pin_code = serializers.CharField(max_length=8, min_length=6, required=True)

    #check if the primary_link object exists
    def validate_pinCode(self, value):
        self.link = get_object_or_404(PrimaryLink, pin_code=value)
        return value


class LinkValidator(serializers.Serializer):
    server_url = serializers.URLField(max_length=200, required=True)
    rsa_pub_pem = serializers.CharField(max_length=512, required=True)
    locale = serializers.CharField(max_length=2, required=True)

    def rsa_pub_pem_validator(self, value):
        try :
            pub = get_public_key(value)
            if pub.key_size < 2048:
                raise serializers.ValidationError("Public key size too small")
        except Exception as e:
            raise serializers.ValidationError("Public key not valid, must be 2048 min rsa key")
        return value



