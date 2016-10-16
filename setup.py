from setuptools import setup


setup(
    name='pluggable-list',
    version='0.1.0',
    description='Functionallity to rapidly implement lists with custom behaviour',
    author='Aubrey Stark-Toller',
    author_email='aubrey@deepearth.uk',
    license='BSD',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL3 License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=['pluggable_list'],
    tests_require = ['pytest', 'pytest-cov',],
    setup_requires = ['pytest-runner']
)
