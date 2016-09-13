import logging
import os
import click
import click_log

from migraine import Migraine


log = logging.getLogger('migraine')

@click.group()
@click.pass_context
@click.option('--config', envvar='FLEXIGRATE_CONFIG', default='migraine.yml')
@click.option('--path', envvar='FLEXIGRATE_PATH', default=None)
@click_log.simple_verbosity_option()
@click_log.init('migraine')
def main(ctx, config, path):
    if not path:
        path = os.getcwd()
    ctx.meta['path'] = path
    ctx.meta['config'] = config
    #try:
    ctx.obj = Migraine(path, config)
    #except:
    #    log.warning("Flexigate is not set up for '%s'.", path)

@main.command()
@click.argument('target')
@click.pass_obj
def migrate(migraine, target):
    """
        Migrate up & down.

        Pass in the target where you want to migrate to.

        Accepted values are:

        \b
        - ``head`` -- the topmost migration
        - any number (1, 2, 3, -4, -5, +17), where migraine will
          migrate the given amount of migrations up or down,
          depending on whether the number is positive or negative
        - any migration hash, where every migration between the
          current and the given migration will be executed.
    """
    migraine.migrate(target)

@main.command()
@click.pass_obj
def revision(migraine):
    """
        Manage the revisions.
    """
    migraine.new_revision()


@main.command()
@click.pass_obj
def info(migraine):
    """
        Returns the current migration.
    """
    click.echo(migraine.current_revision)


@main.command()
@click.pass_context
def init(ctx):
    """
        Will create a configuration file
    """
    Migraine.setup(ctx.meta['path'], ctx.meta['config'], {'revisions_location': 'revisions'})
