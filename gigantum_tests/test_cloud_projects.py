import logging
import time
import os
from subprocess import Popen, PIPE

import selenium
from selenium.webdriver.common.by import By

import testutils
from testutils import graphql


def test_publish_sync_delete_project(driver: selenium.webdriver, *args, **kwargs):
    """
    Test that a project in Gigantum can be published, synced, and deleted.
    """
    # Create and publish project
    r = testutils.prep_py3_minimal_base(driver)
    username, project_title = r.username, r.project_name
    cloud_project_elts = testutils.CloudProjectElements(driver)
    cloud_project_elts.publish_private_project(project_title)
    logging.info(f"Navigating to {username}'s Cloud tab")
    driver.get(f"{os.environ['GIGANTUM_HOST']}/projects/cloud")
    cloud_project_elts.first_cloud_project.wait(30)
    first_cloud_project = cloud_project_elts.first_cloud_project.find().text
    logging.info(f"Found first cloud project {first_cloud_project}")

    assert project_title == first_cloud_project, \
        f"Expected {project_title} to be the first cloud project in {username}'s Cloud tab, " \
        f"but instead got {first_cloud_project}"

    logging.info(f"Checking if a remote is set for project {project_title}")
    project_path = os.path.join(os.environ['GIGANTUM_HOME'], username, username,
                                'labbooks', project_title)
    git_get_remote_command_1 = Popen(['git', 'remote', 'get-url', 'origin'],
                                     cwd=project_path, stdout=PIPE, stderr=PIPE)
    cloud_project_stdout = git_get_remote_command_1.stdout.readline().decode('utf-8').strip()

    assert "https://" in cloud_project_stdout, f"Expected to see a remote set for project {project_title}, " \
                                               f"but got {cloud_project_stdout}"

    # Add a file and sync cloud project
    driver.get(f'{os.environ["GIGANTUM_HOST"]}/projects/{username}/{project_title}/inputData')
    time.sleep(3)
    file_browser_elts = testutils.FileBrowserElements(driver)
    file_browser_elts.drag_drop_file_in_drop_zone()
    cloud_project_elts.sync_cloud_project(project_title)

    assert "Sync complete" in cloud_project_elts.sync_cloud_project_message.find().text, \
        "Expected 'Sync complete' in footer"

    # Delete cloud project
    cloud_project_elts.delete_cloud_project(project_title)

    # Assert project does not exist in cloud tab
    first_cloud_project = cloud_project_elts.first_cloud_project.find().text

    assert project_title != first_cloud_project, \
        f"Expected {project_title} to not be the first cloud project in {username}'s Cloud tab, " \
        f"but instead got {first_cloud_project}"

    # Assert project does not exist remotely (via GraphQL)
    remote_projects = graphql.list_remote_projects()

    assert (username, project_title) not in remote_projects

    # Assert that project does not have remote Git repo (use Git 2.20+)
    git_get_remote_command_2 = Popen(['git', 'remote', 'get-url', 'origin'],
                                     cwd=project_path, stdout=PIPE, stderr=PIPE)
    del_cloud_project_stderr = git_get_remote_command_2.stderr.readline().decode('utf-8').strip()

    assert "fatal" in del_cloud_project_stderr, f"Expected to not see a remote set for project {project_title}, " \
                                                f"but got {del_cloud_project_stderr}"


def test_publish_collaborator(driver: selenium.webdriver, *args, ** kwargs):
    """
    Test that a project in Gigantum can be published, shared with a collaborator, and imported by the collaborator.
    """
    # Owner creates and publishes project
    r = testutils.prep_py3_minimal_base(driver)
    username, project_title = r.username, r.project_name
    cloud_project_elts = testutils.CloudProjectElements(driver)
    cloud_project_elts.publish_private_project(project_title)
    # Owner adds collaborator and logs out
    collaborator = cloud_project_elts.add_collaborator_with_permissions(project_title)
    side_bar_elts = testutils.SideBarElements(driver)
    side_bar_elts.do_logout(username)

    # Collaborator logs in, imports cloud project, and logs out
    logging.info(f"Logging in as {collaborator}")
    testutils.log_in(driver, user_index=1)
    time.sleep(2)
    try:
        testutils.GuideElements.remove_guide(driver)
    except:
        pass
    time.sleep(2)
    logging.info(f"Navigating to {collaborator}'s Cloud tab")
    driver.get(f"{os.environ['GIGANTUM_HOST']}/projects/cloud")
    cloud_project_elts.first_cloud_project.wait()
    first_cloud_project = cloud_project_elts.first_cloud_project.find().text

    assert project_title == first_cloud_project, \
        f"Expected {project_title} to be the first cloud project in {collaborator}'s Cloud tab, " \
        f"but instead got {first_cloud_project}"

    cloud_project_elts.import_first_cloud_project_button.find().click()
    container_elts = testutils.ContainerElements(driver)
    container_elts.container_status_stopped.wait(30)
    shared_project_title = cloud_project_elts.project_overview_project_title.find().text

    assert project_title in shared_project_title, \
        f"After import, expected project {project_title} to open to project overview page"

    side_bar_elts.do_logout(collaborator)

    # Owner logs in and deletes cloud project
    logging.info(f"Logging in as {username}")
    testutils.log_in(driver)
    time.sleep(2)
    try:
        testutils.GuideElements.remove_guide(driver)
    except:
        pass
    time.sleep(2)
    cloud_project_elts.delete_cloud_project(project_title)

    # Assert cloud project does not exist remotely (via GraphQL)
    remote_projects = graphql.list_remote_projects()

    assert (username, project_title) not in remote_projects

    # Assert that cloud project does not have remote Git repo (use Git 2.20+)
    project_path = os.path.join(os.environ['GIGANTUM_HOME'], username, username,
                                'labbooks', project_title)
    git_get_remote_command_2 = Popen(['git', 'remote', 'get-url', 'origin'],
                                     cwd=project_path, stdout=PIPE, stderr=PIPE)
    del_cloud_project_stderr = git_get_remote_command_2.stderr.readline().decode('utf-8').strip()

    assert "fatal" in del_cloud_project_stderr, f"Expected to not see a remote set for project {project_title}, " \
                                                f"but got {del_cloud_project_stderr}"


