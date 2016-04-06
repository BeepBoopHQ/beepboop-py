from setuptools import setup


setup(
    name='beepboop',
    version='0.1.1',
    packages=['beepboop'],
    description='Beep Boop client and Bot Manager',
    author='Beep Boop HQ',
    author_email='hello@beepboophq.com',
    url='https://github.com/BeepBoopHQ/beepboop-py',
    install_requires=['six==1.10.0', 'websocket-client==0.35.0'],
    license='MIT',
    classifiers=(
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ),
    keywords='beepboop slack bot manager api'
)