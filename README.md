# gflow-plugin

NOTE: This repository has been moved to: https://github.com/GFLOW-ORG/gflow-qgis-plugin

QGIS plugin for the GFLOW analytic element program

## Installing

Currently the easiest way to install this plugin in QGIS is by:

* Cloning this repository.
* Installing the [Pixi](https://pixi.sh/dev/) package manager.
* Running `pixi run zip` to create a `gflow-plugin.zip` file.
* Installing the plugin using this ZIP file via "Install from ZIP" in the QGIS Plugins Menu.

Pixi is not necessarily required, the zip step requires only the `shutil` package, which
is part of the Python standard library. If Python is available, run the following command
in the root of the project:

``python ./scripts/package.py`` 

To produce the `gflow-plugin.zip` file.

## Development

To easily synchronize changes, make a symlink from the qgis plugins directory
to the plugin directory in this project. After changes, run the QGIS Plugin
Reloader.

(Note that uninstalling the plugin in QGIS may have unintended consequences if
the plugin is installed via symlink!)
