import logging
import time
import os

import selenium
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains

from .testutils import unique_project_description, load_credentials
from .graphql import list_remote_datasets


class CssElement:
    def __init__(self, driver: selenium.webdriver, selector: str):
        self.driver = driver
        self.selector = selector

    def __call__(self):
        return self.find()

    def find(self):
        """Immediately try to find and return the element.

        raises NoSuchElementException if selector doesn't match anything"""
        return self.driver.find_element_by_css_selector(self.selector)

    def click(self):
        """Immediately try to find and return the element. """
        return self.find().click()

    def is_displayed(self):
        return self.find().is_displayed()

    def wait(self, nsec: int = 10):
        """Block until the element is visible, and then return it. """
        t0 = time.time()
        try:
            wait = WebDriverWait(self.driver, nsec)
            time.sleep(0.1)
            wait.until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, self.selector)))
            return self.find()
        except Exception as e:
            tf = time.time()
            m = f'Timed out finding {self.selector} after {tf-t0:.1f}sec'
            logging.error(m)
            if not str(e).strip():
                raise ValueError(m)
            else:
                raise e

    def selector_exists(self) -> bool:
        try:
            # This throws an exception if it fails
            self.find()
            return True  # i.e., Query succeeded
        except NoSuchElementException:
            return False

    def contains_text(self, text: str) -> bool:
        """Does *text* exist in the text of the specified element?"""
        return text in self.find().text


class UiComponent:
    def __init__(self, driver: selenium.webdriver):
        self.driver = driver


class Auth0LoginElements(UiComponent):
    @property
    def login_green_button(self):
        return CssElement(self.driver, ".Login__button")

    @property
    def auth0_lock_widget(self):
        return CssElement(self.driver, "form.auth0-lock-widget")
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
        self.username_input.wait().click()
        self.username_input().send_keys(username)
        self.password_input.wait().click()
        self.password_input().send_keys(password)
        try:
            self.login_grey_button.wait().click()
        except:
            pass


class SideBarElements(UiComponent):
    @property
    def projects_icon(self):
        return CssElement(self.driver, ".SideBar__nav-item--labbooks")

    @property
    def datasets_icon(self):
        return CssElement(self.driver, ".SideBar__icon--datasets")

    @property
    def username_button(self):
        return CssElement(self.driver, "#username")

    @property
    def logout_button(self):
        return CssElement(self.driver, "#logout")

    def do_logout(self, username):
        logging.info(f"Logging out as {username}")
        self.username_button.wait().click()
        self.logout_button.wait().click()
        time.sleep(2)


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
            self.guide_button.wait().click()
            self.helper_button.wait().click()
        except Exception as e:
            logging.warning(e)


class AddProjectElements(UiComponent):
    @property
    def create_new_button(self):
        return self.driver.find_element_by_css_selector(".btn--import")

    @property
    def project_title_input(self):
        return self.driver.find_element_by_css_selector(".CreateLabbook input")

    @property
    def project_description_input(self):
        return self.driver.find_element_by_css_selector(".CreateLabbook__description-input")

    @property
    def project_continue_button(self):
        return self.driver.find_element_by_xpath("//button[contains(text(), 'Continue')]")


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

    @property
    def rstudio_base_button(self):
        return self.driver.find_element_by_css_selector("h6[data-name='rstudio-server']")


class EnvironmentElements(UiComponent):
    @property
    def environment_tab_button(self):
        return CssElement(self.driver, "#environment")

    @property
    def add_packages_button(self):
        return CssElement(self.driver, ".Btn__plus--featurePosition")

    @property
    def package_name_input(self):
        return CssElement(self.driver, "#packageNameInput")

    @property
    def version_name_input(self):
        return CssElement(self.driver, ".PackageDependencies__input--version")

    @property
    def add_button(self):
        return CssElement(self.driver,".AddPackageForm__entry-buttons")

    @property
    def install_packages_button(self):
        return CssElement(self.driver, ".PackageQueue__buttons")

    @property
    def package_info_table_version_one(self):
        return CssElement(self.driver, f".PackageRow:nth-child(1) .PackageRow__version")

    @property
    def package_info_table_version_two(self):
        return CssElement(self.driver, f".PackageRow:nth-child(2) .PackageRow__version")

    @property
    def package_info_table_version_three(self):
        return CssElement(self.driver, f".PackageRow:nth-child(3) .PackageRow__version")

    @property
    def custom_docker_edit_button(self):
        return CssElement(self.driver, ".CustomDockerfile__content .Btn")

    @property
    def custom_docker_text_input(self):
        return CssElement(self.driver, ".CustomDockerfile__content textarea")

    @property
    def custom_docker_save_button(self):
        return CssElement(self.driver, ".CustomDockerfile__content-save-button")

    @property
    def package_manager_dropdown(self):
        return CssElement(self.driver,".Dropdown")

    @property
    def conda_package_manager_dropdown(self):
        return CssElement(self.driver,".Dropdown__item:nth-child(2)")

    @property
    def apt_package_manager_dropdown(self):
        return CssElement(self.driver,".Dropdown__item:nth-child(3)")

    @property
    def close_install_window(self):
        return CssElement(self.driver,".align-self--end:nth-child(3)")

    def get_all_versions(self):
        versions=[]
        versions.append(self.package_info_table_version_one.wait().text)
        versions.append(self.package_info_table_version_two.wait().text)
        versions.append(self.package_info_table_version_three.wait().text)
        versions.reverse()
        return versions


    def add_pip_packages(self, *pip_packages):
        logging.info("Adding pip packages")
        self.environment_tab_button.wait().click()
        self.driver.execute_script("window.scrollBy(0, -400);")
        self.driver.execute_script("window.scrollBy(0, 400);")
        self.add_packages_button.wait().click()
        for pip_pack in pip_packages:
            logging.info(f"Adding pip package {pip_pack}")
            self.package_name_input.find().send_keys(pip_pack)
            self.add_button.wait().click()
        # Added sleep to wait for packages to finish validating
        time.sleep(6)
        self.install_packages_button.wait(10).click()
        self.close_install_window.wait().click()
        project_control = ProjectControlElements(self.driver)
        project_control.container_status_stopped.wait(120)

    def add_conda_packages(self, *conda_packages):
        logging.info("Adding conda packages")
        self.environment_tab_button.wait().click()
        self.driver.execute_script("window.scrollBy(0, -400);")
        self.driver.execute_script("window.scrollBy(0, 400);")
        self.add_packages_button.wait().click()
        self.package_manager_dropdown.wait().click()
        self.conda_package_manager_dropdown.wait().click()
        for con_pack in conda_packages:
            logging.info(f"Adding conda package {con_pack}")
            self.package_name_input.find().send_keys(con_pack)
            self.add_button.wait().click()
        # conda packages tend to take longer to validate than pip
        time.sleep(10)
        self.install_packages_button.wait(10).click()
        self.close_install_window.wait().click()
        project_control = ProjectControlElements(self.driver)
        project_control.container_status_stopped.wait(120)


    '''Timing should be adjusted before use
     should be reintroduced when apt functions properly
    
    def add_apt_packages(self, *apt_packages):
        logging.info("Adding conda packages")
        self.environment_tab_button.wait().click()
        self.driver.execute_script("window.scrollBy(0, -400);")
        self.driver.execute_script("window.scrollBy(0, 400);")
        self.add_packages_button.wait().click()
        self.package_manager_dropdown.wait().click()
        self.conda_package_manager_dropdown.wait().click()
        for con_pack in con_packages:
            logging.info(f"Adding conda package {con_pack}")
            self.package_name_input.find().send_keys(con_pack)
            self.add_button.wait().click()
        time.sleep(10)
        self.install_packages_button.wait(10).click()
        self.close_install_window.wait().click()
        container_elts = ContainerElements(self.driver)
        container_elts.container_status_stopped.wait(60)
    '''

    def add_custom_docker_instructions(self, docker_instruction):
        logging.info("Adding custom Docker instruction")
        self.environment_tab_button.wait().click()
        time.sleep(2)
        self.driver.execute_script("window.scrollBy(0, 600);")
        self.custom_docker_edit_button.find().click()
        time.sleep(2)
        self.custom_docker_text_input.find().send_keys(docker_instruction)
        time.sleep(2)
        self.driver.execute_script("window.scrollBy(0, 400);")
        self.custom_docker_save_button.wait().click()


class JupyterLabElements(UiComponent):
    @property
    def jupyter_notebook_button(self):
        return CssElement(self.driver, ".jp-LauncherCard-label")

    @property
    def code_input(self):
        return CssElement(self.driver, ".CodeMirror-line")

    @property
    def run_button(self):
        return CssElement(self.driver, ".jp-RunIcon")

    @property
    def code_output(self):
        return CssElement(self.driver, ".jp-OutputArea-output>pre")




class RStudioElements(UiComponent):
    @property
    def some_selected_tab(self):
        """A selector to let us wait until tabs are populated"""
        return CssElement(self.driver, ".gwt-TabLayoutPanelTab-selected")

    @property
    def selected_files_tab(self):
        """A compound selector for the *files* tab ONLY if it's selected"""
        return CssElement(self.driver, ".gwt-TabLayoutPanelTab-selected #rstudio_workbench_tab_files")

    @property
    def selected_plots_tab(self):
        """A compound selector for the *plots* tab ONLY if it's selected"""
        return CssElement(self.driver, ".gwt-TabLayoutPanelTab-selected #rstudio_workbench_tab_plots")

    @property
    def new_button(self):
        """The "New" / "+" button"""
        return CssElement(self.driver, 'div.rstheme_toolbarWrapper > table table td')

    @property
    def r_notebook(self):
        """The R Notebook button - visible only after `new_button` is clicked"""
        return CssElement(self.driver, 'table#rstudio_label_r_notebook_command')

    def new_notebook(self):
        """Create a new notebook"""
        self.new_button.click()
        self.r_notebook.wait().click()

    def ctrl_shift_enter(self, actions):
        """Useful for executing a code block"""
        return actions.key_down(Keys.SHIFT).key_down(Keys.CONTROL).send_keys(Keys.ENTER) \
            .key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()


class ImportProjectElements(UiComponent):
    @property
    def import_existing_button(self):
        return CssElement(self.driver, ".btn--import~.btn--import")

    @property
    def project_url_input(self):
        return CssElement(self.driver, ".Import__input")

    @property
    def import_button(self):
        # TODO This needs to be made more specific
        return CssElement(self.driver, "button~button")

    @property
    def overview_tab(self):
        return CssElement(self.driver, "#overview")

    def import_project_via_url(self, project_url):
        self.import_existing_button.wait().click()
        self.project_url_input.find().send_keys(project_url)
        self.import_button.wait().click()
        self.overview_tab.wait(90)
        # Wait to ensure that the container changes from stopped to building
        time.sleep(5)


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
    def gigantum_cloud_button(self):
        return self.driver.find_element_by_css_selector(".BaseCard")

    @property
    def data_tab(self):
        return CssElement(self.driver, '#data')

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
        wait.until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".TitleSection")))
        logging.info(f"Finished creating dataset {dataset_name}")
        return dataset_name


class BranchElements(UiComponent):
    @property
    def create_branch_button(self):
        return CssElement(self.driver, ".Btn--branch--create")

    @property
    def branch_name_input(self):
        return CssElement(self.driver, "#CreateBranchName")

    @property
    def create_button(self):
        return CssElement(self.driver, ".CreateBranch__buttons .ButtonLoader")

    @property
    def upper_left_branch_name(self):
        return CssElement(self.driver, ".BranchMenu__dropdown-text")

    @property
    def upper_left_branch_local_only(self):
        return CssElement(self.driver, ".BranchMenu__dropdown-btn>div[data-tooltip='Local only']")

    @property
    def upper_left_branch_drop_down_button(self):
        return CssElement(self.driver, ".BranchMenu__dropdown-btn")

    @property
    def upper_left_first_branch_button(self):
        return CssElement(self.driver, ".BranchMenu__text")

    @property
    def manage_branches_button(self):
        return CssElement(self.driver, ".Btn--branch--manage")

    @property
    def manage_branches_branch_name(self):
        return CssElement(self.driver, ".Branches__branchname")

    @property
    def manage_branches_local_only(self):
        return CssElement(self.driver, ".Branches__details>div[data-tooltip='Local only']")

    @property
    def manage_branches_branch_container(self):
        return CssElement(self.driver, ".Branches__branch>.Branches__base-section>.Branches__branchname-container")

    @property
    def manage_branches_merge_branch_button(self):
        return CssElement(self.driver, ".Branches__btn--merge")

    @property
    def manage_branches_confirm_merge_branch_button(self):
        return CssElement(self.driver, ".Branches__Modal-confirm")

    def create_local_branch(self, branch_name):
        logging.info(f"Creating a new local branch {branch_name}")
        self.create_branch_button.wait().click()
        self.branch_name_input.find().send_keys(branch_name)
        self.create_button.wait().click()

    def switch_to_alternate_branch(self):
        """ Switch from the current branch to the alternate branch """
        logging.info("Switching from current branch to alternate branch")
        self.upper_left_branch_drop_down_button.find().click()
        self.upper_left_first_branch_button.wait().click()
        time.sleep(4)

    def merge_alternate_branch(self):
        """ Merge the alternate branch into the current branch """
        logging.info("Merging alternate branch into current branch")
        self.manage_branches_button.wait().click()
        branch_container_hover = ActionChains(self.driver).move_to_element(self.manage_branches_branch_container.find())
        branch_container_hover.perform()
        self.manage_branches_merge_branch_button.wait().click()
        time.sleep(2)
        self.manage_branches_confirm_merge_branch_button.wait().click()
        time.sleep(8)


class CloudProjectElements(UiComponent):
    @property
    def publish_project_button(self):
        return CssElement(self.driver, ".Btn--branch--sync--publish")

    @property
    def publish_confirm_button(self):
        return CssElement(self.driver, ".VisibilityModal__buttons .Btn--last")

    @property
    def open_collaborators_button(self):
        return CssElement(self.driver, ".Collaborators__btn")

    @property
    def collaborator_input(self):
        return CssElement(self.driver, ".CollaboratorsModal__input--collaborators")

    @property
    def collaborator_permissions_button(self):
        return CssElement(self.driver, ".CollaboratorsModal__permissions")

    @property
    def select_write_permissions_button(self):
        return self.driver.find_element_by_xpath("//div[contains(text(), 'Write')]")

    @property
    def select_admin_permissions_button(self):
        return self.driver.find_element_by_xpath("//div[contains(text(), 'Admin')]")

    @property
    def add_collaborator_button(self):
        return CssElement(self.driver, ".Btn__plus")

    @property
    def close_collaborators_button(self):
        return CssElement(self.driver, ".Modal__close")

    @property
    def sync_cloud_project_button(self):
        return CssElement(self.driver, ".Btn--branch--sync--upToDate")

    @property
    def sync_cloud_project_message(self):
        return CssElement(self.driver, ".Footer__message-item>p")

    @property
    def delete_cloud_project_button(self):
        return CssElement(self.driver, ".Button__icon--delete")

    @property
    def delete_cloud_project_input(self):
        return CssElement(self.driver, "#deleteInput")

    @property
    def delete_cloud_project_confirm_button(self):
        return CssElement(self.driver, ".ButtonLoader")

    @property
    def cloud_tab(self):
        return CssElement(self.driver, ".Tab--cloud")

    @property
    def first_cloud_project(self):
        return CssElement(self.driver, ".RemoteLabbooks__panel-title span span")

    @property
    def import_first_cloud_project_button(self):
        return CssElement(self.driver, ".Button__icon--cloud-download")

    @property
    def project_overview_project_title(self):
        return CssElement(self.driver, ".TitleSection__namespace-title")

    @property
    def merge_conflict_use_mine_button(self):
        return CssElement(self.driver, ".ForceSync__buttonContainer button:nth-child(1)")

    @property
    def merge_conflict_use_theirs_button(self):
        return CssElement(self.driver, ".ForceSync__buttonContainer button:nth-child(2)")

    @property
    def merge_conflict_abort_button(self):
        return CssElement(self.driver, ".ForceSync__buttonContainer button:nth-child(3)")

    def publish_private_project(self, project_title):
        logging.info(f"Publishing private project {project_title}")
        self.publish_project_button.wait().click()
        self.publish_confirm_button.wait().click()
        time.sleep(5)
        project_control= ProjectControlElements(self.driver)
        project_control.container_status_stopped.wait(30)
        time.sleep(10)

    def add_collaborator_with_permissions(self, project_title, permissions="read"):
        logging.info(f"Adding a collaborator to project {project_title} with {permissions} permissions")
        self.open_collaborators_button.find().click()
        collaborator = load_credentials(user_index=1)[0].rstrip()
        self.collaborator_input.wait().send_keys(collaborator)
        if permissions == "read":
            self.add_collaborator_button.wait().click()
            time.sleep(2)
        elif permissions == "write":
            self.collaborator_permissions_button.wait().click()
            self.select_write_permissions_button.click()
            self.add_collaborator_button.wait().click()
            time.sleep(2)
        elif permissions == "admin":
            self.collaborator_permissions_button.wait().click()
            self.select_admin_permissions_button.click()
            self.add_collaborator_button.wait().click()
            time.sleep(2)
        else:
            assert False, "An invalid argument was supplied for permissions in add_collaborator_with_permissions"
        self.close_collaborators_button.find().click()
        return collaborator

    def sync_cloud_project(self, project_title):
        logging.info(f"Syncing cloud project {project_title}")
        self.sync_cloud_project_button.find().click()
        time.sleep(5)
        project_control = ProjectControlElements(self.driver)
        project_control.container_status_stopped.wait()

    def delete_cloud_project(self, project_title):
        logging.info(f"Deleting cloud project {project_title}")
        side_bar_elts = SideBarElements(self.driver)
        side_bar_elts.projects_icon.find().click()
        self.cloud_tab.wait().click()
        self.first_cloud_project.wait()
        self.delete_cloud_project_button.find().click()
        self.delete_cloud_project_input.wait().send_keys(project_title)
        self.delete_cloud_project_confirm_button.wait().click()
        time.sleep(10)


class ProjectControlElements(UiComponent):
    @property
    def container_status_stopped(self):
        return CssElement(self.driver, ".flex>.Stopped")

    @property
    def container_status_building(self):
        return CssElement(self.driver, ".flex>.Building")

    @property
    def devtool_launch_button(self):
        return CssElement(self.driver, ".DevTools__btn--launch")

    def launch_devtool(self, tool_name='dev tool'):
        """Launch a dev tool, then switch to it

        tool_name:
            Name of the dev tool, used only for messages
        """
        logging.info(f"Switching to {tool_name}")
        self.devtool_launch_button.wait().click()
        self.open_devtool_tab(tool_name)

    def open_devtool_tab(self, tool_name='dev tool') -> None:
        """Wait for a new tab, then switch to it

        tool_name:
            Name of the dev tool, used only in Exception message
        """
        # Starting a dev tool may take a long time, hence the 35 second timeout
        waiting_start = time.time()
        window_handles = self.driver.window_handles
        while len(window_handles) == 1:
            window_handles = self.driver.window_handles
            if time.time() - waiting_start > 35:
                raise ValueError(f'Timed out waiting for {tool_name} tab (35 second max)')

        self.driver.switch_to.window(window_handles[1])

    def open_gigatab(self) -> None:
        """Switch to the Gigantum Client"""
        window_handles = self.driver.window_handles
        self.driver.switch_to.window(window_handles[0])


class FileBrowserElements(UiComponent):
    @property
    def code_tab(self):
        return CssElement(self.driver, "#code")

    @property
    def input_data_tab(self):
        return CssElement(self.driver, "#inputData")

    @property
    def data_tab(self):
        return CssElement(self.driver, "#data")

    @property
    def file_browser_empty(self):
        return CssElement(self.driver, ".FileBrowser__empty")

    @property
    def file_browser_area(self):
        return CssElement(self.driver, ".FileBrowser")

    @property
    def file_information(self):
        return CssElement(self.driver, ".File__text div span")

    @property
    def check_file_check_box(self):
        return CssElement(self.driver, ".File__row>.CheckboxMultiselect")

    @property
    def delete_file_button(self):
        return CssElement(self.driver, ".FileBrowser__multiselect>.Btn__delete")

    @property
    def confirm_delete_file_button(self):
        return CssElement(self.driver, ".justify--space-around>.File__btn--add")

    @property
    def favorite_file_button_off(self):
        return CssElement(self.driver, ".Btn__Favorite-off")

    @property
    def favorite_file_button_on(self):
        return CssElement(self.driver, ".Btn__Favorite-on")

    @property
    def link_dataset_button(self):
        return CssElement(self.driver, 'button[data-tooltip="Link Dataset"]')

    def drag_drop_file_in_drop_zone(self, file_content="Sample Text"):
        logging.info("Dragging and dropping a file into the drop zone")
        with open("testutils/file_browser_drag_drop_script.js", "r") as js_file:
            js_script = js_file.read()
        file_path = "/tmp/sample-upload.txt"
        with open(file_path, "w") as example_file:
            example_file.write(file_content)
        file_input = self.driver.execute_script(js_script, self.file_browser_area.find(), 0, 0)
        file_input.send_keys(file_path)
        self.file_information.wait()

    def link_dataset(self, ds_owner: str, ds_name: str):
        logging.info("Linking the dataset to project")
        self.input_data_tab.wait().click()
        self.link_dataset_button.wait().click()
        time.sleep(4)
        self.driver.find_element_by_css_selector(".LinkCard__details").click()
        time.sleep(4)
        wait = WebDriverWait(self.driver, 200)
        wait.until(expected_conditions.invisibility_of_element_located((By.CSS_SELECTOR, ".Footer__message-title")))
        self.driver.find_element_by_css_selector(".ButtonLoader ").click()
        # wait the linking window to disappear
        wait.until(expected_conditions.invisibility_of_element_located((By.CSS_SELECTOR, ".LinkModal__container")))


class ActivityElements(UiComponent):
    @property
    def link_activity_tab(self):
        return CssElement(self.driver, 'li#activity > a')

    @property
    def first_card_label(self):
        return CssElement(self.driver, "h6.ActivityCard__commit-message")

    @property
    def first_card_img(self):
        """Returns the first img in an Activity Detail List - not necessarily from the first list!"""
        return CssElement(self.driver, "li.DetailsRecords__item img")

