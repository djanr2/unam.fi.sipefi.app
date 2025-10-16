select
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM SIPEFI.TD_REL_ASIG_EVALUACION formas
            WHERE formas.ID_FORMA_EVAL = fe.ID_FORMA_EVAL
              and formas.ID_SOLICITUD = :id_asignatura
        ) THEN 1 ELSE 0
        END AS formas_evaluacion_diagnostica
FROM CATALOGO.TC_FORMAS_EVALUACION fe
where fe.ID_FORMA_EVAL > 0
  and TIPO_EVALUACION = :id_forma_evaluacion
order by fe.ID_FORMA_EVAL