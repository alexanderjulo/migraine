import os
from unittest import TestCase
from tempfile import TemporaryDirectory

from triptan.core import Triptan


class TriptanInitializationTest(TestCase):
    """
        Asserts that triptan can setup the necessary data correctly.
    """

    def test_init_file_structure(self):
        """
            Assert the file structure is created correctly.
        """
        with TemporaryDirectory() as tmpd:
            Triptan.setup(
                tmpd,
                'triptan.yml',
                {'revisions_location': 'revisions'}
            )
            assert os.path.exists(os.path.join(tmpd, 'triptan.yml'))
            assert os.path.exists(os.path.join(tmpd, 'revisions'))


class TriptanTest(TestCase):
    """
        Assert the core functionality is working.
    """

    def setUp(self):
        """
            Create a temporary directory and set triptan up with it.
        """
        self.path = TemporaryDirectory()
        Triptan.setup(
            self.path.name,
            'triptan.yml',
            {'revisions_location': 'revisions'}
        )
        self.triptan = Triptan(self.path.name, 'triptan.yml')

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
        rev_path = os.path.join(self.path.name, 'revisions/revision-000.py')
        assert os.path.exists(rev_path)

        self.triptan.new_revision("another")
        rev_path = os.path.join(self.path.name, 'revisions/revision-001.py')
        assert os.path.exists(rev_path)
