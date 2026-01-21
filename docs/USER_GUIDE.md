# 📖 Guía de Usuario - Commercial RAG System

Bienvenido al Sistema de Consultas Empresariales con IA.

## 🎯 ¿Qué es este sistema?

Este sistema te permite hacer preguntas en lenguaje natural sobre la documentación de la empresa y recibir respuestas precisas e inmediatas, como si hablaras con un experto que conoce todos nuestros documentos.

---

## 🚀 Primeros Pasos

### 1. Acceder al Sistema

1. Abre tu navegador web
2. Ve a la URL proporcionada por tu administrador: `http://[servidor]:8501`
3. Verás la pantalla de inicio de sesión

### 2. Iniciar Sesión

1. Ingresa tu **usuario** (proporcionado por el administrador)
2. Ingresa tu **contraseña**
3. Click en **"Iniciar Sesión"**

**Primera vez:**
- Se recomienda cambiar tu contraseña
- Contacta al administrador si olvidaste tus credenciales

---

## 💬 Hacer Consultas

### Tu Primera Pregunta

1. Verás un cuadro de texto que dice "Escribe tu pregunta aquí..."
2. Escribe tu pregunta de forma natural, como si hablaras con un compañero
3. Presiona **Enter** o click en el botón de enviar

**Ejemplo:**
¿Cuál es el precio del CRM Enterprise?

### Entender la Respuesta

La respuesta incluye:
- **Texto de la respuesta**: La información que pediste
- **📚 Fuentes**: Documentos de donde se obtuvo la información
- **💰 Coste** y **📊 Tokens**: Métricas de uso (informativo)

### Preguntas de Seguimiento

Puedes hacer preguntas adicionales en la misma conversación:
Tú: ¿Cuál es el precio del CRM?
Sistema: El CRM Enterprise cuesta 299€/mes por usuario...
Tú: ¿Hay descuentos disponibles?
Sistema: Sí, hay un descuento del 10% para equipos de 20+...

El sistema **recuerda** el contexto de la conversación.

---

## 📋 Gestionar Conversaciones

### Ver Conversaciones Anteriores

1. En la parte superior verás un **dropdown**
2. Click para ver lista de tus conversaciones
3. Selecciona una para verla completa

### Crear Nueva Conversación

1. Click en el botón **"➕ Nueva"**
2. Empieza desde cero
3. Tu conversación anterior se guarda automáticamente

### Cambiar Título de Conversación

(Si está habilitado)
1. Click en el título de la conversación
2. Editar nombre
3. Guardar

---

## 💡 Consejos para Mejores Resultados

### ✅ Buenas Prácticas

**Sé específico:**
❌ "Dime sobre productos"
✅ "¿Cuáles son las características del Producto B?"

**Pregunta una cosa a la vez:**
❌ "¿Cuánto cuesta el CRM y cuáles son sus características y hay descuentos y cómo se paga?"
✅ "¿Cuánto cuesta el CRM Enterprise?"

**Usa el contexto:**
Si ya mencionaste algo, puedes referirte a ello:
Tú: ¿Qué productos de software vendemos?
Sistema: Vendemos CRM Enterprise, herramientas de BI...
Tú: ¿Cuál es el más vendido?  ← El sistema sabe que hablas de los productos mencionados

### 📝 Tipos de Preguntas que Funciona Bien

✅ **Preguntas de información:**
- "¿Cuál es el precio de X?"
- "¿Qué características tiene Y?"
- "¿Cuál es la política de devoluciones?"

✅ **Comparaciones:**
- "¿Cuál es la diferencia entre Producto A y B?"
- "¿Qué plan me recomiendas para una empresa de 50 personas?"

✅ **Procedimientos:**
- "¿Cómo solicito un descuento para ONGs?"
- "¿Cuál es el proceso de pago?"

❌ **Preguntas que NO funcionan:**
- Información no en documentos: "¿Cuál es el email de Juan?"
- Tiempo real: "¿Cuántas ventas hicimos hoy?"
- Opiniones subjetivas: "¿Cuál es el mejor producto?"

---

## ⚙️ Configuración Personal

### Ver Mi Perfil

1. Click en tu nombre en el sidebar
2. Verás tu información básica

### Cerrar Sesión

1. Click en **"🚪 Cerrar Sesión"** en el sidebar
2. Serás redirigido al login

---

## ❓ Preguntas Frecuentes

**P: ¿El sistema inventa respuestas?**
R: No. El sistema solo responde basándose en la documentación empresarial. Si no encuentra información, te lo dirá claramente.

**P: ¿Se guardan mis conversaciones?**
R: Sí, todas tus conversaciones se guardan y puedes verlas cuando quieras. Solo tú y los administradores pueden verlas.

**P: ¿Cuántas preguntas puedo hacer?**
R: No hay límite técnico, pero se registra el uso para estadísticas internas.

**P: ¿Puedo compartir una conversación con un compañero?**
R: Actualmente no hay función de compartir. Copia y pega la información si necesitas enviarla.

**P: La respuesta no es correcta, ¿qué hago?**
R: Contacta al administrador reportando la pregunta y respuesta. Pueden mejorar la documentación o reportar el problema.

**P: ¿Puedo usar el sistema desde mi móvil?**
R: Sí, el sistema es responsive y funciona en navegadores móviles.

---

## 🆘 Soporte

### Problemas Técnicos

**Si no puedes iniciar sesión:**
- Verifica usuario y contraseña
- Contacta al administrador para resetear password

**Si el sistema no responde:**
- Refresca la página (F5)
- Si persiste, contacta al administrador

**Si una respuesta parece incorrecta:**
- Verifica las fuentes citadas
- Reporta al administrador con captura de pantalla

### Contacto

- **Email:** [soporte@tuempresa.com]
- **Teléfono:** [XXX-XXX-XXXX]
- **Chat interno:** [Canal #rag-soporte]

---

## 🎓 Ejemplos de Uso

### Ejemplo 1: Consulta de Precios
Tú: Necesito saber el precio del CRM para un cliente
Sistema: El CRM Enterprise tiene un precio de 299€/mes
por usuario. Hay un descuento del 10% para equipos de
20 o más usuarios.
📚 Fuente: productos.txt
Tú: ¿Y si es para una startup?
Sistema: Las startups (empresas con menos de 2 años)
tienen un descuento adicional del 15% sobre el precio
estándar.
📚 Fuente: politicas.txt

### Ejemplo 2: Información de Servicios
Tú: Un cliente pregunta sobre consultoría IT
Sistema: Ofrecemos servicios de consultoría IT a 150€/hora.
Tenemos paquetes disponibles:

20 horas
50 horas
100 horas

Con descuentos progresivos según el paquete.
📚 Fuente: productos.txt

### Ejemplo 3: Políticas
Tú: ¿Cuál es nuestra política de garantía?
Sistema: Ofrecemos una garantía de satisfacción de 30 días
en todos nuestros productos. Si el cliente no está satisfecho,
realizamos una devolución del 100% del importe. Además,
incluimos soporte técnico gratuito durante los primeros 3 meses.
📚 Fuente: politicas.txt

---

**¡Bienvenido al sistema! Estamos aquí para ayudarte a responder a tus clientes más rápido y con mayor precisión.**

---

**Versión:** 1.0 | **Última actualización:** Enero 2026
