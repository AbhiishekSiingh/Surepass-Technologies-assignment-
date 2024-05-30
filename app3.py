import requests
from lxml import html
import json
from PIL import Image
from io import BytesIO

class ParivahanScraper:
    def __init__(self):
        self.base_url = 'https://parivahan.gov.in'
        self.session = requests.Session()

    def fetch(self, url):
        response = self.session.get(url)
        response.raise_for_status()
        return response.content

    def parse(self, content):
        return html.fromstring(content)

    def get_data(self):
        url = f"{self.base_url}/rcdlstatus/?pur_cd=101"
        content = self.fetch(url)
        tree = self.parse(content)

        # Print the HTML content for debugging
        print(html.tostring(tree, pretty_print=True).decode())

        captcha_img_elements = tree.xpath('//img[contains(@id, "form_rcdl:j_idt")]/@src')
        if not captcha_img_elements:
            print("CAPTCHA image URL not found.")
            return None

        captcha_url = self.base_url + captcha_img_elements[0]
        captcha_response = self.session.get(captcha_url)
        captcha_image = Image.open(BytesIO(captcha_response.content))
        captcha_image.show()

        captcha_value = input("Enter CAPTCHA value: ")
        form_data = {
            'form_rcdl:tf_dlNO': 'MH0320140015542',
            'form_rcdl:tf_dob_input': '21-06-1992',
            'form_rcdl:j_idt34:CaptchaID': captcha_value,
            'javax.faces.ViewState': tree.xpath('//input[@name="javax.faces.ViewState"]/@value')[0],
            'form_rcdl': 'form_rcdl',
            'form_rcdl:j_idt40': 'Check Status'
        }
        form_url = f"{self.base_url}/rcdlstatus/?pur_cd=101"
        response = self.session.post(form_url, data=form_data)
        response.raise_for_status()
        tree = self.parse(response.content)
        data = self.extract_data(tree)
        return data

    def extract_data(self, tree):
        data = {
            "DL Status": tree.xpath('//div[@id="form_rcdl:j_idt63"]//table//tr//td//text()')
        }
        data["DL Status"] = [text.strip() for text in data["DL Status"] if text.strip()]

        return data

    def save_to_json(self, data, filename):
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data saved to {filename}")

if __name__ == "__main__":
    scraper = ParivahanScraper()
    data = scraper.get_data()
    if data:
        print(data)
        scraper.save_to_json(data, 'scraped_data.json')
