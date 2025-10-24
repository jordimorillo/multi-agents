#!/usr/bin/env python3
"""
CLI para ejecutar el sistema multi-agente con comandos simples
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar componentes necesarios
from graphs.workflow import MultiAgentWorkflow
from graphs.state import create_initial_state


async def execute_task(task_description: str):
    """
    Ejecuta una tarea con el sistema multi-agente
    
    Args:
        task_description: Descripción de la tarea a realizar
    """
    print("🚀 Iniciando Sistema Multi-Agente...")
    print(f"📝 Tarea: {task_description}\n")
    
    # Verificar API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "sk-your-key-here":
        print("❌ ERROR: OPENAI_API_KEY no configurada en .env")
        print("   Por favor edita el archivo .env con tu API key de OpenAI")
        sys.exit(1)
    
    github_token = os.getenv("GITHUB_TOKEN", "")
    github_repo = os.getenv("GITHUB_REPO", "")
    linear_api_key = os.getenv("LINEAR_API_KEY", "")
    
    if not github_repo or github_repo == "owner/repo-name":
        print("⚠️  ADVERTENCIA: GITHUB_REPO no configurado en .env")
        print("   Continuando sin integración GitHub...")
        github_repo = None
        github_token = None
    
    # Configuración del workflow
    config = {
        "openai_api_key": openai_key,
        "github_token": github_token,
        "github_repo": github_repo,
        "linear_api_key": linear_api_key,
        "model": os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview"),
        "temperature": float(os.getenv("DEFAULT_TEMPERATURE", "0.2"))
    }
    
    # Crear estado inicial
    initial_state = create_initial_state(
        task_description=task_description,
        github_repo=github_repo,
        github_branch="main"
    )
    
    print("=" * 80)
    print("🤖 AGENTES ACTIVADOS:")
    print("=" * 80)
    print("  📐 @fullstack-architect - Coordinador y Arquitecto")
    print("  🔒 @security-specialist - Revisor de Seguridad")
    print("  💻 @frontend-specialist - Desarrollo Frontend")
    print("  🔧 @backend-specialist - Desarrollo Backend")
    print("  ✅ @qa-specialist - Control de Calidad")
    print("  🔍 @observer-optimizer - Análisis y Optimización")
    print("=" * 80)
    print()
    
    # Crear y ejecutar workflow
    try:
        workflow = MultiAgentWorkflow(config)
        print("⚙️  Compilando workflow multi-agente...")
        
        # Ejecutar el workflow
        print("🎯 Ejecutando coordinación multi-agente...\n")
        final_state = await workflow.execute(initial_state)
        
        # Mostrar resultados
        print("\n" + "=" * 80)
        print("✅ EJECUCIÓN COMPLETADA")
        print("=" * 80)
        
        if final_state.get("task_complete"):
            print("✅ Estado: COMPLETADA")
        else:
            print("⏸️  Estado: EN PROGRESO")
        
        print(f"\n📊 Métricas:")
        print(f"   - Agentes ejecutados: {len(final_state.get('agent_results', []))}")
        print(f"   - Tokens usados: ~{final_state.get('total_tokens', 0)}")
        
        if final_state.get('github_pr_url'):
            print(f"\n🔗 Pull Request: {final_state['github_pr_url']}")
        
        if final_state.get('linear_issue_url'):
            print(f"📋 Issue Linear: {final_state['linear_issue_url']}")
        
        # Mostrar resumen de cada agente
        print("\n📝 Resumen de Agentes:")
        for result in final_state.get('agent_results', []):
            status_emoji = "✅" if result['status'] == 'success' else "❌"
            print(f"\n   {status_emoji} {result['agent_name']}")
            print(f"      {result['message'][:100]}...")
            if result.get('files_modified'):
                print(f"      Archivos: {', '.join(result['files_modified'][:3])}")
        
        print("\n" + "=" * 80)
        print("🎉 Sistema multi-agente finalizado!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR durante la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Función principal del CLI"""
    if len(sys.argv) < 2:
        print("=" * 80)
        print("🤖 SISTEMA MULTI-AGENTE - CLI")
        print("=" * 80)
        print("\nUso:")
        print("  python cli.py \"<descripción de la tarea>\"")
        print("\nEjemplos:")
        print('  python cli.py "Implementar traducciones a catalán e inglés"')
        print('  python cli.py "Añadir autenticación OAuth al sistema"')
        print('  python cli.py "Optimizar performance del frontend"')
        print("\nDocumentación:")
        print("  - README_LANGGRAPH.md")
        print("  - architecture/LANGGRAPH_ARCHITECTURE.md")
        print("=" * 80)
        sys.exit(1)
    
    # Obtener la tarea del argumento
    task = " ".join(sys.argv[1:])
    
    # Ejecutar el workflow de forma asíncrona
    asyncio.run(execute_task(task))


if __name__ == "__main__":
    main()
