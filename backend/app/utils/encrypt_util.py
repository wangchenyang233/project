from passlib.context import CryptContext
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import os
from flask import current_app

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AES加密函数
class AESCipher:
    def __init__(self, key=None):
        # 使用应用配置中的加密密钥，如果没有则使用默认密钥
        if key is None:
            key = current_app.config.get('ENCRYPT_SECRET_KEY', 'your-encrypt-secret-key-change-in-production')
        # 确保密钥长度为16、24或32字节
        self.key = key.encode('utf-8')[:32].ljust(32, b'\0')  # 32 bytes for AES-256
        self.block_size = AES.block_size
    
    def encrypt(self, data):
        data = data.encode('utf-8')
        iv = get_random_bytes(self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(data, self.block_size))
        return base64.b64encode(iv + ciphertext).decode('utf-8')
    
    def decrypt(self, data):
        data = base64.b64decode(data.encode('utf-8'))
        iv = data[:self.block_size]
        ciphertext = data[self.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), self.block_size)
        return plaintext.decode('utf-8')

# 密码加密函数
def encrypt_pwd(password):
    """使用bcrypt加密密码"""
    return pwd_context.hash(password)

# 密码验证函数
def verify_pwd(hashed_password, password):
    """验证密码是否正确"""
    return pwd_context.verify(password, hashed_password)

# 字符串加密函数
def encrypt_str(data):
    """使用AES加密敏感字符串"""
    cipher = AESCipher()
    return cipher.encrypt(data)

# 字符串解密函数
def decrypt_str(encrypted_data):
    """使用AES解密敏感字符串"""
    cipher = AESCipher()
    return cipher.decrypt(encrypted_data)
