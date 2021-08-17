from imdb import IMDbDataAccessError
from pathlib import Path
import os
import time
import shutil
import logging
import renamer as rn

# This will prevent printing errors from other modules
logger = logging.getLogger("imdbpy")
logger.disabled = True

# Getting the terminal size for always printing the results in the middle
col = shutil.get_terminal_size().columns

# All the global Flags
option_4_selected = False
warning_message_shown = False
file_episode_count_not_eq = False
mission_successful = False

# Clear the console
def clearConsole():
    command = "clear"
    # If Machine is running on Windows, use cls
    if os.name in ("nt", "dos"):
        command = "cls"
    os.system(command)


# Assign new the index number from the nenamer.py file
def setIndex():

    try:
        serial = int(input('Enter the "Serial No." of the show you need: '))
    except ValueError:
        error = True
        while error:
            print("\nInvalid Input!...\n")
            serial = input('Enter the "Serial No." of the show you need: ')
            if serial.isdigit():
                error = False
                serial = int(serial)

    rn.index = serial - 1


# Print statements for the Main Menu. Returns a response from the user
def mainMenu():

    global mission_successful

    clearConsole()
    rn.index = 0

    mission_successful = False

    print("||                ~~ MAIN MENU ~~                  ||".center(col))
    print("||               -----------------                 ||".center(col))
    print("|| Press [1] - Rename Anime / TV - Series episodes ||".center(col))
    print("|| Press [2] - Rename General Files                ||".center(col))
    print("|| Press [3] - Exit                                ||".center(col))

    response = input("\nPlease press a valid option: ")
    return response


# Pring statements for the General Menu. This function use the global flag to determine which Menu to show. Returns a response from the user.
def menu():

    # Global Flags
    global option_4_selected, warning_message_shown, file_episode_count_not_eq, mission_successful

    if option_4_selected:

        print("||                  ~ MENU ~                       ||".center(col))
        print("||                 ----------                      ||".center(col))
        print("||  Press [1] - If you've found the show you want  ||".center(col))
        print("||  Press [2] - NEXT show info                     ||".center(col))
        print("||  Press [3] - Previous show info                 ||".center(col))
        print("||  Press [4] - Next 5 show-info at once.          ||".center(col))
        print("||  Press [5] - Search Again                       ||".center(col))
        print("||  Press [6] - Main Menu                          ||".center(col))
        print("||  Press [7] - Exit                               ||".center(col))

        option_4_selected = False

    # Used in response("1") and in rn.init()
    elif warning_message_shown:

        print("||        ~ MENU ~          ||".center(col))
        print("||       ----------         ||".center(col))
        print("|| Press [1] - Search Again ||".center(col))
        print("|| Press [2] - Main Menu    ||".center(col))
        print("|| Press [3] - Exit         ||".center(col))

        warning_message_shown = False

    elif file_episode_count_not_eq:

        print("||        ~ MENU ~          ||".center(col))
        print("||       ----------         ||".center(col))
        print("|| Press [1] - Retry        ||".center(col))
        print("|| Press [2] - Main Menu    ||".center(col))
        print("|| Press [3] - Exit         ||".center(col))

        file_episode_count_not_eq = False

    elif mission_successful:

        print("||                ~ MENU ~                      ||".center(col))
        print("||               ----------                     ||".center(col))
        print("|| Press [1] - Choose Another Season            ||".center(col))
        print("|| Press [2] - Search For Another Series/ Anime ||".center(col))
        print("|| Press [3] - Main Menu                        ||".center(col))
        print("|| Press [4] - Exit                             ||".center(col))

    else:

        print("||                   ~ MENU ~                      ||".center(col))
        print("||                  ----------                     ||".center(col))
        print("||    Press [1] - Confirm                          ||".center(col))
        print("||    Press [2] - NEXT show-info                   ||".center(col))
        print("||    Press [3] - Previous show-info               ||".center(col))
        print("||    Press [4] - Next 5 show-info at once         ||".center(col))
        print("||    Press [5] - Search Again                     ||".center(col))
        print("||    Press [6] - Main Menu                        ||".center(col))
        print("||    Press [7] - Exit                             ||".center(col))

    response = input("\nPlease press a valid option: ")
    return response


# Special Menu for showing after user have selected the season
def episodeMenu():

    print("||                    ~ MENU ~                     ||".center(col))
    print("||                   ----------                    ||".center(col))
    print("||        Press [1] - Confirm                      ||".center(col))
    print("||        Press [2] - Choose Another Season        ||".center(col))
    print("||        Press [3] - Main Menu                    ||".center(col))

    response = input("\nPlease press a valid option: ")
    return response


def chooseAnotherSeasonErrorHandle():
    try:
        season = int(input("\nPlease choose a season: "))

    except ValueError:
        print(
            "\nInvalid Season! Please choose from the available season(s) shown above..."
        )
        season_str = input("\nPlease choose a season: ")

        error = True
        while error:
            if season_str.isdigit():
                season = int(season_str)
                error = False
                break

            print(
                "\nInvalid Season! Please choose from the available season(s) shown above..."
            )

            season_str = input("\nPlease choose a season: ")

    if season not in season_list:

        while season not in season_list:
            print(
                "\nI-Invalid Season! Please choose from the available season(s) shown above..."
            )
            season = chooseAnotherSeasonErrorHandle()
    else:
        return season


def chooseAnotherSeason(season):

    global mission_successful

    season = chooseAnotherSeasonErrorHandle()

    seasonToEpisodes(season)
    episodeMenuResponse(episodeMenu())

    mission_successful = False


# Get additional information on the season and episode list of a show / title using the "episodes" infoset from the IMDbPy server.
def showAvailableSeasons():

    global season_list

    print("\nRetrieving season data please wait...")

    # Getting the episodes using "episodes" infoset form imdb server
    try:
        rn.ia.update(rn.title, "episodes")
    except IMDbDataAccessError:
        print("\nError!: Please try again...")
        exit()

    season_list = list(sorted(rn.title["episodes"].keys()))

    seasons = ""
    for i in season_list:
        # If i is not any "Unknown" season
        if i > 0:
            seasons += "Season " + str(i) + " - "

    seasons = seasons[:-3]

    print(f"\nSeason(s) available : {seasons}")


# After getting the season(s) print the episodes on the console
def seasonToEpisodes(season):

    global episode_names

    season_x = rn.title["episodes"][season]
    print(f"\nTotal Episode(s) count for Season {season}: {len(season_x)}\n")
    print(f"Showing all the season {season} episodes: \n")

    episode_names = []
    for serial, name in season_x.items():
        episode_names.append(name)

        print(f"Episode {serial}: {name}")


# Take the response from the Main Menu and execute according to the user input
def mainMenuResponse(option):

    # Option - Rename Anime / TV - Series episodes
    if option == "1":

        rn.init()
        rn.showInfo(rn.getInfo())
        response(menu())

    # Option - Rename General Files
    elif option == "2":

        print(
            "\nNOTE: Please make sure you've only the file(s) you want to rename in the folder..."
        )
        print(
            "Please remove all unnecessary file type(s) (.srt , .bat, etc...) & check the hidden files or else they'll be also renamed with the other files..."
        )

        general_files = Path(input("\nFolder Path: "))

        if not general_files.exists() or not general_files.is_dir():

            error = True
            print("\nWARNING! : File Path doesn't exist...")

            while error:
                files = Path(input("\nFolder Path: "))

                if files.exists():

                    if files.is_dir():
                        error = False
                    else:
                        print("\nWARNING! : Not a directory...")
                else:
                    print("\nWARNING! : File Path doesn't exist...")

        print("\nNOTE: The files will be rename in this format:\n")
        print('>>> "Title" - "Serial no." || Example - "Python Tutorial - 01.mkv"\n')
        print(
            "If you want to change the format, edith the source code of this script.\n"
        )
        file_title = input("Title of the file(s): ")
        print("")
        sl = 1

        for file in general_files.iterdir():
            if file.is_file() and file.suffix != ".ini":
                directory = file.parent
                file_extension = file.suffix

                new_file_name = f"{file_title} - {sl}{file_extension}"
                sl += 1

                print(new_file_name)
                file.rename(Path(directory, new_file_name))

        print("")
        print("____________________________________________________".center(col))
        print("||                                                ||".center(col))
        print("||   ~~~ Successfully Renamed All The Files! ~~~  ||".center(col))
        print("||                                                ||".center(col))
        print("____________________________________________________".center(col))
        print("")

        time.sleep(4)
        exit()

    # Option - Exit
    elif option == "3":
        clearConsole()
        exit()

    else:
        while option not in ("1", "2", "3"):
            mainMenuResponse(mainMenu())


# Take the response from the General Menu and execute according to the user input
def response(option):

    global option_4_selected, warning_message_shown, season

    # Option - Confirm
    if option == "1":

        # If the title isn't a movie or title has a number of season(s)
        if (
            rn.title.get("kind") != "movie"
            and rn.title.get("number of seasons", "N/A") != "N/A"
        ):

            # get season information and show how many season is available
            showAvailableSeasons()

            season = chooseAnotherSeasonErrorHandle()

            # Take the season no. input from the user and show all the episode names of that season
            seasonToEpisodes(season)
            episodeMenuResponse(episodeMenu())

        else:
            print(
                '\nWARNING! : No season information available for the selected title ("N/A") or The selected title is a movie type\n'.center(
                    col
                )
            )
            warning_message_shown = True

            option = menu()
            if option == "1":
                response("5")
            elif option == "2":
                response("6")
            elif option == "3":
                response("7")
            else:
                while option not in ("1", "2", "3"):
                    print("\nWARNING! : Wrong Input!\n")
                    warning_message_shown = True
                    option = menu()
                    if option == "1":
                        response("5")
                    elif option == "2":
                        response("6")
                    elif option == "3":
                        response("7")

    # Option - Next show info
    elif option == "2":
        # Increment the search index by 1
        rn.index += 1
        # Show the information of the current index
        rn.showInfo(rn.getInfo())
        # Take response for the
        response(menu())

    # Option - Previous show info
    elif option == "3":
        rn.index -= 1
        rn.showInfo(rn.getInfo())
        response(menu())

    # Option - Show 5 show info at once
    elif option == "4":

        # Response option 4 flag is true
        option_4_selected = True

        start = rn.index
        end = rn.index + 5

        for counter in range(start, end):
            rn.showInfo(rn.getInfo())
            rn.index += 1

        # Take user input from menu()
        user_input = menu()
        if user_input == "1":
            # set the index according to the show user choose
            setIndex()
            # Get the informations for the index we just set
            rn.showInfo(rn.getInfo())
            response("1")
        elif user_input in ("2", "3", "4", "5", "6", "7"):
            # For other options call normal response
            response(user_input)
        else:
            while user_input not in ("1", "2", "3", "4", "5", "6", "7"):
                print("\nWARNING! : Wrong Input!\n")

                option_4_selected = True
                user_input = menu()
                if user_input == "1":
                    setIndex()
                    rn.showInfo(rn.getInfo())
                    response("1")
                elif user_input in ("2", "3", "4", "5", "6", "7"):
                    response(user_input)

    # Option - Search Again
    elif option == "5":

        global mission_successful

        clearConsole()
        rn.index = 0

        mission_successful = False

        # This option does the same thing as mainMenuResponse() option - 1
        rn.init()
        rn.showInfo(rn.getInfo())
        response(menu())

    # Option - Back to the main menu
    elif option == "6":
        rn.index = 0
        mainMenuResponse(mainMenu())
        # Program exit because nothing to do

    # Option - Exit the program
    elif option == "7":
        clearConsole()
        exit()

    else:
        while option not in ("1", "2", "3", "4", "5", "6", "7"):
            print("\nWARNING! : Wrong Input!\n")
            response(menu())


# Take the response from the Episode Menu and execute according to the user input
def episodeMenuResponse(option):
    # Option - Confirm
    if option == "1":

        global files

        files = Path(input("\nFolder Path: "))

        if not files.exists() or not files.is_dir():

            error = True
            print("\nWARNING! : File Path doesn't exist...")

            while error:
                files = Path(input("\nFolder Path: "))

                if files.exists():

                    if files.is_dir():
                        error = False
                    else:
                        print("\nWARNING! : Not a directory...")
                else:
                    print("\nWARNING! : File Path doesn't exist...")

        rn.rename(rn.checkFiles(files))

    # Option - Choose another season
    elif option == "2":
        chooseAnotherSeason(chooseAnotherSeasonErrorHandle())

    # Option - Main Menu
    elif option == "3":
        mainMenuResponse(mainMenu())

    else:
        while option not in ("1", "2", "3"):
            print("\nWARNING! : Wrong Input!\n")
            episodeMenuResponse(episodeMenu())
