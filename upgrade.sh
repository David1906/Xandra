cd "$(dirname "$0")"

git stash push -m xandra_config.json
git restore .
git pull
git stash pop

chmod +x Resources/chk_station_is_disabled.py
chmod +x Resources/chk_station_is_disabled.sh
chmod +x Resources/chk_station_test_finished.py
chmod +x Resources/test_upload.sh

if ! [ -x "$(command -v alembic)" ]; then
    echo "alembic upgrade head"
else
    echo "/root/.local/bin/alembic upgrade head"
fi