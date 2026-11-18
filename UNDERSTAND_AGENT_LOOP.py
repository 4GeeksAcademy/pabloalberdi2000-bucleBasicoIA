"""
EXAMPLE: How the Agent Loop Works - Step by Step

This is a conceptual walkthrough of how the agentic loop operates.
Run this to understand the flow before using the actual agent.
"""

print("""
════════════════════════════════════════════════════════════════
   🤖 AGENTE IA - FLUJO DE TRABAJO PASO A PASO
════════════════════════════════════════════════════════════════

Imagina que el usuario pregunta:
  👤 "¿Cuántos productos con bajo stock tenemos?"

El agente ejecuta este bucle:


PASO 1️⃣ : OBSERVAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Lee la pregunta del usuario
✓ La añade al historial de la sesión


PASO 2️⃣ : PENSAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Envía al LLM:
  - Toda la historia de la conversación (contexto)
  - Las 4 herramientas disponibles (definiciones JSON Schema):
    
    Tool 1: get_inventory()
      → Devuelve lista de todos los productos
    
    Tool 2: add_product(name, quantity, unit)
      → Añade un nuevo producto
    
    Tool 3: update_stock(product_id, delta)
      → Actualiza stock (+/-) para un producto
    
    Tool 4: get_stock_alerts(threshold)
      → Devuelve productos con stock bajo
  
✓ El LLM analiza la pregunta y decide:
  "El usuario quiere alertas de bajo stock... debo usar get_stock_alerts()"


PASO 3️⃣ : ACTUAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ El agente recibe: "Ejecutar tool: get_stock_alerts()"
✓ Hace un HTTP PATCH a: http://localhost:8000/inventory/alerts
✓ Respuesta JSON:
  
  [
    {
      "product_id": 5,
      "name": "Chocolate en Polvo",
      "quantity": 5.5,
      "unit": "kg",
      "alert_threshold": 10
    },
    {
      "product_id": 10,
      "name": "Té Negro",
      "quantity": 2,
      "unit": "kg",
      "alert_threshold": 10
    }
  ]


PASO 4️⃣ : ACTUALIZAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ El agente inyecta el resultado en el historial de conversación:
  
  Mensaje 1: User - "¿Cuántos productos con bajo stock tenemos?"
  Mensaje 2: Assistant - "Voy a consultar las alertas"
  Mensaje 3: Tool Result - [JSON con alertas]


PASO 5️⃣ : REPETIR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Envía la historia COMPLETA + resultado de la tool al LLM otra vez
✓ El LLM ahora tiene toda la información y genera una respuesta natural


PASO 6️⃣ : IMPRIMIR Y REGISTRAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ El agente imprime en consola:
  
  🤖 Agente: "Tenemos 2 productos con bajo stock:
  
  1. Chocolate en Polvo: 5.5 kg (alerta en 10 kg)
  2. Té Negro: 2 kg (alerta en 10 kg)
  
  Te recomiendo reordenar estos productos pronto."

✓ Escribe en conversation_log.csv:
  
  Row 1: actor=user, message=¿Cuántos productos..., tool_call="", timestamp=2024-11-18T16:30:45Z
  Row 2: actor=agent, message=Ejecutando: get_stock_alerts, tool_call=get_stock_alerts, timestamp=...
  Row 3: actor=tool, message=[JSON alerts], tool_call=get_stock_alerts, timestamp=...
  Row 4: actor=agent, message=Tenemos 2 productos con bajo stock..., tool_call="", timestamp=...


════════════════════════════════════════════════════════════════
OTRO EJEMPLO: Registrar una Venta
════════════════════════════════════════════════════════════════

User Input:
  👤 "Se vendieron 10 vasos de papel esta mañana"

LLM Analysis:
  → "El usuario está registrando una venta. Necesito:
     1. Consultar el inventario para identificar 'vasos de papel'
     2. Actualizar el stock con delta = -10"

Agent Actions:
  1. HTTP GET http://localhost:8000/inventory
     Resultado: Encuentra product_id=3 (Vasos de Papel)
  
  2. HTTP PATCH http://localhost:8000/inventory/3
     Payload: {"delta": -10}
     Resultado: Vasos: 150 → 140

LLM Response:
  "✓ Venta registrada. Los vasos de papel bajaron de 150 a 140 unidades."


════════════════════════════════════════════════════════════════
LAS 4 HERRAMIENTAS DISPONIBLES
════════════════════════════════════════════════════════════════

1. get_inventory()
   Parámetros: Ninguno
   Devuelve: Lista de todos los productos con ID, nombre, cantidad y unidad
   Uso: "¿Qué tenemos en stock?" o "Muéstrame el inventario"

2. add_product(name, quantity, unit)
   Parámetros: 
     - name (string): Nombre del producto
     - quantity (number): Cantidad inicial
     - unit (string): Unidad (kg, litros, unidades, etc.)
   Devuelve: El producto creado con ID asignado
   Uso: "Añade café premium, tengo 5 kg" o "Nuevo producto: leche de avena, 20 litros"

3. update_stock(product_id, delta)
   Parámetros:
     - product_id (integer): ID del producto a actualizar
     - delta (number): Cambio en cantidad (+5 para entrega, -3 para venta)
   Devuelve: Producto actualizado con nueva cantidad
   Uso: "Llegó una entrega de 25 kg de café" o "Se vendieron 10 vasos"

4. get_stock_alerts(threshold)
   Parámetros:
     - threshold (integer, opcional): Límite de stock (default: 10)
   Devuelve: Lista de productos por debajo del umbral
   Uso: "¿Qué productos están por agotarse?" o "Alertas de bajo stock"


════════════════════════════════════════════════════════════════
EJEMPLO REAL: Sesión Completa
════════════════════════════════════════════════════════════════

👤 Tú: ¿Qué tenemos en stock?
🤖 Agente: Pensando... ✓
  🔧 Ejecutando herramienta: get_inventory
🤖 Agente: Generando respuesta final... ✓
🤖 Agente: Tenemos 10 productos:
  1. Café Arábica Premium: 25.5 kg
  2. Leche de Avena: 12 litros
  ...

👤 Tú: Acaba de llegar café, +20 kg
🤖 Agente: Pensando... ✓
  🔧 Ejecutando herramienta: get_inventory  (para identificar el café)
  🔧 Ejecutando herramienta: update_stock   (product_id=1, delta=20)
🤖 Agente: Generando respuesta final... ✓
🤖 Agente: ✓ Entrega registrada. Café Arábica Premium pasó de 25.5 kg a 45.5 kg

👤 Tú: ¿Qué productos están bajos?
🤖 Agente: Pensando... ✓
  🔧 Ejecutando herramienta: get_stock_alerts
🤖 Agente: Generando respuesta final... ✓
🤖 Agente: 3 productos con stock bajo:
  ⚠️ Chocolate en Polvo: 5.5 kg
  ⚠️ Servilletas: 8 paquetes
  ⚠️ Té Negro: 2 kg

👤 Tú: salir
¡Hasta luego! El registro de la sesión se guardó en conversation_log.csv


════════════════════════════════════════════════════════════════
ARCHIVO DE LOG GENERADO (conversation_log.csv)
════════════════════════════════════════════════════════════════

actor,message,tool_call,timestamp
user,¿Qué tenemos en stock?,,2024-11-18T16:30:45.123Z
agent,Ejecutando: get_inventory con entrada: {},get_inventory,2024-11-18T16:30:46.456Z
tool,"[{"product_id": 1, "name": "Café Arábica Premium"...}]",get_inventory,2024-11-18T16:30:46.789Z
agent,Tenemos 10 productos:...,, 2024-11-18T16:30:47.012Z
user,Acaba de llegar café +20 kg,,2024-11-18T16:30:50.100Z
agent,Ejecutando: get_inventory con entrada: {},get_inventory,2024-11-18T16:30:51.200Z
tool,"[{"product_id": 1, "name": "Café Arábica Premium", "quantity": 25.5...}]",get_inventory,2024-11-18T16:30:51.500Z
agent,Ejecutando: update_stock con entrada: {"product_id": 1 "delta": 20},update_stock,2024-11-18T16:30:52.100Z
tool,"{"product_id": 1, "name": "Café Arábica Premium", "quantity": 45.5...}",update_stock,2024-11-18T16:30:52.400Z
agent,✓ Entrega registrada. Café Arábica Premium pasó de 25.5 kg a 45.5 kg,,2024-11-18T16:30:52.700Z
user,salir,,2024-11-18T16:30:55.000Z


════════════════════════════════════════════════════════════════

¡Ahora ya entiendes cómo funciona el bucle! 🚀

Para ejecutar el sistema real, ve a QUICKSTART.md
""")
