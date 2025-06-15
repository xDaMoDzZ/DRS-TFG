import sys
import os
import ctypes

# Importaciones de módulos principales
from modules.disk import disk_partition_management
from modules.docker import docker_management
from modules.firewall import firewall_management
from modules.network import network_management
from modules.resource import resource_monitoring
from modules.user import user_group_management
from modules.process import process_management
from modules.services import service_management
from modules.package import package_management

# Importaciones de utilidades (se consolida una sola vez)
from utils.display import clear_screen, print_menu, print_header, print_error, get_user_input
from utils.system_info import get_os_type

# --- Comprobación de Permisos ---
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
        # Para otros sistemas operativos, asume no hay comprobación especial
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
        sys.exit(1)
    else:
        print("No se soporta la elevación automática de privilegios en este sistema operativo.")
        print("Asegúrese de ejecutar el script con los permisos necesarios manualmente.")
        sys.exit(1)

# --- Función Principal ---
def main_menu():
    """
    Muestra el menú principal de la aplicación de administración de sistemas.
    Las opciones se adaptan al sistema operativo.
    """
    current_os = get_os_type()

    while True:
        clear_screen()
        print_header(f"Administración de Sistemas ({current_os.capitalize()})")
              
        if current_os == 'linux':            
            options = {
            "1": "Administración de Usuarios y Grupos",
            "2": "Administración de Redes",
            "3": "Monitorización de Recursos",
            "4": "Gestión de Particiones de Disco",
            "5": "Gestión de Firewall",
            "6": "Gestión de Procesos",
            "7": "Gestión de Docker",
            "8": "Gestión de Servicios/Daemons",
            "9": "Gestión de Paquetes/Software",
            "0": "Salir"
        }
        else:
            options = {
            "1": "Administración de Usuarios y Grupos",
            "2": "Administración de Redes",
            "3": "Monitorización de Recursos",
            "4": "Gestión de Particiones de Disco",
            "5": "Gestión de Firewall",
            "6": "Gestión de Procesos",
            "7": "Gestión de Docker",
            "8": "Gestión de Servicios/Daemons",
            "0": "Salir"
            }
            
        print_menu(options)

        choice = get_user_input("Seleccione una opción")
        
        #Lista de opciones
        if choice == '1':
            user_group_management.user_group_menu()
        elif choice == '2':
            network_management.network_menu()
        elif choice == '3':
            resource_monitoring.resource_monitoring_menu()
        elif choice == '4':
            disk_partition_management.disk_partition_menu() 
        elif choice == '5':
            firewall_management.firewall_menu()
        elif choice == '6':
            process_management.process_menu()
        elif choice == '7':
            docker_management.docker_menu()
        elif choice == '8':
            service_management.service_menu()
        elif choice == '9':
            if current_os == 'linux':
                package_management.package_menu()
            else:
                print_error("La gestión de paquetes/software está disponible solo para sistemas Linux.")
                get_user_input("Presione Enter para continuar...")
        elif choice == '0':
            print_header("Saliendo del script. ¡Hasta luego!")
            sys.exit()
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
            get_user_input("Presione Enter para continuar...")

# --- Punto de Entrada del Script ---
if __name__ == "__main__":
    if not is_admin():
        print("Detectado: No se está ejecutando como administrador/root.")
        relaunch_as_admin()
        sys.exit(1) 
    main_menu()