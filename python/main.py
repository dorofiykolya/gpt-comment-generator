from asyncio import Task

import openai
import os
import sys
import dotenv
import tiktoken

import utils
import asyncio

# load .env
dotenv.load_dotenv()

# get env
GPT_API = os.getenv("GPT_API") or os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL") or "gpt-4-1106-preview"
ROOT_DIR = os.getenv("ROOT_DIR") or None
SOURCE_DIRS = os.getenv("SOURCE_DIRS")

if (
        ROOT_DIR is not None
        and ROOT_DIR != ""
        and SOURCE_DIRS is not None
        and SOURCE_DIRS != ""
):
    SOURCES = [s.strip() for s in SOURCE_DIRS.split(",")]
    NEW_SOURCES = []
    for SOURCE in SOURCES:
        NEW_SOURCES.append(os.path.join(ROOT_DIR.strip(), SOURCE))
    SOURCE_DIRS = ",".join(NEW_SOURCES)

# source dir from SOURCE_DIR or use second argument
source = [s.strip() for s in (SOURCE_DIRS if len(sys.argv) == 1 else sys.argv[1]).split(",")]

# read content
source_content = utils.read_content(source)


# custom join files
def join_cs(content: str, join_file: utils.FileContent) -> (bool, str):
    # return f"{content}\n{join_file.content}"
    file_content = join_file.content

    REMOVE_DOUBLE_SPACE = False

    if REMOVE_DOUBLE_SPACE:
        while "  " in file_content:
            file_content = file_content.replace("  ", " ")

    return True, f"{content}\n<BEGIN file={join_file.file_name}>\n{file_content}\n<END>\n"


# joined code
joined_content = source_content.join(join_cs)

client = openai.AsyncClient()


async def generate(file_name: str, code: str):
    
    tokenizer = tiktoken.get_encoding("cl100k_base")
    print(f'Input tokens count: {len(tokenizer.encode(code))} {file_name}')
    
    completion = await client.chat.completions.create(
        model=GPT_MODEL,
        temperature=0,
        max_tokens=8000,
        messages=[
            {
                "role": "system",
                "content":
                    f"""You are a comment and documentation generator for different types of programming code. 
                    You will be provided a concatenated code from all project's source files.
                    You must analyze each given class and method and define relationships between them. 
                    Based on analyzed info, you must create comments that suits programming language of the given class or method.
                    You must strictly follow general comment and documentation rules for given programming language.
                    Remember to indicate method or class main purpose and variables in your comments.
                    You must also add comments inside methods in order to explain main logic better with details and DO NOT OMMIT for brevity.
                    Do NOT change original code, add comments ONLY.
                    Write CODE ONLY.
                    CODE:
                    {code}
                    """
            },
            {
                "role": "user",
                "content": f"Rewrite file: {file_name}"
            }
        ]
    )
    result = completion.choices[0].message.content
    result = result.removeprefix("```csharp")
    result = result.removesuffix("```")
    print(f">>> {file_name}\n{result}\n>>>\n")


loop = asyncio.get_event_loop()


async def run_async():
    tasks: list[Task] = []
    for file in joined_content.files:
        tasks.append(
            loop.create_task(
                generate(file.file_name, joined_content.content)
            )
        )
    await asyncio.wait(tasks)


loop.run_until_complete(run_async())
loop.close()
