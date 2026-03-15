
import json
from archhub.backends.paru import ParuBackend
from archhub.backends.pacman import PacmanBackend
from archhub.core.aur_rpc import get_package_info
from archhub.core.runner import run

if __name__ == "__main__":
    pacman_backend = PacmanBackend()
    paru_backend = ParuBackend()
    assert len(pacman_backend.get_installed()) > len(paru_backend.get_installed())
    
    search_term = "vlc"
    assert len(pacman_backend.search(search_term)) > len(paru_backend.search(search_term))

    r = run(["paru", "-Sy"])

    package_details = pacman_backend.get_package_details("git")
    print(package_details)

    package_details = paru_backend.get_package_details("vlc-git")
    print(package_details)

    updates = pacman_backend.get_updates()
    print(updates)

    updates = paru_backend.get_updates()
    print(updates)