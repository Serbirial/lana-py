import setuptools

import versioneer

setuptools.setup(
    name="lana",
    keywords="bot discord api dashboard",
    description="Lana is a new and innovative discord security bot, taking on the challenge of never failing or lagging behind during raids or spam, no matter how large.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    package_data={"lana": ["config/*", "web/html/*", "web/static/*", "ecosystem.config.js"]},
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    include_package_data=True,
    install_requires=[
        "discord.py==2.3.2",
        "psutil",
        "git+https://github.com/Rapptz/discord-ext-menus",
        "unidecode",
        "mariadb",
        "sanic[ext]",
        "redis",
    ],
    packages=setuptools.find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "lana=lana.__main__:main",
        ],
    },
    classifiers=[
        # see https://pypi.org/classifiers/
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    extras_require={
        "dev": ["check-manifest", "versioneer"],
        # 'test': ['coverage'],
    },
    author="Serbirial",
    url="https://github.com/Serbirial/lana-py",
)
