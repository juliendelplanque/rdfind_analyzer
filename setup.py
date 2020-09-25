from setuptools import setup

setup(name='rdfind_analyzer',
      version='0.1',
      description='Analyze and query results of rdfind dry run',
      url='https://github.com/juliendelplanque/rdfind_analyzer',
      author='Julien Delplanque',
      author_email='julien.delplanque@live.be',
      license='GPL-3.0',
      packages=['rdfind_analyzer'],
      zip_safe=False,
      scripts=['bin/rdanalyzer'],
      install_requires=[
          'docopt==0.6.2',
      ],)