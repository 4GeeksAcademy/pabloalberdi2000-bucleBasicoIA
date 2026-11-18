# 🚀 Quick Start Guide - Sistema de Inventario IA

## 30 segundos: Comenzar ahora

### Opción 1: Scripts automáticos (Recomendado)

#### Terminal 1 - Arranca la API:
```bash
./start-api.sh
```

#### Terminal 2 - Arranca el Agente:
```bash
export ANTHROPIC_API_KEY="tu-clave-aqui"  # O tu clave de OpenAI
./start-agent.sh
```

---

### Opción 2: Comandos manuales

#### Terminal 1 - Setup e instala dependencias:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Terminal 1 - Arranca la API:
```bash
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Setup y arranca el Agente:
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
export ANTHROPIC_API_KEY="tu-clave-aqui"
python agent.py
```

---

## ✨ Primeras Interacciones

Una vez que el agente esté corriendo, prueba estos comandos:

### Ver todo el inventario:
```
👤 Tú: ¿Qué productos tenemos en stock?
```

### Registrar una entrega:
```
👤 Tú: Acaba de llegar café arábica, +20 kg
```

### Registrar una venta:
```
👤 Tú: Se vendieron 5 vasos esta mañana
```

### Consultar alertas:
```
👤 Tú: ¿Qué productos están por agotarse?
```

### Agregar un nuevo producto:
```
👤 Tú: Necesito agregar té verde, tenemos 8 kg
```

---

## 🔑 Variables de Entorno Requeridas

### Para Anthropic Claude (Recomendado):
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export LLM_PROVIDER="anthropic"
export LLM_MODEL="claude-3-5-sonnet-20241022"
```

### Para OpenAI:
```bash
export OPENAI_API_KEY="sk-..."
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4o-mini"
```

---

## 🧪 Verificar que todo funciona

```bash
# Verifica que la API responde
curl http://localhost:8000/health

# O ejecuta el test suite
python test_system.py
```

---

## 📂 Archivos Generados Automáticamente

- **`products.csv`** - Base de datos del inventario (creada por la API)
- **`conversation_log.csv`** - Registro de todas las interacciones

---

## 🐛 Troubleshooting

### "API key not found"
```bash
# Asegúrate de exportar la variable antes de ejecutar:
export ANTHROPIC_API_KEY="tu-clave-aqui"
export OPENAI_API_KEY="tu-clave-aqui"
python agent.py
```

### "Connection refused" (API no responde)
```bash
# Verifica que la API esté corriendo en otra terminal
curl http://localhost:8000/health
```

### "No module named 'anthropic'" o "No module named 'openai'"
```bash
# Instala las dependencias
pip install anthropic openai
```

---

## 📚 Documentación Completa

Para más detalles, lee: [README_INVENTORY.md](./README_INVENTORY.md)

---

**¡Ya estás listo! 🎉**
