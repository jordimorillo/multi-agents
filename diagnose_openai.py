#!/usr/bin/env python3
"""
Script de diagnóstico de OpenAI API
Verifica el estado de la API key y la cuenta
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"ℹ️  {text}")

def main():
    print_header("🔍 DIAGNÓSTICO DE OPENAI API")
    
    # Cargar .env
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print_error("No se encontró OPENAI_API_KEY en .env")
        sys.exit(1)
    
    # Mostrar info de la key
    print_info(f"API Key encontrada: {api_key[:20]}...{api_key[-4:]}")
    print_info(f"Longitud: {len(api_key)} caracteres")
    print_info(f"Tipo: {'Project' if api_key.startswith('sk-proj-') else 'User' if api_key.startswith('sk-') else 'Desconocido'}")
    
    # Crear cliente
    print_header("1️⃣ Verificando conexión básica")
    try:
        client = OpenAI(api_key=api_key)
        print_success("Cliente OpenAI creado correctamente")
    except Exception as e:
        print_error(f"Error creando cliente: {e}")
        sys.exit(1)
    
    # Test 1: Listar modelos disponibles
    print_header("2️⃣ Verificando modelos disponibles")
    try:
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        
        print_success(f"Se pueden listar modelos: {len(model_ids)} modelos encontrados")
        
        # Verificar modelos específicos
        important_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4-turbo']
        print_info("\nModelos importantes:")
        for model in important_models:
            if any(model in m for m in model_ids):
                print_success(f"  {model} - DISPONIBLE")
            else:
                print_warning(f"  {model} - NO DISPONIBLE")
        
        # Mostrar todos los modelos GPT
        print_info("\nTodos los modelos GPT disponibles:")
        gpt_models = [m for m in model_ids if 'gpt' in m.lower()]
        for model in sorted(gpt_models)[:20]:  # Primeros 20
            print(f"  • {model}")
        if len(gpt_models) > 20:
            print(f"  ... y {len(gpt_models) - 20} más")
            
    except Exception as e:
        print_error(f"Error listando modelos: {e}")
        print_warning("Esto puede indicar un problema con la API key o la cuenta")
    
    # Test 2: Hacer una llamada simple
    print_header("3️⃣ Test de llamada a la API (gpt-3.5-turbo)")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Di hola"}],
            max_tokens=10
        )
        print_success("Llamada exitosa a gpt-3.5-turbo")
        print_info(f"Respuesta: {response.choices[0].message.content}")
    except Exception as e:
        print_error(f"Error en llamada a gpt-3.5-turbo: {e}")
        print_warning("La API key no tiene permisos para gpt-3.5-turbo")
    
    # Test 3: Intentar con gpt-4
    print_header("4️⃣ Test de llamada a la API (gpt-4)")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Di hola"}],
            max_tokens=10
        )
        print_success("Llamada exitosa a gpt-4")
        print_info(f"Respuesta: {response.choices[0].message.content}")
    except Exception as e:
        print_error(f"Error en llamada a gpt-4: {e}")
        print_warning("La API key no tiene permisos para gpt-4")
    
    # Test 4: Intentar con gpt-4o
    print_header("5️⃣ Test de llamada a la API (gpt-4o)")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Di hola"}],
            max_tokens=10
        )
        print_success("Llamada exitosa a gpt-4o")
        print_info(f"Respuesta: {response.choices[0].message.content}")
    except Exception as e:
        print_error(f"Error en llamada a gpt-4o: {e}")
        print_warning("La API key no tiene permisos para gpt-4o")
    
    # Verificar límites y uso
    print_header("6️⃣ Información de la cuenta")
    try:
        # Intentar obtener info de la organización (si está disponible)
        print_info("Para ver límites y uso, visita:")
        print_info("  • https://platform.openai.com/usage")
        print_info("  • https://platform.openai.com/account/limits")
        print_info("  • https://platform.openai.com/api-keys")
    except Exception as e:
        print_warning(f"No se pudo obtener info adicional: {e}")
    
    # Test con LangChain
    print_header("7️⃣ Test con LangChain (como en el sistema)")
    try:
        from langchain_openai import ChatOpenAI
        
        # Exactamente como lo hace el sistema
        os.environ['OPENAI_API_KEY'] = api_key
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
        
        response = llm.invoke("Di hola")
        print_success("LangChain funciona correctamente")
        print_info(f"Respuesta: {response.content}")
        
    except Exception as e:
        print_error(f"Error con LangChain: {e}")
        print_warning("El problema está en la integración con LangChain")
        import traceback
        print(f"\n{RED}Traceback completo:{RESET}")
        traceback.print_exc()
    
    # Resumen final
    print_header("📊 RESUMEN Y RECOMENDACIONES")
    print_info("Si ves errores 401 (Unauthorized):")
    print("  1. La API key puede estar revocada o expirada")
    print("  2. Verifica en: https://platform.openai.com/api-keys")
    print("  3. Regenera la API key si es necesario")
    print()
    print_info("Si ves errores 429 (Rate Limit):")
    print("  1. Has excedido los límites de uso")
    print("  2. Verifica en: https://platform.openai.com/usage")
    print("  3. Espera o actualiza tu plan")
    print()
    print_info("Si ves errores de modelo no disponible:")
    print("  1. Tu cuenta no tiene acceso a ese modelo")
    print("  2. Verifica tu plan en: https://platform.openai.com/account/limits")
    print("  3. Actualiza tu plan si es necesario")
    print()

if __name__ == "__main__":
    main()
