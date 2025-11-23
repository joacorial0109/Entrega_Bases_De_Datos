USE gestion_salas;

---------------------------------------------------------
-- 1) FACULTAD
---------------------------------------------------------
INSERT INTO facultad (nombre) VALUES
('Ingeniería'),
('Ciencias Empresariales');

---------------------------------------------------------
-- 2) PROGRAMAS ACADÉMICOS
---------------------------------------------------------
INSERT INTO programa_academico (nombre_programa, id_facultad, tipo) VALUES
('Ingeniería Informática', 1, 'grado'),
('Data Science', 1, 'posgrado'),
('Administración de Empresas', 2, 'grado');

---------------------------------------------------------
-- 3) LOGIN (admin + usuarios reales)
---------------------------------------------------------
INSERT INTO login (usuario, contrasena) VALUES
('admin@ucu.edu.uy', 'admin123'),     -- ADMIN (sin participante)
('juan@ucu.edu.uy', '1234'),          -- Alumno grado
('ana@ucu.edu.uy', 'abcd'),           -- Alumna posgrado (sancionada)
('prof.silva@ucu.edu.uy', 'pass123'); -- Docente

---------------------------------------------------------
-- 4) PARTICIPANTES
---------------------------------------------------------
INSERT INTO participante (ci, nombre, apellido, email, id_login) VALUES
('12345678', 'Juan', 'Pérez', 'juan@ucu.edu.uy', 2),
('87654321', 'Ana', 'Rodríguez', 'ana@ucu.edu.uy', 3),
('13245678', 'Carlos', 'Silva', 'prof.silva@ucu.edu.uy', 4);

---------------------------------------------------------
-- 5) PARTICIPANTE x PROGRAMA
---------------------------------------------------------
INSERT INTO participante_programa_academico (ci_participante, id_programa, rol) VALUES
('12345678', 1, 'alumno'),  -- Ingeniería (grado)
('87654321', 2, 'alumno'),  -- Data Science (posgrado)
('13245678', 1, 'docente'); -- Docente de Ingeniería

---------------------------------------------------------
-- 6) EDIFICIOS
---------------------------------------------------------
INSERT INTO edificio (nombre_edificio, direccion, departamento) VALUES
('Edificio Central', 'Av. 8 de Octubre 2738', 'Montevideo'),
('Edificio Mulling', 'Comandante Braga 2745', 'Montevideo');

---------------------------------------------------------
-- 7) SALAS
---------------------------------------------------------
INSERT INTO sala (nombre_sala, id_edificio, capacidad, tipo_sala) VALUES
('Sala 101', 1, 10, 'libre'),
('Sala 102', 1, 8, 'posgrado'),
('Sala 201', 2, 6, 'docente');

---------------------------------------------------------
-- 8) TURNOS (08:00 a 23:00)
---------------------------------------------------------
INSERT INTO turno (hora_inicio, hora_fin) VALUES
('08:00:00','09:00:00'),
('09:00:00','10:00:00'),
('10:00:00','11:00:00'),
('11:00:00','12:00:00'),
('12:00:00','13:00:00'),
('13:00:00','14:00:00'),
('14:00:00','15:00:00'),
('15:00:00','16:00:00'),
('16:00:00','17:00:00'),
('17:00:00','18:00:00'),
('18:00:00','19:00:00'),
('19:00:00','20:00:00'),
('20:00:00','21:00:00'),
('21:00:00','22:00:00'),
('22:00:00','23:00:00');

---------------------------------------------------------
-- 9) RESERVA DE EJEMPLO
---------------------------------------------------------
INSERT INTO reserva (id_sala, fecha, id_turno, estado) VALUES
(1, '2025-10-31', 3, 'activa');  -- Sala 101, 10:00-11:00

---------------------------------------------------------
-- 10) PARTICIPANTES EN ESA RESERVA
---------------------------------------------------------
INSERT INTO reserva_participante (id_reserva, ci_participante, asistencia) VALUES
(1, '12345678', TRUE),    -- Juan fue
(1, '13245678', TRUE);    -- Docente Carlos fue

---------------------------------------------------------
-- 11) SANCIONES (Ana sancionada)
---------------------------------------------------------
INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin) VALUES
('87654321', '2025-11-01', '2026-01-01');
