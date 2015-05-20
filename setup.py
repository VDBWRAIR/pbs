from setuptools import setup, find_packages

import pbs

setup(
    name = pbs.__projectname__,
    version = pbs.__release__,
    packages = find_packages(),
    author = pbs.__authors__,
    author_email = pbs.__authoremails__,
    description = pbs.__description__,
    license = "GPLv2",
    keywords = pbs.__keywords__,
    entry_points = {
        'console_scripts': [
            'pstat = pbs.pstat:main',
            'psub = pbs.psub:main',
            'taskmaster = pbs.taskmaster:main',
        ],
    },
)
