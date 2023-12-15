
# install Mininet dependencies
sudo apt install -y mininet openvswitch-switch cgroup-tools help2man
# install poetry
curl -sSL https://install.python-poetry.org | python3 -
yes | poetry cache clear --all .  # Clear Poetry cache, this is sometimes needed
rm -rf poetry.lock                # # Bugfix for repeated install
rm -rf dist                       # Bugfix for repeated install
#poetry update                     # Update Poetry lock dependencies
poetry install                    # Package the dc_gym
