# 🏪 Sistema de Control de Inventario con Agente de IA

Un asistente conversacional moderno para cafeterías que permite gestionar inventario mediante lenguaje natural, sin formularios complejos. Construido con **FastAPI + Python Puro** (cero frameworks de agentes como LangChain).

---

## 📋 Características

✅ **API REST en FastAPI** con persistencia en CSV  
✅ **Agente de IA en Python Puro** (sin LangChain, AutoGen, etc.)  
✅ **Function Calling Manual** – el agente razona y ejecuta herramientas vía HTTP  
✅ **Logging Append-Only** – cada evento se registra en `conversation_log.csv`  
✅ **Interfaz Conversacional CLI** – interactúa con el agente por terminal  
✅ **Soporte para dos proveedores LLM** – Anthropic Claude o OpenAI  

---

## 🛠️ Requisitos

- **Python 3.10+**
- **pip** (gestor de paquetes de Python)

### Dependencias

```
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
httpx>=0.25.0
anthropic>=0.7.0  # Para usar Anthropic Claude
openai>=1.0.0     # Para usar OpenAI
```

---

## 📦 Instalación

1. **Clona o descarga el repositorio**
   ```bash
   git clone <repository-url>
   cd pabloalberdi2000-bucleBasicoIA
   ```

2. **Crea un entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install fastapi uvicorn pydantic httpx anthropic openai
   ```

4. **Configura las variables de entorno**
   
   Para **Anthropic Claude** (recomendado):
   ```bash
   export ANTHROPIC_API_KEY="tu-clave-aqui"
   export LLM_PROVIDER="anthropic"
   export LLM_MODEL="claude-3-5-sonnet-20241022"
   ```
   
   Para **OpenAI**:
   ```bash
   export OPENAI_API_KEY="tu-clave-aqui"
   export LLM_PROVIDER="openai"
   export LLM_MODEL="gpt-4o-mini"
   ```

---

## 🚀 Cómo Iniciar

### Paso 1: Arranca la API FastAPI

En una **primera terminal**:

```bash
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

Verás algo como:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Verifica que la API esté activa:**
```bash
curl http://localhost:8000/health
# Respuesta esperada: {"status":"ok","message":"Inventory API is running"}
```

### Paso 2: Inicia el Agente en otra Terminal

En una **segunda terminal** (con el mismo entorno virtual activo):

```bash
python agent.py
```

Verás:
```
============================================================
🏪 Asistente de Inventario para Cafeterías
============================================================

Bienvenido. Puedes:
  • Ver el inventario actual
  • Añadir nuevos productos
  • Registrar entregas o ventas (actualizar stock)
  • Consultar productos con bajo stock

Escribe 'salir' para terminar.

👤 Tú: 
```

---

## 💬 Ejemplos de Uso

### Consultar Inventario

```
👤 Tú: ¿Cuántos productos tenemos en inventario?

🤖 Agente: Pensando... ✓
  🔧 Ejecutando herramienta: get_inventory
🤖 Agente: Generando respuesta final... ✓

🤖 Agente: Tenemos 10 productos en inventario:

1. Café Arábica Premium: 25.5 kg
2. Leche de Avena: 12 litros
3. Vasos de Papel 8oz: 150 unidades
4. Azúcar Morena: 8 kg
5. Chocolate en Polvo: 5.5 kg
6. Servilletas: 8 paquetes
7. Hielo: 30 kg
8. Crema Batida: 3 litros
9. Espresso: 15 kg
10. Té Negro: 2 kg
```

### Registrar una Entrega (Stock Positivo)

```
👤 Tú: Acaba de llegar una entrega de 10 kg de café arábica

🤖 Agente: Pensando... ✓
  🔧 Ejecutando herramienta: update_stock
🤖 Agente: Generando respuesta final... ✓

🤖 Agente: ✓ Entrega registrada exitosamente.
El café arábica pasó de 25.5 kg a 35.5 kg.
```

### Registrar una Venta (Stock Negativo)

```
👤 Tú: Se vendieron 5 vasos de papel esta mañana

🤖 Agente: Pensando... ✓
  🔧 Ejecutando herramienta: update_stock
🤖 Agente: Generando respuesta final... ✓

🤖 Agente: Venta registrada. Los vasos de papel bajaron de 150 a 145 unidades.
```

### Consultar Alertas de Stock Bajo

```
👤 Tú: ¿Qué productos tenemos con bajo stock?

🤖 Agente: Pensando... ✓
  🔧 Ejecutando herramienta: get_stock_alerts
🤖 Agente: Generando respuesta final... ✓

🤖 Agente: Tenemos 3 productos con stock bajo (menos de 10 unidades):

1. Chocolate en Polvo: 5.5 kg (alerta en 10 kg)
2. Servilletas: 8 paquetes (alerta en 10 paquetes)
3. Té Negro: 2 kg (alerta en 10 kg)

Te recomiendo reordenar estos productos pronto.
```

### Añadir un Nuevo Producto

```
👤 Tú: Necesito agregar café descafeinado, tengo 12 kg disponibles

🤖 Agente: Pensando... ✓
  🔧 Ejecutando herramienta: add_product
🤖 Agente: Generando respuesta final... ✓

🤖 Agente: ✓ Producto añadido exitosamente.
Café Descafeinado - 12 kg (ID: 11)
```

---

## 📁 Estructura de Archivos

```
pabloalberdi2000-bucleBasicoIA/
├── api/
│   └── app.py                 # Aplicación FastAPI con endpoints de inventario
├── agent.py                   # Agente en Python puro (bucle agentico manual)
├── products.csv               # Archivo de persistencia de inventario (creado por API)
├── conversation_log.csv       # Log append-only de eventos (creado por agente)
├── README_INVENTORY.md        # Esta documentación
└── README.md                  # Readme original del proyecto
```

---

## 🔧 API REST - Endpoints Disponibles

### 1. `GET /inventory`
Devuelve la lista completa de productos.

**Respuesta (200):**
```json
[
  {
    "product_id": 1,
    "name": "Café Arábica Premium",
    "quantity": 25.5,
    "unit": "kg"
  },
  ...
]
```

---

### 2. `POST /inventory`
Añade un nuevo producto.

**Payload:**
```json
{
  "name": "Nuevo Producto",
  "quantity": 10,
  "unit": "kg"
}
```

**Respuesta (201):**
```json
{
  "product_id": 11,
  "name": "Nuevo Producto",
  "quantity": 10,
  "unit": "kg"
}
```

---

### 3. `PATCH /inventory/{product_id}`
Actualiza el stock con un delta (positivo o negativo).

**Payload:**
```json
{
  "delta": 5
}
```

**Respuesta (200):**
```json
{
  "product_id": 1,
  "name": "Café Arábica Premium",
  "quantity": 30.5,
  "unit": "kg"
}
```

---

### 4. `GET /inventory/alerts`
Devuelve productos con stock bajo (threshold por defecto: 10).

**Query Parameters (opcional):**
- `threshold` (int, default: 10)

**Respuesta (200):**
```json
[
  {
    "product_id": 5,
    "name": "Chocolate en Polvo",
    "quantity": 5.5,
    "unit": "kg",
    "alert_threshold": 10
  },
  ...
]
```

---

### 5. `GET /health`
Verifica que la API esté activa.

**Respuesta (200):**
```json
{
  "status": "ok",
  "message": "Inventory API is running"
}
```

---

## 📊 Archivo de Log: `conversation_log.csv`

Cada evento de la interacción se registra en formato CSV con 4 columnas:

| actor | message | tool_call | timestamp |
|-------|---------|-----------|-----------|
| user | ¿Cuántos productos hay? | | 2024-11-18T16:30:45.123Z |
| agent | Ejecutando: get_inventory con entrada: {} | get_inventory | 2024-11-18T16:30:46.456Z |
| tool | [{"product_id": 1, ...}] | get_inventory | 2024-11-18T16:30:46.789Z |
| agent | Tenemos 10 productos... | | 2024-11-18T16:30:47.012Z |

**Columnas:**
- **actor**: `user`, `agent` o `tool`
- **message**: Contenido del texto o JSON (payload/resultado)
- **tool_call**: Nombre de la herramienta invocada (vacío si no aplica)
- **timestamp**: ISO 8601 UTC (ej: `2024-11-18T16:30:45.123Z`)

---

## 🧠 Arquitectura del Agente

El agente implementa un **bucle agentico manual** sin frameworks:

```
┌─────────────────────────────────────────┐
│ 1. OBSERVAR: Leer input del usuario    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ 2. PENSAR: Enviar historial + tools    │
│    al LLM (Anthropic/OpenAI)           │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼────────┐
         │ ¿Tool calls?   │
         └───┬────────┬───┘
        SÍ │         │ NO
           │         └──────────────────┐
    ┌──────▼─────────┐                 │
    │ 3. ACTUAR:     │                 │
    │ Ejecutar       │                 │
    │ herramientas   │                 │
    │ (HTTP calls)   │                 │
    └──────┬─────────┘                 │
           │                           │
    ┌──────▼─────────────┐             │
    │ 4. ACTUALIZAR:     │             │
    │ Inyectar resultados│             │
    │ en historial       │             │
    └──────┬─────────────┘             │
           │                           │
    ┌──────▼─────────────┐             │
    │ 5. REPETIR:        │             │
    │ Llamar LLM otra vez│             │
    └──────┬─────────────┘             │
           │                           │
           └──────────┬────────────────┘
                      │
         ┌────────────▼────────────────┐
         │ 6. IMPRIMIR respuesta final │
         │    y registrar en log       │
         └────────────┬────────────────┘
                      │
         ┌────────────▼────────────────┐
         │ ¿Continuar? → Volver a 1    │
         │ ¿Salir? → Terminar         │
         └─────────────────────────────┘
```

---

## 🔐 Variables de Entorno

| Variable | Descripción | Valor por Defecto | Obligatoria |
|----------|-------------|-------------------|------------|
| `LLM_PROVIDER` | Proveedor de LLM | `anthropic` | No |
| `LLM_MODEL` | Modelo a usar | `claude-3-5-sonnet-20241022` (Anthropic) | No |
| `ANTHROPIC_API_KEY` | Clave API de Anthropic | - | Sí (si provider=anthropic) |
| `OPENAI_API_KEY` | Clave API de OpenAI | - | Sí (si provider=openai) |
| `API_BASE_URL` | URL base de la API | `http://localhost:8000` | No |

---

## 🐛 Solución de Problemas

### Error: "API key not found"
**Solución:** Asegúrate de haber configurado las variables de entorno:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# o
export OPENAI_API_KEY="sk-..."
```

### Error: "Connection refused" al conectar con la API
**Solución:** Verifica que la API FastAPI esté corriendo en `http://localhost:8000`:
```bash
curl http://localhost:8000/health
```

### Error: "Product already exists"
**Solución:** No puedes añadir dos productos con el mismo nombre. Usa un nombre diferente.

### Error: "Stock cannot be negative"
**Solución:** El delta (cambio en stock) no puede resultar en un número negativo. Por ejemplo, si tienes 5 unidades, no puedes restar 10.

---

## 📝 Notas Técnicas

- **Persistencia Atómica:** La API usa locks (`threading.Lock`) para evitar condiciones de carrera al escribir en CSV.
- **Bucle Agentico Manual:** Implementado con Python puro, sin dependencias externas de orquestación.
- **Function Calling:** El agente recibe definiciones de herramientas en JSON Schema, razona sobre cuál usar, y ejecuta requests HTTP contra la API.
- **Logging Inmediato:** Cada evento se escribe al CSV inmediatamente (append-only), sin riesgo de pérdida de datos.

---

## 📄 Licencia

Este proyecto es de código abierto y forma parte del curriculum de 4Geeks Academy.

---

## 📧 Soporte

Para reportar bugs o sugerencias, abre un issue en el repositorio.

---

**¡Feliz gestión de inventario! 🎉**
