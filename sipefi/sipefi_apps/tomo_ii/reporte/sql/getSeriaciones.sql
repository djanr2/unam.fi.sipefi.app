WITH ANTESEDENTE AS (select  LISTAGG(distinct a.ASIGNATURA, ', ') WITHIN GROUP (ORDER BY a.ASIGNATURA) as seriacion_antecedente
FROM SIPEFI.TD_ASIGNATURA a,
     SIPEFI.TD_REL_LIC_ASIGNATURA s
WHERE s.ID_LICENCIATURA = :id_licenciatura
and s.ID_SOLICITUD = :id_asignatura
and s.SERIACION_ANT = a.ID_ASIGNATURA),
    CONSECUENTE AS (select  LISTAGG(distinct a.ASIGNATURA, ', ') WITHIN GROUP (ORDER BY a.ASIGNATURA) as seriacion_consecuente
FROM SIPEFI.TD_ASIGNATURA a,
     SIPEFI.TD_REL_LIC_ASIGNATURA s
WHERE s.ID_LICENCIATURA = :id_licenciatura
and s.ID_SOLICITUD = :id_asignatura
and s.SERIACION_CONS = a.ID_ASIGNATURA)
SELECT a.seriacion_antecedente, c.seriacion_consecuente
from ANTESEDENTE a, CONSECUENTE c;