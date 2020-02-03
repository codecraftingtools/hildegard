#!/usr/bin/env python3

# Copyright (c) 2020 Jeffrey A. Webb

from setuptools import setup, find_packages

setup(
    name="hildegard",
    version="0.1",
    packages=find_packages(),
    install_requires=["qtpy", "pyside2"],
    entry_points={
        # "console_scripts": [
        "gui_scripts": [
            "hildegard = hildegard.__main__:main",
        ],
    },
)
