# -*- coding: utf-8 -*-
'''
@author: LeoGU
'''
import getpass as gp
from cryptography.fernet import Fernet

def encripta(texto, key):
    f = Fernet(key)
    return f.encrypt(texto.encode())

if __name__ == '__main__':
    crypt = b'0slta8tBUADjm2Gmot4psNhupGWrN03OkeFirEIsnFY='
    f = open("connectionDjangoDev.txt","w+")
    print(".::| Favor de llenar proporcionar los datos de conexion a la base de datos |::.\n")
    SID = input("SID/Service Name --> ")
    HOST = input("HOST --> ")
    PORT = input("PORT --> ")
    USER = input("USER/SCHEMA --> ")
    PASS = gp.getpass()
    data = [SID,HOST,PORT,USER,PASS]
    f.write(str(crypt.decode()) + "*##@@##*")
    for d in data:
        f.write(str(encripta(d,crypt).decode()) + "*##@@##*")
    f.close()