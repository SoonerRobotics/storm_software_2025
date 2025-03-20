# storm_software_2025

Software for our 2025 [Student Teleoperated Robotics Mission](https://storm.soonerrobotics.org/) entry, TBD.

We are using [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/) on [Ubuntu 24.04](https://releases.ubuntu.com/24.04/) for the operator, [Boost.Asio](https://www.boost.org/doc/libs/1_87_0/doc/html/boost_asio.html) on [Raspbian Bookworm](https://www.raspberrypi.com/software/operating-systems/) for the robot, and [PlatformIO](https://platformio.org/) for our firmware.

<p align="center">
  <img src="https://raw.githubusercontent.com/SoonerRobotics/storm_software_2025/refs/heads/main/operator/assets/RobotModel.png" alt="alt text" width="400" />
</p>

## Dependencies

### Operator

To set up the dependencies for the operator code, run the following commands.

```bash
python3 -m venv venv
source venv/bin/activate
cd operator
pip install -r requirements.txt
```

### Robot

To set up the dependencies for the robot code, run the following commands.

```bash
sudo apt update
sudo apt install build-essential cmake libboost-all-dev libopencv-dev libqt5core5a libqt5widgets5 libqt5gui5 libgstreamer1.0-0 libavcodec-dev libavformat-dev libswscale-dev libgstreamer-plugins-base1.0-0 libopencv-core-dev libopencv-imgproc-dev libopencv-highgui-dev
```

## Execute
<p align="center">
    <img src="https://raw.githubusercontent.com/SoonerRobotics/storm_software_2025/refs/heads/main/operator/assets/GUI.png" alt="alt text" width="600" />
</p>

### Operator

```bash
python -m venv venv
source venv/bin/activate
cd operator/src
python3 app.py
```

### Robot

The operator code automatically begins the robot's code when it runs via SSH. But, the following commands can run the code on their own.

#### Automated 
```bash
./launch.sh # 1: Build, 2: Run, 3: Build/Run/Clean, 4: Clean
```

#### Manual
```bash
cd robot
mkdir build && cd build
cmake ..
make
./robot
```
