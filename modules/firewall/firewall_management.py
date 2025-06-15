from utils.display import print_header, print_info, print_success, print_error, print_warning, get_user_input, print_menu, clear_screen
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os

def firewall_menu():
    """
    Muestra el menú de gestión de Firewall y maneja las interacciones del usuario por consola.
    Pasa los inputs directamente a las funciones de gestión.
    """
    while True:
        clear_screen()
        print_header("Gestión de Firewall")
        options = {
            "1": "Ver Estado del Firewall",
            "2": "Habilitar Firewall (Requiere Privilegios)",
            "3": "Deshabilitar Firewall (Requiere Privilegios)",
            "4": "Listar Reglas del Firewall",
            "5": "Añadir Regla (Permitir Puerto) (Requiere Privilegios)",
            "6": "Eliminar Regla (Permitir Puerto) (Requiere Privilegios)",
            "7": "Mostrar Información de Regla por Nombre",
            "9": "Generar Log de Firewall",
            "0": "Volver al Menú Principal"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            view_firewall_status()
        elif choice == '2':
            confirm = get_user_input("¿Está seguro que desea habilitar el firewall? Esto podría afectar la conectividad. (s/N)").lower()
            enable_firewall(confirm)
        elif choice == '3':
            confirm = get_user_input("¿Está seguro que desea deshabilitar el firewall? Esto podría dejar el sistema vulnerable. (s/N)").lower()
            disable_firewall(confirm)
        elif choice == '4':
            list_firewall_rules()
        elif choice == '5':
            print_info("Añadir Regla (Permitir Puerto)")
            print_info("Esta operación requiere privilegios de administrador/root.")
            rule_name = get_user_input("Ingrese un nombre para la regla (ej. 'Permitir_SSH')")
            port = get_user_input("Ingrese el número de puerto a permitir (ej. 22, 8080)")
            protocol = get_user_input("Ingrese el protocolo (tcp/udp/any, dejar en blanco para 'any')").lower() or "any"
            direction = get_user_input("Ingrese la dirección (in/out, dejar en blanco para 'in')").lower() or "in"
            
            confirm = get_user_input("¿Está seguro que desea añadir esta regla? (s/N)").lower()
            if confirm == 's': # Solo llama si el usuario confirma en el menú
                add_allow_port_rule(rule_name, port, protocol, direction)
            else:
                print_info("Operación cancelada.")
                log_action("Firewall", "Add Rule", "Adición de regla cancelada por el usuario en el menú.")
        elif choice == '6':
            print_info("Eliminar Regla (Permitir Puerto)")
            print_info("Esta operación requiere privilegios de administrador/root.")
            rule_name = get_user_input("Ingrese el nombre de la regla a eliminar (Windows) / (Descripción para Linux)")
            port = get_user_input("Ingrese el número de puerto de la regla a eliminar (Linux UFW) (ej. 22)")
            protocol = get_user_input("Ingrese el protocolo de la regla (tcp/udp/any, dejar en blanco para 'any')").lower() or "any"

            confirm = get_user_input("¿Está seguro que desea eliminar esta regla? (s/N)").lower()
            if confirm == 's': # Solo llama si el usuario confirma en el menú
                delete_allow_port_rule(rule_name, port, protocol, confirm) # Pasar 's' para confirmar internamente
            else:
                print_info("Operación cancelada.")
                log_action("Firewall", "Delete Rule", "Eliminación de regla cancelada por el usuario en el menú.")
        elif choice == '7':
            rule_name = get_user_input("Ingrese el nombre de la regla a mostrar")
            show_rule_by_name(rule_name)
        elif choice == '9':
            generate_firewall_log()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        get_user_input("Presione Enter para continuar...")

def view_firewall_status():
    """
    Verifica y muestra el estado actual del firewall (Windows o Linux) con un formato mejorado
    y evita la duplicación de salida en consola.
    """
    print_header("Ver Estado del Firewall")
    os_type = get_os_type()
    
    # Variables para almacenar el resumen del estado y el contenido detallado
    firewall_name = "Desconocido"
    status_summary = "" # Mensaje de éxito/error/advertencia general
    detailed_output = "" # Contenido detallado del comando del firewall

    if os_type == 'windows':
        firewall_name = "Windows Defender Firewall"
        command = "netsh advfirewall show allprofiles state"
        output, status = execute_command(command)
        
        if status == 0:
            if "State" or "Estado" in output:
                state_lines = [line.strip() for line in output.split('\n') if "State" or "Estado" in line]
                detailed_output = "Estado del Firewall de Windows:\n" + "\n".join(state_lines)
                status_summary = f"Estado de {firewall_name} obtenido exitosamente."
                log_action("Firewall", "View Status", f"Estado de {firewall_name} listado.")
            else:
                detailed_output = (
                    f"El comando se ejecutó exitosamente, pero no se pudo determinar el estado del firewall de la salida. "
                    f"Posiblemente por permisos insuficientes o salida inesperada.\n"
                    f"--- Salida completa del comando netsh ---\n{output.strip()}\n--- Fin de Salida ---"
                )
                status_summary = f"Advertencia: Salida inesperada de {firewall_name}."
                log_action("Firewall", "View Status", 
                           f"Comando exitoso pero salida inesperada de {firewall_name}. Output: {output.strip()[:200]}...")
        else:
            detailed_output = f"Error al ejecutar el comando de estado de {firewall_name}:\n{output}"
            status_summary = f"Error al ver estado de {firewall_name} (código: {status})."
            log_action("Firewall", "View Status", f"Error al ver estado de {firewall_name} (código: {status}).")

    else: # linux
        # Primero intentamos con UFW
        firewall_name = "UFW (Uncomplicated Firewall)"
        command = "ufw status"
        output, status = execute_command(command, sudo=True)

        if status == 0:
            if "Status: active" in output or "Status: inactive" in output:
                status_line = [line.strip() for line in output.split('\n') if "Status" in line][0]
                detailed_output = f"{firewall_name}: {status_line.replace('Status: ', '')}"
                if "Status: active" in output and len(output.split('\n')) > 1:
                    detailed_output += "\nReglas de UFW (primeras 5 líneas):"
                    detailed_output += "\n" + "\n".join(output.split('\n')[1:6])
                    if len(output.split('\n')) > 6:
                        detailed_output += "\n..."
                status_summary = f"Estado de {firewall_name} obtenido exitosamente."
                log_action("Firewall", "View Status", f"Estado de {firewall_name} listado.")
            else:
                 detailed_output = f"UFW encontrado, pero salida inesperada:\n{output}"
                 status_summary = f"Advertencia: Salida inesperada de {firewall_name}."
                 log_action("Firewall", "View Status", f"UFW encontrado pero salida inesperada.")
        else:
            # Si UFW no está activo o no se encuentra, intentamos con iptables
            firewall_name = "iptables"
            # Este mensaje informativo es útil en consola, pero no debe duplicarse como error.
            print_info("UFW no encontrado o no activo. Intentando con iptables...") 
            command = "sudo iptables -L -n -v"
            output, status = execute_command(command, sudo=True)

            if status == 0:
                detailed_output = f"{firewall_name} (Reglas):"
                lines = output.split('\n')
                if len(lines) > 10: # Mostrar solo las primeras 10 líneas si hay muchas
                    detailed_output += "\n" + "\n".join(lines[:10]) + "\n..."
                else:
                    detailed_output += "\n" + output
                status_summary = f"Estado de {firewall_name} obtenido exitosamente."
                log_action("Firewall", "View Status", f"Estado de {firewall_name} listado.")
            else:
                detailed_output = f"Error al ejecutar el comando de estado de {firewall_name}:\n{output}"
                status_summary = f"Error al ver estado de {firewall_name} (código: {status})."
                log_action("Firewall", "View Status", f"Error al ver estado de {firewall_name} (código: {status}).")
    
    # --- Bloque de salida consolidado para consola y GUI ---
    print_info("-" * 30)
    print_info(f"Firewall detectado: {firewall_name}")
    print_info("-" * 30)
    
    # Imprime el resumen de estado con el color adecuado
    if "Error" in status_summary:
        print_error(status_summary)
        # Si hubo un error, muestra el detalle también en rojo
        if detailed_output:
            print_error(detailed_output) 
    elif "Advertencia" in status_summary:
        print_warning(status_summary)
        # Si hubo una advertencia, muestra el detalle también en amarillo
        if detailed_output:
            print_warning(detailed_output)
    else: # Si es un éxito
        print_success(status_summary)
        # Para el éxito, el detalle se muestra en color normal (info)
        if detailed_output:
            print_info(detailed_output)
    
    # Mensaje final de cierre (siempre en info)
    print_info("-" * 30)

def enable_firewall(confirm: str):
    """
    Habilita el firewall (Windows o Linux).
    Args:
        confirm (str): 's' para confirmar, 'n' para cancelar.
    """
    print_header("Habilitar Firewall")
    if confirm.lower() != 's':
        print_info("Operación cancelada.")
        log_action("Firewall", "Enable Firewall", "Habilitación de firewall cancelada.")
        return

    os_type = get_os_type()
    if os_type == 'windows':
        command = "netsh advfirewall set allprofiles state on"
    else: # linux
        command = "ufw enable"
        print_info("Consideraciones en Linux: Si UFW no está instalado o en uso, esta operación puede fallar.")
        print_info("Para RHEL/CentOS, considere 'sudo systemctl enable firewalld' y 'sudo systemctl start firewalld'.")
        print_info("Para reglas directas de iptables, consulte la documentación.")
    
    print_info(f"Comando a ejecutar: {command}")
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success("Firewall habilitado exitosamente.")
        print_info(output) # Mostrar salida del comando si existe
        log_action("Firewall", "Enable Firewall", "Firewall habilitado.")
    else:
        print_error(f"Error al habilitar firewall: {output}")
        log_action("Firewall", "Enable Firewall", f"Error al habilitar firewall: {output}")

def disable_firewall(confirm: str):
    """
    Deshabilita el firewall (Windows o Linux).
    Args:
        confirm (str): 's' para confirmar, 'n' para cancelar.
    """
    print_header("Deshabilitar Firewall")
    if confirm.lower() != 's':
        print_info("Operación cancelada.")
        log_action("Firewall", "Disable Firewall", "Deshabilitación de firewall cancelada.")
        return

    os_type = get_os_type()
    if os_type == 'windows':
        command = "netsh advfirewall set allprofiles state off"
    else: # linux
        command = "ufw disable"
        print_info("Consideraciones en Linux: Si UFW no está instalado o en uso, esta operación puede fallar.")
        print_info("Para RHEL/CentOS, considere 'sudo systemctl stop firewalld' y 'sudo systemctl disable firewalld'.")
        print_info("Para limpiar reglas de iptables, use 'sudo iptables -F' y 'sudo iptables -X'.")
    
    print_info(f"Comando a ejecutar: {command}")
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success("Firewall deshabilitado exitosamente.")
        print_info(output) # Mostrar salida del comando si existe
        log_action("Firewall", "Disable Firewall", "Firewall deshabilitado.")
    else:
        print_error(f"Error al deshabilitar firewall: {output}")
        log_action("Firewall", "Disable Firewall", f"Error al deshabilitar firewall: {output}")

def list_firewall_rules():
    """
    Lista todas las reglas del firewall (Windows o Linux).
    """
    print_header("Listar Reglas del Firewall")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "netsh advfirewall firewall show rule name=all"
        output, status = execute_command(command)
    else: # linux
        command = "ufw status verbose"
        output, status = execute_command(command, sudo=True)
        if status != 0:
            print_info("UFW no encontrado o no activo. Intentando con iptables...")
            command = "sudo iptables -L -n -v" # Más completo que iptables -S para visualización
            output, status = execute_command(command, sudo=True)
    
    if status == 0:
        print_info("Reglas del Firewall:")
        print_info(output) # Usamos print_info
        log_action("Firewall", "List Rules", "Reglas del firewall listadas exitosamente.")
    else:
        print_error(f"Error al listar reglas del firewall: {output}")
        log_action("Firewall", "List Rules", f"Error al listar reglas del firewall: {output}")

def add_allow_port_rule(rule_name: str, port: str, protocol: str = "any", direction: str = "in"):
    """
    Añade una regla para permitir el tráfico en un puerto específico.
    Args:
        rule_name (str): Nombre de la regla.
        port (str): Número de puerto.
        protocol (str): Protocolo (tcp/udp/any).
        direction (str): Dirección (in/out).
    """
    print_header("Añadir Regla (Permitir Puerto)")
    print_info("Esta operación requiere privilegios de administrador/root.")
    
    if not rule_name or not port:
        print_error("Nombre de regla y puerto son obligatorios.")
        log_action("Firewall", "Add Rule", "Error: Campos obligatorios vacíos.")
        return

    protocol = protocol.lower() if protocol else "any"
    direction = direction.lower() if direction else "in"

    os_type = get_os_type()
    if os_type == 'windows':
        command = f'netsh advfirewall firewall add rule name="{rule_name}" dir={direction} action=allow protocol={protocol} localport={port}'
    else: # linux (ufw)
        if direction == 'in':
            command = f"ufw allow {port}/{protocol}"
        elif direction == 'out':
            command = f"ufw allow out {port}/{protocol}"
        else:
            print_error("Dirección inválida. Use 'in' o 'out'.")
            log_action("Firewall", "Add Rule", "Error: Dirección inválida.")
            return
        print_info("Si UFW no está en uso, necesitará reglas de iptables (ej: sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT).")
    
    print_info(f"Comando a ejecutar: {command}")
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Regla '{rule_name}' (permitir puerto {port}/{protocol}, {direction}) añadida exitosamente.")
        print_info(output)
        log_action("Firewall", "Add Rule", f"Regla '{rule_name}' (permitir puerto {port}/{protocol}, {direction}) añadida.")
    else:
        print_error(f"Error al añadir regla: {output}")
        log_action("Firewall", "Add Rule", f"Error al añadir regla '{rule_name}': {output}")

def delete_allow_port_rule(rule_name: str, port: str, protocol: str = "any", confirm: str = "n"):
    
    """
    Elimina una regla para permitir el tráfico en un puerto específico.
    Args:
        rule_name (str): Nombre de la regla a eliminar (usado directamente en Windows).
        port (str): Número de puerto (necesario para UFW).
        protocol (str): Protocolo (tcp/udp/any, necesario para UFW).
        confirm (str): 's' para confirmar, 'n' para cancelar.
    """
    print_header("Eliminar Regla (Permitir Puerto)")
    print_info("Esta operación requiere privilegios de administrador/root.")
    
    if confirm.lower() != 's':
        print_info("Operación cancelada.")
        log_action("Firewall", "Delete Rule", "Eliminación de regla cancelada.")
        return

    if not rule_name and not port:
        print_error("Debe proporcionar al menos el nombre de la regla (Windows) o el puerto/protocolo (Linux).")
        log_action("Firewall", "Delete Rule", "Error: Campos obligatorios vacíos.")
        return

    protocol = protocol.lower() if protocol else "any"

    os_type = get_os_type()
    if os_type == 'windows':
        command = f'netsh advfirewall firewall delete rule name="{rule_name}"'
    else: # linux (ufw)
        # UFW no permite eliminar por nombre directo. Usamos puerto/protocolo.
        print_warning("En Linux (UFW), la eliminación de reglas por nombre exacto no es directa. Se usa puerto/protocolo.")
        print_info("Considere 'ufw status numbered' y eliminar por número para mayor precisión.")
        command = f"ufw delete allow {port}/{protocol}"

    print_info(f"Comando a ejecutar: {command}")
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Regla '{rule_name or f'{port}/{protocol}'}' eliminada exitosamente.")
        print_info(output)
        log_action("Firewall", "Delete Rule", f"Regla '{rule_name or f'{port}/{protocol}'}' eliminada.")
    else:
        print_error(f"Error al eliminar regla: {output}")
        log_action("Firewall", "Delete Rule", f"Error al eliminar regla '{rule_name or f'{port}/{protocol}'}': {output}")

def add_deny_port_rule(rule_name: str, port: str, protocol: str = "any", direction: str = "in"):
    """
    Añade una regla para denegar el tráfico en un puerto específico.
    Args:
        rule_name (str): Nombre de la regla.
        port (str): Número de puerto.
        protocol (str): Protocolo (tcp/udp/any).
        direction (str): Dirección (in/out).
    """
    print_header("Añadir Regla (Denegar Puerto)")
    print_info("Esta operación requiere privilegios de administrador/root.")
    
    if not rule_name or not port:
        print_error("Nombre de regla y puerto son obligatorios.")
        log_action("Firewall", "Add Deny Rule", "Error: Campos obligatorios vacíos.")
        return

    protocol = protocol.lower() if protocol else "any"
    direction = direction.lower() if direction else "in"

    os_type = get_os_type()
    if os_type == 'windows':
        command = f'netsh advfirewall firewall add rule name="{rule_name}" dir={direction} action=block protocol={protocol} localport={port}'
    else: # linux (ufw)
        if direction == 'in':
            command = f"ufw deny {port}/{protocol}"
        elif direction == 'out':
            command = f"ufw deny out {port}/{protocol}"
        else:
            print_error("Dirección inválida. Use 'in' o 'out'.")
            log_action("Firewall", "Add Deny Rule", "Error: Dirección inválida.")
            return
        print_info("Si UFW no está en uso, necesitará reglas de iptables (ej: sudo iptables -A INPUT -p tcp --dport 80 -j DROP).")
    
    print_info(f"Comando a ejecutar: {command}")
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Regla '{rule_name}' (denegar puerto {port}/{protocol}, {direction}) añadida exitosamente.")
        print_info(output)
        log_action("Firewall", "Add Deny Rule", f"Regla '{rule_name}' (denegar puerto {port}/{protocol}, {direction}) añadida.")
    else:
        print_error(f"Error al añadir regla de denegación: {output}")
        log_action("Firewall", "Add Deny Rule", f"Error al añadir regla de denegación '{rule_name}': {output}")

def add_app_rule(rule_name: str, app_path: str, action: str = "allow", direction: str = "in"):
    """
    Añade una regla para permitir/denegar una aplicación. Principalmente para Windows.
    UFW puede usar perfiles de aplicación, pero no es tan directo como un path.
    Args:
        rule_name (str): Nombre de la regla.
        app_path (str): Ruta completa al ejecutable de la aplicación.
        action (str): 'allow' o 'block'.
        direction (str): 'in' o 'out'.
    """
    print_header(f"Añadir Regla ({action.capitalize()} Aplicación)")
    print_info("Esta operación requiere privilegios de administrador/root.")
    
    if not rule_name or not app_path:
        print_error("Nombre de regla y ruta de aplicación son obligatorios.")
        log_action("Firewall", f"Add {action.capitalize()} App Rule", "Error: Campos obligatorios vacíos.")
        return

    action = action.lower()
    direction = direction.lower()

    os_type = get_os_type()
    if os_type == 'windows':
        # Ejemplo: netsh advfirewall firewall add rule name="Allow_MyApp" dir=in action=allow program="C:\Program Files\MyApp\MyApp.exe" enable=yes
        command = f'netsh advfirewall firewall add rule name="{rule_name}" dir={direction} action={action} program="{app_path}" enable=yes'
    else: # linux (UFW o iptables)
        # UFW permite perfiles de aplicación para apps conocidas, pero no directamente por path arbitrario.
        # iptables es más complejo para este tipo de regla.
        print_warning("En Linux, la gestión de reglas por aplicación por ruta de ejecutable no es tan directa como en Windows.")
        print_info("Considera usar reglas basadas en puertos o perfiles de aplicación UFW si están disponibles (ej: ufw allow 'Apache').")
        print_error("La adición de reglas de firewall por ruta de aplicación no es directamente compatible en Linux con este método.")
        log_action("Firewall", f"Add {action.capitalize()} App Rule", "Operación no compatible directamente en Linux.")
        return # Salir si no es Windows

    print_info(f"Comando a ejecutar: {command}")
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Regla '{rule_name}' ({action} aplicación '{app_path}', {direction}) añadida exitosamente.")
        print_info(output)
        log_action("Firewall", f"Add {action.capitalize()} App Rule", f"Regla '{rule_name}' ({action} aplicación '{app_path}', {direction}) añadida.")
    else:
        print_error(f"Error al añadir regla de aplicación '{rule_name}': {output}")
        log_action("Firewall", f"Add {action.capitalize()} App Rule", f"Error al añadir regla de aplicación '{rule_name}': {output}")

def delete_app_rule(rule_name: str, confirm: str = "n"):
    """
    Elimina una regla de aplicación por su nombre.
    Args:
        rule_name (str): Nombre de la regla de aplicación a eliminar.
        confirm (str): 's' para confirmar, 'n' para cancelar.
    """
    print_header("Eliminar Regla de Aplicación")
    print_info("Esta operación requiere privilegios de administrador/root.")
    
    if confirm.lower() != 's':
        print_info("Operación cancelada.")
        log_action("Firewall", "Delete App Rule", "Eliminación de regla de aplicación cancelada.")
        return
    
    if not rule_name:
        print_error("El nombre de la regla a eliminar es obligatorio.")
        log_action("Firewall", "Delete App Rule", "Error: Nombre de regla vacío.")
        return

    os_type = get_os_type()
    if os_type == 'windows':
        command = f'netsh advfirewall firewall delete rule name="{rule_name}"'
    else: # linux
        print_warning("En Linux, la eliminación de reglas de aplicación por nombre no es directamente compatible con este método.")
        print_info("Considere listar las reglas y eliminarlas manualmente si es posible.")
        log_action("Firewall", "Delete App Rule", "Operación de eliminación por nombre de aplicación no compatible directamente en Linux.")
        return # Salir si no es Windows

    print_info(f"Comando a ejecutar: {command}")
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Regla de aplicación '{rule_name}' eliminada exitosamente.")
        print_info(output)
        log_action("Firewall", "Delete App Rule", f"Regla de aplicación '{rule_name}' eliminada.")
    else:
        print_error(f"Error al eliminar regla de aplicación '{rule_name}': {output}")
        log_action("Firewall", "Delete App Rule", f"Error al eliminar regla de aplicación '{rule_name}': {output}")

def show_rule_by_name(rule_name: str):
    """
    Muestra la información detallada de una regla de firewall por su nombre.
    Args:
        rule_name (str): El nombre de la regla a buscar.
    """
    print_header("Mostrar Información de Regla por Nombre")
    if not rule_name:
        print_error("El nombre de la regla no puede estar vacío.")
        log_action("Firewall", "Show Rule by Name", "Error: Nombre de regla vacío.")
        return

    os_type = get_os_type()
    if os_type == 'windows':
        command = f'netsh advfirewall firewall show rule name="{rule_name}"'
        output, status = execute_command(command)
        
        if status == 0:
            if rule_name.lower() in output.lower(): # Case-insensitive check
                print_info(f"Información de la regla '{rule_name}':")
                print_info(output)
                log_action("Firewall", "Show Rule by Name", f"Información de la regla '{rule_name}' mostrada exitosamente.")
            else:
                print_error(f"No se encontró ninguna regla con el nombre '{rule_name}'.")
                print_info(output) # Mostrar la salida completa para ayudar a depurar
                log_action("Firewall", "Show Rule by Name", f"No se encontró la regla '{rule_name}'.")
        else:
            print_error(f"Error al mostrar información de la regla: {output}")
            log_action("Firewall", "Show Rule by Name", f"Error al mostrar información de la regla '{rule_name}': {output}")
    else: # linux
        print_warning("En Linux (UFW/iptables), no hay un comando directo para mostrar una regla específica por nombre.")
        print_info("Se listarán todas las reglas detalladas y se recomienda buscar manualmente.")
        print_info("Considere revisar la salida de 'ufw status verbose' o 'sudo iptables -S' para buscar manualmente.")
        
        command = "ufw status verbose"
        output, status = execute_command(command, sudo=True)
        if status != 0:
            print_info("UFW no encontrado o no activo. Intentando con iptables...")
            command = "sudo iptables -S" # Muestra las reglas de iptables en formato que se pueden volver a añadir
            output, status = execute_command(command, sudo=True)
        
        if status == 0:
            print_info(f"Salida completa de las reglas del firewall (busque '{rule_name}' manualmente):")
            print_info(output)
            log_action("Firewall", "Show Rule by Name", f"Reglas del firewall listadas para buscar '{rule_name}'.")
        else:
            print_error(f"Error al listar reglas para buscar por nombre: {output}")
            log_action("Firewall", "Show Rule by Name", f"Error al listar reglas para buscar '{rule_name}': {output}")

def generate_firewall_log():
    """
    Genera un informe consolidado del estado y reglas del firewall.
    """
    print_header("Generar Log de Firewall")
    log_action("Firewall", "Generate Log", "Generando log de gestión de firewall.")
    print_info("Generando informe de Estado del Firewall...")
    view_firewall_status() # Reutiliza la función existente
    print_info("\nGenerando informe de Reglas del Firewall...")
    list_firewall_rules() # Reutiliza la función existente
    # La ruta del log ya la maneja utils/logger, no es necesario imprimirla aquí.
    print_success("Log de firewall generado. Consulte los archivos de log para detalles.")