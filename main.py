import sys
from utils.display import clear_screen, print_menu, print_header, print_error, get_user_input
from utils.system_info import get_os_type
from modules import user_group_management, network_management, resource_monitoring, \
                    disk_partition_management, firewall_management, process_management

def main_menu():
    while True:
        clear_screen()
        print_header(f"Administración de Sistemas ({get_os_type().capitalize()})")
        options = {
            "1": "Administración de Usuarios y Grupos",
            "2": "Administración de Redes",
            "3": "Monitorización de Recursos",
            "4": "Gestión de Particiones de Disco",
            "5": "Gestión de Firewall",
            "6": "Gestión de Procesos",
            "0": "Salir"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

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
        elif choice == '0':
            print_header("Saliendo del script. ¡Hasta luego!")
            sys.exit()
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
            get_user_input("Presione Enter para continuar...")

if __name__ == "__main__":
    main_menu()