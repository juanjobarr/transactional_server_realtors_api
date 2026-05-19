# Servicio transaccional

## 1. Rol del servicio

Este servicio es el núcleo del sistema. Administra:

* autenticación y autorización con JWT;
* perfiles comerciales;
* suscripciones y cuotas;
* drafts y guiones;
* jobs de generación;
* eventos y auditoría;
* webhooks;
* publicación final de videos.

Debe conservar el negocio completo, pero con una base de datos más simple y fácil de mantener.

---

## 2. Objetivo de simplificación

La base de datos debe:

* mantener las mismas funcionalidades del sistema actual;
* alinearse con los datos mockeados del frontend;
* incluir soporte para autenticación con JWT;
* evitar tablas innecesarias o demasiado fragmentadas;
* usar estructuras simples y consistentes;
* permitir crecer sin romper el modelo actual.

En lugar de múltiples entidades pequeñas, se priorizan tablas principales complementadas con algunos campos JSON.

---

## 3. Arquitectura sugerida

Arquitectura recomendada:

* Hexagonal Architecture
* Clean Architecture

```text
transactional_service/
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── services/
│   │   ├── events/
│   │   └── ports/
│   ├── application/
│   │   ├── use_cases/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── dto/
│   ├── infrastructure/
│   │   ├── db/
│   │   ├── clients/
│   │   ├── messaging/
│   │   └── observability/
│   └── interfaces/
│       └── api/
└── tests/
```

---

## 4. Modelo de datos simplificado

### 4.1 users

Representa al usuario del sistema, normalmente un realtor.

#### Campos

* id
* full_name
* email
* password_hash
* avatar_initials
* role
* status
* is_email_verified
* last_login_at
* created_at
* updated_at

#### Relación con frontend

* `full_name` → `MOCK_USER.name`
* `avatar_initials` → `MOCK_USER.avatar`

---

### 4.2 auth_sessions

Registra sesiones activas derivadas de JWT cuando se desea poder revocar tokens o auditar acceso.

#### Campos

* id
* user_id
* refresh_token_hash
* device_name
* ip_address
* user_agent
* expires_at
* revoked_at
* created_at
* updated_at

Esta tabla es opcional a nivel de implementación, pero útil si se desea soporte para logout real, refresh tokens y revocación.

---

### 4.3 plans

Define el plan comercial.

#### Campos

* id
* name
* monthly_video_limit
* monthly_scene_limit
* price
* currency
* active
* created_at
* updated_at

#### Relación con frontend

* `name` → `MOCK_USER.plan`

---

### 4.4 subscriptions

Relaciona usuarios con planes y controla el ciclo de facturación.

#### Campos

* id
* user_id
* plan_id
* billing_start
* billing_end
* status
* videos_used
* scenes_used
* videos_remaining
* created_at
* updated_at

Esta tabla mantiene el control de cuotas sin necesidad de estructuras complejas.

---

### 4.5 realtor_profiles

Guarda la identidad comercial del realtor.

#### Campos

* id
* user_id
* brokerage_name
* brand_name
* logo_url
* avatar_asset_id
* voice_profile_id
* default_tone
* brand_settings_json
* created_at
* updated_at

#### Notas

`brand_settings_json` puede almacenar:

* colores de marca;
* firmas;
* estilos visuales;
* CTA por defecto;
* configuraciones visuales.

---

### 4.6 video_topics

Catálogo simple de temas de video.

#### Campos

* id
* code
* label
* description
* icon
* active
* created_at

#### Ejemplos alineados al frontend

| code    | label         |
| ------- | ------------- |
| listing | New Listing   |
| market  | Market Update |
| tips    | Buyer Tips    |
| sold    | Just Sold     |
| intro   | About Me      |
| open    | Open House    |

Esta tabla hace match directo con `VIDEO_TOPICS`.

---

### 4.7 video_drafts

Guarda el borrador del flujo de creación.

#### Campos

* id
* user_id
* topic_id
* title
* subject
* property_address
* description
* bullet_points_json
* tone
* pacing
* status
* current_step
* created_at
* updated_at

#### Notas

* `subject` permite cubrir market updates, intros o temas generales.
* `property_address` sirve para listings y open houses.
* `bullet_points_json` evita tablas adicionales innecesarias.

---

### 4.8 video_draft_reference_images

Imágenes de referencia asociadas al draft.

#### Campos

* id
* draft_id
* storage_url
* role
* sort_order
* metadata_json
* created_at

Se conserva esta tabla porque las imágenes requieren orden y trazabilidad.

---

### 4.9 script_versions

Versiona los guiones generados.

#### Campos

* id
* draft_id
* version_number
* script_text
* structured_script_json
* estimated_read_time_seconds
* is_approved
* approved_by_user_id
* approved_at
* created_at

Este diseño mantiene regeneración, edición y aprobación sin fragmentar demasiado el modelo.

---

### 4.10 video_jobs

Registro maestro de ejecución del pipeline.

#### Campos

* id
* draft_id
* status
* job_type
* idempotency_key
* generation_job_id
* render_job_id
* progress_percent
* error_code
* error_message
* created_at
* updated_at

Esta tabla representa el estado operativo principal.

---

### 4.11 video_job_events

Auditoría temporal y trazabilidad de jobs.

#### Campos

* id
* job_id
* event_type
* payload_json
* created_at

Aquí se registran:

* cambios de estado;
* callbacks;
* errores;
* reintentos;
* transiciones.

---

### 4.12 videos

Entidad final visible en “My Videos”.

#### Campos

* id
* job_id
* user_id
* title
* topic_id
* thumbnail_url
* final_video_url
* final_video_storage_key
* format
* duration_seconds
* scenes_count
* views_count
* downloads_count
* status
* published_at
* created_at
* updated_at

#### Relación con frontend

Los siguientes campos alimentan directamente `MOCK_LIBRARY`:

* `title`
* `topic_id`
* `views_count`
* `status`
* `published_at`

---

### 4.13 quota_usage

Control simple de consumo mensual.

#### Campos

* id
* user_id
* billing_period
* videos_generated
* scenes_generated
* seconds_generated
* last_updated

---

### 4.14 webhook_events

Evita duplicados y registra callbacks externos.

#### Campos

* id
* source
* external_event_id
* event_type
* payload_json
* received_at
* processed_at
* status

Debe soportar:

* generación;
* render;
* futuras integraciones.

---

## 5. Objetos de dominio

Conviene modelar como objetos pequeños:

* Tone
* Pacing
* Topic
* DurationSeconds
* JobStatus
* DraftStatus
* VideoStatus
* StorageUrl
* JwtToken
* RefreshToken

---

## 6. Servicios de dominio

Servicios principales:

* ScriptComposer
* JobStateMachine
* QuotaPolicy
* TopicResolver
* AuthService
* TokenService
* SessionService
* VideoPublishingService

---

## 7. Casos de uso

Casos de uso típicos:

* RegisterUser
* LoginUser
* RefreshAccessToken
* LogoutUser
* GetCurrentUser
* CreateDraft
* UpdateDraft
* UploadReferenceImage
* GenerateScript
* RegenerateScript
* ApproveScript
* StartVideoJob
* HandleGenerationWebhook
* HandleRenderWebhook
* FinalizeVideo
* ListVideos
* GetJobStatus

---

## 8. Flujo interno

1. El usuario se registra o inicia sesión con email y password.
2. El servicio valida credenciales y emite un access token JWT y, si aplica, un refresh token.
3. El frontend guarda el access token y solicita el perfil, plan y cuota disponible.
4. El usuario crea un draft.
5. Se almacena el contexto del draft.
6. Se genera el guion.
7. El guion se versiona.
8. El usuario aprueba el guion.
9. Se valida y reserva cuota.
10. Se crea el job.
11. Se envía el payload al motor de generación.
12. Se reciben webhooks.
13. Se publica el MP4 final.
14. El video aparece en la biblioteca.

---

## 9. Endpoints

Todos los endpoints deben versionarse usando `/api/v1/`.

### Autenticación

| Método | Endpoint                | Descripción                 |
| ------ | ----------------------- | --------------------------- |
| POST   | `/api/v1/auth/register` | Registrar usuario           |
| POST   | `/api/v1/auth/login`    | Iniciar sesión y emitir JWT |
| POST   | `/api/v1/auth/refresh`  | Renovar access token        |
| POST   | `/api/v1/auth/logout`   | Revocar sesión actual       |
| GET    | `/api/v1/auth/me`       | Obtener usuario autenticado |

### Negocio principal

| Método | Endpoint                                  | Descripción               |
| ------ | ----------------------------------------- | ------------------------- |
| POST   | `/api/v1/video-drafts`                    | Crear draft               |
| PATCH  | `/api/v1/video-drafts/:id`                | Actualizar draft          |
| POST   | `/api/v1/video-drafts/:id/script`         | Generar o regenerar guion |
| POST   | `/api/v1/video-drafts/:id/approve-script` | Aprobar guion             |
| POST   | `/api/v1/video-jobs`                      | Iniciar job               |
| GET    | `/api/v1/video-jobs/:id`                  | Obtener estado del job    |
| GET    | `/api/v1/videos`                          | Listar videos             |
| GET    | `/api/v1/video-topics`                    | Listar topics             |

### Webhooks

| Método | Endpoint                     | Descripción           |
| ------ | ---------------------------- | --------------------- |
| POST   | `/api/v1/webhooks/generated` | Webhook de generación |
| POST   | `/api/v1/webhooks/rendered`  | Webhook de render     |

---

## 10. Persistencia

La base de datos debe guardar:

* usuarios;
* sesiones o refresh tokens para JWT;
* planes;
* suscripciones;
* perfiles comerciales;
* topics de video;
* drafts;
* imágenes de referencia;
* versiones de script;
* jobs;
* eventos;
* videos finales;
* cuotas;
* webhooks.

---

## 11. Relación con datos mockeados

### MOCK_USER

| Frontend | Base de datos           |
| -------- | ----------------------- |
| `name`   | `users.full_name`       |
| `avatar` | `users.avatar_initials` |
| `plan`   | `plans.name`            |

---

### VIDEO_TOPICS

Mapea directamente a `video_topics`.

---

### MOCK_LIBRARY

Mapea directamente a `videos`.

---

### MOCK_SCRIPTS

Puede almacenarse en:

* `script_versions.script_text`
* seeds iniciales
* templates por topic

---

### MOCK_CREDENTIALS

| Frontend   | Base de datos         |
| ---------- | --------------------- |
| `email`    | `users.email`         |
| `password` | `users.password_hash` |

El login debe validar estas credenciales y devolver un JWT de acceso.

---

## 12. Estados sugeridos

### Drafts

* draft
* ready
* approved
* processing
* completed
* failed

### Jobs

* queued
* generating
* rendering
* completed
* failed

### Videos

* published
* processing
* failed

### Auth sessions

* active
* revoked
* expired

---

## 13. Ventajas del enfoque

* menos tablas;
* menor complejidad;
* mejor alineación con el frontend mockeado;
* soporte completo para autenticación con JWT, drafts, jobs y eventos;
* onboarding más rápido;
* facilidad para testing y seeds;
* mantenimiento más sencillo;
* escalabilidad progresiva sin rediseñar el modelo.
