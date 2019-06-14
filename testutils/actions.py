import logging
import time
import os

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from testutils import elements
from testutils import testutils
from .graphql import list_remote_projects, delete_remote_project


class ProjectPrepResponse(object):
    def __init__(self, username, project_name):
        self.username = username
        self.project_name = project_name


def prep_base(driver, base_button_check, skip_login=False):
    """Create a new project from the UI and wait until it builds successfully

    Args:
        driver: Selenium webdriver
        base_button_check: Lambda which gives identifier to element in selection menu.
        skip_login: If true, assume you are already logged in
    """
    username = None
    if skip_login is False:
        username = log_in(driver)
        elements.GuideElements(driver).remove_guide()
    else:
        time.sleep(2)
    proj_name = create_project_without_base(driver)
    time.sleep(2)
    select_project_base(driver, base_button_check())

    # assert container status is stopped
    project_elts = elements.ProjectControlElements(driver)
    # This will throw an exception on time-out
    project_elts.container_status_stopped.wait(200).is_displayed()

    return ProjectPrepResponse(username=username, project_name=proj_name)


def create_project_without_base(driver: selenium.webdriver) -> str:
    """
    Create a project without a base.

    Args:
        driver

    Returns:
        Name of project just created
    """
    unique_project_name = testutils.unique_project_name()
    logging.info(f"Creating a new project: {unique_project_name}")
    project_elts = elements.AddProjectElements(driver)
    project_elts.create_new_button.click()
    project_elts.project_title_input.click()
    project_elts.project_title_input.send_keys(unique_project_name)
    project_elts.project_description_input.click()
    project_elts.project_description_input.send_keys(testutils.unique_project_description())
    project_elts.project_continue_button.click()
    return unique_project_name


def select_project_base(driver, button_elt):
    base_elts = elements.AddProjectBaseElements(driver)
    while not button_elt.is_displayed():
        base_elts.arrow_button.click()
        time.sleep(0.25)
    button_elt.click()
    time.sleep(0.25)
    base_elts.create_project_button.click()


def prep_py3_minimal_base(driver, skip_login=False):
    b = lambda: elements.AddProjectBaseElements(driver).py3_minimal_base_button
    return prep_base(driver, b, skip_login)


def log_in(driver: selenium.webdriver, user_index: int = 0) -> str:
    """
    Log in to Gigantum.

    Args:
        driver
        user_index: an offset into credentials.txt

    Returns:
        Username of user just logged in
    """
    username, password = testutils.load_credentials(user_index=user_index)

    driver.get(f"{os.environ['GIGANTUM_HOST']}/projects/local#")
    auth0_elts = elements.Auth0LoginElements(driver)
    auth0_elts.login_green_button.wait().click()
    auth0_elts.auth0_lock_widget.wait()
    if auth0_elts.auth0_lock_button.selector_exists():
        logging.info("Clicking 'Not your account?'")
        auth0_elts.not_your_account_button.wait().click()
    auth0_elts.do_login(username, password)
    time.sleep(5)
    # Set the ID and ACCESS TOKENS -- Used as headers for GraphQL mutations
    access_token = driver.execute_script("return window.localStorage.getItem('access_token')")
    id_token = driver.execute_script("return window.localStorage.getItem('id_token')")
    active_username = driver.execute_script("return window.localStorage.getItem('username')")

    assert active_username == username, \
        f"Username from credentials.txt ({username}) must match chrome cache ({active_username})"

    os.environ['GIGANTUM_USERNAME'] = active_username
    os.environ['ACCESS_TOKEN'] = access_token
    os.environ['ID_TOKEN'] = id_token
    assert os.environ['ACCESS_TOKEN'], "ACCESS_TOKEN could not be retrieved"
    assert os.environ['ID_TOKEN'], "ID_TOKEN could not be retrieved"
    return username.strip()


def delete_dataset_cloud(driver: selenium.webdriver, dataset_title):
    """
    Delete a dataset from cloud.

    Args:
        driver
        dataset

    """
    logging.info(f"Removing dataset {dataset_title} from cloud")
    driver.find_element_by_xpath("//a[contains(text(), 'Datasets')]").click()
    driver.find_element_by_css_selector(".Datasets__nav-item--cloud").click()
    time.sleep(2)
    driver.find_element_by_css_selector(".RemoteDatasets__icon--delete").click()
    driver.find_element_by_css_selector("#deleteInput").send_keys(dataset_title)
    time.sleep(2)
    driver.find_element_by_css_selector(".ButtonLoader").click()
    time.sleep(5)
    wait = WebDriverWait(driver, 200)
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".DeleteDataset")))
