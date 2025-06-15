from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import execute_command, get_os_type
from utils.logger import log_action

def package_menu():
    while True:
        clear_screen()
        print_header("Gestión de Paquetes/Software")
        options = {
            "1": "Actualizar Paquetes del Sistema",
            "2": "Instalar Paquete",
            "3": "Eliminar Paquete",
            "4": "Buscar Paquete",
            "0": "Volver al Menú Principal de Gestión"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            update_system_packages()
        elif choice == '2':
            install_package()
        elif choice == '3':
            remove_package()
        elif choice == '4':
            search_package()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        get_user_input("Presione Enter para continuar...")

def update_system_packages():
    print_header("Actualizar Paquetes del Sistema")
    os_type = get_os_type()
    command = ""

    if os_type == 'linux':
        print_info("Actualizando índices de paquetes y luego actualizando paquetes instalados.")
        command = "sudo apt update && sudo apt upgrade -y"
    elif os_type == 'windows':
        print_info("Windows usa Winget para gestionar paquetes (requiere Winget instalado).")
        print_info("Actualizando todos los paquetes instalados vía Winget.")
        command = "winget upgrade --all --silent --accept-source-agreements --accept-package-agreements"
    else:
        print_error("Sistema operativo no soportado para la gestión de paquetes.")
        log_action("Package", "Update Packages", "Sistema operativo no soportado.")
        return

    print_info(f"Ejecutando: {command}")
    output, status = execute_command(command, sudo=(os_type == 'linux'))

    if status == 0:
        print_success("Paquetes del sistema actualizados exitosamente.")
        print(output)
        log_action("Package", "Update Packages", "Paquetes actualizados exitosamente.")
    else:
        print_error(f"Error al actualizar paquetes del sistema: {output}")
        log_action("Package", "Update Packages", f"Error al actualizar paquetes: {output}")

def install_package():
    print_header("Instalar Paquete")
    package_name = get_user_input("Ingrese el nombre del paquete a instalar")
    os_type = get_os_type()
    command = ""

    if os_type == 'linux':
        command = f"sudo apt install -y {package_name}"
    elif os_type == 'windows':
        print_info("Windows usa Winget (requiere Winget instalado).")
        print_info("Nota: Para Winget, a veces se requiere el ID exacto del paquete. Use 'winget search' primero.")
        command = f"winget install --id {package_name} --silent --accept-source-agreements --accept-package-agreements"
    else:
        print_error("Sistema operativo no soportado para la instalación de paquetes.")
        log_action("Package", "Install Package", "Sistema operativo no soportado.")
        return

    print_info(f"Ejecutando: {command}")
    output, status = execute_command(command, sudo=(os_type == 'linux'))

    if status == 0:
        print_success(f"Paquete '{package_name}' instalado exitosamente.")
        print(output)
        log_action("Package", "Install Package", f"Paquete '{package_name}' instalado.")
    else:
        print_error(f"Error al instalar paquete '{package_name}': {output}")
        log_action("Package", "Install Package", f"Error al instalar paquete '{package_name}': {output}")

def remove_package():
    print_header("Eliminar Paquete")
    package_name = get_user_input("Ingrese el nombre del paquete a eliminar")
    os_type = get_os_type()
    command = ""

    confirm = get_user_input(f"¿Está seguro que desea eliminar el paquete '{package_name}'? (s/N)").lower()
    if confirm != 's':
        print_info("Operación cancelada.")
        log_action("Package", "Remove Package", f"Eliminación de paquete '{package_name}' cancelada.")
        return

    if os_type == 'linux':
        command = f"sudo apt remove -y {package_name}"
    elif os_type == 'windows':
        print_info("Windows usa Winget (requiere Winget instalado).")
        command = f"winget uninstall --id {package_name} --silent --accept-source-agreements --accept-package-agreements"
    else:
        print_error("Sistema operativo no soportado para la eliminación de paquetes.")
        log_action("Package", "Remove Package", "Sistema operativo no soportado.")
        return

    print_info(f"Ejecutando: {command}")
    output, status = execute_command(command, sudo=(os_type == 'linux'))

    if status == 0:
        print_success(f"Paquete '{package_name}' eliminado exitosamente.")
        print(output)
        log_action("Package", "Remove Package", f"Paquete '{package_name}' eliminado.")
    else:
        print_error(f"Error al eliminar paquete '{package_name}': {output}")
        log_action("Package", "Remove Package", f"Error al eliminar paquete '{package_name}': {output}")

def search_package():
    print_header("Buscar Paquete")
    search_query = get_user_input("Ingrese el término de búsqueda para el paquete")
    os_type = get_os_type()
    command = ""

    if os_type == 'linux':
        command = f"apt search {search_query}"
    elif os_type == 'windows':
        print_info("Windows usa Winget (requiere Winget instalado).")
        command = f"winget search {search_query}"
    else:
        print_error("Sistema operativo no soportado para la búsqueda de paquetes.")
        log_action("Package", "Search Package", "Sistema operativo no soportado.")
        return

    print_info(f"Ejecutando: {command}")
    output, status = execute_command(command)

    if status == 0:
        print_success(f"Resultados de búsqueda para '{search_query}':")
        print(output)
        log_action("Package", "Search Package", f"Búsqueda de paquete '{search_query}' exitosa.")
    else:
        print_error(f"Error al buscar paquete '{search_query}': {output}")
        log_action("Package", "Search Package", f"Error al buscar paquete '{search_query}': {output}")
