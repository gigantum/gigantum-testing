import logging
import time
import os

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        time.sleep(2)
        elements.GuideElements(driver).remove_guide()
    else:
        time.sleep(2)
    proj_name = create_project_without_base(driver)
    time.sleep(2)
    select_project_base(driver, base_button_check())
    wait = selenium.webdriver.support.ui.WebDriverWait(driver, 200)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".flex>.Stopped")))
    # assert container status is stopped
    container_elts = elements.PublishProjectElements(driver)
    assert container_elts.container_status_stopped.wait().is_displayed(), "Expected stopped container"

    return ProjectPrepResponse(username=username, project_name=proj_name)



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


# create project
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


# environment
def add_pip_package(driver: selenium.webdriver):
    """
    Add pip packages.

    Args:
        driver
    """
    # TODO - Refactor to Environment class in elements.py
    logging.info("Adding pip packages")
    environment = elements.EnvironmentElements(driver)
    environment.environment_tab_button.click()
    time.sleep(3)
    driver.execute_script("window.scrollBy(0, -400);")
    driver.execute_script("window.scrollBy(0, 400);")
    environment.add_packages_button.click()
    pip_list = ["pandas", "numpy", "matplotlib"]
    for pip_pack in pip_list:
        environment.package_name_input.send_keys(pip_pack)
        time.sleep(3)
        environment.add_button.click()
        time.sleep(3)
    environment.install_packages_button.click()


def add_conda3_package(driver: selenium.webdriver):
    """
    Add conda3 packages.

    Args:
        driver
    """
    logging.info("Adding conda3 package")
    environment = elements.EnvironmentElements(driver)
    environment.environment_tab_button.click()
    time.sleep(3)
    environment.conda3_tab_button.click()
    driver.execute_script("window.scrollBy(0, -400);")
    driver.execute_script("window.scrollBy(0, 400);")
    environment.add_packages_button.click()
    environment.package_name_input.send_keys("pyflakes")
    time.sleep(3)
    environment.add_button.click()
    time.sleep(3)
    environment.install_packages_button.click()


def add_apt_package(driver: selenium.webdriver):
    """
    Add apt packages.

    Args:
        driver
    """
    logging.info("Adding apt packages")
    environment = elements.EnvironmentElements(driver)
    environment.environment_tab_button.click()
    time.sleep(3)
    environment.apt_tab_button.click()
    driver.execute_script("window.scrollBy(0, -400);")
    driver.execute_script("window.scrollBy(0, 400);")
    environment.add_packages_button.click()
    environment.package_name_input.send_keys("apache2")
    time.sleep(3)
    environment.add_button.click()
    time.sleep(3)
    environment.install_packages_button.click()


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


def delete_project_cloud(driver: selenium.webdriver, project_title):
    """
    Delete a project from cloud.

    Args:
        driver
        project

    """
    logging.info(f"Removing project {project_title} from cloud")
    publish_elts = elements.PublishProjectElements(driver)
    publish_elts.project_page_tab.click()
    publish_elts.cloud_tab.click()
    time.sleep(2)
    publish_elts.delete_project_button.click()
    time.sleep(2)
    publish_elts.delete_project_input.send_keys(project_title)
    time.sleep(2)
    publish_elts.delete_confirm_button.click()
    time.sleep(5)
    wait = WebDriverWait(driver, 200)
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".DeleteLabbook")))


def log_out(driver: selenium.webdriver):
    """
    Log out of Gigantum.

    Args:
     driver
    """
    logging.info("Logging out")
    time.sleep(2)
    side_bar_elts = elements.SideBarElements(driver)
    side_bar_elts.username_button.click()
    time.sleep(2)
    side_bar_elts.logout_button.click()
    time.sleep(2)
