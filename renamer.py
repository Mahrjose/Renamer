from imdb import IMDb, IMDbDataAccessError
from pathlib import Path
import os
import time
import logging
import urllib.request
import shutil
import navigation as nav


# This will prevent printing errors from other modules
logger = logging.getLogger("imdbpy")
logger.disabled = True

# Getting the terminal size for always printing the results in the middle
col = shutil.get_terminal_size().columns
# This will controll the search result output // which item from the search result list you need
index = 0

# Check if the machine is connected to the internet
def isConnected(host="http://google.com"):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False


# This function initialize the IMDb object and search for a movie / series
def init():

    global ia, search

    ia = IMDb(reraiseExceptions=True)
    search_str = input("\nAnime / TV-series: ")

    while search_str in ("", " ", "  ", "   ", "    "):
        print("\nWARNING! : Please Input Something!")
        search_str = input("\nAnime / TV-series: ")

    try:
        if isConnected():
            search = ia.search_movie(search_str)
        else:
            print(
                "No Internet Connection!!\nPlease check your Internet Connection & try again..."
            )
            exit()

    except IMDbDataAccessError:
        pass

    if len(search) == 0:

        print("\nNo Serach Result found! Check the spelling & search again...\n")

        nav.warning_message_shown = True
        resp = nav.menu()
        if resp == "1":
            nav.response("5")
        elif resp == "2":
            nav.response("6")
        elif resp == "3":
            nav.response("7")
        else:
            while resp not in ("1", "2", "3"):

                print("\nWARNING! : Wrong Input!")
                nav.warning_message_shown = True
                resp = nav.menu()

                if resp == "1":
                    nav.response("5")
                elif resp == "2":
                    nav.response("6")
                elif resp == "3":
                    nav.response("7")

    else:
        print("\nRetrieving data please wait...\n")
        print(f"Total search result(s) : {len(search)}")


# After the search, this function returns a list with all the information of a specific search result
def getInfo():

    global index, serial, ID, title

    # If Index variable is greater than the last index of search
    if index > len(search) - 1:
        # Reset the index variable to 0
        index = 0

    # If index variable is less than first index of search
    elif index < 0:
        # Reset the index variable eq to the last index of search
        index = len(search) - 1

    ID = search[index].movieID
    title = ia.get_movie(ID)

    serial = index + 1

    try:
        info = [
            title.get("title"),
            title.get("kind"),
            title.get("series years", "N/A"),
            title.get("runtime", "N/A")[0],
            title.get("number of seasons", "N/A"),
            title.get("plot", "N/A")[0],
        ]
    except IMDbDataAccessError:
        pass
    except TypeError:
        pass

    # If the show is a movie type
    if title.get("kind") == "movie":
        # Then show the year of release instead of series years.
        info[2] = title.get("year", "N/A")

    # IMDB synopsis string comes with "::" separator (TEXT::Author). We need to split this for geting only the synopsis.
    plot = info[5].split("::")
    info[5] = plot[0]

    if info[3] == "N":
        info[3] = "N/A"

    if info[5] == "N":
        info[5] = "N/A"

    return info


# After getting the information needed, this function will show the information on the console
def showInfo(info):

    # Show the serial number
    print(f"\nSerial: {serial}")
    print(
        f"Title: {info[0]} [ Type: {info[1]} || Year: {info[2]} || Show time: {info[3]} min(s) ]"
    )
    print(f"Number of season(s): {info[4]}")
    print()
    print(f"IMDB URL: https://www.imdb.com/title/tt{ID}/")
    print()
    print(f"Synopsis: {info[5]}")
    print("-" * col)


# This function checks, if a string contains any speciall character which is will prevent from renaming a file (system reserved characters)
def checker(string):
    spec_char = ("\\", "/", "*", ":", "?", ">", "<", "|")

    for char in spec_char:
        if char in string:
            string = string.replace(char, " - ")
        else:
            string = string

    return string


# Check if the path dir/ folder contains any .srt/ subtitle files and returns the total file count in that directory. Also returns the episode count and file path
def checkFiles(files):

    print("\nPreparing to rename the Episode names...\n")

    all_files = []
    subtitle_files = []
    for file in files.iterdir():

        # If not a directory
        if file.is_file() and file.suffix != ".ini":
            all_files.append(file)

            # If the file is a subtitle / .srt file
            if file.suffix == ".srt":
                subtitle_files.append(file)
                subtitle_dir = Path(f"{files}\\Subtitle")

                # If Subtitle directory doesnot exist
                if not (subtitle_dir.exists()):
                    try:
                        subtitle_dir.mkdir(parents=True, exist_ok=False)
                    except FileExistsError:
                        print("File Exist")

                move_path = f"{subtitle_dir}\\{file.stem}{file.suffix}"

                try:
                    os.rename(file, move_path)
                except Exception as error:
                    print(error)
                    exit()

    file_count = len(all_files) - len(subtitle_files)
    episode_num = len(nav.episode_names)

    return files, file_count, episode_num


# Rename the files after checking some conditions
def rename(file_episode_count_tuple):

    files, file_count, episode_num = file_episode_count_tuple

    count = 1

    if file_count != episode_num:
        nav.file_episode_count_not_eq = True

        if file_count > episode_num:
            print(
                f"\nWARNING! : Selected folder has more files ({file_count} files) than total episode number of season {nav.season} ({episode_num} episodes)"
            )
            print(
                "Plaease make sure the total file number is equal to the episode number and Try Again."
            )
            print(
                "\nConsider removing other kinds of files (.txt , .jpg , .mp3 etc..) or other hidden files from the direcotry if it exists\n"
            )

            time.sleep(3)

            option = nav.menu()

            if option == "1":
                rename(checkFiles(nav.files))
            elif option == "2":
                nav.response("6")
            elif option == "3":
                nav.response("7")
            else:
                while option not in ("1", "2", "3"):
                    print("\nWARNING! : Wrong Input!\n")
                    nav.file_episode_count_not_eq = True
                    option = nav.menu()
                    if option == "1":
                        rename(checkFiles(nav.files))
                    elif option == "2":
                        nav.response("6")
                    elif option == "3":
                        nav.response("7")

        else:
            print(
                f"\nWARNING! : Selected folder has less files ({file_count} files) than total episode number of season {nav.season} ({episode_num} episodes)"
            )
            print(
                "Plaease make sure the total file number is equal to the episode number and Try Again.\n"
            )

            time.sleep(3)

            option = nav.menu()

            if option == "1":
                rename(checkFiles(nav.files))
            elif option == "2":
                nav.response("6")
            elif option == "3":
                nav.response("7")
            else:
                while option not in ("1", "2", "3"):
                    print("\nWARNING! : Wrong Input!\n")
                    nav.file_episode_count_not_eq = True
                    option = nav.menu()
                    if option == "1":
                        rename(checkFiles(nav.files))
                    elif option == "2":
                        nav.response("6")
                    elif option == "3":
                        nav.response("7")

    else:
        for file in files.iterdir():
            if file.is_file() and file.suffix != ".ini":

                directory = file.parent
                extension = file.suffix

                try:
                    name_string = nav.episode_names[count - 1]
                except IndexError as error:
                    print(error)
                    exit()

                name_string = str(name_string)
                name_string = checker(name_string)

                # Change this if you want to name your files in a different format
                new_name = f"Episode {count:0>2d} - {name_string}{extension}"
                count += 1

                file.rename(Path(directory, new_name))

        print("____________________________________________________".center(col))
        print("||                                                ||".center(col))
        print("||   ~~~ Successfully Renamed All The Files! ~~~  ||".center(col))
        print("||                                                ||".center(col))
        print("____________________________________________________".center(col))
        print("")

        # Success !!!
        nav.mission_successful = True
        option = nav.menu()

        if option == "1":
            nav.chooseAnotherSeason(nav.chooseAnotherSeasonErrorHandle())
        elif option == "2":
            nav.response("5")
        elif option == "3":
            nav.response("6")
        elif option == "4":
            nav.response("7")

        else:
            while option not in ("1", "2", "3", "4"):
                print("\nWARNING! : Wrong Input!\n")

                nav.mission_successful = True
                option = nav.menu()

                if option == "1":
                    nav.chooseAnotherSeason(nav.chooseAnotherSeasonErrorHandle())
                elif option == "2":
                    nav.response("5")
                elif option == "3":
                    nav.response("6")
                elif option == "4":
                    nav.response("7")


# If the script run directly not as an imported module
if __name__ == "__main__":

    if isConnected():
        nav.mainMenuResponse(nav.mainMenu())
    else:
        print(
            "No Internet Connection!!\nPlease check your Internet Connection & try again..."
        )
