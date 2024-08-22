#!/usr/bin/env python3
import datetime
import os
import subprocess
from getpass import getpass

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

WEBDRIVER_WAIT_TIMEOUT = 20


def run(args, password_: str):
    return subprocess.run(args, input=password_.encode(), stdout=subprocess.PIPE)


if __name__ == '__main__':
    keepass_file = os.environ['KEEPASS_FILE']
    keepass_password = getpass("Enter your password: ")

    search_mega_completed_process = run(['keepassxc-cli', 'search', keepass_file, "mega.nz"], keepass_password)
    unfiltered_mega_entries = search_mega_completed_process.stdout.decode()

    # print(unfiltered_mega_entries)

    mega_entries = list(filter(lambda x: len(x) > 0 and "Recycle Bin" not in x, unfiltered_mega_entries.split("\n")))

    # print(f"Mega entries\n{mega_entries}")

    user_pass_list = []

    for mega_entry in mega_entries:
        show_entry_completed_process = run(['keepassxc-cli', 'show', '-s', keepass_file, mega_entry], keepass_password)
        entry_fields = show_entry_completed_process.stdout.decode().split("\n")

        has_cloud_full = 'mrt' in mega_entry
        username = None
        password = None

        for entry_field in entry_fields:
            if ": " not in entry_field:
                continue

            field_name, field_value = entry_field.split(": ", 1)

            if field_name == "UserName":
                username = field_value
            elif field_name == "Password":
                password = field_value

        if username is None or password is None:
            print(f"Entry {mega_entry} does not have username or password")
            continue

        user_pass_list.append((username, password, has_cloud_full))

    mega_login_link = "https://mega.nz/login"
    driver = webdriver.Chrome()
    driver.get(mega_login_link)

    for index, (username, password, has_cloud_full) in enumerate(user_pass_list):
        print(f"[{datetime.datetime.now().isoformat()}] [entry {index + 1}/{len(user_pass_list)}: {username}]: start processing")
        # print(f"Logging in with username: {username} and password: {password}")

        login_input = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
            ec.element_to_be_clickable((By.XPATH, '//*[@id="login-name2"]')))
        password_input = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="login-password2"]')))
        submit_button = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="login_form"]/button')))

        login_input.send_keys(username)
        password_input.send_keys(password)
        submit_button.click()

        create_folder_span = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
            ec.presence_of_element_located((By.XPATH, '//span[contains(text(), "Create folder")]')))

        # test the XPATH in browser by using:
        # document.evaluate("XPATH", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue
        # test the XPATH in browser, through selenium by using:
        # driver.execute_script("""console.log(document.evaluate("XPATH", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue)""")
        # driver.execute_script("console.log('hello')")

        print(f"[{datetime.datetime.now().isoformat()}] [entry {index + 1}/{len(user_pass_list)}: {username}]: found 'Create folder' span")

        if has_cloud_full:
            try:
                drive_full_pop_close_button = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
                    ec.element_to_be_clickable(
                        (By.XPATH, "//div[@aria-label='Storage capacity warning']//button[@aria-label='Close']")))
                drive_full_pop_close_button.click()
            except TimeoutException as e:
                print("Failed to get drive_full_pop_close_button")
                continue

        try:
            avatar = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
                ec.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'js-topbaravatar rendered')]")))
            WebDriverWait(driver, 60).until(ec.invisibility_of_element_located((By.CLASS_NAME, "light-overlay")))
            avatar.click()
        except TimeoutException as e:
            print("Failed to get avatar")
            continue

        try:
            logout = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
                ec.element_to_be_clickable((By.XPATH, "//*[@id='topmenu']//button[contains(text(),'Log')]")))
            logout.click()
        except TimeoutException as e:
            print("Failed to get logout button")
            continue

        try:
            WebDriverWait(driver, 5).until(
                ec.element_to_be_clickable((By.XPATH, '//*[@id="login-name2"]')))
            continue
        except TimeoutException as e:
            # when logout requires password
            try:
                logout_password_input = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
                    ec.element_to_be_clickable((By.XPATH, '//*[@id="test-pass"]')))
                logout_password_input.send_keys(password)
            except TimeoutException as e:
                print("Failed to get logout password input")
                continue

            try:
                confirm_password_button = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
                    ec.presence_of_element_located((By.XPATH, "//button[contains(@class,'button-prd-confirm')]")))
                confirm_password_button.click()
            except TimeoutException as e:
                print("Failed to get confirm password button")
                continue

            try:
                confirm_logout_button = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
                    ec.presence_of_element_located((By.XPATH, "//button[contains(@class,'button-prd-skip')]")))
                confirm_logout_button.click()
            except TimeoutException as e:
                print("Failed to get confirm logout button")
                continue

        print(f"[{datetime.datetime.now().isoformat()}] [entry {index + 1}/{len(user_pass_list)}: {username}]: logged out")
