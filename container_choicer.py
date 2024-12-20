import os
from typing import List
from container import ContainerData, CONTAINER_FILE
from directory import Directory
from helpers.choicer_list import ChoicerList


def is_folder_container(folder: str) -> bool:
    return os.path.isdir(folder)


class ContainerChoicer:

    @classmethod
    def choice_named(cls, folder: str):
        # Указываем путь к каталогу, который хотим исследовать
        folders = Directory(folder).get_subdirectories()
        containers = []
        for container_folder in folders:
            if Directory(folder).join_path(container_folder).file_exists(CONTAINER_FILE):
                containers.append(container_folder)
            elif Directory(folder).join_path(container_folder).file_exists('nested'):
                containers.append(container_folder)
        if len(containers) == 0:
            return []

        selected_items = ChoicerList(containers).name('контейнеров').choose_multi()
        # Выводим выбранные элементы
        print(f'Ваши выборы: "{', '.join(selected_items)}"')

        return selected_items

    @classmethod
    def exists_containers(cls, folder: str) -> bool:
        explorer = Directory(folder)
        containers = explorer.get_subdirectories()
        if not containers:
            return False
        else:
            return True

    @classmethod
    def choice_file(cls, folder: str) -> List[ContainerData]:
        # print('choice_file_containers', folder)
        explorer = Directory(os.path.realpath(folder))
        container_exists = []
        for container in ContainerChoicer.choice_named(folder):
            if explorer.file_exists(CONTAINER_FILE, container):
                container_exists.append(
                    ContainerData(
                        container,
                        explorer.get_path(container)
                    )
                )
            elif ContainerChoicer.exists_containers(f'{folder}/{container}'):
                print(f'Блок "{container}" имеет внутренние деления')
                sup_containers = ContainerChoicer.choice_file(f'{folder}/{container}')
                container_exists = container_exists + sup_containers
            else:
                print(f'Блок "{container}" не имеет внутренних делений')
        return container_exists
