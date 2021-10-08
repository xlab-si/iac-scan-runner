#!/usr/bin/env python

import setuptools


# constructs the local component of the version without the commit hash
def local_scheme(version):
    return ""


setuptools.setup(use_scm_version={"local_scheme": local_scheme})
