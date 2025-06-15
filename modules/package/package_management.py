from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import execute_command, get_os_type
from utils.logger import log_action

def package_menu():
    """
    Muestra un menú para la gestión de paquetes/software.
    """
    while True:
        clear_screen()
        print_header("Gestión de Paquetes/Software")
        options = {
            "1": "Listar Paquetes Instalados",
            "2": "Actualizar Lista de Paquetes del Sistema",
            "3": "Actualizar Todos los Paquetes Instalados",
            "4": "Instalar Paquete",
            "5": "Eliminar Paquete",
            "6": "Buscar Paquete",
            "0": "Volver al Menú Principal de Gestión"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            list_installed_packages()
        elif choice == '2':
            update_package_list()
        elif choice == '3':
            upgrade_all_packages()
        elif choice == '4':
            package_name = get_user_input("Ingrese el nombre del paquete a instalar")
            install_package(package_name)
        elif choice == '5':
            package_name = get_user_input("Ingrese el nombre del paquete a eliminar")
            remove_package(package_name)
        elif choice == '6':
            package_name = get_user_input("Ingrese el nombre del paquete a buscar")
            search_package(package_name)
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        get_user_input("Presione Enter para continuar...")

def _get_package_manager():
    """
    Determina el gestor de paquetes del sistema operativo (solo Linux).
    Retorna 'apt', 'yum'/'dnf', o None si no es Linux o no se detecta.
    """
    os_type = get_os_type()
    if os_type == 'linux':
        if os.path.exists('/etc/debian_version'):
            return 'apt'
        elif os.path.exists('/etc/redhat-release'):
            # Prefer dnf on modern RedHat/Fedora, fallback to yum
            output, status = execute_command("which dnf")
            if status == 0:
                return 'dnf'
            return 'yum'
    return None

def _unsupported_os_message(operation: str):
    """Prints a message for unsupported OS/package manager."""
    print_error(f"Operación de gestión de paquetes '{operation}' no soportada en este sistema operativo (solo Linux compatible con apt/yum/dnf).")
    log_action("PackageManager", operation, "Operación no soportada: OS no es Linux o gestor no detectado.")

def list_installed_packages():
    """
    Lista los paquetes instalados en el sistema (solo Linux).
    Imprime la salida para ser capturada por la GUI.
    """
    print_header("Listar Paquetes Instalados")
    manager = _get_package_manager()
    output = ""
    status = 1
    
    if manager == 'apt':
        print_info("Listando paquetes instalados (apt list --installed)...")
        output, status = execute_command("apt list --installed")
    elif manager in ['yum', 'dnf']:
        print_info(f"Listando paquetes instalados ({manager} list installed)...")
        output, status = execute_command(f"{manager} list installed")
    else:
        _unsupported_os_message("listar paquetes")
        return # Exit early

    if status == 0:
        print_success("Paquetes instalados:")
        print("```\n" + output + "\n```")
        log_action("PackageManager", "List Packages", "Paquetes listados exitosamente.")
    else:
        print_error(f"Error al listar paquetes: {output}")
        log_action("PackageManager", "List Packages", f"Error al listar paquetes: {output}")

def search_package(package_name: str):
    """
    Busca un paquete por nombre (solo Linux).
    Imprime la salida para ser capturada por la GUI.
    """
    if not package_name:
        print_error("Por favor, introduce un nombre de paquete para buscar.")
        return

    print_header(f"Buscar Paquete: {package_name}")
    manager = _get_package_manager()
    output = ""
    status = 1

    if manager == 'apt':
        print_info(f"Buscando '{package_name}' (apt search {package_name})...")
        output, status = execute_command(f"apt search {package_name}")
    elif manager in ['yum', 'dnf']:
        print_info(f"Buscando '{package_name}' ({manager} search {package_name})...")
        output, status = execute_command(f"{manager} search {package_name}")
    else:
        _unsupported_os_message("buscar paquete")
        return
    
    if status == 0:
        print_success(f"Resultados de búsqueda para '{package_name}':")
        print("```\n" + output + "\n```")
        log_action("PackageManager", "Search Package", f"Búsqueda de '{package_name}' exitosa.")
    else:
        print_error(f"Error al buscar paquete: {output}")
        log_action("PackageManager", "Search Package", f"Error al buscar '{package_name}': {output}")

def install_package(package_name: str):
    """
    Instala un paquete específico (solo Linux).
    Imprime la salida para ser capturada por la GUI.
    """
    if not package_name:
        print_error("Por favor, introduce un nombre de paquete para instalar.")
        return

    print_header(f"Instalar Paquete: {package_name}")
    manager = _get_package_manager()
    output = ""
    status = 1

    if manager == 'apt':
        print_info(f"Instalando '{package_name}' (sudo apt install -y {package_name})...")
        output, status = execute_command(f"sudo apt install -y {package_name}")
    elif manager in ['yum', 'dnf']:
        print_info(f"Instalando '{package_name}' (sudo {manager} install -y {package_name})...")
        output, status = execute_command(f"sudo {manager} install -y {package_name}")
    else:
        _unsupported_os_message("instalar paquete")
        return
    
    if status == 0:
        print_success(f"Paquete '{package_name}' instalado exitosamente.")
        print("```\n" + output + "\n```")
        log_action("PackageManager", "Install Package", f"Paquete '{package_name}' instalado exitosamente.")
    else:
        print_error(f"Error al instalar paquete '{package_name}': {output}")
        log_action("PackageManager", "Install Package", f"Error al instalar '{package_name}': {output}")

def remove_package(package_name: str):
    """
    Desinstala un paquete específico (solo Linux).
    Imprime la salida para ser capturada por la GUI.
    """
    if not package_name:
        print_error("Por favor, introduce un nombre de paquete para desinstalar.")
        return

    print_header(f"Desinstalar Paquete: {package_name}")
    manager = _get_package_manager()
    output = ""
    status = 1

    if manager == 'apt':
        print_info(f"Desinstalando '{package_name}' (sudo apt remove -y {package_name})...")
        output, status = execute_command(f"sudo apt remove -y {package_name}")
    elif manager in ['yum', 'dnf']:
        print_info(f"Desinstalando '{package_name}' (sudo {manager} remove -y {package_name})...")
        output, status = execute_command(f"sudo {manager} remove -y {package_name}")
    else:
        _unsupported_os_message("desinstalar paquete")
        return
    
    if status == 0:
        print_success(f"Paquete '{package_name}' desinstalado exitosamente.")
        print("```\n" + output + "\n```")
        log_action("PackageManager", "Remove Package", f"Paquete '{package_name}' desinstalado exitosamente.")
    else:
        print_error(f"Error al desinstalar paquete '{package_name}': {output}")
        log_action("PackageManager", "Remove Package", f"Error al desinstalar '{package_name}': {output}")

def update_package_list():
    """
    Actualiza la lista de paquetes disponibles (solo Linux).
    Imprime la salida para ser capturada por la GUI.
    """
    print_header("Actualizar Lista de Paquetes")
    manager = _get_package_manager()
    output = ""
    status = 1

    if manager == 'apt':
        print_info("Actualizando lista de paquetes (sudo apt update)...")
        output, status = execute_command("sudo apt update")
    elif manager in ['yum', 'dnf']:
        print_info(f"Actualizando lista de paquetes (sudo {manager} check-update)...")
        output, status = execute_command(f"sudo {manager} check-update")
    else:
        _unsupported_os_message("actualizar lista de paquetes")
        return
    
    if status == 0:
        print_success("Lista de paquetes actualizada exitosamente.")
        print("```\n" + output + "\n```")
        log_action("PackageManager", "Update List", "Lista de paquetes actualizada exitosamente.")
    else:
        print_error(f"Error al actualizar lista de paquetes: {output}")
        log_action("PackageManager", "Update List", f"Error al actualizar lista de paquetes: {output}")

def upgrade_all_packages():
    """
    Actualiza todos los paquetes instalados a sus últimas versiones (solo Linux).
    Imprime la salida para ser capturada por la GUI.
    """
    print_header("Actualizar Todos los Paquetes")
    manager = _get_package_manager()
    output = ""
    status = 1

    if manager == 'apt':
        print_info("Actualizando todos los paquetes (sudo apt upgrade -y)...")
        output, status = execute_command("sudo apt upgrade -y")
    elif manager in ['yum', 'dnf']:
        print_info(f"Actualizando todos los paquetes (sudo {manager} update -y)...")
        output, status = execute_command(f"sudo {manager} update -y")
    else:
        _unsupported_os_message("actualizar todos los paquetes")
        return
    
    if status == 0:
        print_success("Todos los paquetes actualizados exitosamente.")
        print("```\n" + output + "\n```")
        log_action("PackageManager", "Upgrade All", "Todos los paquetes actualizados exitosamente.")
    else:
        print_error(f"Error al actualizar todos los paquetes: {output}")
        log_action("PackageManager", "Upgrade All", f"Error al actualizar todos los paquetes: {output}")