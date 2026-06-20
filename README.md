# Pantalla 1 — Listado y Búsqueda de Clientes

Módulo de Clientes · Sistema Distribuido Sakila

Esta API es la única vía por la que se consultan y registran clientes.

## Instalación (una vez)
```
pip install -r requirements.txt
```

## Configurar credenciales
Crear el archivo `.env` con:
```
SUPABASE_URL=https://xvtkzpoecnmcfekihneo.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2dGt6cG9lY25tY2Zla2lobmVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NDc3NjMsImV4cCI6MjA5NTQyMzc2M30.iLpgcaiCTgkxybD3aNpDdo9H0o5-8ZfCZzsUQoR7haA
```

## Levantar la API
```
uvicorn api:app --reload --port 8001
```
Luego abrir: http://localhost:8001/docs

## Servicios que expone
- `GET /clientes` — lista/busca clientes (filtros: nombre, tienda, estado; con paginación)
- `GET /clientes/{id}` — obtiene un cliente por su ID
- `POST /clientes` — registra un cliente nuevo

## Estructura (arquitectura por capas)
```
clientes/
├── config.py        Conexión a Supabase (lee el .env)
├── modelos.py       Cliente, EstadoCliente, DatosNuevoCliente
├── excepciones.py   Errores del dominio
├── repositorio.py   Acceso a datos (consultas y registro)
└── servicio.py      Lógica de negocio + validaciones
api.py               La API REST (GET y POST)
```
