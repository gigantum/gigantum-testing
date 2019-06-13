import logging
import time

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import testutils


def test_pip_packages(driver: selenium.webdriver, *args, **kwargs):
    """
    Test that pip packages install successfully.

    Args:
        driver
    """
    # Create project
    r = testutils.prep_py3_minimal_base(driver)
    username, project_title = r.username, r.project_name
    # Add pip packages
    env_elts = testutils.EnvironmentElements(driver)
    env_elts.add_pip_packages("pandas", "numpy", "matplotlib")
    # Get environment package versions
    logging.info("Extracting package versions from environment")
    environment_package_versions = env_elts.get_all_versions()

    #Open JupyterLab and create Jupyter notebook
    jupyterlab_elts = testutils.JupyterLabElements(driver)
    jupyterlab_elts.create_jupyter_notebook()
    logging.info("Running script to import packages and print package versions")
    package_script = "import pandas\nimport numpy\nimport matplotlib\n" \
                     "print(pandas.__version__,numpy.__version__,matplotlib.__version__)"
    actions = ActionChains(driver)
    actions.move_to_element(jupyterlab_elts.code_input.find()).click(jupyterlab_elts.code_input.find()).send_keys(package_script).perform()
    time.sleep(30)
    jupyterlab_elts.run_button.find().click()

    time.sleep(3)

    # Get JupyterLab package versions
    logging.info("Extracting package versions from JupyterLab")
    jupyterlab_package_output = jupyterlab_elts.code_output.find().text.split(" ")
    jupyterlab_package_versions = jupyterlab_package_output
    logging.info(f"Environment package version {environment_package_versions} \n "
                 f"JupyterLab package version {jupyterlab_package_versions}")

    assert environment_package_versions == jupyterlab_package_versions,\
        "Environment and JupyterLab package versions do not match"

def test_valid_custom_docker(driver: selenium.webdriver, *args, **kwargs):
    """
    Test valid custom Docker instructions.

    Args:
        driver
    """
    # Create project
    r = testutils.prep_py3_minimal_base(driver)
    username, project_name = r.username, r.project_name
    env_elts = testutils.EnvironmentElements(driver)
    env_elts.add_custom_docker_instructions("RUN cd /tmp && "
                                            "git clone https://github.com/gigantum/confhttpproxy && "
                                            "cd /tmp/confhttpproxy && pip install -e.")
    time.sleep(3)
    wait = WebDriverWait(driver, 90)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".flex>.Stopped")))
    container_status = driver.find_element_by_css_selector(".flex>.Stopped").is_displayed()
    time.sleep(2)
    assert container_status, "Expected stopped container status"


def test_invalid_custom_docker(driver: selenium.webdriver, *args, **kwargs):
    """
    Test invalid custom Docker instructions.

    Args:
        driver
    """
    # Create project
    r = testutils.prep_py3_minimal_base(driver)
    username, project_name = r.username, r.project_name
    env_elts = testutils.EnvironmentElements(driver)
    env_elts.add_custom_docker_instructions("RUN /bin/false")
    time.sleep(3)
    wait = WebDriverWait(driver, 90)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".flex>.Rebuild")))

    container_status = driver.find_element_by_css_selector(".flex>.Rebuild").is_displayed()
    assert container_status, "Expected rebuild container status"

    footer_message_text = driver.find_element_by_css_selector(".Footer__message-title").text
    assert "Project failed to build" in footer_message_text, "Expected 'Project failed to build' in footer message"