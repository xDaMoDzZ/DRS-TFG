# run_gui.py (Refactorizado)

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.gui import gui_interface

# Importa el módulo de display para establecer el modo GUI
import utils.display as display_utils

# Importaciones específicas del sistema operativo para la comprobación de privilegios
if os.name == 'nt':  # Windows
    import ctypes
elif os.name == 'posix': # Linux/macOS
    import os

def is_admin():
    """
    Comprueba si el script se está ejecutando con privilegios de administrador/root.
    """
    if os.name == 'nt':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False
    elif os.name == 'posix':
        return os.geteuid() == 0
    else:
        # Para otros sistemas operativos, asume que no hay una comprobación especial
        return True 

def relaunch_as_admin():
    """
    Intenta relanzar el script actual con privilegios de administrador/root.
    Si tiene éxito, el proceso actual se cierra.
    """
    if os.name == 'nt':
        params = " ".join(sys.argv)        
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        except Exception as e:
            print(f"Error al intentar relanzar como administrador: {e}")
            sys.exit(1)

        sys.exit(0) # Salir del proceso no elevado
    elif os.name == 'posix':
        print("\nEste script requiere permisos de superusuario (root).")
        print("Por favor, ejecútelo con 'sudo':")
        print(f"  sudo {sys.executable} {' '.join(sys.argv)}")
        sys.exit(1) # Salir con error y dar instrucciones
    else:
        print("No se soporta la elevación automática de privilegios en este sistema operativo.")
        print("Asegúrese de ejecutar el script con los permisos necesarios manualmente.")
        sys.exit(1)

def launch_gui():
    """
    Lanza la interfaz gráfica de usuario.
    Verifica los privilegios de administrador/root antes de proceder.
    """
    if not is_admin():
        print("Detectado: No se está ejecutando como administrador/root.")
        relaunch_as_admin()
        # No se necesita un 'return' aquí, ya que relaunch_as_admin() llama a sys.exit()
        # si el relanzamiento es exitoso o si no es compatible.

    print("Iniciando la interfaz gráfica de usuario (Gradio)...")
    try:
        # Activa la bandera de modo GUI en utils.display
        display_utils.IS_GUI_MODE = True
        
        # Llama a la función de inicio de la GUI del módulo gui_interface
        # La función start_gui en modules/gui/gui_interface.py
        # es la que debe contener `app.launch(share=False, inbrowser=True)`
        gui_interface.start_gui() 
        
    except ImportError:
        print("\nERROR: No se pudo importar el módulo 'gradio'.")
        print("Por favor, asegúrese de haber instalado los requisitos del proyecto:")
        print("  python install_requirements.py")
        sys.exit(1)
    except Exception as e:
        print(f"\nHa ocurrido un error inesperado al iniciar la GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Asegúrate de que la raíz del proyecto esté en sys.path para importaciones
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    launch_gui()