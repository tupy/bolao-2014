# -*- coding: utf-8 -*-

import os
config = os.environ.get('APP_CONFIG', 'Dev')

from bolao.main import app_factory
application = app_factory(config)

if __name__ == "__main__":
    application.run()
