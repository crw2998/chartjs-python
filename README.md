## Install
Install `pip` and `npm` if you don't already have them.
```
pip install -r requirements.txt
npm install
npm run build
```
Note that this package requires `Python>=3.6`. Part of the purpose of my writing it was to use some features of Python introduced in 3.5-3.6. It'd be reasonable to port to 3.5 (maybe just removing fancy-style format strings?) but pretty unreasonable to port to 2.7.

## Usage
See `examples.py`.

## Known Issues
* Sometimes the following is printed on puppeteer shutdown: `pyppeteer.errors.NetworkError: Protocol error Target.sendMessageToTarget: Target closed.`. It doesn't look like this is a problem.
* Headless Chromium is entirely untested
* LaTeX rendering doesn't work offline

## Security
Note that using this package's interactive mode in a situation with untrusted network users represents a security risk. An attacker who can access the interface can use the interactive box to execute arbitrary Python (and thus can run `import os; os.system('rm -rf /')` or similar) on your machine.
