Question 1: Observe the files created, what do you think they contain:
uv init initializes the Python project and creates the basic project files. The pyproject.toml file contains the project's configuration, such as its name, Python version requirements, and dependencies. The .python-version file specifies the Python version used by the project, while README.md contains basic project documentation. The uv.lock file records the exact versions of the project's dependencies to help make the environment reproducible. The .venv directory contains the local Python virtual environment and the installed packages

Question 2: What are the created files. What do you think they are used for? And which ones should be pushed to git?
dvc init creates the .dvc directory, which contains DVC's configuration and internal files needed for the repository to work with DVC. It also creates .dvcignore, which specifies files or directories that DVC should ignore when tracking data. These files are part of the project's DVC setup. They should be pushed to Git because Git stores the DVC configuration and metadata needed to reproduce the project, while the actual large datasets are stored by DVC in the remote storage.

Question 3: Where are the credentials stored? and what are the options other than --global? Should the credentials be pushed to github?
I used --local instead of --global (the flag DagsHub's own UI generated for me), since it's the safer option.
With --local, the credentials are saved in .dvc/config.local, a file scoped to just this one repository. Checking .dvc/.gitignore confirms /config.local is listed there — meaning git will never track or push this file. It stays only on my local machine.
If --global had been used instead, the credentials would go into a user-level config file outside any project folder (e.g. %USERPROFILE%\.dvc\config on Windows), applying to every DVC project on that machine rather than just this one.
--local: scoped to this repo only, stored in .dvc/config.local, automatically git-ignored (what I used).
No flag at all: writes to the shared .dvc/config file — the one version of the config that does get committed to git.
No. Credentials should never be committed to git, since anyone with access to the repo could see them. Using --local (or --global) keeps the secret token out of .dvc/config, which is the only config file that actually gets shared via git. Running the commands with no flag at all would be the risky choice, since it would put the token directly into the shared, git-tracked config file.

Question 4: Take a look at the .gitignore file. Explain what happened.
Before dvc add data, your .gitignore only had whatever DVC's own boilerplate needed. After running dvc add data, DVC automatically appends a new line to .gitignore:
/data
This tells git to completely ignore the data folder from now on. It happens because DVC is now the one responsible for tracking the actual contents of data — git should never try to track those files directly (they're huge binary image files, exactly what git is bad at handling). This is DVC automatically enforcing the separation of concerns described in the lab: git tracks code + pointers, DVC tracks data.

Question 5: Do you see a .dvc file? What does it contain?
Yes — dvc add data creates a file called data.dvc in your project root (note: this is different from the .dvc/ folder made by dvc init — this is a single small text file named after what you tracked).
data.dvc is a plain YAML file containing something like:
yaml
outs:
- md5: <hash>
  size: <bytes>
  path: data
It stores:
A hash (checksum) representing the exact content of the entire data folder at this point in time — if even one byte in one image changes, this hash changes
The size of the tracked data
The path it corresponds to (data)

This data.dvc file is essentially a receipt/pointer: it doesn't contain the actual images, just a fingerprint of them. Git tracks this small file instead of the real data — that's how a tiny text file in your git history can represent gigabytes of images living elsewhere (in DVC's cache and on DagsHub).

Question 6: You can check your main branch on the github web UI. Is the code there? Is the data there? Do you have any file that points to the data location. And what about dagshub web UI do you see the data?
On GitHub, the code is present (pyproject.toml, src/, .dvc/, .dvcignore, .gitignore, etc.), along with data.dvc — the small pointer file representing the tracked data. The actual data folder (the images) is not present on GitHub, since git only tracks the pointer, never the real files.
I initially configured DagsHub as my DVC remote, but ran into repeated upload failures ("Server disconnected") when pushing ~1.1GB / 16,643 files — a known issue our instructor confirmed the class encountered. Per their guidance, I switched to Option 1: a local remote instead — I added a second DVC remote (local_storage) pointing to a folder on my own machine (C:\Users\USER\Desktop\3em-Anne sem1\mlops\dvc_storage, outside the git repo) and set it as default. So in my case, DagsHub does not contain the pushed data — the actual data content lives in that local storage folder instead.

Question 7: In a completely new temporary folder clone your github repo. Do you see the data folder? What dvc command is needed to get the data folder?
After cloning the GitHub repo into a fresh temporary folder, the data folder does not exist — only data.dvc (the pointer) comes down with git clone, confirmed directly (dir data → "File Not Found").
To retrieve the actual data, the command needed is dvc pull (run as uv run dvc pull in my setup). This reads data.dvc, matches its hash against the configured remote, and downloads the real files — in my case pulling from my local dvc_storage folder rather than DagsHub, since that's the remote I set as default after the DagsHub upload issues.

Question 8: Do you still see the new folders you created? food11_processed and food11_processed_mini?
No — after running git checkout <old-commit-hash> followed by dvc checkout, the food11_processed and food11_processed_mini folders disappear from the data directory. Only food11_raw remains, because that older commit's data.dvc file only points to the version of the data that existed before the processing script was run and the processed folders were added and tracked.
This demonstrates that git and DVC move in lockstep: checking out an older git commit rolls back data.dvc to whatever it pointed to at that point in history, and dvc checkout then updates the actual data/ folder on disk to match that pointer — effectively "rewinding" both code and data together.
Running git checkout main followed by dvc checkout again afterward restores the working directory to the latest state, bringing food11_processed and food11_processed_mini back.
