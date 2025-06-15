from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import execute_command, get_os_type
from utils.logger import log_action

def service_menu():
    while True:
        clear_screen()
        print_header("Gestión de Servicios/Daemons")
        options = {
            "1": "Listar Servicios",
            "2": "Iniciar Servicio",
            "3": "Detener Servicio",
            "4": "Reiniciar Servicio",
            "5": "Habilitar Servicio (inicio automático)",
            "6": "Deshabilitar Servicio (no inicio automático)",
            "0": "Volver al Menú Principal de Gestión"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            list_services()
        elif choice == '2':
            start_service()
        elif choice == '3':
            stop_service()
        elif choice == '4':
            restart_service()
        elif choice == '5':
            enable_service()
        elif choice == '6':
            disable_service()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        get_user_input("Presione Enter para continuar...")

#Funciones auxiliares para Listar servicios (La función era muy compleja)
def _format_linux_services_output(output: str):
    """Formatea la salida de systemctl en una tabla legible."""
    lines = output.strip().split('\n')
    if not lines:
        print_info("No se encontraron servicios de systemd.")
        return

    # Encabezados de la tabla
    print(f"{'UNIT':<40} {'LOAD':<10} {'ACTIVE':<10} {'SUB':<10} {'DESCRIPTION':<50}")
    print(f"{'-'*40:<40} {'-'*10:<10} {'-'*10:<10} {'-'*10:<10} {'-'*50:<50}")

    for line in lines:
        parts = line.split(maxsplit=4) # Limita el split para que la descripción no se separe
        if len(parts) >= 5:
            unit = parts[0]
            load = parts[1]
            active = parts[2]
            sub = parts[3]
            description = parts[4]
            # Asegurarse de que los campos no excedan el ancho y truncar si es necesario
            print(f"{unit[:39]:<40} {load[:9]:<10} {active[:9]:<10} {sub[:9]:<10} {description[:49]:<50}")
        else:
            # Manejar líneas que no se ajustan al formato esperado
            print_error(f"Advertencia: Línea inesperada en la salida de systemctl: {line.strip()}")

def _format_windows_services_output(output: str):
    """Formatea la salida de wmic service get en una tabla legible."""
    lines = output.strip().split('\n')
    if len(lines) < 2:
        print_info("No se encontraron servicios de Windows o la salida es inesperada.")
        return

    raw_headers = [h.strip() for h in lines[0].split(',')]
    # Filtramos 'Node' si está presente, ya que generalmente es el nombre de la máquina local
    headers_to_display = [h for h in raw_headers if h != 'Node']

    # Imprimir encabezados de la tabla
    header_mapping = {
        'DisplayName': 'Display Name',
        'Name': 'Name',
        'State': 'State',
        'StartMode': 'Start Mode'
    }
    
    # Definir el orden y ancho de las columnas
    column_order = ['DisplayName', 'Name', 'State', 'StartMode']
    column_widths = {'DisplayName': 40, 'Name': 30, 'State': 10, 'StartMode': 12}

    header_line = ""
    separator_line = ""
    for col in column_order:
        display_name = header_mapping.get(col, col) # Usa el nombre legible si existe
        width = column_widths[col]
        header_line += f"{display_name:<{width}} "
        separator_line += f"{'-'*width:<{width}} "
    
    print(header_line.strip())
    print(separator_line.strip())

    for line in lines[1:]: # Ignorar la línea de encabezado de WMIC
        parts = [p.strip() for p in line.split(',')]
        if not parts or all(p == '' for p in parts): # Ignorar líneas vacías
            continue

        if len(parts) != len(raw_headers):
            print_error(f"Advertencia: Formato de línea WMIC inesperado. Saltando: {line.strip()}")
            continue

        service_data_map = dict(zip(raw_headers, parts))
        
        display_name = service_data_map.get('DisplayName', 'N/A')
        name = service_data_map.get('Name', 'N/A')
        state = service_data_map.get('State', 'N/A')
        start_mode = service_data_map.get('StartMode', 'N/A')

        # Imprimir fila, truncando si es necesario para ajustar el ancho
        print(f"{display_name[:39]:<40} {name[:29]:<30} {state[:9]:<10} {start_mode[:11]:<12}")

#Funciones principales
def list_services():
    clear_screen()
    print_header("Listar Servicios del Sistema")
    os_type = get_os_type()
    command = ""
    
    if os_type == 'linux':
        # --no-pager: Evita paginación.
        # --plain: Salida sin adornos (útil para scripts).
        # --no-legend: No imprime la línea de encabezado.
        command = "systemctl list-units --type=service --all --no-pager --plain --no-legend"
        print_info("Ejecutando: systemctl list-units (Linux)")
    elif os_type == 'windows':
        # /FORMAT:CSV es útil para un parseo más consistente
        command = "wmic service get Name,DisplayName,State,StartMode /FORMAT:CSV"
        print_info("Ejecutando: wmic service get (Windows)")
    else:
        print_error("Sistema operativo no soportado para listar servicios.")
        log_action("Service", "List Services", "Sistema operativo no soportado.")
        return

    output, status = execute_command(command)

    if status == 0:
        if output.strip():
            print_success("Servicios del Sistema:")
            if os_type == 'linux':
                _format_linux_services_output(output)
            elif os_type == 'windows':
                _format_windows_services_output(output)
        else:
            print_info("No se encontraron servicios.")
        log_action("Service", "List Services", "Servicios listados exitosamente.")
    else:
        print_error(f"Error al listar servicios: {output}")
        log_action("Service", "List Services", f"Error al listar servicios: {output}")

def _perform_service_action(action, service_name):
    os_type = get_os_type()
    command = ""
    
    if os_type == 'linux':
        command = f"sudo systemctl {action} {service_name}"
    elif os_type == 'windows':
        if action == 'start':
            command = f"net start \"{service_name}\""
        elif action == 'stop':
            command = f"net stop \"{service_name}\""
        elif action == 'restart':
            command = f"net stop \"{service_name}\" && net start \"{service_name}\""
        elif action == 'enable':
            command = f"sc config \"{service_name}\" start= auto"
        elif action == 'disable':
            command = f"sc config \"{service_name}\" start= disabled"
        else:
            print_error(f"Acción de servicio '{action}' no soportada para Windows.")
            return False
    else:
        print_error("Sistema operativo no soportado para gestionar servicios.")
        return False
    
    print_info(f"Ejecutando: {command}")
    output, status = execute_command(command, sudo=(os_type == 'linux'))

    if status == 0:
        print_success(f"Servicio '{service_name}' {action}ado exitosamente.")
        log_action("Service", f"{action.capitalize()} Service", f"Servicio '{service_name}' {action}ado.")
        return True
    else:
        print_error(f"Error al {action} servicio '{service_name}': {output}")
        log_action("Service", f"{action.capitalize()} Service", f"Error al {action} servicio '{service_name}': {output}")
        return False

def start_service():
    print_header("Iniciar Servicio")
    service_name = get_user_input("Ingrese el nombre del servicio a iniciar")
    _perform_service_action('start', service_name)

def stop_service():
    print_header("Detener Servicio")
    service_name = get_user_input("Ingrese el nombre del servicio a detener")
    _perform_service_action('stop', service_name)

def restart_service():
    print_header("Reiniciar Servicio")
    service_name = get_user_input("Ingrese el nombre del servicio a reiniciar")
    _perform_service_action('restart', service_name)

def enable_service():
    print_header("Habilitar Servicio (inicio automático)")
    service_name = get_user_input("Ingrese el nombre del servicio a habilitar")
    _perform_service_action('enable', service_name)

def disable_service():
    print_header("Deshabilitar Servicio (no inicio automático)")
    service_name = get_user_input("Ingrese el nombre del servicio a deshabilitar")
    _perform_service_action('disable', service_name)