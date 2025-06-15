from utils.display import print_header, print_info, print_success, print_error, print_warning, clear_screen, print_menu, get_user_input
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os
import time
import re

def get_cpu_usage():
    """
    Obtiene y formatea el uso de CPU.
    """
    print_header("Uso de CPU") # No return_string
    os_type = get_os_type()

    if os_type == 'windows':
        print_info("Obteniendo información de CPU (Windows WMIC)...")
        cpu_command = "wmic cpu get LoadPercentage,NumberOfCores,NumberOfLogicalProcessors /value"
        cpu_output, cpu_status = execute_command(cpu_command)
        
        if cpu_status == 0:
            cpu_info = {}
            for line in cpu_output.splitlines():
                if '=' in line:
                    key, value = line.split('=', 1)
                    cpu_info[key.strip()] = value.strip()

            load_percentage = cpu_info.get('LoadPercentage', 'N/A')
            num_cores = cpu_info.get('NumberOfCores', 'N/A')
            num_logical_processors = cpu_info.get('NumberOfLogicalProcessors', 'N/A')

            print_info("--- Detalles de CPU ---")
            print_info(f"  Carga Actual: {load_percentage}%")
            print_info(f"  Núcleos Físicos: {num_cores}")
            print_info(f"  Procesadores Lógicos: {num_logical_processors}")
            log_action("ResourceMonitoring", "Get CPU Usage", f"Uso de CPU listado (Windows): {load_percentage}%")
        else:
            print_error(f"Error al obtener uso de CPU: {cpu_output}")
            log_action("ResourceMonitoring", "Get CPU Usage", f"Error al obtener uso de CPU: {cpu_output}")
    else: # linux
        print_info("Obteniendo uso de CPU (Linux top -bn1)...")
        command = "top -bn1 | head -n 5" # Muestra resumen de CPU
        output, status = execute_command(command)
        if status == 0:
            cpu_line = ""
            for line in output.splitlines():
                if "Cpu(s):" in line:
                    cpu_line = line.strip()
                    break
            
            print_info("--- Detalles de CPU ---")
            if cpu_line:
                print_info(f"```\n{cpu_line}\n```")
            else:
                print_warning("No se pudo parsear la línea de CPU de 'top'.")
            
            log_action("ResourceMonitoring", "Get CPU Usage", "Uso de CPU listado (Linux).")
        else:
            print_error(f"Error al obtener uso de CPU: {output}")
            log_action("ResourceMonitoring", "Get CPU Usage", f"Error al obtener uso de CPU: {output}")

    # Esta función ahora no devuelve nada, su salida es capturada por _run_module_function
    # return "" # No es necesario devolver una cadena vacía, _run_module_function capturará lo impreso.

def get_memory_usage():
    """
    Obtiene y formatea el uso de memoria.
    """
    print_header("Uso de Memoria")
    os_type = get_os_type()

    if os_type == 'windows':
        print_info("Obteniendo información de Memoria (Windows WMIC)...")
        mem_command = "wmic ComputerSystem get TotalPhysicalMemory /value && wmic OS get FreePhysicalMemory /value"
        mem_output, mem_status = execute_command(mem_command)

        if mem_status == 0:
            total_mem_bytes = 0
            free_mem_kb = 0
            for line in mem_output.splitlines():
                if "TotalPhysicalMemory" in line:
                    try:
                        total_mem_bytes = int(line.split('=')[1])
                    except (ValueError, IndexError):
                        pass
                if "FreePhysicalMemory" in line:
                    try:
                        free_mem_kb = int(line.split('=')[1])
                    except (ValueError, IndexError):
                        pass
            
            print_info("--- Detalles de Memoria ---")
            if total_mem_bytes > 0:
                total_mem_gb = total_mem_bytes / (1024**3)
                free_mem_gb = (free_mem_kb * 1024) / (1024**3)
                used_mem_gb = total_mem_gb - free_mem_gb
                
                print_info(f"  Memoria Total: {total_mem_gb:.2f} GB")
                print_info(f"  Memoria Libre: {free_mem_gb:.2f} GB")
                print_info(f"  Memoria Usada: {used_mem_gb:.2f} GB ({used_mem_gb/total_mem_gb:.2%})")
            else:
                print_warning("No se pudo obtener la memoria total. Salida bruta:")
                print_warning(f"```\n{mem_output}\n```")
            log_action("ResourceMonitoring", "Get Memory Usage", "Uso de memoria listado (Windows).")
        else:
            print_error(f"Error al obtener uso de memoria: {mem_output}")
            log_action("ResourceMonitoring", "Get Memory Usage", f"Error al obtener uso de memoria: {mem_output}")
    else: # linux
        print_info("Obteniendo uso de Memoria (Linux top -bn1)...")
        command = "top -bn1 | head -n 5" # Muestra resumen de memoria
        output, status = execute_command(command)
        if status == 0:
            mem_line = ""
            for line in output.splitlines():
                if "MiB Mem :" in line or "KiB Mem :" in line:
                    mem_line = line.strip()
                    break
            
            print_info("--- Detalles de Memoria ---")
            if mem_line:
                print(f"```\n{mem_line}\n```")
            else:
                print_warning("No se pudo parsear la línea de memoria de 'top'.")
            
            log_action("ResourceMonitoring", "Get Memory Usage", "Uso de memoria listado (Linux).")
        else:
            print_error(f"Error al obtener uso de memoria: {output}")
            log_action("ResourceMonitoring", "Get Memory Usage", f"Error al obtener uso de memoria: {output}")

def get_disk_usage():
    """
    Obtiene y formatea el uso de disco.
    """
    print_header("Uso de Disco")
    os_type = get_os_type()

    if os_type == 'windows':
        command = "wmic logicaldisk get Caption,Size,FreeSpace /format:list"
        output, status = execute_command(command)
        if status == 0:
            disk_info = {}
            current_drive = None
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("Caption="):
                    current_drive = line.split('=', 1)[1]
                    disk_info[current_drive] = {}
                elif current_drive and '=' in line:
                    key, value = line.split('=', 1)
                    disk_info[current_drive][key.strip()] = value.strip()
            
            print_info("--- Detalles de Unidades de Disco ---")
            for drive, info in disk_info.items():
                size_bytes = int(info.get('Size', 0))
                free_bytes = int(info.get('FreeSpace', 0))
                used_bytes = size_bytes - free_bytes

                total_gb = size_bytes / (1024**3) if size_bytes > 0 else 0
                free_gb = free_bytes / (1024**3) if free_bytes > 0 else 0
                used_gb = used_bytes / (1024**3) if used_bytes > 0 else 0
                
                percentage_used = (used_bytes / size_bytes) * 100 if size_bytes > 0 else 0

                print_info(f"Unidad: {drive}")
                print_info(f"  - Tamaño Total: {total_gb:.2f} GB")
                print_info(f"  - Espacio Libre: {free_gb:.2f} GB")
                print_info(f"  - Espacio Usado: {used_gb:.2f} GB")
                print_info(f"  - Uso: {percentage_used:.2f}%")
                print("")
            log_action("ResourceMonitoring", "Get Disk Usage", "Uso de disco listado exitosamente (Windows).")
        else:
            print_error(f"Error al obtener uso de disco: {output}")
            log_action("ResourceMonitoring", "Get Disk Usage", f"Error al obtener uso de disco: {output}")

    else: # linux
        command = "df -h"
        output, status = execute_command(command)
        if status == 0:
            print_info("--- Uso de Disco ---")
            print_info(f"```\n{output}\n```")
            log_action("ResourceMonitoring", "Get Disk Usage", "Uso de disco listado exitosamente (Linux).")
        else:
            print_error(f"Error al obtener uso de disco: {output}")
            log_action("ResourceMonitoring", "Get Disk Usage", f"Error al obtener uso de disco: {output}")

def get_network_stats():
    """
    Obtiene y formatea las estadísticas de red (bytes enviados/recibidos).
    """
    print_header("Estadísticas de Red")
    os_type = get_os_type()

    if os_type == 'windows':
        print_info("Obteniendo estadísticas de red (Windows netstat)...")
        command = "netstat -e"
        output, status = execute_command(command)
        
        if status == 0:
            bytes_sent = "N/A"
            bytes_received = "N/A"
            lines = output.splitlines()
            for line in lines:
                if "Bytes" in line:
                    match = re.search(r'Bytes\s*Received\s*=\s*(\d+)\s*Bytes\s*Sent\s*=\s*(\d+)', line, re.IGNORECASE)
                    if match:
                        bytes_received = f"{int(match.group(1)):,} bytes"
                        bytes_sent = f"{int(match.group(2)):,} bytes"
                        break
            
            print_info("--- Resumen de Tráfico de Red ---")
            print_info(f"  Bytes Recibidos: {bytes_received}")
            print_info(f"  Bytes Enviados: {bytes_sent}")
            log_action("ResourceMonitoring", "Get Network Stats", "Estadísticas de red listadas (Windows).")
        else:
            print_error(f"Error al obtener estadísticas de red: {output}")
            log_action("ResourceMonitoring", "Get Network Stats", f"Error al obtener estadísticas de red: {output}")

    else: # linux
        print_info("Obteniendo estadísticas de red (Linux ip -s link)...")
        command = "ip -s link"
        output, status = execute_command(command)
        
        if status == 0:
            network_info = {}
            current_interface = None
            for line in output.splitlines():
                if re.match(r'^\d+:\s+(\w+):', line):
                    current_interface = re.match(r'^\d+:\s+(\w+):', line).group(1)
                    network_info[current_interface] = {"RX": {}, "TX": {}}
                elif current_interface and "RX:" in line:
                    parts = line.strip().split()
                    if len(parts) >= 6:
                        network_info[current_interface]["RX"]["bytes"] = parts[0]
                        network_info[current_interface]["RX"]["packets"] = parts[1]
                elif current_interface and "TX:" in line:
                    parts = line.strip().split()
                    if len(parts) >= 6:
                        network_info[current_interface]["TX"]["bytes"] = parts[0]
                        network_info[current_interface]["TX"]["packets"] = parts[1]

            print_info("--- Estadísticas por Interfaz de Red ---")
            for iface, data in network_info.items():
                rx_bytes = data.get('RX', {}).get('bytes', 'N/A')
                tx_bytes = data.get('TX', {}).get('bytes', 'N/A')
                rx_packets = data.get('RX', {}).get('packets', 'N/A')
                tx_packets = data.get('TX', {}).get('packets', 'N/A')

                print_info(f"Interfaz: `{iface}`")
                print_info(f"  - Recibido (RX): {rx_bytes} bytes ({rx_packets} paquetes)")
                print_info(f"  - Enviado (TX): {tx_bytes} bytes ({tx_packets} paquetes)")
                print("")
            log_action("ResourceMonitoring", "Get Network Stats", "Estadísticas de red listadas (Linux).")
        else:
            print_error(f"Error al obtener estadísticas de red: {output}")
            log_action("ResourceMonitoring", "Get Network Stats", f"Error al obtener estadísticas de red: {output}")
            
    # return ""

def get_system_uptime():
    """
    Obtiene y formatea el tiempo de actividad del sistema (uptime).
    """
    print_header("Tiempo de Actividad del Sistema (Uptime)")
    os_type = get_os_type()

    if os_type == 'windows':
        print_info("Obteniendo tiempo de actividad (Windows systeminfo)...")
        command = "systeminfo | findstr /B /C:\"Tiempo de arranque del sistema\" /C:\"System Boot Time\""
        output, status = execute_command(command)
        
        if status == 0 and output.strip():
            uptime_line = output.strip()
            boot_time_str = uptime_line.split(':', 1)[1].strip()
            
            print_info("--- Detalles de Uptime ---")
            print_info(f"  Hora de Arranque del Sistema: {boot_time_str}")
            log_action("ResourceMonitoring", "Get System Uptime", f"Uptime listado (Windows): {boot_time_str}")
        else:
            print_error(f"Error al obtener tiempo de actividad: {output}")
            log_action("ResourceMonitoring", "Get System Uptime", f"Error al obtener tiempo de actividad (Windows): {output}")
    else: # linux
        print_info("Obteniendo tiempo de actividad (Linux uptime)...")
        command = "uptime -p"
        output, status = execute_command(command)
        
        if status == 0 and output.strip():
            print_info("--- Detalles de Uptime ---")
            print_info(f"  Tiempo de Actividad: {output.strip()}")
            log_action("ResourceMonitoring", "Get System Uptime", f"Uptime listado (Linux): {output.strip()}")
        else:
            command_fallback = "uptime"
            output_fallback, status_fallback = execute_command(command_fallback)
            if status_fallback == 0 and output_fallback.strip():
                print_info("--- Detalles de Uptime ---")
                print_info(f"  Tiempo de Actividad (formato estándar): {output_fallback.strip()}")
                log_action("ResourceMonitoring", "Get System Uptime", f"Uptime listado (Linux fallback): {output_fallback.strip()}")
            else:
                print_error(f"Error al obtener tiempo de actividad: {output_fallback}")
                log_action("ResourceMonitoring", "Get System Uptime", f"Error al obtener tiempo de actividad (Linux): {output_fallback}")

def view_top_processes_linux():
    """
    Verifica y muestra los procesos más consumidores en Linux.
    """
    print_header("Procesos Más Consumidores (Linux)")
    
    os_type = get_os_type()
    if os_type == 'linux':
        print_info("Obteniendo los 10 procesos con mayor uso de CPU y Memoria...")
        command = "ps aux --sort=-%cpu,-%mem | head -n 11"
        output, status = execute_command(command)
        if status == 0:
            print_info("--- Top 10 Procesos ---")
            print_info(f"```\n{output}\n```")
            log_action("ResourceMonitoring", "View Top Processes", "Procesos más consumidores listados (Linux).")
        else:
            print_error(f"Error al obtener procesos: {output}")
            log_action("ResourceMonitoring", "View Top Processes", f"Error al obtener procesos: {output}")
    else:
        print_error("Esta opción solo está disponible en Linux.")
        log_action("ResourceMonitoring", "View Top Processes", "Intento de ver procesos top en SO no Linux.")
    
def generate_monitoring_log():
    """
    Genera un log completo de la monitorización de recursos llamando a las funciones granular.
    """
    print_header("Generar Log de Monitorización")
    log_action("ResourceMonitoring", "Generate Log", "Generando log de monitorización.")
    
    print_info("\n--- Informe de Uso de CPU ---")
    get_cpu_usage() # Llama a la función que imprime directamente

    print_info("\n--- Informe de Uso de Memoria ---")
    get_memory_usage()

    print_info("\n--- Informe de Uso de Disco ---")
    get_disk_usage()

    print_info("\n--- Informe de Estadísticas de Red ---")
    get_network_stats()

    print_info("\n--- Informe de Tiempo de Actividad del Sistema ---")
    get_system_uptime()

    if get_os_type() == 'linux':
        print_info("\n--- Informe de Procesos Más Consumidores ---")
        view_top_processes_linux()
    else:
        print_info("\nLa opción 'Procesos Más Consumidores' solo está disponible en Linux y no se incluyó en este log.")

    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
    print_success(f"Log de monitorización generado. Revisa el directorio 'logs' en la raíz del proyecto para los detalles.")
    print(f"Path del log: `{os.path.abspath(log_file_path)}`")
    
def resource_monitoring_menu():
    """
    Muestra el menú de monitorización de recursos y maneja las interacciones del usuario por consola.
    """
    while True:
        clear_screen()
        print_header("Monitorización de Recursos")
        options = {
            "1": "Ver Uso de CPU",
            "2": "Ver Uso de Memoria",
            "3": "Ver Uso de Disco",
            "4": "Ver Estadísticas de Red",
            "5": "Ver Tiempo de Actividad del Sistema (Uptime)",
            "6": "Ver Procesos Más Consumidores (Solo Linux)",
            "9": "Generar Log de Monitorización Completo",
            "0": "Volver al Menú Principal"
        }

        print_menu(options)
        
        choice = get_user_input("Seleccione una opción: ")

        if choice == '1':
            get_cpu_usage()
        elif choice == '2':
            get_memory_usage()
        elif choice == '3':
            get_disk_usage()
        elif choice == '4':
            get_network_stats()
        elif choice == '5':
            get_system_uptime()
        elif choice == '6':
            if get_os_type() == 'linux':
                view_top_processes_linux()
            else:
                print_error("Esta opción solo está disponible en Linux.")
        elif choice == '9':
            generate_monitoring_log()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        
        input("Presione Enter para continuar...")