import click


@click.group()
def app():
    """nbchat CLI application."""
    pass


@app.command()
def main():
    """Start the nbchat CLI application."""
    click.echo("Welcome to nbchat!")


if __name__ == "__main__":
    app()
