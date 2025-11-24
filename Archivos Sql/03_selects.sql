USE gestion_salas;

-- 1) Salas más reservadas
SELECT sala.nombre_sala, COUNT(reserva.id_reserva) AS total_reservas
FROM sala
LEFT JOIN reserva ON sala.id_sala = reserva.id_sala
GROUP BY sala.id_sala
ORDER BY total_reservas DESC;

-- 2) Turnos más demandados
SELECT turno.hora_inicio, turno.hora_fin, COUNT(reserva.id_reserva) AS total_reservas
FROM turno
LEFT JOIN reserva ON turno.id_turno = reserva.id_turno
GROUP BY turno.id_turno
ORDER BY total_reservas DESC;

-- 3) Promedio de participantes por sala
SELECT sala.nombre_sala,
       ROUND(AVG(sub.cantidad_participantes), 2) AS promedio_participantes
FROM sala
LEFT JOIN (
    SELECT reserva.id_sala, COUNT(reserva_participante.ci_participante) AS cantidad_participantes
    FROM reserva
    LEFT JOIN reserva_participante ON reserva.id_reserva = reserva_participante.id_reserva
    GROUP BY reserva.id_reserva
) AS sub ON sala.id_sala = sub.id_sala
GROUP BY sala.id_sala;

-- 4) Cantidad de reservas por carrera (programa) y facultad
SELECT facultad.nombre AS facultad,
       programa_academico.nombre_programa,
       COUNT(reserva.id_reserva) AS total_reservas
FROM facultad
JOIN programa_academico ON facultad.id_facultad = programa_academico.id_facultad
LEFT JOIN participante_programa_academico
       ON programa_academico.id_programa = participante_programa_academico.id_programa
LEFT JOIN reserva_participante
       ON participante_programa_academico.ci_participante = reserva_participante.ci_participante
LEFT JOIN reserva
       ON reserva_participante.id_reserva = reserva.id_reserva
GROUP BY facultad.id_facultad, programa_academico.id_programa
ORDER BY total_reservas DESC;

-- 5) Porcentaje de ocupación de salas por edificio
SELECT edificio.nombre_edificio,
       COUNT(reserva.id_reserva) AS reservas,
       COUNT(sala.id_sala) AS total_salas,
       ROUND(COUNT(reserva.id_reserva) / COUNT(sala.id_sala) * 100, 2) AS porcentaje_ocupacion
FROM edificio
LEFT JOIN sala ON edificio.id_edificio = sala.id_edificio
LEFT JOIN reserva ON sala.id_sala = reserva.id_sala
GROUP BY edificio.id_edificio;

-- 6) Cantidad de reservas y asistencias de profesores y alumnos
SELECT participante_programa_academico.rol,
       COUNT(reserva_participante.id_reserva) AS total_reservas,
       SUM(reserva_participante.asistencia) AS total_asistencias
FROM participante_programa_academico
LEFT JOIN reserva_participante
       ON participante_programa_academico.ci_participante = reserva_participante.ci_participante
GROUP BY participante_programa_academico.rol;

-- 7) Cantidad de sanciones para profesores y alumnos
SELECT participante_programa_academico.rol,
       COUNT(sancion_participante.id_sancion) AS total_sanciones
FROM participante_programa_academico
LEFT JOIN sancion_participante
       ON participante_programa_academico.ci_participante = sancion_participante.ci_participante
GROUP BY participante_programa_academico.rol;

-- 8) Porcentaje reservas utilizadas vs canceladas/no asistidas
SELECT
    (SELECT COUNT(*) FROM reserva WHERE estado = 'finalizada') AS reservas_utilizadas,
    (SELECT COUNT(*) FROM reserva WHERE estado IN ('cancelada', 'sin_asistencia')) AS reservas_no_utilizadas,
    ROUND(
        (SELECT COUNT(*) FROM reserva WHERE estado = 'finalizada') /
        (SELECT COUNT(*) FROM reserva) * 100, 2
    ) AS porcentaje_utilizacion;

-- Consulta extra 1) Total de reservas por día
SELECT fecha, COUNT(*) AS total_reservas
FROM reserva
GROUP BY fecha
ORDER BY fecha DESC;

-- Consulta extra 2) Salas con mayor capacidad
SELECT nombre_sala, capacidad
FROM sala
ORDER BY capacidad DESC;

-- Consulta extra 3) Cantidad de sanciones vs total de participantes
SELECT
    (SELECT COUNT(*) FROM participante) AS total_participantes,
    (SELECT COUNT(*) FROM sancion_participante) AS total_sanciones,
    ROUND(
        (SELECT COUNT(*) FROM sancion_participante) /
        (SELECT COUNT(*) FROM participante) * 100, 2
    ) AS porcentaje_participantes_sancionados;
