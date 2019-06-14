import selenium
from selenium.webdriver.common.by import By

import testutils


def test_base_python2_min(driver: selenium.webdriver, *args, **kwargs):
    """
    Test the creation of a project with a python 2 minimal base.
    """
    b = lambda : \
        testutils.elements.AddProjectBaseElements(driver).py2_minimal_base_button
    testutils.prep_base(driver, b)


def test_base_python3_min(driver: selenium.webdriver, *args, **kwargs):
    """
    Test the creation a project with a python 3 minimal base.
    """
    b = lambda : \
        testutils.elements.AddProjectBaseElements(driver).py3_minimal_base_button
    testutils.prep_base(driver, b)


def test_base_python3_datasci(driver: selenium.webdriver, *args, **kwargs):
    """
    Test the creation of a project with a python 3 data science base.
    """
    b = lambda : \
        testutils.elements.AddProjectBaseElements(driver).py3_data_science_base_button
    testutils.prep_base(driver, b)


def test_base_rtidy(driver: selenium.webdriver, *args, **kwargs):
    """
    Test the creation of a project with a R Tidyverse base.
    """
    b = lambda : \
        testutils.elements.AddProjectBaseElements(driver).r_tidyverse_base_button
    testutils.prep_base(driver, b)


def test_base_rstudio(driver: selenium.webdriver, *args, **kwargs):
    """
    Add an RStudio base.

    Args:
        driver
    """
    def b():
        return testutils.elements.AddProjectBaseElements(driver).rstudio_base_button

    testutils.prep_base(driver, b)


prep_base_rstudio = test_base_rstudio
