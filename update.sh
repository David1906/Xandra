cd "$(dirname "$0")"

git restore .
git clean -f
git pull

sudo chmod +x ./Resources/chk_station_is_disabled.py
sudo chmod +x ./Resources/chk_station_is_disabled.sh
sudo chmod +x ./Resources/chk_station_test_finished.py
sudo chmod +x ./Resources/test_upload.sh

if command -v alembic > /dev/null; then
    echo "alembic upgrade head"
else
    echo "/root/.local/bin/alembic upgrade head"
fi