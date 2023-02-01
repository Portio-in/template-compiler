from dotenv import load_dotenv
import os
from compiler import TemplateCompiler

load_dotenv()
domain_name = "tanmoy.portio.in"
compiler = TemplateCompiler("dopefolio", domain_name)
compiler.configAWS(os.environ.get("ACCESS_KEY_ID"), os.environ.get("ACCESS_KEY_SECRET"))
compiler.run()
compiler.storeTemplateToS3()