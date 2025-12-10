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

---

## Despliegue en Kubernetes (Minikube)

### Setup inicial

```bash
# Iniciar Minikube
minikube start

# Configurar Docker para usar el daemon de Minikube
eval $(minikube docker-env)

# Construir las imágenes
docker build -t guardian-api:latest -f Dockerfile.api .
docker build -t secret-scanner:latest -f Dockerfile.scanner .
```

### Montar el proyecto

El scanner necesita acceso al código fuente. En una terminal separada ejecutá:

```bash
minikube mount "$(pwd):/host-project"
```

Dejá esta terminal corriendo. Si la cerrás, el scanner no va a poder leer el código.

### Desplegar

```bash
kubectl apply -f k8s/
kubectl get pods  # espera a que estén Running 1/1
```

### Acceder a los servicios

```bash
# Ver las URLs
minikube service guardian-api-service --url
minikube service secret-scanner-service --url

# Probar endpoints
curl $(minikube service guardian-api-service --url)/health
curl $(minikube service secret-scanner-service --url)/scan
curl $(minikube service guardian-api-service --url)/scan-result
```

### Ver logs

```bash
kubectl logs -l component=scanner
kubectl logs -l component=api -f  # follow
```

### Troubleshooting

Si los pods tienen `ErrImageNeverPull`:
```bash
eval $(minikube docker-env)
docker build -t guardian-api:latest -f Dockerfile.api .
docker build -t secret-scanner:latest -f Dockerfile.scanner .
kubectl rollout restart deployment guardian-api secret-scanner
```

Si el scanner da error de I/O en `/scan-target`:
```bash
# El mount se cerró, volvé a ejecutarlo en otra terminal
minikube mount "$(pwd):/host-project"
kubectl delete pod -l component=scanner
```

### Limpiar

```bash
kubectl delete -f k8s/
minikube stop
```
