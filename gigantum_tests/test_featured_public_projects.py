import logging
import time

import selenium
from selenium.webdriver.common.by import By

import testutils


def test_featured_public_projects(driver: selenium.webdriver, *args, **kwargs):
    """
    Test that featured public projects import and build successfully.
    """
    # Log in and remove guide
    testutils.log_in(driver)
    testutils.GuideElements(driver).remove_guide()
    # Import featured public projects
    # TODO - add in https://gigantum.com/gigantum-examples/allen-sdk-examples
    # TODO - add in gigantum.com/randal/baltimore-sun-data-bridge-data
    featured_public_projects = ["gigantum.com/meg297/military-expenditure-gdp-population",
                                "gigantum.com/billvb/fsw-telecoms-study"]

    for project in featured_public_projects:
        logging.info(f"Importing featured public project: {project}")
        import_project_elts = testutils.ImportProjectElements(driver)
        import_project_elts.import_project_via_url(project)
        project_control = testutils.ProjectControlElements(driver)
        project_control.container_status_stopped.wait(90)

        assert project_control.container_status_stopped.find().is_displayed(), "Expected stopped container status"

        logging.info(f"Featured public project {project} was imported successfully")
        side_bar_elts = testutils.SideBarElements(driver)
        side_bar_elts.projects_icon.find().click()
        time.sleep(2)
