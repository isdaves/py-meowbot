"""Free Google Translate API for Python. Translates totally free of charge."""
__all__ = 'Translator',
__version__ = '2.3.0'

print('Imported local version of googletrans!!!')

from googletrans.client import Translator
from googletrans.constants import LANGCODES, LANGUAGES
