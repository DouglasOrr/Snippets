# Manual install of NVIDIA drivers on Ubuntu

```bash
wget -P https://uk.download.nvidia.com/XFree86/Linux-x86_64/440.44/NVIDIA-Linux-x86_64-440.44.run
chmod +x NVIDIA-Linux-x86_64-440.44.run
sudo mv NVIDIA-Linux-x86_64-440.44.run /opt/nvidia

# From a virtual terminal
sudo service lightdm stop
sudo /opt/nvidia/NVIDIA-Linux-x86_64-440.44.run
sudo reboot now
```

## Install nvidia-docker

**TODO**
