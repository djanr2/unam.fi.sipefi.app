'''
@author: lguzmanu
'''
from django.db import connections

class ConexionBD(object):
    """
        Clase que ayuda a preparar las conexiones a las diferentes bases de datos disponibles o 
        que pueden ser usadas para el tratado de informacion
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """
            Funcion que ayuda a inicializar los cursores y guarda en sus caracteristicas de clase en un parametro.
        """
        if not cls._instance:
            cls._instance = super(ConexionBD, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def cursorBD(self):
        """
            Funcion que ayuda a crear el cursor que apunta a la base de datos de riesgos de credito.
            
            :return: Regresa cursor a la base de datos de riesgos de credito.
        """
        cursor = connections['default'].cursor()
        cursor.execute("alter session set nls_date_format = 'dd-mm-yy'")
        return cursor