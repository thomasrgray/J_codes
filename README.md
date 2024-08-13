# Running `blech_lab` Codes on Jetson Nano

## Overview
This repository contains instructions and scripts for setting up and running `blech_lab` codes on a Jetson Nano. The `blech_lab` suite includes various tools for neural data analysis, which are optimized here for the Jetson Nano’s ARM-based architecture and GPU capabilities.

## Features
- **GPU Acceleration**: Leverages the Jetson Nano's GPU for faster data processing and analysis.
- **ARM Compatibility**: Tailored installation instructions for dependencies specific to ARM architecture.
- **Real-Time Processing**: Optimized code for real-time neural data analysis on a compact and energy-efficient platform.

## Getting Started

### Prerequisites
- **Jetson Nano** (4GB model)
- Ubuntu 18.04 or 20.04 (ARM64 architecture)
- Python 3.x
- **JetPack SDK** installed on Jetson Nano

### Required Dependencies
Before running `blech_lab` codes, ensure that the following dependencies are installed:

- `numpy`
- `pandas`
- `matplotlib`
- `scipy`
- `tensorflow` or `pytorch` (with GPU support)
- `jetson-stats` (optional, for monitoring system performance)

You can install these dependencies using the following command:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-dev
pip3
