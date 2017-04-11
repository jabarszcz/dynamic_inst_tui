
import setuptools

setuptools.setup(
    name='dynamic_inst_client',
    version='0.0.1',
    author='Christian Harper-Cyr',
    author_email='charpercyr@gmail.com',
    description='',
    license='GPLv2',
    url='https://github.com/jabarszcz/dynamic_inst_tui',
    packages=['dynamic_inst_client'],
    install_requires=[
        'requests',
        'urwid'
    ],
    entry_points={
        'console_scripts': ['dynamic_inst_client=dynamic_inst_client.client:main']
    }
)
