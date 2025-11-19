USE gestion_salas;


--Salas Mas Reservadas
SELECT s.nombre_sala, COUNT(*) AS cantidad_reservas
FROM reserva r
JOIN sala s ON r.id_sala = s.id_sala
GROUP BY s.nombre_sala
ORDER BY cantidad_reservas DESC;

--Turnos Mas Demandados
SELECT t.hora_inicio, t.hora_fin, COUNT(*) AS cantidad_reservas
FROM reserva r
JOIN turno t ON r.id_turno = t.id_turno
GROUP BY t.hora_inicio, t.hora_fin
ORDER BY cantidad_reservas DESC;

--Promedios de Participantes
SELECT s.nombre_sala, ROUND(AVG(sub.cantidad_participantes), 2) AS promedio_participantes
FROM (
    SELECT r.id_sala, COUNT(rp.ci_participante) AS cantidad_participantes
    FROM reserva r
    JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
    GROUP BY r.id_reserva
) sub
JOIN sala s ON sub.id_sala = s.id_sala
GROUP BY s.nombre_sala;

--Cantidad de reservas por carrera y facultad
SELECT pa.nombre_programa, f.nombre AS facultad, COUNT(*) AS cantidad_reservas
FROM reserva_participante rp
JOIN participante p ON rp.ci_participante = p.ci
JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
JOIN programa_academico pa ON ppa.id_programa = pa.id_programa
JOIN facultad f ON pa.id_facultad = f.id_facultad
GROUP BY pa.nombre_programa, f.nombre;


--Porcentaje de ocupación de salas por edificio
SELECT e.nombre_edificio,
       COUNT(DISTINCT r.id_reserva) AS reservas,
       COUNT(DISTINCT t.id_turno) * COUNT(DISTINCT r.fecha) AS posibles_turnos,
       ROUND(COUNT(DISTINCT r.id_reserva) * 100.0 /
             (COUNT(DISTINCT t.id_turno) * COUNT(DISTINCT r.fecha)), 2) AS porcentaje_ocupacion
FROM reserva r
JOIN sala s ON r.id_sala = s.id_sala
JOIN edificio e ON s.id_edificio = e.id_edificio
JOIN turno t ON r.id_turno = t.id_turno
GROUP BY e.nombre_edificio;


--Cantidad de reservas y asistencias de profesores y alumnos
SELECT ppa.rol, pa.tipo, COUNT(DISTINCT rp.id_reserva) AS reservas,
       SUM(CASE WHEN rp.asistencia = TRUE THEN 1 ELSE 0 END) AS asistencias
FROM reserva_participante rp
JOIN participante_programa_academico ppa ON rp.ci_participante = ppa.ci_participante
JOIN programa_academico pa ON ppa.id_programa = pa.id_programa
GROUP BY ppa.rol, pa.tipo;

--Cantidad de sanciones para profesores y alumnos
SELECT ppa.rol, COUNT(*) AS cantidad_sanciones
FROM sancion_participante sp
JOIN participante_programa_academico ppa ON sp.ci_participante = ppa.ci_participante
GROUP BY ppa.rol;

--Porcentaje de reservas efectivamente utilizadas vs canceladas/no asistidas
SELECT
    COUNT(*) AS total_reservas,
    SUM(CASE WHEN r.estado = 'activa' OR r.estado = 'finalizada' THEN 1 ELSE 0 END) AS utilizadas,
    SUM(CASE WHEN r.estado = 'cancelada' OR r.estado = 'sin_asistencia' THEN 1 ELSE 0 END) AS no_utilizadas,
    ROUND(SUM(CASE WHEN r.estado IN ('activa', 'finalizada') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS porcentaje_utilizadas
FROM reserva r;
