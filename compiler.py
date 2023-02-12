from jinja2 import Environment, PackageLoader, select_autoescape
import requests
import htmlmin
import os
import json
import shutil
from datetime import datetime
import boto3
from io import BytesIO
from dotenv import load_dotenv
from helper import datetimeStringTodate
from pymemcache.client import base

template_path_store = {
    "dopefolio": "dopefolio",
    "devfolio": "devfolio",
    "resume": "resume"
}

template_helpers = {
    "datetimeStringTodate": datetimeStringTodate
}


def formatDate(date):
    if date is None:
        return "Present"
    return str(datetime.strptime(date.split("T")[0], "%Y-%m-%d").strftime("%d/%m/%Y"))


class TemplateCompiler:
    def __init__(self, template_code: str, domain_name: str) -> None:
        self.template_code = template_code
        self.domain_name = domain_name
        self.env = Environment(
            loader=PackageLoader(template_path_store[template_code], package_path="."),
            autoescape=select_autoescape()
        )
        self.env.globals.update(formatDate=formatDate)
        self.config = {}
        self.template_files = []
        self.template_ignore_files = ["config.json"]
        self.data = {}
        self.generated_templates = {}
        self.aws_access_key = ""
        self.aws_access_secret = ""

    def run(self):
        self._loadConfig()
        self._excludeMultiPageElements()
        profileFetchSuccessful, self.data = self._fetchProfile()
        if not profileFetchSuccessful:
            return
        self.findTemplateFiles()
        self.compileTemplates()

    def _loadConfig(self):
        path = os.path.join(template_path_store[self.template_code], "config.json")
        with open(path, "r") as f:
            self.config = json.load(f)

    def _excludeMultiPageElements(self):
        multi_page_elements = self.config["multi_page_elements"]
        for record in multi_page_elements:
            if record["file_name"] not in self.template_ignore_files:
                self.template_ignore_files.append(record["file_name"])

    def configAWS(self, aws_access_key, aws_access_secret):
        self.aws_access_key = aws_access_key
        self.aws_access_secret = aws_access_secret

    def findTemplateFiles(self):
        all_template_files = self.env.list_templates()
        templates_files = []
        for template_file in all_template_files:
            if not (template_file.startswith("base") or template_file.startswith(
                    "partials") or template_file.startswith("ignoreme") or template_file in self.template_ignore_files):
                templates_files.append(template_file)
        self.template_files = templates_files

    def compileTemplates(self):
        # Compile normal template files
        for template_file in self.template_files:
            template = self.env.get_template(template_file)
            html = template.render(**self.data, **template_helpers)
            html = htmlmin.minify(html, remove_empty_space=True)
            self.generated_templates[template_file] = html
        # Compile multi page template files
        multi_page_elements = self.config["multi_page_elements"]
        for record in multi_page_elements:
            json_key = record["json_key"]
            template_file = record["file_name"]
            specific_record_key = record["specific_record_key"]
            folder_name = template_file.split(".")[0]
            template = self.env.get_template(template_file)
            for index, specific_record in enumerate(self.data[json_key]):
                html = template.render(**self.data, **{specific_record_key: specific_record}, **template_helpers)
                html = htmlmin.minify(html, remove_empty_space=True)
                self.generated_templates[f"{folder_name}/{index}.html"] = html

    def _fetchProfile(self):
        try:
            response = requests.get(f"https://api.portio.in/profile.json?domain={self.domain_name}")
            json_response = response.json()
            return True, json_response
        except:
            return False, {}
        
    def purgeCache(self):
        client = base.Client(('localhost', 11211))
        for template_file, _ in self.generated_templates.items():
            path = os.path.join(self.domain_name, template_file)
            client.delete(path)
            
    def storeTemplates(self):
        # random_id = str(uuid4())
        random_id = "tanmoy"
        try:
            shutil.rmtree(random_id)
        except:
            pass
        os.mkdir(random_id)
        for template_file, html in self.generated_templates.items():
            path = os.path.join(random_id, template_file)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(html)

    def storeTemplateToS3(self, buckerName):

        s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_access_secret
        )
        for template_file, html in self.generated_templates.items():
            s3.upload_fileobj(BytesIO(html.encode("utf-8")), buckerName, os.path.join(self.domain_name, template_file))


if __name__ == "__main__":
    load_dotenv()
    template_compiler = TemplateCompiler("resume", "tanmoy.portio.in")
    template_compiler.run()
    template_compiler.storeTemplates()