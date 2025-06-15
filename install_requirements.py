import subprocess
import sys

#Función para instalar todos los requisitos
def install_requirements():
    """
    Instala los paquetes Python listados en requirements.txt usando pip.
    """
    print("Verificando e instalando los requisitos del proyecto...")
    try:
        # Asegúrate de que pip esté actualizado
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("pip ha sido actualizado.")

        # Instala los paquetes de requirements.txt
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                                capture_output=True, text=True, check=True)
        print("\n" + result.stdout)
        print("Todos los requisitos han sido instalados exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"\nERROR al instalar los requisitos:")
        print(f"Comando fallido: {' '.join(e.cmd)}")
        print(f"Salida estándar:\n{e.stdout}")
        print(f"Salida de error:\n{e.stderr}")
        print("Por favor, asegúrese de tener pip instalado y acceso a internet.")
        sys.exit(1)
    except FileNotFoundError:
        print("\nERROR: El archivo 'requirements.txt' no se encontró en el directorio actual.")
        print("Asegúrese de que el script se ejecuta desde la raíz del proyecto.")
        sys.exit(1)
    except Exception as e:
        print(f"\nHa ocurrido un error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_requirements()