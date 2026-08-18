# -*- coding: utf-8 -*-


class FormacionComplementariaError(Exception):
    """Error funcional seguro del módulo de Formación complementaria."""

    def __init__(self, status_code: int, user_message: str):
        super().__init__(user_message)
        self.status_code = int(status_code)
        self.user_message = str(user_message)
