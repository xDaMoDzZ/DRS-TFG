import os
import sys
from utils.display import clear_screen, print_menu, print_warning, print_header, print_info, print_success, print_error, get_user_input, IS_GUI_MODE
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action

#Funciones Auxiliares Internas

#Comprobar que docker este corriendo
def _check_docker_daemon_status():
    """
    Verifica si el demonio de Docker está corriendo.
    Retorna True si está corriendo, False en caso contrario.
    """
    os_type = get_os_type()
    command = ""
    
    if os_type == 'linux':
        command = "systemctl is-active docker"
    elif os_type == 'windows':
        # Comprobamos si el proceso 'Docker Desktop.exe' está en ejecución.
        command = "tasklist /FI \"IMAGENAME eq Docker Desktop.exe\""
    else:
        print_warning("No se puede verificar el estado del demonio de Docker en este sistema operativo.")
        return True # Asumimos que está bien si no podemos verificar (caso inesperado de SO)

    output, status = execute_command(command)

    if os_type == 'linux':
        if status == 0 and "active" in output.lower():
            return True
        else:
            print_error("El demonio de Docker NO está activo. Por favor, inícielo (`sudo systemctl start docker`).")
            log_action("Docker", "Check Daemon Status", "Demón de Docker no activo (Linux).")
            return False
    elif os_type == 'windows':
        if status == 0 and "Docker Desktop.exe" in output:
            return True
        else:
            print_error("El proceso 'Docker Desktop.exe' NO está corriendo. Por favor, inicie Docker Desktop.")
            log_action("Docker", "Check Daemon Status", "Proceso Docker Desktop.exe no encontrado (Windows).")
            return False
    
    return True # Fallback en caso de que ninguna condición se cumpla

#Ejecutar comando de docker
def _execute_docker_command(command: str, action_type: str, success_msg: str, error_prefix: str, cwd: str = None):
    """
    Función auxiliar para ejecutar comandos de Docker y manejar la salida.
    Adapta el comportamiento si está en modo GUI o CLI.
    Añade un parámetro 'cwd' para especificar el directorio de trabajo.
    """
    # 1. Verificar el estado del demonio de Docker antes de ejecutar cualquier comando
    if not _check_docker_daemon_status():
        err_msg = "El demonio de Docker no está activo. No se puede ejecutar el comando."
        print_error(err_msg)
        log_action("Docker", action_type, f"Fallo (Demón no activo): {err_msg}")
        return err_msg if IS_GUI_MODE else None # Retorna el mensaje de error para la GUI

    print_info(f"Ejecutando: docker {command}")
    
    # 2. Ejecutar el comando Docker con el cwd especificado
    output, status = execute_command(f"docker {command}")

    if status == 0:
        if success_msg:
            print_success(success_msg)
        
        # 3. Manejo de la salida: imprimir en CLI, retornar en GUI
        if output.strip():
            if IS_GUI_MODE:
                result = output.strip()
            else:
                print(output.strip())
                result = "" # No retorna nada si ya lo imprimió
        else:
            result = "" # No hay salida, retorna vacío

        log_action("Docker", action_type, f"Comando 'docker {command}' ejecutado exitosamente.")
        return result
    else:
        # 4. Manejo de errores: imprimir y loguear el error completo
        full_error_msg = f"{error_prefix}: {output}"
        print_error(full_error_msg)
        log_action("Docker", action_type, full_error_msg)
        return full_error_msg # Retorna el error para mostrar en la GUI

#Funciones de Gestion de Docker
#Listamos todos los contenedores de docker
def list_docker_containers():
    """Lista todos los contenedores Docker (activos e inactivos)."""
    print_header("Listar Contenedores Docker")
    # Formato de tabla para una salida legible
    command = 'ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"'
    return _execute_docker_command(
        command,
        "List Containers",
        "Contenedores Docker:",
        "Error al listar contenedores"
    )

#Arrancamos contenedor docker por nombre
def start_docker_container(container_id_name: str):
    """Inicia un contenedor Docker."""
    print_header(f"Iniciar Contenedor Docker: {container_id_name}")
    if not container_id_name:
        return print_error("El ID o nombre del contenedor no puede estar vacío.")

    return _execute_docker_command(
        f"start {container_id_name}",
        f"Start Container {container_id_name}",
        f"Contenedor '{container_id_name}' iniciado exitosamente.",
        f"Error al iniciar contenedor '{container_id_name}'"
    )

#Paramos contenedor docker por nombre
def stop_docker_container(container_id_name: str):
    """Detiene un contenedor Docker."""
    print_header(f"Detener Contenedor Docker: {container_id_name}")
    if not container_id_name:
        return print_error("El ID o nombre del contenedor no puede estar vacío.")

    return _execute_docker_command(
        f"stop {container_id_name}",
        f"Stop Container {container_id_name}",
        f"Contenedor '{container_id_name}' detenido exitosamente.",
        f"Error al detener contenedor '{container_id_name}'"
    )

#Reiniciamos un contenedor docker por nombre
def restart_docker_container(container_id_name: str):
    """Reinicia un contenedor Docker."""
    print_header(f"Reiniciar Contenedor Docker: {container_id_name}")
    if not container_id_name:
        return print_error("El ID o nombre del contenedor no puede estar vacío.")

    return _execute_docker_command(
        f"restart {container_id_name}",
        f"Restart Container {container_id_name}",
        f"Contenedor '{container_id_name}' reiniciado exitosamente.",
        f"Error al reiniciar contenedor '{container_id_name}'"
    )

#Eliminamos contenedor docker por nombre
def remove_docker_container(container_id_name: str, confirm: str = 'n'):
    """Elimina un contenedor Docker."""
    print_header(f"Eliminar Contenedor Docker: {container_id_name}")
    if not container_id_name:
        return print_error("El ID o nombre del contenedor no puede estar vacío.")

    if not IS_GUI_MODE:
        user_confirm = get_user_input(
            f"¿Está seguro de que desea eliminar el contenedor '{container_id_name}'? Esta acción es irreversible (s/N)"
        ).lower()
        if user_confirm != 's':
            print_info("Operación de eliminación cancelada.")
            log_action("Docker", f"Remove Container {container_id_name}", "Eliminación cancelada por el usuario.")
            return "Operación de eliminación cancelada." if IS_GUI_MODE else None
    elif confirm.lower() != 's':
        print_info("Operación de eliminación cancelada por el usuario.")
        return "Operación de eliminación cancelada por el usuario."

    return _execute_docker_command(
        f"rm {container_id_name}",
        f"Remove Container {container_id_name}",
        f"Contenedor '{container_id_name}' eliminado exitosamente.",
        f"Error al eliminar contenedor '{container_id_name}'"
    )

#Miramos los logs del contenedor docker
def view_docker_logs(container_id_name: str, num_lines: str = ''):
    """
    Muestra los logs de un contenedor Docker.
    num_lines puede ser un string vacío o un número.
    """
    print_header(f"Ver Logs de Contenedor Docker: {container_id_name}")
    if not container_id_name:
        return print_error("El ID o nombre del contenedor no puede estar vacío.")

    command = f"logs {container_id_name}"
    if num_lines and num_lines.isdigit():
        command += f" -n {num_lines}"
    
    return _execute_docker_command(
        command,
        f"View Logs {container_id_name}",
        f"Logs del contenedor '{container_id_name}':",
        f"Error al ver logs del contenedor '{container_id_name}'"
    )

#Función para limpiar todas las imagenes docker instaladas
def clean_docker_images(confirm: str = 'n'):
    """Elimina todas las imágenes Docker no utilizadas."""
    print_header("Limpiar Imágenes Docker No Utilizadas")

    if not IS_GUI_MODE:
        user_confirm = get_user_input(
            "¿Está seguro de que desea eliminar TODAS las imágenes no utilizadas? Esta acción puede liberar mucho espacio (s/N)"
        ).lower()
        if user_confirm != 's':
            print_info("Operación de limpieza de imágenes cancelada.")
            log_action("Docker", "Clean Images", "Limpieza de imágenes cancelada por el usuario.")
            return "Operación de limpieza de imágenes cancelada." if IS_GUI_MODE else None
    elif confirm.lower() != 's':
        print_info("Operación de limpieza de imágenes cancelada por el usuario.")
        return "Operación de limpieza de imágenes cancelada por el usuario."

    # -a para all (incluye imágenes colgadas)
    return _execute_docker_command(
        "image prune -a -f", # -f para forzar y no pedir confirmación en CLI
        "Clean Images",
        "Imágenes Docker no utilizadas limpiadas exitosamente.",
        "Error al limpiar imágenes Docker"
    )

#FUNCIONES DE DOCKER COMPOSE
#Desplegar docker compose por archivo
def deploy_docker_compose(compose_file_path: str):
    """
    Levanta los servicios definidos en un archivo docker-compose.yml.
    Usa 'docker compose up -d'.
    """
    print_header(f"Levantar Docker Compose: {compose_file_path}")
    if not compose_file_path:
        return print_error("La ruta al archivo docker-compose.yml no puede estar vacía.")

    if not os.path.exists(compose_file_path):
        return print_error(f"El archivo '{compose_file_path}' no existe.")

    # Aseguramos que la ruta es un archivo, no un directorio
    if os.path.isdir(compose_file_path):
        return print_error(f"'{compose_file_path}' es un directorio, no un archivo docker-compose.yml.")

    # Comando 'docker compose' (compatible con versiones más nuevas de Docker)
    # Se usa -f para especificar el archivo y -d para detached mode
    command = f"compose -f \"{compose_file_path}\" up -d"
    
    return _execute_docker_command(
        command,
        f"Deploy Docker Compose {compose_file_path}",
        f"Servicios de Docker Compose '{compose_file_path}' levantados exitosamente.",
        f"Error al levantar Docker Compose '{compose_file_path}'"
    )

#Detener docker comopose
def stop_docker_compose(compose_file_path: str):
    """
    Detiene y elimina los servicios definidos en un archivo docker-compose.yml.
    Usa 'docker compose down'.
    """
    print_header(f"Detener Docker Compose: {compose_file_path}")
    if not compose_file_path:
        return print_error("La ruta al archivo docker-compose.yml no puede estar vacía.")

    if not os.path.exists(compose_file_path):
        return print_error(f"El archivo '{compose_file_path}' no existe.")
    
    if os.path.isdir(compose_file_path):
        return print_error(f"'{compose_file_path}' es un directorio, no un archivo docker-compose.yml.")

    command = f"compose -f \"{compose_file_path}\" down"

    return _execute_docker_command(
        command,
        f"Stop Docker Compose {compose_file_path}",
        f"Servicios de Docker Compose '{compose_file_path}' detenidos exitosamente.",
        f"Error al detener Docker Compose '{compose_file_path}'"
    )

#Menu de docker principal
def docker_menu():
    """Muestra el menú de opciones para la gestión de Docker."""
    while True:
        clear_screen()
        print_header("Gestión de Docker")
        options = {
            "1": "Listar Contenedores",
            "2": "Iniciar Contenedor",
            "3": "Detener Contenedor",
            "4": "Reiniciar Contenedor",
            "5": "Eliminar Contenedor",
            "6": "Ver Logs de Contenedor",
            "7": "Ejecutar Comando en Contenedor",
            "8": "Limpiar Imágenes No Utilizadas",            
            "9": "Levantar Docker Compose (up -d)", # Nueva opción
            "10": "Detener Docker Compose (down)",
            "0": "Volver al Menú Principal"
        }
        from utils.display import print_menu # Importación local para evitar circular si display usa docker_management
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            list_docker_containers()
        elif choice == '2':
            container_id_name = get_user_input("Ingrese el ID o nombre del contenedor a iniciar")
            start_docker_container(container_id_name)
        elif choice == '3':
            container_id_name = get_user_input("Ingrese el ID o nombre del contenedor a detener")
            stop_docker_container(container_id_name)
        elif choice == '4':
            container_id_name = get_user_input("Ingrese el ID o nombre del contenedor a reiniciar")
            restart_docker_container(container_id_name)
        elif choice == '5':
            container_id_name = get_user_input("Ingrese el ID o nombre del contenedor a eliminar")
            remove_docker_container(container_id_name) # La confirmación se maneja dentro de la función
        elif choice == '6':
            container_id_name = get_user_input("Ingrese el ID o nombre del contenedor para ver sus logs")
            num_lines = get_user_input("Ingrese el número de líneas (dejar vacío para todas)")
            view_docker_logs(container_id_name, num_lines)
        elif choice == '7':
            container_id_name = get_user_input("Ingrese el ID o nombre del contenedor")
            command_to_exec = get_user_input(f"Ingrese el comando a ejecutar en '{container_id_name}' (ej: ls -l /app)")
            exec_docker_command(container_id_name, command_to_exec)
        elif choice == '8':
            clean_docker_images() # La confirmación se maneja dentro de la función
        elif choice == '9': # Nueva opción para docker-compose up
            compose_path = "modules\docker\docker-compose.yml"
            deploy_docker_compose(compose_path)
        elif choice == '10': # Nueva opción para docker-compose down            
            compose_path = "modules\docker\docker-compose.yml"
            stop_docker_compose(compose_path)
        elif choice == '0':
            print_info("Volviendo al Menú Principal...")
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        
        get_user_input("Presione Enter para continuar...")