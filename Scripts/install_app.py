import PyInstaller.__main__
import shutil


def main():
    print("Install App")
    PyInstaller.__main__.run(['main.py', '--onefile', '--windowed', '--icon=.\Assets\chef-hat.png' ])

    print("Copy app executable file to main directory")
    shutil.copyfile("./dist/main.exe", "./Restaurant Rating Predictor.exe")


if __name__ == '__main__':
    main()
