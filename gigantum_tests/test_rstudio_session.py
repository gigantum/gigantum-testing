import logging
import time

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


from testutils.elements import ProjectControlElements, RStudioElements, ActivityElements
from gigantum_tests.test_all_base_images import prep_base_rstudio


import_tidyverse_snippet = """```{r}
library(tidyverse)
```
"""

ggplot_snippet = """```{r}
ggplot(mtcars, aes(x=wt, y=mpg)) +
  ggtitle('Dot-plot of mpg on wt') +
  geom_point()
```
"""

def test_rstudio_session(driver: selenium.webdriver, *args, **kwargs):
    """
    Test the creation of a basic RStudio session.
    Args:
        driver
    """
    # Project set up
    prep_base_rstudio(driver)
    # Wait until stopped container status
    project_elements = ProjectControlElements(driver)
    project_elements.container_status_stopped.wait(200)

    logging.info("Opening RStudio")
    project_elements.container_status_stopped.click()
    time.sleep(5)

    project_elements.launch_devtool('RStudio')

    logging.info("Using R console")
    rstudio_elements = RStudioElements(driver)
    rstudio_elements.some_selected_tab.wait()
    # At the beginning, the "Files" tab should be active
    # "selected" is a class on a containing div for the files tab
    assert rstudio_elements.selected_files_tab.selector_exists()
    # We start with the cursor in the console, so we can just start typing
    ActionChains(driver).send_keys("with(mtcars, {plot(wt, mpg); abline(lm(mpg~wt))})\n"
                      "title('Regression of MPG on Weight')\n").perform()
    time.sleep(1)

    logging.info("Checking for active plot")
    # Now the plots tab should be active...
    assert rstudio_elements.selected_plots_tab.selector_exists()
    # ...and the files tab should not
    assert not rstudio_elements.selected_files_tab.selector_exists()

    logging.info('Checking activity record')
    project_elements.open_gigatab()

    activity_elements = ActivityElements(driver)
    activity_elements.link_activity_tab.click()

    time.sleep(1)

    assert activity_elements.first_card_label.contains_text('Executed in console and generated a result')
    # Note - this could be from ANY card, not just the first
    # Dav couldn't figure out how to do searching from within an element
    assert activity_elements.first_card_img.selector_exists()

    logging.info("Creating R notebook")
    # Back to our RStudio window
    project_elements.open_devtool_tab('RStudio')

    rstudio_elements.new_notebook()
    time.sleep(2)

    logging.info("Importing tidyverse in notebook")
    # At this point, we should be in the metadata section of a new R(md) Notebook
    actions = ActionChains(driver).send_keys(Keys.ARROW_DOWN, Keys.ARROW_DOWN) \
        .send_keys(import_tidyverse_snippet) \
        .send_keys(Keys.ARROW_UP)
    # There's probably some more paradigmatic way to do this, but this should work fine enough for now
    rstudio_elements.ctrl_shift_enter(actions)

    # If we run the below before the above finishes, it doesn't appear to work
    time.sleep(1)

    logging.info("Creating a ggplot graph in notebook")
    actions = ActionChains(driver).send_keys(Keys.ARROW_DOWN) \
        .send_keys(ggplot_snippet) \
        .send_keys(Keys.ARROW_UP)
    rstudio_elements.ctrl_shift_enter(actions)

    time.sleep(1)

    logging.info('Checking updated activity record')
    project_elements.open_gigatab()

    # TODO for issue #55 check that a new activity record is created with the proper graphic
