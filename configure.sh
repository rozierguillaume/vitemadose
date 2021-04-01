#!/bin/bash
echo configuration locale
export LC_ALL="fr_FR.UTF-8"
export LC_CTYPE="fr_FR.UTF-8"
sudo dpkg-reconfigure locales
