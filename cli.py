#!/usr/bin/env python3
"""
CLI para ejecutar el sistema multi-agente con comandos simples
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el directorio del script
# (no desde el directorio actual de ejecución)
# SIEMPRE sobrescribir con el .env del proyecto (override=True)
script_dir = Path(__file__).parent.absolute()
dotenv_path = script_dir / '.env'
load_dotenv(dotenv_path=dotenv_path, override=True)

# Mostrar fuente de OPENAI_API_KEY (sin exponer la clave completa)
def _mask_key(key: str | None) -> str | None:
    if not key:
        return None
    try:
        # show a short prefix and suffix only
        if len(key) <= 12:
            return key[:4] + "..."
        return f"{key[:6]}...{key[-4:]}"
    except Exception:
        return None

openai_key_pre = os.getenv("OPENAI_API_KEY")
env_key_in_file = None
try:
    if dotenv_path.exists():
        for line in dotenv_path.read_text().splitlines():
            if line.strip().startswith("OPENAI_API_KEY="):
                env_key_in_file = line.split("=", 1)[1].strip()
                break
except Exception:
    env_key_in_file = None

if openai_key_pre:
    if env_key_in_file and env_key_in_file == openai_key_pre:
        source = f".env file at {dotenv_path}"
    else:
        source = "environment variable (exported)"
    masked = _mask_key(openai_key_pre)
    print(f"🔒 OPENAI_API_KEY loaded from {source}: {masked}")
else:
    print("❌ OPENAI_API_KEY not found in environment or project .env")

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
    
    # Crear estado inicial
    linear_team_id = os.getenv("LINEAR_TEAM_ID", "")
    project_path = os.getcwd()
    
    # Crear y ejecutar workflow
    try:
        workflow = MultiAgentWorkflow(config)
        print("⚙️  Compilando workflow multi-agente...")
        
        # Ejecutar el workflow
        print("🎯 Ejecutando coordinación multi-agente...\n")
        final_state = await workflow.execute(
            task_description=task_description,
            project_path=project_path,
            linear_team_id=linear_team_id,
            github_repo=github_repo or "unknown/repo"
        )
        
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
        agent_results = final_state.get('agent_results', {})
        if isinstance(agent_results, dict):
            for agent_name, result in agent_results.items():
                if isinstance(result, dict):
                    # Check both 'success' and 'status' for compatibility
                    success = result.get('success', result.get('status') == 'success')
                    status_emoji = "✅" if success else "❌"
                    
                    # Get name and summary/message
                    display_name = result.get('agent_name', agent_name)
                    summary = result.get('summary', result.get('message', 'No details'))
                    
                    print(f"\n   {status_emoji} {display_name}")
                    if summary and len(summary) > 0:
                        print(f"      {summary[:200]}...")
                    
                    # Show files if present
                    files_created = result.get('files_created', [])
                    files_modified = result.get('files_modified', [])
                    all_files = files_created + files_modified
                    if all_files:
                        print(f"      📁 Archivos: {', '.join(all_files[:3])}")
                        if len(all_files) > 3:
                            print(f"         ... y {len(all_files) - 3} más")
                    
                    # Show metrics if present
                    tokens = result.get('tokens_used', 0)
                    cost = result.get('cost_usd', 0.0)
                    if tokens > 0:
                        print(f"      💰 Tokens: {tokens:,} | Costo: ${cost:.4f}")
                    
                    # Show PR if present
                    pr_url = result.get('pr_url', '')
                    if pr_url:
                        print(f"      🔗 PR: {pr_url}")
        elif isinstance(agent_results, list):
            for result in agent_results:
                if isinstance(result, dict):
                    success = result.get('success', result.get('status') == 'success')
                    status_emoji = "✅" if success else "❌"
                    display_name = result.get('agent_name', 'Unknown')
                    summary = result.get('summary', result.get('message', 'No details'))
                    print(f"\n   {status_emoji} {display_name}")
                    if summary and len(summary) > 0:
                        print(f"      {summary[:200]}...")
        
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
