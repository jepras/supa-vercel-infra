import os
import base64
import hashlib
import secrets
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class TokenEncryption:
    def __init__(self):
        encryption_key = os.getenv("ENCRYPTION_KEY")
        
        # Require encryption key in all environments
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY environment variable is required")
        
        # Handle base64-encoded keys
        try:
            # Try to decode as base64 first
            decoded_key = base64.urlsafe_b64decode(encryption_key + '=' * (4 - len(encryption_key) % 4))
            if len(decoded_key) == 32:
                # It's a valid base64-encoded 32-byte key
                self.encryption_key = decoded_key
                logger.info("Using base64-decoded 32-byte encryption key")
            else:
                # Not a valid base64-encoded key, treat as raw string
                self.encryption_key = encryption_key.encode()
        except Exception:
            # Not valid base64, treat as raw string
            self.encryption_key = encryption_key.encode()
        
        # Ensure the key is exactly 32 bytes (256 bits)
        if len(self.encryption_key) != 32:
            raise ValueError("ENCRYPTION_KEY must be exactly 32 bytes")
    
    def _derive_key(self, salt: bytes) -> bytes:
        """Derive a key from the master key using PBKDF2-like approach"""
        # Use SHA256 for key derivation (simplified PBKDF2)
        key = hashlib.sha256(self.encryption_key + salt).digest()
        return key
    
    def _xor_encrypt(self, data: bytes, key: bytes) -> bytes:
        """Simple XOR encryption (for basic token protection)"""
        # Repeat key to match data length
        repeated_key = (key * (len(data) // len(key) + 1))[:len(data)]
        return bytes(a ^ b for a, b in zip(data, repeated_key))
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token string using built-in libraries"""
        try:
            # Generate a random salt for this encryption
            salt = secrets.token_bytes(16)
            
            # Derive encryption key
            derived_key = self._derive_key(salt)
            
            # Encrypt the token
            token_bytes = token.encode('utf-8')
            encrypted_data = self._xor_encrypt(token_bytes, derived_key)
            
            # Combine salt + encrypted data and encode as base64
            combined = salt + encrypted_data
            return base64.urlsafe_b64encode(combined).decode()
            
        except Exception as e:
            logger.error(f"Error encrypting token: {str(e)}")
            raise Exception(f"Failed to encrypt token: {str(e)}")
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt an encrypted token string"""
        try:
            # Decode from base64
            combined = base64.urlsafe_b64decode(encrypted_token.encode())
            
            # Extract salt (first 16 bytes) and encrypted data
            salt = combined[:16]
            encrypted_data = combined[16:]
            
            # Derive the same key
            derived_key = self._derive_key(salt)
            
            # Decrypt the data
            decrypted_data = self._xor_encrypt(encrypted_data, derived_key)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error decrypting token: {str(e)}")
            raise Exception(f"Failed to decrypt token: {str(e)}")
    
    def encrypt_dict(self, data: dict) -> dict:
        """Encrypt sensitive fields in a dictionary"""
        encrypted_data = data.copy()
        
        # Fields that should be encrypted
        sensitive_fields = ['access_token', 'refresh_token', 'id_token']
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_token(encrypted_data[field])
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict) -> dict:
        """Decrypt sensitive fields in a dictionary"""
        decrypted_data = data.copy()
        
        # Fields that should be decrypted
        sensitive_fields = ['access_token', 'refresh_token', 'id_token']
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt_token(decrypted_data[field])
                except Exception as e:
                    logger.warning(f"Could not decrypt {field}: {str(e)}")
                    # Keep encrypted value if decryption fails
                    pass
        
        return decrypted_data

# Create global instance
token_encryption = TokenEncryption() 