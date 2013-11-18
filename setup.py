from setuptools import setup, find_packages


setup(name='agent.pgep',
      version='0.2.1',
      description='Rackspace Cloud Monitoring plugin for PostgreSQL \
      endpoints as an agent.plugin type of check.',
      author='Vic Watkins',
      author_email='vic.watkins@rackspace.com',
      url='https://github.com/vickleford/agent.pgep',
      install_requires=['argparse', 'psycopg2', 'configobj'],
      packages=find_packages(),
      py_modules=['agent_pgep'],
      entry_points = { 'console_scripts': [
        'agent.pgep = agent_pgep:spawn'
      ] }
     )
