# -*- coding: utf-8 -*-
class SolicitudError(Exception):
    """Error funcional seguro para devolver al cliente sin exponer detalles internos."""

    def __init__(self, status_code, user_message):
        super().__init__(user_message)
        self.status_code = int(status_code)
        self.user_message = str(user_message)
