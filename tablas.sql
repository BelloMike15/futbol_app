----Nombre de la database : futbol_gestion


-- Tabla: equipos
CREATE TABLE equipos (
    id_equipo SERIAL PRIMARY KEY,
    nombre_equipo VARCHAR(100) NOT NULL,
    pais VARCHAR(50) NOT NULL,
    estadio VARCHAR(100)
);

-- Tabla: jugadores
CREATE TABLE jugadores (
    id_jugador SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    edad INT CHECK (edad >= 15 AND edad <= 50),
    nacionalidad VARCHAR(50),
    posicion VARCHAR(30),
    id_equipo INT REFERENCES equipos(id_equipo) ON DELETE SET NULL
);

-- Tabla: partidos
CREATE TABLE partidos (
    id_partido SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    equipo_local INT REFERENCES equipos(id_equipo) ON DELETE CASCADE,
    equipo_visitante INT REFERENCES equipos(id_equipo) ON DELETE CASCADE,
    marcador_local INT DEFAULT 0,
    marcador_visitante INT DEFAULT 0
);

-- Tabla: estadisticas
CREATE TABLE estadisticas (
    id_estadistica SERIAL PRIMARY KEY,
    id_jugador INT REFERENCES jugadores(id_jugador) ON DELETE CASCADE,
    id_partido INT REFERENCES partidos(id_partido) ON DELETE CASCADE,
    goles INT DEFAULT 0,
    asistencias INT DEFAULT 0,
    minutos_jugados INT CHECK (minutos_jugados >= 0)
);

-- Tabla: usuarios
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasena TEXT NOT NULL,
    rol VARCHAR(20) CHECK (rol IN ('admin', 'usuario', 'invitado')) NOT NULL
);

-- Tabla: bitacora
CREATE TABLE bitacora (
    id_bitacora SERIAL PRIMARY KEY,
    usuario VARCHAR(50),
    hora_ingreso TIMESTAMP,
    hora_salida TIMESTAMP,
    navegador VARCHAR(100),
    ip VARCHAR(50),
    nombre_maquina VARCHAR(100),
    tabla_afectada VARCHAR(50),
    tipo_accion VARCHAR(20),
    descripcion TEXT
);


-- Rol con todos los privilegios
CREATE ROLE rol_admin LOGIN PASSWORD 'admin123';

-- Rol para usuarios normales (lectura y escritura limitada)
CREATE ROLE rol_usuario LOGIN PASSWORD 'usuario123';

-- Rol para invitados (solo lectura)
CREATE ROLE rol_invitado LOGIN PASSWORD 'invitado123';


-- asignar permisos a los roles 
-- rol admin 
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rol_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rol_admin;



-- rol usuario 

-- Permitir leer y modificar sus propios datos (sin ver bitácora)
GRANT SELECT, INSERT, UPDATE ON jugadores, estadisticas TO rol_usuario;
GRANT SELECT ON equipos, partidos TO rol_usuario;


-- rol invitado 
GRANT SELECT ON jugadores, equipos, partidos TO rol_invitado;

--- restringir acceso 
REVOKE ALL ON bitacora FROM PUBLIC;
GRANT ALL ON bitacora TO rol_admin;


-- Crear usuario asociado a rol
CREATE USER admin1 WITH PASSWORD 'admin1pass' IN ROLE rol_admin;
CREATE USER user1 WITH PASSWORD 'user1pass' IN ROLE rol_usuario;
CREATE USER invitado1 WITH PASSWORD 'invitado1pass' IN ROLE rol_invitado;

insert into usuarios (nombre_usuario, contrasena, rol) VALUES
('Kevin', '123', 'admin'),
('Diego', '123', 'usuario'),
('Mike', '123', 'invitado');

🔹 📊 REPORTE 1: Estadísticas de Jugadores por Partido
Objetivo: Mostrar cuántos goles, asistencias y minutos jugó cada jugador por partido.

🧠 JOIN: jugadores + estadisticas + partidos

SELECT
    j.nombre AS jugador,
    e.nombre_equipo AS equipo,
    p.fecha AS fecha_partido,
    p.equipo_local,
    p.equipo_visitante,
    est.goles,
    est.asistencias,
    est.minutos_jugados
FROM estadisticas est
JOIN jugadores j ON est.id_jugador = j.id_jugador
LEFT JOIN equipos e ON j.id_equipo = e.id_equipo
JOIN partidos p ON est.id_partido = p.id_partido
ORDER BY p.fecha DESC;


🔹 📊 REPORTE 2: Resultados de Partidos con Nombres de Equipos
Objetivo: Mostrar partidos con los nombres de los equipos, no solo sus IDs.

🧠 JOIN: partidos + equipos (2 veces)

SELECT
    p.fecha,
    el.nombre_equipo AS equipo_local,
    ev.nombre_equipo AS equipo_visitante,
    p.marcador_local,
    p.marcador_visitante
FROM partidos p
JOIN equipos el ON p.equipo_local = el.id_equipo
JOIN equipos ev ON p.equipo_visitante = ev.id_equipo
ORDER BY p.fecha DESC;



✅ 1. Crear la FUNCIÓN para insertar en la bitácora
CREATE OR REPLACE FUNCTION registrar_bitacora()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO bitacora (
        usuario,
        hora_ingreso,
        navegador,
        ip,
        nombre_maquina,
        tabla_afectada,
        tipo_accion,
        descripcion
    ) VALUES (
        current_user,
        current_timestamp,
        'Desconocido',  -- Esto se puede llenar desde el frontend
        inet_client_addr(),
        inet_client_hostname(),
        TG_TABLE_NAME,
        TG_OP,
        CASE 
            WHEN TG_OP = 'INSERT' THEN 'Nuevo registro insertado.'
            WHEN TG_OP = 'UPDATE' THEN 'Registro actualizado.'
            WHEN TG_OP = 'DELETE' THEN 'Registro eliminado.'
            ELSE 'Acción desconocida.'
        END
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM public.bitacora
ORDER BY id_bitacora ASC 

✅ 2. Crear TRIGGERS en tablas clave
Jugadores
CREATE TRIGGER trigger_jugadores
AFTER INSERT OR UPDATE OR DELETE ON jugadores
FOR EACH ROW
EXECUTE FUNCTION registrar_bitacora();

Estadísticas
CREATE TRIGGER trigger_estadisticas
AFTER INSERT OR UPDATE OR DELETE ON estadisticas
FOR EACH ROW
EXECUTE FUNCTION registrar_bitacora();

Equipos (opcional)
CREATE TRIGGER trigger_equipos
AFTER INSERT OR UPDATE OR DELETE ON equipos
FOR EACH ROW
EXECUTE FUNCTION registrar_bitacora();



INSERT INTO equipos (nombre_equipo, pais, estadio) VALUES
('FC Barcelona', 'España', 'Camp Nou'),
('Real Madrid', 'España', 'Santiago Bernabéu'),
('Manchester City', 'Inglaterra', 'Etihad Stadium');





INSERT INTO jugadores (nombre, edad, nacionalidad, posicion, id_equipo) VALUES
('Lionel Messi', 36, 'Argentina', 'Delantero', 4),
('Karim Benzema', 35, 'Francia', 'Delantero', 2),
('Kevin De Bruyne', 32, 'Bélgica', 'Centrocampista', 3);


INSERT INTO partidos (fecha, equipo_local, equipo_visitante, marcador_local, marcador_visitante) VALUES
('2024-06-01', 10, 11, 3, 2),  -- PSG vs Boca
('2024-06-05', 12, 13, 5, 1);  -- Liverpool vs Juventus


INSERT INTO estadisticas (id_jugador, id_partido, goles, asistencias, minutos_jugados) VALUES
(14, 5, 2, 1, 90),  -- Mbappé en partido 3
(16, 6, 10, 0, 78),  -- Cavani en partido 3
(17, 9, 1, 2, 88),  -- Salah en partido 4
(8, 10, 1, 0, 90);  -- Cristiano en partido 4

INSERT INTO usuarios (nombre_usuario, contrasena, rol) VALUES
('usuario1', 'user1pass', 'usuario'),
('invitado1', 'invitado1pass', 'invitado');


INSERT INTO equipos (nombre_equipo, pais, estadio) VALUES
('Paris Saint-Germain', 'Francia', 'Parc des Princes'),
('Boca Juniors', 'Argentina', 'La Bombonera'),
('Liverpool', 'Inglaterra', 'Anfield'),
('Juventus', 'Italia', 'Allianz Stadium');



INSERT INTO jugadores (nombre, edad, nacionalidad, posicion, id_equipo) VALUES
('Kylian Mbappé', 25, 'Francia', 'Delantero', 4),
('Edinson Cavani', 37, 'Uruguay', 'Delantero', 5),
('Mohamed Salah', 32, 'Egipto', 'Delantero', 6),
('Cristiano Ronaldo', 39, 'Portugal', 'Delantero', 7);



INSERT INTO partidos (fecha, equipo_local, equipo_visitante, marcador_local, marcador_visitante) VALUES
('2024-06-01', 10, 11, 3, 2),  -- PSG vs Boca
('2024-06-05', 12, 13, 5, 1);  -- Liverpool vs Juventus



INSERT INTO estadisticas (id_jugador, id_partido, goles, asistencias, minutos_jugados) VALUES
(4, 3, 2, 1, 90),  -- Mbappé en partido 3
(8, 3, 10, 0, 78),  -- Cavani en partido 3
(14, 4, 1, 2, 88),  -- Salah en partido 4
(12, 4, 1, 0, 90);  -- Cristiano en partido 4

select * from jugadores

INSERT INTO jugadores (nombre, edad, nacionalidad, posicion, id_equipo) VALUES
('Enner Valencia', 25, 'Ecuador', 'Delantero', 7),
('Carlos Gómez', 22, 'Colombia', 'Mediocampista', 9),
('Luis Martínez', 28, 'Perú', 'Defensa', 8),
('Marco Silva', 31, 'Brasil', 'Portero', 10),
('José Torres', 24, 'Chile', 'Delantero', 11),
('Ricardo León', 29, 'Argentina', 'Defensa', 12),
('Daniel Ramírez', 26, 'Uruguay', 'Mediocampista', 13),
('Pedro Aguilar', 27, 'Paraguay', 'Portero', 9),
('Mario Cedeño', 23, 'Ecuador', 'Delantero', 8),
('Esteban Ruiz', 30, 'Colombia', 'Defensa', 7),

('Andrés Bravo', 21, 'Perú', 'Mediocampista', 10),
('Sebastián Herrera', 22, 'Venezuela', 'Portero', 11),
('Gabriel Suárez', 24, 'Ecuador', 'Delantero', 13),
('Felipe Castro', 25, 'Chile', 'Defensa', 7),
('Matías Molina', 28, 'Argentina', 'Mediocampista',8),
('Cristian Narváez', 29, 'Uruguay', 'Portero', 9),
('Oscar Delgado', 23, 'Colombia', 'Delantero', 10),
('Hugo Vera', 26, 'Paraguay', 'Defensa', 11),
('David Romero', 27, 'Perú', 'Mediocampista', 11),
('Jonathan Ibarra', 30, 'Ecuador', 'Portero', 12),

('Kevin Mena', 24, 'Colombia', 'Delantero', 12),
('Francisco Paredes', 22, 'Chile', 'Defensa', 13),
('Javier Acosta', 28, 'Argentina', 'Mediocampista',9),
('Alfredo Mejía', 31, 'Honduras', 'Portero', 9),
('Milton Ríos', 25, 'Ecuador', 'Delantero', 10),
('René Sánchez', 27, 'Venezuela', 'Defensa', 12),
('César Bustos', 23, 'Perú', 'Mediocampista', 13),
('Iván Zamora', 26, 'Chile', 'Portero', 9),
('Damián Pérez', 24, 'Paraguay', 'Delantero', 12),
('Luciano Rivas', 29, 'Argentina', 'Defensa', 13);

select * from jugadores 
select * from partidos
select * from estadisticas
select * from equipos
select * from bitacora
select * from usuarios


-- TABLAS NUEVAS 

-- 🔹 Tabla 7: ENTRENADORES
CREATE TABLE entrenadores (
    id_entrenador SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nacionalidad VARCHAR(50),
    edad INT CHECK (edad >= 30 AND edad <= 70),
    id_equipo INT REFERENCES equipos(id_equipo) ON DELETE SET NULL
);

-- 🔹 Tabla 8: SANCIONES
CREATE TABLE sanciones (
    id_sancion SERIAL PRIMARY KEY,
    id_jugador INT NOT NULL REFERENCES jugadores(id_jugador) ON DELETE CASCADE,
    id_partido INT NOT NULL REFERENCES partidos(id_partido) ON DELETE CASCADE,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('Amarilla', 'Roja', 'Suspensión')),
    minuto INT CHECK (minuto >= 0 AND minuto <= 120),
    observacion TEXT
);

-- 🔹 Tabla 9: TORNEOS
CREATE TABLE torneos (
    id_torneo SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    año INT NOT NULL CHECK (año >= 1900),
    categoria VARCHAR(50) NOT NULL
);

-- ⚠️ Modificación necesaria a la tabla PARTIDOS para relacionar con TORNEOS
ALTER TABLE partidos
ADD COLUMN id_torneo INT REFERENCES torneos(id_torneo) ON DELETE SET NULL;

-- 🔹 Tabla 10: ASISTENCIAS POR PARTIDO
CREATE TABLE asistencias_partido (
    id_asistencia SERIAL PRIMARY KEY,
    id_partido INT NOT NULL REFERENCES partidos(id_partido) ON DELETE CASCADE,
    espectadores INT NOT NULL CHECK (espectadores >= 0),
    capacidad_estadio INT NOT NULL CHECK (capacidad_estadio >= 0),
    porcentaje_ocupacion NUMERIC GENERATED ALWAYS AS (
        espectadores * 100.0 / NULLIF(capacidad_estadio, 0)
    ) STORED
);


-- DATOS PARA TABLAS NUEVAS (recomendable borrar tablas y poner datos desde cero )
-- 1. EQUIPOS
INSERT INTO equipos (nombre_equipo, pais, estadio) VALUES
('Barcelona SC', 'Ecuador', 'Monumental'),
('Emelec', 'Ecuador', 'Capwell'),
('LDU Quito', 'Ecuador', 'Casa Blanca'),
('Independiente del Valle', 'Ecuador', 'Banco Guayaquil'),
('Deportivo Cuenca', 'Ecuador', 'Alejandro Serrano'),
('Aucas', 'Ecuador', 'Gonzalo Pozo Ripalda'),
('Macará', 'Ecuador', 'Bellavista'),
('Mushuc Runa', 'Ecuador', 'Echaleche'),
('El Nacional', 'Ecuador', 'Olímpico Atahualpa'),
('Orense', 'Ecuador', '9 de Mayo');

-- 2. JUGADORES
INSERT INTO jugadores (nombre, edad, nacionalidad, posicion, id_equipo) VALUES
('Carlos Tenorio', 34, 'Ecuador', 'Delantero', 1),
('Ángel Mena', 31, 'Ecuador', 'Volante', 2),
('Alexander Domínguez', 36, 'Ecuador', 'Arquero', 3),
('Junior Sornoza', 30, 'Ecuador', 'Volante', 4),
('Jhon Jairo Cifuente', 28, 'Ecuador', 'Delantero', 5),
('Lourdes Bermeo', 25, 'Ecuador', 'Defensa', 6),
('Enner Valencia', 35, 'Ecuador', 'Delantero', 1),
('Pedro Ortiz', 33, 'Ecuador', 'Arquero', 2),
('Franklin Guerra', 31, 'Ecuador', 'Defensa', 3),
('Moisés Caicedo', 23, 'Ecuador', 'Volante', 4);

-- 3. TORNEOS
INSERT INTO torneos (nombre, año, categoria) VALUES
('LigaPro Serie A', 2025, 'Primera División'),
('Copa Ecuador', 2025, 'Nacional'),
('Libertadores', 2025, 'Internacional'),
('Sudamericana', 2025, 'Internacional'),
('Torneo Clausura', 2025, 'Primera División'),
('Torneo Apertura', 2025, 'Primera División'),
('Supercopa Ecuador', 2025, 'Nacional'),
('Recopa', 2025, 'Internacional'),
('Campeonato Provincial', 2025, 'Regional'),
('Copa Juvenil', 2025, 'Formativas');

-- 4. PARTIDOS
INSERT INTO partidos (fecha, equipo_local, equipo_visitante, marcador_local, marcador_visitante, id_torneo) VALUES
('2025-08-01', 1, 2, 2, 1, 1),
('2025-08-02', 3, 4, 0, 0, 1),
('2025-08-03', 5, 6, 1, 2, 2),
('2025-08-04', 7, 8, 3, 1, 2),
('2025-08-05', 9, 10, 0, 1, 3),
('2025-08-06', 1, 3, 2, 2, 1),
('2025-08-07', 2, 4, 1, 1, 4),
('2025-08-08', 5, 7, 0, 0, 5),
('2025-08-09', 6, 9, 2, 3, 6),
('2025-08-10', 10, 8, 1, 0, 7);

-- 5. ESTADISTICAS
INSERT INTO estadisticas (id_jugador, id_partido, goles, asistencias, minutos_jugados) VALUES
(1, 1, 1, 0, 90),
(2, 1, 1, 1, 85),
(3, 2, 0, 0, 90),
(4, 2, 0, 1, 80),
(5, 3, 1, 0, 75),
(6, 3, 0, 0, 90),
(7, 6, 2, 0, 90),
(8, 6, 0, 1, 90),
(9, 7, 1, 0, 90),
(10, 7, 0, 2, 88);

-- 6. USUARIOS
INSERT INTO usuarios (nombre_usuario, contrasena, rol) VALUES
('Admin','admin123', 'admin'),
('Usuario1','u123', 'usuario'),
('Usuario2', 'u123', 'usuario'),
('Invitado1', 'i123', 'invitado'),
('Invitado2', 'i123', 'invitado'),
('Moderador', 'mod123', 'admin'),
('Scout1', 's123', 'usuario'),
('JugadorX', 'j123', 'usuario'),
('EntrenadorZ', 'e123', 'usuario'),
('Prensa', 'p123', 'invitado');

-- 7. BITACORA
INSERT INTO bitacora (usuario, hora_ingreso, hora_salida, navegador, ip, nombre_maquina, tabla_afectada, tipo_accion, descripcion) VALUES
('Admin', now(), now(), 'Chrome', '192.168.1.10', 'PC-Admin', 'jugadores', 'INSERT', 'Registro de Carlos Tenorio'),
('Admin', now(), now(), 'Chrome', '192.168.1.10', 'PC-Admin', 'equipos', 'INSERT', 'Registro de Barcelona SC'),
('Usuario1', now(), now(), 'Firefox', '192.168.1.15', 'Laptop-User', 'partidos', 'SELECT', 'Consulta de partidos 2025'),
('Usuario2', now(), now(), 'Edge', '192.168.1.25', 'PC-Lab', 'estadisticas', 'UPDATE', 'Actualización de goles'),
('Invitado1', now(), now(), 'Chrome', '192.168.1.30', 'Tablet', 'equipos', 'SELECT', 'Visualización de equipos'),
('Admin', now(), now(), 'Firefox', '192.168.1.11', 'PC-Admin2', 'bitacora', 'SELECT', 'Auditoría del sistema'),
('Scout1', now(), now(), 'Safari', '192.168.1.50', 'Macbook', 'jugadores', 'SELECT', 'Revisión de jugadores'),
('EntrenadorZ', now(), now(), 'Opera', '192.168.1.100', 'PC-Oficina', 'estadisticas', 'INSERT', 'Nuevo rendimiento'),
('Admin', now(), now(), 'Chrome', '192.168.1.10', 'PC-Admin', 'usuarios', 'INSERT', 'Registro de Scout1'),
('Usuario1', now(), now(), 'Edge', '192.168.1.15', 'Laptop-User', 'partidos', 'DELETE', 'Eliminación de partido prueba');

-- 8. ENTRENADORES
INSERT INTO entrenadores (nombre, nacionalidad, edad, id_equipo) VALUES
('Fabián Bustos', 'Argentina', 52, 1),
('Miguel Rondelli', 'Argentina', 45, 2),
('Luis Zubeldía', 'Argentina', 50, 3),
('Martín Anselmi', 'Argentina', 42, 4),
('Gabriel Schürrer', 'Argentina', 47, 5),
('César Farías', 'Venezuela', 49, 6),
('Alex Aguinaga', 'Ecuador', 53, 7),
('Geovanny Cumbicus', 'Ecuador', 41, 8),
('Ever Hugo Almeida', 'Paraguay', 70, 9),
('Andrés García', 'España', 38, 10);

-- 9. SANCIONES
INSERT INTO sanciones (id_jugador, id_partido, tipo, minuto, observacion) VALUES
(1, 1, 'Amarilla', 45, 'Falta por empujón'),
(2, 1, 'Roja', 88, 'Agresión directa'),
(3, 2, 'Amarilla', 60, 'Demora en saque'),
(4, 2, 'Suspensión', 0, 'Acumulación de tarjetas'),
(5, 3, 'Amarilla', 30, 'Juego peligroso'),
(6, 3, 'Roja', 70, 'Entrada desleal'),
(7, 6, 'Amarilla', 15, 'Mano intencional'),
(8, 6, 'Amarilla', 55, 'Simulación'),
(9, 7, 'Roja', 90, 'Insultos al árbitro'),
(10, 7, 'Amarilla', 78, 'Protesta reiterada');

-- 10. ASISTENCIAS POR PARTIDO
INSERT INTO asistencias_partido (id_partido, espectadores, capacidad_estadio) VALUES
(1, 35000, 50000),
(2, 22000, 40000),
(3, 15000, 25000),
(4, 8000, 20000),
(5, 17000, 30000),
(6, 28000, 50000),
(7, 30000, 40000),
(8, 5000, 15000),
(9, 14000, 18000),
(10, 19000, 25000);

select * from jugadores 
select * from partidos
select * from estadisticas
select * from equipos
select * from bitacora
select * from usuarios
select * from entrenadores
select * from sanciones
select * from asistencias_partido
select * from torneos 


--🔹 1. registrar_jugador(nombre, edad, nacionalidad, posicion, equipo_id)
--     Inserta un nuevo jugador y registra en la bitácora automáticamente.

CREATE OR REPLACE PROCEDURE registrar_jugador(
    IN nombre VARCHAR,
    IN edad INT,
    IN nacionalidad VARCHAR,
    IN posicion VARCHAR,
    IN equipo_id INT,
    IN usuario VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO jugadores(nombre, edad, nacionalidad, posicion, id_equipo)
    VALUES (nombre, edad, nacionalidad, posicion, equipo_id);

    INSERT INTO bitacora(usuario, hora_ingreso, hora_salida, navegador, ip, nombre_maquina, tabla_afectada, tipo_accion, descripcion)
    VALUES (usuario, now(), now(), 'Desconocido', '127.0.0.1', 'Servidor', 'jugadores', 'INSERT', 'Registro desde procedimiento');
END;
$$;



--🔹 2. actualizar_marcador(partido_id, local, visitante)
--Actualiza el marcador de un partido y guarda un registro en bitácora.

CREATE OR REPLACE PROCEDURE actualizar_marcador(
    IN partido_id INT,
    IN marcador_local INT,
    IN marcador_visitante INT,
    IN usuario VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE partidos
    SET marcador_local = marcador_local,
        marcador_visitante = marcador_visitante
    WHERE id_partido = partido_id;

    INSERT INTO bitacora(usuario, hora_ingreso, hora_salida, navegador, ip, nombre_maquina, tabla_afectada, tipo_accion, descripcion)
    VALUES (usuario, now(), now(), 'Desconocido', '127.0.0.1', 'Servidor', 'partidos', 'UPDATE', 'Actualización de marcador');
END;
$$;



--🔹 3. consultar_estadisticas_jugador(jugador_id, OUT goles INT, OUT asistencias INT)
--    Devuelve los goles y asistencias totales de un jugador.

CREATE OR REPLACE PROCEDURE consultar_estadisticas_jugador(
    IN jugador_id INT,
    OUT goles INT,
    OUT asistencias INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT COALESCE(SUM(e.goles), 0), COALESCE(SUM(e.asistencias), 0)
    INTO goles, asistencias
    FROM estadisticas e
    WHERE e.id_jugador = jugador_id;
END;
$$;


--🔹 4. registrar_sancion(jugador_id, partido_id, tipo, minuto, observacion)
--Agrega una sanción al jugador en un partido.

CREATE OR REPLACE PROCEDURE registrar_sancion(
    IN jugador_id INT,
    IN partido_id INT,
    IN tipo VARCHAR,
    IN minuto INT,
    IN observacion TEXT,
    IN usuario VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO sanciones(id_jugador, id_partido, tipo, minuto, observacion)
    VALUES (jugador_id, partido_id, tipo, minuto, observacion);

    INSERT INTO bitacora(usuario, hora_ingreso, hora_salida, navegador, ip, nombre_maquina, tabla_afectada, tipo_accion, descripcion)
    VALUES (usuario, now(), now(), 'Desconocido', '127.0.0.1', 'Servidor', 'sanciones', 'INSERT', 'Registro de sanción desde procedimiento');
END;
$$;


-- LO LLAMAMOS DE ESTA MANERA

--🔹 Registrar nuevo jugador:

CALL registrar_jugador('Jefferson Montero', 32, 'Ecuador', 'Volante', 1, 'Admin');

--🔹 Actualizar marcador:

CALL actualizar_marcador(1, 3, 2, 'Usuario1');

--🔹 Consultar estadísticas:

CALL consultar_estadisticas_jugador(1, NULL, NULL);
-- Revisa el resultado en el panel de "Messages" de pgAdmin


--🔹 Registrar sanción:

CALL registrar_sancion(2, 1, 'Amarilla', 34, 'Mano dentro del área', 'Usuario2');





-- ================================
-- 🔹 TRIGGER 1: Registrar en bitácora al insertar un jugador
-- ================================

-- Función para insertar en bitácora automáticamente al registrar un jugador
CREATE OR REPLACE FUNCTION log_insert_jugador()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO bitacora(
    usuario,
    hora_ingreso,
    hora_salida,
    navegador,
    ip,
    nombre_maquina,
    tabla_afectada,
    tipo_accion,
    descripcion
  )
  VALUES (
    current_user,
    now(),
    now(),
    'Desconocido',
    '127.0.0.1',
    'Servidor',
    'jugadores',
    'INSERT',
    CONCAT('Se insertó jugador: ', NEW.nombre)
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear el trigger que ejecuta la función anterior
CREATE TRIGGER trg_insert_jugador
AFTER INSERT ON jugadores
FOR EACH ROW
EXECUTE FUNCTION log_insert_jugador();

-- ================================
-- 🔹 TRIGGER 2: Validar edad antes de insertar o actualizar jugador
-- ================================

-- Función para validar edad permitida entre 15 y 50 años
CREATE OR REPLACE FUNCTION validar_edad_jugador()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.edad < 15 OR NEW.edad > 50 THEN
    RAISE EXCEPTION 'Edad inválida: debe estar entre 15 y 50 años';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear trigger que aplica la validación antes de insertar o actualizar
CREATE TRIGGER trg_validar_edad
BEFORE INSERT OR UPDATE ON jugadores
FOR EACH ROW
EXECUTE FUNCTION validar_edad_jugador();

-- ================================
-- 🔹 TRIGGER 3: Registrar en bitácora cuando se actualiza el marcador de un partido
-- ================================

-- Función para registrar en bitácora los cambios de marcador
CREATE OR REPLACE FUNCTION log_update_marcador()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO bitacora(
    usuario,
    hora_ingreso,
    hora_salida,
    navegador,
    ip,
    nombre_maquina,
    tabla_afectada,
    tipo_accion,
    descripcion
  )
  VALUES (
    current_user,
    now(),
    now(),
    'Desconocido',
    '127.0.0.1',
    'Servidor',
    'partidos',
    'UPDATE',
    CONCAT('Marcador actualizado de ', OLD.marcador_local, '-', OLD.marcador_visitante,
           ' a ', NEW.marcador_local, '-', NEW.marcador_visitante)
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para capturar los cambios en los marcadores
CREATE TRIGGER trg_update_marcador
AFTER UPDATE ON partidos
FOR EACH ROW
WHEN (
  OLD.marcador_local IS DISTINCT FROM NEW.marcador_local OR
  OLD.marcador_visitante IS DISTINCT FROM NEW.marcador_visitante
)
EXECUTE FUNCTION log_update_marcador();

-- ================================
-- 🔹 TRIGGER 4: Evitar sanciones duplicadas en el mismo partido
-- ================================

-- Función que verifica si ya existe una sanción similar
CREATE OR REPLACE FUNCTION evitar_sancion_duplicada()
RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM sanciones
    WHERE id_jugador = NEW.id_jugador
      AND id_partido = NEW.id_partido
      AND tipo = NEW.tipo
  ) THEN
    RAISE EXCEPTION 'El jugador ya tiene esta sanción en este partido';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger que ejecuta la validación antes de insertar
CREATE TRIGGER trg_sancion_duplicada
BEFORE INSERT ON sanciones
FOR EACH ROW
EXECUTE FUNCTION evitar_sancion_duplicada();



-- COMO PROBRAS LOS TRIGGERS

-- 🔹 Insertar un nuevo jugador para probar el trigger de bitácora
INSERT INTO jugadores (nombre, edad, nacionalidad, posicion, id_equipo)
VALUES ('Michael Estrada', 28, 'Ecuador', 'Delantero', 1);


-- 🔹 Actualizar el marcador de un partido para probar el trigger de bitácora
UPDATE partidos SET marcador_local = 4, marcador_visitante = 2 WHERE id_partido = 1;

-- 🔹 Intentar insertar una sanción duplicada para probar el trigger de validación
INSERT INTO sanciones (id_jugador, id_partido, tipo, minuto, observacion)
VALUES (1, 1, 'Amarilla', 45, 'Repetida');

-- 🔹 Insertar una sanción válida para probar el trigger de bitácora
INSERT INTO sanciones (id_jugador, id_partido, tipo, minuto, observacion)
VALUES (2, 1, 'Roja', 60, 'Falta grave');


-- 🔹 Intentar insertar un jugador con edad inválida para probar el trigger de validación
INSERT INTO jugadores (nombre, edad, nacionalidad, posicion, id_equipo)
VALUES ('Jugador Prohibido', 10, 'Ecuador', 'Delantero', 1);



--3 VISTAS ÚTILES 



-- VISTA 1: vista_estadisticas_jugadores

-- Esta vista muestra un resumen del rendimiento de cada jugador:
-- incluye su equipo, total de goles, asistencias y minutos jugados.

CREATE OR REPLACE VIEW vista_estadisticas_jugadores AS
SELECT 
    j.id_jugador,
    j.nombre AS jugador,
    e.nombre_equipo AS equipo,
    SUM(es.goles) AS total_goles,
    SUM(es.asistencias) AS total_asistencias,
    SUM(es.minutos_jugados) AS total_minutos
FROM jugadores j
LEFT JOIN equipos e ON j.id_equipo = e.id_equipo
LEFT JOIN estadisticas es ON j.id_jugador = es.id_jugador
GROUP BY j.id_jugador, j.nombre, e.nombre_equipo
ORDER BY total_goles DESC;

-- USO:
SELECT * FROM vista_estadisticas_jugadores;


-- VISTA 2: vista_partidos_completos
-- Muestra una lista de partidos con nombres de equipos y torneo.
-- Ideal para reportes de juegos, resultados y competencias.

CREATE OR REPLACE VIEW vista_partidos_completos AS
SELECT 
    p.id_partido,
    p.fecha,
    el.nombre_equipo AS equipo_local,
    ev.nombre_equipo AS equipo_visitante,
    p.marcador_local,
    p.marcador_visitante,
    t.nombre AS torneo,
    t.año
FROM partidos p
JOIN equipos el ON p.equipo_local = el.id_equipo
JOIN equipos ev ON p.equipo_visitante = ev.id_equipo
LEFT JOIN torneos t ON p.id_torneo = t.id_torneo
ORDER BY p.fecha DESC;

-- USO:
SELECT * FROM vista_partidos_completos;


-- VISTA 3: vista_sanciones_jugadores
-- Muestra las sanciones recibidas por los jugadores en partidos.
-- Incluye tipo, minuto, fecha y observaciones.

CREATE OR REPLACE VIEW vista_sanciones_jugadores AS
SELECT 
    s.id_sancion,
    j.nombre AS jugador,
    eq.nombre_equipo AS equipo,
    p.fecha,
    s.tipo,
    s.minuto,
    s.observacion
FROM sanciones s
JOIN jugadores j ON s.id_jugador = j.id_jugador
LEFT JOIN equipos eq ON j.id_equipo = eq.id_equipo
JOIN partidos p ON s.id_partido = p.id_partido
ORDER BY p.fecha DESC, s.tipo;

-- USO:
-SELECT * FROM vista_sanciones_jugadores;
