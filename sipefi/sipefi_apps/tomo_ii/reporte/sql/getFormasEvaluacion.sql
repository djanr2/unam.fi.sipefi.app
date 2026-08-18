SELECT CASE
           WHEN EXISTS (
               SELECT 1
                 FROM SIPEFI.TD_REL_ASIG_EVALUACION formas
                 INNER JOIN SIPEFI.TD_SOLICITUD_TOMO_II s
                   ON s.ID_SOLICITUD = formas.ID_SOLICITUD
                  AND s.ID_ESTATUS_SOLICITUD = formas.ID_ESTATUS_SOLICITUD
                WHERE formas.ID_FORMA_EVAL = fe.ID_FORMA_EVAL
                  AND formas.ID_SOLICITUD = :id_asignatura
                  AND s.HISTORICA = 0
                  AND s.ID_ESTATUS_SOLICITUD <> 0
           ) THEN 1 ELSE 0
       END AS formas_evaluacion
  FROM CATALOGO.TC_FORMAS_EVALUACION fe
 WHERE fe.ID_FORMA_EVAL > 0
   AND fe.TIPO_EVALUACION = :id_forma_evaluacion
 ORDER BY fe.ID_FORMA_EVAL
