from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os

def network_menu():
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
            configure_static_ip()
        elif choice == '3':
            toggle_interface_status()
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
    print_header("Ver Configuración IP")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "ipconfig /all"
    else: # linux
        command = "ip a"
    
    output, status = execute_command(command)
    if status == 0:
        print_info("Configuración IP:")
        print(output)
        log_action("Network", "View IP Config", "Configuración IP listada exitosamente.")
    else:
        print_error(f"Error al ver configuración IP: {output}")
        log_action("Network", "View IP Config", f"Error al ver configuración IP: {output}")

def configure_static_ip():
    print_header("Configurar IP Estática")
    print_info("Esta operación requiere privilegios de administrador/root y es delicada.")
    interface_name = get_user_input("Ingrese el nombre de la interfaz de red (ej. 'Ethernet', 'eth0')")
    ip_address = get_user_input("Ingrese la dirección IP (ej. 192.168.1.100)")
    subnet_mask = get_user_input("Ingrese la máscara de subred (ej. 255.255.255.0)")
    gateway = get_user_input("Ingrese la puerta de enlace (opcional, dejar en blanco si no aplica)")

    os_type = get_os_type()
    if os_type == 'windows':
        # netsh requiere el nombre exacto de la interfaz y un orden específico
        command = f'netsh interface ip set address name="{interface_name}" static {ip_address} {subnet_mask}'
        if gateway:
            command += f' {gateway} 1' # '1' es el métrica, puedes ajustarlo
    else: # linux
        # Para Linux, los comandos varían mucho según la distribución y la configuración de red (systemd-networkd, NetworkManager, etc.)
        # Este es un ejemplo básico para interfaces 'ip' en sistemas basados en Debian/Ubuntu (ej. /etc/network/interfaces o directamente con 'ip a')
        print_error("La configuración de IP estática en Linux varía mucho.")
        print_error("Considere editar /etc/network/interfaces o usar nmtui/nmcli para NetworkManager.")
        
        # Ejemplo con 'ip' command, puede requerir deshacer DHCP primero
        command = f"ip address add {ip_address}/{subnet_mask} dev {interface_name}"
        if gateway:
            command += f" && ip route add default via {gateway}"

    print_info(f"Comando a ejecutar: {command}")
    confirm = get_user_input("¿Está seguro que desea ejecutar este comando? (s/N)").lower()
    if confirm == 's':
        output, status = execute_command(command, sudo=True)
        if status == 0:
            print_success(f"Configuración de IP estática aplicada a '{interface_name}'.")
            log_action("Network", "Configure Static IP", f"IP estática {ip_address}/{subnet_mask} configurada en '{interface_name}'.")
        else:
            print_error(f"Error al configurar IP estática: {output}")
            log_action("Network", "Configure Static IP", f"Error al configurar IP estática en '{interface_name}': {output}")
    else:
        print_info("Operación cancelada.")
        log_action("Network", "Configure Static IP", "Configuración de IP estática cancelada.")

def toggle_interface_status():
    print_header("Habilitar/Deshabilitar Interfaz")
    print_info("Esta operación requiere privilegios de administrador/root.")
    interface_name = get_user_input("Ingrese el nombre de la interfaz de red (ej. 'Ethernet', 'eth0')")
    action = get_user_input("¿Desea 'habilitar' o 'deshabilitar' la interfaz?").lower()

    os_type = get_os_type()
    if os_type == 'windows':
        if action == 'habilitar':
            command = f'netsh interface set interface name="{interface_name}" admin=enable'
        elif action == 'deshabilitar':
            command = f'netsh interface set interface name="{interface_name}" admin=disable'
        else:
            print_error("Acción inválida. Use 'habilitar' o 'deshabilitar'.")
            return
    else: # linux
        if action == 'habilitar':
            command = f"ip link set dev {interface_name} up"
        elif action == 'deshabilitar':
            command = f"ip link set dev {interface_name} down"
        else:
            print_error("Acción inválida. Use 'habilitar' o 'deshabilitar'.")
            return
    
    print_info(f"Comando a ejecutar: {command}")
    confirm = get_user_input("¿Está seguro que desea ejecutar este comando? (s/N)").lower()
    if confirm == 's':
        output, status = execute_command(command, sudo=True)
        if status == 0:
            print_success(f"Interfaz '{interface_name}' {action}da exitosamente.")
            log_action("Network", "Toggle Interface", f"Interfaz '{interface_name}' {action}da.")
        else:
            print_error(f"Error al {action} la interfaz: {output}")
            log_action("Network", "Toggle Interface", f"Error al {action} interfaz '{interface_name}': {output}")
    else:
        print_info("Operación cancelada.")
        log_action("Network", "Toggle Interface", f"Operación {action} interfaz cancelada.")

def view_routing_tables():
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
    print_header("Generar Log de Redes")
    log_action("Network", "Generate Log", "Generando log de redes.")
    print_info("Listado de Configuración IP:")
    view_ip_config()
    print_info("\nListado de Tablas de Enrutamiento:")
    view_routing_tables()
    print_info("\nListado de Conexiones de Red:")
    view_network_connections()
    print_success(f"Log de redes generado en {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')}")