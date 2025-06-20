from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input, IS_GUI_MODE
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os

#Menu principal de gestion de discos
def disk_partition_menu():
    while True:
        clear_screen()
        print_header("Gestión de Particiones de Disco Duro")
        options = {
            "1": "Listar Discos y Particiones",
            "2": "Ver Uso de Particiones Montadas", # df -h ya lo cubre parcialmente
            "9": "Generar Log de Particiones",
            "0": "Volver al Menú Principal"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            list_disks_partitions()
        elif choice == '2':
            view_mounted_partition_usage()
        elif choice == '9':
            generate_disk_partition_log()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        get_user_input("Presione Enter para continuar...")

#Funciones auxiliares
def _parse_wmic_output(output: str) -> list[dict]:
    """
    Parsea la salida de WMIC /value y la convierte en una lista de diccionarios.
    Cada diccionario representa un objeto (disco, partición, etc.).
    """
    parsed_data = []
    current_item = {}
    for line in output.strip().split('\n'):
        line = line.strip()
        if '=' in line:
            key, value = line.split('=', 1)
            current_item[key] = value
        elif not line and current_item: # Línea vacía indica fin de un objeto
            parsed_data.append(current_item)
            current_item = {}
    if current_item: # Añadir el último item si no terminó con una línea vacía
        parsed_data.append(current_item)
    return parsed_data

def _format_windows_disk_info(data: list[dict]) -> str:
    """Formatea la información de discos físicos de Windows en una tabla."""
    if not data:
        return "No se encontraron discos físicos."

    header = f"{'Model':<40} {'Size (GB)':<15} {'Media Type':<20} {'Serial Number':<25}"
    separator = f"{'-'*40:<40} {'-'*15:<15} {'-'*20:<20} {'-'*25:<25}"
    
    lines = [header, separator]
    for item in data:
        model = item.get('Model', 'N/A')
        size_bytes = int(item.get('Size', 0))
        size_gb = f"{(size_bytes / (1024**3)):.2f}" if size_bytes > 0 else "N/A"
        media_type = item.get('MediaType', 'N/A')
        serial = item.get('SerialNumber', 'N/A')
        
        lines.append(f"{model[:39]:<40} {size_gb:<15} {media_type[:19]:<20} {serial[:24]:<25}")
    return "\n".join(lines)

def _format_windows_partition_info(data: list[dict]) -> str:
    """Formatea la información de particiones de Windows en una tabla."""
    if not data:
        return "No se encontraron particiones."

    header = f"{'Name':<45} {'Disk Index':<12} {'Size (GB)':<15}"
    separator = f"{'-'*45:<45} {'-'*12:<12} {'-'*15:<15}"

    lines = [header, separator]
    for item in data:
        name = item.get('Name', 'N/A').split('\\')[-1] # Solo el nombre de la partición
        disk_index = item.get('DiskIndex', 'N/A')
        size_bytes = int(item.get('Size', 0))
        size_gb = f"{(size_bytes / (1024**3)):.2f}" if size_bytes > 0 else "N/A"
        
        lines.append(f"{name[:44]:<45} {disk_index:<12} {size_gb:<15}")
    return "\n".join(lines)

def _format_windows_logical_disk_info(data: list[dict]) -> str:
    """Formatea la información de unidades lógicas (volúmenes) de Windows en una tabla."""
    if not data:
        return "No se encontraron unidades lógicas."

    header = f"{'Caption':<10} {'File System':<15} {'Total Size (GB)':<20} {'Free Space (GB)':<20}"
    separator = f"{'-'*10:<10} {'-'*15:<15} {'-'*20:<20} {'-'*20:<20}"

    lines = [header, separator]
    for item in data:
        caption = item.get('Caption', 'N/A')
        file_system = item.get('FileSystem', 'N/A')
        size_bytes = int(item.get('Size', 0))
        free_space_bytes = int(item.get('FreeSpace', 0))
        
        total_size_gb = f"{(size_bytes / (1024**3)):.2f}" if size_bytes > 0 else "N/A"
        free_space_gb = f"{(free_space_bytes / (1024**3)):.2f}" if free_space_bytes > 0 else "N/A"
        
        lines.append(f"{caption:<10} {file_system[:14]:<15} {total_size_gb:<20} {free_space_gb:<20}")
    return "\n".join(lines)

def list_disks_partitions():
    """
    Lista discos y particiones del sistema operativo.
    La salida es impresa y capturada por la redirección de sys.stdout.
    """
    print_header("Listar Discos y Particiones") # Esta función ahora solo imprime
    os_type = get_os_type()
    
    if os_type == 'windows':
        print_info("Recopilando información de discos y particiones (Windows)...")
        commands = {
            "disk": "wmic diskdrive get Caption,Size,MediaType,Model,SerialNumber /value",
            "partition": "wmic partition get Name,DiskIndex,Size,StartingOffset /value",
            "logicaldisk": "wmic logicaldisk get Caption,Size,FreeSpace,FileSystem /value"
        }
        
        all_status_ok = True
        
        # Discos Físicos
        output_disk, status_disk = execute_command(commands["disk"])
        if status_disk == 0:
            parsed_data = _parse_wmic_output(output_disk)
            formatted_output = _format_windows_disk_info(parsed_data)
            print_info("\n--- Discos Físicos ---")
            print("```\n" + formatted_output + "\n```") # Usamos print para la salida del comando
        else:
            print_error(f"Error al listar discos físicos: {output_disk}")
            all_status_ok = False

        # Particiones
        output_partition, status_partition = execute_command(commands["partition"])
        if status_partition == 0:
            parsed_data = _parse_wmic_output(output_partition)
            formatted_output = _format_windows_partition_info(parsed_data)
            print_info("\n--- Particiones ---")
            print("```\n" + formatted_output + "\n```")
        else:
            print_error(f"Error al listar particiones: {output_partition}")
            all_status_ok = False
        
        # Unidades Lógicas
        output_logicaldisk, status_logicaldisk = execute_command(commands["logicaldisk"])
        if status_logicaldisk == 0:
            parsed_data = _parse_wmic_output(output_logicaldisk)
            formatted_output = _format_windows_logical_disk_info(parsed_data)
            print_info("\n--- Unidades Lógicas (Volúmenes) ---")
            print("```\n" + formatted_output + "\n```")
        else:
            print_error(f"Error al listar unidades lógicas: {output_logicaldisk}")
            all_status_ok = False

        if all_status_ok:
            log_action("DiskPartition", "List Disks/Partitions", "Discos y particiones listados exitosamente (Windows).")
        else:
            log_action("DiskPartition", "List Disks/Partitions", "Errores encontrados al listar discos y particiones (Windows).")
            
    else: # linux
        print_info("Recopilando información de discos y particiones (Linux - lsblk)...")
        command = "lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT,UUID,MODEL,STATE"
        output, status = execute_command(command)
        if status == 0:
            print_success("Información de Discos y Particiones (Linux):")
            print("```\n" + output + "\n```")
            log_action("DiskPartition", "List Disks/Partitions", "Discos y particiones listados exitosamente (Linux).")
        else:
            print_error(f"Error al listar discos y particiones: {output}")
            log_action("DiskPartition", "List Disks/Partitions", f"Error al listar discos y particiones: {output}")
    # Esta función ya no devuelve nada explícitamente; su salida se captura por redirección.

def view_mounted_partition_usage():
    """
    Muestra el uso de las particiones montadas.
    La salida es impresa y capturada por la redirección de sys.stdout.
    """
    print_header("Ver Uso de Particiones Montadas")
    os_type = get_os_type()
    
    if os_type == 'windows':
        print_info("Ver uso de particiones montadas (información de volúmenes):")
        command = "wmic logicaldisk get Caption,Size,FreeSpace,FileSystem /value"
        output, status = execute_command(command)
        if status == 0:
            parsed_data = _parse_wmic_output(output)
            formatted_output = _format_windows_logical_disk_info(parsed_data)
            print("```\n" + formatted_output + "\n```")
            log_action("DiskPartition", "View Mounted Usage", "Uso de particiones montadas listado exitosamente (Windows).")
        else:
            print_error(f"Error al ver uso de particiones montadas: {output}")
            log_action("DiskPartition", "View Mounted Usage", f"Error al ver uso de particiones montadas: {output}")
    else: # linux
        command = "df -hT" # -h: humano, -T: tipo de sistema de archivos
        output, status = execute_command(command)
        if status == 0:
            print("```\n" + output + "\n```")
            log_action("DiskPartition", "View Mounted Usage", "Uso de particiones montadas listado exitosamente (Linux).")
        else:
            print_error(f"Error al ver uso de particiones montadas: {output}")
            log_action("DiskPartition", "View Mounted Usage", f"Error al ver uso de particiones montadas: {output}")

def generate_disk_partition_log():
    """
    Genera un log consolidado de la gestión de particiones de disco.
    La salida es impresa y capturada por la redirección de sys.stdout.
    """
    print_header("Generar Log de Particiones")
    log_action("DiskPartition", "Generate Log", "Generando log de gestión de particiones.")
    
    print_info("\n--- Informe de Discos y Particiones ---")
    list_disks_partitions() # Llama a la función existente, que ahora solo imprime

    print_info("\n--- Informe de Uso de Particiones Montadas ---")
    view_mounted_partition_usage() # Llama a la función existente, que ahora solo imprime
    
    print_success("Log de particiones generado. Consulta los logs del sistema para ver los detalles completos.")
