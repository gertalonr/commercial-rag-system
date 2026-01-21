# 🏢 Commercial RAG System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

> Sistema empresarial de consultas con IA utilizando RAG (Retrieval-Augmented Generation) y Claude de Anthropic.

Permite a equipos hacer preguntas en lenguaje natural sobre documentación empresarial y recibir respuestas precisas con citas de fuentes, gestión de usuarios, historial de conversaciones y dashboard administrativo con tracking de costes.

---

## ✨ Características

- 🤖 **RAG con Claude Sonnet 4** - Respuestas precisas basadas en tus documentos
- 💬 **Chat conversacional** - Contexto multi-turno con historial
- 👥 **Gestión de usuarios** - Roles (Admin/Usuario) con autenticación JWT
- 📊 **Dashboard administrativo** - Métricas de uso y costes en tiempo real
- 📁 **Gestión de documentos** - Upload, indexación y búsqueda vectorial
- 🔍 **Citas de fuentes** - Transparencia en cada respuesta
- 💰 **Tracking de costes** - Monitoreo de consumo de tokens por usuario
- 🐳 **Dockerizado** - Despliegue con un comando
- 📱 **Responsive** - Funciona en desktop y mobile

---

## 🎥 Demo

![Demo Screenshot](docs/images/screenshot-chat.png)
*Interfaz de chat con respuestas contextualizadas*

![Admin Dashboard](docs/images/screenshot-dashboard.png)
*Dashboard administrativo con métricas en tiempo real*

---

## 🏗️ Arquitectura
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Streamlit  │─────▶│   FastAPI   │─────▶│ PostgreSQL  │
│  Frontend   │      │   Backend   │      │  Database   │
└─────────────┘      └──────┬──────┘      └─────────────┘
                            │
                     ┌──────▼──────┐
                     │  ChromaDB   │
                     │  (Vectores) │
                     └──────┬──────┘
                            │
                     ┌──────▼──────┐
                     │  Claude API │
                     │ (Anthropic) │
                     └─────────────┘
```

**Stack:**
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **RAG:** ChromaDB, sentence-transformers, Claude API
- **Frontend:** Streamlit, Plotly
- **Infraestructura:** Docker, Docker Compose

---

## 🚀 Quick Start

### Requisitos Previos

- Docker 20.10+
- Docker Compose 2.0+
- API Key de Anthropic Claude ([obtener aquí](https://console.anthropic.com/))

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/gertalonr/commercial-rag-system.git
cd commercial-rag-system
```

2. **Generar secretos seguros**
```bash
chmod +x scripts/generate-secrets.sh
./scripts/generate-secrets.sh
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
nano .env  # Añadir tu ANTHROPIC_API_KEY
```

4. **Añadir documentos** (opcional)
```bash
cp tus-documentos/*.pdf data/documents/
```

5. **Iniciar el sistema**
```bash
docker-compose up -d
```

6. **Acceder a la aplicación**

- Frontend: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Credenciales iniciales:**
- Usuario: `admin`
- Password: (ver archivo `.env`)

---

## 📖 Documentación

- [📘 Guía de Usuario](docs/USER_GUIDE.md) - Para usuarios finales
- [📗 Documentación Técnica](docs/TECHNICAL_DOCUMENTATION.md) - Para desarrolladores
- [🧪 Guía de Testing](tests/manual_integration_test.md) - Tests manuales

---

## 💻 Desarrollo Local

### Setup sin Docker
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env con tus valores

# Iniciar PostgreSQL (o usar Docker solo para DB)
docker-compose up -d db

# Inicializar BD
python backend/init_rag.py --init-db --create-admin --index-docs

# Iniciar backend (terminal 1)
python backend/app.py

# Iniciar frontend (terminal 2)
streamlit run frontend/streamlit_app.py
```

### Ejecutar Tests
```bash
# Tests automatizados
docker-compose exec backend pytest tests/ -v

# Tests rápidos
./tests/quick_test.sh
```

---

## 🛠️ Configuración

### Variables de Entorno Principales

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `ANTHROPIC_API_KEY` | API key de Claude | ✅ Sí |
| `DATABASE_URL` | PostgreSQL connection string | ✅ Sí |
| `JWT_SECRET_KEY` | Secret para JWT (32 chars) | ✅ Sí |
| `ADMIN_USERNAME` | Usuario admin inicial | No |
| `ADMIN_PASSWORD` | Password admin inicial | ✅ Sí |

Ver [.env.example](.env.example) para lista completa.

---

## 📊 Uso

### Como Usuario

1. Login con tus credenciales
2. Haz preguntas en lenguaje natural
3. Recibe respuestas con citas de fuentes
4. Revisa conversaciones anteriores

**Ejemplo:**
```
Tú: ¿Cuál es el precio del producto X?
Sistema: El precio es $299/mes. Hay un descuento del 10% 
para equipos de 20+ usuarios.
📚 Fuente: productos.pdf
```

### Como Administrador

1. Gestionar usuarios (crear, editar, desactivar)
2. Subir y gestionar documentos
3. Ver métricas de uso y costes
4. Monitorear consumo por usuario

---

## 🤝 Contribuir

¡Contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

---

## 📝 Roadmap

- [ ] Cache de respuestas frecuentes
- [ ] Soporte para Excel y PowerPoint
- [ ] Export de conversaciones a PDF
- [ ] Notificaciones por email
- [ ] Integración con Slack/Teams
- [ ] Multi-idioma
- [ ] API rate limiting avanzado
- [ ] Telemetría con Prometheus

---

## 🐛 Troubleshooting

### El frontend no conecta con el backend
```bash
docker-compose logs backend
docker-compose restart backend
```

### Documentos no se indexan
```bash
docker-compose exec backend python backend/init_rag.py --index-docs
```

### Olvidé la contraseña de admin
```bash
docker-compose exec backend python -c "
from backend.database import get_db
from backend.admin_service import update_user_password
from backend.database import User
db = next(get_db())
admin = db.query(User).filter(User.username == 'admin').first()
update_user_password(db, admin.id, 'NuevoPassword123!')
"
```

Más soluciones en [Troubleshooting](docs/TECHNICAL_DOCUMENTATION.md#troubleshooting)

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- [Anthropic](https://www.anthropic.com/) - Claude API
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Streamlit](https://streamlit.io/) - Frontend framework

---

## 📧 Contacto

Germán Talón Ramírez - [@tu_twitter](https://twitter.com/tu_twitter)

Project Link: [https://github.com/gertalonr/commercial-rag-system](https://github.com/gertalonr/commercial-rag-system)

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=gertalonr/commercial-rag-system&type=Date)](https://star-history.com/#gertalonr/commercial-rag-system&Date)

---

**¿Te resultó útil? ¡Dale una ⭐ al proyecto!**
