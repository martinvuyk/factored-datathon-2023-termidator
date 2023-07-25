__pdoc__ = {
    "env": False,
}

import os

if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    """Django crashea a la hora de hacer los Docs si no esta inicializado el setup().\n
    Pero si no se estan haciendo los docs y se ejecuta django.setup(), crashea."""
    import django

    os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"
    django.setup()
