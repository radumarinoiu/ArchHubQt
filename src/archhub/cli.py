from archhub.backends.paru import ParuBackend


if __name__ == "__main__":
    backend = ParuBackend()
    updates = backend.search_aur("vlc")
    print(updates)
