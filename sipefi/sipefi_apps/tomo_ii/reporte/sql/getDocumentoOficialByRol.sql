SELECT COUNT(ID_PERFIL) from CATALOGO.TC_PERFIL
where ID_PERFIL = :id_perfil
and (NOMBRE_PERFIL like :str_validador
    OR NOMBRE_PERFIL like :str_administrador
    OR NOMBRE_PERFIL LIKE :str_coordinador)