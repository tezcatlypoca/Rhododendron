import subprocess

def install_requirements(requirements_file):
    with open(requirements_file, "r") as file:
        lines = file.readlines()

    failed_libraries = []
    
    for line in lines:
        library = line.strip()
        if library and not library.startswith("#"):
            print(f"Installing {library}...")
            result = subprocess.run(["pip", "install", library], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Failed to install {library}")
                failed_libraries.append(library)
    
    if failed_libraries:
        print("\nThe following libraries failed to install:")
        for lib in failed_libraries:
            print(lib)
    else:
        print("\nAll libraries installed successfully.")

if __name__ == "__main__":
    install_requirements("./requirements.txt")
