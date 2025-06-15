import gradio as gr
import io
import sys

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


#Funciones auxiliares

# Función genérica para ejecutar cualquier función de módulo en modo GUI
def _run_module_function(func, *input_args):
    """
    Ejecuta una función de módulo en modo GUI, gestionando la entrada y la salida.
    input_args son los valores que se pondrán en la cola de input si la función los pide.
    """
    if input_args:
        display_utils.set_gui_input_queue(input_args)
    display_utils.clear_screen()

    try:
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output
        func()
        cli_direct_prints = redirected_output.getvalue()

    finally:
        sys.stdout = old_stdout

    gui_formatted_output = display_utils.get_gui_output_buffer_and_clear()

    final_output = ""
    if cli_direct_prints.strip():
        final_output += f"### Salida Directa de Consola:\n<pre>{cli_direct_prints}</pre>\n"
    if gui_formatted_output.strip():
        final_output += f"### Mensajes del Script:\n{gui_formatted_output}"

    return final_output

#Funciones auxiliares por módulos

# Procesos
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

# Docker
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
    return _run_module_function(docker_management.view_docker_logs, container_id_name, num_lines)

def gui_exec_docker_command(container_id_name: str, command_to_exec: str):
    return _run_module_function(docker_management.exec_docker_command, container_id_name, command_to_exec)

def gui_clean_docker_images(confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(docker_management.clean_docker_images, confirm_str)


# Servicios
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


# Paquetes
def gui_update_system_packages():
    return _run_module_function(package_management.update_system_packages)

def gui_install_package(package_name: str):
    return _run_module_function(package_management.install_package, package_name)

def gui_remove_package(package_name: str, confirm: bool):
    confirm_str = 's' if confirm else 'n'
    return _run_module_function(package_management.remove_package, package_name, confirm_str)

def gui_search_package(search_query: str):
    return _run_module_function(package_management.search_package, search_query)


#Creamos la interfaz con Gradio
def create_gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown(f"# Herramienta de Administración de Sistemas (GUI)")
        gr.Markdown(f"### Sistema Operativo Detectado: {system_info_utils.get_os_type().capitalize()}")

        with gr.Tab("Procesos"):
            with gr.Accordion("Listar Procesos", open=False):
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
                # ELIMINAR ESTE CHECKBOX: confirm_search_terminate = gr.Checkbox(label="¿Desea intentar terminar procesos encontrados?", info="Marque si desea que el script pregunte para terminar procesos")
                search_proc_btn = gr.Button("Buscar Proceso")
                output_proc_search = gr.Markdown()
                search_proc_btn.click(
                    gui_find_process_info_by_name,
                    # Ahora solo pasamos el nombre del proceso como input
                    inputs=[search_proc_name],
                    outputs=output_proc_search
                )

        with gr.Tab("Docker"):
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

        with gr.Tab("Servicios"):
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

        with gr.Tab("Paquetes"):
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

    return demo

#Lanzamos la interfaz
def start_gui():
    """Inicia la interfaz gráfica de Gradio."""
    display_utils.IS_GUI_MODE = True
    print("Iniciando la interfaz gráfica de Gradio...")
    app = create_gradio_interface()
    #Nos aseguramos que gradio se lanza en el navegador
    app.launch(share=False, inbrowser=True)