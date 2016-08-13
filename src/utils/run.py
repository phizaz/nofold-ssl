def run_command(command):
    import subprocess
    output = subprocess.check_output(command)
    return output

def run_command_attach_output(command):
    import subprocess
    import sys
    p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
    p.wait()
    if p.returncode is not 0:
        raise Exception('run_command_attach_output with command {} exit with {}'.format(command, p.returncode))

def run_python(script_file, *args, **kwargs):
    import subprocess
    import sys

    params = [
        '--{}={}'.format(key, val)
        for key, val in kwargs.items()
    ]
    args = list(map(str, args))
    return run_command([sys.executable, script_file] + list(args) + params)

def run_python_attach_output(script_file, *args, **kwargs):
    import sys
    params = [
        '--{}={}'.format(key, val)
        for key, val in kwargs.items()
    ]
    return run_command_attach_output([sys.executable, script_file] + list(args) + params)