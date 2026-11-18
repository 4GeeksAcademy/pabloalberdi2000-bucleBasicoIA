"""
Pure Python AI Agent for Inventory Management using Function Calling.
No frameworks (no LangChain, no LlamaIndex, no AutoGen).
Manual agentic loop with LLM provider SDK + HTTP tool calls.
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional
import httpx

# LLM configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")  # or "openai"
LLM_MODEL = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
LLM_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Paths
CONVERSATION_LOG = Path(__file__).parent / "conversation_log.csv"
CONVERSATION_LOG.parent.mkdir(exist_ok=True)

# Ensure log file has headers
if not CONVERSATION_LOG.exists():
    with open(CONVERSATION_LOG, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["actor", "message", "tool_call", "timestamp"])


def log_event(actor: str, message: str, tool_call: str = ""):
    """Log an event to the conversation log (append-only)."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    with open(CONVERSATION_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([actor, message, tool_call, timestamp])


def get_tools_definitions() -> list[dict]:
    """Return structured tool definitions for LLM function calling."""
    return [
        {
            "name": "get_inventory",
            "description": "Retrieve the complete inventory list with product IDs, names, quantities, and units",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "add_product",
            "description": "Add a new product to the inventory with name, quantity, and unit of measurement",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Product name (e.g., 'Café Arábica', 'Leche de Avena')"
                    },
                    "quantity": {
                        "type": "number",
                        "description": "Initial quantity (must be >= 0)"
                    },
                    "unit": {
                        "type": "string",
                        "description": "Unit of measurement (e.g., 'kg', 'litros', 'unidades', 'paquetes')"
                    }
                },
                "required": ["name", "quantity", "unit"]
            }
        },
        {
            "name": "update_stock",
            "description": "Update stock quantity for a product using a delta (positive for delivery/inbound, negative for sales/outbound)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "The product ID to update"
                    },
                    "delta": {
                        "type": "number",
                        "description": "Change in quantity (e.g., +5 for delivery, -3 for sales)"
                    }
                },
                "required": ["product_id", "delta"]
            }
        },
        {
            "name": "get_stock_alerts",
            "description": "Retrieve all products with stock below the alert threshold (default: 10 units)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "threshold": {
                        "type": "integer",
                        "description": "Alert threshold in units (default: 10)"
                    }
                },
                "required": []
            }
        }
    ]


def call_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool call against the FastAPI inventory API."""
    with httpx.Client(timeout=10.0) as client:
        try:
            if tool_name == "get_inventory":
                response = client.get(f"{API_BASE_URL}/inventory")
                response.raise_for_status()
                return json.dumps(response.json())
            
            elif tool_name == "add_product":
                payload = {
                    "name": tool_input.get("name"),
                    "quantity": tool_input.get("quantity"),
                    "unit": tool_input.get("unit")
                }
                response = client.post(f"{API_BASE_URL}/inventory", json=payload)
                response.raise_for_status()
                return json.dumps(response.json())
            
            elif tool_name == "update_stock":
                product_id = tool_input.get("product_id")
                payload = {"delta": tool_input.get("delta")}
                response = client.patch(f"{API_BASE_URL}/inventory/{product_id}", json=payload)
                response.raise_for_status()
                return json.dumps(response.json())
            
            elif tool_name == "get_stock_alerts":
                threshold = tool_input.get("threshold", 10)
                response = client.get(f"{API_BASE_URL}/inventory/alerts", params={"threshold": threshold})
                response.raise_for_status()
                return json.dumps(response.json())
            
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"API error: {e.response.text}"})
        except Exception as e:
            return json.dumps({"error": str(e)})


def call_llm(messages: list[dict]) -> dict:
    """Call the LLM provider with the conversation history and tool definitions."""
    if not LLM_API_KEY:
        raise ValueError(f"API key not found. Set {LLM_PROVIDER.upper()}_API_KEY environment variable")
    
    if LLM_PROVIDER == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=LLM_API_KEY)
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=4096,
            system=(
                "You are a helpful AI assistant for a coffee shop inventory system. "
                "Help the user manage their stock, record deliveries, process sales, and check for low-stock alerts. "
                "Be concise and professional in your responses. Use Spanish for greetings and normal communication with the user."
            ),
            tools=get_tools_definitions(),
            messages=messages
        )
        return {
            "content": response.content,
            "stop_reason": response.stop_reason
        }
    
    elif LLM_PROVIDER == "openai":
        import openai
        client = openai.OpenAI(api_key=LLM_API_KEY)
        response = client.chat.completions.create(
            model=LLM_MODEL,
            max_tokens=4096,
            system=(
                "You are a helpful AI assistant for a coffee shop inventory system. "
                "Help the user manage their stock, record deliveries, process sales, and check for low-stock alerts. "
                "Be concise and professional in your responses. Use Spanish for greetings and normal communication with the user."
            ),
            tools=[{"type": "function", "function": tool} for tool in get_tools_definitions()],
            messages=messages
        )
        return {
            "content": response.choices[0].message.content or "",
            "tool_calls": response.choices[0].message.tool_calls,
            "stop_reason": response.choices[0].finish_reason
        }
    
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")


def run_agent():
    """Run the main agentic loop."""
    print("\n" + "="*60)
    print("🏪 Asistente de Inventario para Cafeterías")
    print("="*60)
    print("\nBienvenido. Puedes:")
    print("  • Ver el inventario actual")
    print("  • Añadir nuevos productos")
    print("  • Registrar entregas o ventas (actualizar stock)")
    print("  • Consultar productos con bajo stock")
    print("\nEscribe 'salir' para terminar.\n")
    
    conversation_history = []
    
    while True:
        # Step 1: Observe - Get user input
        user_input = input("👤 Tú: ").strip()
        
        if user_input.lower() in ("salir", "exit", "quit"):
            print("\n¡Hasta luego! El registro de la sesión se guardó en conversation_log.csv")
            log_event("user", "salir", "")
            break
        
        if not user_input:
            continue
        
        # Log user message
        log_event("user", user_input, "")
        
        # Add user message to conversation history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Step 2: Think - Call LLM with function definitions
        print("\n🤖 Agente: Pensando...", end=" ", flush=True)
        
        try:
            llm_response = call_llm(conversation_history)
        except Exception as e:
            print(f"\n❌ Error al contactar LLM: {e}")
            log_event("agent", f"Error: {str(e)}", "")
            continue
        
        print("✓")
        
        # Determine if we have tool calls to process
        tool_calls = []
        agent_text = None
        
        if LLM_PROVIDER == "anthropic":
            # Anthropic returns content blocks
            for block in llm_response["content"]:
                if hasattr(block, "text"):
                    agent_text = block.text
                elif hasattr(block, "type") and block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
        elif LLM_PROVIDER == "openai":
            # OpenAI returns tool_calls list
            if isinstance(llm_response["content"], str):
                agent_text = llm_response["content"]
            if hasattr(llm_response, "tool_calls") and llm_response["tool_calls"]:
                for tc in llm_response["tool_calls"]:
                    tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "input": json.loads(tc.function.arguments)
                    })
        
        # Step 3 & 4: Act & Update - Execute tool calls if any
        if tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["input"]
                tool_id = tool_call["id"]
                
                print(f"  🔧 Ejecutando herramienta: {tool_name}")
                log_event("agent", f"Ejecutando: {tool_name} con entrada: {json.dumps(tool_input)}", tool_name)
                
                # Execute tool
                tool_result = call_tool(tool_name, tool_input)
                log_event("tool", tool_result, tool_name)
                
                # Add tool result to conversation history
                if LLM_PROVIDER == "anthropic":
                    conversation_history.append({
                        "role": "assistant",
                        "content": [
                            {"type": "tool_use", "id": tool_id, "name": tool_name, "input": tool_input}
                        ]
                    })
                    conversation_history.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": tool_result
                            }
                        ]
                    })
                elif LLM_PROVIDER == "openai":
                    # For OpenAI, we continue in the same message
                    conversation_history.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "name": tool_name,
                        "content": tool_result
                    })
            
            # Step 5: Repeat - Call LLM again to generate final response
            print("\n🤖 Agente: Generando respuesta final...", end=" ", flush=True)
            try:
                llm_response = call_llm(conversation_history)
            except Exception as e:
                print(f"\n❌ Error: {e}")
                log_event("agent", f"Error: {str(e)}", "")
                continue
            
            print("✓")
            
            # Extract final text response
            if LLM_PROVIDER == "anthropic":
                for block in llm_response["content"]:
                    if hasattr(block, "text"):
                        agent_text = block.text
            elif LLM_PROVIDER == "openai":
                if isinstance(llm_response["content"], str):
                    agent_text = llm_response["content"]
            
            # Add assistant's final message to history
            if agent_text:
                conversation_history.append({
                    "role": "assistant",
                    "content": agent_text
                })
        else:
            # No tool calls, just add response to history
            if agent_text:
                conversation_history.append({
                    "role": "assistant",
                    "content": agent_text
                })
        
        # Print final agent response
        if agent_text:
            print(f"\n🤖 Agente: {agent_text}\n")
            log_event("agent", agent_text, "")
        else:
            print("\n(Sin respuesta)\n")


if __name__ == "__main__":
    run_agent()
