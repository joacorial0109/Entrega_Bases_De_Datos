CREATE DATABASE IF NOT EXISTS gestion_salas;
USE gestion_salas;

-- Tabla: facultad
CREATE TABLE facultad (
    id_facultad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla: programa_academico
CREATE TABLE programa_academico (
    id_programa INT AUTO_INCREMENT PRIMARY KEY,
    nombre_programa VARCHAR(120) NOT NULL,
    id_facultad INT NOT NULL,
    tipo ENUM('grado', 'posgrado') NOT NULL,
    CONSTRAINT fk_programa_facultad
        FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Tabla: edificio
CREATE TABLE edificio (
    id_edificio INT AUTO_INCREMENT PRIMARY KEY,
    nombre_edificio VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    departamento VARCHAR(100)
);

-- Tabla: sala
CREATE TABLE sala (
    id_sala INT AUTO_INCREMENT PRIMARY KEY,
    nombre_sala VARCHAR(100) NOT NULL,
    id_edificio INT NOT NULL,
    capacidad INT NOT NULL,
    tipo_sala ENUM('libre', 'posgrado', 'docente') NOT NULL,
    FOREIGN KEY (id_edificio) REFERENCES edificio(id_edificio)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Tabla: turno
CREATE TABLE turno (
    id_turno INT AUTO_INCREMENT PRIMARY KEY,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

USE gestion_salas;

-- Tabla: login
CREATE TABLE login (
    id_login INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contrasena VARCHAR(100) NOT NULL
);

-- Tabla: participante
CREATE TABLE participante (
    ci VARCHAR(15) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    id_login INT,
    FOREIGN KEY (id_login) REFERENCES login(id_login)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

-- Tabla: participante_programa_academico
CREATE TABLE participante_programa_academico (
    id_alumno_programa INT AUTO_INCREMENT PRIMARY KEY,
    ci_participante VARCHAR(15) NOT NULL,
    id_programa INT NOT NULL,
    rol ENUM('alumno', 'docente') NOT NULL,
    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (id_programa) REFERENCES programa_academico(id_programa)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

USE gestion_salas;

-- Tabla: reserva
CREATE TABLE reserva (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_sala INT NOT NULL,
    fecha DATE NOT NULL,
    id_turno INT NOT NULL,
    estado ENUM('activa', 'cancelada', 'sin_asistencia', 'finalizada') DEFAULT 'activa',
    FOREIGN KEY (id_sala) REFERENCES sala(id_sala)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (id_turno) REFERENCES turno(id_turno)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Tabla: reserva_participante
CREATE TABLE reserva_participante (
    id_reserva_participante INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva INT NOT NULL,
    ci_participante VARCHAR(15) NOT NULL,
    fecha_solicitud_reserva DATETIME DEFAULT CURRENT_TIMESTAMP,
    asistencia BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- Tabla: sancion_participante
CREATE TABLE sancion_participante (
    id_sancion INT AUTO_INCREMENT PRIMARY KEY,
    ci_participante VARCHAR(15) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);
