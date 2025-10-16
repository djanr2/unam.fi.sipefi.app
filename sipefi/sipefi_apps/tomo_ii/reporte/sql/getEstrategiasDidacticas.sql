SELECT CASE
           WHEN EXISTS (
               SELECT 1
               FROM SIPEFI.TD_REL_ASIG_ESTRAT_DID sed
               WHERE sed.ID_ESTRATEGIA_DIDACT = ed.ID_ESTRATEGIA_DIDACT
                 and sed.ID_SOLICITUD = :id_asignatura
           ) THEN 1 ELSE 0
           END AS bool_estrategias_didacticas,
            ed.ESTRATEGIA_DIDACTICA

FROM CATALOGO.TC_ESTRATEGIAS_DIDACTICAS ed
where ed.ID_ESTRATEGIA_DIDACT > 0
order by ed.ID_ESTRATEGIA_DIDACT
