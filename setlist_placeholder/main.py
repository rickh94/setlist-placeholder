import os
import random
import tempfile
import webbrowser
from pathlib import Path

from flask import Flask, send_file, render_template, current_app
import click
import jinja2
import toml
import weasyprint
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

HERE = Path(__file__).parent

JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(str(HERE / "templates")))

main_template = JINJA_ENV.get_template("primary.html")


def render_page(page, output: Path):
    tmpdir = Path(tempfile.mkdtemp())
    html = main_template.render(**page)
    tmp_out = tmpdir / "output.html"
    with tmp_out.open("w") as html_file:
        html_file.write(html)
    filename = str(output / f"{page['main_title']}.pdf")
    weasyprint.HTML(filename=str(tmp_out)).write_pdf(filename)
    return filename


def render_from_config_file(config_file, output):
    config = toml.load(config_file)
    for page in config["pages"]:
        render_page(page, output)

    print(output.absolute())


class CreationForm(FlaskForm):
    main_title = StringField("Main Title", validators=[DataRequired()])
    piece_title = StringField("Piece Title")
    piece_players = StringField("Piece Players")
    quote_speaker = StringField("Quote Speaker")
    quote_text = TextAreaField("Quote Text")
    quote_caption = StringField("Quote Caption")


def index():
    form = CreationForm()
    if form.validate_on_submit():
        page = {"main_title": form.data["main_title"]}
        if form.data["piece_title"]:
            page["piece"] = {
                "title": form.data["piece_title"],
                "players": form.data["piece_players"],
            }
        elif form.data["quote_text"]:
            page["quote"] = {
                "speaker": form.data["quote_speaker"],
                "text": form.data["quote_text"],
                "caption": form.data["quote_caption"],
            }
        filename = render_page(page, current_app.config["OUTPUT"])
        return send_file(filename)
    template = JINJA_ENV.get_template("index.html")
    return render_template(template, form=form)


def create_app(output):
    app = Flask("Setlist Placeholder")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "localonly")
    app.config["OUTPUT"] = output

    app.add_url_rule("/", "Index", index, methods=["GET", "POST"])

    return app


@click.command()
@click.option("-c", "--config-file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None)
@click.option("-w", "--web-server", is_flag=True, default=False)
def cli(config_file, output, web_server):
    if not output:
        output = tempfile.mkdtemp()
    output = Path(output)
    if not output.exists():
        output.mkdir(parents=True)

    if config_file:
        render_from_config_file(config_file, output)
    elif web_server:
        app = create_app(output)
        random_port = random.randint(3000, 65535)
        webbrowser.open(f"http://localhost:{random_port}")
        app.run(host="localhost", port=random_port, debug=False)
    else:
        print(
            "You must either specify a configuration file or create pages "
            "interactively with the web server."
        )
