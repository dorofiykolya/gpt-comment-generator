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
                """You are comment and documentation generator. 
                User provide you concatenated code from source files.
                You have to understand and generate comment with examples for each method"""
        },
        {
            "role": "user",
            "content": code
        }
    ]
)

print(completion.choices[0].message)
