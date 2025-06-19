# NBA Player Statistics Application

This application, developed with Python using the Kivy framework, provides a user-friendly graphical interface (GUI) to retrieve and analyze NBA player career statistics directly from the official NBA API (`nba_api` library). Users can view statistics for one or multiple players across specific seasons and obtain a general analysis output.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Important Notes](#important-notes)
- [Contributing](#contributing)
- [License](#license)

## Features

* **Player Stats Retrieval:** Dynamically fetches career statistics for a specific NBA player or multiple players directly from the NBA API.
* **Season Filtering:** Ability to query statistics for a single season or a specified range of seasons.
* **Data Analysis:** Provides basic descriptive analyses (mean, maximum values, etc.) and highlights top performances (highest points, assists, rebounds) from the retrieved statistics.
* **User-Friendly Interface:** Easy to use thanks to the intuitive graphical interface developed with Kivy.
* **Responsive Design:** Includes basic responsive adjustments to maintain a tidy layout when the window size changes.
* **Background Processing:** Executes lengthy data retrieval operations in the background (using `threading`) without freezing the user interface.

## Installation

Follow these steps to run the application on your local machine.

### 1. Python Installation

Python 3.x must be installed on your computer. You can install Python from [python.org](https://www.python.org/downloads/) or via a distribution like Anaconda.

### 2. Installing Required Libraries

Open Command Prompt (Windows) or Terminal (macOS/Linux) and navigate to the project directory to install the project dependencies. Run the following command:

```bash
pip install -r requirements.txt
If you face any issues, ensure your requirements.txt file is correctly formatted as follows:

Kivy==2.3.1
kivy-deps.angle==0.4.0
kivy-deps.glew==0.3.1
kivy-deps.sdl2==0.8.0
nba-api==1.10.0
pandas==2.2.2
numpy==1.26.4
3. Cloning the Project (Downloading from GitHub)
If you are downloading the project via GitHub, clone the repository using the following command:

Bash

git clone [https://github.com/Mustafaerdmsahin/NBA_Stats_App.git](https://github.com/Mustafaerdmsahin/NBA_Stats_App.git)
cd NBA_Stats_App
Remember to replace YOUR_USERNAME and NBA_Stats_App with your GitHub username and repository name.

Usage
Navigate to the project directory and run the following command to start the application:

Bash

python nba_app.py
Note: Ensure your main application file is named nba_app.py. If it's named nba_app_stats.py, adjust the command accordingly (e.g., python nba_app_stats.py).

Once the application opens:

In the "Player Name" field, enter the name(s) of the player(s) you wish to query, separated by commas (e.g., Stephen Curry, LeBron James).
In the "Season Range" field, enter a single season (e.g., 2023) or a season range (e.g., 2020-2023).
Click the "Fetch Stats" button.
The application will retrieve the data and display the results in the scrollable area below.

Important Notes
The application requires an active internet connection to fetch data.
The nba_api library may receive updates periodically, or temporary issues with API data retrieval might occur.
This project was developed with the assistance of an artificial intelligence assistant. AI support was specifically utilized in resolving some complex rendering issues within the Kivy interface. This should be explicitly stated as "developed with AI assistance" in accordance with academic integrity guidelines.
Contributing
If you wish to contribute to the project, feel free to open a pull request or report an issue.

License
(No specific license information provided for this project. If you intend to choose a license, please add its details here or link to a separate LICENSE file.)

