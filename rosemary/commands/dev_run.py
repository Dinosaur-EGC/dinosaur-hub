import click
import subprocess

@click.command("devrun", help="Inicia el servidor Flask en modo desarrollo (debug + reload).")
def dev_run():
    """
    Ejecuta el comando largo de flask run con host 0.0.0.0
    """
    click.echo(click.style("Iniciando DINOSAUR-HUB en modo desarrollo...", fg="green"))
    
    try:
        subprocess.run(
            ["flask", "run", "--host=0.0.0.0", "--reload", "--debug"], 
            check=True
        )
    except KeyboardInterrupt:
        click.echo(click.style("\nServidor detenido.", fg="yellow"))
    except Exception as e:
        click.echo(click.style(f"Error al iniciar el servidor: {e}", fg="red"))