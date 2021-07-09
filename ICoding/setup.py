from setuptools import setup


setup(
    setup_requires=['pbr>=2.0.0'],
    pbr=True,
    install_requires=[
        'pytz',
        'Flask',
        'tqdm',
        'psutil',
        'paramiko',
        'pyzbar',
        'gevent',
        'urllib3',
        'beautifulsoup4',
        'Pillow',
    ]
)
