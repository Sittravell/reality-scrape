from alembic.config import Config
from alembic import command
from dotenv import dotenv_values

def main():
    cfg = dotenv_values()
    albc_cfg = Config(f"{cfg['ROOT']}/alembic.ini")
    command.upgrade(albc_cfg,"head")

if __name__ == '__main__':
    main()