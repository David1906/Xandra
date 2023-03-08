cd "$(dirname "$0")"

git checkout -f
git clean -f
git pull

sudo chmod +x Resources/chk_station_is_disabled.py
sudo chmod +x Resources/chk_station_test_finished.py
sudo chmod +x Resources/up_sfc.sh
sudo chmod +x update.sh

if command -v alembic > /dev/null; then
    alembic upgrade head
else
    /root/.local/bin/alembic upgrade head
fi