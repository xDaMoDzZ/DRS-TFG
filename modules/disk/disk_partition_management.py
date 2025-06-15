from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os

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

def list_disks_partitions():
    print_header("Listar Discos y Particiones")
    os_type = get_os_type()
    if os_type == 'windows':
        print_info("Información de discos y particiones (wmic diskdrive, wmic partition, wmic logicaldisk):")
        command_disk = "wmic diskdrive get Caption,Size,MediaType,Model,SerialNumber /value"
        command_partition = "wmic partition get Name,DiskIndex,Size,StartingOffset /value"
        command_logicaldisk = "wmic logicaldisk get Caption,Size,FreeSpace,FileSystem /value"

        output_disk, status_disk = execute_command(command_disk)
        output_partition, status_partition = execute_command(command_partition)
        output_logicaldisk, status_logicaldisk = execute_command(command_logicaldisk)

        if status_disk == 0:
            print_info("\n--- Discos Físicos ---")
            print(output_disk)
        else:
            print_error(f"Error al listar discos físicos: {output_disk}")

        if status_partition == 0:
            print_info("\n--- Particiones ---")
            print(output_partition)
        else:
            print_error(f"Error al listar particiones: {output_partition}")
        
        if status_logicaldisk == 0:
            print_info("\n--- Unidades Lógicas (Volúmenes) ---")
            print(output_logicaldisk)
        else:
            print_error(f"Error al listar unidades lógicas: {output_logicaldisk}")

        if all(s == 0 for s in [status_disk, status_partition, status_logicaldisk]):
            log_action("DiskPartition", "List Disks/Partitions", "Discos y particiones listados exitosamente (Windows).")
        else:
            log_action("DiskPartition", "List Disks/Partitions", "Error al listar discos y particiones (Windows).")

    else: # linux
        print_info("Información de discos y particiones (lsblk):")
        command = "lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT,UUID,MODEL,STATE"
        output, status = execute_command(command)
        if status == 0:
            print(output)
            log_action("DiskPartition", "List Disks/Partitions", "Discos y particiones listados exitosamente (Linux).")
        else:
            print_error(f"Error al listar discos y particiones: {output}")
            log_action("DiskPartition", "List Disks/Partitions", f"Error al listar discos y particiones: {output}")

def view_mounted_partition_usage():
    print_header("Ver Uso de Particiones Montadas")
    os_type = get_os_type()
    if os_type == 'windows':
        # Ya lo cubrimos en `list_disks_partitions` con `wmic logicaldisk`
        print_info("Ver uso de particiones montadas (información de volúmenes):")
        command = "wmic logicaldisk get Caption,Size,FreeSpace,FileSystem /value"
    else: # linux
        command = "df -hT" # -h: humano, -T: tipo de sistema de archivos
    
    output, status = execute_command(command)
    if status == 0:
        print(output)
        log_action("DiskPartition", "View Mounted Usage", "Uso de particiones montadas listado exitosamente.")
    else:
        print_error(f"Error al ver uso de particiones montadas: {output}")
        log_action("DiskPartition", "View Mounted Usage", f"Error al ver uso de particiones montadas: {output}")


def generate_disk_partition_log():
    print_header("Generar Log de Particiones")
    log_action("DiskPartition", "Generate Log", "Generando log de gestión de particiones.")
    print_info("Generando informe de Discos y Particiones...")
    list_disks_partitions()
    print_info("\nGenerando informe de Uso de Particiones Montadas...")
    view_mounted_partition_usage()
    print_success(f"Log de particiones generado en {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')}")