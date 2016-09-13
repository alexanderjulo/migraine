import os
from unittest import TestCase
from tempfile import mkdtemp
from shutil import rmtree

from triptan.core import Triptan


class TriptanBaseTestCase(TestCase):

    def setUp(self):
        self.path = mkdtemp()

    def tearDown(self):
        rmtree(self.path)


class TriptanInitializationTest(TriptanBaseTestCase):
    """
        Asserts that triptan can setup the necessary data correctly.
    """

    def test_init_file_structure(self):
        """
            Assert the file structure is created correctly.
        """
        Triptan.setup(
            self.path,
            'triptan.yml',
            {'revisions_location': 'revisions'}
        )
        assert os.path.exists(os.path.join(self.path, 'triptan.yml'))
        assert os.path.exists(os.path.join(self.path, 'revisions'))


class TriptanTest(TriptanBaseTestCase):
    """
        Assert the core functionality is working.
    """

    def setUp(self):
        """
            Create a temporary directory and set triptan up with it.
        """
        super(TriptanTest, self).setUp()
        Triptan.setup(
            self.path,
            'triptan.yml',
            {'revisions_location': 'revisions'}
        )
        self.triptan = Triptan(self.path, 'triptan.yml')

    def test_default_revision(self):
        """
            Assert the default revision is -1.
        """
        assert self.triptan.current_revision == -1

    def test_revision_creation(self):
        """
            Assert that revisions are correctly created.
        """
        self.triptan.new_revision("test revision")
        rev_path = os.path.join(self.path, 'revisions/revision-000.py')
        assert os.path.exists(rev_path)

        self.triptan.new_revision("another")
        rev_path = os.path.join(self.path, 'revisions/revision-001.py')
        assert os.path.exists(rev_path)
