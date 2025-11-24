DROP DATABASE IF EXISTS gestion_salas;
CREATE DATABASE gestion_salas;
USE gestion_salas;

-- 1) FACULTAD
CREATE TABLE facultad (
    id_facultad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- 2) PROGRAMA ACADÉMICO
CREATE TABLE programa_academico (
    id_programa INT AUTO_INCREMENT PRIMARY KEY,
    nombre_programa VARCHAR(150) NOT NULL,
    id_facultad INT NOT NULL,
    tipo ENUM('grado','posgrado','otros') NOT NULL,

    FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- 3) LOGIN
CREATE TABLE login (
    id_login INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(100) NOT NULL
);

-- 4) PARTICIPANTE
CREATE TABLE participante (
    ci VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    id_login INT,

    FOREIGN KEY (id_login) REFERENCES login(id_login)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- 5) PARTICIPANTE x PROGRAMA
CREATE TABLE participante_programa_academico (
    ci_participante VARCHAR(20),
    id_programa INT,
    rol ENUM('alumno','docente') NOT NULL,

    PRIMARY KEY (ci_participante, id_programa),

    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
        ON DELETE CASCADE ON UPDATE CASCADE,

    FOREIGN KEY (id_programa) REFERENCES programa_academico(id_programa)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- 6) EDIFICIO
CREATE TABLE edificio (
    id_edificio INT AUTO_INCREMENT PRIMARY KEY,
    nombre_edificio VARCHAR(120) NOT NULL,
    direccion VARCHAR(200),
    departamento VARCHAR(100)
);

-- 7) SALA
CREATE TABLE sala (
    id_sala INT AUTO_INCREMENT PRIMARY KEY,
    nombre_sala VARCHAR(100) NOT NULL,
    id_edificio INT NOT NULL,
    capacidad INT NOT NULL,
    tipo_sala ENUM('libre','posgrado','docente') NOT NULL,

    FOREIGN KEY (id_edificio) REFERENCES edificio(id_edificio)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- 8) TURNO
CREATE TABLE turno (
    id_turno INT AUTO_INCREMENT PRIMARY KEY,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

-- 9) RESERVA
CREATE TABLE reserva (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_sala INT NOT NULL,
    fecha DATE NOT NULL,
    id_turno INT NOT NULL,
    estado ENUM('activa','cancelada','finalizada') DEFAULT 'activa',

    FOREIGN KEY (id_sala) REFERENCES sala(id_sala)
        ON DELETE CASCADE ON UPDATE CASCADE,

    FOREIGN KEY (id_turno) REFERENCES turno(id_turno)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- 10) RESERVA x PARTICIPANTE
CREATE TABLE reserva_participante (
    id_reserva INT,
    ci_participante VARCHAR(20),
    asistencia BOOLEAN DEFAULT FALSE,

    PRIMARY KEY (id_reserva, ci_participante),

    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
        ON DELETE CASCADE ON UPDATE CASCADE,

    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- 11) SANCIONES
CREATE TABLE sancion_participante (
    id_sancion INT AUTO_INCREMENT PRIMARY KEY,
    ci_participante VARCHAR(20) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,

    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
        ON DELETE CASCADE ON UPDATE CASCADE
);
