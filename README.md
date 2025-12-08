# Secret Guardian

Secret Guardian es un sistema completo de escaneo y detección de secretos hardcodeados en repositorios de código. El proyecto implementa dos servicios principales: un escáner de secretos y una API para consultar los resultados.


## Descripción General

Secret Guardian es una herramienta de seguridad que escanea repositorios en busca de secretos hardcodeados como:
- Claves API
- Contraseñas
- Tokens de autenticación
- Claves AWS
- Claves privadas
- URLs de bases de datos con credenciales
- Tokens Bearer

El sistema genera reportes en formato JSON y expone endpoints para consultar los resultados del escaneo.




## Despliegue con Docker Compose

### Paso 1: Crear el volumen compartido

Ambos servicios comparten un volumen para los datos de evidencia:

```powershell
docker volume create evidence_data
```

### Paso 2: Desplegar el Secret Scanner Service

Este servicio escanea el código y genera los reportes JSON.

```powershell
# Construir y levantar el servicio
docker-compose -f docker-compose-scanner.yml up -d

# Ver logs del servicio
docker-compose -f docker-compose-scanner.yml logs -f

# Detener el servicio
docker-compose -f docker-compose-scanner.yml down
```

**Características del servicio:**
- **Puerto**: 8001
- **Container**: `secret-scanner-service`
- **Volúmenes**:
  - `evidence_data:/app/evidence` - Almacena resultados del escaneo
  - `.:/scan-target` - Monta el código a escanear

**Dockerfile.scanner:**
- Imagen base: `python:3.11-slim`
- Usuario no-root: `appuser`
- Expone puerto 8001
- Comando: `python scripts/secret_guardian_service.py`

### Paso 3: Desplegar el Guardian API Service

Este servicio expone los resultados del escaneo a través de una API REST.

```powershell
# Construir y levantar el servicio
docker-compose -f docker-compose-api.yml up -d

# Ver logs del servicio
docker-compose -f docker-compose-api.yml logs -f

# Detener el servicio
docker-compose -f docker-compose-api.yml down
```

**Características del servicio:**
- **Puerto**: 8000
- **Container**: `guardian-api-service`
- **Volúmenes**:
  - `evidence_data:/app/evidence` - Lee resultados del escaneo

**Dockerfile.api:**
- Imagen base: `python:3.11-slim`
- Usuario no-root: `appuser`
- Expone puerto 8000
- Comando: `python -m app.main`

### Paso 4: Desplegar ambos servicios simultáneamente

```powershell
# Levantar ambos servicios
docker-compose -f docker-compose-scanner.yml up -d
docker-compose -f docker-compose-api.yml up -d

# Ver el estado de los contenedores
docker ps

# Ver logs de ambos servicios
docker logs secret-scanner-service
docker logs guardian-api-service
```
