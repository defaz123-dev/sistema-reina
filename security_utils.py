import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Usamos la SECRET_KEY del sistema como semilla para generar la llave de cifrado
# Si no existe, usamos una por defecto (se recomienda configurar SECRET_KEY en variables de entorno)
SECRET_SEED = os.environ.get('SECRET_KEY', 'clave_secreta_reina_2024').encode()

def _get_fernet():
    # Generamos una llave determinística basada en la semilla para poder descifrar después
    salt = b'sistema_reina_salt_pro_2024' # Sal fija para consistencia
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_SEED))
    return Fernet(key)

def cifrar_password(password):
    if not password: return ""
    try:
        f = _get_fernet()
        return f.encrypt(password.encode()).decode()
    except Exception as e:
        print(f"Error al cifrar: {e}")
        return password

def descifrar_password(password_cifrado):
    if not password_cifrado: return ""
    try:
        f = _get_fernet()
        return f.decrypt(password_cifrado.encode()).decode()
    except Exception:
        # Si falla el descifrado, asumimos que aún está en texto plano (para compatibilidad inicial)
        return password_cifrado
