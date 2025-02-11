#!/bin/bash

# *************************************************************************************
# | Install the scripts for use by the user without having to specify the full        |
# | path to them.                                                                     |
# |                                                                                   |
# | This script will:                                                                 |
# | 1. Creates symlinks for the scripts in the `/usr/local/bin`` directory            |
# |                                                                                   |
# | Usage:                                                                            |
# | 1. Open a Bash terminal                                                           |
# | 2. Run the script `.\install-scripts.sh`                                          |
# | 3. Use the `create-helm-chart` command to create a chart in the current directory |
# |                                                                                   |
# | --------------------------------------------------------------------------------- |
# | Author: [Bridgeman Accessible](https://bridgemanaccessible.ca)                    |
# | Date: 2025-02-11                                                                  |
# | Version: 1.0.0                                                                    |
# | --------------------------------------------------------------------------------- |
# | MIT License                                                                       |
# |                                                                                   |
# | Copyright (c) 2025 Bridgeman Accessible / Alan Bridgeman                          |
# |                                                                                   |
# | Permission is hereby granted, free of charge, to any person obtaining a copy      |
# | of this software and associated documentation files (the "Software"), to deal     |
# | in the Software without restriction, including without limitation the rights      |
# | to use, copy, modify, merge, publish, distribute, sublicense, and/or sell         |
# | copies of the Software, and to permit persons to whom the Software is             |
# | furnished to do so, subject to the following conditions:                          |
# |                                                                                   |
# | The above copyright notice and this permission notice shall be included in all    |
# | copies or substantial portions of the Software.                                   |
# |                                                                                   |
# | THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR        |
# | IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,          |
# | FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE       |
# | AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER            |
# | LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,     |
# | OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE     |
# | SOFTWARE.                                                                         |
# *************************************************************************************

# Install the script by creating a symlink in the `/usr/local/bin` directory
ln -s $(realpath ./create-helm-chart.sh) /usr/local/bin/create-helm-chart