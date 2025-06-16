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

#Ejecutar comando en contenedor
def execute_command_in_container(container_name: str, command: str) -> tuple[str, int]:
    """
    Ejecuta un comando dentro de un contenedor Docker específico.

    Args:
        container_name (str): El nombre o ID del contenedor donde se ejecutará el comando.
        command (str): El comando a ejecutar dentro del contenedor.

    Returns:
        tuple[str, int]: Una tupla que contiene la salida del comando (stdout/stderr)
                         y el código de estado de salida.
    """
    print_header(f"Ejecutar Comando en Contenedor '{container_name}'")

    if not container_name:
        print_error("El nombre del contenedor no puede estar vacío.")
        log_action("Docker", "Execute Command in Container", "Error: Nombre de contenedor vacío.")
        return "Error: El nombre del contenedor no puede estar vacío.", 1

    if not command:
        print_error("El comando a ejecutar no puede estar vacío.")
        log_action("Docker", "Execute Command in Container", "Error: Comando vacío.")
        return "Error: El comando a ejecutar no puede estar vacío.", 1
    
    # Construir el comando docker exec
    # Usamos sh -c para que el comando se interprete correctamente,
    # lo que es útil para comandos con pipes, redirecciones, etc.
    docker_command = f'docker exec {container_name} sh -c "{command}"'
    
    print_info(f"Ejecutando '{command}' en el contenedor '{container_name}'...")
    output, status = execute_command(docker_command, sudo=True) # docker commands usually require sudo

    if status == 0:
        print_success(f"Comando ejecutado exitosamente en '{container_name}'.")
        print_info("Salida del comando:")
        print_info(output) # Imprime la salida del comando dentro del contenedor
        log_action("Docker", "Execute Command in Container", 
                   f"Comando '{command}' ejecutado en '{container_name}'. Salida: {output.strip()[:100]}...")
    else:
        print_error(f"Error al ejecutar comando en '{container_name}': {output}")
        log_action("Docker", "Execute Command in Container", 
                   f"Error al ejecutar comando '{command}' en '{container_name}': {output.strip()[:100]}...")
    
    return output, status

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
STATIC_DOCKER_COMPOSE_PATH = "./modules/docker/docker-compose.yml"

# Verificar la ruta del archivo (opcional)
if not os.path.exists(STATIC_DOCKER_COMPOSE_PATH):
    print_warning(f"Advertencia: El archivo Docker Compose no se encontró en la ruta estática: {STATIC_DOCKER_COMPOSE_PATH}")
    print_warning("Por favor, asegúrese de que la ruta sea correcta o cree el archivo.")

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
def docker_compose_up():
    """
    Inicia los servicios definidos en el archivo Docker Compose de la ruta estática.
    """
    print_header("Docker Compose: Iniciar Servicios")
    
    if not os.path.exists(STATIC_DOCKER_COMPOSE_PATH):
        print_error(f"Error: Archivo Docker Compose no encontrado en '{STATIC_DOCKER_COMPOSE_PATH}'.")
        log_action("Docker Compose", "Up", f"Error: Archivo no encontrado en '{STATIC_DOCKER_COMPOSE_PATH}'.")
        return

    # Usamos -d para ejecutar en modo 'detached' (segundo plano)
    command = f"docker-compose -f \"{STATIC_DOCKER_COMPOSE_PATH}\" up -d"
    
    print_info(f"Iniciando servicios Docker Compose desde '{STATIC_DOCKER_COMPOSE_PATH}'...")
    output, status = execute_command(command, sudo=True)

    if status == 0:
        print_success(f"Servicios Docker Compose iniciados exitosamente desde '{STATIC_DOCKER_COMPOSE_PATH}'.")
        print_info(output)
        log_action("Docker Compose", "Up", f"Servicios iniciados desde '{STATIC_DOCKER_COMPOSE_PATH}'.")
    else:
        print_error(f"Error al iniciar servicios Docker Compose: {output}")
        log_action("Docker Compose", "Up", f"Error al iniciar servicios desde '{STATIC_DOCKER_COMPOSE_PATH}': {output}")

def docker_compose_down():
    """
    Detiene y remueve los servicios definidos en el archivo Docker Compose de la ruta estática.
    """
    print_header("Docker Compose: Detener Servicios")

    if not os.path.exists(STATIC_DOCKER_COMPOSE_PATH):
        print_error(f"Error: Archivo Docker Compose no encontrado en '{STATIC_DOCKER_COMPOSE_PATH}'.")
        log_action("Docker Compose", "Down", f"Error: Archivo no encontrado en '{STATIC_DOCKER_COMPOSE_PATH}'.")
        return

    # Usamos --volumes para remover también volúmenes anónimos
    command = f"docker-compose -f \"{STATIC_DOCKER_COMPOSE_PATH}\" down --volumes"
    
    print_info(f"Deteniendo servicios Docker Compose desde '{STATIC_DOCKER_COMPOSE_PATH}'...")
    output, status = execute_command(command, sudo=True)

    if status == 0:
        print_success(f"Servicios Docker Compose detenidos y removidos exitosamente desde '{STATIC_DOCKER_COMPOSE_PATH}'.")
        print_info(output)
        log_action("Docker Compose", "Down", f"Servicios detenidos desde '{STATIC_DOCKER_COMPOSE_PATH}'.")
    else:
        print_error(f"Error al detener servicios Docker Compose: {output}")
        log_action("Docker Compose", "Down", f"Error al detener servicios desde '{STATIC_DOCKER_COMPOSE_PATH}': {output}")

def docker_compose_build():
    """
    Reconstruye las imágenes de los servicios definidos en el archivo Docker Compose de la ruta estática.
    """
    print_header("Docker Compose: Reconstruir Imágenes")

    if not os.path.exists(STATIC_DOCKER_COMPOSE_PATH):
        print_error(f"Error: Archivo Docker Compose no encontrado en '{STATIC_DOCKER_COMPOSE_PATH}'.")
        log_action("Docker Compose", "Build", f"Error: Archivo no encontrado en '{STATIC_DOCKER_COMPOSE_PATH}'.")
        return

    command = f"docker-compose -f \"{STATIC_DOCKER_COMPOSE_PATH}\" build"
    
    print_info(f"Reconstruyendo imágenes Docker Compose desde '{STATIC_DOCKER_COMPOSE_PATH}'...")
    output, status = execute_command(command, sudo=True)

    if status == 0:
        print_success(f"Imágenes Docker Compose reconstruidas exitosamente desde '{STATIC_DOCKER_COMPOSE_PATH}'.")
        print_info(output)
        log_action("Docker Compose", "Build", f"Imágenes reconstruidas desde '{STATIC_DOCKER_COMPOSE_PATH}'.")
    else:
        print_error(f"Error al reconstruir imágenes Docker Compose: {output}")
        log_action("Docker Compose", "Build", f"Error al reconstruir imágenes desde '{STATIC_DOCKER_COMPOSE_PATH}': {output}")

#Menu de docker principal
def docker_menu():
    """
    Muestra el menú de administración de Docker en la consola.
    """
    while True:
        clear_screen()
        print_header("Administración de Docker")
        options = {
            "1": "Listar Contenedores Docker",
            "2": "Iniciar Contenedor Docker",
            "3": "Detener Contenedor Docker",
            "4": "Remover Contenedor Docker",
            "5": "Ejecutar Comando en Contenedor",
            "6": "Docker Compose: Iniciar Servicios (Up)", # Nueva opción
            "7": "Docker Compose: Detener Servicios (Down)", # Nueva opción
            "8": "Docker Compose: Reconstruir Imágenes (Build)", # Nueva opción
            "0": "Volver al Menú Principal"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            list_docker_containers()
        elif choice == '2':
            container_name = get_user_input("Ingrese el nombre o ID del contenedor a iniciar")
            start_docker_container(container_name)
        elif choice == '3':
            container_name = get_user_input("Ingrese el nombre o ID del contenedor a detener")
            stop_docker_container(container_name)
        elif choice == '4':
            container_name = get_user_input("Ingrese el nombre o ID del contenedor a remover")
            confirm = get_user_input(f"¿Está seguro de que desea remover '{container_name}'? (s/N)")
            remove_docker_container(container_name, confirm)
        elif choice == '5':
            container_name = get_user_input("Ingrese el nombre o ID del contenedor")
            command_to_execute = get_user_input("Ingrese el comando a ejecutar dentro del contenedor")
            execute_command_in_container(container_name, command_to_execute)
        elif choice == '6':
            docker_compose_up()
        elif choice == '7':
            docker_compose_down()
        elif choice == '8':
            docker_compose_build()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        
        get_user_input("Presione Enter para continuar...")