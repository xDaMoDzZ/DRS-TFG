from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os

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
    print_header("Buscar Información de Proceso por Nombre")
    search_name = get_user_input("Ingrese el nombre (o parte del nombre) del proceso a buscar")
    
    os_type = get_os_type()
    found_processes = []

    if os_type == 'windows':
        powershell_command = f'Get-Process -Name "*{search_name}*" | Select-Object Name,Id,WorkingSet | ConvertTo-Csv -NoTypeInformation'
        command = f'powershell.exe -Command "{powershell_command}"'
        
        print_info(f"Buscando procesos en Windows con: {command}")
        output, status = execute_command(command)
        
        if status == 0 and output.strip():
            lines = output.strip().split('\n')
            
            # Verificar si hay al menos una línea de encabezado y una de datos
            if len(lines) > 1: 
                # La primera línea son los encabezados, la podemos usar para referenciarlos
                headers = [h.strip('"') for h in lines[0].split(',')]
                
                # Iterar desde la segunda línea en adelante (saltando el encabezado)
                for line in lines[1:]: 
                    parts = [p.strip('"') for p in line.split(',')]
                    
                    # Asegurarse de que la línea tiene el número correcto de partes
                    if len(parts) == len(headers): 
                        try:
                            process_data = dict(zip(headers, parts))
                            
                            process_name = process_data.get('Name', 'N/A')
                            pid = process_data.get('Id', 'N/A')
                            mem_bytes = process_data.get('WorkingSet', '0')

                            try:
                                mem_mb = float(mem_bytes) / (1024 * 1024)
                                mem_display = f"{mem_mb:.2f} MB"
                            except ValueError:
                                mem_display = f"{mem_bytes} B"
                            
                            if search_name.lower() in process_name.lower():
                                found_processes.append({
                                    "name": process_name, 
                                    "pid": pid, 
                                    "mem_usage": mem_display
                                })
                        except Exception as e:
                            # Imprime el error pero no lo loggea como un error fatal del comando,
                            # sino como un problema de parseo específico.
                            print_error(f"Error al parsear línea de PowerShell: {line} - {e}")
                            continue
        
        if not found_processes: # Si no se encontraron procesos o hubo error de comando
             if status != 0:
                 print_error(f"Error al ejecutar el comando de búsqueda: {output}")
             else:
                 print_info(f"No se encontraron procesos que contengan '{search_name}'.")
             log_action("Process", "Find Process", f"No se encontró el proceso '{search_name}'.")
             return

    else: # linux (esta sección se mantiene igual)
        command = f"pgrep -l -f '{search_name}'"
        print_info(f"Buscando procesos en Linux con: {command}")
        output, status = execute_command(command)

        if status == 0 and output.strip():
            for line in output.strip().split('\n'):
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    pid, name = parts
                    detail_cmd = f"ps -p {pid} -o user,pid,%cpu,%mem,vsz,rss,tty,stat,start,time,comm --no-headers"
                    detail_output, detail_status = execute_command(detail_cmd)
                    if detail_status == 0 and detail_output.strip():
                        found_processes.append({"name": name, "pid": pid, "details": detail_output.strip()})
                    else:
                        found_processes.append({"name": name, "pid": pid, "details": "Detalles no disponibles."})
        
        if not found_processes:
            if status != 0:
                print_error(f"Error al ejecutar el comando de búsqueda: {output}")
            else:
                print_info(f"No se encontraron procesos que contengan '{search_name}'.")
            log_action("Process", "Find Process", f"No se encontró el proceso '{search_name}'.")
            return
            
    # Mostrar los procesos encontrados
    print_success(f"Se encontraron los siguientes procesos para '{search_name}':")
    if os_type == 'windows':
        print(f"{'No.':<5} {'Image Name':<30} {'PID':<10} {'Mem Usage':<15}")
        print(f"{'-'*5:<5} {'-'*30:<30} {'-'*10:<10} {'-'*15:<15}")
        for i, proc in enumerate(found_processes):
            print(f"{i+1:<5} {proc['name']:<30} {proc['pid']:<10} {proc['mem_usage']:<15}")
    else: # Linux
        print(f"{'No.':<5} {'PID':<10} {'Process Name/Command':<40}")
        print(f"{'-'*5:<5} {'-'*10:<10} {'-'*40:<40}")
        for i, proc in enumerate(found_processes):
            print(f"{i+1:<5} {proc['pid']:<10} {proc['name']:<40}")

    log_action("Process", "Find Process", f"Se encontraron {len(found_processes)} procesos para '{search_name}'.")

    if found_processes:
        action_choice = get_user_input("¿Desea terminar alguno de estos procesos? (s/N)").lower()
        if action_choice == 's':
            while True:
                try:
                    process_index = int(get_user_input("Ingrese el número del proceso a terminar (0 para cancelar)"))
                    if process_index == 0:
                        print_info("Operación de terminación cancelada.")
                        log_action("Process", "Terminate from Search", "Terminación de proceso desde búsqueda cancelada.")
                        break
                    
                    if 1 <= process_index <= len(found_processes):
                        selected_process = found_processes[process_index - 1]
                        print_info(f"Ha seleccionado el proceso: '{selected_process['name']}' (PID: {selected_process['pid']}).")
                        
                        confirm_kill = get_user_input(f"¿Confirma la terminación de este proceso? (s/N)").lower()
                        if confirm_kill == 's':
                            terminate_process_by_pid_internal(selected_process['pid'])
                        else:
                            print_info("Terminación de proceso cancelada.")
                            log_action("Process", "Terminate from Search", "Terminación de proceso desde búsqueda cancelada por usuario.")
                        break
                    else:
                        print_error("Número de proceso inválido. Intente de nuevo.")
                except ValueError:
                    print_error("Entrada inválida. Por favor, ingrese un número.")
        else:
            print_info("No se seleccionó ningún proceso para terminar.")
            log_action("Process", "Find Process", "No se seleccionó terminación de proceso desde búsqueda.")

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