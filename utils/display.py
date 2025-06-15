import os
import sys
import collections

# Detectar si estamos en modo GUI (se setea externamente, por ejemplo, desde gui_interface.py)
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
    WARNING = '\033[93m'   # Amarillo
    FAIL = '\033[91m'      # Rojo
    ENDC = '\033[0m'       # Resetear color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# --- Funciones Auxiliares para Impresión ---

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
        # Formato Markdown para encabezado en GUI: Nivel 2 y una línea
        _gui_output_buffer.append(f"## {title}\n---")

def print_info(message: str):
    """Imprime un mensaje de información."""
    if not IS_GUI_MODE:
        print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} {message}")
    else:
        # Formato Markdown para información
        _gui_output_buffer.append(f"**[INFO]** {message}")

def print_success(message: str):
    """Imprime un mensaje de éxito."""
    if not IS_GUI_MODE:
        print(f"{Colors.OKGREEN}[ÉXITO]{Colors.ENDC} {message}")
    else:
        # Formato Markdown para éxito
        _gui_output_buffer.append(f"**[ÉXITO]** {message}")

def print_error(message: str):
    """Imprime un mensaje de error."""
    if not IS_GUI_MODE:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {message}")
    else:
        # Formato Markdown para error (puede ser más prominente)
        _gui_output_buffer.append(f"**[ERROR]** {message}")

def print_warning(message: str):
    """Imprime un mensaje de advertencia."""
    if not IS_GUI_MODE:
        print(f"{Colors.WARNING}[ADVERTENCIA]{Colors.ENDC} {message}")
    else:
        # Formato Markdown para advertencia
        _gui_output_buffer.append(f"**[ADVERTENCIA]** {message}")

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
    # Unir las líneas del buffer con saltos de línea dobles para Markdown,
    # excepto para los encabezados que ya manejan sus propios saltos.
    # Podríamos añadir un salto de línea extra entre elementos para mejorar la legibilidad.
    output = "\n\n".join(_gui_output_buffer) 
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
            response = _gui_input_queue.popleft()
            # También logeamos esta interacción en el buffer para que se vea en la GUI
            print_info(f"Respuesta automática para '{prompt}': '{response}'") 
            return str(response).strip()
        else:
            # Esto es un caso de error; la GUI debería proporcionar la entrada.
            print_error(f"Error: `get_user_input` llamado en modo GUI sin entrada predefinida para el prompt: '{prompt}'")
            return "" # Retornar cadena vacía o considerar levantar una excepción.

def print_menu(options: dict):
    """
    Imprime un menú de opciones en la terminal o lo añade al buffer GUI.
    """
    if not IS_GUI_MODE:
        for key, value in options.items():
            print(f"{Colors.OKBLUE}{key}.{Colors.ENDC} {value}")
        print(f"{Colors.OKBLUE}-------------------------{Colors.ENDC}")
    else:
        # En modo GUI, formatearlo como una lista Markdown para añadir al buffer
        menu_str = "**Opciones del Menú:**\n" # Un título para el menú en GUI
        for key, value in options.items():
            menu_str += f"- **{key}**: {value}\n"
        # No imprimir directamente, añadir al buffer
        _gui_output_buffer.append(menu_str)