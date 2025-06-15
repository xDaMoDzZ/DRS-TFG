import os
import sys

# Detectar si estamos en modo GUI (Gradio)
# Gradio establece una variable de entorno 'GRADIO_SERVER_PORT'
IS_GUI_MODE = os.environ.get("GRADIO_SERVER_PORT") is not None

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

#Funcion auxiliar generica para imprimir mensajes
def _print_colored_message(message: str, color_code: str):
    """Función interna para imprimir mensajes con color en la terminal."""
    if not IS_GUI_MODE:
        print(f"{color_code}{message}{Colors.ENDC}")
    else:
        # En modo GUI, no usamos colores ANSI directamente
        # Podríamos usar Markdown si fuera necesario, pero para warnings, un simple print está bien.
        print(message)

#Funcion de limpiar pantall
def clear_screen():
    """Limpia la pantalla de la terminal."""
    if not IS_GUI_MODE:
        os.system('cls' if os.name == 'nt' else 'clear')

#Imprimir titulo formateado
def print_header(title: str):
    """Imprime un encabezado formateado."""
    if not IS_GUI_MODE:
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}--- {title.upper()} ---{Colors.ENDC}\n")
    else:
        # En modo GUI, usar Markdown para el encabezado
        print(f"## {title}\n---")

#Prints por tipo
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
    """
    Imprime un mensaje de advertencia.
    NUEVA FUNCIÓN AÑADIDA
    """
    _print_colored_message(message, Colors.WARNING)

#Funcion para obtener input
def get_user_input(prompt: str) -> str:
    """Obtiene la entrada del usuario, adaptado para GUI/CLI."""
    if not IS_GUI_MODE:
        return input(f"{Colors.OKBLUE}{prompt}: {Colors.ENDC}").strip()
    else:
        # En modo GUI, esta función no se usaría directamente para obtener input,
        # sino que el input vendría de los componentes Gradio.
        # Sin embargo, si se llama accidentalmente en GUI, debemos manejarlo.
        print_warning(f"Advertencia: `get_user_input` llamado en modo GUI. Prompt: '{prompt}'")
        return "" # Retornar cadena vacía o levantar un error según la necesidad.

#Funcion para imprimir menu
def print_menu(options: dict):
    """Imprime un menú de opciones."""
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