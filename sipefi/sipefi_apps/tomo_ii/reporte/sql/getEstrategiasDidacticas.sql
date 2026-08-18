SELECT CASE
           WHEN EXISTS (
               SELECT 1
                 FROM SIPEFI.TD_REL_ASIG_ESTRAT_DID sed
                 INNER JOIN SIPEFI.TD_SOLICITUD_TOMO_II s
                   ON s.ID_SOLICITUD = sed.ID_SOLICITUD
                  AND s.ID_ESTATUS_SOLICITUD = sed.ID_ESTATUS_SOLICITUD
                WHERE sed.ID_ESTRATEGIA_DIDACT = ed.ID_ESTRATEGIA_DIDACT
                  AND sed.ID_SOLICITUD = :id_asignatura
                  AND s.HISTORICA = 0
                  AND s.ID_ESTATUS_SOLICITUD <> 0
           ) THEN 1 ELSE 0
       END AS bool_estrategias_didacticas,
       ed.ESTRATEGIA_DIDACTICA
  FROM CATALOGO.TC_ESTRATEGIAS_DIDACTICAS ed
 WHERE ed.ID_ESTRATEGIA_DIDACT > 0
 ORDER BY ed.ID_ESTRATEGIA_DIDACT
