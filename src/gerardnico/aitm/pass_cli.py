import subprocess


def get_secret(path: str) -> str:
    try:
        result = subprocess.run(
            ["pass", path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        raise Exception(f"Api Key Not Found at {path}")
