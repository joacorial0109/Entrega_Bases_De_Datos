USE gestion_salas;

-- Facultades
INSERT INTO facultad (nombre)
VALUES
('Ingeniería'),
('Ciencias Empresariales');

-- Programas académicos
INSERT INTO programa_academico (nombre_programa, id_facultad, tipo)
VALUES
('Ingeniería Informática', 1, 'grado'),
('Data Science', 1, 'posgrado'),
('Administración de Empresas', 2, 'grado');

-- Edificios
INSERT INTO edificio (nombre_edificio, direccion, departamento)
VALUES
('Edificio Central', 'Av. 8 de Octubre 2738', 'Montevideo'),
('Edificio Mulling', 'Comandante Braga 2745', 'Montevideo');

-- Salas
INSERT INTO sala (nombre_sala, id_edificio, capacidad, tipo_sala)
VALUES
('Sala 101', 1, 10, 'libre'),
('Sala 102', 1, 8, 'posgrado'),
('Sala 201', 2, 6, 'docente');

-- Turnos (de 8 a 23 hs)
INSERT INTO turno (hora_inicio, hora_fin) VALUES
('08:00:00', '09:00:00'),
('09:00:00', '10:00:00'),
('10:00:00', '11:00:00'),
('11:00:00', '12:00:00'),
('12:00:00', '13:00:00'),
('13:00:00', '14:00:00'),
('14:00:00', '15:00:00'),
('15:00:00', '16:00:00'),
('16:00:00', '17:00:00'),
('17:00:00', '18:00:00'),
('18:00:00', '19:00:00'),
('19:00:00', '20:00:00'),
('20:00:00', '21:00:00'),
('21:00:00', '22:00:00'),
('22:00:00', '23:00:00');

USE gestion_salas;

-- Logins
INSERT INTO login (correo, contrasena)
VALUES
('juan@ucu.edu.uy', '1234'),
('ana@ucu.edu.uy', 'abcd'),
('prof.silva@ucu.edu.uy', 'pass123');

-- Participantes
INSERT INTO participante (ci, nombre, apellido, email, id_login)
VALUES
('12345678', 'Juan', 'Pérez', 'juan@ucu.edu.uy', 1),
('87654321', 'Ana', 'Rodríguez', 'ana@ucu.edu.uy', 2),
('13245678', 'Carlos', 'Silva', 'prof.silva@ucu.edu.uy', 3);

-- Participante por programa
INSERT INTO participante_programa_academico (ci_participante, id_programa, rol)
VALUES
('12345678', 1, 'alumno'),
('87654321', 2, 'alumno'),
('13245678', 1, 'docente');


USE gestion_salas;

-- Reserva (Juan reserva la Sala 101 el 2025-10-31 a las 10)
INSERT INTO reserva (id_sala, fecha, id_turno, estado)
VALUES (1, '2025-10-31', 3, 'activa');

-- Participantes en esa reserva
INSERT INTO reserva_participante (id_reserva, ci_participante, asistencia)
VALUES
(1, '12345678', TRUE),    -- Juan fue
(1, '13245678', TRUE);    -- El profe Silva también

-- Sanción de prueba (Ana no asistió)
INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin)
VALUES ('87654321', '2025-11-01', '2026-01-01');
