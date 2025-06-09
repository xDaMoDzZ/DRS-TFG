from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os
import time

def resource_monitoring_menu():
    while True:
        clear_screen()
        print_header("Monitorización de Recursos")
        options = {
            "1": "Ver Uso de CPU y Memoria",
            "2": "Ver Uso de Disco",
            "3": "Ver Procesos Más Consumidores (Solo Linux)", # top en Windows no es tan directo
            "9": "Generar Log de Monitorización",
            "0": "Volver al Menú Principal"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            view_cpu_memory_usage()
        elif choice == '2':
            view_disk_usage()
        elif choice == '3':
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
        get_user_input("Presione Enter para continuar...")

def view_cpu_memory_usage():
    print_header("Uso de CPU y Memoria")
    os_type = get_os_type()
    if os_type == 'windows':
        print_info("Información de CPU y Memoria (WMIC):")
        cpu_command = "wmic cpu get LoadPercentage,NumberOfCores,NumberOfLogicalProcessors /value"
        mem_command = "wmic ComputerSystem get TotalPhysicalMemory /value && wmic OS get FreePhysicalMemory /value"
        
        cpu_output, cpu_status = execute_command(cpu_command)
        mem_output, mem_status = execute_command(mem_command)

        if cpu_status == 0:
            print_info("Uso de CPU:")
            print(cpu_output)
        else:
            print_error(f"Error al obtener uso de CPU: {cpu_output}")
        
        if mem_status == 0:
            print_info("Uso de Memoria (MB):")
            # Convertir bytes a MB para mejor legibilidad
            total_mem_bytes = 0
            free_mem_kb = 0
            for line in mem_output.splitlines():
                if "TotalPhysicalMemory" in line:
                    try:
                        total_mem_bytes = int(line.split('=')[1])
                    except ValueError:
                        pass
                if "FreePhysicalMemory" in line:
                    try:
                        free_mem_kb = int(line.split('=')[1])
                    except ValueError:
                        pass
            
            if total_mem_bytes > 0:
                total_mem_gb = total_mem_bytes / (1024**3)
                free_mem_gb = (free_mem_kb * 1024) / (1024**3)
                used_mem_gb = total_mem_gb - free_mem_gb
                print(f"  Memoria Total: {total_mem_gb:.2f} GB")
                print(f"  Memoria Libre: {free_mem_gb:.2f} GB")
                print(f"  Memoria Usada: {used_mem_gb:.2f} GB")
            else:
                print(mem_output)
        else:
            print_error(f"Error al obtener uso de memoria: {mem_output}")
        log_action("ResourceMonitoring", "View CPU/Memory Usage", "Uso de CPU y memoria listado (Windows).")

    else: # linux
        print_info("Uso de CPU y Memoria (top -bn1):")
        command = "top -bn1 | head -n 5" # Muestra resumen de CPU y memoria
        output, status = execute_command(command)
        if status == 0:
            print(output)
            log_action("ResourceMonitoring", "View CPU/Memory Usage", "Uso de CPU y memoria listado (Linux).")
        else:
            print_error(f"Error al obtener uso de CPU/Memoria: {output}")
            log_action("ResourceMonitoring", "View CPU/Memory Usage", f"Error al obtener uso de CPU/Memoria: {output}")

def view_disk_usage():
    print_header("Uso de Disco")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "wmic logicaldisk get Caption,Size,FreeSpace /value"
    else: # linux
        command = "df -h"
    
    output, status = execute_command(command)
    if status == 0:
        print_info("Uso de Disco:")
        print(output)
        log_action("ResourceMonitoring", "View Disk Usage", "Uso de disco listado exitosamente.")
    else:
        print_error(f"Error al obtener uso de disco: {output}")
        log_action("ResourceMonitoring", "View Disk Usage", f"Error al obtener uso de disco: {output}")

def view_top_processes_linux():
    print_header("Procesos Más Consumidores (Linux)")
    print_info("Los 10 procesos con mayor uso de CPU y Memoria:")
    command = "ps aux --sort=-%cpu,-%mem | head -n 11" # Top 10 procesos + encabezado
    output, status = execute_command(command)
    if status == 0:
        print(output)
        log_action("ResourceMonitoring", "View Top Processes", "Procesos más consumidores listados (Linux).")
    else:
        print_error(f"Error al obtener procesos: {output}")
        log_action("ResourceMonitoring", "View Top Processes", f"Error al obtener procesos: {output}")

def generate_monitoring_log():
    print_header("Generar Log de Monitorización")
    log_action("ResourceMonitoring", "Generate Log", "Generando log de monitorización.")
    print_info("Generando informe de CPU y Memoria...")
    view_cpu_memory_usage()
    print_info("\nGenerando informe de Uso de Disco...")
    view_disk_usage()
    if get_os_type() == 'linux':
        print_info("\nGenerando informe de Procesos Más Consumidores...")
        view_top_processes_linux()
    print_success(f"Log de monitorización generado en {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')}")