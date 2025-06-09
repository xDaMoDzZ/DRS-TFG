import os

def clear_screen():
    """Limpia la pantalla de la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * (len(title) + 6))
    print(f"   {title}   ")
    print("=" * (len(title) + 6) + "\n")

def print_menu(options):
    """Imprime un menú de opciones."""
    for key, value in options.items():
        print(f"[{key}] {value}")
    print("-" * 30)

def print_info(message):
    """Imprime un mensaje informativo."""
    print(f"\n[INFO] {message}")

def print_success(message):
    """Imprime un mensaje de éxito."""
    print(f"\n[OK] {message}")

def print_error(message):
    """Imprime un mensaje de error."""
    print(f"\n[ERROR] {message}")

def get_user_input(prompt):
    """Obtiene la entrada del usuario con un prompt."""
    return input(f"\n{prompt}: ").strip()