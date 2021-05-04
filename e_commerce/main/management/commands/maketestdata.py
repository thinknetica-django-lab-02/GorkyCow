import logging

from django.core.management.base import BaseCommand
from main.tests.fixtures import GoodsFactory

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """This is a class for 'maketestdata' management command which adds some new goods."""

    help = "Makes test data."

    def handle(self, *args, **options):
        """The actual logic of the command."""

        logger.info("Creating test Goods.")
        new_test_good = GoodsFactory()
        new_test_good.save()
        logger.info("Successfully created a test data!")
