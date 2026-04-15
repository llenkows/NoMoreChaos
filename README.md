
**No More Chaos** is a standalone Windows application designed to organize your daily tasks, media consumption, and sports schedule into one unified dashboard. It replaces scattered lists and browser tabs with a clean, dark-mode desktop application.

---

## ✨ Features

### The Home Dashboard
The Home page summarizes all of your tasks for the day. Once a day, it randomly selects one focus topic, one album, and one movie for you to tackle.

### Job Tracker
Keep a running log of your job applications. Track the company, role, and current application status. The Home dashboard will remind you every day to log at least one new application.

### Focus Topics (Video Ideas)
Manage a queue of video ideas or gaming backlogs. 
* Rank topics by "Strength Score" and "Time to Beat."
* Supports **Single Game** or **Multi-Game** projects.
* Automatically syncs subtopic progress to the parent project.

### Music Queue & Rating (Spotify Integration)
* Search the entire Spotify catalog directly from the app.
* Add albums to a listening queue.
* Rate albums track-by-track, calculating a weighted average score, and save them to your library.

### Movie Watchlist (TMDB Integration)
* Search the TMDB database to add movies to your Letterboxd watchlist. Simply export your watchlist to a `.csv` file and import it back into the app.
* Pulls in official posters, runtimes, and community ratings.
* Filter your backlog by "Shortest Runtime," "Highest Rated," or let the app pick a random movie for you.

### Sports Calendar (ESPN Integration)
* Fetches a rolling 7-day schedule for the NFL, NBA, MLB, NHL, and MLS.
* Automatically filters out the noise, specifically isolating Playoff games, Play-In tournaments, and configured hometown teams.
* **Desktop Notifications:** If the app is minimized to the system tray, it will send a native Windows notification 15 minutes before your games start.

### Auto-Backups & System Tray
* Hides cleanly in the Windows System Tray to keep your taskbar clear.
* **Failsafe Data:** Whenever you fully close the app, it automatically exports your entire database into readable `.csv` files stored safely in your `Documents/NoMoreChaos/Backups` folder.

---

## How to Download & Run

**No More Chaos** is packaged as a standalone Windows executable. Head to the releases page to download the latest version.

### 1. Download the App
1. Go to the [Releases page](https://github.com/llenkows/NoMoreChaos/releases) on this GitHub repository.
2. Download the latest version of the exe and run it.

### 2. Add Your API Keys (One-Time Setup) 
### (TO BE ADDED IN NEXT RELEASE)
To enable the Movie and Music search features, the app needs to connect to TMDB and Spotify. 
1. Open the folder you just downloaded.
2. Create a new text file and name it exactly **`.env`** (make sure it doesn't save as `.env.txt`).
3. Paste your API keys inside like this: