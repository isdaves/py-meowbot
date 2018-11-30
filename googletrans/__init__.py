"""Free Google Translate API for Python. Translates totally free of charge."""
__all__ = 'Translator',
__version__ = '2.3.0'

print('Imported local version of googletrans!!!')
print('Manually fixes https://github.com/ssut/py-googletrans/issues/78 and https://github.com/ssut/py-googletrans/issues/93')


from googletrans.client import Translator
from googletrans.constants import LANGCODES, LANGUAGES
