from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os

def user_group_menu():
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
            create_user()
        elif choice == '3':
            delete_user()
        elif choice == '4':
            list_groups()
        elif choice == '5':
            create_group()
        elif choice == '6':
            delete_group()
        elif choice == '7':
            add_user_to_group()
        elif choice == '8':
            remove_user_from_group()
        elif choice == '9':
            generate_user_group_log()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        get_user_input("Presione Enter para continuar...")

def list_users():
    print_header("Listar Usuarios")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "net user"
    else: # linux
        command = "cat /etc/passwd | cut -d: -f1" # Muestra solo los nombres de usuario
    
    output, status = execute_command(command)
    if status == 0: # Comando exitoso
        print_info("Usuarios del sistema:")
        print(output)
        log_action("UserGroup", "List Users", "Usuarios listados exitosamente.")
    else:
        print_error(f"Error al listar usuarios: {output}")
        log_action("UserGroup", "List Users", f"Error al listar usuarios: {output}")

def create_user():
    print_header("Crear Usuario")
    username = get_user_input("Ingrese el nombre del nuevo usuario")
    password = get_user_input("Ingrese la contraseña para el nuevo usuario (dejar en blanco para no establecer)")
    
    os_type = get_os_type()
    if os_type == 'windows':
        command = f'net user "{username}" "{password}" /add' if password else f'net user "{username}" * /add'
        # Puedes añadir /passwordchg:no /passwordreq:yes si lo necesitas en Windows
    else: # linux
        command = f"useradd {username}"
        if password:
            command += f" && echo '{username}:{password}' | chpasswd" # chpasswd requiere sudo
    
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Usuario '{username}' creado exitosamente.")
        log_action("UserGroup", "Create User", f"Usuario '{username}' creado.")
    else:
        print_error(f"Error al crear usuario: {output}")
        log_action("UserGroup", "Create User", f"Error al crear usuario '{username}': {output}")

def delete_user():
    print_header("Eliminar Usuario")
    username = get_user_input("Ingrese el nombre del usuario a eliminar")
    
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
        print_error(f"Error al eliminar usuario: {output}")
        log_action("UserGroup", "Delete User", f"Error al eliminar usuario '{username}': {output}")

def list_groups():
    print_header("Listar Grupos")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "net localgroup"
    else: # linux
        command = "cat /etc/group | cut -d: -f1"
    
    output, status = execute_command(command)
    if status == 0:
        print_info("Grupos del sistema:")
        print(output)
        log_action("UserGroup", "List Groups", "Grupos listados exitosamente.")
    else:
        print_error(f"Error al listar grupos: {output}")
        log_action("UserGroup", "List Groups", f"Error al listar grupos: {output}")

def create_group():
    print_header("Crear Grupo")
    groupname = get_user_input("Ingrese el nombre del nuevo grupo")
    
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
        print_error(f"Error al crear grupo: {output}")
        log_action("UserGroup", "Create Group", f"Error al crear grupo '{groupname}': {output}")

def delete_group():
    print_header("Eliminar Grupo")
    groupname = get_user_input("Ingrese el nombre del grupo a eliminar")
    
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
        print_error(f"Error al eliminar grupo: {output}")
        log_action("UserGroup", "Delete Group", f"Error al eliminar grupo '{groupname}': {output}")

def add_user_to_group():
    print_header("Añadir Usuario a Grupo")
    username = get_user_input("Ingrese el nombre del usuario")
    groupname = get_user_input("Ingrese el nombre del grupo")
    
    os_type = get_os_type()
    if os_type == 'windows':
        command = f'net localgroup "{groupname}" "{username}" /add'
    else: # linux
        command = f"usermod -aG {groupname} {username}"
    
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Usuario '{username}' añadido al grupo '{groupname}' exitosamente.")
        log_action("UserGroup", "Add User to Group", f"Usuario '{username}' añadido a '{groupname}'.")
    else:
        print_error(f"Error al añadir usuario a grupo: {output}")
        log_action("UserGroup", "Add User to Group", f"Error al añadir usuario '{username}' a '{groupname}': {output}")

def remove_user_from_group():
    print_header("Remover Usuario de Grupo")
    username = get_user_input("Ingrese el nombre del usuario")
    groupname = get_user_input("Ingrese el nombre del grupo")
    
    os_type = get_os_type()
    if os_type == 'windows':
        command = f'net localgroup "{groupname}" "{username}" /delete'
    else: # linux
        # gpasswd es más seguro que userdel para remover de un grupo
        command = f"gpasswd -d {username} {groupname}"
    
    output, status = execute_command(command, sudo=True)
    if status == 0:
        print_success(f"Usuario '{username}' removido del grupo '{groupname}' exitosamente.")
        log_action("UserGroup", "Remove User from Group", f"Usuario '{username}' removido de '{groupname}'.")
    else:
        print_error(f"Error al remover usuario de grupo: {output}")
        log_action("UserGroup", "Remove User from Group", f"Error al remover usuario '{username}' de '{groupname}': {output}")

def generate_user_group_log():
    print_header("Generar Log de Usuarios y Grupos")
    log_action("UserGroup", "Generate Log", "Generando log de usuarios y grupos.")
    print_info("Listado de Usuarios:")
    list_users() # Llama a la función para mostrar y registrar en el log
    print_info("\nListado de Grupos:")
    list_groups() # Llama a la función para mostrar y registrar en el log
    print_success(f"Log de usuarios y grupos generado en {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')}")