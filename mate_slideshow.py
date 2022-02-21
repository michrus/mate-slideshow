import argparse
import shutil
import sys
from typing import Any, Iterable, Tuple
from pathlib import Path


USR_BACKGROUNDS_PATH = Path('/usr/share/backgrounds/')


def main() -> int:
    arguments = parse_arguments()
    images_directory_name = arguments.directory_name or \
        arguments.images_directory_path.name
    target_directory_path = Path(USR_BACKGROUNDS_PATH, images_directory_name)
    # Create subdirectory in /usr/share/backgrounds/
    print(f'[INFO] Creating {target_directory_path}')
    Path(target_directory_path).mkdir(
        parents=True,
        exist_ok=True)
    # Create xml file
    print(f'[INFO] Creating xml file in {arguments.images_directory_path}')
    create_xml_file(arguments.images_directory_path,
                    arguments.image_duration,
                    arguments.transition_duration,
                    target_directory_path)
    # Copy files to subdirectory in /usr/share/backgrounds/
    print(f'[INFO] Copying images to {target_directory_path}')
    for image_path in arguments.images_directory_path.glob("*"):
        target_path = target_directory_path / image_path.name
        shutil.copy(str(image_path), str(target_path))
    print('[INFO] Done.')

    return 0


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Create xml file for background slideshow.'
    )
    parser.add_argument('-i',
                        type=Path,
                        dest='images_directory_path',
                        required=True,
                        help='Path to directory containing slideshow images',
                        )
    parser.add_argument('-d',
                        type=int,
                        dest='image_duration',
                        required=True,
                        help='Single image duration in minutes.')
    parser.add_argument('-t',
                        type=int,
                        dest='transition_duration',
                        required=True,
                        help='Transition duration duration in seconds.')
    parser.add_argument('-n',
                        type=str,
                        dest='directory_name',
                        required=False,
                        help='Optional directory name overload for '
                             f'directory in {USR_BACKGROUNDS_PATH}')
    arguments = parser.parse_args()

    # Validation
    if not Path.is_dir(arguments.images_directory_path):
        raise ImageDirectoryPathError(arguments.images_directory_path)
    if arguments.image_duration <= 0:
        raise ImageDurationError(arguments.image_duration)
    if arguments.transition_duration < 0:
        raise TransitionDurationError(arguments.transition_duration)

    return arguments


def create_xml_file(images_directory_path: Path,
                    image_duration: int,
                    transition_duration: int,
                    target_directory_path: Path) -> None:
    # Initial xml section
    xml_content = [
        '<background>\n',
        '-\n',
        '<starttime>\n',
        '<year>2009</year>\n'
        '<month>08</month>\n',
        '<day>04</day>\n',
        '<hour>00</hour>\n',
        '<minute>00</minute>\n',
        '<second>00</second>\n',
        '</starttime>\n'
    ]

    extensions = ['jpg', 'jpeg', 'png']
    # Xml sections for image transition
    for image_path, next_image_path in \
            pair_elements(glob_all_extensions(images_directory_path,
                                              extensions)):
        image_xml = [
            '-\n',
            '<static>\n',
            f'<duration>{image_duration * 60.0}</duration>\n',
            f'<file>{target_directory_path / image_path.name}</file>\n',
            '</static>\n',
            '-\n',
            '<transition>\n',
            f'<duration>{transition_duration}</duration>\n',
            f'<from>{target_directory_path / image_path.name}</from>\n',
            f'<to>{target_directory_path / next_image_path.name}</to>\n',
            '</transition>\n'
        ]
        xml_content.extend(image_xml)
    xml_content.append('</background>\n')
    # Write xml file
    xml_file_path = target_directory_path / \
        (target_directory_path.name + '.xml')
    with open(xml_file_path, 'w') as xml_file:
        xml_file.writelines(xml_content)


def glob_all_extensions(path: Path, extensions: list) -> list:
    all_files = []
    for file_extension in extensions:
        all_files.extend(path.glob(f'*.{file_extension}'))
    return all_files


def pair_elements(elements: Iterable) -> Iterable[Tuple[Any, Any]]:
    elements_len = len(elements)
    for item_index in range(0, elements_len):
        next_item_index = item_index + 1 if \
            item_index < elements_len - 1 else 0
        yield elements[item_index], elements[next_item_index]


class ImageDirectoryPathError(Exception):
    def __init__(self, path):
        self.message = 'Given path is not directory or does not exist! ' \
                       f'Path: {path}'
        super().__init__(self.message)


class ImageDurationError(Exception):
    def __init__(self, duration):
        self.message = 'Image duration must be greater than 0.' \
                       f'Given duration: {duration} minutes.'
        super().__init__(self.message)


class TransitionDurationError(Exception):
    def __init__(self, duration):
        self.message = 'Image transition duration can\'t be less than 0.' \
                       f'Given duration: {duration} minutes.'
        super().__init__(self.message)


if __name__ == "__main__":
    sys.exit(main())
