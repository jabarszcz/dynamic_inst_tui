
import setuptools

setuptools.setup(
    name='uftrace_dynamic_client',
    version='0.0.1',
    author='Christian Harper-Cyr',
    author_email='charpercyr@gmail.com',
    description='',
    license='GPLv2',
    keywords='uftrace',
    url='https://github.com/namhyung/uftrace',
    packages=['uftrace_dynamic_client'],
    install_requires=[
        'requests',
        'urwid'
    ],
    entry_points={
        'console_scripts': ['uftrace_dynamic_client=uftrace_dynamic_client.client:main']
    }
)
