# PyCheckPhish
I wasn't able to find a python tool/lib for Checkphish, so I decided to make my own. 

## References:
- https://checkphish.ai/docs/checkphish-api/#api-introduction - API Documentation
- https://checkphish.ai/checkphish-api/ - You'll need to sign up for a free API key minimally.

## Installation:
```
git clone https://github.com/GitStoph/pycheckphish.git
cd pycheckphish
python3 -m venv venv # create a virtual environment. always.
source venv/bin/activate # activate your venv
python3 -m pip install --upgrade pip # don't be a monster. upgrade your pip
python3 -m pip install --upgrade -r requirements.txt # if you want to try the latest versions of all libs
python3 -m pip install -r requirements.txt # if you want to use what it was originally built with
chmod +x checkphish.py
```

## Get your Keyring set:
```
python3 # to open an interpreter
import keyring
keyring.set_password("checkphish", "apikey", "yourapikeyhere")
quit()
```

## Usage:
```
./checkphish.py -h                                                                                       py pycheckphish 02:18:10 PM
usage: checkphish.py [-h] -u URL [-v [VERBOSE]] [-i [IMAGE]]

Arguments for submitting URLs to Checkphish.ai. Note that if you choose to download/view an image, it is on you to delete it later!

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     What URL should be investigated.
  -v [VERBOSE], --verbose [VERBOSE]
                        Pass this arg to see verbose output while running.
  -i [IMAGE], --image [IMAGE]
                        Pass this arg to download and view a screenshot of the URL that was submitted.
```
Example: `./checkphish.py -u google.com -v -i`

Usage within other scripts:
```
from checkphish import get_checkphish_result
results = get_checkphish_result('https://google.com, suppressprint=True)
```

## Disclaimer:
Of course, CheckPhish isn't perfect. Just because a deposition comes back as clean, does not mean it's safe. Apply good judgement to your query results. 