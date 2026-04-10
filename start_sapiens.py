#!/usr/bin/env python3
"""
Script de inicialização rápida para SAPIENS
Sistema simplificado para iniciar análise acadêmica
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


class SapiensLauncher:
    """Launcher simplificado para SAPIENS"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.requirements_installed = False
        self.python_cmd = self._get_python_command()

    def _get_python_command(self):
        """Detecta comando Python disponível"""
        commands = ["python3", "python"]
        for cmd in commands:
            try:
                result = subprocess.run([cmd, "--version"],
                                      capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    return cmd
            except FileNotFoundError:
                continue
        return "python3"  # fallback

    def check_python_version(self):
        """Verifica versão do Python"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            print("❌ Python 3.10+ é obrigatório!")
            print(f"📦 Versão atual: {sys.version}")
            return False
        print(f"✅ Python {sys.version.split()[0]} detectado")
        return True

    def install_dependencies(self):
        """Instala dependências"""
        print("📦 Instalando dependências...")

        try:
            # Tenta usar UV se disponível
            result = subprocess.run(["uv", "--version"],
                                  capture_output=True, text=True, check=False)

            if result.returncode == 0:
                print("🚀 Usando UV para instalação rápida...")
                subprocess.run(["uv", "pip", "install", "-e", "."], check=True)
            else:
                print("📦 Usando pip tradicional...")
                subprocess.run([self.python_cmd, "-m", "pip", "install", "-e", "."], check=True)

            self.requirements_installed = True
            print("✅ Dependências instaladas com sucesso!")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na instalação: {e}")
            return False

    def check_environment_file(self):
        """Verifica arquivo .env"""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        if not env_file.exists() and env_example.exists():
            print("⚙️ Arquivo .env não encontrado")
            response = input("📋 Criar .env baseado no .env.example? (y/n): ")
            if response.lower() == 'y':
                import shutil
                shutil.copy(env_example, env_file)
                print("✅ Arquivo .env criado! Edite com suas configurações.")
                print("⚠️ Lembre-se de configurar OPENAI_API_KEY!")
                return False

        if env_file.exists():
            print("✅ Arquivo .env encontrado")
            return True

        return False

    def start_web_interface(self, host="127.0.0.1", port=4000):
        """Inicia interface web"""
        print("🌐 Iniciando interface web SAPIENS...")
        print(f"📡 Endereço: http://{host}:{port}")

        try:
            # Executa interface web sem mudar diretório
            from src.Sapiens_MultiAgente.web.app import SapiensWebInterface
            interface = SapiensWebInterface()
            app = interface.create_app()
            app.run(host=host, port=port, debug=True)

        except KeyboardInterrupt:
            print("\n🛑 Interface interrompida pelo usuário")
        except Exception as e:
            print(f"❌ Erro ao iniciar interface: {e}")
            print("💡 Tente executar: cd .. && python3 -c \"from src.Sapiens_MultiAgente.web.app import SapiensWebInterface; SapiensWebInterface().run(debug=True)\"")

    def run_analysis_cli(self, topic=None, data_files=None):
        """Executa análise via linha de comando"""
        print("🤖 Executando análise via linha de comando...")

        try:
            os.chdir(self.project_root / "src" / "Sapiens_MultiAgente")

            # Comando básico
            cmd = [self.python_cmd, "main.py", "run"]

            if topic:
                print(f"📝 Tópico: {topic}")

            # Executa análise
            subprocess.run(cmd, check=True)

        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na análise: {e}")
        except KeyboardInterrupt:
            print("\n🛑 Análise interrompida pelo usuário")

    def show_status(self):
        """Mostra status do sistema"""
        print("📊 Status do Sistema SAPIENS")
        print("=" * 40)

        # Verifica arquivos essenciais
        files_to_check = {
            "README.md": "📋 Documentação",
            "pyproject.toml": "⚙️ Configuração Python",
            ".env.example": "🔧 Exemplo de ambiente",
            "src/Sapiens_MultiAgente/crew.py": "🤖 Agentes",
            "src/Sapiens_MultiAgente/web/app.py": "🌐 Interface web"
        }

        for file_path, description in files_to_check.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {description}: {file_path}")
            else:
                print(f"❌ {description}: {file_path} (não encontrado)")

        print("\n📁 Estrutura de diretórios:")
        for dir_path in ["src", "logs", "uploads"]:
            full_dir = self.project_root / dir_path
            if full_dir.exists():
                print(f"✅ {dir_path}/")
            else:
                print(f"⚠️ {dir_path}/ (não existe)")

    def main(self):
        """Função principal"""
        parser = argparse.ArgumentParser(description="Launcher SAPIENS")
        parser.add_argument("--web", action="store_true", help="Iniciar interface web")
        parser.add_argument("--cli", action="store_true", help="Executar análise CLI")
        parser.add_argument("--status", action="store_true", help="Mostrar status")
        parser.add_argument("--host", default="127.0.0.1", help="Host para interface web")
        parser.add_argument("--port", type=int, default=4000, help="Porta para interface web")
        parser.add_argument("--topic", help="Tópico de pesquisa para análise CLI")

        args = parser.parse_args()

        print("🚀 SAPIENS - Plataforma Acadêmica Multiagente")
        print("=" * 50)

        # Verifica Python
        if not self.check_python_version():
            return 1

        # Mostra status se solicitado
        if args.status:
            self.show_status()
            return 0

        # Instala dependências se necessário
        if not self.requirements_installed:
            if not self.install_dependencies():
                return 1

        # Verifica arquivo de ambiente
        env_ok = self.check_environment_file()

        # Executa conforme argumentos
        if args.web:
            if not env_ok:
                print("⚠️ Configure o arquivo .env antes de usar a interface web!")
                return 1
            self.start_web_interface(args.host, args.port)

        elif args.cli:
            self.run_analysis_cli(args.topic)

        else:
            # Menu interativo
            print("\n🎯 Escolha uma opção:")
            print("1) 🌐 Iniciar interface web")
            print("2) 🤖 Executar análise CLI")
            print("3) 📊 Ver status do sistema")
            print("4) ❌ Sair")

            choice = input("\nOpção: ").strip()

            if choice == "1":
                if not env_ok:
                    print("⚠️ Configure o arquivo .env primeiro!")
                    return 1
                self.start_web_interface()

            elif choice == "2":
                topic = input("📝 Tópico de pesquisa: ").strip()
                self.run_analysis_cli(topic)

            elif choice == "3":
                self.show_status()

            else:
                print("👋 Até logo!")

        return 0


if __name__ == "__main__":
    launcher = SapiensLauncher()
    exit_code = launcher.main()
    sys.exit(exit_code)