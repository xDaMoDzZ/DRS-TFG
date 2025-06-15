from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os

def list_users():
    """
    Lista los usuarios del sistema.
    """
    print_header("Listar Usuarios")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "net user"
    else: # linux
        command = "cat /etc/passwd | cut -d: -f1"
    
    output, status = execute_command(command)
    if status == 0: # Comando exitoso
        print_info("Usuarios del sistema:")
        print_info(output) 
        log_action("UserGroup", "List Users", "Usuarios listados exitosamente.")
    else:
        print_error(f"Error al listar usuarios: {output}")
        log_action("UserGroup", "List Users", f"Error al listar usuarios: {output}")

def add_user(username: str, password: str = ""):
    """
    Crea un nuevo usuario con el nombre y la contraseña proporcionados.
    Acepta los parámetros directamente para la GUI.
    """
    print_header("Crear Usuario")
    if not username:
        print_error("El nombre de usuario no puede estar vacío.")
        return

    os_type = get_os_type()
    if os_type == 'windows':
        if password:
            command = f'net user "{username}" "{password}" /add'
        else:
            command = f'net user "{username}" "" /add'
    else: # linux
        command = f"useradd {username}"
        if password:
            command += f" && echo '{username}:{password}' | chpasswd"
    
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Usuario '{username}' creado exitosamente.")
        log_action("UserGroup", "Create User", f"Usuario '{username}' creado.")
    else:
        print_error(f"Error al crear usuario '{username}': {output}")
        log_action("UserGroup", "Create User", f"Error al crear usuario '{username}': {output}")

def remove_user(username: str, confirm: str):
    """
    Elimina un usuario. La confirmación es un string 's' o 'n' de la GUI.
    """
    print_header("Eliminar Usuario")
    if not username:
        print_error("El nombre de usuario no puede estar vacío.")
        return
    
    if confirm.lower() != 's':
        print_info("Operación de eliminación de usuario cancelada.")
        return

    os_type = get_os_type()
    if os_type == 'windows':
        command = f'net user "{username}" /delete'
    else: # linux
        command = f"userdel {username}"
    
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Usuario '{username}' eliminado exitosamente.")
        log_action("UserGroup", "Delete User", f"Usuario '{username}' eliminado.")
    else:
        print_error(f"Error al eliminar usuario '{username}': {output}")
        log_action("UserGroup", "Delete User", f"Error al eliminar usuario '{username}': {output}")

def list_groups():
    """
    Lista los grupos del sistema.
    """
    print_header("Listar Grupos")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "net localgroup"
    else: # linux
        command = "cat /etc/group | cut -d: -f1"
    
    output, status = execute_command(command)
    if status == 0:
        print_info("Grupos del sistema:")
        print_info(output)
        log_action("UserGroup", "List Groups", "Grupos listados exitosamente.")
    else:
        print_error(f"Error al listar grupos: {output}")
        log_action("UserGroup", "List Groups", f"Error al listar grupos: {output}")

def add_group(groupname: str):
    """
    Crea un nuevo grupo con el nombre proporcionado.
    Acepta el parámetro directamente para la GUI.
    """
    print_header("Crear Grupo")
    if not groupname:
        print_error("El nombre del grupo no puede estar vacío.")
        return

    os_type = get_os_type()
    if os_type == 'windows':
        command = f'net localgroup "{groupname}" /add'
    else: # linux
        command = f"groupadd {groupname}"
    
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Grupo '{groupname}' creado exitosamente.")
        log_action("UserGroup", "Create Group", f"Grupo '{groupname}' creado.")
    else:
        print_error(f"Error al crear grupo '{groupname}': {output}")
        log_action("UserGroup", "Create Group", f"Error al crear grupo '{groupname}': {output}")

def remove_group(groupname: str, confirm: str):
    """
    Elimina un grupo. La confirmación es un string 's' o 'n' de la GUI.
    """
    print_header("Eliminar Grupo")
    if not groupname:
        print_error("El nombre del grupo no puede estar vacío.")
        return

    if confirm.lower() != 's':
        print_info("Operación de eliminación de grupo cancelada.")
        return
    
    os_type = get_os_type()
    if os_type == 'windows':
        command = f'net localgroup "{groupname}" /delete'
    else: # linux
        command = f"groupdel {groupname}"
    
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Grupo '{groupname}' eliminado exitosamente.")
        log_action("UserGroup", "Delete Group", f"Grupo '{groupname}' eliminado.")
    else:
        print_error(f"Error al eliminar grupo '{groupname}': {output}")
        log_action("UserGroup", "Delete Group", f"Error al eliminar grupo '{groupname}': {output}")

def add_user_to_group(username: str, groupname: str):
    """
    Añade un usuario a un grupo. Acepta los parámetros directamente para la GUI.
    """
    print_header("Añadir Usuario a Grupo")
    if not username or not groupname:
        print_error("El nombre de usuario y el nombre del grupo no pueden estar vacíos.")
        return

    os_type = get_os_type()
    if os_type == 'windows':
        command = f'net localgroup "{groupname}" "{username}" /add'
    else: # linux
        # usermod -aG añade el usuario al grupo sin eliminarlo de otros grupos primarios.
        command = f"usermod -aG {groupname} {username}"
    
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Usuario '{username}' añadido al grupo '{groupname}' exitosamente.")
        log_action("UserGroup", "Add User to Group", f"Usuario '{username}' añadido a '{groupname}'.")
    else:
        print_error(f"Error al añadir usuario '{username}' al grupo '{groupname}': {output}")
        log_action("UserGroup", "Add User to Group", f"Error al añadir usuario '{username}' a '{groupname}': {output}")

def remove_user_from_group(username: str, groupname: str):
    """
    Remueve un usuario de un grupo. Acepta los parámetros directamente para la GUI.
    """
    print_header("Remover Usuario de Grupo")
    if not username or not groupname:
        print_error("El nombre de usuario y el nombre del grupo no pueden estar vacíos.")
        return

    os_type = get_os_type()
    if os_type == 'windows':
        command = f'net localgroup "{groupname}" "{username}" /delete'
    else: # linux
        # gpasswd es el comando recomendado para remover usuarios de grupos suplementarios.
        command = f"gpasswd -d {username} {groupname}"
    
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Usuario '{username}' removido del grupo '{groupname}' exitosamente.")
        log_action("UserGroup", "Remove User from Group", f"Usuario '{username}' removido de '{groupname}'.")
    else:
        print_error(f"Error al remover usuario '{username}' del grupo '{groupname}': {output}")
        log_action("UserGroup", "Remove User from Group", f"Error al remover usuario '{username}' de '{groupname}': {output}")

def generate_user_group_log():
    """
    Genera un log de usuarios y grupos.
    """
    print_header("Generar Log de Usuarios y Grupos")
    log_action("UserGroup", "Generate Log", "Generando log de usuarios y grupos.")
    print_info("Listado de Usuarios:")
    list_users() # Llama a la función para mostrar y registrar en el log
    print_info("\nListado de Grupos:")
    list_groups() # Llama a la función para mostrar y registrar en el log
    print_success(f"Log de usuarios y grupos generado en {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')}")

def user_group_menu():
    """
    Muestra el menú de administración de usuarios y grupos para la consola
    y llama a las funciones de gestión con los parámetros obtenidos.
    """
    while True:
        clear_screen()
        print_header("Administración de Usuarios y Grupos")
        options = {
            "1": "Listar Usuarios",
            "2": "Crear Usuario",
            "3": "Eliminar Usuario",
            "4": "Listar Grupos",
            "5": "Crear Grupo",
            "6": "Eliminar Grupo",
            "7": "Añadir Usuario a Grupo",
            "8": "Remover Usuario de Grupo",
            "9": "Generar Log de Usuarios y Grupos",
            "0": "Volver al Menú Principal"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            list_users()
        elif choice == '2':
            # Ahora pedimos los parámetros al usuario para add_user
            username = get_user_input("Ingrese el nombre del nuevo usuario")
            password = get_user_input("Ingrese la contraseña para el nuevo usuario (dejar en blanco para no establecer)")
            add_user(username, password)
        elif choice == '3':
            # Ahora pedimos los parámetros y confirmación para remove_user
            username = get_user_input("Ingrese el nombre del usuario a eliminar")
            confirm = get_user_input(f"¿Está seguro de que desea eliminar a '{username}'? (s/N)")
            remove_user(username, confirm)
        elif choice == '4':
            list_groups()
        elif choice == '5':
            # Ahora pedimos el parámetro para add_group
            groupname = get_user_input("Ingrese el nombre del nuevo grupo")
            add_group(groupname)
        elif choice == '6':
            # Ahora pedimos el parámetro y confirmación para remove_group
            groupname = get_user_input("Ingrese el nombre del grupo a eliminar")
            confirm = get_user_input(f"¿Está seguro de que desea eliminar el grupo '{groupname}'? (s/N)")
            remove_group(groupname, confirm)
        elif choice == '7':
            # Ahora pedimos los parámetros para add_user_to_group
            username = get_user_input("Ingrese el nombre del usuario")
            groupname = get_user_input("Ingrese el nombre del grupo")
            add_user_to_group(username, groupname)
        elif choice == '8':
            # Ahora pedimos los parámetros para remove_user_from_group
            username = get_user_input("Ingrese el nombre del usuario")
            groupname = get_user_input("Ingrese el nombre del grupo")
            remove_user_from_group(username, groupname)
        elif choice == '9':
            generate_user_group_log()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        
        # Mantener este para la pausa en el modo consola
        get_user_input("Presione Enter para continuar...")