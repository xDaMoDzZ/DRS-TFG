import os
import sys
import collections
# Detectar si estamos en modo GUI
IS_GUI_MODE = False

_gui_output_buffer = []

# Cola para almacenar las respuestas predefinidas para get_user_input en modo GUI
_gui_input_queue = collections.deque()

# Clase de colore personalizado para el terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'  # Amarillo
    FAIL = '\033[91m'     # Rojo
    ENDC = '\033[0m'      # Resetear color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# --- Funciones Auxiliares para Impresión ---

def _print_colored_message(message: str, color_code: str):
    """
    Función interna para imprimir mensajes con color en la terminal
    o añadirlos al buffer GUI con formato Markdown.
    """
    if not IS_GUI_MODE:
        print(f"{color_code}{message}{Colors.ENDC}")
    else:
        # En modo GUI, añadimos el mensaje al buffer con un formato Markdown básico
        prefix = ""
        if color_code == Colors.OKCYAN:
            prefix = "**[INFO]** "
        elif color_code == Colors.OKGREEN:
            prefix = "**[ÉXITO]** "
        elif color_code == Colors.FAIL:
            prefix = "**[ERROR]** "
        elif color_code == Colors.WARNING:
            prefix = "**[ADVERTENCIA]** "
        
        _gui_output_buffer.append(f"{prefix}{message}")

def clear_screen():
    """
    Limpia la pantalla de la terminal o el buffer de salida en modo GUI.
    """
    if not IS_GUI_MODE:
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        # En modo GUI, vaciamos el buffer de salida
        _gui_output_buffer.clear()

def print_header(title: str):
    """
    Imprime un encabezado formateado en la terminal o lo añade al buffer GUI.
    """
    if not IS_GUI_MODE:
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}--- {title.upper()} ---{Colors.ENDC}\n")
    else:
        _gui_output_buffer.append(f"## {title}\n---") # Formato Markdown para encabezado

def print_info(message: str):
    """Imprime un mensaje de información."""
    _print_colored_message(message, Colors.OKCYAN)

def print_success(message: str):
    """Imprime un mensaje de éxito."""
    _print_colored_message(message, Colors.OKGREEN)

def print_error(message: str):
    """Imprime un mensaje de error."""
    _print_colored_message(message, Colors.FAIL)

def print_warning(message: str):
    """Imprime un mensaje de advertencia."""
    _print_colored_message(message, Colors.WARNING)

def set_gui_input_queue(inputs: list):
    """
    Establece una cola de entradas predefinidas para `get_user_input` en modo GUI.
    Esto permite que las funciones que esperan una interacción de usuario (como 's/N')
    obtengan sus respuestas de manera no interactiva desde la GUI.
    """
    _gui_input_queue.clear()
    _gui_input_queue.extend(inputs)

def get_gui_output_buffer_and_clear() -> str:
    """
    Recupera el contenido actual del buffer de salida de la GUI,
    lo formatea como una cadena Markdown y luego limpia el buffer.
    """
    output = "\n".join(_gui_output_buffer)
    _gui_output_buffer.clear() # Limpiar el buffer después de recuperarlo
    return output

def get_user_input(prompt: str) -> str:
    """
    Obtiene la entrada del usuario, adaptado para GUI/CLI.
    En modo GUI, intenta obtener la entrada de la cola predefinida.
    """
    if not IS_GUI_MODE:
        return input(f"{Colors.OKBLUE}{prompt}: {Colors.ENDC}").strip()
    else:
        if _gui_input_queue:
            # Si hay elementos en la cola, los usa
            response = _gui_input_queue.popleft()
            print_info(f"Respuesta automática para '{prompt}': '{response}'")
            return str(response).strip()
        else:
            # Esto no debería ocurrir si la lógica de la GUI es correcta y predefine las entradas.
            # Podría indicar un error en la configuración de `set_gui_input_queue` o una interacción inesperada.
            print_warning(f"Advertencia: `get_user_input` llamado en modo GUI sin entrada predefinida para el prompt: '{prompt}'")
            return "" # Retornar cadena vacía o levantar un error según la necesidad.

def print_menu(options: dict):
    """
    Imprime un menú de opciones en la terminal o lo añade al buffer GUI.
    """
    if not IS_GUI_MODE:
        for key, value in options.items():
            print(f"{Colors.OKBLUE}{key}.{Colors.ENDC} {value}")
        print(f"{Colors.OKBLUE}-------------------------{Colors.ENDC}")
    else:
        # En modo GUI, podríamos formatearlo como una lista Markdown
        menu_str = ""
        for key, value in options.items():
            menu_str += f"- **{key}**: {value}\n"
        print(menu_str)