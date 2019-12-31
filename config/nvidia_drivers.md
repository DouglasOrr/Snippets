# Manual install of NVIDIA drivers on Ubuntu

Find the latest version from [NVIDIA Driver Downloads](https://www.nvidia.co.uk/Download/index.aspx).

```bash
wget https://uk.download.nvidia.com/XFree86/Linux-x86_64/440.44/NVIDIA-Linux-x86_64-440.44.run
chmod +x NVIDIA-Linux-x86_64-440.44.run
sudo mv NVIDIA-Linux-x86_64-440.44.run /opt/nvidia

# From a virtual terminal
sudo nvidia-uninstall
sudo reboot now
sudo service lightdm stop
sudo /opt/nvidia/NVIDIA-Linux-x86_64-440.44.run
sudo reboot now
```
