import os
import subprocess

def get_os_type():
    """Retorna 'windows' o 'linux'."""
    return 'windows' if os.name == 'nt' else 'linux'

def execute_command(command, sudo=False, shell=True):
    """
    Ejecuta un comando en el sistema operativo y retorna su salida y código de retorno.
    Añade 'sudo' automáticamente si es necesario en Linux y la opción sudo es True.
    """
    if get_os_type() == 'linux' and sudo:
        command = f"sudo {command}"
    
    try:
        process = subprocess.run(
            command, 
            shell=shell, 
            capture_output=True, 
            text=True, 
            check=False # No lanza excepción para códigos de retorno no cero
        )
        output = process.stdout + process.stderr # Captura stdout y stderr
        status = process.returncode
        return output, status
    except Exception as e:
        return f"Excepción al ejecutar comando: {e}", 1 # Retorna un error genérico y código 1