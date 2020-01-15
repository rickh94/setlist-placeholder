import tempfile
from pathlib import Path

import click
import jinja2
import toml
import weasyprint

HERE = Path(__file__).parent

JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(str(HERE / "templates")))

main_template = JINJA_ENV.get_template("primary.html")


def render_page(page, output: Path):
    tmpdir = Path(tempfile.mkdtemp())
    html = main_template.render(**page)
    tmp_out = tmpdir / "output.html"
    with tmp_out.open("w") as html_file:
        html_file.write(html)
    weasyprint.HTML(filename=str(tmp_out)).write_pdf(
        str(output / f"{page['main_title']}.pdf")
    )


@click.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=Path("/tmp"))
def cli(config_file, output):
    config = toml.load(config_file)

    output = Path(output)
    if not output.exists():
        output.mkdir(parents=True)

    for page in config["pages"]:
        render_page(page, output)

    print(output.absolute())
