from setuptools import setup

setup(
   name='FnF',
   version='2.0.0',
   description='Library to work with Files \'n\' Folders',
   author='Alan Bacon',
   author_email='alan@bacontowers.co.uk',
   packages=['FnF'],
   install_requires=[
      'pyAbstracts>=1',
      'StringQuartet>=1'
   ]
)