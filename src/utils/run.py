def run_command(command):
    import subprocess
    output = subprocess.check_output(command)
    return output


def run_python(script_file, *args, **kwargs):
    import subprocess
    import sys

    params = [
        '--{}={}'.format(key, val)
        for key, val in kwargs.items()
    ]

    args = list(map(str, args))

    output = subprocess.check_output([sys.executable, script_file] + args + params)
    return output
