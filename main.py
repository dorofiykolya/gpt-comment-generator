import openai
import os
import sys
import dotenv
import utils

# load .env
dotenv.load_dotenv()

# get env
GPT_API = os.getenv("GPT_API") or os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL") or "gpt-4-1106-preview"
SOURCE_DIR = os.getenv("SOURCE_DIR")

# source dir from SOURCE_DIR or use second argument
source = SOURCE_DIR if len(sys.argv) == 1 else sys.argv[1]

# read content
source_content = utils.read_content(source)


# custom join files
def join_cs(content: str, join_file: utils.FileContent) -> str:
    return f"{content}\n{join_file.content}"
    # return f"{content}\nBEGIN: {join_file.file_name}\n{join_file.content}\nEND: {join_file.file_name}\n"


# joined code
code = source_content.join(join_cs)

client = openai.OpenAI()

completion = client.chat.completions.create(
    model=GPT_MODEL,
    messages=[
        {
            "role": "system",
            "content":
                """You are a comment and documentation generator for different types of programming code. 
                You will be provided a concatenated code from all project's source files.
                You must analyze each given class and method and define relationships between them. 
                Based on analyzed info, you must create comments that suits programming language of the given class or method.
                ALSO you must strictly follow general comment and documentation rules for given programming language.
                Remember to indicate method or class main purpose and variables in your comments."""
        },
        {
            "role": "user",
            "content": code
        }
    ]
)

print(completion.choices[0].message)
