# Senior Design Project - Team 312


## Links:

__Files & Notes:__ [SharePoint](https://fsu-my.sharepoint.com/personal/amw21i_fsu_edu/_layouts/15/Doc.aspx?sourcedoc={c8d6e6cb-04f5-4a5c-a4a4-ac70581ecfba}&action=edit&wd=target%28Class%20Handouts.one%7C43749e4e-c570-4688-8d40-703e8b013bf2%2FSenior%20Design%20Projects%7C01b6a98f-3880-41ca-834b-d67c770890d6%2F%29&wdorigin=NavigationUrl)


## Information:

__Accessing the Repo:__

1. Make a github account (Make sure you set your username and email in global config)
2. install _gh_ for github authentication (VNC is a lot easier to use when setting this up on a rpi)
```bash
gh auth login
```
3. Follow steps and log in
4. Verify with:
```bash
gh auth status
```
5. Cloning with HTTP should work now




__RPI Setup:__

* Flash a microSD card with a 64-bit OS w/ RPI imager (ex. debian)

* Select option that initializes SSH while flashing OS

* Initialize ssh & VNC connectivity via:
```bash
sudo raspi-config
```

* Run:
```bash
sudo apt upgrade
```

## Using Git:

* Always make edits in a branch, do not work directly on main. To see what branch is active:
```bash
git branch
```

* To checkout an active branch with name *branchname*:
```bash
git checkout branchname
```

* To create a new working branch:
```bash
git checkout -b nameofbranch
```

* After making changes on a branch, save (commit) the changes by:
```bash
git commit -a -m "brief description of what was done"
```
This saves the changes locally on your computer, to add (push the changes to github)
```bash
git push origin branchname
```


___
__More information:__ [git information](https://git-scm.com/book/en/v2)


## Contributors:
Danielle Awoniyi : danielle1.awoniyi@famu.edu

Amira McKaige : amm21bc@fsu.edu

Amelia Wondracek : amw21i@fsu.edu

Travis Gabauer : tg21b@fsu.edu

Adam Zoiss : aez18@fsu.edu