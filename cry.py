from pysmx.SM4 import Sm4, ENCRYPT, DECRYPT
from pysmx.SM3 import digest as SM3_pysmx
import binascii
import time
import os
from connect_mysql import MysqlManager
import datetime

# 填充成16字节倍数bytes
def pad(s: bytes) -> bytes:
    n = 16 - (len(s) & 0xf)
    return s + bytes([n] * n)


# 将填充后的bytes还原
def unpad(s: bytes) -> bytes:
    return s[0:-s[-1]]


def SM3(msg):    #输入字符串
    from pysmx.SM3 import SM3
    sm3 = SM3()
    sm3.update(msg)
    ciphertext = sm3.hexdigest()
    # print(ciphertext)
    return ciphertext

# pysmx - SM4加密器
class SM4_pysmx:
    def __init__(self, raw_key):
        key = SM3_pysmx(raw_key)
        self._enc = Sm4()
        self._enc.sm4_setkey(key, ENCRYPT)
        self._dec = Sm4()
        self._dec.sm4_setkey(key, DECRYPT)

    # SM4加密（ECB模式）
    def enc(self, data):
        return bytes(self._enc.sm4_crypt_ecb(pad(data)))

    # SM4解密（ECB模式）
    def dec(self, data):
        assert len(data) & 0xf == 0
        return unpad(bytes(self._dec.sm4_crypt_ecb(data)))

    # SM4加密（CBC模式）
    def enc_cbc(self, iv, data):
        assert len(iv) == 16
        return bytes(self._enc.sm4_crypt_cbc(iv, pad(data)))

    # SM4解密（CBC模式）
    def dec_cbc(self, iv, data):
        assert len(iv) == 16
        assert len(data) & 0xf == 0
        return unpad(bytes(self._dec.sm4_crypt_cbc(iv, data)))

def set_SM4_Key():
    KA = os.urandom(16)
    return KA
def set_SM4_iv():
    iv = os.urandom(16)
    return iv

def en_SM4(msg, KA,iv):
    sm4_smx = SM4_pysmx(KA)
    ciphertext = sm4_smx.enc_cbc(iv,msg)
    return ciphertext

def de_SM4(ciphertext,KA,iv):
    sm4_smx = SM4_pysmx(KA)
    plaintext = sm4_smx.dec_cbc(iv,ciphertext)
    return plaintext


def file_insert(keyword, file, IV, KEY):
    test1 = MysqlManager()
    test1.connect_db()
    # 对文件进行SM3哈希
    keyword = SM3(keyword)
    # 对文件进行SM4加密
    file = en_SM4(file.encode(),KEY,IV)
    file = binascii.b2a_hex(file).decode()
    # print(file)
    test1.insert_table1(keyword,test1.insert_table2(file))


def file_retrieval(keyword_list,IV,KEY):
    test1 = MysqlManager()
    test1.connect_db()
    keyword_hash_list = []
    for i in keyword_list:
        keyword_hash_list.append(SM3(i))
    start = datetime.datetime.now()
    ret_vector = test1.query_filevector(keyword_hash_list)
    ciphertext = test1.query_ciphertext(ret_vector)
    print("--------------------------------------------------------------")
    print(ciphertext)
    plaintext = []
    for i in ciphertext:
        c2 = binascii.a2b_hex(i)
        plaintext.append(de_SM4(c2,KEY,IV).decode())
    print(plaintext)
    print('查询文件为:',plaintext)
    end = datetime.datetime.now()
    print('时间开销:',end - start,'ms')

