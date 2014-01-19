from distutils.core import setup  
setup(name='crfseg',
      version='0.01.alpha',  
      keywords=('word', 'segment', 'keyword', 'summerize'),
      description='Chinese Words Segementation Utilities',
      license = 'MIT License',
      author='Janson, Yuzheng',  
      author_email='gandancing@gmail.com',  
      url='http://github.com/jannson/crfseg',  
      packages=['crfseg'],  
      package_dir={'crfseg':'crfseg'},
      package_data={'crfseg':['*.*','data/*']}
)
