import os
import sys
from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input, IS_GUI_MODE
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action

#Funciones Auxiliares Internas ---

def _execute_docker_command(command: str, action_type: str, success_msg: str, error_prefix: str):
    """
    Función auxiliar para ejecutar comandos de Docker y manejar la salida.
    Adapta el comportamiento si está en modo GUI o CLI.
    """
    # Docker commands are mostly consistent across OS, but underlying shell might differ
    # We assume 'docker' command is available in PATH
    
    print_info(f"Ejecutando: docker {command}")
    
    output, status = execute_command(f"docker {command}")

    if status == 0:
        if success_msg:
            print_success(success_msg)
        if output.strip():
            # En modo GUI, devolvemos la salida directamente para el Markdown
            # En modo CLI, imprimimos la salida directamente
            if IS_GUI_MODE:
                return output.strip()
            else:
                print(output.strip())
        log_action("Docker", action_type, f"Comando 'docker {command}' ejecutado exitosamente.")
        return output.strip() if IS_GUI_MODE else "" # Retorna vacío en CLI para evitar doble impresión
    else:
        full_error_msg = f"{error_prefix}: {output}"
        print_error(full_error_msg)
        log_action("Docker", action_type, full_error_msg)
        return full_error_msg # Retorna el error para mostrar en la GUI

#Funciones de Gestión de Docker ---

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

def exec_docker_command(container_id_name: str, command_to_exec: str):
    """Ejecuta un comando dentro de un contenedor Docker."""
    print_header(f"Ejecutar Comando en Contenedor Docker: {container_id_name}")
    if not container_id_name or not command_to_exec:
        return print_error("El ID/nombre del contenedor y el comando no pueden estar vacíos.")

    return _execute_docker_command(
        f"exec {container_id_name} {command_to_exec}",
        f"Exec Command in {container_id_name}",
        f"Comando '{command_to_exec}' ejecutado en '{container_id_name}':",
        f"Error al ejecutar comando en contenedor '{container_id_name}'"
    )

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