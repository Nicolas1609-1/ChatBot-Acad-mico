"""Install this project's files in its own home directory only."""
from pathlib import Path
from zipfile import ZipFile
import os

target=Path("/home/nicolas/chatbot-academico")
package=target/"package.zip"
with ZipFile(package) as archive:
    for item in archive.infolist():
        name=item.filename
        if not name.startswith("chatbot-academico/"):
            raise RuntimeError("Invalid package root")
        relative=Path(name.removeprefix("chatbot-academico/"))
        path=target/relative
        if not path.resolve().is_relative_to(target.resolve()):
            raise RuntimeError("Invalid package path")
        if item.is_dir():
            path.mkdir(parents=True,exist_ok=True)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(archive.read(item))
            path.chmod(0o640)
deploy=target/"deploy"
deploy.mkdir(exist_ok=True)
deploy.chmod(0o700)
env=deploy/"app.env"
if not env.exists():
    env.write_text("APP_BIND=100.74.216.15\nAPP_PORT=8091\nAPP_ALLOWED_HOSTS=100.74.216.15:8091,127.0.0.1:8091,localhost:8091\nN8N_CHAT_URL=\n",encoding="utf-8")
    env.chmod(0o600)
unit_directory=Path.home()/".config/systemd/user"
unit_directory.mkdir(parents=True,exist_ok=True)
unit=unit_directory/"chatbot-academico-web.service"
source=(target/"pc/chatbot-academico-web.service").read_bytes()
if unit.exists() and unit.read_bytes()!=source:
    raise RuntimeError("Existing unit differs; manual review required")
unit.write_bytes(source)
print("Installed:",target)
print("Service unit:",unit)
configured=any(line.startswith("N8N_CHAT_URL=https://") for line in env.read_text().splitlines())
print("Chat backend configured:",configured)
