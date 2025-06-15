from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os

def network_menu():
    """
    Menú de administración de redes para la interfaz de consola.
    Ahora pasa los parámetros requeridos a las funciones de network_management.
    """
    while True:
        clear_screen()
        print_header("Administración de Redes")
        options = {
            "1": "Ver Configuración IP",
            "2": "Configurar IP Estática (Requiere Privilegios)",
            "3": "Habilitar/Deshabilitar Interfaz (Requiere Privilegios)",
            "4": "Ver Tablas de Enrutamiento",
            "5": "Ver Conexiones de Red",
            "9": "Generar Log de Redes",
            "0": "Volver al Menú Principal"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            view_ip_config()
        elif choice == '2':
            print_info("\nConfiguración de IP Estática:")
            interface_name = get_user_input("Ingrese el nombre de la interfaz de red (ej. 'Ethernet', 'eth0')")
            ip_address = get_user_input("Ingrese la dirección IP (ej. 192.168.1.100)")
            subnet_mask = get_user_input("Ingrese la máscara de subred (ej. 255.255.255.0)")
            gateway = get_user_input("Ingrese la puerta de enlace (opcional, dejar en blanco si no aplica)")
            confirm = get_user_input("¿Está seguro que desea aplicar esta configuración? (s/N)").lower()
            configure_static_ip(interface_name, ip_address, subnet_mask, gateway, confirm)
        elif choice == '3':
            print_info("\nHabilitar/Deshabilitar Interfaz:")
            interface_name = get_user_input("Ingrese el nombre de la interfaz de red (ej. 'Ethernet', 'eth0')")
            action = get_user_input("¿Desea 'habilitar' o 'deshabilitar' la interfaz?").lower()
            confirm = get_user_input(f"¿Está seguro que desea '{action}' la interfaz '{interface_name}'? (s/N)").lower()
            toggle_interface_status(interface_name, action, confirm)
        elif choice == '4':
            view_routing_tables()
        elif choice == '5':
            view_network_connections()
        elif choice == '9':
            generate_network_log()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        get_user_input("Presione Enter para continuar...")

def view_ip_config():
    """
    Muestra la configuración IP del sistema.
    Adapta la salida para ser capturada por la GUI.
    """
    print_header("Ver Configuración IP")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "ipconfig /all"
    else: # linux
        command = "ip a"
    
    output, status = execute_command(command)
    if status == 0:
        print_info("Configuración IP:")
        print(output) # Usa print() para la salida bruta del comando
        log_action("Network", "View IP Config", "Configuración IP listada exitosamente.")
    else:
        print_error(f"Error al ver configuración IP: {output}")
        log_action("Network", "View IP Config", f"Error al ver configuración IP: {output}")

def configure_static_ip(interface_name: str, ip_address: str, subnet_mask: str, gateway: str, confirm: str):
    """
    Configura una dirección IP estática para una interfaz de red.
    Requiere privilegios. Los inputs ahora son argumentos.
    """
    print_header("Configurar IP Estática")
    print_info("Esta operación requiere privilegios de administrador/root y es delicada.")

    if not interface_name or not ip_address or not subnet_mask:
        print_error("Nombre de interfaz, dirección IP y máscara de subred son obligatorios.")
        log_action("Network", "Configure Static IP", "Intento fallido: Campos obligatorios vacíos.")
        return

    os_type = get_os_type()
    command = ""
    if os_type == 'windows':
        command = f'netsh interface ip set address name="{interface_name}" static {ip_address} {subnet_mask}'
        if gateway:
            command += f' {gateway} 1' # '1' es la métrica predeterminada
    else: # linux
        # La configuración de IP estática en Linux varía significativamente (NetworkManager, systemd-networkd, ifupdown).
        # Este ejemplo usa comandos 'ip' que pueden no ser persistentes después de un reinicio
        # o pueden conflictos con servicios como DHCP si no se deshabilitan primero.
        # Para persistencia, se recomienda editar archivos de configuración como /etc/network/interfaces
        # o usar herramientas como nmcli/nmtui para NetworkManager.
        print_info("Para Linux, la configuración de IP estática puede requerir pasos adicionales para la persistencia.")
        print_info("Considera deshabilitar DHCP para la interfaz antes de aplicar IP estática.")
        
        # Eliminar cualquier configuración IP existente (ej. DHCP)
        # command_clear = f"ip address flush dev {interface_name}"
        # execute_command(command_clear, sudo=True) # Ejecutar esto primero si es necesario
        
        command = f"ip address add {ip_address}/{subnet_mask} dev {interface_name}"
        if gateway:
            # Añadir la ruta de puerta de enlace por defecto
            command += f" && ip route add default via {gateway} dev {interface_name}"

    print_info(f"Comando a ejecutar: {command}")
    if confirm.lower() == 's':
        output, status = execute_command(command, sudo=True)
        if status == 0:
            print_success(f"Configuración de IP estática aplicada a '{interface_name}'.")
            log_action("Network", "Configure Static IP", f"IP estática {ip_address}/{subnet_mask} configurada en '{interface_name}'.")
        else:
            print_error(f"Error al configurar IP estática: {output}")
            log_action("Network", "Configure Static IP", f"Error al configurar IP estática en '{interface_name}': {output}")
    else:
        print_info("Operación de configuración IP estática cancelada por el usuario.")
        log_action("Network", "Configure Static IP", "Configuración de IP estática cancelada.")

def toggle_interface_status(interface_name: str, action: str, confirm: str):
    """
    Habilita o deshabilita una interfaz de red.
    Requiere privilegios. Los inputs ahora son argumentos.
    """
    print_header("Habilitar/Deshabilitar Interfaz")
    print_info("Esta operación requiere privilegios de administrador/root y puede interrumpir la conectividad.")
    
    if not interface_name or not action:
        print_error("Nombre de interfaz y acción son obligatorios.")
        log_action("Network", "Toggle Interface", "Intento fallido: Campos obligatorios vacíos.")
        return

    os_type = get_os_type()
    command = ""
    if os_type == 'windows':
        if action == 'habilitar':
            command = f'netsh interface set interface name="{interface_name}" admin=enable'
        elif action == 'deshabilitar':
            command = f'netsh interface set interface name="{interface_name}" admin=disable'
        else:
            print_error("Acción inválida. Use 'habilitar' o 'deshabilitar'.")
            log_action("Network", "Toggle Interface", "Acción inválida proporcionada.")
            return
    else: # linux
        if action == 'habilitar':
            command = f"ip link set dev {interface_name} up"
        elif action == 'deshabilitar':
            command = f"ip link set dev {interface_name} down"
        else:
            print_error("Acción inválida. Use 'habilitar' o 'deshabilitar'.")
            log_action("Network", "Toggle Interface", "Acción inválida proporcionada.")
            return
    
    print_info(f"Comando a ejecutar: {command}")
    if confirm.lower() == 's':
        output, status = execute_command(command, sudo=True)
        if status == 0:
            print_success(f"Interfaz '{interface_name}' {action}da exitosamente.")
            log_action("Network", "Toggle Interface", f"Interfaz '{interface_name}' {action}da.")
        else:
            print_error(f"Error al {action} la interfaz: {output}")
            log_action("Network", "Toggle Interface", f"Error al {action} interfaz '{interface_name}': {output}")
    else:
        print_info(f"Operación de {action} interfaz cancelada por el usuario.")
        log_action("Network", "Toggle Interface", f"Operación {action} interfaz cancelada.")

def view_routing_tables():
    """
    Muestra las tablas de enrutamiento del sistema.
    Adapta la salida para ser capturada por la GUI.
    """
    print_header("Ver Tablas de Enrutamiento")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "route print"
    else: # linux
        command = "ip r" # o "route -n" para un formato más clásico
    
    output, status = execute_command(command)
    if status == 0:
        print_info("Tablas de enrutamiento:")
        print(output)
        log_action("Network", "View Routing Tables", "Tablas de enrutamiento listadas exitosamente.")
    else:
        print_error(f"Error al ver tablas de enrutamiento: {output}")
        log_action("Network", "View Routing Tables", f"Error al ver tablas de enrutamiento: {output}")

def view_network_connections():
    """
    Muestra las conexiones de red activas del sistema.
    Adapta la salida para ser capturada por la GUI.
    """
    print_header("Ver Conexiones de Red")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "netstat -ano" # -a: todas las conexiones, -n: números, -o: PID
    else: # linux
        command = "ss -tunap" # -t: tcp, -u: udp, -n: numérica, -a: todas, -p: proceso
    
    output, status = execute_command(command)
    if status == 0:
        print_info("Conexiones de red activas:")
        print(output)
        log_action("Network", "View Network Connections", "Conexiones de red listadas exitosamente.")
    else:
        print_error(f"Error al ver conexiones de red: {output}")
        log_action("Network", "View Network Connections", f"Error al ver conexiones de red: {output}")

def generate_network_log():
    """
    Genera un log consolidado de la configuración y estado de la red.
    Adapta la salida para ser capturada por la GUI.
    """
    print_header("Generar Log de Redes")
    log_action("Network", "Generate Log", "Generando log de redes.")
    
    print_info("--- Configuración IP ---")
    view_ip_config() # Llama a la función existente para obtener y mostrar la configuración IP

    print_info("\n--- Tablas de Enrutamiento ---")
    view_routing_tables() # Llama a la función existente para obtener y mostrar las tablas de enrutamiento

    print_info("\n--- Conexiones de Red ---")
    view_network_connections() # Llama a la función existente para obtener y mostrar las conexiones de red
    
    # La ruta de log ahora se maneja por utils.logger.py, no se imprime aquí directamente
    print_success("Log de redes generado. Consulta los logs del sistema para ver los detalles.")