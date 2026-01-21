# 📋 Guía de Tests Manuales - Commercial RAG System

Esta guía describe los tests que se deben realizar manualmente para verificar el correcto funcionamiento del sistema.

## 🎯 Objetivos

Verificar:
- ✅ Flujo completo de usuario comercial
- ✅ Funciones administrativas
- ✅ Calidad de respuestas RAG
- ✅ UI/UX

---

## TEST 1: Primer Arranque del Sistema

### Pasos:

1. ✅ **Desplegar sistema**
```bash
   docker-compose up -d
```
   - [ ] Todos los contenedores inician correctamente
   - [ ] No hay errores en logs
   - [ ] Health checks pasan

2. ✅ **Acceder a frontend**
   - [ ] URL http://localhost:8501 accesible
   - [ ] Pantalla de login se muestra correctamente
   - [ ] No hay errores en consola del navegador

3. ✅ **Login inicial admin**
   - [ ] Usar credenciales del .env
   - [ ] Login exitoso
   - [ ] Redirect a página principal
   - [ ] Sidebar muestra opciones de admin

---

## TEST 2: Funciones de Administrador

### 2.1 Gestión de Usuarios

1. ✅ **Crear usuario comercial**
   - [ ] Ir a "👥 Usuarios"
   - [ ] Click en "➕ Nuevo Usuario"
   - [ ] Completar formulario:
     - Usuario: comercial1
     - Email: comercial1@empresa.com
     - Password: ComercialPass123!
     - Rol: user
   - [ ] Usuario creado exitosamente
   - [ ] Aparece en la lista

2. ✅ **Editar usuario**
   - [ ] Click en ⚙️ junto al usuario
   - [ ] Cambiar contraseña
   - [ ] Confirmación de cambio exitoso

3. ✅ **Desactivar/Activar usuario**
   - [ ] Toggle activo/inactivo funciona
   - [ ] Usuario desactivado no puede hacer login
   - [ ] Usuario reactivado puede hacer login

4. ✅ **Eliminar usuario**
   - [ ] Crear usuario de prueba
   - [ ] Eliminar con botón 🗑️
   - [ ] Confirmación solicitada
   - [ ] Usuario eliminado correctamente

### 2.2 Dashboard Administrativo

1. ✅ **Visualizar métricas**
   - [ ] Ir a "📊 Dashboard"
   - [ ] Métricas se muestran:
     - Total tokens
     - Coste total
     - Número de queries
     - Usuarios activos
   - [ ] Valores son coherentes (no negativos)

2. ✅ **Gráficos**
   - [ ] Gráfico de barras de usuarios se renderiza
   - [ ] Datos son correctos
   - [ ] Interactividad funciona (hover, zoom)

3. ✅ **Auto-refresh**
   - [ ] Click en "🔄 Actualizar"
   - [ ] Datos se actualizan

### 2.3 Gestión de Documentos

1. ✅ **Ver documentos**
   - [ ] Ir a "📁 Documentos"
   - [ ] Lista de documentos se muestra
   - [ ] Información correcta (nombre, tamaño, fecha)

2. ✅ **Subir documento**
   - [ ] Click en "📤 Subir Documentos"
   - [ ] Seleccionar PDF de prueba
   - [ ] Upload exitoso
   - [ ] Documento aparece en lista

3. ✅ **Reindexar**
   - [ ] Click en "🔄 Reindexar"
   - [ ] Proceso inicia
   - [ ] Confirmación de éxito
   - [ ] Número de chunks actualizado

4. ✅ **Eliminar documento**
   - [ ] Click en ❌ junto a documento
   - [ ] Confirmación solicitada
   - [ ] Documento eliminado
   - [ ] Desaparece de lista

---

## TEST 3: Funciones de Usuario Comercial

### 3.1 Login y Navegación

1. ✅ **Login como usuario comercial**
   - [ ] Logout del admin
   - [ ] Login con credenciales de comercial1
   - [ ] Login exitoso
   - [ ] Sidebar muestra opciones de usuario (sin admin)

### 3.2 Consultas RAG

1. ✅ **Primera consulta (nueva conversación)**
   - [ ] Hacer pregunta: "¿Cuál es el precio del CRM?"
   - [ ] Respuesta se genera
   - [ ] Respuesta es correcta y relevante
   - [ ] Fuentes citadas aparecen
   - [ ] Tokens y coste se muestran

2. ✅ **Segunda consulta (misma conversación)**
   - [ ] Hacer pregunta de seguimiento: "¿Hay descuentos disponibles?"
   - [ ] Respuesta usa contexto de conversación anterior
   - [ ] Respuesta coherente

3. ✅ **Nueva conversación**
   - [ ] Click en "➕ Nueva"
   - [ ] Conversación se limpia
   - [ ] Hacer nueva pregunta
   - [ ] Nueva conversación se crea

4. ✅ **Cambiar entre conversaciones**
   - [ ] Usar dropdown de conversaciones
   - [ ] Seleccionar conversación anterior
   - [ ] Historial se carga correctamente
   - [ ] Todos los mensajes visibles

### 3.3 Calidad de Respuestas

Test con preguntas específicas:

1. ✅ **Pregunta directa**
   - Pregunta: "¿Cuánto cuesta el Producto A?"
   - [ ] Respuesta correcta: 299€/mes
   - [ ] Cita fuente correcta
   - [ ] No inventa información

2. ✅ **Pregunta compleja**
   - Pregunta: "¿Qué descuentos tenemos para una startup con 25 usuarios?"
   - [ ] Menciona descuento de startups (15%)
   - [ ] Menciona descuento por volumen (10% por >20 usuarios)
   - [ ] Combina información de múltiples fuentes

3. ✅ **Pregunta sin respuesta en documentación**
   - Pregunta: "¿Cuál es el horario de atención?"
   - [ ] Sistema indica que no encuentra info
   - [ ] No inventa respuesta
   - [ ] Sugiere contactar con otro departamento

4. ✅ **Pregunta de seguimiento**
   - Pregunta 1: "Háblame del Producto B"
   - Pregunta 2: "¿Cuál es su precio?"
   - [ ] Segunda respuesta usa contexto
   - [ ] Responde sobre Producto B, no A

---

## TEST 4: Rendimiento y Estabilidad

### 4.1 Carga Múltiple

1. ✅ **Múltiples usuarios simultáneos**
   - [ ] Abrir 3+ pestañas con diferentes usuarios
   - [ ] Hacer queries simultáneas
   - [ ] Todas responden correctamente
   - [ ] No hay conflictos de sesión

2. ✅ **Consultas rápidas sucesivas**
   - [ ] Hacer 10 queries seguidas sin esperar
   - [ ] Todas se procesan
   - [ ] No hay timeouts
   - [ ] Orden de respuestas correcto

### 4.2 Manejo de Errores

1. ✅ **Backend caído**
```bash
   docker-compose stop backend
```
   - [ ] Frontend muestra error claro
   - [ ] No crash de la aplicación
   - [ ] Reiniciar backend:
```bash
   docker-compose start backend
```
   - [ ] Sistema se recupera automáticamente

2. ✅ **Token expirado**
   - [ ] Esperar expiración (o modificar JWT_EXPIRATION_MINUTES a 1)
   - [ ] Intentar hacer query
   - [ ] Sistema redirige a login
   - [ ] Re-login funciona

3. ✅ **Query muy larga**
   - [ ] Hacer pregunta de 500+ palabras
   - [ ] Sistema maneja correctamente
   - [ ] Respuesta generada o error claro

---

## TEST 5: UI/UX

### 5.1 Responsividad

1. ✅ **Desktop**
   - [ ] Layout correcto en 1920x1080
   - [ ] Sidebar visible
   - [ ] Chat ocupa espacio adecuado

2. ✅ **Tablet**
   - [ ] Resize a 768px ancho
   - [ ] Layout se adapta
   - [ ] Todo funcional

3. ✅ **Mobile** (si aplica)
   - [ ] Resize a 375px
   - [ ] Sidebar colapsa o se oculta
   - [ ] Chat usable

### 5.2 Accesibilidad

1. ✅ **Navegación con teclado**
   - [ ] Tab navega entre elementos
   - [ ] Enter envía mensajes
   - [ ] Esc cierra modales

2. ✅ **Contraste y legibilidad**
   - [ ] Texto legible en todos los fondos
   - [ ] Colores no causan fatiga visual

---

## TEST 6: Seguridad

### 6.1 Autenticación

1. ✅ **Acceso no autorizado**
   - [ ] Sin login, ir a http://localhost:8501
   - [ ] Redirect automático a login
   - [ ] No se puede acceder sin autenticación

2. ✅ **Separación de roles**
   - [ ] Usuario normal no ve opciones admin
   - [ ] Usuario normal no puede acceder a /admin/* endpoints
   - [ ] Admin puede acceder a todo

### 6.2 Datos

1. ✅ **Aislamiento de conversaciones**
   - [ ] Usuario A no puede ver conversaciones de Usuario B
   - [ ] Intentar acceder a UUID de otra conversación
   - [ ] Error 403 o 404 apropiado

---

## ✅ CHECKLIST FINAL

Marcar todos los items probados:

- [ ] Sistema se despliega correctamente
- [ ] Login funciona (admin y usuario)
- [ ] Gestión de usuarios completa
- [ ] Dashboard muestra métricas
- [ ] Documentos se pueden subir y eliminar
- [ ] Reindexación funciona
- [ ] Queries RAG generan respuestas correctas
- [ ] Citas de fuentes funcionan
- [ ] Tracking de tokens y costes preciso
- [ ] Conversaciones se guardan y recuperan
- [ ] Múltiples usuarios simultáneos OK
- [ ] Manejo de errores robusto
- [ ] UI responsive
- [ ] Seguridad: roles y permisos OK

---

## 📊 RESULTADOS

**Fecha del test:** _______________  
**Testeado por:** _______________  
**Tests pasados:** _____ / _____  
**Tests fallados:** _____  

**Notas adicionales:**
_______________________________________________
_______________________________________________
_______________________________________________

**Estado final:** ☐ APROBADO  ☐ APROBADO CON OBSERVACIONES  ☐ REQUIERE CORRECCIONES
