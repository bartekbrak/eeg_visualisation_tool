* How to install and run the project
    cd ~/workspace
    git clone it@bitbucket.org:nausicaaa/eeg_visualisation_tool.git
    cd eeg_visualisation_tool
    mkvirtualenv -a ~/workspace/eeg_visualisation_tool eeg
    pip install -r requirements.txt
    ipython notebook
* Run on iwatch
  while inotifywait -e close_write,moved_to,create -r evt; do evt_standalone; done
  cd evt/static/gauge.js/dist
  while inotifywait -e close_write,moved_to,create -r .; do coffee -c gauge.coffee; done

* Dependencies
  ffprobe (part of ffmpeg), ppa: https://launchpad.net/~mc3man/+archive/ubuntu/trusty-media

        sudo add-apt-repository ppa:mc3man/trusty-media
        sudo apt-get update && sudo apt-get install ffmpeg

* Optional dependencies:
  `apt-get install  inotify-tools`
