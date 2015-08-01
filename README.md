* How to install and run the project
    cd ~/workspace
    git clone it@bitbucket.org:nausicaaa/eeg_visualisation_tool.git
    cd eeg_visualisation_tool
    mkvirtualenv -a ~/workspace/eeg_visualisation_tool eeg
    pip install -r requirements.txt
    ipython notebook
* Run on iwatch
  while inotifywait -e close_write,moved_to,create -r evt; do evt_standalone; done
