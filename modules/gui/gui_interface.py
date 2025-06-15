import gradio as gr
import io
import sys
import os # Necesario para deploy/stop docker compose con cwd

# Importar todos los módulos de gestión
from modules.process import process_management
from modules.docker import docker_management
from modules.services import service_management
from modules.package import package_management
from modules.user import user_group_management
from modules.network import network_management
from modules.resource import resource_monitoring
from modules.disk import disk_partition_management
from modules.firewall import firewall_management

# Importar las utilidades modificadas
import utils.display as display_utils
import utils.system_info as system_info_utils
import utils.logger as logger_utils


# --- Funciones auxiliares para Gradio ---

# Función genérica para ejecutar cualquier función de módulo en modo GUI
def _run_module_function(func, *input_args):
    """
    Ejecuta una función de módulo en modo GUI, gestionando la entrada y la salida.
    input_args son los valores que se pondrán en la cola de input si la función los pide (e.g., para confirmaciones).
    """
    # Si la función necesita input (ej. confirmación s/N), lo pasamos a la cola de display_utils
    if input_args:
        display_utils.set_gui_input_queue(list(input_args)) # Convertir a lista para que sea mutable y pop funcione
    
    display_utils.clear_screen() # Limpia el buffer de salida antes de cada ejecución

    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    try:
        # Llamar a la función principal del módulo
        # Si la función del módulo retorna un valor, lo capturamos
        result = func(*input_args) # Pasar los argumentos directamente a la función si ella los espera

        cli_direct_prints = redirected_output.getvalue()

    finally:
        sys.stdout = old_stdout # Restaurar stdout

    # Obtener y limpiar el buffer de Gradio después de que la función haya terminado de imprimir
    gui_formatted_output = display_utils.get_gui_output_buffer_and_clear()

    final_output = ""
    # Incluir la salida directa del CLI (si la hay)
    if cli_direct_prints.strip():
        final_output += f"### Salida Directa de Consola:\n<pre>{cli_direct_prints}</pre>\n"
    
    # Incluir los mensajes formateados por display_utils (si los hay)
    if gui_formatted_output.strip():
        final_output += f"### Mensajes del Script:\n{gui_formatted_output}"

    # Si la función del módulo devolvió algo (ej. una lista formateada de Docker, o un mensaje de error), lo añadimos
    # Asegúrate de que este 'result' no duplique la salida ya capturada por gui_formatted_output o cli_direct_prints
    if result is not None and isinstance(result, str) and result.strip() and result.strip() not in final_output:
        final_output += f"\n### Resultado de la Operación:\n{result}"

    return final_output


# --- Funciones auxiliares por módulos (adaptadas para Gradio) ---

## Procesos
def gui_list_processes():
    return _run_module_function(process_management.list_processes)

def gui_terminate_process_by_pid(pid: str, confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(process_management.terminate_process_by_pid, pid, confirm_str)

def gui_terminate_process_by_name(name: str, confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(process_management.terminate_process_by_name, name, confirm_str)

def gui_find_process_info_by_name(name: str):
    return _run_module_function(process_management.find_process_info_by_name, name)


## Docker
def gui_list_docker_containers():
    return _run_module_function(docker_management.list_docker_containers)

def gui_start_docker_container(container_id_name: str):
    return _run_module_function(docker_management.start_docker_container, container_id_name)

def gui_stop_docker_container(container_id_name: str):
    return _run_module_function(docker_management.stop_docker_container, container_id_name)

def gui_restart_docker_container(container_id_name: str):
    return _run_module_function(docker_management.restart_docker_container, container_id_name)

def gui_remove_docker_container(container_id_name: str, confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(docker_management.remove_docker_container, container_id_name, confirm_str)

def gui_view_docker_logs(container_id_name: str, num_lines: str = ''):
    # num_lines debe ser un string o vacío, la función lo manejará
    return _run_module_function(docker_management.view_docker_logs, container_id_name, num_lines)

def gui_exec_docker_command(container_id_name: str, command_to_exec: str):
    return _run_module_function(docker_management.exec_docker_command, container_id_name, command_to_exec)

def gui_clean_docker_images(confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(docker_management.clean_docker_images, confirm_str)

def gui_docker_compose_up():
    return _run_module_function(docker_management.docker_compose_up)

def gui_docker_compose_down():
    return _run_module_function(docker_management.docker_compose_down)

def gui_docker_compose_build():
    return _run_module_function(docker_management.docker_compose_build)

## Servicios
def gui_list_services():
    return _run_module_function(service_management.list_services)

def gui_start_service(service_name: str):
    return _run_module_function(service_management.start_service, service_name)

def gui_stop_service(service_name: str):
    return _run_module_function(service_management.stop_service, service_name)

def gui_restart_service(service_name: str):
    return _run_module_function(service_management.restart_service, service_name)

def gui_enable_service(service_name: str):
    return _run_module_function(service_management.enable_service, service_name)

def gui_disable_service(service_name: str):
    return _run_module_function(service_management.disable_service, service_name)

## Paquetes
def gui_update_system_packages():
    return _run_module_function(package_management.update_system_packages)

def gui_install_package(package_name: str):
    return _run_module_function(package_management.install_package, package_name)

def gui_remove_package(package_name: str, confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(package_management.remove_package, package_name, confirm_str)

def gui_search_package(search_query: str):
    return _run_module_function(package_management.search_package, search_query)

## Usuarios y Grupos
def gui_list_users():
    return _run_module_function(user_group_management.list_users)

def gui_list_groups():
    return _run_module_function(user_group_management.list_groups)

def gui_add_user(username: str, password: str):
    return _run_module_function(user_group_management.add_user, username, password)

def gui_remove_user(username: str, confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(user_group_management.remove_user, username, confirm_str)

def gui_add_group(group_name: str):
    return _run_module_function(user_group_management.add_group, group_name)

def gui_remove_group(group_name: str, confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(user_group_management.remove_group, group_name, confirm_str)

def gui_add_user_to_group(username: str, group_name: str):
    return _run_module_function(user_group_management.add_user_to_group, username, group_name)

def gui_remove_user_from_group(username: str, group_name: str):
    return _run_module_function(user_group_management.remove_user_from_group, username, group_name)

## Redes
def gui_show_network_config():
    return _run_module_function(network_management.show_network_config)

def gui_flush_dns_cache():
    return _run_module_function(network_management.flush_dns_cache)

def gui_test_network_speed():
    return _run_module_function(network_management.test_network_speed)

def gui_view_open_ports():
    return _run_module_function(network_management.view_open_ports)

## Monitorización de Recursos
def gui_get_cpu_usage():
    return _run_module_function(resource_monitoring.get_cpu_usage)

def gui_get_memory_usage():
    return _run_module_function(resource_monitoring.get_memory_usage)

def gui_get_disk_usage():
    return _run_module_function(resource_monitoring.get_disk_usage)

def gui_get_network_stats():
    return _run_module_function(resource_monitoring.get_network_stats)

def gui_get_system_uptime():
    return _run_module_function(resource_monitoring.get_system_uptime)

## Disco y Particiones
def gui_list_disk_partitions():
    return _run_module_function(disk_partition_management.list_disk_partitions)

def gui_get_mount_points():
    return _run_module_function(disk_partition_management.get_mount_points)

def gui_create_directory(path: str):
    return _run_module_function(disk_partition_management.create_directory, path)

def gui_delete_file(path: str, confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(disk_partition_management.delete_file, path, confirm_str)

def gui_delete_directory(path: str, confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(disk_partition_management.delete_directory, path, confirm_str)

def gui_check_disk_health():
    return _run_module_function(disk_partition_management.check_disk_health)


## Firewall
def gui_view_firewall_status():
    return _run_module_function(firewall_management.view_firewall_status)

def gui_enable_firewall(confirm_checkbox: bool):
    confirm_input = 's' if confirm_checkbox else 'n'
    return _run_module_function(firewall_management.enable_firewall, confirm_input)

def gui_disable_firewall(confirm_checkbox: bool):
    confirm_input = 's' if confirm_checkbox else 'n'
    return _run_module_function(firewall_management.disable_firewall, confirm_input)

def gui_list_firewall_rules():
    return _run_module_function(firewall_management.list_firewall_rules)

def gui_add_allow_port_rule_gui(rule_name: str, port: str, protocol: str, direction: str):
    return _run_module_function(firewall_management.add_allow_port_rule, rule_name, port, protocol, direction)

def gui_add_deny_port_rule_gui(rule_name: str, port: str, protocol: str, direction: str):
    return _run_module_function(firewall_management.add_deny_port_rule, rule_name, port, protocol, direction)

def gui_delete_firewall_rule_gui(rule_name: str, port: str, protocol: str, confirm_checkbox: bool):
    confirm_input = 's' if confirm_checkbox else 'n'
    return _run_module_function(firewall_management.delete_allow_port_rule, rule_name, port, protocol, confirm_input)

def gui_add_app_rule_gui(rule_name: str, app_path: str, action: str = "allow", direction: str = "in"):
    return _run_module_function(firewall_management.add_app_rule, rule_name, app_path, action, direction)

def gui_deny_app_rule_gui(rule_name: str, app_path: str, action: str = "block", direction: str = "in"):
    return _run_module_function(firewall_management.add_app_rule, rule_name, app_path, action, direction)

def gui_delete_app_rule_gui(rule_name: str, confirm_checkbox: bool):
    confirm_input = 's' if confirm_checkbox else 'n'
    return _run_module_function(firewall_management.delete_app_rule, rule_name, confirm_input)

def gui_show_rule_by_name_gui(rule_name: str):
    return _run_module_function(firewall_management.show_rule_by_name, rule_name)

def gui_generate_firewall_log_gui():
    return _run_module_function(firewall_management.generate_firewall_log)

def create_gradio_interface():
    with gr.Blocks(title="System Administration Tool",theme=gr.themes.Soft()) as demo:
        gr.Markdown(f"# Herramienta de Administración de Sistemas (GUI)")
        gr.Markdown(f"### Sistema Operativo Detectado: **{system_info_utils.get_os_type().capitalize()}**")

        # --- Pestaña de Usuarios y Grupos ---
        with gr.Tab("Usuarios y Grupos"):
            gr.Markdown("## Administración de Usuarios y Grupos")
            with gr.Accordion("Listar Usuarios y Grupos", open=True):
                list_users_btn = gr.Button("Listar Usuarios")
                output_list_users = gr.Markdown()
                list_users_btn.click(gui_list_users, inputs=None, outputs=output_list_users)

                list_groups_btn = gr.Button("Listar Grupos")
                output_list_groups = gr.Markdown()
                list_groups_btn.click(gui_list_groups, inputs=None, outputs=output_list_groups)

            with gr.Accordion("Añadir Usuario", open=False):
                add_username = gr.Textbox(label="Nombre de Usuario")
                add_password = gr.Textbox(label="Contraseña (opcional)", type="password", info="Si se deja vacío, algunos sistemas podrían pedirla después o usar contraseña vacía.")
                add_user_btn = gr.Button("Añadir Usuario")
                output_add_user = gr.Markdown()
                add_user_btn.click(gui_add_user, inputs=[add_username, add_password], outputs=output_add_user)

            with gr.Accordion("Eliminar Usuario", open=False):
                remove_username = gr.Textbox(label="Nombre de Usuario a Eliminar")
                confirm_remove_user = gr.Checkbox(label="Confirmar Eliminación", info="Marque para confirmar la eliminación de usuario")
                remove_user_btn = gr.Button("Eliminar Usuario")
                output_remove_user = gr.Markdown()
                remove_user_btn.click(gui_remove_user, inputs=[remove_username, confirm_remove_user], outputs=output_remove_user)

            with gr.Accordion("Añadir Grupo", open=False):
                add_group_name = gr.Textbox(label="Nombre del Grupo")
                add_group_btn = gr.Button("Añadir Grupo")
                output_add_group = gr.Markdown()
                add_group_btn.click(gui_add_group, inputs=[add_group_name], outputs=output_add_group)

            with gr.Accordion("Eliminar Grupo", open=False):
                remove_group_name = gr.Textbox(label="Nombre del Grupo a Eliminar")
                confirm_remove_group = gr.Checkbox(label="Confirmar Eliminación", info="Marque para confirmar la eliminación de grupo")
                remove_group_btn = gr.Button("Eliminar Grupo")
                output_remove_group = gr.Markdown()
                remove_group_btn.click(gui_remove_group, inputs=[remove_group_name, confirm_remove_group], outputs=output_remove_group)

            with gr.Accordion("Añadir/Eliminar Usuario de Grupo", open=False):
                user_group_user = gr.Textbox(label="Nombre de Usuario")
                user_group_group = gr.Textbox(label="Nombre del Grupo")
                add_user_to_group_btn = gr.Button("Añadir Usuario a Grupo")
                remove_user_from_group_btn = gr.Button("Eliminar Usuario de Grupo")
                output_user_group = gr.Markdown()
                add_user_to_group_btn.click(gui_add_user_to_group, inputs=[user_group_user, user_group_group], outputs=output_user_group)
                remove_user_from_group_btn.click(gui_remove_user_from_group, inputs=[user_group_user, user_group_group], outputs=output_user_group)


        # --- Pestaña de Redes ---
        with gr.Tab("Redes"):
            gr.Markdown("## Administración de Redes")
            with gr.Accordion("Configuración de Red", open=True):
                show_net_config_btn = gr.Button("Mostrar Configuración de Red")
                output_net_config = gr.Markdown()
                show_net_config_btn.click(gui_show_network_config, inputs=None, outputs=output_net_config)

            with gr.Accordion("Vaciar Caché DNS", open=False):
                flush_dns_btn = gr.Button("Vaciar Caché DNS")
                output_flush_dns = gr.Markdown()
                flush_dns_btn.click(gui_flush_dns_cache, inputs=None, outputs=output_flush_dns)
            
            with gr.Accordion("Test de Velocidad de Red", open=False):
                test_speed_btn = gr.Button("Realizar Test de Velocidad")
                output_test_speed = gr.Markdown()
                test_speed_btn.click(gui_test_network_speed, inputs=None, outputs=output_test_speed)

            with gr.Accordion("Ver Puertos Abiertos", open=False):
                view_ports_btn = gr.Button("Ver Puertos Abiertos")
                output_view_ports = gr.Markdown()
                view_ports_btn.click(gui_view_open_ports, inputs=None, outputs=output_view_ports)


        # --- Pestaña de Paquetes ---
        with gr.Tab("Paquetes"):
            gr.Markdown("## Administración de Paquetes")
            with gr.Accordion("Actualizar Paquetes del Sistema", open=True):
                update_packages_btn = gr.Button("Actualizar Paquetes del Sistema")
                output_packages_update = gr.Markdown()
                update_packages_btn.click(gui_update_system_packages, inputs=None, outputs=output_packages_update)
            
            with gr.Accordion("Instalar Paquete", open=False):
                package_name_install = gr.Textbox(label="Nombre del Paquete a Instalar")
                install_package_btn = gr.Button("Instalar Paquete")
                output_package_install = gr.Markdown()
                install_package_btn.click(gui_install_package, inputs=[package_name_install], outputs=output_package_install)

            with gr.Accordion("Eliminar Paquete", open=False):
                package_name_remove = gr.Textbox(label="Nombre del Paquete a Eliminar")
                confirm_remove_package = gr.Checkbox(label="Confirmar Eliminación", info="Marque para confirmar la eliminación")
                remove_package_btn = gr.Button("Eliminar Paquete")
                output_package_remove = gr.Markdown()
                remove_package_btn.click(gui_remove_package, inputs=[package_name_remove, confirm_remove_package], outputs=output_package_remove)

            with gr.Accordion("Buscar Paquete", open=False):
                search_package_query = gr.Textbox(label="Término de búsqueda")
                search_package_btn = gr.Button("Buscar Paquete")
                output_package_search = gr.Markdown()
                search_package_btn.click(gui_search_package, inputs=[search_package_query], outputs=output_package_search)


        # --- Pestaña de Recursos ---
        with gr.Tab("Recursos"):
            gr.Markdown("## Monitorización de Recursos")
            with gr.Accordion("Uso de CPU", open=True):
                get_cpu_btn = gr.Button("Obtener Uso de CPU")
                output_cpu_usage = gr.Markdown()
                get_cpu_btn.click(gui_get_cpu_usage, inputs=None, outputs=output_cpu_usage)
            
            with gr.Accordion("Uso de Memoria", open=False):
                get_mem_btn = gr.Button("Obtener Uso de Memoria")
                output_mem_usage = gr.Markdown()
                get_mem_btn.click(gui_get_memory_usage, inputs=None, outputs=output_mem_usage)

            with gr.Accordion("Uso de Disco", open=False):
                get_disk_usage_btn = gr.Button("Obtener Uso de Disco")
                output_disk_usage = gr.Markdown()
                get_disk_usage_btn.click(gui_get_disk_usage, inputs=None, outputs=output_disk_usage)
            
            with gr.Accordion("Estadísticas de Red", open=False):
                get_net_stats_btn = gr.Button("Obtener Estadísticas de Red")
                output_net_stats = gr.Markdown()
                get_net_stats_btn.click(gui_get_network_stats, inputs=None, outputs=output_net_stats)
            
            with gr.Accordion("Tiempo de Actividad (Uptime)", open=False):
                get_uptime_btn = gr.Button("Obtener Tiempo de Actividad")
                output_uptime = gr.Markdown()
                get_uptime_btn.click(gui_get_system_uptime, inputs=None, outputs=output_uptime)


        # --- Pestaña de Servicios ---
        with gr.Tab("Servicios"):
            gr.Markdown("## Administración de Servicios")
            with gr.Accordion("Listar Servicios", open=True):
                list_services_btn = gr.Button("Listar Servicios")
                output_services_list = gr.Markdown()
                list_services_btn.click(gui_list_services, inputs=None, outputs=output_services_list)
            
            with gr.Accordion("Control de Servicios", open=False):
                service_name_control = gr.Textbox(label="Nombre del Servicio")
                start_service_btn = gr.Button("Iniciar")
                stop_service_btn = gr.Button("Detener")
                restart_service_btn = gr.Button("Reiniciar")
                enable_service_btn = gr.Button("Habilitar (Auto)")
                disable_service_btn = gr.Button("Deshabilitar (No Auto)")
                output_service_control = gr.Markdown()

                start_service_btn.click(gui_start_service, inputs=[service_name_control], outputs=output_service_control)
                stop_service_btn.click(gui_stop_service, inputs=[service_name_control], outputs=output_service_control)
                restart_service_btn.click(gui_restart_service, inputs=[service_name_control], outputs=output_service_control)
                enable_service_btn.click(gui_enable_service, inputs=[service_name_control], outputs=output_service_control)
                disable_service_btn.click(gui_disable_service, inputs=[service_name_control], outputs=output_service_control)


        # --- Pestaña de Docker ---
        with gr.Tab("Docker"):
            gr.Markdown("## Administración de Docker")
            with gr.Accordion("Listar Contenedores", open=True):
                list_docker_btn = gr.Button("Listar Contenedores")
                output_docker_list = gr.Markdown()
                list_docker_btn.click(gui_list_docker_containers, inputs=None, outputs=output_docker_list)

            with gr.Accordion("Control de Contenedores", open=False):
                container_id_name_control = gr.Textbox(label="ID o Nombre del Contenedor")
                start_docker_btn = gr.Button("Iniciar")
                stop_docker_btn = gr.Button("Detener")
                restart_docker_btn = gr.Button("Reiniciar")
                output_docker_control = gr.Markdown()

                start_docker_btn.click(gui_start_docker_container, inputs=[container_id_name_control], outputs=output_docker_control)
                stop_docker_btn.click(gui_stop_docker_container, inputs=[container_id_name_control], outputs=output_docker_control)
                restart_docker_btn.click(gui_restart_docker_container, inputs=[container_id_name_control], outputs=output_docker_control)
            
            with gr.Accordion("Eliminar Contenedor", open=False):
                container_id_name_remove = gr.Textbox(label="ID o Nombre del Contenedor a Eliminar")
                confirm_remove_docker = gr.Checkbox(label="Confirmar Eliminación", info="Marque para confirmar la eliminación")
                remove_docker_btn = gr.Button("Eliminar Contenedor")
                output_docker_remove = gr.Markdown()
                remove_docker_btn.click(gui_remove_docker_container, inputs=[container_id_name_remove, confirm_remove_docker], outputs=output_docker_remove)

            with gr.Accordion("Ver Logs de Contenedor", open=False):
                container_id_name_logs = gr.Textbox(label="ID o Nombre del Contenedor")
                num_lines_logs = gr.Textbox(label="Número de líneas (opcional, vacío para todas)", placeholder="Ej: 100")
                view_logs_btn = gr.Button("Ver Logs")
                output_docker_logs = gr.Markdown()
                view_logs_btn.click(gui_view_docker_logs, inputs=[container_id_name_logs, num_lines_logs], outputs=output_docker_logs)

            with gr.Accordion("Ejecutar Comando en Contenedor", open=False):
                container_id_name_exec = gr.Textbox(label="ID o Nombre del Contenedor")
                command_to_exec = gr.Textbox(label="Comando a Ejecutar (ej: ls -l /)", placeholder="ls -l /app")
                exec_command_btn = gr.Button("Ejecutar Comando")
                output_docker_exec = gr.Markdown()
                exec_command_btn.click(gui_exec_docker_command, inputs=[container_id_name_exec, command_to_exec], outputs=output_docker_exec)
            
            with gr.Accordion("Eliminar Imágenes No Utilizadas", open=False):
                confirm_clean_images = gr.Checkbox(label="Confirmar Eliminación", info="Marque para confirmar la eliminación de todas las imágenes no utilizadas")
                clean_images_btn = gr.Button("Limpiar Imágenes")
                output_docker_clean = gr.Markdown()
                clean_images_btn.click(gui_clean_docker_images, inputs=[confirm_clean_images], outputs=output_docker_clean)

            with gr.Accordion("Docker Compose", open=False):                                
                with gr.Row():
                    deploy_compose_btn = gr.Button("Levantar Servicios (Up -d)")
                    stop_compose_btn = gr.Button("Detener y Eliminar Servicios (Down)")
                    build_compose_btn = gr.Button("Reconstruir Imágenes (Build)")
                
                output_docker_compose = gr.Markdown()
                deploy_compose_btn.click(gui_docker_compose_up, inputs=None, outputs=output_docker_compose)
                stop_compose_btn.click(gui_docker_compose_down, inputs=None, outputs=output_docker_compose)
                build_compose_btn.click(gui_docker_compose_build, inputs=None, outputs=output_docker_compose)

        # --- Pestaña de Firewall Actualizada ---
        with gr.Tab("Firewall"):
            gr.Markdown("## Administración de Firewall")

            # Acordeón 1: Estado y Control General
            with gr.Accordion("Estado y Control del Firewall", open=True):
                gr.Markdown("### Estado del Firewall")
                check_firewall_btn = gr.Button("Ver Estado del Firewall")
                output_firewall_status = gr.Markdown() # Salida específica para estado
                check_firewall_btn.click(gui_view_firewall_status, inputs=None, outputs=output_firewall_status)

                gr.Markdown("### Habilitar/Deshabilitar Firewall")
                gr.Warning("⚠️ Estas operaciones requieren privilegios y pueden afectar la conectividad. Úselas con precaución.")
                with gr.Row():
                    enable_firewall_confirm = gr.Checkbox(label="Confirmar Habilitación", info="Marque para habilitar el firewall.", scale=1)
                    enable_firewall_btn = gr.Button("Habilitar Firewall", scale=2)
                with gr.Row():
                    disable_firewall_confirm = gr.Checkbox(label="Confirmar Deshabilitación", info="Marque para deshabilitar el firewall. Esto puede dejar su sistema vulnerable.", scale=1)
                    disable_firewall_btn = gr.Button("Deshabilitar Firewall", scale=2)
                output_firewall_toggle = gr.Markdown() # Salida específica para habilitar/deshabilitar
                
                enable_firewall_btn.click(gui_enable_firewall, inputs=[enable_firewall_confirm], outputs=output_firewall_toggle)
                disable_firewall_btn.click(gui_disable_firewall, inputs=[disable_firewall_confirm], outputs=output_firewall_toggle)


            # Acordeón 2: Gestión de Reglas por Puerto
            with gr.Accordion("Gestión de Reglas por Puerto", open=False):
                gr.Markdown("### Añadir/Denegar Puerto")
                add_port_rule_name = gr.Textbox(label="Nombre de la Regla (ej: 'Servidor_Web_80')", placeholder="Campo obligatorio")
                add_port_number = gr.Textbox(label="Número de Puerto (ej: 80, 8080)", placeholder="Campo obligatorio")
                add_port_protocol = gr.Radio(["tcp", "udp", "any"], label="Protocolo", value="tcp")
                add_port_direction = gr.Radio(["in", "out", "both"], label="Dirección", value="in", info="La dirección 'both' es para comodidad, se creará una regla 'in' y otra 'out' si el sistema lo soporta.")
                
                with gr.Row():
                    add_allow_port_btn = gr.Button("Añadir Regla (Permitir)")
                    add_deny_port_btn = gr.Button("Añadir Regla (Denegar)")
                output_port_rule_add = gr.Markdown() # Salida específica para añadir reglas de puerto

                # Funciones para permitir/denegar puerto
                def allow_port_wrapper(name, port, protocol, direction):
                    if direction == "both":
                        result_in = gui_add_allow_port_rule_gui(name + "_IN", port, protocol, "in")
                        result_out = gui_add_allow_port_rule_gui(name + "_OUT", port, protocol, "out")
                        return result_in + "\n" + result_out # Concatenar resultados
                    else:
                        return gui_add_allow_port_rule_gui(name, port, protocol, direction)
                
                def deny_port_wrapper(name, port, protocol, direction):
                    if direction == "both":
                        result_in = gui_add_deny_port_rule_gui(name + "_IN", port, protocol, "in")
                        result_out = gui_add_deny_port_rule_gui(name + "_OUT", port, protocol, "out")
                        return result_in + "\n" + result_out
                    else:
                        return gui_add_deny_port_rule_gui(name, port, protocol, direction)

                add_allow_port_btn.click(
                    allow_port_wrapper, # Usamos el wrapper para manejar 'both'
                    inputs=[add_port_rule_name, add_port_number, add_port_protocol, add_port_direction],
                    outputs=output_port_rule_add
                )
                add_deny_port_btn.click(
                    deny_port_wrapper, # Usamos el wrapper para manejar 'both'
                    inputs=[add_port_rule_name, add_port_number, add_port_protocol, add_port_direction],
                    outputs=output_port_rule_add
                )

            # Acordeón 3: Gestión de Reglas por Aplicación
            with gr.Accordion("Gestión de Reglas por Aplicación (Solo Windows)", open=False):
                gr.Markdown("### Añadir/Denegar Aplicación")
                gr.Info("Esta funcionalidad está diseñada principalmente para Windows. En Linux, la gestión por aplicación es diferente (perfiles UFW, etc.).")
                add_app_rule_name = gr.Textbox(label="Nombre de la Regla", placeholder="Ej: 'Permitir_Navegador'")
                add_app_path = gr.Textbox(label="Ruta Completa de la Aplicación (Ej: C:\\Program Files\\App\\app.exe)", placeholder="Campo obligatorio")
                add_app_direction = gr.Radio(["in", "out"], label="Dirección", value="in")
                
                with gr.Row():
                    add_allow_app_btn = gr.Button("Añadir Regla (Permitir Aplicación)")
                    add_deny_app_btn = gr.Button("Añadir Regla (Denegar Aplicación)")
                output_app_rule_add = gr.Markdown() # Salida específica para añadir reglas de app

                add_allow_app_btn.click(
                    lambda name, path, direction: gui_add_app_rule_gui(name, path, "allow", direction), # Lambda para pasar 'allow'
                    inputs=[add_app_rule_name, add_app_path, add_app_direction],
                    outputs=output_app_rule_add
                )
                add_deny_app_btn.click(
                    lambda name, path, direction: gui_deny_app_rule_gui(name, path, "block", direction), # Lambda para pasar 'block'
                    inputs=[add_app_rule_name, add_app_path, add_app_direction],
                    outputs=output_app_rule_add
                )

            # Acordeón 4: Listar y Eliminar Reglas (General)
            with gr.Accordion("Listar y Eliminar Reglas", open=False):
                gr.Markdown("### Listar Todas las Reglas")
                list_firewall_rules_btn = gr.Button("Listar Reglas del Firewall")
                output_list_rules = gr.Markdown() # Salida específica para listar reglas
                list_firewall_rules_btn.click(gui_list_firewall_rules, inputs=None, outputs=output_list_rules)

                gr.Markdown("### Eliminar Regla por Nombre/Puerto")
                gr.Info("Para Windows, use el Nombre de la Regla. Para Linux (UFW), el Puerto y Protocolo son clave. Si no está seguro, liste las reglas primero.")
                delete_rule_name = gr.Textbox(label="Nombre de la Regla (Windows) / (Opcional, para Linux)", placeholder="Ej: 'Permitir_SSH'")
                delete_rule_port = gr.Textbox(label="Puerto (Linux UFW / Opcional)", placeholder="Ej: 22")
                delete_rule_protocol = gr.Radio(["tcp", "udp", "any"], label="Protocolo (Linux UFW / Opcional)", value="any")
                
                with gr.Row():
                    delete_rule_confirm = gr.Checkbox(label="Confirmar Eliminación", info="Marque para confirmar la eliminación de la regla.", scale=1)
                    delete_rule_btn = gr.Button("Eliminar Regla", scale=2)
                output_delete_rule = gr.Markdown() # Salida específica para eliminar reglas

                delete_rule_btn.click(
                    gui_delete_firewall_rule_gui,
                    inputs=[delete_rule_name, delete_rule_port, delete_rule_protocol, delete_rule_confirm],
                    outputs=output_delete_rule
                )
                
                gr.Markdown("### Eliminar Regla de Aplicación (Solo Windows)")
                delete_app_rule_name = gr.Textbox(label="Nombre de la Regla de Aplicación a Eliminar", placeholder="Ej: 'Permitir_Navegador'")
                with gr.Row():
                    delete_app_rule_confirm = gr.Checkbox(label="Confirmar Eliminación de Regla de Aplicación", info="Marque para confirmar.", scale=1)
                    delete_app_rule_btn = gr.Button("Eliminar Regla de Aplicación", scale=2)
                output_delete_app_rule = gr.Markdown() # Salida específica para eliminar reglas de app
                
                delete_app_rule_btn.click(
                    gui_delete_app_rule_gui,
                    inputs=[delete_app_rule_name, delete_app_rule_confirm],
                    outputs=output_delete_app_rule
                )
                
            # Acordeón 5: Mostrar Regla por Nombre (Consolidado)
            with gr.Accordion("Buscar Regla por Nombre", open=False):
                gr.Info("Útil principalmente en Windows. En Linux, se listarán todas las reglas para búsqueda manual.")
                search_rule_name_input = gr.Textbox(label="Nombre de la Regla a Buscar")
                search_rule_by_name_btn = gr.Button("Mostrar Regla por Nombre")
                output_search_rule = gr.Markdown() # Salida específica para búsqueda por nombre
                search_rule_by_name_btn.click(gui_show_rule_by_name_gui, inputs=[search_rule_name_input], outputs=output_search_rule)


            # Acordeón 6: Generar Log (Consolidado)
            with gr.Accordion("Generar Log de Firewall", open=False):
                generate_firewall_log_btn = gr.Button("Generar Log Completo del Firewall")
                output_generate_log = gr.Markdown() # Salida específica para log
                generate_firewall_log_btn.click(gui_generate_firewall_log_gui, inputs=None, outputs=output_generate_log)

        # --- Pestaña de Disco ---
        with gr.Tab("Disco"):
            gr.Markdown("## Administración de Disco y Particiones")
            with gr.Accordion("Listar Discos y Particiones", open=True):
                list_disk_parts_btn = gr.Button("Listar Discos y Particiones")
                output_disk_parts = gr.Markdown()
                list_disk_parts_btn.click(gui_list_disk_partitions, inputs=None, outputs=output_disk_parts)

                get_mount_points_btn = gr.Button("Ver Puntos de Montaje")
                output_mount_points = gr.Markdown()
                get_mount_points_btn.click(gui_get_mount_points, inputs=None, outputs=output_mount_points)
            
            with gr.Accordion("Crear Directorio", open=False):
                create_dir_path = gr.Textbox(label="Ruta del Nuevo Directorio (ej: /home/usuario/nueva_carpeta)")
                create_dir_btn = gr.Button("Crear Directorio")
                output_create_dir = gr.Markdown()
                create_dir_btn.click(gui_create_directory, inputs=[create_dir_path], outputs=output_create_dir)

            with gr.Accordion("Eliminar Archivo", open=False):
                delete_file_path = gr.Textbox(label="Ruta del Archivo a Eliminar (ej: /home/usuario/archivo.txt)")
                confirm_delete_file = gr.Checkbox(label="Confirmar Eliminación", info="Marque para confirmar la eliminación del archivo")
                delete_file_btn = gr.Button("Eliminar Archivo")
                output_delete_file = gr.Markdown()
                delete_file_btn.click(gui_delete_file, inputs=[delete_file_path, confirm_delete_file], outputs=output_delete_file)
            
            with gr.Accordion("Eliminar Directorio (Recursivo)", open=False):
                delete_dir_path = gr.Textbox(label="Ruta del Directorio a Eliminar (ej: /home/usuario/carpeta_a_eliminar)")
                confirm_delete_dir = gr.Checkbox(label="Confirmar Eliminación", info="Marque para confirmar la eliminación recursiva del directorio y su contenido")
                delete_dir_btn = gr.Button("Eliminar Directorio")
                output_delete_dir = gr.Markdown()
                delete_dir_btn.click(gui_delete_directory, inputs=[delete_dir_path, confirm_delete_dir], outputs=output_delete_dir)
            
            with gr.Accordion("Comprobar Salud del Disco (S.M.A.R.T. en Linux)", open=False):
                check_disk_health_btn = gr.Button("Comprobar Salud del Disco")
                output_disk_health = gr.Markdown()
                check_disk_health_btn.click(gui_check_disk_health, inputs=None, outputs=output_disk_health)


        # --- Pestaña de Procesos (ya existente) ---
        # Este es el código que ya tenías para la pestaña de Procesos
        with gr.Tab("Procesos"): # Repetimos la pestaña de Procesos aquí para que esté ordenada
            gr.Markdown("## Administración de Procesos")
            with gr.Accordion("Listar Procesos", open=True):
                list_proc_btn = gr.Button("Listar Procesos")
                output_proc_list = gr.Markdown()
                list_proc_btn.click(gui_list_processes, inputs=None, outputs=output_proc_list)
            
            with gr.Accordion("Terminar Proceso por PID", open=False):
                pid_to_terminate = gr.Textbox(label="PID del Proceso")
                confirm_terminate_proc = gr.Checkbox(label="Confirmar Terminación", info="Marque para confirmar la eliminación")
                terminate_proc_btn = gr.Button("Terminar Proceso")
                output_proc_terminate = gr.Markdown()
                terminate_proc_btn.click(
                    gui_terminate_process_by_pid,
                    inputs=[pid_to_terminate, confirm_terminate_proc],
                    outputs=output_proc_terminate
                )
            
            with gr.Accordion("Terminar Proceso por Nombre", open=False):
                name_to_terminate = gr.Textbox(label="Nombre del Proceso")
                confirm_terminate_name = gr.Checkbox(label="Confirmar Terminación", info="Marque para confirmar la eliminación")
                terminate_name_btn = gr.Button("Terminar Proceso por Nombre")
                output_proc_terminate_name = gr.Markdown()
                terminate_name_btn.click(
                    gui_terminate_process_by_name,
                    inputs=[name_to_terminate, confirm_terminate_name],
                    outputs=output_proc_terminate_name
                )
            
            with gr.Accordion("Buscar Información de Proceso por Nombre", open=False):
                search_proc_name = gr.Textbox(label="Nombre o parte del nombre del proceso a buscar")
                search_proc_btn = gr.Button("Buscar Proceso")
                output_proc_search = gr.Markdown()
                search_proc_btn.click(
                    gui_find_process_info_by_name,
                    inputs=[search_proc_name],
                    outputs=output_proc_search
                )

    return demo

# --- Lanzamiento de la Interfaz (ya proporcionado y validado en la respuesta anterior) ---
def start_gui():
    """Inicia la interfaz gráfica de Gradio."""
    display_utils.IS_GUI_MODE = True
    print("Iniciando la interfaz gráfica de Gradio...")
    app = create_gradio_interface()
    # Aseguramos que Gradio se lance en el navegador automáticamente
    app.launch(share=False, inbrowser=True)