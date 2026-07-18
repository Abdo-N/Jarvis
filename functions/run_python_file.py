import os
from subprocess import *
import subprocess

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    
    try:
        absolute_path = os.path.abspath(working_directory)

        target_dir = os.path.normpath(os.path.join(absolute_path, file_path))

        valid_target_dir = os.path.commonpath([absolute_path, target_dir]) == absolute_path

        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_dir):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        
        if not target_dir.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", target_dir] #building the command which is python (script)

        if args != None: #if we have extra configs or flags
            command.extend(args)

        result: CompletedProcess = subprocess.run(command,cwd=absolute_path,capture_output=True,text=True,timeout=30)
        output = ""

        if result.returncode != 0:
            output += f"Process exited with code {result.returncode}"
        
        match (result.stderr, result.stdout):
            case ("", ""):
                output += "No output produced"
            case ("", out):
                output += f"STDOUT: {out}"
            case (out, ""):
                output += f"STDERR: {out}"
            case(stderr,stdout):
                output += f"STDERR: {stderr} \n"
                output += f"STDOUT: {stdout}"
                
        return output
    
    except Exception as e:
       return f"Error: excuting Pyhton file: {e}"