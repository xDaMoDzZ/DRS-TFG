from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os
import psutil

def process_menu():
    while True:
        clear_screen()
        print_header("Gestión de Procesos y Subprocesos")
        options = {
            "1": "Listar Procesos",
            "2": "Terminar Proceso por PID",
            "3": "Terminar Proceso por Nombre (Requiere PID en Windows)",
            "4": "Buscar Información de Proceso por Nombre", # Nueva opción
            "9": "Generar Log de Procesos",
            "0": "Volver al Menú Principal"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            list_processes()
        elif choice == '2':
            terminate_process_by_pid()
        elif choice == '3':
            terminate_process_by_name()
        elif choice == '4': # Manejo de la nueva opción
            find_process_info_by_name()
        elif choice == '9':
            generate_process_log()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        get_user_input("Presione Enter para continuar...")

def list_processes():
    print_header("Listar Procesos")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "tasklist /v /fo list" # /v: verbose, /fo list: list format
    else: # linux
        command = "ps aux"
    
    output, status = execute_command(command)
    if status == 0:
        print_info("Procesos del sistema:")
        print(output)
        log_action("Process", "List Processes", "Procesos listados exitosamente.")
    else:
        print_error(f"Error al listar procesos: {output}")
        log_action("Process", "List Processes", f"Error al listar procesos: {output}")

def terminate_process_by_pid():
    print_header("Terminar Proceso por PID")
    pid = get_user_input("Ingrese el PID del proceso a terminar")
    
    os_type = get_os_type()
    if os_type == 'windows':
        command = f"taskkill /PID {pid} /F" # /F: force
    else: # linux
        command = f"kill {pid}" # -9 para forzar
    
    print_info(f"Comando a ejecutar: {command}")
    confirm = get_user_input(f"¿Está seguro que desea terminar el proceso con PID {pid}? (s/N)").lower()
    if confirm == 's':
        output, status = execute_command(command, sudo=True)
        if status == 0:
            print_success(f"Proceso con PID {pid} terminado exitosamente.")
            log_action("Process", "Terminate by PID", f"Proceso con PID {pid} terminado.")
        else:
            print_error(f"Error al terminar proceso con PID {pid}: {output}")
            log_action("Process", "Terminate by PID", f"Error al terminar proceso con PID {pid}: {output}")
    else:
        print_info("Operación cancelada.")
        log_action("Process", "Terminate by PID", f"Terminación de proceso PID {pid} cancelada.")

def terminate_process_by_name():
    print_header("Terminar Proceso por Nombre")
    process_name = get_user_input("Ingrese el nombre del proceso a terminar (ej. 'chrome.exe', 'apache2')")
    
    os_type = get_os_type()
    if os_type == 'windows':
        command = f'taskkill /IM "{process_name}" /F'
        print_info(f"Nota: En Windows, para procesos con múltiples instancias o si no se termina, puede que necesites el PID específico.")
    else: # linux
        command = f"pkill {process_name}" # pkill es más robusto para nombres
        print_info(f"Nota: En Linux, 'pkill' terminará todos los procesos con ese nombre.")
    
    print_info(f"Comando a ejecutar: {command}")
    confirm = get_user_input(f"¿Está seguro que desea terminar el proceso(s) '{process_name}'? (s/N)").lower()
    if confirm == 's':
        output, status = execute_command(command, sudo=True)
        if status == 0:
            print_success(f"Proceso(s) '{process_name}' terminado(s) exitosamente.")
            log_action("Process", "Terminate by Name", f"Proceso(s) '{process_name}' terminado(s).")
        else:
            print_error(f"Error al terminar proceso(s) '{process_name}': {output}")
            log_action("Process", "Terminate by Name", f"Error al terminar proceso(s) '{process_name}': {output}")
    else:
        print_info("Operación cancelada.")
        log_action("Process", "Terminate by Name", f"Terminación de proceso '{process_name}' cancelada.")

def find_process_info_by_name():
    """
    Busca procesos por nombre o parte del nombre y muestra su información.
    Ahora solo lista, no pregunta por terminación.
    """
    clear_screen()
    print_header("Buscar Información de Proceso por Nombre")
    process_name_query = get_user_input(
        "Ingrese el nombre o parte del nombre del proceso a buscar"
    )

    found_processes = []
    try:
        for proc in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_info"]):
            if process_name_query.lower() in proc.info["name"].lower():
                found_processes.append(proc)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        # Ignorar procesos que desaparecen o son inaccesibles durante la iteración
        pass

    if found_processes:
        print_success(f"Se encontraron los siguientes procesos para '{process_name_query}':")
        # Encabezados de la tabla
        print(f"{'PID':<10} {'Nombre':<30} {'Usuario':<20} {'CPU %':<10} {'Mem (MB)':<12}")
        print(f"{'-'*10:<10} {'-'*30:<30} {'-'*20:<20} {'-'*10:<10} {'-'*12:<12}")

        for proc in found_processes:
            try:
                pid = proc.info["pid"]
                name = proc.info["name"]
                username = proc.info["username"] if proc.info["username"] else "N/A"
                cpu_percent = proc.info["cpu_percent"]
                mem_info = proc.info["memory_info"]
                memory_mb = round(mem_info.rss / (1024 * 1024), 2) if mem_info else 0

                print(
                    f"{pid:<10} {name:<30} {username:<20} {cpu_percent:<10.2f} {memory_mb:<12.2f}"
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue # Saltar procesos si son inaccesibles

        log_action(
            "Process",
            "Search Process",
            f"Procesos buscados por nombre '{process_name_query}'.",
        )
    else:
        print_info(f"No se encontraron procesos con el nombre '{process_name_query}'.")
        log_action(
            "Process",
            "Search Process",
            f"No se encontraron procesos con el nombre '{process_name_query}'.",
        )

def terminate_process_by_pid_internal(pid):
    os_type = get_os_type()
    if os_type == 'windows':
        command = f"taskkill /PID {pid} /F"
    else: # linux
        command = f"kill {pid}" # -9 para forzar
    
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Proceso con PID {pid} terminado exitosamente.")
        log_action("Process", "Terminate from Search", f"Proceso con PID {pid} terminado exitosamente desde la búsqueda.")
    else:
        print_error(f"Error al terminar proceso con PID {pid}: {output}")
        log_action("Process", "Terminate from Search", f"Error al terminar proceso con PID {pid} desde la búsqueda: {output}")

def generate_process_log():
    print_header("Generar Log de Procesos")
    log_action("Process", "Generate Log", "Generando log de gestión de procesos.")
    print_info("Generando informe de Procesos Activos...")
    list_processes()
    print_success(f"Log de procesos generado en {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')}")