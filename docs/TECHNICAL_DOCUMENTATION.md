# 📚 Documentación Técnica - Commercial RAG System

## 📑 Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura)
2. [Base de Datos](#base-de-datos)
3. [API Endpoints](#api-endpoints)
4. [Sistema RAG](#sistema-rag)
5. [Autenticación](#autenticacion)
6. [Frontend](#frontend)
7. [Configuración](#configuracion)
8. [Desarrollo](#desarrollo)
9. [Notas Adicionales](#notas-adicionales)

---

## 🏗️ Arquitectura del Sistema {#arquitectura}

### Diagrama de Componentes
```
┌─────────────────────────────────────────────────────────┐
│                    COMMERCIAL RAG SYSTEM                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  Streamlit   │────────▶│   FastAPI    │             │
│  │  Frontend    │         │   Backend    │             │
│  │              │         │              │             │
│  │ - Login      │         │ - REST API   │             │
│  │ - Chat UI    │         │ - Auth       │             │
│  │ - Dashboard  │         │ - RAG Engine │             │
│  │ - Admin UI   │         │ - Business   │             │
│  └──────────────┘         │   Logic      │             │
│                            └──────┬───────┘             │
│                                   │                     │
│           ┌───────────────────────┼───────────────┐    │
│           │                       │               │    │
│           ▼                       ▼               ▼    │
│  ┌─────────────┐       ┌─────────────┐  ┌──────────┐  │
│  │ PostgreSQL  │       │  ChromaDB   │  │ Claude   │  │
│  │             │       │             │  │   API    │  │
│  │ - Users     │       │ - Vectors   │  │          │  │
│  │ - Messages  │       │ - Stats     │  │ Anthropic│  │
│  │ - Stats     │       │ - Embeddings│  │          │  │
│  └─────────────┘       └─────────────┘  └──────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Stack Tecnológico

**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0+
- PostgreSQL 15
- Python 3.11+

**RAG:**
- ChromaDB
- sentence-transformers (all-MiniLM-L6-v2)
- Anthropic Claude API (Sonnet 4)
- LangChain

**Frontend:**
- Streamlit 1.28+
- Plotly
- Pandas

**Infraestructura:**
- Docker
- Docker Compose

---

## 💾 Base de Datos {#base-de-datos}

### Esquema de Tablas

#### Tabla: users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'user')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### Tabla: conversations
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
```

#### Tabla: messages
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost_usd DECIMAL(10, 4)
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
```

#### Tabla: usage_stats
```sql
CREATE TABLE usage_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_tokens_input INTEGER DEFAULT 0,
    total_tokens_output INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10, 4) DEFAULT 0,
    query_count INTEGER DEFAULT 0,
    UNIQUE(user_id, date)
);

CREATE INDEX idx_usage_stats_user_date ON usage_stats(user_id, date DESC);
```

### Relaciones
users (1) ─── (N) conversations
conversations (1) ─── (N) messages
users (1) ─── (N) usage_stats

---

## 🔌 API Endpoints {#api-endpoints}

### Autenticación

| Método | Endpoint | Descripción | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/auth/register` | Registrar nuevo usuario | No | - |
| POST | `/auth/login` | Login | No | - |
| GET | `/auth/me` | Usuario actual | Sí | - |
| POST | `/auth/refresh` | Renovar token | Sí | - |

### Conversaciones

| Método | Endpoint | Descripción | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/conversations/create` | Crear conversación | Sí | - |
| GET | `/conversations` | Listar conversaciones | Sí | - |
| GET | `/conversations/{id}` | Ver conversación | Sí | - |
| PUT | `/conversations/{id}/title` | Actualizar título | Sí | - |
| DELETE | `/conversations/{id}` | Eliminar conversación | Sí | - |

### RAG

| Método | Endpoint | Descripción | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/query` | Hacer consulta RAG | Sí | - |

### Admin - Usuarios

| Método | Endpoint | Descripción | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/admin/users` | Listar usuarios | Sí | Admin |
| POST | `/admin/users/create` | Crear usuario | Sí | Admin |
| GET | `/admin/users/{id}` | Ver usuario | Sí | Admin |
| PUT | `/admin/users/{id}/password` | Cambiar password | Sí | Admin |
| PUT | `/admin/users/{id}/toggle-active` | Activar/Desactivar | Sí | Admin |
| DELETE | `/admin/users/{id}` | Eliminar usuario | Sí | Admin |

### Admin - Documentos

| Método | Endpoint | Descripción | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/admin/documents` | Listar documentos | Sí | Admin |
| POST | `/admin/documents/upload` | Subir documentos | Sí | Admin |
| POST | `/admin/documents/reindex` | Reindexar | Sí | Admin |
| DELETE | `/admin/documents/{filename}` | Eliminar documento | Sí | Admin |

### Admin - Estadísticas

| Método | Endpoint | Descripción | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/admin/usage/user/{id}` | Stats de usuario | Sí | Admin |
| GET | `/admin/usage/global` | Stats globales | Sí | Admin |
| GET | `/admin/usage/realtime` | Stats tiempo real | Sí | Admin |

---

## 🤖 Sistema RAG {#sistema-rag}

### Flujo de Procesamiento

INDEXACIÓN (una vez):
Documentos → Chunking → Embeddings → ChromaDB
QUERY (cada consulta):
Pregunta → Embedding → Búsqueda → Contexto + Historial → Claude → Respuesta


### Componentes

**DocumentProcessor:**
- Carga documentos (PDF, DOCX, TXT, MD)
- Divide en chunks (500 tokens, overlap 50)
- Genera embeddings con sentence-transformers
- Almacena en ChromaDB

**ClaudeRAG:**
- Busca chunks relevantes (top 5)
- Construye prompt con contexto
- Llama a Claude API
- Calcula tokens y costes
- Retorna respuesta estructurada

### Configuración de Embeddings
```python
model = "sentence-transformers/all-MiniLM-L6-v2"
chunk_size = 500  # tokens
chunk_overlap = 50  # tokens
top_k = 5  # chunks a recuperar
```

### Prompt Template
Eres un asistente comercial experto. Responde basándote ÚNICAMENTE
en la documentación proporcionada.
CONTEXTO DE DOCUMENTACIÓN:
{contexto_relevante}
HISTORIAL DE CONVERSACIÓN:
{historial}
PREGUNTA DEL USUARIO:
{query}
INSTRUCCIONES:

Responde de forma clara y profesional
Cita las fuentes cuando uses información específica
Si no encuentras la respuesta en la documentación, dilo claramente
No inventes información


---

## 🔐 Autenticación {#autenticacion}

### JWT Tokens

**Estructura:**
```json
{
  "sub": "user_id_uuid",
  "username": "john_doe",
  "role": "user",
  "exp": 1234567890
}
```

**Algoritmo:** HS256  
**Expiración:** 24 horas (configurable)  
**Secret:** Generado con `openssl rand -hex 32`

### Flujo de Autenticación

POST /auth/login
↓
Validar credenciales (bcrypt)
↓
Generar JWT token
↓
Retornar token + user data
↓
Cliente guarda token
↓
Requests incluyen: Authorization: Bearer {token}
↓
Backend valida token en cada request


### Roles

- **admin**: Acceso completo (usuarios, documentos, stats)
- **user**: Solo chat y conversaciones propias

---

## 🎨 Frontend {#frontend}

### Estructura de Páginas
streamlit_app.py (main)
├── pages/
│   ├── login.py
│   ├── chat.py
│   ├── admin_dashboard.py
│   ├── admin_users.py
│   └── admin_documents.py
├── components/
│   ├── sidebar.py
│   ├── metrics_cards.py
│   └── usage_charts.py
└── utils.py

### Gestión de Estado

**Session State Variables:**
```python
st.session_state = {
    "token": "jwt_token_string",
    "user": {
        "id": "uuid",
        "username": "john",
        "email": "john@empresa.com",
        "role": "user"
    },
    "current_conversation_id": "uuid",
    "messages": [...]
}
```

### Routing
```python
if not is_authenticated():
    show_login_page()
elif selected_page == "Chat":
    show_chat_page()
elif selected_page == "Dashboard" and is_admin():
    show_admin_dashboard()
...
```

---

## ⚙️ Configuración {#configuracion}

### Variables de Entorno

Ver `.env.example` para lista completa.

**Críticas:**
- `ANTHROPIC_API_KEY`: API key de Claude
- `DATABASE_URL`: Connection string PostgreSQL
- `JWT_SECRET_KEY`: Secret para JWT (32 chars hex)

**Opcionales:**
- `JWT_EXPIRATION_MINUTES`: Tiempo de expiración (default: 1440)
- `CLAUDE_INPUT_PRICE_PER_MILLION`: Precio input tokens
- `CLAUDE_OUTPUT_PRICE_PER_MILLION`: Precio output tokens

---

## 👨💻 Desarrollo {#desarrollo}

### Setup Local
```bash
# Clonar repo
git clone ...
cd commercial-rag-system

# Entorno virtual
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Si existe

# Configurar .env
cp .env.example .env
# Editar .env con tus valores

# Iniciar PostgreSQL local o usar Docker
docker-compose up -d db

# Inicializar BD
python backend/init_rag.py --init-db --create-admin

# Iniciar backend
python backend/app.py

# En otra terminal, iniciar frontend
streamlit run frontend/streamlit_app.py
```

### Ejecutar Tests
```bash
# Tests automatizados
pytest tests/ -v

# Con coverage
pytest tests/ --cov=backend --cov-report=html

# Tests específicos
pytest tests/test_complete_system.py::TestAuthentication -v
```

### Linting y Formato
```bash
# Black (formato)
black backend/ frontend/

# Flake8 (linting)
flake8 backend/ frontend/

# mypy (type checking)
mypy backend/
```

### Logs

**Backend:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message")
```

**Ubicación:** `data/logs/`

---

## 📝 Notas Adicionales

### Limitaciones Conocidas

1. ChromaDB no es distribuido (single instance)
2. Sin sistema de caché de respuestas
3. Auto-refresh en dashboard requiere recarga manual

### Futuras Mejoras

- [ ] Sistema de caché para queries frecuentes
- [ ] Soporte para más formatos (Excel, PPT)
- [ ] Export de conversaciones a PDF
- [ ] Notificaciones por email para alertas
- [ ] API rate limiting más sofisticado
- [ ] Telemetría y métricas avanzadas

---

**Última actualización:** Enero 2026  
**Versión:** 1.0.0
