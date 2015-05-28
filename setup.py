from distutils.core import setup

setup(
      name='pysos',
      version = '1.9',
      description = 'Utility to parse through a sosreport and present related information at a glance',
      long_description = "This utility will parse through a sosreport and report back desired information in a structured and human-readable fashion in order to make troubleshooting easier and faster.",
      author = 'Jake Hunsaker',
      author_email = 'jhunsaker@redhat.com',
      maintainer = 'Jake Hunsaker',
      maintainer_email = 'jhunsaker@redhat.com',
      license = 'GPL',
      url='https://github.com/TurboTurtle/pysos',
      packages = ['pysos', 'pysos.rhevlcbridge'],
      scripts = ['pysos/bin/pysos'],
     )
