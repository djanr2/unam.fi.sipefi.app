select NUM_TEMA, NUM_CONTENIDO id_contenido, CONTENIDO
from SIPEFI.TD_CONTENIDO_TEMATICO
where ID_SOLICITUD = :id_asignatura
order by NUM_TEMA, id_contenido