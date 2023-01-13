import base64
import captcha

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def captcha_solver(CDCWebsite):
    captcha_img = CDCWebsite.driver.find_element_by_id(
        "ctl00_ContentPlaceHolder1_CaptchaImg"
    )

    captcha_base64_string = captcha_img.get_attribute("src")
    with open("captcha_tmp.png", "wb") as fh:
        fh.write(base64.b64decode(captcha_base64_string.split(",")[1]))

    captcha_text = captcha.resolve_3("captcha_tmp.png")
    print(f"captcha text: {captcha_text}")
    captcha_input: WebElement = CDCWebsite.driver.find_element_by_name(
        "ctl00$ContentPlaceHolder1$txtVerificationCode"
    )

    # wait for the popup to appear
    WebDriverWait(CDCWebsite.driver, 5).until(
        EC.element_to_be_clickable(
            (By.ID, "ctl00_ContentPlaceHolder1_txtVerificationCode")
        )
    )
    captcha_input.send_keys(captcha_text)

    # click in submit
    CDCWebsite.driver.find_element_by_name(
        "ctl00$ContentPlaceHolder1$Button1"
    ).click()

    # wait for the popup to appear
    WebDriverWait(CDCWebsite.driver, 5).until(
        EC.element_to_be_clickable(
            (By.ID, "ctl00_ContentPlaceHolder1_txtVerificationCode")
        )
    )
    except Exception:
        traceback.print_exc()

