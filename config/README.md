# Setup notes

## General

```bash
apt install git emacs-nox tree htop bmon net-tools powertop mosh jq python3-pip
```

Copy config from this project:

```bash
cp .emacs .gitconfig ~
cp flake8 ~/.config/
sudo cp bin/* /usr/local/bin  # you might want to be specific
# manually merge `.bashrc`
```

After starting emacs, run `M-x package-install-selected-packages`.

## Desktop

Manual install:
 - Google Chrome
 - Android Studio
 - Docker (Engine)

Run `ssh-keygen` & add private key to GitHub.

```bash
apt install fonts-inconsolata gimp vlc
```

### Desktop tweaks

When Ubuntu insists on grouping windows in the app switcher...

 - Gnome
   - `gnome-tweak-tool`
   - `dconf-editor`
   - `gsettings set org.gnome.shell.app-switcher current-workspace-only true`
   - Use `dconf-editor` to change `<Alt>Tab` from `switch-applications` to `cycle-windows` (and similar for `<Alt><Shift>Tab`)
 - Unity
   - `compizconfig-settings-manager`
   - `compiz-plugins` (so we can change the app switcher)
   - Use `compizconfig-settings-manager` to select the static app switcher
