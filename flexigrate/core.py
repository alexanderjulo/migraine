import logging
import os
from fnmatch import fnmatch
from importlib import import_module
from importlib.machinery import SourceFileLoader

import yaml
import click
from jinja2 import Template


log = logging.getLogger('flexigrate')


REV_FILE_NAME_FORMAT = u'revision-{0:03d}.py'


class MigrationLoadingException(Exception):
    pass


class Flexigrate(object):
    """
        The main flexigrate object.
    """

    def __init__(self, path, config_file):
        self.path = path
        self.config_file = config_file
        self.load_config()

        self.revisions = []
        self.load_revisions()
        self.storage = None
        self.init_storage()

    def get_join_path(self, path):
        return os.path.join(self.path, path)

    @property
    def config_path(self):
        return self.get_join_path(self.config_file)

    @property
    def current_revision(self):
        return self.storage.get_current_revision()

    def load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = yaml.load(f)

    def _get_revision(self, num):
        revisions_dir = self.get_join_path(self.config['revisions_location'])
        file_name = REV_FILE_NAME_FORMAT.format(num)
        rev_path = os.path.join(revisions_dir, file_name)
        if not os.path.exists(rev_path):
            return False
        try:
            return SourceFileLoader(
                "revision-{}".format(num), rev_path).load_module()
        except:
            raise MigrationLoadingException(
                "Revision #{} failed to load.".format(num)
            )

    def load_revisions(self):
        i = 0
        while self._get_revision(i):
            self.revisions.append(self._get_revision(i))
            i += 1

    def init_storage(self):
        log.debug(
            "Using %s.%s as storage.",
            self.config['storage']['module'],
            self.config['storage']['class']
        )
        store_mod = import_module(self.config['storage']['module'])
        store_class = getattr(store_mod, self.config['storage']['class'])

        self.storage = store_class(self.path, self.config['storage'])

    def new_revision(self, name=""):
        num = len(self.revisions)
        log.info("Creating new revision #%i", num)
        template_path = os.path.join(
            os.path.dirname(__file__),
            'templates/migration.py'
        )
        with open(template_path, 'r') as f:
            template = Template(f.read())
        revisions_dir = self.get_join_path(self.config['revisions_location'])
        file_name = REV_FILE_NAME_FORMAT.format(num)
        revision_path = os.path.join(revisions_dir, file_name)
        with open(revision_path, 'w') as f:
            f.write(template.render(num=num, name=name))

    def migrate(self, target):
        """
            Runs the given migration.
        """
        log.info("Running migration: %s.", target)
        if target.startswith("-"):
            clean_target = target[1:]
            target_revision = self.current_revision - int(clean_target)
        elif target.startswith("+"):
            clean_target = target[1:]
            target_revision = self.current_revision + int(clean_target)
        elif target == 'head':
            target_revision = len(self.revisions) - 1
        else:
            target_revision = int(target)

        log.info("Current revision #%i.", self.current_revision)
        log.info("Final revision #%i.", target_revision)

        if target_revision > len(self.revisions) - 1 or target_revision < -1:
            log.error("Final revision does not exist.")
            return False

        while self.current_revision != target_revision:
            # store the current revision so that we don't get confused
            # while we are in an iteration
            current = self.current_revision
            if target_revision > current:
                next_revision = self.revisions[current + 1]
                log.info("Running up migration #%i", current + 1)
                next_revision.up()
                log.info("Setting current revision #%i", current + 1)
                self.storage.set_current_revision(current + 1)
            if target_revision < current:
                current_revision = self.revisions[current]
                log.info("Running down migration #%i", current)
                current_revision.down()
                log.info("Setting current revision #%i", current - 1)
                self.storage.set_current_revision(current - 1)

        return True

    @classmethod
    def setup(cls, path, config_file, config):
        """
            Will initialize flexigrate at the given path.
        """
        log.info("Setting up flexigrate for '%s'..", path)
        template_path = os.path.join(
            os.path.dirname(__file__),
            'templates/config.yml'
        )
        with open(template_path, 'r') as f:
            template = Template(f.read())
        with open(os.path.join(path, config_file), 'w') as f:
            f.write(template.render(**config))
        log.info("Created config file '%s'.", config_file)
        os.makedirs(os.path.join(path, config['revisions_location']))
        log.info("Created revisions directory '%s'.",
                 config['revisions_location'])
        log.info("Done.")


class BaseStorage(object):
    """
        Stores the current state of the migrations.
    """

    def __init__(self, path, config):
        """
        Initializes the storage with the current storage configuration.

        :param dict config: the configuration dictionary
        """
        self.path = path
        self.config = config

    def get_current_revision(self):
        """
            Get the current revision from the store.

            :returns: the current revision
            :rtype: int
        """
        raise NotImplementedError()

    def set_current_revision(self, revision):
        """
            Set the current revision in the store.

            :param int revision: the revision to store.
        """
        raise NotImplementedError()
