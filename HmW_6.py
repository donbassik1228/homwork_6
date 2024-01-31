from pathlib import Path
import shutil
import re
import sys

def get_extensions(file_name):
    return Path(file_name).suffix[1:].split('.')[0].upper()

def scan(folder, IMAGES, DOCS, VIDEO, MUSIC, ARCHIVES, OTHER, Folders, Unknown, Extensions):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('Images', 'Video', 'Docs', 'Music', 'Archive', 'Other'):
                Folders.append(item)
                scan(item, IMAGES, DOCS, VIDEO, MUSIC, ARCHIVES, OTHER, Folders, Unknown, Extensions)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder / item.name
        if not extension:
            OTHER.append(new_name)
        else:
            try:
                container = registered_extensions[extension]
                Extensions.add(extension)
                container.append(new_name)
            except KeyError:
                Unknown.add(extension)
                OTHER.append(new_name)

def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}"

def handle_file(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder / normalize(path.name))

def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.name.replace(".zip", ''))

    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except (shutil.ReadError, FileNotFoundError):
        archive_folder.rmdir()
        return
    path.unlink()

def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <folder_path>")
        sys.exit(1)

    folder_path = Path(sys.argv[1])
    print(folder_path)
    folder_path = Path(sys.argv[1])
    print(folder_path)

    IMAGES, DOCS, VIDEO, MUSIC, ARCHIVES, OTHER, Folders, Unknown, Extensions = [], [], [], [], [], [], [], set(), set()

    scan(folder_path, IMAGES, DOCS, VIDEO, MUSIC, ARCHIVES, OTHER, Folders, Unknown, Extensions)

    for file in IMAGES:
        handle_file(file, folder_path, "Images")

    for file in VIDEO:
        handle_file(file, folder_path, "Video")

    for file in DOCS:
        handle_file(file, folder_path, "Docs")

    for file in MUSIC:
        handle_file(file, folder_path, "Music")

    for file in OTHER:
        handle_file(file, folder_path, "Other")

    for file in ARCHIVES:
        handle_archive(file, folder_path, "Archive")

    remove_empty_folders(folder_path)

if __name__ == '__main__':
    main()
