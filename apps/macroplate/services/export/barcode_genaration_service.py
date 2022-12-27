import random


class BarcodeGenerationService(object):
    """Generate unique bar-codes."""

    def __init__(self):
        self.used_bar_codes = set()

    def generate(self) -> int:
        """Generate unique for this class bar-code"""
        while True:
            bar_code = self._generate_random_bar_code()
            if bar_code not in self.used_bar_codes:
                self.used_bar_codes.add(bar_code)
                return bar_code

    @staticmethod
    def _generate_random_bar_code():
        """Generate ranfom 6-digit code."""
        return random.randint(100000, 999999)
