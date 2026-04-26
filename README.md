# Docker Domain Communication Demo (FastAPI)

Este proyecto es una prueba de concepto (PoC) que demuestra cómo establecer comunicación entre microservicios dentro de una red de Docker utilizando **nombres de dominio personalizados** en lugar de direcciones IP, simulando diferentes entornos de despliegue (Desarrollo, QA y Producción).

## ¿Qué hace?
El sistema levanta dos contenedores independientes (`dockerone` y `dockertwo`) ejecutando **FastAPI**. Cada contenedor puede:
1.  **Recibir llamadas API** en endpoints específicos.
2.  **Enviar mensajes** al otro contenedor utilizando un nombre de dominio que cambia según el ambiente configurado (`.des`, `.qa`, o `.com`).
3.  **Identificar el ambiente** (Local, QA, Prod) a través de variables de entorno.

## ¿Cómo lo hace? (Arquitectura)

### 1. Service Discovery via Docker DNS
Docker incluye un servidor DNS interno. Al definir `aliases` dentro de una red (`networks`), le decimos a Docker que un contenedor debe responder a múltiples nombres de dominio.
*   **Local**: `contenedorone.des`
*   **QA**: `contenedorone.qa`
*   **Producción**: `subdominioone.dominio.com`

### 2. Abstracción de Ambientes
El código Python es agnóstico al dominio. No tiene URLs "hardcodeadas". En su lugar, lee la variable `TARGET_URL` inyectada por Docker Compose, la cual se construye dinámicamente usando el archivo `.env`.

### 3. Flujo de Comunicación
1.  El usuario llama a un "disparador" (trigger) en `http://localhost:8081/send`.
2.  El contenedor `dockerone` recibe la petición y busca en su archivo de configuración a quién debe llamar.
3.  Realiza una petición `POST` hacia `http://contenedortwo.des:8080/...`.
4.  El DNS de Docker traduce `contenedortwo.des` a la IP interna de `dockertwo`.
5.  `dockertwo` procesa el JSON y responde.

## Requisitos
*   Docker y Docker Compose instalados.

## Configuración y Uso

### 1. Definir el ambiente
Edita el archivo `.env` en la raíz del proyecto:
```env
APP_ENV=local  # Cambia a qa o prod para simular otros ambientes
```

### 2. Levantar los servicios
```bash
docker-compose up --build
```

### 3. Probar la comunicación
Para probar la comunicación **interna**, usamos los puertos mapeados al host (8081 y 8082):

*   **De Uno a Dos**:
    ```bash
    curl http://localhost:8081/send
    ```
*   **De Dos a Uno**:
    ```bash
    curl http://localhost:8082/send
    ```

## Simulación de Entornos

| Ambiente | Dominio Utilizado | Resolución de Nombres |
| :--- | :--- | :--- |
| **Local (Desarrollo)** | `*.des` | Interna vía Docker / Externa vía `/etc/hosts` |
| **QA** | `*.qa` | Administrado por Active Directory en entornos reales |
| **Producción** | `*.com` | Simulado internamente, pero diseñado para Cloudflare |

## ¿Cuál es el límite? (Restricciones)

1.  **Resolución fuera de Docker**: El host (tu PC) **no conoce** los dominios `.des` o `.qa` automáticamente. Para que `http://contenedorone.des` funcione en tu navegador, debes mapearlos en tu archivo `/etc/hosts`.
2.  **Aislamiento de Red**: Los dominios definidos en `aliases` solo son visibles para otros contenedores en la **misma red** de Docker.
3.  **Puertos Internos vs Externos**: 
    *   Internamente (entre contenedores), siempre se usa el puerto del proceso (`8080`).
    *   Externamente (desde el host), se usan los puertos mapeados (`8081`, `8082`).
4.  **Certificados SSL**: Esta demo usa `http`. En un ambiente real de producción (`.com`), se requeriría un Proxy Inverso (como Nginx o Traefik) para manejar la terminación SSL/TLS de Cloudflare.
5.  **Persistencia del DNS**: Si un contenedor cae, el DNS de Docker deja de resolver ese dominio inmediatamente hasta que el servicio esté `UP`.
