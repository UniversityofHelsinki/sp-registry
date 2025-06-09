"""
behave environment module for testing behave-django
"""

import os
import re

from django.conf import settings
from django.core.management import call_command
from selenium.webdriver.firefox.service import Service
from splinter import Browser


def before_all(context):
    driver_path = getattr(settings, "FIREFOX_DRIVER_PATH", None)
    if driver_path:
        service = Service(executable_path=driver_path)
        context.browser = Browser("firefox", headless=True, service=service)
    else:
        context.browser = Browser("firefox", headless=True)


def before_feature(context, feature):
    if feature.name == "Fixture loading":
        context.fixtures = ["behave-fixtures.json"]
    call_command("flush", verbosity=0, interactive=False)


def before_scenario(context, scenario):
    context.fixtures = ["attribute.json", "nameidformat.json"]


def after_step(context, step):
    if step.status == "failed":
        directory = settings.TEST_SCREENSHOT_DIR
        scenario = re.sub(r"\W+", "", context.scenario.name)
        step = re.sub(r"\W+", "", step.name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(directory + scenario + " " + step + ".html", "w") as f:
            f.write(context.browser.html)
            context.browser.screenshot(directory + scenario + " " + step + ".png")


def after_all(context):
    context.browser.quit()
    context.browser = None
