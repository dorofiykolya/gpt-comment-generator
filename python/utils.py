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
    def __call__(self, content: str, join_file: FileContent) -> (bool, str):
        ...


class JoinedContent:
    files: list[FileContent] = []
    content: str

    def __init__(self, content: str, files: list[FileContent]):
        self.content = content
        self.files = files


class Content:
    files: list[FileContent] = []

    def join(self, join_by: JoinCallable | None = None) -> JoinedContent:
        result: JoinedContent | None
        if (join_by is not None):
            content = ""
            files: list[FileContent] = []
            for file in self.files:
                include, content = join_by(content=content, join_file=file)
                if include:
                    files.append(file)

            result = JoinedContent(
                content=content,
                files=files
            )
        else:
            combined_content = [v.content for v in self.files]
            result = JoinedContent(
                content='\n'.join(combined_content),
                files=self.files[:]
            )

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
