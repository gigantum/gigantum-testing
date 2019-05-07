import logging
from typing import List, Tuple
import time

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .testutils import *
from .graphql import list_remote_datasets, list_remote_projects


class CssElement(object):
    def __init__(self, driver, selector: str):
        self.driver = driver
        self.selector = selector

    def __call__(self):
        return self.find()

    def find(self):
        """Immediately try to find and return the element. """
        return self.driver.find_element_by_css_selector(self.selector)

    def wait(self, nsec: int = 10):
        """Block until the element is visible, and then return it. """
        t0 = time.time()
        try:
            wait = WebDriverWait(self.driver, nsec)
            time.sleep(0.1)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.selector)))
            return self.find()
        except Exception as e:
            tf = time.time()
            m = f'Timed out finding {self.selector} after {tf-t0:.1f}sec'
            logging.error(m)
            if not str(e).strip():
                raise ValueError(m)
            else:
                raise e


class UiComponent(object):
    def __init__(self, driver):
        self.driver = driver


class Auth0LoginElements(UiComponent):
    @property
    def login_green_button(self):
        return CssElement(self.driver, ".Login__button")

    @property
    def auth0_lock_button(self):
        return CssElement(self.driver, ".auth0-lock-social-button")

    @property
    def not_your_account_button(self):
        return CssElement(self.driver, ".auth0-lock-alternative-link")

    @property
    def username_input(self):
        return CssElement(self.driver, ".auth0-lock-input[name = username]")

    @property
    def password_input(self):
        return CssElement(self.driver, ".auth0-lock-input[name = password]")

    @property
    def login_grey_button(self):
        return CssElement(self.driver, ".auth0-lock-submit")

    def do_login(self, username, password):
        self.login_green_button.wait(10).click()
        self.username_input.wait().click()
        self.username_input().send_keys(username)
        self.password_input.wait().click()
        self.password_input().send_keys(password)
        try:
            self.login_grey_button.wait().click()
        except:
            pass


class GuideElements(UiComponent):
    @property
    def got_it_button(self):
        return CssElement(self.driver, ".button--green")

    @property
    def guide_button(self):
        return CssElement(self.driver, ".Helper-guide-slider")

    @property
    def helper_button(self):
        return CssElement(self.driver, ".Helper__button--open")

    def remove_guide(self):
        try:
            logging.info("Getting rid of 'Got it!'")
            self.got_it_button.wait().click()
            logging.info("Turning off guide and helper")
            self.guide_button.wait(5).click()
            self.helper_button.wait(5).click()
        except Exception as e:
            logging.warning(e)


class AddProjectElements(UiComponent):
    @property
    def create_new_button(self):
        return CssElement(self.driver, ".btn--import")

    @property
    def project_title_input(self):
        return CssElement(self.driver, ".CreateLabbook input")

    @property
    def project_description_input(self):
        return CssElement(self.driver, ".CreateLabbook__description-input")

    @property
    def project_continue_button(self):
        return self.driver.find_element_by_xpath("//button[contains(text(), 'Continue')]")

    def create_project_without_base(self) -> str:
        """
        Create a project without a base.

        Returns:
            Name of project just created
        """
        unique_project_name = testutils.unique_project_name()
        logging.info(f"Creating a new project: {unique_project_name}")
        self.create_new_button.click()
        self.project_title_input.click()
        self.project_title_input.send_keys(unique_project_name)
        self.project_description_input.click()
        self.project_description_input.send_keys(testutils.unique_project_description())
        self.project_continue_button.click()
        return unique_project_name


class AddProjectBaseElements(UiComponent):
    @property
    def arrow_button(self):
        return self.driver.find_element_by_css_selector(".slick-arrow slick-next")

    @property
    def create_project_button(self):
        return self.driver.find_element_by_css_selector(".ButtonLoader ")

    @property
    def projects_page_button(self):
        return self.driver.find_element_by_css_selector(".SideBar__icon")

    @property
    def py2_minimal_base_button(self):
        return self.driver.find_element_by_css_selector("h6[data-name='python2-minimal']")

    @property
    def py3_minimal_base_button(self):
        return self.driver.find_element_by_css_selector("h6[data-name='python3-minimal']")

    @property
    def py3_data_science_base_button(self):
        return self.driver.find_element_by_css_selector("h6[data-name='python3-data-science']")

    @property
    def r_tidyverse_base_button(self):
        return self.driver.find_element_by_css_selector("h6[data-name='r-tidyverse']")


class EnvironmentElements(UiComponent):
    @property
    def environment_tab_button(self):
        return self.driver.find_element_by_css_selector("#environment")

    @property
    def add_packages_button(self):
        return self.driver.find_element_by_css_selector(".PackageDependencies__addPackage")

    @property
    def package_name_input(self):
        return self.driver.find_element_by_css_selector(".PackageDependencies__input")

    @property
    def version_name_input(self):
        return self.driver.find_element_by_css_selector(".PackageDependencies__input--version")

    @property
    def add_button(self):
        return self.driver.find_element_by_css_selector(".PackageDependencies__btn--round")

    @property
    def install_packages_button(self):
        return self.driver.find_element_by_css_selector(".PackageDependencies__btn--absolute")

    @property
    def pip_tab_button(self):
        return self.driver.find_element_by_css_selector(".PackageDependencies__btn--absolute")

    @property
    def apt_tab_button(self):
        return self.driver.find_element_by_css_selector(".PackageDependencies__tab:nth-child(3)")

    @property
    def conda3_tab_button(self):
        return self.driver.find_element_by_css_selector(".PackageDependencies__tab:nth-child(2)")

    @property
    def custom_docker_edit_button(self):
        return self.driver.find_element_by_css_selector(".CustomDockerfile__content .Btn")

    @property
    def custom_docker_text_input(self):
        return self.driver.find_element_by_css_selector(".CustomDockerfile__content textarea")

    @property
    def custom_docker_save_button(self):
        return self.driver.find_element_by_css_selector(".CustomDockerfile__content-save-button")


class ImportProjectElements(UiComponent):
    @property
    def import_existing_button(self):
        return self.driver.find_element_by_css_selector(".btn--import~.btn--import")

    @property
    def project_url_input(self):
        return self.driver.find_element_by_css_selector(".Import__input")

    @property
    def import_button(self):
        return self.driver.find_element_by_css_selector("button~button")


class SideBarElements(UiComponent):
    @property
    def projects_icon(self):
        return self.driver.find_element_by_css_selector(".SideBar__nav-item--labbooks")

    @property
    def username_button(self):
        return self.driver.find_element_by_css_selector("#username")

    @property
    def logout_button(self):
        return self.driver.find_element_by_css_selector("#logout")


class DatasetElements(UiComponent):
    @property
    def dataset_page_tab(self):
        return CssElement(self.driver, 'a[href="/datasets/local"]')

    @property
    def create_new_button(self):
        return CssElement(self.driver, ".btn--import")

    @property
    def dataset_title_input(self):
        return CssElement(self.driver, ".CreateLabbook input")

    @property
    def dataset_description_input(self):
        return CssElement(self.driver, ".CreateLabbook__description-input")

    @property
    def dataset_continue_button(self):
        return CssElement(self.driver, ".WizardModal__buttons .Btn--last")

    @property
    def managed_cloud_card_selector(self):
        # TODO - We need a better selector for this
        return CssElement(self.driver, '.BaseCard-wrapper')

    @property
    def create_dataset_button(self):
        return CssElement(self.driver, '.ButtonLoader')

    @property
    def publish_dataset_button(self):
        return CssElement(self.driver, ".Btn--branch--sync--publish")

    @property
    def dataset_cloud_page(self):
        return CssElement(self.driver, ".Tab--cloud")

    @property
    def title(self):
        return CssElement(self.driver, ".TitleSection__namespace-title")

    @property
    def sync_button(self):
        return CssElement(self.driver, 'button[data-tooltip="Sync"]')

    @property
    def publish_confirm_button(self):
        return CssElement(self.driver, ".VisibilityModal__buttons .Btn--last")

    def publish_dataset(self):
        """
        Publish a dataset to cloud and navigate to the cloud.
        """
        logging.info("Publish dataset to cloud")
        self.publish_dataset_button.wait().click()
        time.sleep(1)
        self.publish_confirm_button.wait().click()
        time.sleep(2)
        self.sync_button.wait()
        dss = list_remote_datasets()
        owner, name = self.title().text.split('/')
        owner = owner.strip()
        name = name.strip()
        assert (owner, name) in dss, f"Cannot find {owner}/{name} in remote datasets."
        logging.info(f"Published dataset {owner}/{name}.")

    def create_dataset(self, dataset_name: str) -> str:
        logging.info(f"Creating a new dataset: {dataset_name}...")
        self.driver.get(os.environ['GIGANTUM_HOST'] + '/datasets/local')
        self.dataset_page_tab.wait().click()
        self.create_new_button.wait().click()
        self.dataset_title_input.wait().click()
        self.dataset_title_input().send_keys(dataset_name)
        self.dataset_description_input().click()
        self.dataset_description_input().send_keys(unique_project_description())
        self.dataset_continue_button().click()
        self.managed_cloud_card_selector.wait().click()
        self.create_dataset_button.wait().click()
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".TitleSection")))
        logging.info(f"Finished creating dataset {dataset_name}")
        return dataset_name


class BranchElements(UiComponent):
    @property
    def create_branch_button(self):
        return self.driver.find_element_by_css_selector(".Btn--branch--create")

    @property
    def branch_name_input(self):
        return self.driver.find_element_by_css_selector("#CreateBranchName")

    @property
    def create_button(self):
        return self.driver.find_element_by_css_selector(".CreateBranch__buttons .ButtonLoader")

    @property
    def manage_branches_button(self):
        return self.driver.find_element_by_css_selector(".Btn--branch--manage")


class PublishProjectElements(UiComponent):
    @property
    def publish_project_button(self):
        return CssElement(self.driver, ".Btn--branch--sync--publish")

    @property
    def publish_confirm_button(self):
        return CssElement(self.driver, ".VisibilityModal__buttons .Btn--last")

    @property
    def project_page_tab(self):
        return self.driver.find_element_by_css_selector(".SideBar__nav-item--labbooks")

    @property
    def cloud_tab(self):
        return self.driver.find_element_by_css_selector(".Tab--cloud")

    @property
    def local_tab(self):
        return self.driver.find_element_by_css_selector(".Tab--local")

    @property
    def sync_project_button(self):
        return self.driver.find_element_by_css_selector(".Btn--branch--sync--upToDate")

    @property
    def delete_project_button(self):
        return self.driver.find_element_by_css_selector(".Button__icon--delete")

    @property
    def delete_project_input(self):
        return self.driver.find_element_by_css_selector("#deleteInput")

    @property
    def delete_confirm_button(self):
        return self.driver.find_element_by_css_selector(".ButtonLoader")

    @property
    def publish_continue_button(self):
        return self.driver.find_element_by_xpath("//button[contains(text(), 'Continue')]")

    @property
    def publish_private_project_button(self):
        return self.driver.find_element_by_xpath("//label[@for='project_private']")

    @property
    def publish_private_dataset_button(self):
        return self.driver.find_element_by_xpath("//label[@class='PublishDatasetsModal__private-label']")

    @property
    def publish_all_button(self):
        return self.driver.find_element_by_xpath("//button[contains(text(), 'Publish All')]")

    @property
    def collaborators_button(self):
        return self.driver.find_element_by_css_selector(".Collaborators__btn")

    @property
    def select_permission_button(self):
        return self.driver.find_element_by_css_selector(".CollaboratorsModal__permissions")

    @property
    def select_admin_button(self):
        return self.driver.find_element_by_xpath("//div[contains(text(), 'Admin')]")

    @property
    def collaborators_input(self):
        return self.driver.find_element_by_css_selector(".CollaboratorsModal__input--collaborators")

    @property
    def add_collaborators_button(self):
        return self.driver.find_element_by_css_selector(".CollaboratorsModal__btn--add")

    @property
    def close_collaborators_button(self):
        return self.driver.find_element_by_css_selector(".Modal__close")

    @property
    def import_first_cloud_project_button(self):
        return self.driver.find_element_by_css_selector(".RemoteLabbooks__icon--cloud-download")

    @property
    def container_status_stopped(self):
        return CssElement(self.driver, ".flex>.Stopped")

    @property
    def owner_title(self) -> Tuple[str, str]:
        text = CssElement(self.driver, ".TitleSection__namespace-title").wait(2).text.split('/')
        return text[0].strip(), text[1].strip()

    def publish_project(self):
        """
            Publish a project to cloud. Then assert it is in list_remote_labbooks
            """
        owner, title = self.owner_title
        logging.info(f"Publishing project {owner}/{title}...")
        self.publish_project_button.wait().click()
        self.publish_confirm_button.wait().click()
        logging.info("Waiting for container status to be stopped.")
        self.container_status_stopped.wait(20)
        time.sleep(4)
        remote_projs = list_remote_projects()
        print(remote_projs)
        assert (owner, title) in remote_projs, \
            "Expected {owner}/{title} in published project list"


class ProjectFileBrowserElements(UiComponent):
    @property
    def input_data_tab(self):
        return CssElement(self.driver, "#inputData")

    @property
    def link_dataset_button(self):
        return CssElement(self.driver, 'button[data-tooltip="Link Dataset"]')

    def link_dataset(self, ds_owner: str, ds_name: str):
        logging.info("Linking the dataset to project")
        self.input_data_tab.wait().click()
        self.link_dataset_button.wait().click()
        time.sleep(4)
        self.driver.find_element_by_css_selector(".LinkCard__details").click()
        time.sleep(4)
        wait = WebDriverWait(self.driver, 200)
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".Footer__message-title")))
        self.driver.find_element_by_css_selector(".ButtonLoader ").click()
        # wait the linking window to disappear
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".LinkModal__container")))

