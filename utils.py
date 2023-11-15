import os
from pathlib import Path
from typing import Protocol


class FileContent:
    path: str | None
    content: str | None

    @property
    def file_name(self):
        path = Path(self.path)
        return path.name

    def __init__(self, path: str, content: str):
        self.path = path
        self.content = content


class JoinCallable(Protocol):
    def __call__(self, content: str, join_file: FileContent) -> str:
        ...


class Content:
    files: list[FileContent] = []

    def join(self, join_by: JoinCallable | None = None) -> str:
        if (join_by is not None):
            content = ""
            for file in self.files:
                content = join_by(content=content, join_file=file)

            return content
        else:
            combined_content = [v.content for v in self.files]
            result = '\n'.join(combined_content)
            return result


def get_files_recursively(root_dir: str):
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            # Construct the full path and add it to the list
            file_path = os.path.join(dirpath, filename)
            all_files.append(file_path)
    return all_files


def read_content(source_dirs: list[str], ext: str = ".cs") -> Content:
    # Content result
    result = Content()

    for source_dir in source_dirs:
        # Loop through each file in the directory
        for filename in get_files_recursively(source_dir):
            if filename.endswith(ext):
                # Construct the full file path
                file_path = os.path.join(source_dir, filename)
                # Open and read the file
                with open(file_path, 'r') as file:
                    content = file.read()
                    result.files.append(FileContent(
                        path=file_path,
                        content=content
                    ))

    return result
